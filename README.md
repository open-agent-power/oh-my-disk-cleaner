<p align="center">
  <img src="logo.png" alt="Disk Cleaner Logo" width="180">
</p>

# Disk Cleaner v2.1 - Intelligent Cross-Platform Disk Management

**[English](README.md)** | **[中文文档](README_zh.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/gccszs/disk-cleaner)
[![Skill](https://img.shields.io/badge/skill-add--skill-blue)](https://github.com/gccszs/disk-cleaner)

A comprehensive cross-platform disk space monitoring, analysis, and intelligent cleaning toolkit. Features advanced 3D file classification, duplicate detection, automated scheduling, and platform-specific optimization.

## ⚡ Quick Install

### Option 1: Install as Agent Skill (Recommended)

Install directly from CLI:

```bash
npx add-skill gccszs/disk-cleaner
```
OR
```bash
npx skills add gccszs/disk-cleaner
```

This will install the skill with all necessary files. The `.skill` package contains only the essential components:
- ✅ Core modules (`diskcleaner/`)
- ✅ Executable scripts (`scripts/`)
- ✅ Skill definition (`SKILL.md`)
- ✅ Reference documentation (`references/`)

**Note:** The skill package excludes tests, CI/CD configs, and development files for a clean, minimal installation.

### Option 2: Clone Repository

For development or standalone use:

```bash
git clone https://github.com/gccszs/disk-cleaner.git
cd disk-cleaner
```

See [Usage](#usage-examples) section for how to run the scripts.

---

## ✨ v2.1 New Features

### 🚀 Critical Cross-Platform Encoding Fix
- **✅ ASCII-Safe Output** - All scripts use ASCII characters for 100% cross-platform compatibility
- **🌐 Universal Console Support** - Works on Windows GBK, Linux UTF-8, macOS UTF-8, and any other encoding
- **🛡️ No Encoding Errors** - Eliminates UnicodeEncodeError on all platforms
- **📝 Smart Emoji Policy** - Scripts use ASCII, Agents can use emojis when reporting to users

### ⚡ Progressive Scanning for Large Disks
- **🔍 Quick Sample Mode** - Estimate disk size and scan time in just 1 second
- **📊 Progressive Scan Mode** - Get partial results in 30 seconds for large disks (500GB+)
- **⏱️ Smart Time Limits** - Prevent users from waiting hours for full scans
- **🔄 Real-Time Feedback** - Progress updates every 2 seconds
- **⏸️ Interruptible** - Press Ctrl+C to get partial results anytime

### 🤖 Intelligent Bootstrap System
- **📍 Auto Location Detection** - Automatically searches 20+ common skill package locations
- **🔧 Environment Variable Support** - Override with `DISK_CLEANER_SKILL_PATH`
- **📦 Auto Module Import** - Automatically imports diskcleaner modules with fallbacks
- **🌍 Cross-Platform Python Detection** - Tries both `python` and `python3`
- **🛠️ Diagnostic Tool** - `check_skill.py` verifies all functionality

### 🎯 Advanced Performance Optimizations
- **⚡ QuickProfiler** - Fast sampling to estimate scan characteristics
- **🚀 ConcurrentScanner** - Multi-threaded I/O for 3-5x speedup
- **🔍 os.scandir() Optimization** - 3-5x faster than Path.glob
- **💾 IncrementalCache** - Cache scan results for faster repeat scans
- **🧠 Memory Monitoring** - Auto-adapts based on available memory
- **⏹️ Early Stopping** - Configurable file/time limits

### 🔧 Core v2.0 Features
- **🤖 Intelligent 3D Classification** - Files categorized by type, risk level, and age
- **🔍 Adaptive Duplicate Detection** - Fast/accurate strategies with automatic optimization
- **⚡ Incremental Scanning** - Cache-based performance optimization for repeated scans
- **🔒 Process-Aware Safety** - File lock detection and process termination
- **💻 Platform-Specific Optimization** - Windows Update, APT, Homebrew cache detection
- **⏰ Automated Scheduling** - Timer-based cleanup tasks
- **🎯 Interactive Cleanup UI** - 5 view modes with visual feedback
- **🛡️ Enhanced Safety** - Protected roots and extensions, explicit custom-path opt-in, exact-path confirmation, recursive previews

## Features

### Core Capabilities
- **Disk Space Analysis**: Identify large files and directories consuming disk space
- **Smart Cleanup**: AI-powered suggestions based on file patterns and usage
- **Duplicate Detection**: Find and remove duplicate files to reclaim space
- **Safe Junk Cleaning**: Remove temporary files, caches, logs with built-in safety mechanisms
- **Disk Monitoring**: Real-time monitoring with configurable alert thresholds
- **Cross-Platform**: Full support for Windows, Linux, and macOS
- **Zero Dependencies**: Pure Python standard library implementation

### Advanced Features
- **3D File Classification**: Type × Risk × Age matrix for smart decisions
- **Incremental Scanning**: Only scan changed files for 10x faster subsequent scans
- **File Lock Detection**: Prevents deletion of locked files on all platforms
- **Platform-Specific Cleanup**: Windows Update, Linux package caches, macOS Xcode derived data
- **Automated Scheduling**: Set up recurring cleanup tasks with custom intervals
- **Interactive Selection**: Choose exactly what to clean with detailed previews

## Quick Start

### Prerequisites

Python 3.7 or higher (no external dependencies required - uses only standard library).

### Basic Usage

```bash
# Quick sample mode (1 second) - NEW v2.0
python skills/disk-cleaner/scripts/analyze_disk.py --sample

# Progressive scanning for large disks - NEW v2.0
python skills/disk-cleaner/scripts/analyze_progressive.py --max-seconds 30

# Verify skill package - NEW v2.0
python skills/disk-cleaner/scripts/check_skill.py

# Analyze disk space (with smart defaults)
python skills/disk-cleaner/scripts/analyze_disk.py

# Smart cleanup with duplicate detection (NEW v2.1)
python -c "from diskcleaner.core import SmartCleanupEngine; engine = SmartCleanupEngine('.'); print(engine.get_summary(engine.analyze()))"

# Preview cleanup (dry-run mode)
python skills/disk-cleaner/scripts/clean_disk.py --dry-run

# Monitor disk usage
python skills/disk-cleaner/scripts/monitor_disk.py

# Continuous monitoring
python skills/disk-cleaner/scripts/monitor_disk.py --watch
```

### v2.1 Advanced Usage

```bash
# Quick sample (estimate scan time) - NEW v2.0
python skills/disk-cleaner/scripts/analyze_disk.py --sample --json

# Progressive scanning (30-second limit) - NEW v2.0
python skills/disk-cleaner/scripts/analyze_progressive.py --max-seconds 30

# Progressive scanning (file limit) - NEW v2.0
python skills/disk-cleaner/scripts/analyze_progressive.py --max-files 50000

# Schedule automated cleanup (NEW v2.0)
python skills/disk-cleaner/scripts/scheduler.py add "Daily Cleanup" /tmp 24h --type smart
python skills/disk-cleaner/scripts/scheduler.py run  # Run due tasks

# Platform-specific cleanup suggestions
python -c "from diskcleaner.platforms import WindowsPlatform; import pprint; pprint.pprint(WindowsPlatform.get_system_maintenance_items())"
```

## Usage Examples

### Example 1: Smart Cleanup with Duplicate Detection

```python
from diskcleaner.core import SmartCleanupEngine

# Initialize engine
engine = SmartCleanupEngine("/path/to/clean", cache_enabled=True)

# Analyze directory
report = engine.analyze(
    include_duplicates=True,
    safety_check=True
)

# Get summary
print(engine.get_summary(report))

# Interactive cleanup (if you want)
from diskcleaner.core import InteractiveCleanupUI
ui = InteractiveCleanupUI(report)
ui.display_menu()  # Shows 5 view options
```

### Example 2: Automated Scheduling

```bash
# Add daily cleanup task
python skills/disk-cleaner/scripts/scheduler.py add "Daily Temp Cleanup" /tmp 24h --type temp

# List all scheduled tasks
python skills/disk-cleaner/scripts/scheduler.py list

# Run due tasks (dry-run by default)
python skills/disk-cleaner/scripts/scheduler.py run

# Run with actual deletion
python skills/disk-cleaner/scripts/scheduler.py run --force
```

### Example 3: Platform-Specific Cleanup

```python
from diskcleaner.platforms import WindowsPlatform, LinuxPlatform, MacOSPlatform
import platform

if platform.system() == "Windows":
    platform_impl = WindowsPlatform()
elif platform.system() == "Linux":
    platform_impl = LinuxPlatform()
else:
    platform_impl = MacOSPlatform()

# Get platform-specific cleanup suggestions
items = platform_impl.get_system_maintenance_items()
for key, item in items.items():
    print(f"{item['name']}: {item['description']}")
    print(f"  Risk: {item['risk']}, Size: {item['size_hint']}")
```

## Installation

### Quick Install (Recommended)

Install directly from GitHub using Vercel's add-skill CLI:

```bash
npx add-skill gccszs/disk-cleaner -g
```

Replace `gccszs` with your actual GitHub username.

### As a Claude Code Skill (Manual)

1. Download `disk-cleaner.skill` from the [Releases](https://github.com/gccszs/disk-cleaner/releases) page
2. Install via Claude Code:
   ```
   /skill install path/to/disk-cleaner.skill
   ```

### Standalone Usage

```bash
# Clone the repository
git clone https://github.com/gccszs/disk-cleaner.git
cd disk-cleaner

# Scripts are ready to use (no dependencies needed)
python skills/disk-cleaner/scripts/analyze_disk.py
```

## Usage Examples

### Disk Space Analysis

```bash
# Analyze current drive (C:\ on Windows, / on Unix)
python skills/disk-cleaner/scripts/analyze_disk.py

# Analyze specific path
python skills/disk-cleaner/scripts/analyze_disk.py --path "D:\Projects"

# Get top 50 largest items
python skills/disk-cleaner/scripts/analyze_disk.py --top 50

# Output as JSON for automation
python skills/disk-cleaner/scripts/analyze_disk.py --json

# Save report to file
python skills/disk-cleaner/scripts/analyze_disk.py --output disk_report.json
```

### Cleaning Junk Files

**IMPORTANT**: Always run with `--dry-run` first to preview changes!

```bash
# Preview cleanup (recommended first step)
python skills/disk-cleaner/scripts/clean_disk.py --dry-run

# Actually clean files
python skills/disk-cleaner/scripts/clean_disk.py --force

# Clean specific categories
python skills/disk-cleaner/scripts/clean_disk.py --temp       # Clean temp files only
python skills/disk-cleaner/scripts/clean_disk.py --cache      # Clean cache only
python skills/disk-cleaner/scripts/clean_disk.py --logs       # Clean logs only
python skills/disk-cleaner/scripts/clean_disk.py --recycle    # Clean recycle bin only
python skills/disk-cleaner/scripts/clean_disk.py --downloads 90  # Clean downloads older than 90 days
```

### Disk Monitoring

```bash
# Check current status
python skills/disk-cleaner/scripts/monitor_disk.py

# Continuous monitoring (every 60 seconds)
python skills/disk-cleaner/scripts/monitor_disk.py --watch

# Custom thresholds
python skills/disk-cleaner/scripts/monitor_disk.py --warning 70 --critical 85

# Alert mode (CI/CD friendly - exit codes based on status)
python skills/disk-cleaner/scripts/monitor_disk.py --alerts-only

# Custom monitoring interval (5 minutes)
python skills/disk-cleaner/scripts/monitor_disk.py --watch --interval 300
```

## Scripts Reference

### `analyze_disk.py`

Disk space analysis tool with progressive scanning support (v2.0+).

**New in v2.0:**
- **Quick Sample Mode** (`--sample`): 1-second estimation of scan time
- **Smart Limits**: Default 50,000 files, 30 seconds for large disks
- **Progressive Display**: Real-time feedback during scanning
- **Auto-Sampling**: Automatically suggests scan mode based on disk size

**Capabilities:**
- Scan directories to find largest files and folders
- Analyze temporary file locations
- Calculate disk usage statistics
- Generate detailed reports

### `analyze_progressive.py` (NEW v2.0)

Progressive scanning tool specifically designed for large disks.

**Features:**
- **Quick Sample** (`--sample`): 1-second estimation
- **Progressive Scan** (`--max-seconds`): Get results in 30 seconds
- **File Limit** (`--max-files`): Limit scan to specific file count
- **Real-Time Progress**: Updates every 2 seconds
- **Interruptible**: Press Ctrl+C for partial results

**Usage:**
```bash
# Quick sample
python skills/disk-cleaner/scripts/analyze_progressive.py --sample

# 30-second progressive scan
python skills/disk-cleaner/scripts/analyze_progressive.py --max-seconds 30

# Limit file count
python skills/disk-cleaner/scripts/analyze_progressive.py --max-files 50000
```

### `check_skill.py` (NEW v2.0)

Diagnostic tool to verify skill package functionality.

**Checks:**
- Python version and platform
- File structure integrity
- Module imports
- File permissions
- Script execution

**Usage:**
```bash
python skills/disk-cleaner/scripts/check_skill.py
```

### `skill_bootstrap.py` (NEW v2.0)

Intelligent bootstrap module for automatic environment setup.

**Features:**
- Auto-detects skill package location (20+ locations)
- Automatically imports diskcleaner modules
- Cross-platform encoding handling
- Graceful fallbacks for errors

**Usage:**
```python
from skill_bootstrap import import_diskcleaner_modules

success, modules = import_diskcleaner_modules()
if success:
    ProgressBar = modules['ProgressBar']
    DirectoryScanner = modules['DirectoryScanner']
```

### `clean_disk.py`

Safe junk file removal with multiple safety mechanisms.

**Safety Features:**
- Protected paths (never deletes system directories)
- Protected extensions skip matching top-level entries
- Filesystem and home/profile roots are always rejected
- Custom paths use a junk-directory allowlist and exact-path confirmation
- Dry-run mode by default
- Recursive preview sizing matches the execution selection

**Categories Cleaned:**
- **temp**: Temporary files (%TEMP%, /tmp, etc.)
- **cache**: Application and browser caches
- **logs**: Log files (older than 30 days default)
- **recycle**: Recycle bin / trash
- **downloads**: Old download files (configurable age)

### `monitor_disk.py`

Continuous or one-shot disk usage monitoring.

**Features:**
- Multi-drive monitoring (all mount points)
- Configurable warning/critical thresholds
- Continuous monitoring mode with alerts
- JSON output for automation
- Non-zero exit codes for CI/CD integration

**Exit Codes:**
- `0`: All drives OK
- `1`: Warning threshold exceeded
- `2`: Critical threshold exceeded

## Platform Support

| Feature | Windows | Linux | macOS |
|---------|---------|-------|-------|
| Disk Analysis | ✅ | ✅ | ✅ |
| Progressive Scanning (NEW) | ✅ | ✅ | ✅ |
| Quick Sample Mode (NEW) | ✅ | ✅ | ✅ |
| Temp Cleaning | ✅ | ✅ | ✅ |
| Cache Cleaning | ✅ | ✅ | ✅ |
| Log Cleaning | ✅ | ✅ | ✅ |
| Recycle Bin | ✅ | ✅ | ✅ |
| Real-time Monitoring | ✅ | ✅ | ✅ |
| GBK Console Support (NEW) | ✅ | N/A | N/A |
| UTF-8 Console Support | ✅ | ✅ | ✅ |

### Windows-Specific Locations
- `%TEMP%`, `%TMP%`, `%LOCALAPPDATA%\Temp`
- `C:\Windows\Temp`, `C:\Windows\Prefetch`
- `C:\Windows\SoftwareDistribution\Download`
- Browser caches (Chrome, Edge, Firefox)
- Development tool caches (npm, pip, Gradle, Maven)

### Linux-Specific Locations
- `/tmp`, `/var/tmp`, `/var/cache`
- Package manager caches (apt, dnf, pacman)
- Browser caches
- Development tool caches

### macOS-Specific Locations
- `/tmp`, `/private/tmp`, `/var/folders`
- `~/Library/Caches`, `~/Library/Logs`
- iOS device backups
- Homebrew cache

## Safety Features

### Protected Paths
System directories are never touched:
- Windows: `C:\Windows`, `C:\Program Files`, `C:\ProgramData`
- Linux/macOS: `/usr`, `/bin`, `/sbin`, `/System`, `/Library`

### Custom `--path` Boundary

`--path` removes matching child directories recursively. Filesystem roots and
the current home/profile root are rejected. Targets named `cache`, `tmp`,
`temp`, `logs`, `trash`, `recycle`, or `downloads` are accepted by default.
Other target names and junk-named directories containing project markers
require `--allow-unsafe-path`. Actual custom-path deletion also requires
`--confirm-path` with the resolved absolute target. The validated root identity
is checked again immediately before cleanup. Dry-run sizing measures directory
contents recursively and treats symbolic links and Windows reparse points as
leaf entries. Cleanup errors remain visible in the report and produce a nonzero
exit status.

```bash
# Preview a recognized junk directory
python skills/disk-cleaner/scripts/clean_disk.py --path "D:/Temp" --dry-run

# Execute after confirming the exact target
python skills/disk-cleaner/scripts/clean_disk.py --path "D:/Temp" --force \
  --confirm-path "D:/Temp"

# Select an arbitrary directory through the explicit opt-in
python skills/disk-cleaner/scripts/clean_disk.py --path "D:/BuildOutput" \
  --allow-unsafe-path --force --confirm-path "D:/BuildOutput"
```

### Protected Extensions
Protected extensions apply to matching top-level entries. A selected directory
is removed recursively with its contents.
```
.exe, .dll, .sys, .drv, .bat, .cmd, .ps1, .sh, .bash, .zsh,
.app, .dmg, .pkg, .deb, .rpm, .msi, .iso, .vhd, .vhdx
```

## Use Cases

### 1. Free Up C Drive Space on Windows
```bash
# Analyze what's taking space
python skills/disk-cleaner/scripts/analyze_disk.py

# Preview cleanup
python skills/disk-cleaner/scripts/clean_disk.py --dry-run

# Execute cleanup
python skills/disk-cleaner/scripts/clean_disk.py --force
```

### 2. Automated Disk Monitoring
```bash
# Run in background with custom thresholds
python skills/disk-cleaner/scripts/monitor_disk.py --watch --warning 70 --critical 85 --interval 300
```

### 3. CI/CD Integration
```bash
# Check disk space in pipeline
python skills/disk-cleaner/scripts/monitor_disk.py --alerts-only --json

# Exit codes: 0=OK, 1=WARNING, 2=CRITICAL
if [ $? -ne 0 ]; then
  echo "Disk space issue detected!"
fi
```

## Development

### Project Structure
```
disk-cleaner/
├── skills/                   # Skills marketplace directory
│   └── disk-cleaner/
│       ├── SKILL.md          # Complete skill guide (v2.0)
│       ├── ENCODING_FIX_SUMMARY.md    # Encoding fix documentation (NEW)
│       ├── PROGRESSIVE_SCAN_SUMMARY.md # Progressive scanning guide (NEW)
│       ├── UNIVERSAL_INSTALL.md       # Universal installation guide (NEW)
│       ├── NO_PYTHON_GUIDE.md         # Guide for users without Python (NEW)
│       ├── FIXES.md                  # v2.0 fixes list (NEW)
│       ├── AGENT_QUICK_REF.txt       # Agent quick reference (NEW)
│       ├── README.md         # Skill documentation
│       ├── diskcleaner.skill # Self-contained skill package (v2.0)
│       ├── scripts/          # Executable scripts
│       │   ├── analyze_disk.py       # Enhanced with progressive scanning
│       │   ├── analyze_progressive.py # NEW: Progressive scanning
│       │   ├── clean_disk.py          # Safe cleanup
│       │   ├── monitor_disk.py        # Disk monitoring
│       │   ├── scheduler.py           # Automated scheduling
│       │   ├── check_skill.py         # NEW: Diagnostic tool
│       │   ├── skill_bootstrap.py     # NEW: Intelligent bootstrap
│       │   └── package_skill.py       # Package creation tool
│       ├── diskcleaner/      # Core Python module (self-contained)
│       │   ├── core/         # Core functionality
│       │   ├── optimization/ # Performance optimizations (v2.0)
│       │   ├── platforms/    # Platform-specific code
│       │   └── config/       # Configuration
│       └── references/       # Reference documentation
│           └── temp_locations.md
├── tests/                    # Test suite (244 tests)
└── docs/                     # Additional documentation
```

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool modifies files on your system. Always:
1. Review the dry-run output before actual cleaning
2. Backup important data before cleanup
3. Use at your own risk

The authors are not responsible for any data loss or system issues.

## Acknowledgments

- Built as a [Claude Code Skill](https://claude.com/claude-code)
- Installable via [Vercel's add-skill CLI](https://github.com/vercel/vercel/tree/main/packages/add-skill)
- Cross-platform compatibility tested on Windows 10/11, Ubuntu 20.04+, macOS 12+
