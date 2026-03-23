import pytest
from core.auth import get_user, is_teacher


def test_get_user_extracts_all_headers():
    headers = {
        "X-User-Id": "42",
        "X-User-Email": "jinto@enuma.com",
        "X-User-Name": "Jinto",
        "X-User-Roles": "staff,admin",
    }
    user = get_user(headers)
    assert user["user_id"] == "42"
    assert user["email"] == "jinto@enuma.com"
    assert user["name"] == "Jinto"
    assert user["roles"] == "staff,admin"


def test_get_user_missing_headers_returns_anonymous_fallback():
    user = get_user({})
    assert user["user_id"] == "anonymous"
    assert user["email"] == ""


def test_is_teacher_detects_staff():
    assert is_teacher("staff") is True
    assert is_teacher("staff,reader") is True
    assert is_teacher("admin,staff") is True


def test_is_teacher_detects_teacher_role():
    assert is_teacher("teacher") is True


def test_is_teacher_returns_false_for_student():
    assert is_teacher("") is False
    assert is_teacher("student") is False
    assert is_teacher("reader") is False


def test_is_teacher_returns_false_for_none():
    assert is_teacher(None) is False
