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
            overall_level INTEGER
        );

        CREATE TABLE IF NOT EXISTS domain_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL REFERENCES attempts(id),
            subject TEXT NOT NULL,
            domain_key TEXT NOT NULL,
            score REAL NOT NULL,
            level INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_domain_scores_attempt ON domain_scores(attempt_id);
        CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user_id);
    """)
    conn.commit()
    conn.close()


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


def create_attempt(user_id: str, student_name: str, conn=None) -> int:
    close = conn is None
    if close:
        conn = get_connection()
    cur = conn.execute(
        "INSERT INTO attempts (user_id, student_name) VALUES (?, ?)",
        (user_id, student_name)
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
    conn.execute(
        "UPDATE attempts SET math_raw=?, science_raw=?, math_scores=?, science_scores=?, "
        "overall_level=?, completed_at=datetime('now') WHERE id=?",
        (json.dumps(math_raw), json.dumps(science_raw),
         json.dumps(math_scores), json.dumps(science_scores),
         overall_level, attempt_id)
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
