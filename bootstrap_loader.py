"""Load streamlit_bootstrap by file path — works on Streamlit Cloud without sys.path."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def repo_root(caller_file: str) -> Path:
    path = Path(caller_file).resolve()
    if path.parent.name == "pages":
        return path.parents[1]
    return path.parent


def load_bootstrap(caller_file: str) -> ModuleType:
    """Import streamlit_bootstrap from the repo root using an absolute path."""
    name = "streamlit_bootstrap"
    cached = sys.modules.get(name)
    if cached is not None:
        return cached

    root = repo_root(caller_file)
    bootstrap_path = root / "streamlit_bootstrap.py"
    if not bootstrap_path.is_file():
        raise ImportError(
            f"streamlit_bootstrap.py not found at {bootstrap_path}. "
            "Check that the file is committed on the deployed branch."
        )

    spec = importlib.util.spec_from_file_location(name, bootstrap_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load bootstrap module from {bootstrap_path}")

    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
