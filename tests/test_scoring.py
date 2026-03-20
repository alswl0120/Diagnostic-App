import pytest
from core.scoring import classify_level, score_domain, score_section, compute_overall_level


def test_classify_level_boundaries():
    assert classify_level(0.0) == 1
    assert classify_level(0.40) == 1
    assert classify_level(0.41) == 2
    assert classify_level(0.60) == 2
    assert classify_level(0.61) == 3
    assert classify_level(0.80) == 3
    assert classify_level(0.81) == 4
    assert classify_level(1.0) == 4


def test_classify_level_midpoints():
    assert classify_level(0.2) == 1
    assert classify_level(0.5) == 2
    assert classify_level(0.7) == 3
    assert classify_level(0.9) == 4


def test_score_domain_all_correct():
    result = score_domain([0, 1, 2, 3], [0, 1, 2, 3])
    assert result["score"] == 1.0
    assert result["level"] == 4
    assert result["correct"] == 4
    assert result["total"] == 4


def test_score_domain_all_wrong():
    result = score_domain([1, 0, 0, 0], [0, 1, 2, 3])
    assert result["score"] == 0.0
    assert result["level"] == 1
    assert result["correct"] == 0


def test_score_domain_partial():
    result = score_domain([0, 1, 0, 0], [0, 1, 2, 3])
    assert result["correct"] == 2
    assert result["total"] == 4
    assert result["score"] == pytest.approx(0.5)
    assert result["level"] == 2


def test_score_domain_skipped_counts_as_wrong():
    result = score_domain([None, None, 0, 0], [0, 0, 0, 0])
    assert result["correct"] == 2
    assert result["total"] == 4
    assert result["score"] == pytest.approx(0.5)


def test_score_domain_all_skipped():
    result = score_domain([None, None, None], [0, 1, 2])
    assert result["correct"] == 0
    assert result["score"] == 0.0
    assert result["level"] == 1


def test_score_domain_six_items():
    result = score_domain([0, 1, 2, 3, 0, 1], [0, 1, 2, 3, 0, 1])
    assert result["correct"] == 6
    assert result["score"] == 1.0


def test_score_section_returns_all_domains():
    questions_by_domain = {
        "number": [
            {"answer_index": 0}, {"answer_index": 1}, {"answer_index": 2}, {"answer_index": 3},
        ],
        "algebra": [
            {"answer_index": 0}, {"answer_index": 0}, {"answer_index": 0},
        ],
    }
    responses = {
        "number": [0, 1, 2, 3],
        "algebra": [0, 1, 0],
    }
    result = score_section(responses, questions_by_domain)
    assert "number" in result
    assert "algebra" in result
    assert result["number"]["score"] == 1.0
    assert result["algebra"]["correct"] == 2


def test_score_section_missing_domain_responses():
    questions_by_domain = {
        "number": [{"answer_index": 0}, {"answer_index": 1}],
    }
    responses = {}
    result = score_section(responses, questions_by_domain)
    assert result["number"]["correct"] == 0


def test_compute_overall_level_all_low():
    scores = {k: {"score": 0.2, "level": 1, "correct": 1, "total": 4}
              for k in ["a", "b", "c"]}
    assert compute_overall_level(scores) == 1


def test_compute_overall_level_all_high():
    scores = {k: {"score": 0.9, "level": 4, "correct": 4, "total": 4}
              for k in ["a", "b", "c", "d"]}
    assert compute_overall_level(scores) == 4


def test_compute_overall_level_mixed():
    scores = {
        "a": {"score": 0.2, "level": 1, "correct": 1, "total": 4},
        "b": {"score": 0.9, "level": 4, "correct": 4, "total": 4},
    }
    overall = compute_overall_level(scores)
    assert overall == classify_level((0.2 + 0.9) / 2)


def test_compute_overall_level_nine_domains():
    scores = {f"d{i}": {"score": 0.5, "level": 2, "correct": 2, "total": 4}
              for i in range(9)}
    assert compute_overall_level(scores) == 2
