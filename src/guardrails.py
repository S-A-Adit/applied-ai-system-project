"""
Guardrails for the Gym Equipment Recommender RAG pipeline.

Two layers:
  1. Input guardrail  — validates parse_query output against known vocabulary
                        before it reaches the scorer.
  2. Output guardrail — checks that the generated recommendation is non-empty,
                        long enough to be meaningful, and references at least one
                        retrieved equipment item (prevents hallucination).
"""

from typing import Dict, List, Tuple

VALID_MUSCLE_GROUPS = {"full_body", "legs", "chest", "back", "core", "upper_body", "recovery"}
VALID_GOALS        = {"muscle_gain", "fat_loss", "strength", "toning", "conditioning", "recovery"}
VALID_SPACES       = {"small", "medium", "large"}
VALID_BUDGETS      = {"low", "medium", "high"}
VALID_SKILLS       = {"beginner", "intermediate"}

FIELD_DEFAULTS = {
    "muscle_group": "",
    "goal": "",
    "space": "medium",
    "budget": "medium",
    "skill_level": "beginner",
}


def validate_prefs(prefs: Dict) -> Tuple[Dict, List[str]]:
    """
    Validate LLM-extracted preferences against known vocabulary.

    Returns a cleaned copy of prefs and a list of warning strings.
    Unknown values are replaced with the field default so the scorer
    still receives a valid dict.
    """
    cleaned = {}
    warnings = []

    checks = [
        ("muscle_group", VALID_MUSCLE_GROUPS),
        ("goal",         VALID_GOALS),
        ("space",        VALID_SPACES),
        ("budget",       VALID_BUDGETS),
        ("skill_level",  VALID_SKILLS),
    ]

    for field, valid_set in checks:
        value = prefs.get(field, "")
        if value and value not in valid_set:
            warnings.append(
                f"[INPUT GUARDRAIL] '{value}' is not a recognized {field}. "
                f"Valid options: {sorted(valid_set)}. Resetting to default."
            )
            cleaned[field] = FIELD_DEFAULTS[field]
        else:
            cleaned[field] = value

    if not cleaned["muscle_group"] and not cleaned["goal"]:
        warnings.append(
            "[INPUT GUARDRAIL] Neither muscle_group nor goal could be extracted. "
            "Results may be ranked by space/budget/skill only and could be low quality."
        )

    return cleaned, warnings


def validate_output(recommendation: str, results: List[Tuple[Dict, float]]) -> Tuple[str, List[str]]:
    """
    Validate the LLM-generated recommendation.

    Checks:
      - Non-empty response
      - Minimum meaningful length (> 60 characters)
      - At least one retrieved equipment name appears in the response

    Returns the original recommendation (or a fallback string) and a list of warnings.
    """
    warnings = []

    if not recommendation or not recommendation.strip():
        warnings.append("[OUTPUT GUARDRAIL] Gemini returned an empty response. Using fallback.")
        fallback = _build_fallback(results)
        return fallback, warnings

    if len(recommendation.strip()) < 60:
        warnings.append(
            f"[OUTPUT GUARDRAIL] Response is suspiciously short ({len(recommendation.strip())} chars). "
            "May not be meaningful."
        )

    retrieved_names = [
        (item.get("equipment") or item.get("name", "")).lower()
        for item, _ in results
    ]
    mentioned = any(name in recommendation.lower() for name in retrieved_names if name)

    if not mentioned:
        warnings.append(
            "[OUTPUT GUARDRAIL] Response does not mention any retrieved equipment. "
            "Possible hallucination — verify output manually."
        )

    return recommendation, warnings


def _build_fallback(results: List[Tuple[Dict, float]]) -> str:
    """Generate a plain fallback recommendation when Gemini fails."""
    if not results:
        return "No equipment matched your query. Try broadening your preferences."
    lines = ["Here are the top matches based on your preferences:\n"]
    for i, (item, score) in enumerate(results, 1):
        name = item.get("equipment") or item.get("name", "Unknown")
        lines.append(f"  {i}. {name} — score {score:.2f} ({item.get('notes', '')})")
    return "\n".join(lines)
