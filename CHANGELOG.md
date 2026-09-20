# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Directory sizing undercounted deep trees** - `DiskAnalyzer._get_dir_size_fast`
  defaulted to `max_depth=1`, so the "Largest Directories" ranking stopped
  measuring after two levels and reported deeply nested content (Wine prefixes,
  `node_modules`, game installs) as near-zero. The size walk now defaults to the
  full tree; an explicit `max_depth` still bounds it for shallow estimates.

## [2.0.0] - 2025-01-22

### Added

#### Core Functionality
- **Smart Cleanup Engine** - Intelligent 3D file classification (type × risk × age)
- **Duplicate Detection** - Adaptive strategy automatically switches between fast and accurate modes
- **Incremental Scanning** - Cache-based optimization for 10x faster repeated scans
- **File Lock Detection** - Cross-platform file locking detection (handle.exe/lsof)
- **Process Manager** - Safe process termination for locked files
- **Interactive UI** - 5 view modes (by type, risk, age, duplicates, detailed)
- **Safety Checker** - Protected paths, file extensions, and 'YES' confirmation mechanism
- **Backup & Logging** - Automatic backup and cleanup logging

#### Platform-Specific Features
- **Windows Platform**
  - Windows Update cache detection
  - Recycle Bin cleanup
  - Prefetch cache management
  - Docker Desktop integration

- **Linux Platform**
  - Package manager cache cleanup (APT, YUM, DNF, Pacman)
  - Systemd journal log management
  - Old kernel version detection
  - Snap cache cleanup

- **macOS Platform**
  - Homebrew cache cleanup
  - Xcode derived data cleanup
  - iOS device backup detection
  - Thumbnail cache management

#### Automation
- **Scheduler** - Automated cleanup task scheduling
- **Task Persistence** - JSON-based task configuration
- **Multiple Cleanup Types** - smart, temp, cache, logs
- **Interval Scheduling** - Configurable time intervals (e.g., "24h")

### Changed
- **Refactored Architecture** - Modular design with `diskcleaner/` package
- **Enhanced Scripts** - All scripts now use core engine for consistency
- **Improved Safety** - Default dry-run mode, explicit confirmation required
- **Better Error Handling** - Comprehensive error messages and graceful failures
- **Cross-Platform** - Ensured Windows, Linux, macOS parity

### Testing
- **66 Test Cases** - Comprehensive test coverage
- **Platform Tests** - 17 cross-platform tests with appropriate skipif decorators
- **Integration Tests** - End-to-end workflow testing
- **100% Pass Rate** - All tests passing on all platforms

### Documentation
- **Enhanced README** - Updated with v2.0 features and examples
- **Usage Examples** - Added Python API examples
- **Platform Guides** - Platform-specific cleanup instructions
- **CHANGELOG** - This file

### Performance
- **10x Faster** - Incremental scanning on repeated runs
- **Adaptive Strategy** - Automatic optimization based on file count
- **Efficient Memory** - Streaming file processing for large directories

### Security
- **Protected Paths** - System directories, user profiles protected by default
- **Protected Extensions** - Executables, system files never deleted
- **File Lock Detection** - Prevents deletion of in-use files
- **Backup Before Delete** - Optional backup of files before deletion
- **Audit Logging** - Complete cleanup trail for accountability

### Developer Experience
- **Zero Dependencies** - Pure Python standard library
- **Type Hints** - Full type annotations for IDE support
- **Modular Design** - Easy to extend and customize
- **Well-Tested** - Comprehensive test suite with >54% coverage
- **CI/CD** - GitHub Actions for all platforms and Python versions

## [1.0.0] - Previous Release

### Features
- Basic disk space analysis
- Simple junk file cleaning
- Disk usage monitoring
- Cross-platform support (Windows, Linux, macOS)
