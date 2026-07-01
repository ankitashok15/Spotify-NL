import importlib.util
import os
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "_page_bootstrap", _root / "pages" / "_page_bootstrap.py"
)
_pb = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_pb)

import streamlit as st

st.set_page_config(page_title="Ask RAG", page_icon="💬", layout="wide")
st.title("Ask (RAG)")

if _pb.deploy_config_issues():
    _pb.render_deploy_config_help()
    st.stop()

question = st.text_area("Question", value="Why do free users hate playlist recommendations?", height=100)

if st.button("Ask", type="primary"):
    try:
        from phase01.database.session import get_db_session
        from phase04.rag.pipeline import RAGPipeline

        with get_db_session() as session:
            with st.spinner("Retrieving reviews and generating answer…"):
                result = RAGPipeline(session).query(question)

        c1, c2, c3 = st.columns(3)
        c1.metric("Reviews considered", result.reviews_considered)
        c2.metric("Citations", result.reviews_cited)
        c3.metric("Confidence", f"{result.confidence * 100:.0f}%")

        if result.reviews_considered == 0:
            st.warning(
                "No reviews were retrieved. Ensure data is loaded in your cloud database "
                "and vectors are indexed in Qdrant (`python scripts/index_vectors.py embed`)."
            )

        if result.answer:
            st.markdown("### Answer")
            st.markdown(result.answer)
        else:
            st.warning("The model returned an empty answer. Try rephrasing your question.")

        if result.warnings:
            with st.expander("Warnings"):
                for warning in result.warnings:
                    st.write(warning)

        if result.citations:
            st.markdown("### Citations")
            for cite in result.citations:
                st.markdown(f"> ★ {cite.get('rating')} — {cite.get('excerpt', '')[:300]}")
        elif result.reviews_considered > 0:
            st.caption("Answer generated but no citation blocks were attached.")

        st.caption(f"Intent: `{result.intent}` · Search query: `{result.search_query}` · {result.took_ms:.0f} ms")

    except Exception as exc:
        st.error(str(exc))
        if "GEMINI_API_KEY" in str(exc):
            st.caption("Add GEMINI_API_KEY to Streamlit secrets and reboot the app.")
        if "QDRANT" in str(exc).upper() or "qdrant" in str(exc):
            st.caption("Check QDRANT_URL and QDRANT_API_KEY in Streamlit secrets.")
