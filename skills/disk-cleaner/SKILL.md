---
name: disk-cleaner
description: "Cross-platform disk space management toolkit with intelligent optimization. REQUIREMENTS: Python 3.7+. UNIVERSAL COMPATIBILITY: Works with ALL AI IDEs (Cursor, Windsurf, Continue, Aider, Claude Code, etc.). PLATFORM-INDEPENDENT: Works at any location - global, project, or user level. SELF-CONTAINED: No pip install needed, includes intelligent bootstrap. KEY FEATURES: (1) PROGRESSIVE SCANNING: Quick sample (1s) + Progressive mode for large disks, (2) INTELLIGENT BOOTSTRAP: Auto-detection of skill location and auto-import of modules, (3) CROSS-PLATFORM ENCODING: Safe emoji/Unicode handling on all platforms, (4) DIAGNOSTIC TOOLS: check_skill.py for quick verification, (5) OPTIMIZED SCANNING: 3-5x faster with os.scandir(), concurrent scanning, intelligent sampling. AGENT WORKFLOW: (1) Check Python, (2) Find skill package (20+ locations auto-detected), (3) Run diagnostics, (4) Use progressive scanning for large disks. The skill package includes all optimization modules - no features are lost!"
---

# Disk Cleaner Skill - Complete Feature Guide for All Agents

## 🚨 IMPORTANT: Emoji Usage Policy

### For Script Output (Cross-Platform Safety)
- **NEVER use emoji in script output** - All scripts use ASCII-safe characters
- Scripts use: `[OK]`, `[X]`, `[!]`, `[*]`, `[i]`, `[DIR]`, `[FILE]`, `[PKG]`, `[x]`
- This ensures compatibility with Windows GBK and other non-UTF-8 consoles
- **DO NOT modify script output to add emoji** - This will break cross-platform compatibility

### For Agent-to-Human Communication (Recommended)
- **SHOULD use emoji when reporting results to humans** - Makes output more readable
- Use these emoji in your final reports to users:
  - `✅` (Success) - Completed operations, successful scans
  - `❌` (Error) - Failed operations, critical errors
  - `⚠️` (Warning) - Warnings, issues that need attention
  - `🔍` (Scanning) - Search/scan operations
  - `📊` (Statistics) - Analysis results, statistics
  - `📁` (Directory) - Directory-related information
  - `📦` (Package) - Package/module information
  - `🎉` (Success) - Celebratory messages for successful completion
  - `🚨` (Critical) - Critical warnings
  - `💡` (Tip) - Suggestions, recommendations
  - `📋` (List) - Checklists, summaries
  - `🔧` (Tool) - Tools, utilities
  - `🌐` (Global) - Cross-platform, universal features
  - `🛡️` (Safety) - Safety-related information
  - `⚡` (Performance) - Performance improvements
  - `📝` (Document) - Documentation
  - `🎓` (Learning) - Educational content
  - `📞` (Support) - Help, support information
  - `📈` (Growth) - Improvements, gains
  - `🎯` (Target) - Goals, objectives
  - `🚀` (Launch) - Quick start, fast operations
  - `🛠️` (Tools) - Tool-related features

**Example:**
```
Script output (ASCII):    [OK] Scan completed: 50,000 files in 30 seconds
Your report to human:     ✅ Scan completed successfully! Found 50,000 files in 30 seconds
```

---

## 📦 COMPLETE FEATURE LIST (READ THIS FIRST!)

### 🚨 CRITICAL: Progressive Scanning (MANDATORY for Large Disks)
- ✅ **Quick Sample Mode**: 1-second estimation of disk size and scan time
- ✅ **Progressive Scan Mode**: Get partial results in 30 seconds for large disks
- ✅ **Smart Time Limits**: Prevent users from waiting hours
- ✅ **Real-time Feedback**: Progress updates every 2 seconds
- ✅ **Interruptible**: Ctrl+C to get partial results

### 🔧 Intelligent Bootstrap (Auto-Detection & Import)
- ✅ **Auto Location Detection**: Searches 20+ common skill package locations
- ✅ **Environment Variable Support**: DISK_CLEANER_SKILL_PATH override
- ✅ **Auto Module Import**: Automatically imports diskcleaner modules
- ✅ **Fallback Mechanisms**: Works even if some features unavailable
- ✅ **Cross-Platform Python Detection**: Tries both 'python' and 'python3'

### 🌐 Universal Compatibility
- ✅ **All AI IDEs**: Cursor, Windsurf, Continue, Aider, Claude Code, etc.
- ✅ **All Platforms**: Windows, macOS, Linux (including Windows GBK console)
- ✅ **All Installation Levels**: Global, project, user level
- ✅ **No Configuration Needed**: Works out of the box
- ✅ **Cross-Platform Encoding**: All scripts use ASCII-safe output (v2.0+)

### 🛡️ Safety & Reliability
- ✅ **Diagnostic Tool**: check_skill.py - verifies all functionality
- ✅ **Safe Encoding**: All scripts use ASCII characters (no emoji in output)
- ✅ **Safe Defaults**: --dry-run for cleaning, smart limits for scanning
- ✅ **Protected Paths**: Never deletes system directories or executables
- ✅ **Error Handling**: Graceful degradation on errors
- ✅ **GBK/UTF-8 Compatible**: Works on Windows GBK, UTF-8, and all other encodings

### ⚡ Performance Optimizations (ALL INCLUDED)
- ✅ **QuickProfiler**: Fast sampling to estimate scan characteristics
- ✅ **ConcurrentScanner**: Multi-threaded I/O for 3-5x speedup
- ✅ **os.scandir() Optimization**: 3-5x faster than Path.glob
- ✅ **IncrementalCache**: Cache scan results for faster repeat scans
- ✅ **Memory Monitoring**: Auto-adapts based to available memory
- ✅ **Early Stopping**: Configurable file/time limits
- ✅ **Enhanced Cache Detection**: 26+ cache paths (was 8) - 225% improvement

