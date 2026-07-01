import importlib.util
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "_page_bootstrap", _root / "pages" / "_page_bootstrap.py"
)
_pb = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_pb)

import streamlit as st

st.set_page_config(page_title="Themes", page_icon="🎯", layout="wide")
st.title("Discovery Themes")

if _pb.deploy_config_issues():
    _pb.render_deploy_config_help()
    st.stop()

try:
    from phase01.database.session import get_db_session
    from phase05.database.repositories import ClusterRepository

    with get_db_session() as session:
        clusters = ClusterRepository(session).list_clusters(limit=30)

    if not clusters:
        st.info("No clusters yet — run Phase 5 clustering.")
    for c in clusters:
        with st.expander(f"{c.label} ({c.member_count} reviews · avg ★ {c.avg_rating})"):
            st.write(c.description or "—")
            st.caption(c.taxonomy_theme_id or "")
except Exception as exc:
    st.error(str(exc))
