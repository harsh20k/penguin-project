import sqlite3
from contextlib import contextmanager
from app.config import DB_PATH
from app.schemas.db import ALL_TABLES


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        for ddl in ALL_TABLES:
            conn.execute(ddl)
        conn.commit()


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()