### 🆕 v2.2+ New Features
- ✅ **Duplicate File Detection**: Find and remove duplicate files with adaptive strategies
- ✅ **Growth Trend Analysis**: Track disk usage over time, predict when disk will be full
- ✅ **Interactive Wizard**: Step-by-step guided cleanup with safety confirmations
- ✅ **File Organization**: Intelligent file archival and organization (4 strategies)
- ✅ **Enhanced Scan Limits**: 500K files (was 50K), 120s timeout (was 30s)
- ✅ **Deep Scan Mode**: `--deep-scan` for unlimited scanning
- ✅ **Windows Directory Support**: `--include-windows` for system directory scanning

### 📊 Available Scripts (13+ Total)
**Core Analysis:**
1. **analyze_disk.py** - Disk analysis with smart sampling (enhanced v2.2)
2. **analyze_progressive.py** - Progressive scanning for large disks
3. **find_duplicates.py** - Duplicate file detection (NEW v2.2)
4. **analyze_growth.py** - Growth trend analysis (NEW v2.2)

**Cleaning & Organization:**
5. **clean_disk.py** - Safe junk file cleaning (enhanced cache detection)
6. **interactive_wizard.py** - Interactive guided cleanup (NEW v2.2)
7. **organize_files.py** - File archival and organization (NEW v2.2)

**Monitoring & Diagnostics:**
8. **monitor_disk.py** - Disk usage monitoring
9. **check_skill.py** - Diagnostic tool

**Developer Tools:**
10. **skill_bootstrap.py** - Intelligent bootstrap module
11. **package_skill.py** - Package creation tool
12. **scheduler.py** - Automated scheduling

### macOS QQ media cleanup

Use `scripts/qq_cleanup_macos.zsh` when QQ pictures or emojis consume excessive
space on macOS and chat records must remain intact.

1. Audit QQ storage without changing files:

   ```zsh
   scripts/qq_cleanup_macos.zsh audit
   ```

2. Preview pictures and emojis older than 90 days:

   ```zsh
   scripts/qq_cleanup_macos.zsh clean --older-than-days 90 --categories Pic,Emoji
   ```

3. Report the preview and obtain explicit approval. Quit QQ, then repeat the
   approved command with `--execute`.

Never select `nt_db`, account roots, preferences, voice messages, videos, or
received files. The script accepts only `Pic` and `Emoji`, defaults to preview,
and refuses execution while QQ is running. Warn that removed local media might
no longer be available in old conversations.

### 🚀 Multi-Agent Acceleration (CRITICAL FOR PERFORMANCE)

**🎯 KEY INSIGHT: Use Sub-Agents for Parallel Processing**

This is one of the MOST POWERFUL features of disk-cleaner when used by AI Agents!

#### Why Use Multiple Agents?

Single-threaded scanning:
```
Agent scans → [Dir1] → [Dir2] → [Dir3] → ... (sequential, slow)
```

Multi-Agent parallel scanning:
```
Main Agent
  ├─ Sub-Agent-1 scans → [Dir1, Dir2, Dir3] (parallel)
  ├─ Sub-Agent-2 scans → [Dir4, Dir5, Dir6] (parallel)
  └─ Sub-Agent-3 scans → [Dir7, Dir8, Dir9] (parallel)
Result: 3-10x faster! ⚡
```

#### When to Use Multi-Agent Mode?

✅ **ALWAYS use when:**
- Scanning multiple top-level directories (e.g., C:\, D:\, E:\)
- Cleaning multiple user profiles
- Processing large file sets (>100K files)
- Time-critical operations

❌ **Don't use when:**
- Single small directory (<10K files)
- Quick analysis (<30 seconds)
- Simple cleanup tasks

#### How to Implement Multi-Agent Scanning

**Option 1: Use Agent Tool (Recommended for Claude Code)**

```python
# Agent code that spawns sub-agents
from anthropic import Anthropic

def parallel_scan_directories(directories_list):
    """
    Scan multiple directories in parallel using sub-agents
    """
    # Split directories among sub-agents (3-5 agents optimal)
    chunks = split_list(directories_list, n_chunks=3)
    
    # Launch sub-agents in parallel
    agents = []
    for i, chunk in enumerate(chunks):
        agent = Anthropic().agent.create(
            name=f"scanner-{i}",
            instructions=f"""
            Scan these directories: {chunk}
            Use disk-cleaner with: --file-limit 50000 --time-limit 60
            Return results in JSON format
            """,
            model="claude-sonnet-4-20250514"  # Fast model
        )
        agents.append(agent)
    
    # Wait for all agents and collect results
    results = [agent.wait() for agent in agents]
    return merge_results(results)
```

**Option 2: Parallel Subprocess (Platform Independent)**

```python
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def parallel_scan_subprocess(directories_list):
    """
    Scan multiple directories using parallel subprocess calls
    Works with ALL AI IDEs that support subprocess
    """
    def scan_directory(directory):
        """Scan a single directory"""
        cmd = [
            'python',
            'skills/disk-cleaner/scripts/analyze_disk.py',
            '--path', str(directory),
            '--file-limit', '50000',
            '--json'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    # Use 3-5 parallel workers
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(scan_directory, d): d
            for d in directories_list
        }
        
        results = {}
        for future in as_completed(futures):
            directory = futures[future]
            try:
                results[directory] = future.result()
            except Exception as e:
                results[directory] = {"error": str(e)}
    
    return results

# Usage: Scan C:\, D:\, E:\ in parallel
directories = ['C:\\', 'D:\\', 'E:\\']
results = parallel_scan_subprocess(directories)
```

**Option 3: Multi-Platform Agent Team (Advanced)**

For Agent-capable systems (Claude Code, Cursor with Agent support):

