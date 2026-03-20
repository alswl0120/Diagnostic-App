import pytest
from assessment.session import (
    init_responses, record_response, is_section_complete,
    get_domain_and_local_index
)


def test_init_responses_creates_none_structure():
    grouped = {"number": [1, 2, 3], "algebra": [4, 5]}
    responses = init_responses("math", grouped)
    assert responses["number"] == [None, None, None]
    assert responses["algebra"] == [None, None]


def test_record_response_updates_correct_slot():
    grouped = {"number": [1, 2, 3]}
    responses = init_responses("math", grouped)
    record_response(responses, "number", 1, 2)
    assert responses["number"][1] == 2
    assert responses["number"][0] is None


def test_is_section_complete_false_when_unanswered():
    grouped = {"number": [1, 2]}
    responses = init_responses("math", grouped)
    assert is_section_complete(responses) is False


def test_is_section_complete_true_when_all_answered():
    grouped = {"number": [1, 2]}
    responses = init_responses("math", grouped)
    record_response(responses, "number", 0, 0)
    record_response(responses, "number", 1, 1)
    assert is_section_complete(responses) is True


def test_get_domain_and_local_index():
    ordered_items = [
        {"domain": "number", "id": "M-NUM-01"},
        {"domain": "number", "id": "M-NUM-02"},
        {"domain": "algebra", "id": "M-ALG-01"},
    ]
    assert get_domain_and_local_index(ordered_items, 0) == ("number", 0)
    assert get_domain_and_local_index(ordered_items, 1) == ("number", 1)
    assert get_domain_and_local_index(ordered_items, 2) == ("algebra", 0)
