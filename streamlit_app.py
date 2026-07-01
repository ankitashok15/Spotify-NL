import importlib.util
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "bootstrap_loader", _ROOT / "bootstrap_loader.py"
)
_loader = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_loader)

_sb = _loader.load_bootstrap(__file__)
_sb.init_runtime()

import streamlit as st

deploy_config_issues = _sb.deploy_config_issues
gemini_key_configured = _sb.gemini_key_configured
render_deploy_config_help = _sb.render_deploy_config_help

st.set_page_config(
    page_title="Spotify NL",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Spotify NL — Review Discovery Engine")
st.markdown(
    """
    AI-powered analysis of **Spotify** Google Play reviews (`com.spotify.music`).

    Use the sidebar pages for dashboard, semantic search, RAG Q&A, agent analysis,
    themes, and insights.
    """
)

if deploy_config_issues():
    render_deploy_config_help()
elif gemini_key_configured():
    st.success("Cloud config looks good (GEMINI_API_KEY, DATABASE_URL, QDRANT_URL).")
else:
    st.error("GEMINI_API_KEY is missing in Streamlit secrets.")

st.info(
    "The React UI on Vercel uses a separate REST API (Render). "
    "Set `VITE_API_URL` on Vercel to your API host — not this Streamlit URL."
)
