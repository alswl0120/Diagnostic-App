import pytest
from assessment.loader import load_questions, get_questions_by_domain, get_ordered_items


def test_load_math_questions_count():
    data = load_questions("math")
    assert len(data["items"]) == 20


def test_load_science_questions_count():
    data = load_questions("science")
    assert len(data["items"]) == 18


def test_all_items_have_required_fields():
    for subject in ["math", "science"]:
        for item in load_questions(subject)["items"]:
            assert "id" in item
            assert "domain" in item
            assert "stem" in item
            assert len(item["options"]) == 4
            assert 0 <= item["answer_index"] <= 3
            assert "difficulty" in item


def test_get_questions_by_domain_math():
    grouped = get_questions_by_domain("math")
    assert len(grouped) == 4
    assert "number" in grouped
    assert "algebra" in grouped
    assert "geometry_measurement" in grouped
    assert "handling_data" in grouped
    assert sum(len(v) for v in grouped.values()) == 20


def test_get_questions_by_domain_science():
    grouped = get_questions_by_domain("science")
    assert len(grouped) == 5
    assert "diversity_matter" in grouped
    assert "cycles" in grouped
    assert "systems" in grouped
    assert "forces_energy" in grouped
    assert "humans_environment" in grouped
    assert sum(len(v) for v in grouped.values()) == 18


def test_get_ordered_items_sorted_by_difficulty():
    items = get_ordered_items("math")
    domains_seen = {}
    for item in items:
        domain = item["domain"]
        if domain not in domains_seen:
            domains_seen[domain] = []
        domains_seen[domain].append(item["difficulty"])
    for domain, difficulties in domains_seen.items():
        assert difficulties == sorted(difficulties), f"Domain {domain} not sorted by difficulty"


def test_math_number_domain_has_six_items():
    grouped = get_questions_by_domain("math")
    assert len(grouped["number"]) == 6


def test_science_cycles_domain_has_four_items():
    grouped = get_questions_by_domain("science")
    assert len(grouped["cycles"]) == 4
