import streamlit as st

from streamlit_lib.bootstrap import apply_secrets

apply_secrets()

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

    **Deploy pairing:** This Streamlit app is the Python backend on Streamlit Cloud.
    The React UI is hosted separately on Vercel and calls the REST API (see `DEPLOY.md`).
    """
)

st.info(
    "Configure secrets in Streamlit Cloud (DATABASE_URL, GEMINI_API_KEY, QDRANT_URL) "
    "before running pipelines."
)
