import pytest
from core.database import (
    init_db, upsert_user, create_attempt, save_attempt_results,
    classify_group, get_attempts_by_name, update_group_label,
    add_sync_item, get_pending_sync_items, mark_sync_item_done,
    increment_sync_attempt,
)


def test_classify_group_foundational():
    assert classify_group(1) == "기초"
    assert classify_group(2) == "기초"


def test_classify_group_developing():
    assert classify_group(3) == "중간"


def test_classify_group_advanced():
    assert classify_group(4) == "상위"


def test_get_attempts_by_name_empty(tmp_db):
    results = get_attempts_by_name("Nobody", conn=tmp_db)
    assert results == []


def test_get_attempts_by_name_ordered(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    id1 = create_attempt("u1", "Ama", conn=tmp_db)
    id2 = create_attempt("u1", "Ama", conn=tmp_db)
    save_attempt_results(id1, {}, {}, {"number": {"score": 0.5, "level": 2, "correct": 2, "total": 4}}, {}, 2, conn=tmp_db)
    save_attempt_results(id2, {}, {}, {"number": {"score": 0.75, "level": 3, "correct": 3, "total": 4}}, {}, 3, conn=tmp_db)
    results = get_attempts_by_name("Ama", conn=tmp_db)
    assert len(results) == 2
    assert results[0]["overall_level"] == 2
    assert results[1]["overall_level"] == 3


def test_update_group_label(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Ama", conn=tmp_db)
    update_group_label(attempt_id, "기초", conn=tmp_db)
    row = tmp_db.execute("SELECT group_label FROM attempts WHERE id=?", (attempt_id,)).fetchone()
    assert row["group_label"] == "기초"


def test_sync_queue_add_and_retrieve(tmp_db):
    item_id = add_sync_item("save_attempt", {"attempt_id": 1, "student_name": "Ama"}, conn=tmp_db)
    assert item_id > 0
    pending = get_pending_sync_items(conn=tmp_db)
    assert len(pending) == 1
    assert pending[0]["operation"] == "save_attempt"


def test_sync_queue_mark_done(tmp_db):
    item_id = add_sync_item("save_attempt", {"attempt_id": 1}, conn=tmp_db)
    mark_sync_item_done(item_id, conn=tmp_db)
    pending = get_pending_sync_items(conn=tmp_db)
    assert len(pending) == 0


def test_sync_queue_increment_attempts(tmp_db):
    item_id = add_sync_item("save_attempt", {"attempt_id": 1}, conn=tmp_db)
    increment_sync_attempt(item_id, conn=tmp_db)
    row = tmp_db.execute("SELECT attempts FROM sync_queue WHERE id=?", (item_id,)).fetchone()
    assert row["attempts"] == 1


def test_attempts_has_assessment_type_column(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Ama", assessment_type="midline", conn=tmp_db)
    row = tmp_db.execute("SELECT assessment_type FROM attempts WHERE id=?", (attempt_id,)).fetchone()
    assert row["assessment_type"] == "midline"


def test_attempts_has_group_label_column(tmp_db):
    upsert_user("u1", "a@b.com", "Ama", "student", conn=tmp_db)
    attempt_id = create_attempt("u1", "Ama", conn=tmp_db)
    row = tmp_db.execute("SELECT group_label FROM attempts WHERE id=?", (attempt_id,)).fetchone()
    assert row is not None
