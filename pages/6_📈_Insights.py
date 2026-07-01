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

st.set_page_config(page_title="Insights", page_icon="📈", layout="wide")
st.title("Product Insights")

if _pb.deploy_config_issues():
    _pb.render_deploy_config_help()
    st.stop()

try:
    from phase01.database.session import get_db_session
    from phase05.database.repositories import InsightRepository

    with get_db_session() as session:
        items = InsightRepository(session).list_insights(limit=30)

    if not items:
        st.info("No insights yet — run Phase 5 insights pipeline.")
    for item in items:
        st.markdown(f"**{item.title}** `{item.insight_type}`")
        st.caption(item.summary[:500])
        st.divider()
except Exception as exc:
    st.error(str(exc))
