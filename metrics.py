"""
metrics.py
----------
Pulls financial + market data OUT of SQL into Pandas, computes 10+
financial & valuation metrics per company per fiscal year, and writes
the results back into the `metrics` table in SQLite.

Metrics computed (10 total):
  1. Revenue growth (YoY %)
  2. EBITDA margin
  3. Net margin
  4. ROE            (Net income / Total equity)
  5. ROA            (Net income / Total assets)
  6. Debt-to-Equity
  7. Current ratio
  8. Free cash flow (OCF - Capex)
  9. FCF yield      (FCF / Market cap, latest year only)
 10. P/E ratio      (Price / EPS, latest year only)
 11. EV/EBITDA      (Enterprise value / EBITDA, latest year only)
 12. P/B ratio      (Market cap / Total equity, latest year only)
"""

import sqlite3
import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "equity_research.db")


def compute_metrics(conn):
    financials = pd.read_sql("SELECT * FROM financials ORDER BY ticker, fiscal_year", conn)
    market = pd.read_sql("SELECT * FROM market_data", conn)

    financials = financials.sort_values(["ticker", "fiscal_year"])

    # --- Year-over-year revenue growth, per ticker ---
    financials["revenue_growth"] = (
        financials.groupby("ticker")["revenue"].pct_change() * 100
    )

    # --- Margin & return ratios (all years) ---
    financials["ebitda_margin"] = financials["ebitda"] / financials["revenue"] * 100
    financials["net_margin"] = financials["net_income"] / financials["revenue"] * 100
    financials["roe"] = financials["net_income"] / financials["total_equity"] * 100
    financials["roa"] = financials["net_income"] / financials["total_assets"] * 100
    financials["debt_to_equity"] = financials["total_debt"] / financials["total_equity"]
    financials["current_ratio"] = financials["current_assets"] / financials["current_liabilities"]
    financials["fcf"] = financials["operating_cash_flow"] - financials["capex"]

    # --- Valuation multiples: only meaningful for the latest year, using market snapshot ---
    latest_year = financials["fiscal_year"].max()
    latest = financials[financials["fiscal_year"] == latest_year].merge(market, on="ticker", how="left")

    latest["eps"] = latest["net_income"] / latest["shares_outstanding"]
    latest["pe_ratio"] = latest["price"] / latest["eps"]
    latest["enterprise_value"] = latest["market_cap"] + latest["total_debt"] - latest["cash_and_equiv"]
    latest["ev_ebitda"] = latest["enterprise_value"] / latest["ebitda"]
    latest["pb_ratio"] = latest["market_cap"] / latest["total_equity"]
    latest["fcf_yield"] = latest["fcf"] / latest["market_cap"] * 100

    val_cols = ["ticker", "fiscal_year", "pe_ratio", "ev_ebitda", "pb_ratio", "fcf_yield"]
    financials = financials.merge(latest[val_cols], on=["ticker", "fiscal_year"], how="left")

    return financials


def peer_benchmarking(conn, financials):
    """Sector-level averages/medians for the latest fiscal year — the 'peer benchmarking' layer."""
    companies = pd.read_sql("SELECT ticker, sector FROM companies", conn)
    latest_year = financials["fiscal_year"].max()
    latest = financials[financials["fiscal_year"] == latest_year].merge(companies, on="ticker")

    bench_cols = ["revenue_growth", "ebitda_margin", "net_margin", "roe", "roa",
                  "debt_to_equity", "current_ratio", "fcf_yield", "pe_ratio", "ev_ebitda", "pb_ratio"]

    sector_bench = latest.groupby("sector")[bench_cols].agg(["mean", "median"]).round(2)
    sector_bench.columns = ["_".join(c) for c in sector_bench.columns]
    return sector_bench.reset_index(), latest


def comparative_valuation(latest_with_sector):
    """Percentile rank of each company vs its sector peers — 'comparative valuation' layer.
    Lower percentile on PE / EV-EBITDA / PB = cheaper vs peers.
    Higher percentile on ROE / margins / FCF yield = stronger fundamentals vs peers.
    """
    df = latest_with_sector.copy()
    cheap_cols = ["pe_ratio", "ev_ebitda", "pb_ratio"]
    strong_cols = ["roe", "roa", "ebitda_margin", "net_margin", "fcf_yield", "revenue_growth"]

    for col in cheap_cols:
        df[col + "_pctile"] = df.groupby("sector")[col].rank(pct=True, ascending=True) * 100
    for col in strong_cols:
        df[col + "_pctile"] = df.groupby("sector")[col].rank(pct=True, ascending=True) * 100

    # Simple composite score: average of fundamental-strength percentiles minus
    # average of valuation-richness percentiles (rewards cheap + strong)
    df["composite_score"] = (
        df[[c + "_pctile" for c in strong_cols]].mean(axis=1)
        - df[[c + "_pctile" for c in cheap_cols]].mean(axis=1)
    ).round(1)

    return df


def main():
    conn = sqlite3.connect(DB_PATH)

    financials = compute_metrics(conn)

    # Write metrics table back to SQL
    metrics_cols = ["ticker", "fiscal_year", "revenue_growth", "ebitda_margin", "net_margin",
                    "roe", "roa", "debt_to_equity", "current_ratio", "fcf", "fcf_yield",
                    "pe_ratio", "ev_ebitda", "pb_ratio"]
    financials[metrics_cols].to_sql("metrics", conn, if_exists="replace", index=False)

    sector_bench, latest_with_sector = peer_benchmarking(conn, financials)
    comp_val = comparative_valuation(latest_with_sector)

    sector_bench.to_sql("sector_benchmarks", conn, if_exists="replace", index=False)
    comp_val.to_sql("comparative_valuation", conn, if_exists="replace", index=False)

    conn.commit()
    print("Computed metrics for", financials["ticker"].nunique(), "companies across",
          financials["fiscal_year"].nunique(), "fiscal years.")
    print("Peer benchmarking table: sector_benchmarks")
    print("Comparative valuation table: comparative_valuation")

    conn.close()


if __name__ == "__main__":
    main()
