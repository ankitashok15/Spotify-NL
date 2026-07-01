import streamlit as st

from streamlit_lib.bootstrap import apply_secrets

apply_secrets()

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")
st.title("Semantic Search")

query = st.text_input("Query", value="free users hate playlist recommendations")
top_k = st.slider("Top K", 3, 30, 10)

if st.button("Search", type="primary"):
    try:
        from phase03.search.semantic_search import SemanticSearchService

        with st.spinner("Searching…"):
            res = SemanticSearchService().search(query, top_k=top_k)
        st.caption(f"{len(res.results)} results · {res.took_ms:.0f} ms")
        for hit in res.results:
            with st.expander(f"★ {hit.rating} · score {hit.score:.3f} · {hit.primary_issue or '—'}"):
                st.write(hit.text_en or "No text")
                st.caption(f"{hit.subscription_type} · {hit.device_type} · {hit.review_id}")
    except Exception as exc:
        st.error(str(exc))
