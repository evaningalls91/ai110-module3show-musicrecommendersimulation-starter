import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Optional numeric targets (default to neutral so existing callers/tests
    # keep working). These let the score use every numeric audio feature.
    target_valence: float = 0.5
    target_danceability: float = 0.5
    target_tempo: float = 120.0


# ---------------------------------------------------------------------------
# Scoring configuration
# ---------------------------------------------------------------------------
# Per-feature weights. Tune these to change the recommender's behaviour.
# Categorical features contribute their full weight on an exact match, 0 otherwise.
# Numeric features contribute weight * similarity, where similarity is in [0, 1].
WEIGHTS: Dict[str, float] = {
    "genre": 2.0,          # categorical match
    "mood": 1.5,           # categorical match
    "energy": 1.5,         # strongest numeric signal
    "acousticness": 1.0,   # driven by likes_acoustic
    "valence": 1.0,
    "danceability": 1.0,
    "tempo_bpm": 0.5,      # correlates with energy; kept low
}

# Range used to normalise tempo distance into [0, 1].
TEMPO_RANGE = 100.0


def _similarity(target: float, value: float) -> float:
    """Similarity in [0, 1] for two 0-1 features (1 = identical)."""
    return 1.0 - abs(target - value)


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences, returning (score in [0, 1], reasons)."""
    weighted_sum = 0.0
    active_weight = 0.0
    # Collect (weight, reason) so we can surface the top contributing features.
    contributions: List[Tuple[float, str]] = []

    # --- Categorical: genre ---
    genre_pref = user_prefs.get("genre")
    if genre_pref is not None:
        w = WEIGHTS["genre"]
        active_weight += w
        if song["genre"] == genre_pref:
            weighted_sum += w
            contributions.append((w, f"matches your favorite genre ({genre_pref})"))

    # --- Categorical: mood ---
    mood_pref = user_prefs.get("mood")
    if mood_pref is not None:
        w = WEIGHTS["mood"]
        active_weight += w
        if song["mood"] == mood_pref:
            weighted_sum += w
            contributions.append((w, f"matches your mood ({mood_pref})"))

    # --- Numeric: energy ---
    energy_pref = user_prefs.get("energy")
    if energy_pref is not None:
        w = WEIGHTS["energy"]
        sim = _similarity(energy_pref, song["energy"])
        weighted_sum += w * sim
        active_weight += w
        if sim >= 0.85:
            contributions.append(
                (w * sim, f"energy close to target ({song['energy']:.2f} vs {energy_pref:.2f})")
            )

    # --- Numeric: valence ---
    valence_pref = user_prefs.get("valence")
    if valence_pref is not None:
        w = WEIGHTS["valence"]
        sim = _similarity(valence_pref, song["valence"])
        weighted_sum += w * sim
        active_weight += w
        if sim >= 0.85:
            contributions.append((w * sim, f"positivity fits your taste ({song['valence']:.2f})"))

    # --- Numeric: danceability ---
    dance_pref = user_prefs.get("danceability")
    if dance_pref is not None:
        w = WEIGHTS["danceability"]
        sim = _similarity(dance_pref, song["danceability"])
        weighted_sum += w * sim
        active_weight += w
        if sim >= 0.85:
            contributions.append((w * sim, f"danceability fits your taste ({song['danceability']:.2f})"))

    # --- Numeric: acousticness (derived from likes_acoustic) ---
    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        w = WEIGHTS["acousticness"]
        target = 1.0 if likes_acoustic else 0.0
        sim = _similarity(target, song["acousticness"])
        weighted_sum += w * sim
        active_weight += w
        if sim >= 0.85:
            label = "acoustic sound you like" if likes_acoustic else "produced/electronic sound you like"
            contributions.append((w * sim, f"{label} ({song['acousticness']:.2f})"))

    # --- Numeric: tempo (raw BPM, distance normalised) ---
    tempo_pref = user_prefs.get("tempo")
    if tempo_pref is not None:
        w = WEIGHTS["tempo_bpm"]
        sim = 1.0 - min(1.0, abs(tempo_pref - song["tempo_bpm"]) / TEMPO_RANGE)
        weighted_sum += w * sim
        active_weight += w
        if sim >= 0.85:
            contributions.append((w * sim, f"tempo near your target ({song['tempo_bpm']:.0f} BPM)"))

    score = weighted_sum / active_weight if active_weight else 0.0

    # Top reasons first; fall back to a generic note if nothing stood out.
    contributions.sort(key=lambda c: c[0], reverse=True)
    reasons = [reason for _, reason in contributions]
    if not reasons:
        reasons = ["broadly similar to your preferences"]

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top k as (song, score, explanation) tuples, highest first."""
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; \n\t".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of songs to recommend from."""
        self.songs = songs

    @staticmethod
    def _prefs_from_profile(user: UserProfile) -> Dict:
        """Map a UserProfile onto the dict keys score_song understands."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "valence": user.target_valence,
            "danceability": user.target_danceability,
            "tempo": user.target_tempo,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for the given user profile, highest score first."""
        prefs = self._prefs_from_profile(user)
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a one-line string explaining the song's score for this user."""
        prefs = self._prefs_from_profile(user)
        score, reasons = score_song(prefs, asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts, casting numeric columns to numbers."""
    numeric_floats = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for col in numeric_floats:
                row[col] = float(row[col])
            songs.append(row)
    return songs
