"""PostgreSQL JSONB compatibility store for the CCT Express legacy state API."""
import os
import psycopg
from psycopg.types.json import Jsonb

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cct_app_state (
    id SMALLINT PRIMARY KEY CHECK (id = 1),
    data JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

def _connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing. Configure PostgreSQL in the .env file.")
    return psycopg.connect(DATABASE_URL, connect_timeout=10)

def init_db():
    with _connect() as conn:
        conn.execute(TABLE_SQL)

def read_state():
    with _connect() as conn:
        conn.execute(TABLE_SQL)
        row = conn.execute("SELECT data FROM cct_app_state WHERE id = 1").fetchone()
        return row[0] if row else None

def write_state(data):
    with _connect() as conn:
        conn.execute(TABLE_SQL)
        conn.execute(
            """INSERT INTO cct_app_state (id, data, updated_at)
               VALUES (1, %s, NOW())
               ON CONFLICT (id) DO UPDATE
               SET data = EXCLUDED.data, updated_at = NOW()""",
            (Jsonb(data),),
        )
