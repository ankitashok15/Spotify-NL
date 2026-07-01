import sys
from pathlib import Path

import pytest

_PHASE05 = Path(__file__).resolve().parents[2] / "phases" / "phase-05-clustering-insights"
sys.path.insert(0, str(_PHASE05))

from phase05.clustering.assigner import aggregate_cluster_stats  # noqa: E402
from phase05.clustering.clusterer import VectorPoint  # noqa: E402
from phase05.clustering.taxonomy import SEED_THEMES, map_text_to_theme, theme_label  # noqa: E402


def test_seed_taxonomy_has_twelve_themes():
    assert len(SEED_THEMES) == 12


def test_map_text_to_discover_weekly():
    theme = map_text_to_theme("Discover Weekly keeps giving me the same terrible picks", None)
    assert theme == "poor_discover_weekly"


def test_theme_label():
    assert theme_label("playlist_fatigue") == "Playlist fatigue"


def test_aggregate_cluster_stats():
    points = [
        VectorPoint("r1", [1.0, 0.0], {"rating": 2, "thumbs_up": 5, "subscription_type": "free", "text_en": "bad dw"}),
        VectorPoint("r2", [0.9, 0.1], {"rating": 1, "thumbs_up": 3, "subscription_type": "free", "text_en": "discover weekly repeats"}),
    ]
    assignments = {"r1": 0, "r2": 0}
    stats = aggregate_cluster_stats(assignments, points)
    assert 0 in stats
    assert stats[0]["member_count"] == 2
    assert stats[0]["avg_rating"] == 1.5
    assert len(stats[0]["centroid"]) == 2
