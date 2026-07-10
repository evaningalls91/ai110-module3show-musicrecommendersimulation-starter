"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys

from recommender import load_songs, recommend_songs

# Ensure UTF-8 output so the header emoji and score bars render everywhere
# (Windows consoles default to cp1252, which can't encode them).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

WIDTH = 60  # total width of the output rules/headers


def rule(char: str = "=") -> str:
    """A horizontal divider line."""
    return char * WIDTH


def score_bar(score: float, size: int = 20) -> str:
    """A simple text meter, e.g. '██████████████░░░░░░'."""
    filled = round(score * size)
    return "█" * filled + "░" * (size - filled)


def print_profile(prefs: dict) -> None:
    """Show the user's taste profile as an aligned key/value block."""
    print("Your taste profile")
    print(rule("-"))
    label_width = max(len(k) for k in prefs)
    for key, value in prefs.items():
        print(f"  {key.replace('_', ' ').title():<{label_width + 2}} {value}")
    print()


def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    """Render a single recommendation: title, tags, score bar, and reasons."""
    print(f"  {rank}. {song['title']}  —  {song['artist']}")
    print(f"     {song['genre']} / {song['mood']}")
    print(f"     Score {score:.2f}  {score_bar(score)}")
    print("     Why:")
    for reason in explanation.split(";"):
        reason = reason.strip()
        if reason:
            print(f"       • {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile. Any of these keys is optional — score_song only
    # uses the preferences you provide (see recommender.py).
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "valence": 0.8,
        "danceability": 0.8,
        "likes_acoustic": False,
        "tempo": 120,
    }

    k = 5
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print()
    print(rule())
    print("  🎵  MUSIC RECOMMENDER".ljust(WIDTH))
    print(rule())
    print()

    print_profile(user_prefs)

    print(f"Top {k} recommendations")
    print(rule("-"))
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)


if __name__ == "__main__":
    main()