```python
# Create agent team for massive parallelism
def create_agent_team_scan(top_level_paths):
    """
    Create a team of sub-agents, each handling a portion of the work
    """
    team_config = {
        "name": "disk-cleaner-team",
        "members": [
            {
                "name": "scanner-1",
                "task": f"Scan {top_level_paths[0]} using progressive mode",
                "tool_use": "subprocess"
            },
            {
                "name": "scanner-2",
                "task": f"Scan {top_level_paths[1]} using progressive mode",
                "tool_use": "subprocess"
            },
            {
                "name": "scanner-3",
                "task": f"Scan {top_level_paths[2]} using progressive mode",
                "tool_use": "subprocess"
            }
        ],
        "coordination": "parallel",  # All run at once
        "aggregation": "merge_results"  # Combine results at end
    }
    
    return launch_agent_team(team_config)
```

#### Performance Comparison

| Scenario | Single Agent | 3 Sub-Agents | Speedup |
|----------|-------------|--------------|---------|
| 3 disks (1TB each) | ~15 minutes | ~5 minutes | **3x** |
| 10 user profiles | ~20 minutes | ~4 minutes | **5x** |
| 1M files | ~30 minutes | ~6 minutes | **5x** |
| Cache cleanup (26 locations) | ~8 minutes | ~2 minutes | **4x** |

#### Recommended Agent Count

- **Small job** (<50K files): 1 agent (not worth overhead)
- **Medium job** (50K-500K files): 2-3 agents
- **Large job** (500K-2M files): 3-5 agents
- **Massive job** (>2M files): 5-8 agents

**Sweet spot: 3-4 agents** (best balance of speed vs overhead)

#### Best Practices

1. **Divide work logically**: By disk, by user profile, by directory type
2. **Use consistent parameters**: All agents use same scan limits
3. **Merge results carefully**: Deduplicate, sort, format
4. **Handle failures gracefully**: If one agent fails, continue others
5. **Monitor progress**: Track which agents completed

⚠️ **IMPORTANT**: Not all AI IDEs support sub-agents. Fall back to parallel subprocess if unavailable.

### 📚 Documentation (Essential Files Only)
- SKILL.md - This complete guide (READ THIS FIRST)
- README.md - Project overview and quick start
- README_zh.md - Chinese documentation
- CHANGELOG.md - Version history and changes
- AGENT_QUICK_REF.txt - One-page reference for agents
- INSTALL.md - Detailed installation guide
- NO_PYTHON_GUIDE.md - Help for users without Python
- references/temp_locations.md - Platform-specific cache locations

---

## 🎯 AGENT CHECKLIST (Must Follow)

### For ANY Disk Analysis Request:

```
[ ] STEP 1: Check Python availability
[ ] STEP 2: Find skill package (auto-detects 20+ locations)
[ ] STEP 3: Run diagnostics: python scripts/check_skill.py
[ ] STEP 4: Run quick sample: --sample (MANDATORY - do this FIRST)
[ ] STEP 5: Choose scan mode based on estimate
[ ] STEP 6: Inform user of expected time
[ ] STEP 7: Execute scan with appropriate limits
[ ] STEP 8: Show results and offer next steps
```

### For ANY Clean Request:

```
[ ] STEP 1-3: Same as above
[ ] STEP 4: ALWAYS use --dry-run first (MANDATORY)
[ ] STEP 5: Show preview results
[ ] STEP 6: Ask user confirmation before --force
[ ] STEP 7: Execute actual cleaning if confirmed
```

---

## ⚡ PROGRESSIVE SCANNING (CRITICAL FOR LARGE DISKS)

## 🚨 CRITICAL INFORMATION (Read First)

### Universal Compatibility
- ✅ **Works with ALL AI IDEs**: Cursor, Windsurf, Continue, Aider, Claude Code, etc.
- ✅ **Platform Independent**: Windows, macOS, Linux
- ✅ **Installation Agnostic**: Works at global, project, or user level
- ✅ **Self-Contained**: No external dependencies, just Python 3.7+

### The Only Requirement
```python
import subprocess
result = subprocess.run(['python', '--version'], capture_output=True, text=True)
# If this succeeds, you can use this skill
```

---

## ⚡ PROGRESSIVE SCANNING (CRITICAL FOR LARGE DISKS)

### 🚨 AGENT MUST USE FOR LARGE DISKS (>100GB)

**Problem**: Full disk scan on large disks (500GB+) can take HOURS. Users will lose patience.

**Solution**: Use progressive scanning - get results in seconds, not hours!

### 📋 Three Scanning Modes

#### Mode 1: Quick Sample (⚡ FASTEST - 1 Second)

**When to use**: Get instant estimate of directory size and scan time

```bash
python scripts/analyze_disk.py --sample
# OR
python scripts/analyze_progressive.py --sample
```

**Output**:
```json
{
  "sample_file_count": 7591,
  "sample_size_gb": 17.62,
  "files_per_second": 7501.0,
  "estimated_time_seconds": 2.0
}
```

**Agent Decision Logic**:
```python
# ALWAYS run quick sample first for unknown disk sizes
result = subprocess.run(
    ['python', 'scripts/analyze_disk.py', '--sample', '--json'],
    capture_output=True,
    text=True,
    timeout=10,
    cwd=skill_path
)

import json
sample = json.loads(result.stdout)
estimated_time = sample.get('estimated_time_seconds', 0)

# Choose next action based on estimate
if estimated_time < 30:
    mode = 'full'  # Full scan is fine
elif estimated_time < 120:
    mode = 'time_limited'  # Use time limit
else:
    mode = 'progressive'  # MUST use progressive mode
```

#### Mode 2: Progressive Scan (🎯 RECOMMENDED FOR LARGE DISKS)

**When to use**: Get partial results in 30 seconds for large disks

