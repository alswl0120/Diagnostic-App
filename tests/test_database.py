import pytest
from core.database import init_db, upsert_user, create_attempt, save_attempt_results, save_domain_scores, get_attempts_for_user, get_all_attempts, get_class_domain_averages


def get_table_names(conn):
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {r["name"] for r in rows}


def test_init_db_creates_tables(tmp_db):
    tables = get_table_names(tmp_db)
    assert "users" in tables
    assert "attempts" in tables
    assert "domain_scores" in tables


def test_upsert_user_creates_user(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    row = tmp_db.execute("SELECT * FROM users WHERE user_id='u1'").fetchone()
    assert row is not None
    assert row["email"] == "a@b.com"
    assert row["name"] == "Alice"


def test_upsert_user_updates_on_conflict(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    upsert_user("u1", "new@b.com", "Alice2", "staff", conn=tmp_db)
    rows = tmp_db.execute("SELECT * FROM users WHERE user_id='u1'").fetchall()
    assert len(rows) == 1
    assert rows[0]["email"] == "new@b.com"


def test_create_attempt_returns_id(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Alice", conn=tmp_db)
    assert isinstance(attempt_id, int)
    assert attempt_id > 0


def test_save_attempt_results(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Alice", conn=tmp_db)
    math_scores = {"number": {"score": 0.75, "level": 3, "correct": 3, "total": 4}}
    science_scores = {"cycles": {"score": 0.5, "level": 2, "correct": 2, "total": 4}}
    save_attempt_results(attempt_id, {}, {}, math_scores, science_scores, 2, conn=tmp_db)
    row = tmp_db.execute("SELECT * FROM attempts WHERE id=?", (attempt_id,)).fetchone()
    assert row["overall_level"] == 2
    assert row["completed_at"] is not None


def test_save_domain_scores(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Alice", conn=tmp_db)
    scores = {"math": {"number": {"score": 0.75, "level": 3, "correct": 3, "total": 4}}}
    save_domain_scores(attempt_id, scores, conn=tmp_db)
    rows = tmp_db.execute("SELECT * FROM domain_scores WHERE attempt_id=?", (attempt_id,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["domain_key"] == "number"
    assert rows[0]["score"] == pytest.approx(0.75)


def test_get_attempts_for_user_filters(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    upsert_user("u2", "b@b.com", "Bob", "student", conn=tmp_db)
    create_attempt("u1", "Alice", conn=tmp_db)
    create_attempt("u2", "Bob", conn=tmp_db)
    results = get_attempts_for_user("u1", conn=tmp_db)
    assert len(results) == 1
    assert results[0]["student_name"] == "Alice"


def test_get_all_attempts_returns_completed_only(tmp_db):
    upsert_user("u1", "a@b.com", "Alice", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Alice", conn=tmp_db)
    assert len(get_all_attempts(conn=tmp_db)) == 0
    save_attempt_results(attempt_id, {}, {}, {}, {}, 2, conn=tmp_db)
    assert len(get_all_attempts(conn=tmp_db)) == 1


def test_get_class_domain_averages_empty(tmp_db):
    result = get_class_domain_averages(conn=tmp_db)
    assert result == []
