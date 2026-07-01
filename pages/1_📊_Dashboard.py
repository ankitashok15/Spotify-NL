import streamlit as st

from streamlit_lib.bootstrap import init_runtime

init_runtime()

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("Discovery Dashboard")

try:
    from sqlalchemy import text
    from phase01.database.session import get_db_session
    from phase01.database.repositories import ReviewRepository, ScrapeRunRepository
    from phase01.shared.config import settings as phase1_settings

    with get_db_session() as session:
        repo = ReviewRepository(session)
        _, reviews_total = repo.list_reviews(limit=1, offset=0)

        structured = 0
        clusters = 0
        insights = 0
        top_issues: list = []
        try:
            structured = session.execute(text("SELECT COUNT(*) FROM structured_reviews")).scalar_one() or 0
            clusters = session.execute(text("SELECT COUNT(*) FROM clusters")).scalar_one() or 0
            insights = session.execute(text("SELECT COUNT(*) FROM insights")).scalar_one() or 0
            top_issues = list(
                session.execute(
                    text(
                        """
                        SELECT primary_issue, COUNT(*) AS count
                        FROM structured_reviews
                        WHERE primary_issue IS NOT NULL AND primary_issue != 'none'
                        GROUP BY primary_issue ORDER BY count DESC LIMIT 8
                        """
                    )
                ).mappings()
            )
        except Exception:
            pass

        run = ScrapeRunRepository(session).get_latest(phase1_settings.spotify_app_id)

    vectors = 0
    try:
        from qdrant_client import QdrantClient
        from phase03.shared.config import settings as p3

        client = QdrantClient(url=p3.qdrant_url, check_compatibility=False)
        if client.collection_exists(p3.qdrant_collection):
            vectors = int(client.get_collection(p3.qdrant_collection).points_count or 0)
    except Exception:
        pass

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Reviews", reviews_total)
    c2.metric("Structured", int(structured))
    c3.metric("Vectors", vectors)
    c4.metric("Clusters", int(clusters))
    c5.metric("Insights", int(insights))

    if run:
        st.caption(f"Last scrape: **{run.status}** · {run.reviews_new} new")

    if top_issues:
        st.subheader("Top discovery issues")
        import pandas as pd

        st.bar_chart(pd.DataFrame([dict(r) for r in top_issues]).set_index("primary_issue"))
    else:
        st.info("Run Phase 2 extraction to populate structured issues.")

except Exception as exc:
    st.error(f"Could not load dashboard: {exc}")
    st.caption("Check DATABASE_URL in Streamlit secrets.")