```bash
python scripts/analyze_progressive.py --max-seconds 30
```

**Features**:
- ✅ Real-time progress updates every 2 seconds
- ✅ Shows partial results as they're discovered
- ✅ Can interrupt with Ctrl+C and keep results
- ✅ Smart file count limit (50,000 by default)

**Agent Usage**:
```python
def analyze_large_disk_safely(path, max_seconds=30):
    """Safely analyze large disk with time limit"""
    result = subprocess.run(
        ['python', 'scripts/analyze_progressive.py',
         '--max-seconds', str(max_seconds),
         '--path', str(path)],
        capture_output=True,
        text=True,
        timeout=max_seconds + 10,
        cwd=skill_path
    )
    return result.stdout
```

#### Mode 3: Limited Scan (📊 FAST RESULTS)

**When to use**: Get results quickly with file/time limits

```bash
# Limit by file count (fast)
python scripts/analyze_disk.py --file-limit 10000

# Limit by time (safe)
python scripts/analyze_disk.py --time-limit 30

# Both limits (very fast)
python scripts/analyze_disk.py --file-limit 10000 --time-limit 30
```

### 🎯 AGENT DECISION TREE (CRITICAL - FOLLOW THIS)

```
USER REQUEST: "Analyze my disk"
    ↓
┌─────────────────────────────────────────┐
│ STEP 1: Quick Sample (MANDATORY)          │
│ python scripts/analyze_disk.py --sample │
└─────────────────────────────────────────┘
    ↓
    Get estimated_time from sample
    ↓
    ├─ estimated_time < 30 seconds
    │   ↓
    │   ✅ Use FULL SCAN
    │   python scripts/analyze_disk.py
    │
    ├─ estimated_time 30-120 seconds
    │   ↓
    │   ⚠️ Use TIME LIMIT
    │   python scripts/analyze_disk.py --time-limit 60
    │   Tell user: "This will take ~X minutes"
    │
    └─ estimated_time > 120 seconds
        ↓
        🚨 MUST USE PROGRESSIVE MODE
        python scripts/analyze_progressive.py --max-seconds 30
        Tell user: "Large disk detected - using progressive scan (30 seconds)"
```

### 📝 Required Response Templates

#### When Quick Sample Shows < 30 Seconds
```
✅ Disk analysis will take approximately 2 seconds
Starting full scan...
```

#### When Quick Sample Shows 30-120 Seconds
```
⚠️ Disk analysis will take approximately 3 minutes
Using time-limited scan for faster results...
```

#### When Quick Sample Shows > 120 Seconds
```
🚨 Large disk detected! Full scan would take approximately 5 minutes
Using progressive scan mode to get results in 30 seconds...
(This gives you partial results quickly - you can always do a full scan later)
```

### 💡 COPY-PASTE CODE (USE THIS)

```python
import subprocess
import json
from pathlib import Path

def smart_disk_analysis(disk_path, python_cmd='python'):
    """
    SMART disk analysis - automatically chooses best method

    THIS IS THE RECOMMENDED WAY for all agents
    """
    # Find skill package
    skill_path = find_skill_package()  # Use your find function
    if not skill_path:
        return False, "Skill package not found"

    # STEP 1: Quick sample (MANDATORY - do this first!)
    print("🔍 Quick sampling disk...")
    sample_result = subprocess.run(
        [python_cmd, 'scripts/analyze_disk.py', '--sample',
         '--path', str(disk_path), '--json'],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(skill_path)
    )

    if sample_result.returncode != 0:
        return False, "Sample failed"

    try:
        sample = json.loads(sample_result.stdout)
        estimated_time = sample.get('estimated_time_seconds', 0)
    except:
        estimated_time = 0

    print(f"   Estimated scan time: {estimated_time:.0f} seconds")

    # STEP 2: Choose scanning method based on estimate
    if estimated_time < 30:
        # Small disk - full scan
        print("✅ Using full scan (small disk)")
        result = subprocess.run(
            [python_cmd, 'scripts/analyze_disk.py',
             '--path', str(disk_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(skill_path)
        )

    elif estimated_time < 120:
        # Medium disk - time limited
        minutes = estimated_time / 60
        print(f"⚠️  Using time-limited scan (~{minutes:.1f} minutes)")
        result = subprocess.run(
            [python_cmd, 'scripts/analyze_disk.py',
             '--path', str(disk_path),
             '--time-limit', '60'],  # 1 minute max
            capture_output=True,
            text=True,
            timeout=70,
            cwd=str(skill_path)
        )

    else:
        # Large disk - PROGRESSIVE MODE (MANDATORY)
        print(f"🚨 Large disk detected! Using progressive scan (30 seconds)")
        result = subprocess.run(
            [python_cmd, 'scripts/analyze_progressive.py',
             '--path', str(disk_path),
             '--max-seconds', '30',
             '--json'],
            capture_output=True,
            text=True,
            timeout=40,
            cwd=str(skill_path)
        )

    if result.returncode != 0:
        return False, result.stderr

    print(result.stdout)
    return True, result.stdout

# USAGE - Just call this function:
success, output = smart_disk_analysis("C:\\")
success, output = smart_disk_analysis("/home/user")
success, output = smart_disk_analysis("D:\\Projects")
```

### ⚠️ COMMON MISTAKES TO AVOID

❌ **DON'T**: Always run full scan without checking disk size first
✅ **DO**: Always run `--sample` first to estimate

❌ **DON'T**: Let users wait hours for large disk scan
✅ **DO**: Use `--max-seconds 30` for large disks

❌ **DON'T**: Ignore estimated time from sample
✅ **DO**: Use estimate to choose appropriate scan mode

❌ **DON'T**: Run analyze_disk.py on 1TB disk without limits
✅ **DO**: Use analyze_progressive.py with --max-seconds

### 📊 Command Reference Card

