import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from streamlit_bootstrap import init_runtime

init_runtime()

st.set_page_config(page_title="Themes", page_icon="🎯", layout="wide")
st.title("Discovery Themes")

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
