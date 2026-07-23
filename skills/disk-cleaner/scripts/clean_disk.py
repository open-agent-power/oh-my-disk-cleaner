#!/usr/bin/env python3
"""
Disk Cleaner - Cross-platform junk file cleaner
Safely removes temporary files, caches, logs, and other junk files

Enhanced with progress bars for better user feedback.
"""

import json
import os
import platform
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

# Use smart bootstrap module to import diskcleaner
try:
    # Add parent directory of current script to path for importing skill_bootstrap
    script_dir = Path(__file__).parent.resolve()
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    from skill_bootstrap import import_diskcleaner_modules

    # Setup skill environment and import modules
    IMPORT_SUCCESS, MODULES = import_diskcleaner_modules()
    PROGRESS_AVAILABLE = IMPORT_SUCCESS

    if IMPORT_SUCCESS:
        ProgressBar = MODULES["ProgressBar"]
    else:
        ProgressBar = None

except Exception as e:
    # If bootstrap module also fails, try direct import (may be installed)
    try:
        from diskcleaner.core.progress import ProgressBar

        PROGRESS_AVAILABLE = True
        print(f"[Warning] Skill bootstrap failed, using installed version: {e}", file=sys.stderr)
    except ImportError:
        PROGRESS_AVAILABLE = False
        ProgressBar = None
        print(
            f"[Warning] Cannot import diskcleaner module, some features unavailable: {e}",
            file=sys.stderr,
        )


# Custom --path targets must contain at least one of these names as a path
# segment (case-insensitive) to be treated as junk by default. Anything else
# requires explicit opt-in via --allow-unsafe-path. Kept conservative on
# purpose: a false negative (refuse) is safe, a false positive (allow) is not.
JUNK_NAME_HINTS = {
    "cache",
    "caches",
    "tmp",
    "temp",
    "temporary",
    "logs",
    "log",
    "trash",
    "recycle",
    "recycler",
    "$recycle.bin",
    "downloads",
    "cookies",
    "history",
    "inetcache",
    "prefetch",
    "softwaredistribution",
    "webcache",
}


class UnsafePathError(ValueError):
    """Raised when a custom --path is refused by the safety gate."""


