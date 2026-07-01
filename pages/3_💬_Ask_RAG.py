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
            with st.spinner("Generating answer…"):
                result = RAGPipeline(session).query(question)
        st.metric("Confidence", f"{result.confidence * 100:.0f}%")
        st.markdown(result.answer)
        for cite in result.citations:
            st.markdown(f"> ★ {cite.get('rating')} — {cite.get('excerpt', '')[:300]}")
    except Exception as exc:
        st.error(str(exc))
