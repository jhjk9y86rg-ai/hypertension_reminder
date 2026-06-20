"""
一键打包脚本 - 将整个应用打包为可执行文件
使用方法：
    1. 确保依赖已安装：pip install -r requirements.txt pyinstaller
    2. 运行：python build_executable.py
    3. 打包完成后，可执行文件在 dist/ 目录
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def main():
    print("=" * 60)
    print("  高血压服药提醒系统 - 一键打包工具")
    print("=" * 60)

    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # 检查 PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("\n正在安装 PyInstaller ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")

    # 检查主依赖
    for pkg in ["PySide6", "matplotlib"]:
        try:
            __import__(pkg.lower() if pkg.lower() != "pyside6" else "PySide6")
            print(f"✓ {pkg} 已就绪")
        except ImportError:
            print(f"✗ 缺少 {pkg}，正在安装 ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"✓ {pkg} 安装完成")

    print("\n" + "-" * 60)
    print("开始打包（首次打包可能需要 2-5 分钟，请耐心等待）...")
    print("-" * 60 + "\n")

    # 清理旧构建
    for dir_name in ["build", "dist"]:
        dir_path = project_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"已清理旧的 {dir_name}/")

    # PyInstaller 命令
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",              # 不显示命令行窗口
        "--onefile",               # 打包成单个文件
        "--name", "高血压服药提醒系统",
        "--collect-all", "PySide6",
        "--collect-all", "matplotlib",
        "main.py",
    ]

    print(f"执行命令: {' '.join(args)}")
    print()

    try:
        result = subprocess.run(args, capture_output=False)
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("🎉 打包成功！")
            exe_path = project_dir / "dist"
            print(f"可执行文件目录: {exe_path}")
            print("=" * 60)
            print("\n使用说明:")
            print("  - Windows: dist\\高血压服药提醒系统.exe")
            print("  - macOS: dist/高血压服药提醒系统.app")
            print("  - Linux: dist/高血压服药提醒系统")
            print("\n直接双击即可运行，无需安装 Python！")
            print("数据文件保存到用户目录: ~/.hypertension_reminder/")
            print("=" * 60)
        else:
            print(f"\n✗ 打包失败，错误码: {result.returncode}")
    except Exception as e:
        print(f"✗ 打包过程中出错: {e}")


if __name__ == "__main__":
    main()
