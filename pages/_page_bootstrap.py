"""Shared Streamlit page bootstrap — import via bootstrap_loader, not directly."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "bootstrap_loader", _ROOT / "bootstrap_loader.py"
)
_loader_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_loader_mod)

_sb = _loader_mod.load_bootstrap(__file__)
_sb.init_runtime()

deploy_config_issues = _sb.deploy_config_issues
init_runtime = _sb.init_runtime
render_deploy_config_help = _sb.render_deploy_config_help
