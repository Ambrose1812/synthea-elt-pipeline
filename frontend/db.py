# frontend/db.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healthcare")
DB_USER = os.getenv("DB_USER", "analytics_readonly")
DB_PASSWORD = os.getenv("DB_PASSWORD")

_engine = None


def get_engine():
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
    Assumes the SQL has already passed sql_guard.py's checks.
    """
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)