#!/usr/bin/env python3
"""Delegate to Phase 6 agent CLI."""

import runpy
import sys
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "phases" / "phase-06-agentic-scale" / "cli" / "agent.py"
sys.path.insert(0, str(target.parent.parent))
runpy.run_path(str(target), run_name="__main__")
