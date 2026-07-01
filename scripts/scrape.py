#!/usr/bin/env python3
"""Root entry point — delegates to Phase 1 CLI."""

import runpy
import sys
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "phases" / "phase-01-data-foundation" / "cli" / "scrape.py"
sys.path.insert(0, str(target.parent.parent))
runpy.run_path(str(target), run_name="__main__")
