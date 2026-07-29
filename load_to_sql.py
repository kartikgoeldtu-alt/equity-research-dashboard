"""
load_to_sql.py
--------------
Loads data/companies.csv, data/financials.csv, data/market_data.csv into
a SQLite database (equity_research.db) built from sql/schema.sql.

This is the "SQL" layer of the stack: all downstream analysis in
metrics.py reads FROM the database via SQL queries (not directly from
the CSVs), so the project genuinely exercises Python + SQL + Pandas
together rather than using SQL as a formality.
"""

import sqlite3
import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "equity_research.db")
SCHEMA_PATH = os.path.join(BASE, "sql", "schema.sql")
DATA_DIR = os.path.join(BASE, "data")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())

    companies = pd.read_csv(os.path.join(DATA_DIR, "companies.csv"))
    financials = pd.read_csv(os.path.join(DATA_DIR, "financials.csv"))
    market = pd.read_csv(os.path.join(DATA_DIR, "market_data.csv"))

    companies.to_sql("companies", conn, if_exists="append", index=False)
    financials.to_sql("financials", conn, if_exists="append", index=False)
    market.to_sql("market_data", conn, if_exists="append", index=False)

    conn.commit()

    n_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_fin = conn.execute("SELECT COUNT(*) FROM financials").fetchone()[0]
    print(f"Loaded {n_companies} companies and {n_fin} financial-year records into {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
