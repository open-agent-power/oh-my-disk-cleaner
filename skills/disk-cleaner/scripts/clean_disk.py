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
import stat
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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


JUNK_DIRECTORY_NAMES = {
    "$recycle.bin",
    "cache",
    "caches",
    "cookies",
    "downloads",
    "history",
    "inetcache",
    "log",
    "logs",
    "prefetch",
    "recycle",
    "recycler",
    "temp",
    "temporary",
    "tmp",
    "trash",
    "webcache",
}

PROJECT_MARKERS = {
    ".git",
    ".hg",
    ".svn",
    "Cargo.toml",
    "go.mod",
    "package.json",
    "pyproject.toml",
}


class UnsafePathError(ValueError):
    """A custom cleanup target failed validation."""


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
        """Check if a path is safe to delete"""
        try:
            resolved = path.expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            return False

        if self._is_protected_root(resolved):
            return False

        # Path-aware comparison keeps sibling names such as /usr-local distinct.
        for protected in self.protected_paths:
            try:
                protected_path = Path(protected).expanduser().resolve()
            except (OSError, RuntimeError, ValueError):
                continue
            if resolved == protected_path or protected_path in resolved.parents:
                return False

        # Check file extension
        if resolved.suffix.lower() in self.protected_extensions:
            return False

        return True

    @staticmethod
    def _is_filesystem_root(path: Path) -> bool:
        """Return whether path is a POSIX, drive, or UNC filesystem root."""
        return bool(path.anchor) and path == Path(path.anchor)

    def _is_protected_root(self, path: Path) -> bool:
        """Protect filesystem roots and the current home/profile root."""
        if self._is_filesystem_root(path):
            return True
        try:
            home = Path(os.path.expanduser("~")).resolve()
        except (OSError, RuntimeError, ValueError):
            return True
        return path == home

    @staticmethod
    def _is_reparse_point(metadata: os.stat_result) -> bool:
        """Return whether metadata describes a Windows reparse point."""
        attributes = getattr(metadata, "st_file_attributes", 0)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        return bool(attributes & reparse_flag)

    def _item_size(self, path: Path) -> int:
        """Measure recursive bytes without following links or reparse points."""
        metadata = path.lstat()
        if (
            stat.S_ISLNK(metadata.st_mode)
            or self._is_reparse_point(metadata)
            or not stat.S_ISDIR(metadata.st_mode)
        ):
            return metadata.st_size

        total = 0
        pending = [path]
        while pending:
            with os.scandir(str(pending.pop())) as entries:
                for entry in entries:
                    metadata = entry.stat(follow_symlinks=False)
                    if stat.S_ISDIR(metadata.st_mode) and not self._is_reparse_point(metadata):
                        pending.append(Path(entry.path))
                    else:
                        total += metadata.st_size
        return total

    def validate_custom_path(
        self,
        path: str,
        force: bool = False,
        allow_unsafe: bool = False,
        confirm_path: Optional[str] = None,
    ) -> Tuple[str, Tuple[int, int]]:
        """Resolve and validate a user-supplied cleanup directory."""
        requested_path = Path(path).expanduser()
        try:
            initial_metadata = requested_path.stat()
        except OSError as error:
            raise UnsafePathError(f"Cannot inspect custom path {requested_path}: {error}")
        if not stat.S_ISDIR(initial_metadata.st_mode):
            raise UnsafePathError(f"Custom path must be a directory: {requested_path}")
        identity = (initial_metadata.st_dev, initial_metadata.st_ino)

        try:
            target = requested_path.resolve()
            resolved_metadata = target.stat()
        except (OSError, RuntimeError, ValueError) as error:
            raise UnsafePathError(f"Cannot resolve custom path {path!r}: {error}")
        if (resolved_metadata.st_dev, resolved_metadata.st_ino) != identity:
            raise UnsafePathError(f"Custom path changed during validation: {requested_path}")

        if self._is_protected_root(target):
            raise UnsafePathError(f"Filesystem and home/profile roots are protected: {target}")
        if not self._is_safe_to_delete(target):
            raise UnsafePathError(f"Protected path: {target}")

        leaf_name = target.name.casefold().lstrip(".")
        project_markers = sorted(marker for marker in PROJECT_MARKERS if (target / marker).exists())
        if not allow_unsafe and (leaf_name not in JUNK_DIRECTORY_NAMES or project_markers):
            detail = (
                f"project markers found ({', '.join(project_markers)})"
                if project_markers
                else f"directory name {target.name!r} is outside the junk-name allowlist"
            )
            raise UnsafePathError(f"Custom path requires --allow-unsafe-path: {target} ({detail})")

        if force:
            if not confirm_path:
                raise UnsafePathError(f"--path with --force requires --confirm-path {target}")
            confirmation = Path(confirm_path).expanduser()
            if not confirmation.is_absolute():
                raise UnsafePathError(f"--confirm-path must be absolute: {target}")
            try:
                confirmation = confirmation.resolve()
            except (OSError, RuntimeError, ValueError) as error:
                raise UnsafePathError(f"Cannot resolve --confirm-path: {error}")
            if confirmation != target:
                raise UnsafePathError(f"--confirm-path must match the cleanup target: {target}")

        try:
            final_metadata = target.stat()
        except OSError as error:
            raise UnsafePathError(f"Cannot revalidate custom path {target}: {error}")
        if (final_metadata.st_dev, final_metadata.st_ino) != identity:
            raise UnsafePathError(f"Custom path changed during validation: {target}")

        return str(target), identity

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
        expected_identity: Optional[Tuple[int, int]] = None,
    ) -> Dict:
        """
        Clean a directory with safety checks and optional progress bar.

        Args:
            path: Directory path to clean
            older_than_days: Only delete files older than this many days
            max_size_mb: Only delete files smaller than this size (MB)
            pattern: Glob pattern to match files
            show_progress: Show progress bar for this operation
            expected_identity: Validated device and inode for a custom cleanup root

        Returns:
            Dictionary with cleaning results
        """
        result = {"path": path, "files_deleted": 0, "space_freed_mb": 0, "errors": []}

        requested_path = Path(path).expanduser()
        if expected_identity is not None:
            try:
                current_metadata = requested_path.stat()
            except OSError as error:
                message = f"Cannot revalidate cleanup root {requested_path}: {error}"
                result["errors"].append(message)
                self.errors.append(message)
                return result
            if (current_metadata.st_dev, current_metadata.st_ino) != expected_identity:
                message = f"Cleanup root changed after validation: {requested_path}"
                result["errors"].append(message)
                self.errors.append(message)
                return result

        try:
            dir_path = requested_path.resolve()
        except (OSError, RuntimeError, ValueError) as error:
            result["errors"].append(str(error))
            self.errors.append(f"{path}: {error}")
            return result
        if not dir_path.exists():
            return result
        if not self._is_safe_to_delete(dir_path):
            error = f"Refusing protected cleanup root: {dir_path}"
            result["errors"].append(error)
            self.errors.append(error)
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

                    # One measurement drives preview, filtering, and deletion reports.
                    size = self._item_size(item)

                    # Size check
                    if max_size_mb is not None:
                        size_mb = size / (1024 * 1024)
                        if size_mb > max_size_mb:
                            continue

                    # Delete (or simulate)
                    if self.dry_run:
                        result["files_deleted"] += 1
                        result["space_freed_mb"] += size / (1024 * 1024)
                    else:
                        if item.is_dir() and not item.is_symlink():
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
            self.errors.append(f"{dir_path}: {e}")

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
  python scripts/clean_disk.py --temp --path "D:/Downloads" --force \\
    --confirm-path "D:/Downloads"
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
        help="Clean a custom directory recursively. Junk directory names are accepted by default.",
    )
    parser.add_argument(
        "--allow-unsafe-path",
        action="store_true",
        help="Allow a custom path whose target name is outside the junk allowlist",
    )
    parser.add_argument(
        "--confirm-path",
        metavar="ABSOLUTE_PATH",
        help="Exact resolved path required with --path --force",
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
        requested_path = Path(args.path).expanduser()
        if not requested_path.exists():
            print(f"[X] Error: Path does not exist: {args.path}", file=sys.stderr)
            sys.exit(1)
        try:
            custom_path, custom_identity = cleaner.validate_custom_path(
                str(requested_path),
                force=args.force,
                allow_unsafe=args.allow_unsafe_path,
                confirm_path=args.confirm_path,
            )
        except UnsafePathError as error:
            print(f"[X] Refusing custom path: {error}", file=sys.stderr)
            sys.exit(2)

        result = cleaner.clean_directory(
            custom_path,
            show_progress=show_progress,
            expected_identity=custom_identity,
        )
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
        total_errors = 0
        for category in results["categories"]:
            # Safely sum across all locations (categories may have no locations)
            if category.get("locations"):
                for location in category["locations"]:
                    total_files += location.get("files_deleted", 0)
                    total_space += location.get("space_freed_mb", 0)
                    total_errors += len(location.get("errors", []))

        results["summary"] = {
            "total_files_deleted": total_files,
            "total_space_freed_mb": round(total_space, 2),
            "total_space_freed_gb": round(total_space / 1024, 2),
            "total_errors": total_errors,
        }

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n[OK] Report saved to {args.output}")

    if results["summary"]["total_errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
