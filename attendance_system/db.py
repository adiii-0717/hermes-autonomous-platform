"""
Attendance System – Database layer.

Uses SQLite for persistent storage with two tables:
  students   – roster of registered students (roll_number is unique PK)
  attendance – one row per student per day (UNIQUE constraint prevents duplicates)
"""
import sqlite3
import os

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "attendance.db")


def get_connection(db_path=None):
    """Return a sqlite3 connection with row-factory enabled."""
    path = db_path or DEFAULT_DB
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialize_db(db_path=None):
    """Create tables if they don't already exist."""
    conn = get_connection(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            roll_number TEXT PRIMARY KEY,
            name        TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT    NOT NULL,
            date        TEXT    NOT NULL,       -- YYYY-MM-DD
            status      TEXT    NOT NULL DEFAULT 'P',  -- P=present, A=absent
            FOREIGN KEY (roll_number) REFERENCES students(roll_number),
            UNIQUE(roll_number, date)
        );
    """)
    conn.commit()
    conn.close()
