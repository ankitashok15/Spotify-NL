#!/usr/bin/env python3
"""Delegate to Phase 3 embed CLI."""

import runpy
import sys
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "phases" / "phase-03-semantic-search" / "cli" / "embed.py"
sys.path.insert(0, str(target.parent.parent))
runpy.run_path(str(target), run_name="__main__")
