import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from streamlit_bootstrap import gemini_key_configured, init_runtime

init_runtime()

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

if gemini_key_configured():
    st.success("GEMINI_API_KEY is configured.")
else:
    st.error(
        "GEMINI_API_KEY is missing. In Streamlit Cloud → App settings → Secrets, add:\n\n"
        "`GEMINI_API_KEY = \"your-key-from-aistudio.google.com\"`"
    )

st.info(
    "The React UI on Vercel uses a separate REST API (Render). "
    "Set `VITE_API_URL` on Vercel to your API host — not this Streamlit URL."
)
