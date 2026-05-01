"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

   # Profile 1 — genre doesn't exist
    user_prefs = {"genre": "bluegrass", "mood": "chill", "energy": 0.4}

    # Profile 2 — genre beats mood
    user_prefs = {"genre": "pop", "mood": "angry", "energy": 0.5}

    # Profile 3 — high energy classical
    user_prefs = {"genre": "classical", "mood": "peaceful", "energy": 0.99}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
