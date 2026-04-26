from src.recommender import Equipment, UserProfile, Recommender


def make_small_recommender() -> Recommender:
    items = [
        Equipment(
            id=1,
            name="Dumbbells",
            type="free_weight",
            muscle_group="full_body",
            goal="muscle_gain",
            space="small",
            price_level="medium",
            skill_level="beginner",
            versatility="high",
            notes="core strength training staple",
        ),
        Equipment(
            id=2,
            name="Treadmill",
            type="cardio",
            muscle_group="legs",
            goal="fat_loss",
            space="large",
            price_level="high",
            skill_level="beginner",
            versatility="medium",
            notes="cardio endurance training",
        ),
    ]
    return Recommender(items)


def test_recommend_returns_equipment_sorted_by_score():
    user = UserProfile(
        target_muscle="full_body",
        fitness_goal="muscle_gain",
        available_space="medium",
        budget="medium",
        skill_level="beginner",
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Dumbbells (full_body, muscle_gain, small space, medium price) should score higher
    assert results[0].muscle_group == "full_body"
    assert results[0].goal == "muscle_gain"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        target_muscle="full_body",
        fitness_goal="muscle_gain",
        available_space="medium",
        budget="medium",
        skill_level="beginner",
    )
    rec = make_small_recommender()
    item = rec.equipment[0]

    explanation = rec.explain_recommendation(user, item)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
