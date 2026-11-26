import pandas as pd
from database import get_connection


def read_data(query, params=()):

    conn = get_connection()

    try:
        return pd.read_sql_query(
            query, conn, params=params
        )

    finally:
        conn.close()


def execute_query(query, params=()):

    conn = get_connection()

    try:
        conn.execute(query, params)
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_count(table):

    allowed_tables = [
        "employees", "brands", "pods",
        "processes", "assignments",
        "brand_processes", "roster",
        "leaves", "holidays"
    ]

    if table not in allowed_tables:
        raise ValueError("Invalid table name")

    df = read_data(
        f"SELECT COUNT(*) AS total FROM {table}"
    )

    return int(df.iloc[0]["total"])