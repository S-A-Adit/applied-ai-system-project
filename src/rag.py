import json
import re
import time
from typing import List, Dict, Tuple
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from src.guardrails import validate_prefs, validate_output

MODEL = "gemini-2.5-flash"


def _gemini(prompt: str, api_key: str, retries: int = 3) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL)
    for attempt in range(retries):
        try:
            return model.generate_content(prompt).text
        except ResourceExhausted as e:
            if attempt < retries - 1:
                wait = 10 * (attempt + 1)
                print(f"  [Rate limit] Quota hit, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"Gemini API quota exhausted after {retries} attempts. "
                    "Try again later or upgrade your API plan."
                ) from e


def equipment_to_text(item) -> str:
    """Build a plain-English description of an equipment item for context."""
    d = item.__dict__ if hasattr(item, "__dict__") else item
    name = d.get("equipment") or d.get("name", "Unknown")
    return (
        f"Equipment: {name} | Type: {d.get('type')} | "
        f"Targets: {d.get('muscle_group')} | Goal: {d.get('goal')} | "
        f"Space needed: {d.get('space')} | Price: {d.get('price_level')} | "
        f"Skill level: {d.get('skill_level')} | Versatility: {d.get('versatility')} | "
        f"Notes: {d.get('notes')}"
    )


def parse_query(query: str, api_key: str) -> Dict:
    """Step 1 — Use Gemini to extract structured equipment preferences from a natural language request."""
    prompt = f"""Extract gym equipment preferences from this request: "{query}"

Return ONLY a JSON object (no markdown, no explanation) with these fields:
{{
  "muscle_group": one of [full_body, legs, chest, back, core, upper_body, recovery] or null,
  "goal": one of [muscle_gain, fat_loss, strength, toning, conditioning, recovery] or null,
  "space": one of [small, medium, large] or null,
  "budget": one of [low, medium, high] or null,
  "skill_level": one of [beginner, intermediate] or null
}}"""

    raw = _gemini(prompt, api_key)
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        prefs = json.loads(cleaned)
    except json.JSONDecodeError:
        prefs = {}

    raw_prefs = {
        "muscle_group": prefs.get("muscle_group") or "",
        "goal": prefs.get("goal") or "",
        "space": prefs.get("space") or "medium",
        "budget": prefs.get("budget") or "medium",
        "skill_level": prefs.get("skill_level") or "beginner",
    }
    cleaned, warnings = validate_prefs(raw_prefs)
    for w in warnings:
        print(f"  {w}")
    return cleaned


def retrieve(user_prefs: Dict, items: List[Dict], k: int = 3) -> List[Tuple[Dict, float]]:
    """Step 2 — Score every equipment item and return the top-k."""
    from src.recommender import score_equipment
    scored = [(item, score_equipment(user_prefs, item)) for item in items]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


def generate_recommendation(query: str, results: List[Tuple[Dict, float]], user_prefs: Dict, api_key: str) -> str:
    """Step 3 — Pass the top equipment to Gemini and ask it to explain the recommendation."""
    item_lines = "\n".join(
        f"{i+1}. {equipment_to_text(item)} (score={score:.2f})"
        for i, (item, score) in enumerate(results)
    )
    prompt = f"""You are a helpful gym equipment recommendation assistant.

User request: "{query}"
Extracted preferences: muscle_group={user_prefs['muscle_group'] or 'any'}, goal={user_prefs['goal'] or 'any'}, space={user_prefs['space']}, budget={user_prefs['budget']}, skill_level={user_prefs['skill_level']}

Top matched equipment from the catalog:
{item_lines}

Recommend the best equipment for this user. For each pick, write 1–2 sentences explaining why it fits their request. Be conversational and specific."""

    raw_output = _gemini(prompt, api_key)
    final_output, warnings = validate_output(raw_output, results)
    for w in warnings:
        print(f"  {w}")
    return final_output
