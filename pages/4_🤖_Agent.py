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

        with get_db_session() as session:
            llm = GeminiProvider(model_name=p6.gemini_model_rag) if p6.gemini_api_key else None
            with st.spinner("Running agent tools…"):
                result = AgentOrchestrator(session, llm).run(question, debug=True)

        st.metric("Steps", result.steps)
        st.metric("Confidence", f"{result.confidence * 100:.0f}%")
        st.markdown(result.answer)

        if result.tool_trace:
            with st.expander("Tool trace"):
                for step in result.tool_trace:
                    st.write(f"**{step.tool}** — {step.result_summary}")
    except Exception as exc:
        st.error(str(exc))