| Situation | Command | Time | Result |
|-----------|---------|------|--------|
| Unknown size | `--sample` | 1s | Estimate + recommendation |
| < 30 seconds | `analyze_disk.py` | <30s | Full results |
| 30-120 seconds | `--time-limit 60` | 60s | Most results |
| > 120 seconds | `analyze_progressive.py --max-seconds 30` | 30s | Partial results |
| Very large disk | `analyze_progressive.py --max-seconds 60` | 60s | More results |

### 🔍 How Progressive Scan Works

1. **Quick Sample (1 second)**
   - Scans as many files as possible in 1 second
   - Calculates scan rate (files/second)
   - Estimates total scan time
   - Gives immediate feedback

2. **Progressive Scan (N seconds)**
   - Scans continuously for N seconds
   - Shows progress every 2 seconds
   - Collects results as it goes
   - Returns whatever it found when time is up
   - User can interrupt and keep partial results

3. **Smart Stopping**
   - Stops automatically when time/file limit reached
   - Graceful handling of interruption
   - Partial results are still useful

### 🎯 BEST PRACTICE FOR AGENTS

1. **ALWAYS** run `--sample` first
2. **ALWAYS** check estimated_time before choosing mode
3. **ALWAYS** inform user about expected scan time
4. **ALWAYS** use progressive mode for large disks (>2 minutes)
5. **NEVER** let users wait more than 2 minutes without feedback

---

---

## 🎯 UNIVERSAL AGENT WORKFLOW

This workflow works on ANY platform, in ANY AI IDE, at ANY location.

### STEP 1: Verify Python

```python
import subprocess
import sys

def verify_python():
    """Check if Python 3.7+ is available - PLATFORM AGNOSTIC"""
    try:
        # Try 'python' first (Windows, some Unix)
        result = subprocess.run(
            ['python', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stderr.strip() or result.stdout.strip()
    except FileNotFoundError:
        pass

    try:
        # Try 'python3' (macOS, Linux)
        result = subprocess.run(
            ['python3', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stderr.strip() or result.stdout.strip()
    except FileNotFoundError:
        pass

    return False, "Python not found"

# EXECUTE
python_available, version_info = verify_python()
if not python_available:
    print("❌ Python 3.7+ required but not found")
    print("Install from: https://www.python.org/downloads/")
    print("See: NO_PYTHON_GUIDE.md for platform-specific instructions")
    sys.exit(1)

print(f"✅ Python available: {version_info}")
```

### STEP 2: Locate Skill Package

```python
from pathlib import Path
import os

def find_skill_package():
    """
    Find disk-cleaner skill package - LOCATION INDEPENDENT

    Searches in order of priority:
    1. Current working directory
    2. Project-level: ./skills/, ./.skills/, ./agent-skills/
    3. User-level: ~/.skills/, ~/.agent-skills/, ~/skill-packages/
    4. Common AI IDE locations
    5. Parent directories
    """

    # Get python command (python or python3)
    python_cmd = 'python' if os.name == 'nt' else 'python3'

    # Search locations - PLATFORM & IDE AGNOSTIC
    search_locations = []

    # 1. Current directory
    cwd = Path.cwd()
    search_locations.extend([
        cwd / 'disk-cleaner',
        cwd / 'skills' / 'disk-cleaner',
        cwd / '.skills' / 'disk-cleaner',
        cwd / 'agent-skills' / 'disk-cleaner',
        cwd / '.agent-skills' / 'disk-cleaner',
    ])

    # 2. Parent directories (project root)
    for parent in [cwd, *cwd.parents]:
        search_locations.extend([
            parent / 'skills' / 'disk-cleaner',
            parent / '.skills' / 'disk-cleaner',
            parent / 'agent-skills' / 'disk-cleaner',
        ])
        # Limit search depth
        if len(parent.parts) <= 3:
            break

    # 3. User home directory
    home = Path.home()
    search_locations.extend([
        home / 'skills' / 'disk-cleaner',
        home / '.skills' / 'disk-cleaner',
        home / 'agent-skills' / 'disk-cleaner',
        home / '.agent-skills' / 'disk-cleaner',
        home / 'skill-packages' / 'disk-cleaner',
    ])

    # 4. Platform-specific user directories
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            search_locations.append(Path(appdata) / 'skills' / 'disk-cleaner')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        if localappdata:
            search_locations.append(Path(localappdata) / 'skills' / 'disk-cleaner')
    else:  # Unix-like (macOS, Linux)
        search_locations.extend([
            home / '.local' / 'share' / 'skills' / 'disk-cleaner',
            home / '.config' / 'skills' / 'disk-cleaner',
            Path('/usr/local/share/skills/disk-cleaner'),
        ])

    # 5. AI IDE specific directories (IDE-AGNOSTIC)
    # Note: These are examples - actual locations vary
    ide_specific = [
        # Cursor
        home / '.cursor' / 'skills' / 'disk-cleaner',
        home / '.cursor' / 'user' / 'skills' / 'disk-cleaner',
        # Windsurf
        home / '.windsurf' / 'skills' / 'disk-cleaner',
        # Continue
        home / '.continue' / 'skills' / 'disk-cleaner',
        # Generic
        home / '.ai-ide' / 'skills' / 'disk-cleaner',
    ]
    search_locations.extend(ide_specific)

    # 6. sys.path entries (Python module style)
    for path_entry in sys.path:
        if path_entry and path_entry not in ['', '.']:
            test_path = Path(path_entry) / 'disk-cleaner'
            search_locations.append(test_path)

    # Remove duplicates and non-existent
    search_locations = list(set(search_locations))

    # Search for valid skill package
    for location in search_locations:
        if not location:
            continue
        try:
            # Check for key indicator files
            if (location / 'scripts' / 'analyze_disk.py').exists():
                return location, f"Found at: {location}"
            if (location / 'SKILL.md').exists():
                return location, f"Found at: {location}"
        except PermissionError:
            continue
        except Exception:
            continue

    # Not found - provide helpful message
    print("❌ Skill package not found")
    print("\nSearched locations:")
    for loc in search_locations[:10]:  # Show first 10
        print(f"  - {loc}")
    print("\nSolutions:")
    print("1. Extract skill package to one of the locations above")
    print("2. Or set environment variable: DISK_CLEANER_SKILL_PATH")
    print("3. Or provide explicit path when calling functions")
    return None, "Not found"

# EXECUTE
skill_path, message = find_skill_package()
if not skill_path:
    print(message)
    sys.exit(1)

print(f"✅ {message}")
```

