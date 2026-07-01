#!/usr/bin/env python3
"""Delegate to Phase 2 extraction CLI."""

import runpy
import sys
from pathlib import Path

_CLI = Path(__file__).resolve().parent.parent / "phases" / "phase-02-ai-understanding" / "cli" / "extract.py"
sys.path.insert(0, str(_CLI.parent.parent))
runpy.run_path(str(_CLI), run_name="__main__")
