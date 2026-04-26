"""
Evaluation script for the Gym Equipment Recommender.

Runs 4 preset queries through BOTH modes side by side:
  - Mode 1 (Classic): rule-based scorer with structured preferences
  - Mode 2 (RAG):     Gemini parses the query, scorer retrieves, Gemini explains

Usage:
    python eval.py           -- runs both modes
    python eval.py --classic -- runs classic mode only (no API key needed)
    python eval.py --rag     -- runs RAG mode only
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from src.recommender import load_equipment, recommend_equipment
from src.rag import parse_query, retrieve, generate_recommendation

SEPARATOR = "=" * 60

# Each query has a natural language form (for RAG) and the equivalent
# structured preferences (for Classic), using the same values Gemini
# extracted in the RAG run so the comparison is apples-to-apples.
QUERIES = [
    {
        "label": "Query 1 — Valid: beginner leg workout at home, low budget",
        "query": "I want to build leg strength at home and I don't have much money to spend",
        "prefs": {"muscle_group": "legs", "goal": "strength", "space": "small", "budget": "low", "skill_level": "beginner"},
    },
    {
        "label": "Query 2 — Valid: full body, large space, high budget",
        "query": "I have a large garage and a good budget, I want something versatile for full body muscle gain",
        "prefs": {"muscle_group": "full_body", "goal": "muscle_gain", "space": "large", "budget": "high", "skill_level": "beginner"},
    },
    {
        "label": "Query 3 — Edge case: vague query with no clear goal",
        "query": "just something good",
        "prefs": {"muscle_group": "", "goal": "", "space": "medium", "budget": "medium", "skill_level": "beginner"},
    },
    {
        "label": "Query 4 — Stress test: gibberish input",
        "query": "asdfjkl qwerty blah blah 123",
        "prefs": {"muscle_group": "", "goal": "", "space": "medium", "budget": "medium", "skill_level": "beginner"},
    },
]


def run_classic(items: list) -> None:
    print(f"\n{SEPARATOR}")
    print("  MODE 1 — CLASSIC RULE-BASED (no AI)")
    print(f"{SEPARATOR}")

    for test in QUERIES:
        print(f"\n  {test['label']}")
        print(f"  Structured prefs: {test['prefs']}")
        results = recommend_equipment(test["prefs"], items, k=3)
        for item, score, explanation in results:
            print(f"    → {item['equipment']} ({item['type']})  Score: {score:.2f}")
            print(f"       {explanation}")
        print()


def run_rag(items: list, api_key: str) -> None:
    print(f"\n{SEPARATOR}")
    print("  MODE 2 — RAG AI-POWERED (Google Gemini)")
    print(f"{SEPARATOR}")

    for test in QUERIES:
        print(f"\n{SEPARATOR}")
        print(f"  {test['label']}")
        print(f"  Input: \"{test['query']}\"")
        print(SEPARATOR)

        print("\nStep 1: Parsing request...")
        prefs = parse_query(test["query"], api_key)
        print(f"  Extracted: muscle_group={prefs['muscle_group'] or 'any'}, "
              f"goal={prefs['goal'] or 'any'}, space={prefs['space']}, "
              f"budget={prefs['budget']}, skill={prefs['skill_level']}")

        print("\nStep 2: Retrieving matches...")
        results = retrieve(prefs, items, k=3)
        for item, score in results:
            print(f"  → {item['equipment']} (score={score:.2f})")

        print("\nStep 3: Generating recommendation...")
        recommendation = generate_recommendation(test["query"], results, prefs, api_key)

        print("\n--- Recommendation ---")
        print(recommendation)
        print("----------------------\n")


def main() -> None:
    args = sys.argv[1:]
    items = load_equipment("data/equipments.csv")

    print(f"\n{SEPARATOR}")
    print("  GYM EQUIPMENT RECOMMENDER — EVALUATION RUN")
    print(f"{SEPARATOR}")

    run_classic_flag = "--rag" not in args
    run_rag_flag     = "--classic" not in args

    if run_classic_flag:
        run_classic(items)

    if run_rag_flag:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Error: GOOGLE_API_KEY not set in .env — skipping RAG mode.")
        else:
            run_rag(items, api_key)


if __name__ == "__main__":
    main()