### STEP 3: Verify Skill Package

```python
def verify_skill_package(skill_path, python_cmd='python'):
    """Verify skill package integrity - LOCATION INDEPENDENT"""
    check_script = skill_path / 'scripts' / 'check_skill.py'

    if not check_script.exists():
        print(f"❌ Check script not found: {check_script}")
        return False

    try:
        result = subprocess.run(
            [python_cmd, str(check_script)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(skill_path)
        )

        # Show verification output
        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            print("✅ Skill package verified successfully")
            return True
        else:
            print("❌ Skill package verification failed")
            if result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ Verification timed out")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

# Determine python command
python_cmd = 'python' if os.name == 'nt' else 'python3'

# EXECUTE
if not verify_skill_package(skill_path, python_cmd):
    sys.exit(1)
```

### STEP 4: Execute Operation

```python
def execute_operation(skill_path, operation, python_cmd='python', **kwargs):
    """
    Execute disk cleaner operation - PLATFORM & IDE AGNOSTIC

    Args:
        skill_path: Path to skill package
        operation: 'analyze', 'clean', 'monitor'
        python_cmd: 'python' or 'python3'
        **kwargs: Operation-specific arguments
    """

    operation_map = {
        'analyze': 'analyze_disk.py',
        'clean': 'clean_disk.py',
        'monitor': 'monitor_disk.py',
    }

    if operation not in operation_map:
        print(f"❌ Unknown operation: {operation}")
        print(f"Valid operations: {list(operation_map.keys())}")
        return False, None

    script = skill_path / 'scripts' / operation_map[operation]
    cmd = [python_cmd, str(script)]

    # Add operation-specific arguments
    if operation == 'analyze':
        if kwargs.get('path'):
            cmd.extend(['--path', str(kwargs['path'])])
        if kwargs.get('top'):
            cmd.extend(['--top', str(kwargs['top'])])
        if kwargs.get('json'):
            cmd.append('--json')

    elif operation == 'clean':
        # ALWAYS use dry-run for safety
        if not kwargs.get('force'):
            cmd.append('--dry-run')
        else:
            cmd.append('--force')

        if kwargs.get('temp'):
            cmd.append('--temp')
        if kwargs.get('cache'):
            cmd.append('--cache')
        if kwargs.get('logs'):
            cmd.append('--logs')

    elif operation == 'monitor':
        if kwargs.get('watch'):
            cmd.append('--watch')
        if kwargs.get('json'):
            cmd.append('--json')

    try:
        print(f"🔧 Executing: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=kwargs.get('timeout', 300),
            cwd=str(skill_path)
        )

        # Show output
        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            if result.stderr:
                print(f"❌ Error: {result.stderr}")
            return False, None

        return True, result.stdout

    except subprocess.TimeoutExpired:
        print("⚠️ Operation timed out")
        return False, None
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False, None

# EXECUTE
success, output = execute_operation(
    skill_path,
    operation='analyze',
    python_cmd=python_cmd,
    path='C:\\Users' if os.name == 'nt' else '/home',
    json=True
)

if success:
    print("✅ Operation completed successfully")
```

---

## 📋 QUICK REFERENCE (All IDEs)

### ⚠️ CRITICAL: Use Progressive Scanning for Large Disks!

**BEFORE ANY DISK ANALYSIS**:
1. Run `--sample` first to estimate scan time
2. If > 2 minutes estimated, use progressive mode
3. NEVER let users wait more than 2 minutes without feedback

**Quick Reference**:
```bash
# STEP 1: ALWAYS DO THIS FIRST (1 second)
python scripts/analyze_disk.py --sample

# STEP 2: Choose based on estimate
# < 30s: python scripts/analyze_disk.py
# 30-120s: python scripts/analyze_disk.py --time-limit 60
# > 120s: python scripts/analyze_progressive.py --max-seconds 30
```

### User Intent → Operation Mapping

### User Intent → Operation Mapping

| User Says | Operation | Command Template |
|-----------|-----------|------------------|
| "analyze disk" | analyze | `python scripts/analyze_disk.py` |
| "check disk space" | analyze | `python scripts/analyze_disk.py --top 50` |
| "quick scan" | analyze | `python scripts/analyze_disk.py --sample` |
| "large disk analysis" | analyze | `python scripts/analyze_progressive.py --max-seconds 30` |
| "clean temp files" | clean | `python scripts/clean_disk.py --temp --dry-run` |
| "preview cleanup" | clean | `python scripts/clean_disk.py --dry-run` |
| "monitor disk" | monitor | `python scripts/monitor_disk.py` |
| "disk usage" | monitor | `python scripts/monitor_disk.py --json` |

### Progressive Scanning (For Large Disks)

**Problem**: Full disk scan can take hours on large disks (1TB+)

**Solution**: Use progressive scanning with time/file limits

```python
# Quick sample (1 second) - Get instant estimate
subprocess.run(['python', 'scripts/analyze_disk.py', '--sample'])

# Progressive scan (30 seconds) - Get partial results quickly
subprocess.run(['python', 'scripts/analyze_progressive.py',
                 '--max-seconds', '30'])

# Limited file count (fast)
subprocess.run(['python', 'scripts/analyze_disk.py',
                 '--file-limit', '10000'])

# Full scan with time limit
subprocess.run(['python', 'scripts/analyze_disk.py',
                 '--time-limit', '120'])
```

