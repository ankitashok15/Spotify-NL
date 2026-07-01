import streamlit as st

from streamlit_lib.bootstrap import init_runtime

init_runtime()

st.set_page_config(page_title="Ask RAG", page_icon="💬", layout="wide")
st.title("Ask (RAG)")

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
