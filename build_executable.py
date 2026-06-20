"""
One-click build script - package the entire app as an executable
Usage:
    1. Install dependencies: pip install -r requirements.txt pyinstaller
    2. Run: python build_executable.py
    3. After build, executable is in dist/ directory
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def main():
    print("=" * 60)
    print("  Hypertension Reminder - Build Tool")
    print("=" * 60)

    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller already installed (version: {PyInstaller.__version__})")
    except ImportError:
        print("\nInstalling PyInstaller ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed")

    # Check main dependencies
    for pkg in ["PySide6", "matplotlib"]:
        try:
            __import__(pkg.lower() if pkg.lower() != "pyside6" else "PySide6")
            print(f"{pkg} ready")
        except ImportError:
            print(f"Installing {pkg} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"{pkg} installed")

    print("\n" + "-" * 60)
    print("Building (first time may take 2-5 minutes)...")
    print("-" * 60 + "\n")

    # Clean old build
    for dir_name in ["build", "dist"]:
        dir_path = project_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Cleaned old {dir_name}/")

    # PyInstaller command
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed",
        "--onefile",
        "--name", "HypertensionReminder",
        "--collect-all", "PySide6",
        "--collect-all", "matplotlib",
        "main.py"
    ]

    try:
        subprocess.check_call(args)
        print("\n" + "=" * 60)
        print("Build successful!")
        print("Output directory: " + str(project_dir / "dist"))
        print("=" * 60)
        print("\nUsage:")
        print("  - Windows: dist\\HypertensionReminder.exe")
        print("  - macOS: dist/HypertensionReminder.app")
        print("  - Linux: dist/HypertensionReminder")
        print("\nDouble-click to run, no Python required!")
        print("Data saved to: ~/.hypertension_reminder/")
        print("=" * 60)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
