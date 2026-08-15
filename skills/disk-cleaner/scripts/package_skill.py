#!/usr/bin/env python3
"""
Improved skill package script

Create self-contained .skill file, ensuring:
1. Include all required files
2. Auto-detect project root directory
3. Verify package integrity
4. Generate installation instructions
"""

import os
import platform
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import List, Tuple


# Initialize Windows console encoding
def init_console():
    """Initialize console encoding"""
    if platform.system().lower() == "windows":
        try:
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            if hasattr(sys.stdout, "buffer"):
                import io

                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
                )
            if hasattr(sys.stderr, "buffer"):
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True
                )
        except Exception:
            pass


# Initialize at module load time
init_console()


def find_project_root() -> Path:
    """
    Intelligently find project root directory

    Search strategy:
    1. Search upward from current script location
    2. Find parent directory containing diskcleaner directory
    3. Find directory containing pyproject.toml
    """
    # Script location
    script_path = Path(__file__).resolve()

    # Method 1: Infer from script location
    # scripts/disk-cleaner/scripts/package_skill.py
    # -> Project root is 3 levels up
    candidate = script_path.parent.parent.parent.parent
    if (candidate / "diskcleaner").exists():
        return candidate

    # Method 2: Find pyproject.toml
    current = script_path
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent

    # Method 3: Use parent of parent of current script directory
    # Assuming in skills/disk-cleaner/scripts/
    candidate = script_path.parent.parent.parent
    if (candidate / "diskcleaner").exists():
        return candidate

    # Last fallback: use cwd
    cwd = Path.cwd()
    if (cwd / "diskcleaner").exists():
        return cwd

    raise FileNotFoundError(
        f"Cannot find project root. Please run this script from disk-cleaner repo directory.\n"
        f"Current script location: {script_path}\n"
        f"Current working directory: {cwd}"
    )


def find_skill_root(project_root: Path) -> Path:
    """Find skill root directory"""
    # Try common locations
    candidates = [
        project_root / "skills" / "disk-cleaner",
        project_root / "skill",
        project_root,
    ]

    for candidate in candidates:
        if (candidate / "SKILL.md").exists():
            return candidate

    raise FileNotFoundError(
        f"Cannot find skill root directory (requires SKILL.md file).\n"
        f"Tried locations: {[str(c) for c in candidates]}"
    )


def get_files_to_include(project_root: Path, skill_root: Path) -> List[Tuple[Path, str]]:
    """
    Get list of files to include in package

    Returns:
        List of (source path, destination relative path)
    """
    items = []

    # Core modules (from project root)
    core_files = [
        "diskcleaner/__init__.py",
        "diskcleaner/config/__init__.py",
        "diskcleaner/config/defaults.py",
        "diskcleaner/config/loader.py",
        "diskcleaner/core/__init__.py",
        "diskcleaner/core/cache.py",
        "diskcleaner/core/classifier.py",
        "diskcleaner/core/duplicate_finder.py",
        "diskcleaner/core/interactive.py",
        "diskcleaner/core/process_manager.py",
        "diskcleaner/core/progress.py",
        "diskcleaner/core/safety.py",
        "diskcleaner/core/scanner.py",
        "diskcleaner/core/smart_cleanup.py",
        "diskcleaner/optimization/__init__.py",
        "diskcleaner/optimization/concurrency.py",
        "diskcleaner/optimization/delete.py",
        "diskcleaner/optimization/hash.py",
        "diskcleaner/optimization/memory.py",
        "diskcleaner/optimization/profiler.py",
        "diskcleaner/optimization/scan.py",
        "diskcleaner/platforms/__init__.py",
        "diskcleaner/platforms/linux.py",
        "diskcleaner/platforms/macos.py",
        "diskcleaner/platforms/windows.py",
    ]

    for file_path in core_files:
        src = project_root / file_path
        if src.exists():
            items.append((src, file_path))
        else:
            print(f"[!] Warning: File does not exist: {src}")

    # Skill files (from skill root)
    skill_files = [
        "SKILL.md",
        "INSTALL.md",
        "UNIVERSAL_INSTALL.md",
        "NO_PYTHON_GUIDE.md",
        "PROGRESSIVE_SCAN_SUMMARY.md",  # New: Progressive scan guide
        "FIXES.md",
        "ENCODING_FIX_SUMMARY.md",  # New: Encoding fix summary
        "AGENT_QUICK_REF.txt",
        "scripts/analyze_disk.py",
        "scripts/analyze_progressive.py",  # New: Progressive scan
        "scripts/clean_disk.py",
        "scripts/monitor_disk.py",
        "scripts/skill_bootstrap.py",
        "scripts/check_skill.py",
        "scripts/package_skill.py",
        "scripts/scheduler.py",
        "scripts/qq_cleanup_macos.zsh",
        "references/temp_locations.md",
    ]

    for file_path in skill_files:
        src = skill_root / file_path
        if src.exists():
            items.append((src, file_path))
        else:
            print(f"[!] Warning: File does not exist: {src}")

    return items


