#!/usr/bin/env python3
"""Delegate to Phase 4 RAG CLI."""

import runpy
import sys
from pathlib import Path

target = Path(__file__).resolve().parents[1] / "phases" / "phase-04-rag-qa" / "cli" / "query.py"
sys.path.insert(0, str(target.parent.parent))
runpy.run_path(str(target), run_name="__main__")
