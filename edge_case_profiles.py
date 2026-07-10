"""
Edge-case user profiles for stress-testing the recommendation algorithm.

Each profile targets a specific corner of score_song / recommend_songs:
missing data, out-of-range values, conflicts, non-existent categories, etc.

Run from anywhere:
    python edge_case_profiles.py
"""

import os
import sys

# --- Make imports and the data path work regardless of the current directory ---
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
DATA = os.path.join(HERE, "data", "songs.csv")
sys.path.insert(0, SRC)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from recommender import load_songs, recommend_songs, score_song  # noqa: E402


# ---------------------------------------------------------------------------
# Edge-case profiles.  Each is (name, why-it-matters, prefs-dict).
# ---------------------------------------------------------------------------
EDGE_CASES = [
    (
        "Empty profile",
        "No preferences at all. active_weight is 0 -> every song must score 0.0 "
        "without a ZeroDivisionError, and reasons fall back to the generic note.",
        {},
    ),
    (
        "Single preference (genre only)",
        "Only one signal. Score should be 1.0 for every pop song and 0.0 for the "
        "rest — a hard binary partition with no tie-breaker among the pop songs.",
        {"genre": "pop"},
    ),
    (
        "Non-existent genre and mood",
        "Categories that appear in no song ('kpop' / 'sleepy'). Those weights stay "
        "active but never match, so scores are capped below 1.0 for everyone.",
        {"genre": "kpop", "mood": "sleepy", "energy": 0.5},
    ),
    (
        "Case-mismatched category",
        "'Pop' vs the stored 'pop'. Matching is exact/case-sensitive, so this should "
        "match NOTHING — a classic silent-failure edge case.",
        {"genre": "Pop", "mood": "Happy"},
    ),
    (
        "Perfect match to a real song",
        "Copied from 'Neon Stampede' (edm/euphoric). Should score ~1.0 and rank #1 — "
        "verifies the ceiling of the scale is reachable.",
        {
            "genre": "edm",
            "mood": "euphoric",
            "energy": 0.95,
            "valence": 0.92,
            "danceability": 0.94,
            "likes_acoustic": False,
            "tempo": 128,
        },
    ),
    (
        "Out-of-range numerics (above 1.0)",
        "energy/valence/danceability set to 2.0. _similarity returns NEGATIVE values "
        "(1 - |2 - v|), so this exposes that the algorithm does not clamp inputs and "
        "can produce sub-zero contributions.",
        {"energy": 2.0, "valence": 2.0, "danceability": 2.0},
    ),
    (
        "Negative numerics (below 0.0)",
        "energy=-1.0. Again unclamped: similarity goes negative and can drag the "
        "normalized score below 0. Shows the scale isn't guaranteed to stay in [0,1].",
        {"energy": -1.0, "valence": -1.0},
    ),
    (
        "Absurd tempo",
        "tempo=1000 BPM. Distance is clamped by min(1.0, ...) so tempo similarity "
        "floors at 0 rather than going negative — the one numeric feature that IS "
        "bounded. Good contrast with the energy/valence cases above.",
        {"tempo": 1000, "genre": "pop"},
    ),
    (
        "Internally contradictory taste",
        "Wants 'pop' + 'chill' + very high energy. No pop song is chill, and chill "
        "songs are low energy, so no song can satisfy all three — tests graceful "
        "compromise ranking rather than a clean winner.",
        {"genre": "pop", "mood": "chill", "energy": 0.95, "danceability": 0.9},
    ),
    (
        "All-neutral numerics",
        "Every numeric target = 0.5 with no categorical prefs. Rewards the most "
        "'average' songs and should surface middle-of-the-road tracks, not extremes.",
        {"energy": 0.5, "valence": 0.5, "danceability": 0.5, "tempo": 120},
    ),
    (
        "Acoustic lover, extreme",
        "likes_acoustic=True as the ONLY signal. Should rank the most acoustic songs "
        "('Spacewalk Thoughts', 'Coffee Shop Stories') top and the most produced "
        "(edm/metal) at the bottom.",
        {"likes_acoustic": True},
    ),
    (
        "Falsy-but-valid values",
        "energy=0.0 and likes_acoustic=False. These are falsy in Python; score_song "
        "uses `is not None` checks, so they MUST be treated as real preferences, not "
        "skipped. Regression guard against `if not value:` style bugs.",
        {"energy": 0.0, "likes_acoustic": False, "valence": 0.0},
    ),
]


def summarize(prefs: dict, songs: list, k: int = 3) -> None:
    """Print the top-k recommendations plus the min/max score across the catalog."""
    recs = recommend_songs(prefs, songs, k=k)

    # Full-catalog score range tells us if the profile is discriminating at all.
    all_scores = [score_song(prefs, s)[0] for s in songs]
    lo, hi = min(all_scores), max(all_scores)
    print(f"  score range across catalog: {lo:+.3f} .. {hi:+.3f}")

    if not recs:
        print("  (no recommendations returned)")
        return

    for rank, (song, score, _explanation) in enumerate(recs, start=1):
        print(
            f"  {rank}. {score:+.3f}  {song['title']:<22} "
            f"[{song['genre']}/{song['mood']}]"
        )


def main() -> None:
    songs = load_songs(DATA)
    print(f"Loaded {len(songs)} songs from {DATA}\n")

    for name, why, prefs in EDGE_CASES:
        print("=" * 70)
        print(f"EDGE CASE: {name}")
        print(f"  prefs: {prefs}")
        print(f"  why:   {why}")
        print("-" * 70)
        summarize(prefs, songs)
        print()


if __name__ == "__main__":
    main()