**Recommended workflow for large disks**:

1. First, run `--sample` to get estimate (1 second)
2. If estimate is too long, use `--max-seconds` or `--file-limit`
3. Or use `analyze_progressive.py` for real-time feedback

### Cross-Platform Python Commands

| Platform | Python Command | Check Command |
|----------|---------------|---------------|
| Windows | `python` | `python --version` |
| macOS | `python3` | `python3 --version` |
| Linux | `python3` | `python3 --version` |

### Universal Command Template

```python
# Works on ALL platforms
import os
import subprocess

python_cmd = 'python' if os.name == 'nt' else 'python3'
result = subprocess.run([python_cmd, '--version'], capture_output=True, text=True)
```

---

## 🌐 Multi-IDE Compatibility

This skill package works with ALL AI IDEs that support:

### Supported AI IDEs
- ✅ **Cursor** - Works as project or user-level skill
- ✅ **Windsurf** - Works at any location
- ✅ **Continue** - Works as global or project skill
- ✅ **Aider** - Works as agent tool
- ✅ **Claude Code** - Works as skill
- ✅ **Any AI IDE** - Works via subprocess

### Installation by IDE Type

#### Project-Level Installation
```
your-project/
├── skills/
│   └── disk-cleaner/    ← Extract here
├── src/
└── README.md
```

#### User-Level Installation
```
~/.skills/disk-cleaner/      ← Unix-like
~/agent-skills/disk-cleaner/ ← Alternative
C:\Users\You\skills\disk-cleaner\ ← Windows
```

#### Global Installation
```
/usr/local/share/skills/disk-cleaner/  ← Linux (system-wide)
C:\ProgramData\skills\disk-cleaner\   ← Windows (system-wide)
```

---

## 🔧 IDE-Specific Notes

### Cursor
```python
# Cursor automatically searches for skills in:
# - .cursor/skills/
# - project/skills/
# - ~/.skills/

# No special configuration needed
```

### Windsurf
```python
# Windsurf supports skills at:
# - .windsurf/skills/
# - project/skills/

# Skill works via subprocess, no special setup
```

### Continue
```python
# Continue configuration (if needed):
# {
#   "skills": ["./skills/disk-cleaner"]
# }
# But auto-detection works in most cases
```

### Aider
```python
# Use as a tool via subprocess:
# !python skills/disk-cleaner/scripts/analyze_disk.py
```

### Generic/Other IDEs
```python
# The skill includes intelligent auto-detection
# Just extract and use - no configuration needed
```

---

## 🎯 Complete Copy-Paste Template

```python
"""
Universal Disk Cleaner Skill Usage
Works with ALL AI IDEs, on ALL platforms, at ANY location
"""

import subprocess
import sys
import os
from pathlib import Path


def use_disk_cleaner(operation='analyze', **kwargs):
    """
    Use disk cleaner skill - UNIVERSAL FUNCTION

    Works on:
    - All platforms (Windows, macOS, Linux)
    - All AI IDEs (Cursor, Windsurf, Continue, etc.)
    - All installation levels (global, project, user)

    Args:
        operation: 'analyze', 'clean', 'monitor'
        **kwargs: Operation-specific arguments

    Returns:
        (success: bool, output: str)
    """

    # 1. Determine Python command
    python_cmd = 'python' if os.name == 'nt' else 'python3'

    # 2. Verify Python
    try:
        result = subprocess.run(
            [python_cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print("❌ Python not found")
            return False, "Python 3.7+ required"
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False, str(e)

    # 3. Find skill package (intelligent search)
    def find_skill():
        search_paths = [
            # Current directory
            Path.cwd() / 'disk-cleaner',
            Path.cwd() / 'skills' / 'disk-cleaner',
            Path.cwd() / '.skills' / 'disk-cleaner',
            # Project root
            *[(p / 'skills' / 'disk-cleaner') for p in [Path.cwd(), *Path.cwd().parents][:3]],
            # User home
            Path.home() / 'skills' / 'disk-cleaner',
            Path.home() / '.skills' / 'disk-cleaner',
        ]

        for path in search_paths:
            if (path / 'scripts' / 'analyze_disk.py').exists():
                return path
        return None

    skill_path = find_skill()
    if not skill_path:
        print("❌ Skill package not found")
        print("Extract to: skills/disk-cleaner/ or ~/.skills/disk-cleaner/")
        return False, "Skill package not found"

    # 4. Execute operation
    scripts = {
        'analyze': 'analyze_disk.py',
        'clean': 'clean_disk.py',
        'monitor': 'monitor_disk.py',
    }

    if operation not in scripts:
        return False, f"Unknown operation: {operation}"

    script = skill_path / 'scripts' / scripts[operation]
    cmd = [python_cmd, str(script)]

    # Add arguments
    if operation == 'analyze':
        if kwargs.get('path'):
            cmd.extend(['--path', str(kwargs['path'])])
    elif operation == 'clean':
        cmd.append('--dry-run')  # Always safe
    elif operation == 'monitor':
        if kwargs.get('json'):
            cmd.append('--json')

    # Run
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(skill_path)
        )

        return result.returncode == 0, result.stdout

    except Exception as e:
        return False, str(e)


# USAGE EXAMPLES:
# success, output = use_disk_cleaner('analyze', path='.')
# success, output = use_disk_cleaner('clean')
# success, output = use_disk_cleaner('monitor', json=True)

if __name__ == "__main__":
    # Quick test
    success, output = use_disk_cleaner('analyze')
    print(output)
```

---

## ⚡ PROGRESSIVE SCANNING CHECKLIST (CRITICAL)

