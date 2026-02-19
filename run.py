#!/usr/bin/env python3
"""
LizardType launcher — run this from the repo root.
    python run.py
"""
import sys
import os

# When frozen by PyInstaller, bundled data is extracted to sys._MEIPASS.
# Otherwise, resolve relative to this script.
if getattr(sys, "frozen", False):
    _BASE_DIR = sys._MEIPASS
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Make sure src/ is importable
sys.path.insert(0, os.path.join(_BASE_DIR, "src"))

from game import main

if __name__ == "__main__":
    main()
