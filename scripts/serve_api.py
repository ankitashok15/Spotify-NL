#!/usr/bin/env python3
"""Delegate to unified backend server."""

import runpy
import sys
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "cli" / "serve.py"
sys.path.insert(0, str(target.parents[1]))
runpy.run_path(str(target), run_name="__main__")
