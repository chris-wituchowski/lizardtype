#!/usr/bin/env python3
"""
LizardType launcher — run this from the repo root.
    python run.py
"""
import sys
import os

# Make sure src/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from game import main

if __name__ == "__main__":
    main()
