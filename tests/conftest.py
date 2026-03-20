import pytest
import sqlite3
from pathlib import Path
from core.database import init_db, DB_PATH


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("core.database.DB_PATH", db_file)
    init_db(db_file)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()
