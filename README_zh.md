# 磁盘清理工具 v2.1 - 智能跨平台磁盘管理

**[English](README.md)** | **[中文文档](README_zh.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/gccszs/disk-cleaner)
[![Skill](https://img.shields.io/badge/skill-add--skill-blue)](https://github.com/gccszs/disk-cleaner)

一个全面的跨平台磁盘空间监控、分析和智能清理工具包。具备先进的3D文件分类、重复文件检测、自动化调度和平台特定优化功能。

## ⚡ 快速安装

### 方式1：作为 Agent SKILL 技能安装（推荐）

直接从CLI安装：

```bash
npx add-skill gccszs/disk-cleaner
```
或者
```bash
npx skills add gccszs/disk-cleaner
```
这将安装包含所有必要文件的技能。`.skill` 包仅包含核心组件：
- ✅ 核心模块 (`diskcleaner/`)
- ✅ 可执行脚本 (`scripts/`)
- ✅ 技能定义 (`SKILL.md`)
- ✅ 参考文档 (`references/`)

**注意：** 技能包已排除测试文件、CI/CD 配置和开发文件，确保干净、最小化的安装。

### 方式2：克隆仓库

用于开发或独立使用：

```bash
git clone https://github.com/gccszs/disk-cleaner.git
cd disk-cleaner
```

参见 [使用示例](#使用示例) 部分了解如何运行脚本。

---

## ✨ v2.1 新特性

### 🚨 关键跨平台编码修复
- **✅ ASCII安全输出** - 所有脚本使用ASCII字符，确保100%跨平台兼容
- **🌐 通用控制台支持** - 支持Windows GBK、Linux UTF-8、macOS UTF-8和任何其他编码
- **🛡️ 无编码错误** - 在所有平台上彻底消除UnicodeEncodeError
- **📝 智能Emoji策略** - 脚本使用ASCII，Agent向用户汇报时可使用Emoji

### ⚡ 大磁盘渐进式扫描
- **🔍 快速采样模式** - 仅需1秒即可估算磁盘大小和扫描时间
- **📊 渐进式扫描模式** - 30秒内获取大磁盘（500GB+）的部分结果
- **⏱️ 智能时间限制** - 防止用户等待数小时进行完整扫描
- **🔄 实时反馈** - 每2秒更新进度
- **⏸️ 可中断** - 按Ctrl+C随时获取部分结果

### 🤖 智能引导系统
- **📍 自动位置检测** - 自动搜索20+个常见技能包位置
- **🔧 环境变量支持** - 使用`DISK_CLEANER_SKILL_PATH`覆盖
- **📦 自动模块导入** - 自动导入diskcleaner模块，带回退机制
- **🌍 跨平台Python检测** - 同时尝试`python`和`python3`
- **🛠️ 诊断工具** - `check_skill.py`验证所有功能

### 🎯 高级性能优化
- **⚡ QuickProfiler** - 快速采样以估算扫描特征
- **🚀 ConcurrentScanner** - 多线程I/O，速度提升3-5倍
- **🔍 os.scandir()优化** - 比Path.glob快3-5倍
- **💾 IncrementalCache** - 缓存扫描结果，重复扫描更快
- **🧠 内存监控** - 根据可用内存自动调整
- **⏹️ 早期停止** - 可配置的文件/时间限制

### 🔧 核心v2.0功能
- **🤖 智能3D分类** - 按类型、风险等级和文件年龄对文件进行分类
- **🔍 自适应重复检测** - 快速/准确策略，自动优化性能
- **⚡ 增量扫描** - 基于缓存的性能优化，重复扫描速度提升10倍
- **🔒 进程感知安全** - 文件锁定检测和进程终止
- **💻 平台特定优化** - Windows更新、APT、Homebrew缓存检测
- **⏰ 自动化调度** - 基于定时器的清理任务
- **🎯 交互式清理UI** - 5种视图模式，带可视化反馈
- **🛡️ 增强安全性** - 受保护根目录和扩展名、自定义路径显式授权、精确路径确认、递归预览

## 功能特性

### 核心能力
- **磁盘空间分析**：识别占用磁盘空间的大文件和目录
- **智能清理**：基于文件模式和使用情况的AI驱动建议
- **重复文件检测**：查找并删除重复文件以回收空间
- **安全垃圾清理**：内置安全机制，清理临时文件、缓存、日志
- **磁盘监控**：实时监控，可配置告警阈值
- **跨平台**：完全支持 Windows、Linux 和 macOS
- **零依赖**：纯Python标准库实现

### 高级特性
- **3D文件分类**：类型 × 风险 × 年龄矩阵，智能决策
- **增量扫描**：仅扫描变更的文件，后续扫描速度提升10倍
- **文件锁定检测**：防止在所有平台上删除锁定的文件
- **平台特定清理**：Windows更新、Linux包管理器缓存、macOS Xcode衍生数据
- **自动化调度**：设置自定义间隔的定期清理任务
- **交互式选择**：通过详细预览精确选择要清理的内容

## 快速开始

### 前置要求

Python 3.7 或更高版本（无需外部依赖 - 仅使用标准库）。

### 基本使用

```bash
# 快速采样模式（1秒）- v2.0新增
python skills/disk-cleaner/scripts/analyze_disk.py --sample

# 大磁盘渐进式扫描 - v2.0新增
python skills/disk-cleaner/scripts/analyze_progressive.py --max-seconds 30

# 验证技能包 - v2.0新增
python skills/disk-cleaner/scripts/check_skill.py

# 分析磁盘空间（智能默认值）
python skills/disk-cleaner/scripts/analyze_disk.py

# 智能清理及重复检测（v2.1新增）
python -c "from diskcleaner.core import SmartCleanupEngine; engine = SmartCleanupEngine('.'); print(engine.get_summary(engine.analyze()))"

# 预览清理（干运行模式）
python skills/disk-cleaner/scripts/clean_disk.py --dry-run

# 监控磁盘使用
python skills/disk-cleaner/scripts/monitor_disk.py

# 持续监控
python skills/disk-cleaner/scripts/monitor_disk.py --watch
```

### macOS QQ 图片和表情清理

该脚本只处理 QQ 本地的 `Pic` 和 `Emoji` 文件，不会选择聊天数据库
`nt_db`。清理命令默认仅预览，确认结果并退出 QQ 后才可执行。

```zsh
# 只读检查 QQ 存储占用
skills/disk-cleaner/scripts/qq_cleanup_macos.zsh audit

# 预览 90 天以前的图片和表情，不修改文件
skills/disk-cleaner/scripts/qq_cleanup_macos.zsh clean \
  --older-than-days 90 --categories Pic,Emoji

# 确认预览结果并退出 QQ 后执行
skills/disk-cleaner/scripts/qq_cleanup_macos.zsh clean \
  --older-than-days 90 --categories Pic,Emoji --execute
```

删除本地媒体后，旧聊天中的图片或表情可能无法再次下载。保留 `nt_db`
表示脚本不会删除聊天数据库，但不能保证所有历史附件仍可使用。

### v2.1 高级使用

```bash
# 快速采样（估算扫描时间）- v2.0新增
python skills/disk-cleaner/scripts/analyze_disk.py --sample --json

# 渐进式扫描（30秒限制）- v2.0新增
python skills/disk-cleaner/scripts/analyze_progressive.py --max-seconds 30

# 渐进式扫描（文件数量限制）- v2.0新增
python skills/disk-cleaner/scripts/analyze_progressive.py --max-files 50000

# 调度自动清理（v2.0新增）
python skills/disk-cleaner/scripts/scheduler.py add "每日清理" /tmp 24h --type smart
python skills/disk-cleaner/scripts/scheduler.py run  # 执行到期任务

# 平台特定清理建议
python -c "from diskcleaner.platforms import WindowsPlatform; import pprint; pprint.pprint(WindowsPlatform.get_system_maintenance_items())"
```

## 使用示例

### 示例1：智能清理及重复检测

```python
from diskcleaner.core import SmartCleanupEngine

# 初始化引擎
engine = SmartCleanupEngine("/path/to/clean", cache_enabled=True)

# 分析目录
report = engine.analyze(
    include_duplicates=True,
    safety_check=True
)

# 获取摘要
print(engine.get_summary(report))

# 交互式清理（如果需要）
from diskcleaner.core import InteractiveCleanupUI
ui = InteractiveCleanupUI(report)
ui.display_menu()  # 显示5个视图选项
```

### 示例2：自动化调度

```bash
# 添加每日清理任务
python scripts/scheduler.py add "每日临时文件清理" /tmp 24h --type temp

# 列出所有计划任务
python scripts/scheduler.py list

# 运行到期任务（默认干运行）
python scripts/scheduler.py run

# 实际删除运行
python scripts/scheduler.py run --force
```

### 示例3：平台特定清理

```python
from diskcleaner.platforms import WindowsPlatform, LinuxPlatform, MacOSPlatform
import platform

if platform.system() == "Windows":
    platform_impl = WindowsPlatform()
elif platform.system() == "Linux":
    platform_impl = LinuxPlatform()
else:
    platform_impl = MacOSPlatform()

# 获取平台特定的清理建议
items = platform_impl.get_system_maintenance_items()
for key, item in items.items():
    print(f"{item['name']}: {item['description']}")
    print(f"  风险: {item['risk']}, 大小: {item['size_hint']}")
```

## 安装

### 快速安装（推荐）

使用 Vercel 的 add-skill CLI 直接从 GitHub 安装：

```bash
npx add-skill gccszs/disk-cleaner -g
```

将 `gccszs` 替换为你的实际 GitHub 用户名。

### 作为 Claude Code 技能（手动）

1. 从 [发布页面](https://github.com/gccszs/disk-cleaner/releases) 下载 `disk-cleaner.skill`
2. 通过 Claude Code 安装：
   ```
   /skill install path/to/disk-cleaner.skill
   ```

### 独立使用

```bash
# 克隆仓库
git clone https://github.com/gccszs/disk-cleaner.git
cd disk-cleaner

# 脚本可直接使用（无需依赖）
python scripts/analyze_disk.py
```

## 使用示例

### 磁盘空间分析

```bash
# 分析当前驱动器（Windows上为 C:\，Unix上为 /）
python scripts/analyze_disk.py

# 分析特定路径
python scripts/analyze_disk.py --path "D:\Projects"

# 获取前50个最大项目
python scripts/analyze_disk.py --top 50

# 输出为JSON格式以便自动化
python scripts/analyze_disk.py --json

# 保存报告到文件
python scripts/analyze_disk.py --output disk_report.json
```

### 清理垃圾文件

**重要提示**：始终先使用 `--dry-run` 预览变更！

```bash
# 预览清理（推荐的第一步）
python scripts/clean_disk.py --dry-run

# 实际清理文件
python scripts/clean_disk.py --force

# 清理特定类别
python scripts/clean_disk.py --temp       # 仅清理临时文件
python scripts/clean_disk.py --cache      # 仅清理缓存
python scripts/clean_disk.py --logs       # 仅清理日志
python scripts/clean_disk.py --recycle    # 仅清理回收站
python scripts/clean_disk.py --downloads 90  # 清理90天以上的下载文件
```

### 磁盘监控

```bash
# 检查当前状态
python scripts/monitor_disk.py

# 持续监控（每60秒）
python scripts/monitor_disk.py --watch

# 自定义阈值
python scripts/monitor_disk.py --warning 70 --critical 85

# 告警模式（CI/CD友好 - 基于状态的退出代码）
python scripts/monitor_disk.py --alerts-only

# 自定义监控间隔（5分钟）
python scripts/monitor_disk.py --watch --interval 300
```

## 脚本参考

### `analyze_disk.py`

磁盘空间分析工具，识别空间消耗模式。

**能力：**
- 扫描目录以查找最大的文件和文件夹
- 分析临时文件位置
- 计算磁盘使用统计
- 生成详细报告

### `clean_disk.py`

安全的垃圾文件删除，具有多重安全机制。

**安全特性：**
- 受保护的路径（从不删除系统目录）
- 受保护的扩展名会跳过匹配的顶层条目
- 始终拒绝文件系统根目录和当前用户主目录
- 自定义路径使用垃圾目录名称允许列表和精确路径确认
- 默认干运行模式
- 递归预览和实际执行使用同一选择与计量规则

**清理类别：**
- **temp**：临时文件（%TEMP%、/tmp等）
- **cache**：应用程序和浏览器缓存
- **logs**：日志文件（默认30天以上）
- **recycle**：回收站/废纸篓
- **downloads**：旧的下载文件（可配置年龄）

### `monitor_disk.py`

持续或一次性磁盘使用监控。

**特性：**
- 多驱动器监控（所有挂载点）
- 可配置的警告/严重阈值
- 带告警的持续监控模式
- 用于自动化的JSON输出
- CI/CD集成的非零退出代码

**退出代码：**
- `0`：所有驱动器正常
- `1`：超过警告阈值
- `2`：超过严重阈值

## 平台支持

| 功能 | Windows | Linux | macOS |
|---------|---------|-------|-------|
| 磁盘分析 | ✅ | ✅ | ✅ |
| 临时清理 | ✅ | ✅ | ✅ |
| 缓存清理 | ✅ | ✅ | ✅ |
| 日志清理 | ✅ | ✅ | ✅ |
| 回收站 | ✅ | ✅ | ✅ |
| 实时监控 | ✅ | ✅ | ✅ |

### Windows 特定位置
- `%TEMP%`、`%TMP%`、`%LOCALAPPDATA%\Temp`
- `C:\Windows\Temp`、`C:\Windows\Prefetch`
- `C:\Windows\SoftwareDistribution\Download`
- 浏览器缓存（Chrome、Edge、Firefox）
- 开发工具缓存（npm、pip、Gradle、Maven）

### Linux 特定位置
- `/tmp`、`/var/tmp`、`/var/cache`
- 包管理器缓存（apt、dnf、pacman）
- 浏览器缓存
- 开发工具缓存

### macOS 特定位置
- `/tmp`、`/private/tmp`、`/var/folders`
- `~/Library/Caches`、`~/Library/Logs`
- iOS设备备份
- Homebrew缓存

## 安全特性

### 受保护的路径
系统目录永远不会被触动：
- Windows：`C:\Windows`、`C:\Program Files`、`C:\ProgramData`
- Linux/macOS：`/usr`、`/bin`、`/sbin`、`/System`、`/Library`

### 自定义 `--path` 边界

`--path` 会递归删除目标目录中符合条件的子目录。工具会拒绝文件系统根目录和
当前用户主目录。名称为 `cache`、`tmp`、`temp`、`logs`、`trash`、
`recycle` 或 `downloads` 的目标目录可以直接预览。其他名称的目录，以及包含
项目标记的同名目录，需要传入 `--allow-unsafe-path`。执行自定义路径删除时，
还需要通过 `--confirm-path` 提供解析后的绝对路径。清理开始前会再次核对已验证
根目录的设备与 inode。干运行会递归计量目录内容。递归计量与旧版 Windows 执行
均会避免跟随符号链接和 Windows 重解析点。顶层执行会将它们作为叶节点移除。
清理错误会写入报告，并产生非零退出状态。

```bash
# 预览已识别的垃圾目录
python skills/disk-cleaner/scripts/clean_disk.py --path "D:/Temp" --dry-run

# 确认精确目标后执行
python skills/disk-cleaner/scripts/clean_disk.py --path "D:/Temp" --force \
  --confirm-path "D:/Temp"

# 通过显式授权选择任意目录
python skills/disk-cleaner/scripts/clean_disk.py --path "D:/BuildOutput" \
  --allow-unsafe-path --force --confirm-path "D:/BuildOutput"
```

### 受保护的扩展名
受保护扩展名适用于匹配的顶层条目。选中的目录及其内容会被递归删除。
```
.exe, .dll, .sys, .drv, .bat, .cmd, .ps1, .sh, .bash, .zsh,
.app, .dmg, .pkg, .deb, .rpm, .msi, .iso, .vhd, .vhdx
```

## 使用场景

### 1. 释放Windows上的C盘空间
```bash
# 分析占用空间的内容
python scripts/analyze_disk.py

# 预览清理
python scripts/clean_disk.py --dry-run

# 执行清理
python scripts/clean_disk.py --force
```

### 2. 自动化磁盘监控
```bash
# 使用自定义阈值在后台运行
python scripts/monitor_disk.py --watch --warning 70 --critical 85 --interval 300
```

### 3. CI/CD集成
```bash
# 在管道中检查磁盘空间
python scripts/monitor_disk.py --alerts-only --json

# 退出代码：0=正常，1=警告，2=严重
if [ $? -ne 0 ]; then
  echo "检测到磁盘空间问题！"
fi
```

## 开发

### 项目结构
```
disk-cleaner/
├── SKILL.md                 # Claude Code 技能定义
├── README.md                # 英文文档
├── README_zh.md             # 中文文档（本文件）
├── CHANGELOG.md             # 更新日志
├── scripts/
│   ├── analyze_disk.py      # 磁盘分析工具
│   ├── clean_disk.py        # 垃圾文件清理器
│   └── monitor_disk.py      # 磁盘使用监控
└── references/
    └── temp_locations.md    # 平台特定的临时文件位置
```

### 贡献
欢迎贡献！请随时提交 Pull Request。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 免责声明

本工具会修改系统上的文件。始终：
1. 在实际清理前查看干运行输出
2. 清理前备份重要数据
3. 使用风险自负

作者不对任何数据丢失或系统问题负责。

## 致谢

- 作为 [Claude Code 技能](https://claude.com/claude-code) 构建
- 可通过 [Vercel 的 add-skill CLI](https://github.com/vercel/vercel/tree/main/packages/add-skill) 安装
- 跨平台兼容性已在 Windows 10/11、Ubuntu 20.04+、macOS 12+ 上测试
