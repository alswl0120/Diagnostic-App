import json
import pytest
from core.database import (
    init_db, upsert_user, create_attempt, save_attempt_results,
    save_progress_checkpoint, get_latest_incomplete_attempt,
)


def test_save_progress_checkpoint_stores_data(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    aid = create_attempt("u1", "Ama", conn=tmp_db)
    save_progress_checkpoint(aid, {"number": [0, 1]}, {}, 2, 0, conn=tmp_db)
    row = tmp_db.execute(
        "SELECT progress_math_idx, progress_sci_idx, math_raw FROM attempts WHERE id=?", (aid,)
    ).fetchone()
    assert row["progress_math_idx"] == 2
    assert row["progress_sci_idx"] == 0
    assert json.loads(row["math_raw"])["number"] == [0, 1]


def test_save_progress_checkpoint_updates(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    aid = create_attempt("u1", "Ama", conn=tmp_db)
    save_progress_checkpoint(aid, {"number": [0]}, {}, 1, 0, conn=tmp_db)
    save_progress_checkpoint(aid, {"number": [0, 2]}, {}, 2, 0, conn=tmp_db)
    row = tmp_db.execute(
        "SELECT progress_math_idx FROM attempts WHERE id=?", (aid,)
    ).fetchone()
    assert row["progress_math_idx"] == 2


def test_get_latest_incomplete_attempt_none(tmp_db):
    result = get_latest_incomplete_attempt("Nobody", conn=tmp_db)
    assert result is None


def test_get_latest_incomplete_attempt_found(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    aid = create_attempt("u1", "Ama", conn=tmp_db)
    save_progress_checkpoint(aid, {"number": [0]}, {}, 1, 0, conn=tmp_db)
    result = get_latest_incomplete_attempt("Ama", conn=tmp_db)
    assert result is not None
    assert result["id"] == aid
    assert result["progress_math_idx"] == 1


def test_completed_attempt_not_returned_as_incomplete(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    aid = create_attempt("u1", "Ama", conn=tmp_db)
    save_attempt_results(aid, {}, {}, {}, {}, 2, conn=tmp_db)
    result = get_latest_incomplete_attempt("Ama", conn=tmp_db)
    assert result is None


def test_incomplete_attempt_with_no_checkpoint_not_returned(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    create_attempt("u1", "Ama", conn=tmp_db)
    result = get_latest_incomplete_attempt("Ama", conn=tmp_db)
    assert result is None
