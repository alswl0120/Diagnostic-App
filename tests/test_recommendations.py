import pytest
from recommendations.activities import ACTIVITIES, get_recommendations, get_priority_gaps

MATH_DOMAINS = ["number", "algebra", "geometry_measurement", "handling_data"]
SCIENCE_DOMAINS = ["diversity_matter", "cycles", "systems", "forces_energy", "humans_environment"]
ALL_DOMAINS = MATH_DOMAINS + SCIENCE_DOMAINS


def test_all_domains_present():
    for domain in ALL_DOMAINS:
        assert domain in ACTIVITIES, f"Domain '{domain}' missing from ACTIVITIES"


def test_all_domains_have_four_levels():
    for domain in ALL_DOMAINS:
        for level in [1, 2, 3, 4]:
            assert level in ACTIVITIES[domain], f"Level {level} missing for domain '{domain}'"


def test_activity_texts_are_non_empty():
    for domain in ALL_DOMAINS:
        for level in [1, 2, 3, 4]:
            text = ACTIVITIES[domain][level]
            assert isinstance(text, str) and len(text) > 20


def test_get_recommendations_returns_all_domains():
    scores = {d: {"score": 0.5, "level": 2, "correct": 2, "total": 4} for d in ALL_DOMAINS}
    recs = get_recommendations(scores)
    for domain in ALL_DOMAINS:
        assert domain in recs


def test_get_recommendations_matches_level():
    scores = {"number": {"score": 0.2, "level": 1, "correct": 1, "total": 4}}
    recs = get_recommendations(scores)
    assert recs["number"] == ACTIVITIES["number"][1]


def test_get_priority_gaps_returns_level_1_and_2():
    scores = {
        "number": {"score": 0.2, "level": 1, "correct": 1, "total": 4},
        "algebra": {"score": 0.5, "level": 2, "correct": 2, "total": 4},
        "systems": {"score": 0.9, "level": 4, "correct": 4, "total": 4},
    }
    gaps = get_priority_gaps(scores)
    assert "number" in gaps
    assert "algebra" in gaps
    assert "systems" not in gaps


def test_get_priority_gaps_sorted_by_score():
    scores = {
        "number": {"score": 0.3, "level": 1, "correct": 1, "total": 4},
        "algebra": {"score": 0.1, "level": 1, "correct": 0, "total": 4},
    }
    gaps = get_priority_gaps(scores)
    assert gaps[0] == "algebra"
    assert gaps[1] == "number"


def test_get_priority_gaps_empty_when_all_proficient():
    scores = {d: {"score": 0.9, "level": 4, "correct": 4, "total": 4} for d in ALL_DOMAINS}
    assert get_priority_gaps(scores) == []
