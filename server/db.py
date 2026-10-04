import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    name  TEXT NOT NULL,
    age   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    note  TEXT NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email)
);
"""


def get_db(env: str) -> sqlite3.Connection:
    """
    Returns a SQLite connection for the given environment.

    Each environment (dev / prod) has its own .db file so data is
    isolated between test runs targeting different environments.
    """
    conn = sqlite3.connect(f"{env}.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
