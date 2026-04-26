from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

SPACE_ORDER = {"small": 1, "medium": 2, "large": 3}
PRICE_ORDER = {"low": 1, "medium": 2, "high": 3}
SKILL_ORDER = {"beginner": 1, "intermediate": 2}


@dataclass
class Equipment:
    id: int
    name: str
    type: str
    muscle_group: str
    goal: str
    space: str
    price_level: str
    skill_level: str
    versatility: str
    notes: str


@dataclass
class UserProfile:
    target_muscle: str    # e.g. "full_body", "legs", "chest"
    fitness_goal: str     # e.g. "muscle_gain", "fat_loss", "strength"
    available_space: str  # "small", "medium", "large"
    budget: str           # "low", "medium", "high"
    skill_level: str      # "beginner", "intermediate"


class Recommender:
    def __init__(self, equipment: List[Equipment]):
        self.equipment = equipment

    def recommend(self, user: UserProfile, k: int = 5) -> List[Equipment]:
        user_dict = {
            "muscle_group": user.target_muscle,
            "goal": user.fitness_goal,
            "space": user.available_space,
            "budget": user.budget,
            "skill_level": user.skill_level,
        }
        scored = []
        for item in self.equipment:
            item_dict = {
                "muscle_group": item.muscle_group,
                "goal": item.goal,
                "space": item.space,
                "price_level": item.price_level,
                "skill_level": item.skill_level,
            }
            scored.append((item, score_equipment(user_dict, item_dict)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, item: Equipment) -> str:
        parts = []
        if item.muscle_group == user.target_muscle:
            parts.append(f"targets {item.muscle_group}")
        if item.goal == user.fitness_goal:
            parts.append(f"matches goal={item.goal}")
        if SPACE_ORDER.get(user.available_space, 0) >= SPACE_ORDER.get(item.space, 0):
            parts.append(f"fits your {user.available_space} space")
        if PRICE_ORDER.get(user.budget, 0) >= PRICE_ORDER.get(item.price_level, 0):
            parts.append(f"within {user.budget} budget")
        if SKILL_ORDER.get(user.skill_level, 0) >= SKILL_ORDER.get(item.skill_level, 0):
            parts.append(f"suitable for {user.skill_level} level")
        return "; ".join(parts) if parts else "partial match"


def load_equipment(csv_path: str) -> List[Dict]:
    """Read equipments.csv and return a list of dicts."""
    import csv
    items = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            items.append(row)
    print(f"Loaded equipment: {len(items)}")
    return items


def score_equipment(user_prefs: Dict, item: Dict) -> float:
    """Score one equipment item 0–6.0.
    +2.0 muscle_group match, +1.5 goal match, +1.0 space fit,
    +1.0 budget fit, +0.5 skill fit. Max = 6.0.
    """
    score = 0.0

    if item.get("muscle_group") == user_prefs.get("muscle_group"):
        score += 2.0

    if item.get("goal") == user_prefs.get("goal"):
        score += 1.5

    if user_prefs.get("space") and item.get("space"):
        if SPACE_ORDER.get(user_prefs["space"], 0) >= SPACE_ORDER.get(item["space"], 0):
            score += 1.0

    if user_prefs.get("budget") and item.get("price_level"):
        if PRICE_ORDER.get(user_prefs["budget"], 0) >= PRICE_ORDER.get(item["price_level"], 0):
            score += 1.0

    if user_prefs.get("skill_level") and item.get("skill_level"):
        if SKILL_ORDER.get(user_prefs["skill_level"], 0) >= SKILL_ORDER.get(item["skill_level"], 0):
            score += 0.5

    return score


def recommend_equipment(user_prefs: Dict, items: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every item, sort descending, return top-k as (item, score, explanation) tuples."""
    scored = []
    for item in items:
        s = score_equipment(user_prefs, item)
        matches = []
        if item.get("muscle_group") == user_prefs.get("muscle_group"):
            matches.append(f"muscle_group={item['muscle_group']}")
        if item.get("goal") == user_prefs.get("goal"):
            matches.append(f"goal={item['goal']}")
        if SPACE_ORDER.get(user_prefs.get("space", ""), 0) >= SPACE_ORDER.get(item.get("space", ""), 0):
            matches.append(f"fits space={item['space']}")
        if PRICE_ORDER.get(user_prefs.get("budget", ""), 0) >= PRICE_ORDER.get(item.get("price_level", ""), 0):
            matches.append(f"within budget={item['price_level']}")
        explanation = "Matches: " + ", ".join(matches) if matches else "Partial match"
        scored.append((item, s, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
