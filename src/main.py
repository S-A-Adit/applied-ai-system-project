"""
Command line runner for the Gym Equipment Recommender — classic rule-based or AI-powered RAG mode.

Usage:
    python -m src.main          (from project root)

Set GOOGLE_API_KEY in a .env file at the project root to use RAG mode.
"""

import os
import sys
from dotenv import load_dotenv

from src.recommender import load_equipment, recommend_equipment
from src.rag import parse_query, retrieve, generate_recommendation

load_dotenv()


def rag_mode(items: list) -> None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found. Add it to a .env file in the project root.")
        sys.exit(1)

    print("Gym Equipment Recommender — AI Mode (type 'quit' to exit)\n")
    while True:
        query = input("What are you looking for? ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        print("\nStep 1: Parsing your request...")
        user_prefs = parse_query(query, api_key)
        print(f"         → muscle_group={user_prefs['muscle_group'] or 'any'}, "
              f"goal={user_prefs['goal'] or 'any'}, space={user_prefs['space']}, "
              f"budget={user_prefs['budget']}, skill={user_prefs['skill_level']}")

        print("Step 2: Retrieving best matches...")
        results = retrieve(user_prefs, items, k=3)
        for item, score in results:
            print(f"         → {item['equipment']} (score={score:.2f})")

        print("Step 3: Generating recommendation...\n")
        recommendation = generate_recommendation(query, results, user_prefs, api_key)

        print("--- Recommendation ---")
        print(recommendation)
        print("----------------------\n")


def classic_mode(items: list) -> None:
    print("\nMuscle groups : full_body, legs, chest, back, core, upper_body, recovery")
    print("Goals         : muscle_gain, fat_loss, strength, toning, conditioning, recovery")
    print("Space         : small, medium, large")
    print("Budget        : low, medium, high")
    print("Skill level   : beginner, intermediate\n")

    muscle = input("Target muscle group: ").strip()
    goal   = input("Fitness goal       : ").strip()
    space  = input("Available space    : ").strip()
    budget = input("Budget             : ").strip()
    skill  = input("Skill level        : ").strip()

    user_prefs = {
        "muscle_group": muscle,
        "goal": goal,
        "space": space,
        "budget": budget,
        "skill_level": skill,
    }
    recommendations = recommend_equipment(user_prefs, items, k=3)
    print("\nTop recommendations (rule-based):\n")
    for item, score, explanation in recommendations:
        print(f"  {item['equipment']} ({item['type']})  —  Score: {score:.2f}")
        print(f"  {explanation}\n")


def main() -> None:
    items = load_equipment("data/equipments.csv")

    print("\nGym Equipment Recommender")
    print("  [1] Classic rule-based scoring")
    print("  [2] AI-powered RAG (Google Gemini)")
    mode = input("Choose mode: ").strip()

    if mode == "2":
        rag_mode(items)
    else:
        classic_mode(items)


if __name__ == "__main__":
    main()