### Agent MUST Follow This for All Disk Analysis Requests:

```
[ ] Did you run --sample FIRST to estimate scan time?
[ ] Did you inform user about expected scan time?
[ ] Did you choose appropriate mode based on estimate?
[ ] Did you use progressive mode for >2 minute estimates?
[ ] Did you provide feedback during long scans?
```

### Required Behavior by Disk Size:

**Small Disk (< 30 seconds estimated)**:
- ✅ Run full scan
- ✅ No special handling needed

**Medium Disk (30-120 seconds estimated)**:
- ✅ Use --time-limit
- ✅ Inform user of expected time
- ⚠️ Consider progressive mode if user seems impatient

**Large Disk (> 120 seconds estimated)**:
- 🚨 MUST USE PROGRESSIVE MODE
- 🚨 MUST Inform user about time limit
- ✅ Explain partial results
- ✅ Offer full scan as option

### REQUIRED Code Pattern:

```python
# THIS IS THE REQUIRED PATTERN for all disk analysis:

def safe_disk_analysis(disk_path):
    # Step 1: ALWAYS sample first
    sample = subprocess.run(
        ['python', 'scripts/analyze_disk.py', '--sample', '--json'],
        capture_output=True,
        text=True,
        cwd=skill_path
    )
    import json
    data = json.loads(sample.stdout)
    estimate = data.get('estimated_time_seconds', 0)

    # Step 2: Inform user
    if estimate > 120:
        print(f"Large disk detected! Estimated: {estimate/60:.1f} minutes")
        print("Using progressive scan (30 seconds) for quick results...")

    # Step 3: Choose mode
    if estimate < 30:
        # Full scan
        return subprocess.run(['python', 'scripts/analyze_disk.py'])
    elif estimate < 120:
        # Time limited
        return subprocess.run(['python', 'scripts/analyze_disk.py', '--time-limit', '60'])
    else:
        # Progressive (MANDATORY for large disks)
        return subprocess.run(['python', 'scripts/analyze_progressive.py', '--max-seconds', '30'])
```

---

## 🚨 Error Handling (Universal)

### Error: Python not found
```python
# SOLUTION - Platform-independent guidance
import platform

system = platform.system()
if system == "Windows":
    print("Install from: https://www.python.org/downloads/")
    print("Check 'Add Python to PATH' during installation")
elif system == "Darwin":  # macOS
    print("Install: brew install python@3.11")
    print("Or: https://www.python.org/downloads/macos/")
else:  # Linux
    print("Install: sudo apt install python3  # Debian/Ubuntu")
    print("Or: sudo dnf install python3      # Fedora")
```

### Error: Skill not found
```python
# SOLUTION - Show all searched locations
print("Skill package not found.")
print("Extract to ONE of these locations:")
print("  - ./skills/disk-cleaner/")
print("  - ./disk-cleaner/")
print("  - ~/.skills/disk-cleaner/")
print("  - project/skills/disk-cleaner/")
print("\nOr set: DISK_CLEANER_SKILL_PATH=/path/to/skill")
```

### Error: Permission denied
```python
# SOLUTION - Platform-specific advice
if os.name == 'nt':
    print("Run as Administrator if needed")
else:
    print("Some directories may require: sudo")
    print("Or adjust: chmod +x scripts/*.py")
```

---

## 📝 Environment Variables (Optional)

You can optionally set these to help with auto-detection:

```bash
# Set skill package location (overrides auto-detection)
export DISK_CLEANER_SKILL_PATH=/path/to/skills/disk-cleaner

# Set Python command (overrides auto-detection)
export DISK_CLEANER_PYTHON_CMD=python3

# Enable debug output
export DISK_CLEANER_DEBUG=true
```

---

## 🎓 Best Practices for All Agents

1. **ALWAYS check Python first** - Don't assume it's installed
2. **Use 'python3' on Unix** - Use 'python' on Windows
3. **Search multiple locations** - Don't assume single installation path
4. **Use subprocess with timeout** - Prevent hanging
5. **Capture both stdout and stderr** - Complete error information
6. **Prefer --dry-run for clean** - Safety first
7. **Handle all exceptions** - Graceful degradation
8. **Show helpful error messages** - Guide users to solutions

---

## 🔍 Troubleshooting (Universal)

### Problem: Skill works in one IDE but not another

**Solution**: The skill is IDE-agnostic. Check:
1. Python is accessible from that IDE
2. Skill package is in a searchable location
3. File permissions allow execution

### Problem: Different behavior on different platforms

**Solution**: The skill handles platform differences. Check:
1. Python command (`python` vs `python3`)
2. Path separators (auto-handled by pathlib)
3. File permissions (Unix may need `chmod +x`)

### Problem: Can't find skill package

**Solution**: Run diagnostic:
```bash
python skills/disk-cleaner/scripts/check_skill.py
# Or
python3 skills/disk-cleaner/scripts/check_skill.py
```

---

## 📦 Package Contents (Universal)

```
disk-cleaner/
├── SKILL.md              # This file
├── AGENT_QUICK_REF.txt   # Quick reference
├── NO_PYTHON_GUIDE.md    # Help for users without Python
├── INSTALL.md            # Installation guide
├── FIXES.md              # What's fixed in v2.0
├── scripts/              # All scripts (universal)
├── diskcleaner/          # Core modules (self-contained)
└── references/           # Platform information
```

---

## ✅ Universal Checklist

Before using this skill in ANY AI IDE:

- [ ] Python 3.7+ installed
- [ ] Skill package extracted to accessible location
- [ ] Can run: `python --version` (or `python3 --version`)
- [ ] Skill package location known (or let it auto-detect)

---

**This skill package works EVERYWHERE - just Python 3.7+ required!**

No IDE-specific configuration needed. No platform-specific setup. No installation level restrictions.

Just extract and use!
