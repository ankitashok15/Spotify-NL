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

st.set_page_config(page_title="Agent", page_icon="🤖", layout="wide")
st.title("Agent — Multi-step analysis")

if _pb.deploy_config_issues():
    _pb.render_deploy_config_help()
    st.stop()

question = st.text_area(
    "Analytical question",
    value="What discovery issues do free phone users report most, and how has that changed in 2026?",
    height=100,
)

if st.button("Run agent", type="primary"):
    try:
        from phase01.database.session import get_db_session
        from phase02.shared.llm_gemini import GeminiProvider
        from phase06.agent.orchestrator import AgentOrchestrator
        from phase06.shared.config import settings as p6

        llm = None
        if os.environ.get("GEMINI_API_KEY"):
            llm = GeminiProvider(model_name=p6.gemini_model_rag)
        else:
            st.warning("GEMINI_API_KEY not loaded — agent will use limited fallback mode.")

        with get_db_session() as session:
            with st.spinner("Running agent tools…"):
                result = AgentOrchestrator(session, llm).run(question, debug=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Steps", result.steps)
        c2.metric("Citations", len(result.citations))
        c3.metric("Confidence", f"{result.confidence * 100:.0f}%")

        if not result.answer or result.answer.strip() == "No review evidence available to summarize.":
            st.warning(
                "The agent found little or no review evidence. Load data into your cloud database "
                "with scrape/extract scripts, then try a broader question."
            )

        if result.answer:
            st.markdown("### Answer")
            st.markdown(result.answer)

        if result.citations:
            st.markdown("### Citations")
            for cite in result.citations:
                quote = cite.get("quote") or cite.get("excerpt") or ""
                st.markdown(f"> ★ {cite.get('rating')} — {quote[:300]}")

        if result.tool_trace:
            with st.expander("Tool trace"):
                for step in result.tool_trace:
                    st.write(f"**{step.tool}** — {step.result_summary}")
                    if step.result:
                        st.json(step.result)

        st.caption(f"Completed in {result.took_ms:.0f} ms")

    except Exception as exc:
        st.error(str(exc))
