from __future__ import annotations

import json
import logging

from phase02.shared.llm_gemini import GeminiProvider
from phase05.clustering.taxonomy import map_text_to_theme, theme_label
from phase05.shared.config import settings

logger = logging.getLogger(__name__)

_LABEL_SYSTEM = """You label clusters of Spotify Google Play reviews about music discovery.
Return JSON: {"label": "...", "description": "...", "taxonomy_theme_id": "snake_case_or_null"}
Use one of these taxonomy ids when applicable:
repetitive_recommendations, poor_discover_weekly, playlist_fatigue, genre_repetition,
poor_exploration, liked_songs_repetition, algorithm_bias, podcast_interference,
missing_niche_artists, mood_mismatch, context_mismatch, discovery_stagnation
"""


class ClusterLabeler:
    def __init__(self, llm: GeminiProvider | None = None):
        self.llm = llm

    def label_cluster(self, sample_texts: list[str], *, primary_issues: list[str]) -> dict:
        combined = "\n".join(f"- {t[:300]}" for t in sample_texts[:8])
        heuristic_theme = None
        for text, issue in zip(sample_texts, primary_issues, strict=False):
            heuristic_theme = map_text_to_theme(text, issue)
            if heuristic_theme:
                break

        if self.llm is None or not settings.gemini_api_key:
            return self._fallback_label(sample_texts, heuristic_theme)

        try:
            payload = self.llm.generate_json(
                json.dumps(
                    {
                        "sample_reviews": sample_texts[:8],
                        "primary_issues": primary_issues[:8],
                    },
                    ensure_ascii=False,
                ),
                system=_LABEL_SYSTEM,
            )
            theme_id = payload.get("taxonomy_theme_id") or heuristic_theme
            return {
                "label": payload.get("label") or (theme_label(theme_id) if theme_id else "Discovery theme"),
                "description": payload.get("description") or "Cluster of related discovery complaints.",
                "taxonomy_theme_id": theme_id,
            }
        except Exception as exc:
            logger.warning("LLM cluster labeling failed: %s", exc)
            return self._fallback_label(sample_texts, heuristic_theme)

    def _fallback_label(self, sample_texts: list[str], theme_id: str | None) -> dict:
        if theme_id:
            return {
                "label": theme_label(theme_id),
                "description": f"Reviews mapped to seed theme {theme_id}.",
                "taxonomy_theme_id": theme_id,
            }
        snippet = (sample_texts[0][:120] + "...") if sample_texts else "Unlabeled cluster"
        return {
            "label": "Discovery pain point cluster",
            "description": snippet,
            "taxonomy_theme_id": None,
        }
