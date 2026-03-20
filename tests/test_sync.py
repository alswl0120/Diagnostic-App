import pytest
from unittest.mock import patch, MagicMock
from core.sync import check_connectivity, sync_pending_items


def test_check_connectivity_returns_false_on_error():
    with patch("urllib.request.urlopen", side_effect=Exception("no network")):
        assert check_connectivity("http://example.com") is False


def test_check_connectivity_returns_true_on_success():
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert check_connectivity("http://example.com") is True


def test_sync_pending_no_items(tmp_db):
    result = sync_pending_items("http://example.com", conn=tmp_db)
    assert result["synced"] == 0
    assert result["failed"] == 0


def test_sync_pending_marks_done_on_success(tmp_db):
    from core.database import add_sync_item, get_pending_sync_items
    add_sync_item("save_attempt", {"attempt_id": 1}, conn=tmp_db)

    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = sync_pending_items("http://example.com/sync", conn=tmp_db)

    assert result["synced"] == 1
    assert len(get_pending_sync_items(conn=tmp_db)) == 0


def test_sync_pending_increments_on_failure(tmp_db):
    from core.database import add_sync_item
    item_id = add_sync_item("save_attempt", {"attempt_id": 1}, conn=tmp_db)

    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        result = sync_pending_items("http://example.com/sync", conn=tmp_db)

    assert result["failed"] == 1
    row = tmp_db.execute("SELECT attempts FROM sync_queue WHERE id=?", (item_id,)).fetchone()
    assert row["attempts"] == 1
