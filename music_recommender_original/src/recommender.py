from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV of songs and return a list of dicts with numeric fields cast to float/int."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> float:
    """Score one song 0–5.0: +1.0 genre match, +1.5 mood match, +2.0 energy proximity, +0.5 acousticness fit.
    Experiment — energy-first: genre weight halved (2.0 → 1.0), energy multiplier doubled (1.0 → 2.0).
    Max possible score: 1.0 + 1.5 + 2.0 + 0.5 = 5.0
    """
    score = 0.0

    # genre match weight: 1.0 (halved — experiment: energy-first)
    if song.get("genre") == user_prefs.get("genre"):
        score += 1.0

    # mood match weight: 1.5 (unchanged)
    if song.get("mood") == user_prefs.get("mood"):
        score += 1.5

    # energy proximity weight: 2.0 * (1.0 - distance), max +2.0 (doubled — experiment: energy-first)
    if "energy" in user_prefs:
        score += 2.0 * (1.0 - abs(song["energy"] - user_prefs["energy"]))

    # acousticness fit weight: multiplied by 0.5, max +0.5 (unchanged)
    if "likes_acoustic" in user_prefs:
        if user_prefs["likes_acoustic"]:
            score += song["acousticness"] * 0.5
        else:
            score += (1.0 - song["acousticness"]) * 0.5

    return score


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort descending, and return the top-k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        s = score_song(user_prefs, song)
        matches = []
        if song.get("genre") == user_prefs.get("genre"):
            matches.append(f"genre={song['genre']}")
        if song.get("mood") == user_prefs.get("mood"):
            matches.append(f"mood={song['mood']}")
        matches.append(f"energy={song['energy']} vs target={user_prefs.get('energy', '?')}")
        explanation = "Matches: " + ", ".join(matches)
        scored.append((song, s, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
