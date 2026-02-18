"""SQLite table definitions (DDL)."""

USERS = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'client',
    password_hash TEXT,
    cognito_sub TEXT
);
"""

SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    factor1_done INTEGER NOT NULL DEFAULT 0,
    factor2_done INTEGER NOT NULL DEFAULT 0,
    factor3_done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    ttl INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

SECURITY_QA = """
CREATE TABLE IF NOT EXISTS security_qa (
    user_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer_hash TEXT NOT NULL,
    PRIMARY KEY (user_id, question_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

CAESAR_CONFIG = """
CREATE TABLE IF NOT EXISTS caesar_config (
    user_id TEXT PRIMARY KEY,
    rotation INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

CAESAR_CHALLENGES = """
CREATE TABLE IF NOT EXISTS caesar_challenges (
    session_id TEXT PRIMARY KEY,
    plaintext TEXT NOT NULL,
    rotation INTEGER NOT NULL,
    expected_ciphertext TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""

ALL_TABLES = [USERS, SESSIONS, SECURITY_QA, CAESAR_CONFIG, CAESAR_CHALLENGES]