class DiskCleaner:
    def __init__(self, dry_run: bool = True, show_progress: bool = True):
        self.dry_run = dry_run
        self.platform = platform.system()
        self.system = platform.system().lower()
        self.cleaned_files = []
        self.freed_space = 0
        self.errors = []
        self.show_progress = show_progress and PROGRESS_AVAILABLE and sys.stdout.isatty()

        # Safety: paths to never delete
        self.protected_paths = self._get_protected_paths()

        # Safety: file extensions to never delete
        self.protected_extensions = {
            ".exe",
            ".dll",
            ".sys",
            ".drv",
            ".bat",
            ".cmd",
            ".ps1",
            ".sh",
            ".bash",
            ".zsh",
            ".app",
            ".dmg",
            ".pkg",
            ".deb",
            ".rpm",
            ".msi",
            ".iso",
            ".vhd",
            ".vhdx",
        }

    def _get_protected_paths(self) -> Set[str]:
        """Get paths that should never be deleted"""
        protected = set()

        if self.system == "windows":
            protected.update(
                [
                    "C:\\Windows",
                    "C:\\Program Files",
                    "C:\\Program Files (x86)",
                    "C:\\ProgramData",
                ]
            )
            # Protect user profile root but NOT subdirectories (allows cleaning Temp, Cache, etc.)
            # We use a trailing separator to indicate we're protecting the directory itself,
            # not its contents
            # if "USERPROFILE" in os.environ:
            #     protected.add(os.environ["USERPROFILE"])

        elif self.system == "darwin":
            protected.update(
                [
                    "/System",
                    "/Library",
                    "/Applications",
                    "/usr",
                    "/bin",
                    "/sbin",
                ]
            )
            # Don't protect entire home directory to allow cleaning cache/logs
            # protected.add(os.path.expanduser("~"))

        else:  # Linux
            protected.update(
                [
                    "/usr",
                    "/bin",
                    "/sbin",
                    "/lib",
                    "/lib64",
                    "/etc",
                    "/boot",
                    "/sys",
                    "/proc",
                    "/dev",
                ]
            )
            # Don't protect entire home directory to allow cleaning cache/logs
            # protected.add(os.path.expanduser("~"))

        return protected

    def _is_safe_to_delete(self, path: Path) -> bool:
        """Check if a path is safe to delete.

        Uses path-aware comparisons (Path equality / parents) instead of raw
        ``str.startswith`` so that a protected prefix like ``/usr`` can never
        accidentally protect (or fail to protect) a sibling such as
        ``/usr-local``.
        """
        try:
            resolved = path.resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            resolved = path

        # Protected system prefixes (path-aware): the path itself, or anything
        # nested below one of them.
        for protected in self.protected_paths:
            try:
                prot = Path(protected).resolve(strict=False)
            except (OSError, RuntimeError, ValueError):
                continue
            if resolved == prot or prot in resolved.parents:
                return False

        # Protected exact roots: filesystem root and home/profile root.
        if self._is_filesystem_root(resolved):
            return False
        for root in self._get_protected_roots():
            if resolved == root:
                return False

        # Check file extension
        if path.suffix.lower() in self.protected_extensions:
            return False

        return True

    def _is_filesystem_root(self, path: Path) -> bool:
        """Return True for filesystem roots: ``/`` on POSIX, drive/UNC roots
        such as ``C:\\`` on Windows."""
        text = str(path)
        if text in (os.sep, "/"):
            return True
        drive, tail = os.path.splitdrive(text)
        if drive and tail.strip("/\\") == "":
            return True
        return False

    def _get_protected_roots(self) -> Set[Path]:
        """Exact-match roots that must never be cleaned: the filesystem root
        and the user's home / profile root. Subdirectories such as ``~/.cache``
        or ``~/Library/Caches`` are still allowed because this check only
        matches the root directory itself, not its children."""
        roots = set()
        try:
            roots.add(Path(os.path.abspath(os.sep)).resolve(strict=False))
        except (OSError, RuntimeError, ValueError):
            pass
        try:
            roots.add(Path(os.path.expanduser("~")).resolve(strict=False))
        except (OSError, RuntimeError, ValueError):
            pass
        return roots

    def _directory_size(self, path: Path) -> int:
        """Recursively compute the on-disk size in bytes of a directory tree.
        Symlinks are not followed, so a link can never inflate the estimate."""
        total = 0
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            total += self._directory_size(Path(entry.path))
                        else:
                            total += entry.stat(follow_symlinks=False).st_size
                    except (OSError, ValueError):
                        continue
        except (OSError, PermissionError):
            pass
        return total

    @staticmethod
    def _is_real_dir(path: Path) -> bool:
        """True if ``path`` is a directory and not a symlink. This is a
        Python 3.6-compatible replacement for
        ``Path.is_dir(follow_symlinks=False)``, which only exists on 3.12+."""
        try:
            return not path.is_symlink() and path.is_dir()
        except (OSError, RuntimeError, ValueError):
            return False

    def validate_custom_path(
        self,
        path: str,
        force: bool = False,
        allow_unsafe: bool = False,
        confirm_path: Optional[str] = None,
    ) -> str:
        """Safety gate for ``--path``. Returns the resolved absolute path, or
        raises ``UnsafePathError`` explaining why the path is refused.

        Defence in depth:

        1. Never clean a filesystem root.
        2. Never clean the home / profile root (its subdirectories are fine).
        3. By default the path must look like junk (cache/tmp/temp/logs/
           trash/recycle/...); otherwise require --allow-unsafe-path.
        4. Using --path together with --force requires
           --confirm-path <resolved-absolute-path>.
        """
        try:
            resolved = Path(path).expanduser().resolve(strict=False)
        except (OSError, RuntimeError, ValueError) as exc:
            raise UnsafePathError(f"Cannot resolve path {path!r}: {exc}")

        if self._is_filesystem_root(resolved):
            raise UnsafePathError(
                f"Refusing to clean filesystem root {resolved}. "
                "Disk Cleaner never cleans filesystem roots."
            )

        for root in self._get_protected_roots():
            if resolved == root:
                raise UnsafePathError(
                    f"Refusing to clean home/profile root {resolved}. "
                    "Point --path at a junk subdirectory such as "
                    "~/.cache or ~/Library/Caches instead."
                )

        # Strip a leading dot so hidden junk dirs (~/.cache, ~/.Trash) match.
        segments = [part.lower().lstrip(".") for part in resolved.parts]
        looks_like_junk = any(part in JUNK_NAME_HINTS for part in segments)
        if not looks_like_junk and not allow_unsafe:
            raise UnsafePathError(
                f"Custom path {resolved} does not look like a "
                "cache/temp/log/trash directory. By default Disk Cleaner only "
                "cleans junk-like paths. To proceed, re-run with "
                "--allow-unsafe-path (and, when using --force, also "
                "--confirm-path <resolved-path>)."
            )

        if force:
            if not confirm_path:
                raise UnsafePathError(
                    "Using --path with --force requires "
                    "--confirm-path <resolved-absolute-path> to acknowledge "
                    f"exactly what will be deleted. Expected: "
                    f"--confirm-path {resolved}"
                )
            try:
                confirmed = Path(confirm_path).expanduser().resolve(strict=False)
            except (OSError, RuntimeError, ValueError):
                confirmed = Path(confirm_path)
            if str(confirmed) != str(resolved):
                raise UnsafePathError(
                    "--confirm-path does not match the resolved path.\n"
                    f"  provided: {confirmed}\n  resolved:  {resolved}"
                )

        return str(resolved)

    def _deduplicate_paths(self, paths: List[str]) -> List[str]:
        """Deduplicate list of paths by resolving to real paths."""
        seen = set()
        unique_paths = []
        for path in paths:
            if path and os.path.exists(path):
                # Resolve to real path to handle symlinks and duplicates
                real_path = os.path.realpath(path)
                if real_path not in seen:
                    seen.add(real_path)
                    unique_paths.append(real_path)
        return unique_paths

    def get_cleanable_locations(self) -> Dict[str, List[str]]:
        """Get platform-specific locations that can be cleaned"""
        locations = {"temp": [], "cache": [], "logs": [], "recycle": [], "downloads_old": []}

        if self.system == "windows":
            # Temp directories
            temp_dirs = [
                os.environ.get("TEMP", ""),
                os.environ.get("TMP", ""),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
            ]
            locations["temp"].extend(self._deduplicate_paths(temp_dirs))

            # Cache directories
            cache_dirs = [
                os.path.join(
                    os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "INetCache"
                ),
                os.path.join(
                    os.environ.get("LOCALAPPDATA", ""),
                    "Google",
                    "Chrome",
                    "User Data",
                    "Default",
                    "Cache",
                ),
                os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles"),
                os.path.join(
                    os.environ.get("LOCALAPPDATA", ""),
                    "Microsoft",
                    "Edge",
                    "User Data",
                    "Default",
                    "Cache",
                ),
            ]
            locations["cache"].extend(self._deduplicate_paths(cache_dirs))

            # Windows specific
            locations["logs"].extend(
                [
                    os.path.join(
                        os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "History"
                    ),
                    os.path.join(
                        os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "WebCache"
                    ),
                ]
            )

            # Recycle Bin
            recycle_path = os.path.join(os.environ.get("SYSTEMDRIVE", "C:"), "$Recycle.Bin")
            if os.path.exists(recycle_path):
                locations["recycle"].append(recycle_path)

            # Prefetch
            prefetch = os.path.join(os.environ.get("WINDIR", ""), "Prefetch")
            if os.path.exists(prefetch):
                locations["temp"].append(prefetch)

            # Windows Update cache
            update_cache = os.path.join(
                os.environ.get("WINDIR", ""), "SoftwareDistribution", "Download"
            )
            if os.path.exists(update_cache):
                locations["temp"].append(update_cache)

        elif self.system == "darwin":
            # macOS temp and cache
            locations["temp"].extend(
                [
                    "/tmp",
                    "/private/tmp",
                ]
            )
            locations["cache"].extend(
                [
                    os.path.expanduser("~/Library/Caches"),
                ]
            )

            # User logs
            locations["logs"].append(os.path.expanduser("~/Library/Logs"))

            # iOS device backups
            backup_path = os.path.expanduser("~/Library/Application Support/MobileSync/Backup")
            if os.path.exists(backup_path):
                locations["cache"].append(backup_path)

        else:  # Linux
            # System temp and cache
            locations["temp"].extend(
                [
                    "/tmp",
                    "/var/tmp",
                ]
            )
            locations["cache"].extend(
                [
                    "/var/cache",
                ]
            )

            # User cache
            user_cache = os.path.expanduser("~/.cache")
            if os.path.exists(user_cache):
                locations["cache"].append(user_cache)

        # Deduplicate all location lists
        for key in locations:
            locations[key] = self._deduplicate_paths(locations[key])

        return locations

    def clean_directory(
        self,
        path: str,
        older_than_days: int = 0,
        max_size_mb: int = None,
        pattern: str = "*",
        show_progress: bool = True,
    ) -> Dict:
        """
        Clean a directory with safety checks and optional progress bar.

        Args:
            path: Directory path to clean
            older_than_days: Only delete files older than this many days
            max_size_mb: Only delete files smaller than this size (MB)
            pattern: Glob pattern to match files
            show_progress: Show progress bar for this operation

        Returns:
            Dictionary with cleaning results
        """
        result = {"path": path, "files_deleted": 0, "space_freed_mb": 0, "errors": []}

        dir_path = Path(path)
        if not dir_path.exists():
            return result

        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        try:
            # Collect all items first for progress bar
            items = list(dir_path.glob(pattern))

            if self.show_progress and show_progress and len(items) > 0:
                progress = ProgressBar(len(items), prefix=f"Cleaning {Path(path).name}")
            else:
                progress = None

            for item in items:
                if not item.exists():
                    continue

                try:
                    # Safety check
                    if not self._is_safe_to_delete(item):
                        continue

                    # Age check
                    if older_than_days > 0:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if mtime > cutoff_date:
                            continue

                    # Size check
                    if max_size_mb:
                        size_mb = item.stat().st_size / (1024 * 1024)
                        if size_mb > max_size_mb:
                            continue

                    # Calculate size. For directories in dry-run, recurse so
                    # the preview reflects the real recursive impact instead
                    # of just the directory-entry size (which is tiny and
                    # misleadingly reassuring).
                    if self.dry_run and self._is_real_dir(item):
                        size = self._directory_size(item)
                    else:
                        try:
                            size = item.stat(follow_symlinks=False).st_size
                        except OSError:
                            size = 0

                    # Delete (or simulate)
                    if self.dry_run:
                        result["files_deleted"] += 1
                        result["space_freed_mb"] += size / (1024 * 1024)
                    else:
                        if self._is_real_dir(item):
                            # Do not swallow failures: surface them so a
                            # partially-failed recursive delete is visible.
                            shutil.rmtree(item)
                        else:
                            item.unlink()

                        result["files_deleted"] += 1
                        result["space_freed_mb"] += size / (1024 * 1024)

                    # Update progress (safely get item name)
                    if progress:
                        try:
                            item_name = item.name
                        except (AttributeError, OSError, RuntimeError):
                            item_name = str(item)
                        progress.update(1, item_name)

                except (PermissionError, OSError) as e:
                    result["errors"].append(str(e))
                    self.errors.append(f"{item}: {e}")
                except (AttributeError, RuntimeError) as e:
                    # Handle unexpected errors from accessing item attributes
                    result["errors"].append(str(e))
                    self.errors.append(f"{item}: {e}")

            if progress:
                progress.close()

        except (PermissionError, OSError) as e:
            result["errors"].append(str(e))

        result["space_freed_mb"] = round(result["space_freed_mb"], 2)
        return result

    def clean_temp_files(self, show_progress: bool = True) -> Dict:
        """Clean temporary files with progress bar"""
        locations = self.get_cleanable_locations()
        results = {"category": "temp_files", "locations": []}

        temp_dirs = locations.get("temp", [])

        if self.show_progress and show_progress and len(temp_dirs) > 0:
            progress = ProgressBar(len(temp_dirs), prefix="Cleaning temp")
        else:
            progress = None

        for temp_dir in temp_dirs:
            result = self.clean_directory(temp_dir, older_than_days=0, show_progress=False)
            results["locations"].append(result)

            if progress:
                progress.update(1, Path(temp_dir).name)

        if progress:
            progress.close()

        return results

    def clean_cache_files(self, show_progress: bool = True) -> Dict:
        """Clean cache files with progress bar"""
        locations = self.get_cleanable_locations()
        results = {"category": "cache", "locations": []}

        cache_dirs = locations.get("cache", [])

        if self.show_progress and show_progress and len(cache_dirs) > 0:
            progress = ProgressBar(len(cache_dirs), prefix="Cleaning cache")
        else:
            progress = None

        for cache_dir in cache_dirs:
            result = self.clean_directory(cache_dir, older_than_days=30, show_progress=False)
            results["locations"].append(result)

            if progress:
                progress.update(1, Path(cache_dir).name)

        if progress:
            progress.close()

        return results

    def clean_log_files(self, show_progress: bool = True) -> Dict:
        """Clean log files with progress bar"""
        locations = self.get_cleanable_locations()
        results = {"category": "logs", "locations": []}

        log_dirs = locations.get("logs", [])

        if self.show_progress and show_progress and len(log_dirs) > 0:
            progress = ProgressBar(len(log_dirs), prefix="Cleaning logs")
        else:
            progress = None

        for log_dir in log_dirs:
            result = self.clean_directory(
                log_dir, older_than_days=30, pattern="*.log", show_progress=False
            )
            results["locations"].append(result)

            if progress:
                progress.update(1, Path(log_dir).name)

        if progress:
            progress.close()

        return results

    def clean_recycle_bin(self, show_progress: bool = True) -> Dict:
        """Clean recycle bin/trash with progress bar"""
        locations = self.get_cleanable_locations()
        results = {"category": "recycle_bin", "locations": []}

        recycle_dirs = locations.get("recycle", [])

        if self.show_progress and show_progress and len(recycle_dirs) > 0:
            progress = ProgressBar(len(recycle_dirs), prefix="Emptying recycle")
        else:
            progress = None

        for recycle_dir in recycle_dirs:
            result = self.clean_directory(recycle_dir, older_than_days=30, show_progress=False)
            results["locations"].append(result)

            if progress:
                progress.update(1, Path(recycle_dir).name)

        if progress:
            progress.close()

        return results

    def clean_old_downloads(self, days: int = 90, show_progress: bool = True) -> Dict:
        """Clean old download files with progress bar"""
        downloads_path = os.path.expanduser("~/Downloads")
        results = {"category": "old_downloads", "locations": []}

        if os.path.exists(downloads_path):
            result = self.clean_directory(
                downloads_path, older_than_days=days, show_progress=show_progress
            )
            results["locations"].append(result)

        return results

    def clean_all(self, show_progress: bool = True) -> Dict:
        """Run all cleaning operations with progress bars"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform,
            "dry_run": self.dry_run,
            "categories": [],
        }

        # Clean temp files
        temp_result = self.clean_temp_files(show_progress=show_progress)
        results["categories"].append(temp_result)

        # Clean cache
        cache_result = self.clean_cache_files(show_progress=show_progress)
        results["categories"].append(cache_result)

        # Clean logs
        log_result = self.clean_log_files(show_progress=show_progress)
        results["categories"].append(log_result)

        # Clean recycle bin
        recycle_result = self.clean_recycle_bin(show_progress=show_progress)
        results["categories"].append(recycle_result)

        # Calculate totals
        total_files = 0
        total_space_mb = 0

        for category in results["categories"]:
            for location in category["locations"]:
                total_files += location["files_deleted"]
                total_space_mb += location["space_freed_mb"]

        results["summary"] = {
            "total_files_deleted": total_files,
            "total_space_freed_mb": round(total_space_mb, 2),
            "total_space_freed_gb": round(total_space_mb / 1024, 2),
            "total_errors": len(self.errors),
        }

        return results


def print_report(results: Dict):
    """Print formatted cleaning report"""
    mode = "DRY RUN" if results["dry_run"] else "CLEAN"

    print("\n" + "=" * 60)
    print(f"DISK CLEANING REPORT ({mode}) - {results['timestamp']}")
    print("=" * 60)

    for category in results["categories"]:
        print(f"\n[x] {category['category'].upper().replace('_', ' ')}:")

        # Safely handle categories with no locations
        if not category.get("locations"):
            print("  [i] No locations found for this category")
            continue

        for location in category["locations"]:
            if location.get("files_deleted", 0) > 0:
                space_mb = location.get("space_freed_mb", 0)
                space_str = f"{space_mb:.2f} MB" if space_mb < 1024 else f"{space_mb/1024:.2f} GB"
                print(f"  [OK] {location.get('path', 'Unknown')}")
                print(f"     Files: {location.get('files_deleted', 0)}, Space: {space_str}")
            elif location.get("errors"):
                print(f"  [!] {location.get('path', 'Unknown')}: {len(location['errors'])} errors")

    summary = results["summary"]
    print("\n[i] SUMMARY:")
    print(f"  Total files: {summary['total_files_deleted']}")
    print(f"  Space freed: {summary['total_space_freed_gb']:.2f} GB")

    if summary["total_errors"] > 0:
        print(f"  [!] Errors: {summary['total_errors']}")

    if results["dry_run"]:
        print("\n[i] This was a DRY RUN. No files were actually deleted.")
        print("   Run without --dry-run to perform actual cleaning.")

    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean disk junk files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview cleaning (safe mode)
  python scripts/clean_disk.py --dry-run

  # Actually clean
  python scripts/clean_disk.py --force

  # Clean specific categories
  python scripts/clean_disk.py --temp --cache --dry-run

  # Clean old downloads (>90 days)
  python scripts/clean_disk.py --downloads 90 --force

  # Clean custom path (e.g., D:\\Temp on secondary drive)
  python scripts/clean_disk.py --path "D:/Temp" --dry-run

  # Clean system paths + custom path
  python scripts/clean_disk.py --temp --path "D:/Downloads" --force
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simulate cleaning without deleting (default: True)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Actually delete files (disables dry-run)"
    )
    parser.add_argument("--temp", action="store_true", help="Clean only temp files")
    parser.add_argument("--cache", action="store_true", help="Clean only cache")
    parser.add_argument("--logs", action="store_true", help="Clean only logs")
    parser.add_argument("--recycle", action="store_true", help="Clean only recycle bin")
    parser.add_argument(
        "--downloads", type=int, metavar="DAYS", help="Clean downloads older than N days"
    )
    parser.add_argument(
        "--path",
        "-p",
        help="Clean a specific custom path. WARNING: --path deletes matching "
        "child directories RECURSIVELY. The path must look like junk "
        "(cache/temp/log/trash/...) or be opted into with --allow-unsafe-path. "
        "Never point this at ~, /Users/<name>, C:\\Users\\<name>, ~/Documents "
        "or ~/Developer.",
    )
    parser.add_argument(
        "--allow-unsafe-path",
        action="store_true",
        help="Allow a --path target that does not look like junk "
        "(cache/temp/log/trash). Required to clean an arbitrary directory.",
    )
    parser.add_argument(
        "--confirm-path",
        metavar="RESOLVED_PATH",
        help="Required when combining --path with --force: pass the resolved "
        "absolute path to acknowledge exactly what will be deleted.",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Save report to file")
    parser.add_argument(
        "--no-progress", action="store_true", help="Disable progress bars (useful for scripting)"
    )

    args = parser.parse_args()

    dry_run = args.dry_run and not args.force
    show_progress = not args.no_progress and not args.json
    cleaner = DiskCleaner(dry_run=dry_run, show_progress=show_progress)

    # Run specific or all cleaning
    if args.path:
        # Clean custom path specified by user -- run it through the safety
        # gate first. See DiskCleaner.validate_custom_path for the rules.
        from pathlib import Path as PathLib

        custom_path = PathLib(args.path)
        if not custom_path.exists():
            print(f"[X] Error: Path does not exist: {args.path}", file=sys.stderr)
            sys.exit(1)

        try:
            resolved_path = cleaner.validate_custom_path(
                str(custom_path),
                force=args.force,
                allow_unsafe=args.allow_unsafe_path,
                confirm_path=args.confirm_path,
            )
        except UnsafePathError as exc:
            print(f"[X] Refusing to clean custom path:\n    {exc}", file=sys.stderr)
            sys.exit(2)

        result = cleaner.clean_directory(resolved_path, show_progress=show_progress)
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": [
                {"category": "custom_path", "locations": [result]},
            ],
        }

        # If also cleaning system categories, add them
        if args.temp:
            results["categories"].append(cleaner.clean_temp_files())
        if args.cache:
            results["categories"].append(cleaner.clean_cache_files())
        if args.logs:
            results["categories"].append(cleaner.clean_log_files())

    elif args.temp:
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": [cleaner.clean_temp_files()],
        }
    elif args.cache:
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": [cleaner.clean_cache_files()],
        }
    elif args.logs:
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": [cleaner.clean_log_files()],
        }
    elif args.recycle:
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": [cleaner.clean_recycle_bin()],
        }
    elif args.downloads:
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": [cleaner.clean_old_downloads(args.downloads)],
        }
    else:
        results = cleaner.clean_all()

    # Calculate summary if not already present
    if "summary" not in results:
        total_files = 0
        total_space = 0
        for category in results["categories"]:
            # Safely sum across all locations (categories may have no locations)
            if category.get("locations"):
                for location in category["locations"]:
                    total_files += location.get("files_deleted", 0)
                    total_space += location.get("space_freed_mb", 0)

        results["summary"] = {
            "total_files_deleted": total_files,
            "total_space_freed_mb": round(total_space, 2),
            "total_space_freed_gb": round(total_space / 1024, 2),
            "total_errors": 0,
        }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[OK] Report saved to {args.output}")


if __name__ == "__main__":
    main()
