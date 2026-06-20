# 高血压患者服药智能提醒与监测系统

## 📖 目录
- [方式一：复制源码运行](#方式一复制源码运行-推荐给会用-python-的人)
- [方式二：打包为可执行文件分发](#方式二打包为可执行文件分发-推荐给不会用-python-的人)
- [常见问题](#常见问题)

---

## 方式一：复制源码运行（推荐给会用 Python 的人）

### 适用场景：对方电脑上愿意安装 Python，操作较简单

### 步骤

#### 1. 安装 Python（如尚未安装）

从 https://www.python.org/downloads/ 下载 **Python 3.9 或更高版本**，安装时：
- **Windows**：请勾选 ☑️ "Add Python to PATH"
- **macOS**：直接安装即可

#### 2. 复制项目文件夹

将整个 `hypertension_reminder` 文件夹复制到对方电脑任意位置，例如：
- Windows: `C:\Tools\hypertension_reminder`
- macOS: `~/Documents/hypertension_reminder`

#### 3. 打开终端

- **Windows**：在项目文件夹中，按住 Shift 右键空白处 → **"在此处打开 PowerShell 窗口"**
- **macOS**：在项目文件夹中，右键 → **"在终端中打开"**

#### 4. 安装依赖（只需首次运行时执行）

```bash
pip install -r requirements.txt
```

#### 5. 启动应用

```bash
python main.py
```

以后每次要运行，直接双击 `main.py` 或在终端执行 `python main.py` 即可。

---

## 方式二：打包为可执行文件分发（推荐给不会用 Python 的人）

### 适用场景：对方是普通用户，不想折腾安装环境，只需双击运行

### 步骤（先在**您自己的电脑**上打包，然后把生成的文件发过去）

#### 1. 在您的电脑上执行打包脚本

在项目文件夹中打开终端，执行：

```bash
pip install -r requirements.txt pyinstaller
python build_executable.py
```

**注意**：打包时要选择与对方电脑相同的操作系统：
- 在 Windows 上打包 → 可发给其他 Windows 用户
- 在 macOS 上打包 → 可发给其他 macOS 用户
- 在 Linux 上打包 → 可发给其他 Linux 用户

**首次打包可能需要 2-5 分钟**，请耐心等待。

#### 2. 把打包好的文件发给对方

打包完成后，`dist/` 目录下会生成：
- **Windows**: `高血压服药提醒系统.exe`
- **macOS**: `高血压服药提醒系统.app`
- **Linux**: `高血压服药提醒系统`

把这个**单一文件**发给对方即可，对方无需安装任何东西，**双击即运行**。

### 💡 分发小提示

- **Windows**: 如果 Windows SmartScreen 提示"已阻止未知应用"，点击"更多信息" → "仍要运行"即可。这是正常现象，不是病毒。
- **macOS**: 如果提示"无法打开，因为无法验证开发者"，右键点击文件 → 选择"打开" → 在对话框中点击"打开"即可。
- 文件较大（约 50-80MB），可通过微信/邮件/U盘等方式传递。

---

## 常见问题

### Q1. 提示 "ModuleNotFoundError: No module named 'PySide6'"？
**A**: 依赖没装好，请执行：
```bash
pip install -r requirements.txt
```

### Q2. Windows 上 pip 安装报权限错误？
**A**: 用管理员权限打开命令行：按 Win 键，搜索 "cmd"，右键"以管理员身份运行"，然后再执行 pip 安装命令。或改用：
```bash
pip install --user -r requirements.txt
```

### Q3. 应用能正常启动，但窗口看起来字体不对？
**A**: 这是显示问题，不影响功能。可在系统中安装中文字体（如微软雅黑、思源黑体等）解决。

### Q4. 数据保存在哪里？会随着程序删除丢失吗？
**A**: 所有数据（药品、记录、血压）都保存在**用户目录**下的一个独立位置：
- Windows: `C:\Users\用户名\.hypertension_reminder\data.db`
- macOS: `~/.hypertension_reminder/data.db`
- Linux: `~/.hypertension_reminder/data.db`

**程序和数据完全分离**——卸载/删除程序不会丢失数据；要迁移数据，只需复制这个 `.db` 文件到新电脑的相同位置即可。

### Q5. 如何迁移数据到另一台电脑？
**A**: 把上面的 `data.db` 文件复制到新电脑的相同路径（`~/.hypertension_reminder/`）即可。

### Q6. 杀毒软件会误报吗？
**A**: 打包的可执行文件偶尔会被 Windows Defender 或某些杀毒软件标记为"未知程序"，这是常见现象。您可以将其添加到信任名单，或选择方式一（源码方式）运行。

### Q7. 提醒需要软件一直开着吗？
**A**: 是的，提醒功能依赖应用正在运行。建议将应用设为开机自启：
- **Windows**: 将 `main.py`（或打包后的 .exe）的快捷方式放入 `启动` 文件夹（按 Win+R，输入 `shell:startup` 打开）
- **macOS**: 在"系统设置 → 通用 → 登录项"中添加应用

---

## 系统要求

| 项目 | 最低要求 | 推荐 |
|------|---------|------|
| 操作系统 | Windows 10 / macOS 11 / Linux 内核 4.x | Windows 11 / macOS 14 |
| Python（方式一） | 3.9 | 3.10 或更高 |
| 内存 | 200MB | 512MB |
| 磁盘空间（方式一） | 30MB | 50MB |
| 磁盘空间（方式二） | 150MB | 300MB |

---

## 功能速览

- 💊 **药品管理**：登记药品名称、剂量、多个服用时间、注意事项
- ⏰ **定时提醒**：到达服药时间时弹窗提醒，可选择"已服药"或"稍后提醒"
- 📅 **日历视图**：查看每日服药情况，统计服药依从率
- 🩺 **血压监测**：录入血压数据，绘制趋势图，自动分析状态
- 💾 **本地存储**：所有数据保存在本机 SQLite 数据库，不上传云端
