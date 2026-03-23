import json
import sqlite3
from pathlib import Path

DB_PATH = Path("/app/storage/data.db")


def get_connection(db_path: Path = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(attempts)").fetchall()}
    if "assessment_type" not in existing:
        conn.execute("ALTER TABLE attempts ADD COLUMN assessment_type TEXT DEFAULT 'baseline'")
    if "group_label" not in existing:
        conn.execute("ALTER TABLE attempts ADD COLUMN group_label TEXT")
    if "synced" not in existing:
        conn.execute("ALTER TABLE attempts ADD COLUMN synced INTEGER DEFAULT 0")
    if "progress_math_idx" not in existing:
        conn.execute("ALTER TABLE attempts ADD COLUMN progress_math_idx INTEGER DEFAULT 0")
    if "progress_sci_idx" not in existing:
        conn.execute("ALTER TABLE attempts ADD COLUMN progress_sci_idx INTEGER DEFAULT 0")
    conn.commit()


def init_db(db_path: Path = None) -> None:
    conn = get_connection(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL REFERENCES users(user_id),
            student_name TEXT NOT NULL,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            completed_at TEXT,
            math_raw TEXT,
            science_raw TEXT,
            math_scores TEXT,
            science_scores TEXT,
            overall_level INTEGER,
            assessment_type TEXT DEFAULT 'baseline',
            group_label TEXT,
            synced INTEGER DEFAULT 0,
            progress_math_idx INTEGER DEFAULT 0,
            progress_sci_idx INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS domain_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL REFERENCES attempts(id),
            subject TEXT NOT NULL,
            domain_key TEXT NOT NULL,
            score REAL NOT NULL,
            level INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            attempts INTEGER NOT NULL DEFAULT 0,
            last_attempt TEXT,
            done INTEGER NOT NULL DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_domain_scores_attempt ON domain_scores(attempt_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_name ON attempts(student_name);
        CREATE INDEX IF NOT EXISTS idx_sync_queue_done ON sync_queue(done);
    """)
    _migrate(conn)
    conn.commit()
    conn.close()


def classify_group(level: int) -> str:
    if level <= 2:
        return "기초"
    if level == 3:
        return "중간"
    return "상위"


def upsert_user(user_id: str, email: str, name: str, role: str, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    conn.execute(
        "INSERT INTO users (user_id, email, name, role) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET email=excluded.email, name=excluded.name, role=excluded.role",
        (user_id, email, name, role)
    )
    conn.commit()
    if close:
        conn.close()


def create_attempt(user_id: str, student_name: str, assessment_type: str = "baseline", conn=None) -> int:
    close = conn is None
    if close:
        conn = get_connection()
    cur = conn.execute(
        "INSERT INTO attempts (user_id, student_name, assessment_type) VALUES (?, ?, ?)",
        (user_id, student_name, assessment_type)
    )
    conn.commit()
    attempt_id = cur.lastrowid
    if close:
        conn.close()
    return attempt_id


def save_attempt_results(attempt_id: int, math_raw: dict, science_raw: dict,
                          math_scores: dict, science_scores: dict,
                          overall_level: int, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    group_label = classify_group(overall_level)
    conn.execute(
        "UPDATE attempts SET math_raw=?, science_raw=?, math_scores=?, science_scores=?, "
        "overall_level=?, group_label=?, completed_at=datetime('now') WHERE id=?",
        (json.dumps(math_raw), json.dumps(science_raw),
         json.dumps(math_scores), json.dumps(science_scores),
         overall_level, group_label, attempt_id)
    )
    conn.commit()
    if close:
        conn.close()


def save_domain_scores(attempt_id: int, scores_by_subject: dict, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    for subject, domain_scores in scores_by_subject.items():
        for domain_key, ds in domain_scores.items():
            conn.execute(
                "INSERT INTO domain_scores (attempt_id, subject, domain_key, score, level) VALUES (?, ?, ?, ?, ?)",
                (attempt_id, subject, domain_key, ds["score"], ds["level"])
            )
    conn.commit()
    if close:
        conn.close()


def save_progress_checkpoint(attempt_id: int, math_raw: dict, science_raw: dict,
                              math_idx: int, sci_idx: int, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    conn.execute(
        "UPDATE attempts SET math_raw=?, science_raw=?, progress_math_idx=?, progress_sci_idx=? WHERE id=?",
        (json.dumps(math_raw), json.dumps(science_raw), math_idx, sci_idx, attempt_id)
    )
    conn.commit()
    if close:
        conn.close()


def get_latest_incomplete_attempt(student_name: str, conn=None):
    close = conn is None
    if close:
        conn = get_connection()
    row = conn.execute(
        "SELECT * FROM attempts WHERE student_name=? AND completed_at IS NULL "
        "AND progress_math_idx > 0 ORDER BY started_at DESC LIMIT 1",
        (student_name,)
    ).fetchone()
    if close:
        conn.close()
    return dict(row) if row else None


def update_group_label(attempt_id: int, group_label: str, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    conn.execute("UPDATE attempts SET group_label=? WHERE id=?", (group_label, attempt_id))
    conn.commit()
    if close:
        conn.close()


def get_attempts_by_name(student_name: str, conn=None) -> list:
    close = conn is None
    if close:
        conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM attempts WHERE student_name=? AND completed_at IS NOT NULL ORDER BY started_at ASC",
        (student_name,)
    ).fetchall()
    if close:
        conn.close()
    return [dict(r) for r in rows]


def count_attempts_by_name(student_name: str, conn=None) -> int:
    close = conn is None
    if close:
        conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM attempts WHERE student_name=? AND completed_at IS NOT NULL",
        (student_name,)
    ).fetchone()[0]
    if close:
        conn.close()
    return count


def get_attempts_for_user(user_id: str, conn=None) -> list:
    close = conn is None
    if close:
        conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM attempts WHERE user_id=? ORDER BY started_at DESC",
        (user_id,)
    ).fetchall()
    if close:
        conn.close()
    return [dict(r) for r in rows]


def get_all_attempts(conn=None) -> list:
    close = conn is None
    if close:
        conn = get_connection()
    rows = conn.execute(
        "SELECT a.*, u.email FROM attempts a JOIN users u ON a.user_id=u.user_id "
        "WHERE a.completed_at IS NOT NULL ORDER BY a.completed_at DESC"
    ).fetchall()
    if close:
        conn.close()
    return [dict(r) for r in rows]


def get_class_domain_averages(conn=None) -> list:
    close = conn is None
    if close:
        conn = get_connection()
    rows = conn.execute(
        "SELECT subject, domain_key, AVG(score) as avg_score, COUNT(*) as student_count "
        "FROM domain_scores GROUP BY subject, domain_key ORDER BY subject, domain_key"
    ).fetchall()
    if close:
        conn.close()
    return [dict(r) for r in rows]


def add_sync_item(operation: str, payload: dict, conn=None) -> int:
    close = conn is None
    if close:
        conn = get_connection()
    cur = conn.execute(
        "INSERT INTO sync_queue (operation, payload) VALUES (?, ?)",
        (operation, json.dumps(payload))
    )
    conn.commit()
    item_id = cur.lastrowid
    if close:
        conn.close()
    return item_id


def get_pending_sync_items(conn=None) -> list:
    close = conn is None
    if close:
        conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sync_queue WHERE done=0 ORDER BY created_at ASC"
    ).fetchall()
    if close:
        conn.close()
    return [dict(r) for r in rows]


def mark_sync_item_done(item_id: int, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    conn.execute("UPDATE sync_queue SET done=1 WHERE id=?", (item_id,))
    conn.commit()
    if close:
        conn.close()


def increment_sync_attempt(item_id: int, conn=None) -> None:
    close = conn is None
    if close:
        conn = get_connection()
    conn.execute(
        "UPDATE sync_queue SET attempts=attempts+1, last_attempt=datetime('now') WHERE id=?",
        (item_id,)
    )
    conn.commit()
    if close:
        conn.close()
