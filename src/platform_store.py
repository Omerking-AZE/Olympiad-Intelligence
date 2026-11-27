"""SQLite persistence for local Olympiad Intelligence accounts and MathNet data."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("OI_DATA_DIR", ROOT / "data")).resolve()
DB_PATH = Path(os.getenv("OI_DB_PATH", DATA_DIR / "olympiad_intelligence.sqlite3")).resolve()
IMAGE_DIR = DATA_DIR / "mathnet_images"

SKILL_KEYS = (
    "algebra",
    "geometry",
    "number_theory",
    "discrete_mathematics",
    "proof",
    "reasoning",
    "calculation",
    "case_analysis",
)


def connect() -> sqlite3.Connection:
    """Open a configured database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def init_db() -> None:
    """Create tables and indexes. Safe to call at every server startup."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                display_name TEXT NOT NULL,
                password_salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS skill_ratings (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                skill_key TEXT NOT NULL,
                rating REAL NOT NULL DEFAULT 55,
                attempts INTEGER NOT NULL DEFAULT 0,
                solved INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, skill_key)
            );

            CREATE TABLE IF NOT EXISTS problems (
                problem_id TEXT PRIMARY KEY,
                dataset_id TEXT,
                title TEXT NOT NULL,
                country TEXT,
                competition TEXT,
                language TEXT,
                domain TEXT,
                problem_type TEXT,
                problem_text_original TEXT,
                problem_text_en TEXT,
                solution_text_original TEXT,
                solution_text_en TEXT,
                final_answer TEXT,
                source_booklet TEXT,
                booklet_source TEXT,
                topics_json TEXT NOT NULL DEFAULT '[]',
                images_json TEXT NOT NULL DEFAULT '[]',
                difficulty_score REAL NOT NULL DEFAULT 50,
                translation_status TEXT NOT NULL DEFAULT 'pending',
                imported_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                problem_id TEXT NOT NULL REFERENCES problems(problem_id) ON DELETE CASCADE,
                result TEXT NOT NULL CHECK (result IN ('solved', 'attempted')),
                skill_key TEXT NOT NULL,
                rating_after REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_problems_domain ON problems(domain);
            CREATE INDEX IF NOT EXISTS idx_problems_language ON problems(language);
            CREATE INDEX IF NOT EXISTS idx_problems_competition ON problems(competition);
            CREATE INDEX IF NOT EXISTS idx_attempts_user_created ON attempts(user_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_attempts_user_problem ON attempts(user_id, problem_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_attempts_user_problem_unique ON attempts(user_id, problem_id);
            """
        )


def ensure_session_secret() -> bytes:
    """Keep the local cookie-signing key out of source control."""
    secret_dir = DATA_DIR / "security"
    secret_file = secret_dir / "session.key"
    secret_dir.mkdir(parents=True, exist_ok=True)
    try:
        if secret_file.exists():
            return secret_file.read_bytes()
        import secrets

        value = secrets.token_bytes(48)
        descriptor = os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
        return value
    except OSError:
        # A process-local fallback is safer than an insecure hard-coded key.
        import secrets

        return secrets.token_bytes(48)
