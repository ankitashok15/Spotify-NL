import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from streamlit_bootstrap import deploy_config_issues, init_runtime, render_deploy_config_help

init_runtime()

st.set_page_config(page_title="Insights", page_icon="📈", layout="wide")
st.title("Product Insights")

if deploy_config_issues():
    render_deploy_config_help()
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