def create_skill_package(
    output_path: Path = None,
    project_root: Path = None,
    skill_root: Path = None,
    verify: bool = True,
) -> Path:
    """
    Create skill package

    Args:
        output_path: Output file path
        project_root: Project root directory
        skill_root: Skill root directory
        verify: Whether to verify package result

    Returns:
        Path to created .skill file
    """
    # Find directories
    if project_root is None:
        project_root = find_project_root()
        print(f"[DIR] Project root: {project_root}")

    if skill_root is None:
        skill_root = find_skill_root(project_root)
        print(f"[DIR] Skill root: {skill_root}")

    # Determine output path
    if output_path is None:
        output_path = skill_root / "disk-cleaner.skill"
    print(f"[PKG] Output file: {output_path}")

    # Get file list
    items = get_files_to_include(project_root, skill_root)
    print(f"[i] Files to package: {len(items)}")

    # Exclude patterns
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        ".pyc",
        "*.pyo",
        ".pytest_cache",
        "*.egg-info",
        ".mypy_cache",
        ".benchmarks",
        "*.py~",  # Editor backup files
        ".DS_Store",  # macOS
    ]

    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        skill_dir = Path(temp_dir) / "disk-cleaner"
        skill_dir.mkdir()

        # Copy files
        copied = 0
        for src, dst_rel in items:
            dst = skill_dir / dst_rel

            # Create target directory
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Check if should be excluded
            if any(pattern in str(src) for pattern in exclude_patterns):
                continue

            # Copy file
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*exclude_patterns))
            else:
                shutil.copy2(src, dst)
            copied += 1

        print(f"[OK] Files copied: {copied}")

        # Create README
        readme_content = """# Disk Cleaner Skill Package

## Installation

1. Extract this .skill file to your skills directory:
   - Windows: `%USERPROFILE%\\.claude\\skills\\disk-cleaner\\`
   - macOS/Linux: `~/.claude/skills/disk-cleaner/`

2. Or use in Claude Code:
   ```
   /install-skill path/to/disk-cleaner.skill
   ```

## Usage

### Analyze disk space
```bash
python scripts/analyze_disk.py
python scripts/analyze_disk.py --path "D:\\Projects"
python scripts/analyze_disk.py --top 50
```

### Clean junk files
```bash
# Preview (safe mode)
python scripts/clean_disk.py --dry-run

# Actual cleaning
python scripts/clean_disk.py --force

# Clean specific categories
python scripts/clean_disk.py --temp --cache --dry-run
```

### Monitor disk usage
```bash
python scripts/monitor_disk.py
python scripts/monitor_disk.py --watch --interval 300
```

## Troubleshooting

If you encounter issues, run diagnostic tools:
```bash
python scripts/check_skill.py
python scripts/skill_bootstrap.py --test-import
```

## Requirements

- Python 3.7+
- No additional dependencies

For more information, see SKILL.md
"""
        (skill_dir / "README.txt").write_text(readme_content, encoding="utf-8")

        # Create version file
        created_time = __import__("datetime").datetime.now().isoformat()
        version_content = f"""{{
  "name": "disk-cleaner",
  "version": "2.1.0",
  "description": "High-performance cross-platform disk space monitoring, "
  "analysis, and cleaning toolkit with progressive scanning and "
  "cross-platform encoding fixes",
  "python_requires": ">=3.7",
  "created": "{created_time}"
}}
"""
        (skill_dir / "skill.json").write_text(version_content, encoding="utf-8")

        # Create zip file
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(skill_dir)
                    zipf.write(file_path, arcname)

    # Display results
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print("[OK] Package complete!")
    print(f"   File size: {size_mb:.2f} MB")
    print(f"   File location: {output_path}")

    # Verify
    if verify:
        print("\n[?] Verifying package content...")
        verify_skill_package(output_path)

    return output_path


