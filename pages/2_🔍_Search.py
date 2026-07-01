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

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
st.title("Semantic Search")

if _pb.deploy_config_issues():
    _pb.render_deploy_config_help()
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
