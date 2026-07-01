import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from streamlit_bootstrap import deploy_config_issues, init_runtime, render_deploy_config_help

init_runtime()

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
st.title("Semantic Search")

if deploy_config_issues():
    render_deploy_config_help()
    st.stop()

query = st.text_input("Query", value="free users hate playlist recommendations")
top_k = st.slider("Top K", 3, 30, 10)

if st.button("Search", type="primary"):
    try:
        from phase03.search.semantic_search import SemanticSearchService

        with st.spinner("Searching…"):
            service = SemanticSearchService()
            res = service.search(query, top_k=top_k)
        if not res.results:
            st.warning("No vectors indexed yet. Run: `python scripts/index_vectors.py --limit 50`")
        st.caption(f"{len(res.results)} results · {res.took_ms:.0f} ms")
        for hit in res.results:
            with st.expander(f"★ {hit.rating} · score {hit.score:.3f} · {hit.primary_issue or '—'}"):
                st.write(hit.text_en or "No text")
                st.caption(f"{hit.subscription_type} · {hit.device_type} · {hit.review_id}")
    except Exception as exc:
        st.error(str(exc))
