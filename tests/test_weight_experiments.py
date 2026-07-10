"""
Experiments: how do rankings change when we retune the WEIGHTS or drop a feature?

score_song reads the module-level ``recommender.WEIGHTS`` dict at call time, so
we can temporarily override individual weights (or zero one out to "remove" it)
and observe the effect on ``recommend_songs``.

Run just these:
    python -m pytest tests/test_weight_experiments.py -v
See the human-readable comparison table:
    python tests/test_weight_experiments.py
"""

import os
import sys
from contextlib import contextmanager

# Make ``src`` importable and locate the real song catalog, regardless of CWD.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data", "songs.csv")

from src import recommender  # noqa: E402
from src.recommender import load_songs, recommend_songs  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
@contextmanager
def override_weights(**changes):
    """Temporarily patch entries in recommender.WEIGHTS, restoring them after."""
    original = dict(recommender.WEIGHTS)
    recommender.WEIGHTS.update(changes)
    try:
        yield
    finally:
        recommender.WEIGHTS.clear()
        recommender.WEIGHTS.update(original)


def ranked_titles(prefs, songs, k=None):
    """Return song titles ordered best-first under the current WEIGHTS."""
    k = len(songs) if k is None else k
    return [song["title"] for song, _score, _why in recommend_songs(prefs, songs, k=k)]


# A profile with several pop songs in play, where mood is the tie-breaker:
# 'Gym Hero' is the only pop+intense track, so mood decides whether it leads.
BASE_PREFS = {
    "genre": "pop",
    "mood": "intense",
    "energy": 0.5,
    "valence": 0.5,
    "danceability": 0.5,
    "likes_acoustic": False,
    "tempo": 120,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
try:
    import pytest

    @pytest.fixture(scope="module")
    def songs():
        return load_songs(DATA)
except ImportError:  # allow running as a plain script without pytest installed
    pytest = None


# ---------------------------------------------------------------------------
# Removing the mood check
# ---------------------------------------------------------------------------
def test_removing_mood_via_dropping_key_changes_ranking(songs):
    """Dropping the 'mood' preference should reorder the results vs the baseline."""
    with_mood = ranked_titles(BASE_PREFS, songs)

    no_mood_prefs = {k: v for k, v in BASE_PREFS.items() if k != "mood"}
    without_mood = ranked_titles(no_mood_prefs, songs)

    assert with_mood != without_mood, "removing mood should change the ranking"


def test_mood_gives_the_intense_pop_song_its_lead(songs):
    """'Gym Hero' (pop+intense) should rank higher WITH mood than without it."""
    with_mood = ranked_titles(BASE_PREFS, songs)

    no_mood_prefs = {k: v for k, v in BASE_PREFS.items() if k != "mood"}
    without_mood = ranked_titles(no_mood_prefs, songs)

    assert with_mood.index("Gym Hero") < without_mood.index("Gym Hero"), (
        "the mood match should pull the intense pop song up the ranking"
    )


def test_zeroing_mood_weight_equals_dropping_mood_key(songs):
    """Setting the mood weight to 0 is equivalent to not expressing a mood at all."""
    no_mood_prefs = {k: v for k, v in BASE_PREFS.items() if k != "mood"}
    dropped = ranked_titles(no_mood_prefs, songs)

    with override_weights(mood=0.0):
        zeroed = ranked_titles(BASE_PREFS, songs)

    assert zeroed == dropped, (
        "a zero mood weight removes mood from both numerator and denominator, "
        "so it should match simply omitting the mood preference"
    )


# ---------------------------------------------------------------------------
# Retuning the weights
# ---------------------------------------------------------------------------
def test_boosting_genre_weight_clusters_genre_matches_at_top(songs):
    """With genre weight dominating, all pop songs should occupy the top slots."""
    pop_count = sum(1 for s in songs if s["genre"] == "pop")

    with override_weights(genre=100.0):
        top = ranked_titles(BASE_PREFS, songs, k=pop_count)

    top_genres = [s["genre"] for s in songs if s["title"] in top]
    assert all(g == "pop" for g in top_genres), (
        "an overwhelming genre weight should float every pop song to the top"
    )


def test_energy_dominant_weights_rank_by_energy_closeness(songs):
    """When energy is the only meaningful weight, the top pick is the closest energy match."""
    energy_only_profile = {"energy": 0.90}  # near the high-energy tracks

    # Zero out every other weight so energy alone decides the order.
    others = {name: 0.0 for name in recommender.WEIGHTS if name != "energy"}
    with override_weights(**others):
        top = ranked_titles(energy_only_profile, songs, k=1)[0]

    closest = min(songs, key=lambda s: abs(s["energy"] - 0.90))["title"]
    assert top == closest, "energy-dominant weighting should pick the nearest energy match"


def test_reweighting_can_change_the_number_one_pick(songs):
    """A genre-heavy vs energy-heavy weighting should not always agree on #1."""
    with override_weights(genre=100.0):
        genre_leader = ranked_titles(BASE_PREFS, songs, k=1)[0]

    with override_weights(energy=100.0):
        energy_leader = ranked_titles(BASE_PREFS, songs, k=1)[0]

    assert genre_leader != energy_leader, (
        "shifting weight from genre to energy should move the top recommendation"
    )


# ---------------------------------------------------------------------------
# Human-readable comparison when run directly
# ---------------------------------------------------------------------------
def _demo():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    songs = load_songs(DATA)

    scenarios = [
        ("Baseline weights", BASE_PREFS, {}),
        ("Mood removed (drop key)", {k: v for k, v in BASE_PREFS.items() if k != "mood"}, {}),
        ("Mood weight = 0", BASE_PREFS, {"mood": 0.0}),
        ("Genre weight = 100", BASE_PREFS, {"genre": 100.0}),
        ("Energy weight = 100", BASE_PREFS, {"energy": 100.0}),
        ("All weights equal (1.0)", BASE_PREFS, {k: 1.0 for k in recommender.WEIGHTS}),
    ]

    print(f"\nProfile: {BASE_PREFS}\n")
    for name, prefs, weight_changes in scenarios:
        with override_weights(**weight_changes):
            recs = recommend_songs(prefs, songs, k=5)
        print(f"{name}")
        print("-" * 60)
        for rank, (song, score, _why) in enumerate(recs, start=1):
            print(f"  {rank}. {score:.3f}  {song['title']:<22} [{song['genre']}/{song['mood']}]")
        print()


if __name__ == "__main__":
    _demo()
