# frontend/db.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "172.19.128.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healthcare")
DB_USER = os.getenv("DB_USER", "analytics_readonly")
DB_PASSWORD = os.getenv("DB_PASSWORD")

_engine = None


def get_engine():
    """
    Returns a cached SQLAlchemy engine connected as the read-only role.
    Cached so Streamlit doesn't open a new connection pool on every rerun.
    """
    global _engine
    if _engine is None:
        connection_string = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        _engine = create_engine(connection_string, pool_pre_ping=True)
    return _engine


def run_query(sql: str) -> pd.DataFrame:
    """
    Executes a query against the analytics schema and returns a DataFrame.

    This function assumes the SQL has already passed sql_guard.py's checks.
    It does not do its own validation - keeping that logic in one place
    (sql_guard.py) rather than duplicating it here.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)