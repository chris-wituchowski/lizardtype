#!/usr/bin/env python3
"""
Build script for LizardType — packages the game into a single executable
using PyInstaller. Works on both Windows and Linux.

Usage:
    python build.py

The output executable will be in the dist/ folder.
"""

import subprocess
import sys
import os

def main():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    root_dir = os.path.dirname(os.path.abspath(__file__))
    separator = ";" if sys.platform == "win32" else ":"

    # Paths
    run_py = os.path.join(root_dir, "run.py")
    src_dir = os.path.join(root_dir, "src")
    image_cache_dir = os.path.join(root_dir, "image_cache")

    # Build the PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "LizardType",
        # Bundle the src/ package so imports work
        "--add-data", f"{src_dir}{separator}src",
        # Bundle the cached images
        "--add-data", f"{image_cache_dir}{separator}image_cache",
        # Hidden imports that PyInstaller may not detect automatically
        "--hidden-import", "reptile_data",
        "--hidden-import", "sea_creature_data",
        "--hidden-import", "image_manager",
        "--hidden-import", "pygame",
        "--hidden-import", "requests",
        "--hidden-import", "PIL",
        # Overwrite previous build without prompting
        "--noconfirm",
        # No console window on Windows (change to --console for debugging)
        "--windowed",
        # Entry point
        run_py,
    ]

    print("=" * 60)
    print("Building LizardType executable...")
    print(f"  Platform : {sys.platform}")
    print(f"  Entry    : {run_py}")
    print("=" * 60)
    print()

    subprocess.check_call(cmd)

    ext = ".exe" if sys.platform == "win32" else ""
    dist_path = os.path.join(root_dir, "dist", f"LizardType{ext}")
    print()
    print("=" * 60)
    print(f"Build complete!  Executable: {dist_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