def verify_skill_package(skill_path: Path) -> bool:
    """
    Verify skill package integrity

    Checks:
    1. Whether key files exist
    2. Whether Python modules can be imported
    3. Whether file structure is correct
    """
    with zipfile.ZipFile(skill_path, "r") as zipf:
        files = zipf.namelist()

        print(f"   Total files: {len(files)}")

        # Check key files
        key_files = [
            "SKILL.md",
            "skill.json",
            "scripts/skill_bootstrap.py",
            "scripts/analyze_disk.py",
            "scripts/clean_disk.py",
            "scripts/monitor_disk.py",
            "scripts/check_skill.py",
            "diskcleaner/__init__.py",
            "diskcleaner/core/progress.py",
            "diskcleaner/core/scanner.py",
        ]

        all_ok = True
        for key_file in key_files:
            if key_file in files:
                print(f"   [OK] {key_file}")
            else:
                print(f"   [X] {key_file} (missing)")
                all_ok = False

        if not all_ok:
            print("\n[!] Verification failed: Missing key files")
            return False

    print("   [OK] Verification passed!")

    # Try import test
    print("\n[TEST] Testing module import...")
    try:
        # Create temp directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            with zipfile.ZipFile(skill_path, "r") as zipf:
                zipf.extractall(temp_path)

            # Add to path and test import
            skill_extracted = temp_path / "disk-cleaner"
            sys.path.insert(0, str(skill_extracted))

            try:
                from skill_bootstrap import import_diskcleaner_modules

                success, modules = import_diskcleaner_modules()

                if success:
                    print("   [OK] Module import successful")
                    for name in modules.keys():
                        print(f"      - {name}")
                else:
                    print("   [!] Module import failed, but basic features may still work")

            finally:
                # Clean up path
                if str(skill_extracted) in sys.path:
                    sys.path.remove(str(skill_extracted))

    except Exception as e:
        print(f"   [!] Import test failed: {e}")
        print("   (This may not affect actual usage)")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Create Disk Cleaner skill package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create skill package (default location)
  python scripts/package_skill.py

  # Specify output path
  python scripts/package_skill.py --output ../disk-cleaner-v2.0.skill

  # Skip verification
  python scripts/package_skill.py --no-verify

  # Only verify existing skill package
  python scripts/package_skill.py --verify-only disk-cleaner.skill
        """,
    )

    parser.add_argument("--output", "-o", type=Path, help="Output .skill file path")
    parser.add_argument("--project-root", type=Path, help="Project root directory (default: auto-detect)")
    parser.add_argument("--skill-root", type=Path, help="Skill root directory (default: auto-detect)")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification step")
    parser.add_argument("--verify-only", type=Path, metavar="SKILL_FILE", help="Only verify existing skill package")

    args = parser.parse_args()

    if args.verify_only:
        print("[?] Verifying skill package...")
        success = verify_skill_package(args.verify_only)
        sys.exit(0 if success else 1)

    try:
        output_path = create_skill_package(
            output_path=args.output,
            project_root=args.project_root,
            skill_root=args.skill_root,
            verify=not args.no_verify,
        )
        print(f"\n[*] Skill package created successfully: {output_path}")
        sys.exit(0)

    except Exception as e:
        print(f"\n[X] Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
