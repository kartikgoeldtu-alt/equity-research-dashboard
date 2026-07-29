"""
build_dashboard_data.py
------------------------
Reads the computed tables back out of SQL (companies, financials,
metrics, sector_benchmarks, comparative_valuation) and serializes them
into a single dashboard/data.js file (a JS variable holding JSON) that
the static HTML dashboard loads directly — keeping the dashboard fully
offline/portable with no server required.
"""

import sqlite3
import pandas as pd
import json
import os

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "equity_research.db")
OUT_PATH = os.path.join(BASE, "dashboard", "data.js")


def df_records(conn, query):
    return json.loads(pd.read_sql(query, conn).to_json(orient="records"))


def main():
    os.makedirs(os.path.join(BASE, "dashboard"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    payload = {
        "companies": df_records(conn, "SELECT * FROM companies"),
        "financials": df_records(conn, "SELECT * FROM financials ORDER BY ticker, fiscal_year"),
        "metrics": df_records(conn, "SELECT * FROM metrics ORDER BY ticker, fiscal_year"),
        "sector_benchmarks": df_records(conn, "SELECT * FROM sector_benchmarks"),
        "comparative_valuation": df_records(conn, "SELECT * FROM comparative_valuation"),
    }

    with open(OUT_PATH, "w") as f:
        f.write("const DASHBOARD_DATA = ")
        json.dump(payload, f)
        f.write(";")

    print(f"Wrote dashboard data to {OUT_PATH}")
    print(f"  companies: {len(payload['companies'])}")
    print(f"  financials rows: {len(payload['financials'])}")
    print(f"  metrics rows: {len(payload['metrics'])}")
    print(f"  comparative_valuation rows: {len(payload['comparative_valuation'])}")

    conn.close()


if __name__ == "__main__":
    main()
