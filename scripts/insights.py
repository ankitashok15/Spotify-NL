#!/usr/bin/env python3
"""Delegate to Phase 5 insights CLI."""

import runpy
import sys
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "phases" / "phase-05-clustering-insights" / "cli" / "insights.py"
sys.path.insert(0, str(target.parent.parent))
runpy.run_path(str(target), run_name="__main__")
