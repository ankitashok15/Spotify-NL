from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeedTheme:
    theme_id: str
    label: str
    keywords: tuple[str, ...]


SEED_THEMES: list[SeedTheme] = [
    SeedTheme("repetitive_recommendations", "Repetitive recommendations", ("repetitive", "same songs", "repeat", "never change")),
    SeedTheme("poor_discover_weekly", "Poor Discover Weekly", ("discover weekly", "discover_weekly", "dw")),
    SeedTheme("playlist_fatigue", "Playlist fatigue", ("playlist", "playlists", "curated")),
    SeedTheme("genre_repetition", "Genre repetition", ("genre", "same genre", "one genre")),
    SeedTheme("poor_exploration", "Poor exploration", ("explore", "exploration", "find new")),
    SeedTheme("liked_songs_repetition", "Liked Songs repetition", ("liked songs", "favorites repeat")),
    SeedTheme("algorithm_bias", "Algorithm bias", ("algorithm", "biased", "bias")),
    SeedTheme("podcast_interference", "Podcast interference", ("podcast", "podcasts")),
    SeedTheme("missing_niche_artists", "Missing niche artists", ("niche", "underground", "small artist")),
    SeedTheme("mood_mismatch", "Mood mismatch", ("mood", "wrong vibe", "sad when happy")),
    SeedTheme("context_mismatch", "Context mismatch", ("context", "workout", "study", "sleep")),
    SeedTheme("discovery_stagnation", "Discovery stagnation", ("stagnant", "stuck", "no new music")),
]


def map_text_to_theme(text: str, primary_issue: str | None = None) -> str | None:
    haystack = f"{text} {primary_issue or ''}".lower()
    best_id: str | None = None
    best_hits = 0
    for theme in SEED_THEMES:
        hits = sum(1 for kw in theme.keywords if kw in haystack)
        if theme.theme_id.replace("_", " ") in haystack:
            hits += 2
        if hits > best_hits:
            best_hits = hits
            best_id = theme.theme_id
    return best_id if best_hits > 0 else None


def theme_label(theme_id: str) -> str:
    for theme in SEED_THEMES:
        if theme.theme_id == theme_id:
            return theme.label
    return theme_id.replace("_", " ").title()
