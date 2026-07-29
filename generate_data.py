"""
generate_data.py
-----------------
Generates a realistic sample dataset for the Equity Research Dashboard:
  - 25 listed companies across 6 sectors
  - 5 years of annual financial statement line items per company
  - a current market data snapshot (price, market cap)

WHY SYNTHETIC DATA:
This sandbox has no network access to live market data providers
(e.g. Yahoo Finance / NSE / BSE APIs). The pipeline below is written so
that swapping this file out for a real data puller (e.g. `yfinance`,
`nsepy`, a broker API, or a SQL export from a terminal like Bloomberg/
Screener.in) is a drop-in replacement — as long as it writes the same
`companies.csv` / `financials.csv` / `market_data.csv` schemas, nothing
downstream (SQL load, metrics, dashboard) needs to change.

Output: data/companies.csv, data/financials.csv, data/market_data.csv
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

SECTORS = {
    "IT Services":      dict(margin=0.24, growth=0.13, debt_eq=0.10),
    "Banking & NBFC":   dict(margin=0.30, growth=0.15, debt_eq=1.20),
    "Pharma":           dict(margin=0.20, growth=0.11, debt_eq=0.35),
    "FMCG":             dict(margin=0.18, growth=0.10, debt_eq=0.25),
    "Auto & Ancillary": dict(margin=0.13, growth=0.14, debt_eq=0.45),
    "EV / Clean Mobility": dict(margin=0.09, growth=0.32, debt_eq=0.55),
}

COMPANIES = [
    ("INFT", "Infotrek Systems", "IT Services"),
    ("TCSY", "TataCode Synergy", "IT Services"),
    ("WPRO", "Wipronix Global", "IT Services"),
    ("HCLW", "HCL Wavefront", "IT Services"),
    ("MPHX", "MphasiX Labs", "IT Services"),
    ("HDBK", "HDF Bank Ltd", "Banking & NBFC"),
    ("ICIB", "ICIC Bank Corp", "Banking & NBFC"),
    ("BAJF", "Bajaj Financio", "Banking & NBFC"),
    ("KOTM", "Kotam Mahindra Bank", "Banking & NBFC"),
    ("SBIN2", "State Bank Nova", "Banking & NBFC"),
    ("SUNP", "Sun Pharma Industries", "Pharma"),
    ("CIPL", "Ciplex Labs", "Pharma"),
    ("DRRD", "Dr. Reddish Labs", "Pharma"),
    ("LUPN", "Lupinex Pharma", "Pharma"),
    ("AURO", "Aurobindal Pharma", "Pharma"),
    ("HULV", "Hindustan Uni Lever", "FMCG"),
    ("ITCL", "ITC Leaf Ltd", "FMCG"),
    ("NEST", "Nestee India", "FMCG"),
    ("BRIT", "Britanniq Industries", "FMCG"),
    ("DABR", "Dabour India", "FMCG"),
    ("MRTI", "Maroti Suzuki", "Auto & Ancillary"),
    ("TAMO", "Tatva Motors", "Auto & Ancillary"),
    ("BAJA", "Bajaja Auto", "Auto & Ancillary"),
    ("EIMO", "Eichar Motors", "Auto & Ancillary"),
    ("UVAM", "Ultraviolette Automotive", "EV / Clean Mobility"),
]

def gen_company_financials(ticker, sector_params, base_revenue, base_shares):
    years = [2021, 2022, 2023, 2024, 2025]
    rows = []
    revenue = base_revenue
    equity = base_revenue * np.random.uniform(0.9, 1.4)
    for i, yr in enumerate(years):
        g = sector_params["growth"] * np.random.uniform(0.7, 1.3)
        if i > 0:
            revenue = revenue * (1 + g)
        margin = sector_params["margin"] * np.random.uniform(0.85, 1.15)
        ebitda = revenue * margin
        ebit = ebitda * np.random.uniform(0.75, 0.9)
        net_income = ebit * np.random.uniform(0.55, 0.75)
        equity = equity * (1 + np.random.uniform(0.05, 0.18))
        debt = equity * sector_params["debt_eq"] * np.random.uniform(0.8, 1.2)
        total_assets = equity + debt + revenue * 0.15
        cash = revenue * np.random.uniform(0.05, 0.18)
        current_assets = revenue * np.random.uniform(0.35, 0.55)
        current_liabilities = revenue * np.random.uniform(0.22, 0.38)
        capex = revenue * np.random.uniform(0.04, 0.09)
        ocf = ebitda * np.random.uniform(0.6, 0.85)
        rows.append(dict(
            ticker=ticker, fiscal_year=yr,
            revenue=round(revenue, 1), ebitda=round(ebitda, 1), ebit=round(ebit, 1),
            net_income=round(net_income, 1), total_assets=round(total_assets, 1),
            total_equity=round(equity, 1), total_debt=round(debt, 1),
            cash_and_equiv=round(cash, 1), current_assets=round(current_assets, 1),
            current_liabilities=round(current_liabilities, 1), capex=round(capex, 1),
            operating_cash_flow=round(ocf, 1), shares_outstanding=base_shares
        ))
    return rows

def main():
    companies_rows = []
    financials_rows = []
    market_rows = []

    for ticker, name, sector in COMPANIES:
        sp = SECTORS[sector]
        base_revenue = np.random.uniform(800, 45000)   # INR crore
        base_shares = np.random.uniform(10, 250)        # crore shares

        companies_rows.append(dict(
            ticker=ticker, name=name, sector=sector,
            industry=sector, country="India", currency="INR"
        ))

        fin_rows = gen_company_financials(ticker, sp, base_revenue, base_shares)
        financials_rows.extend(fin_rows)

        latest = fin_rows[-1]
        eps = latest["net_income"] / latest["shares_outstanding"]
        pe_target = np.random.uniform(14, 55) if sector != "EV / Clean Mobility" else np.random.uniform(30, 90)
        price = max(eps * pe_target, 5)
        market_cap = price * latest["shares_outstanding"]

        market_rows.append(dict(
            ticker=ticker, price=round(price, 2),
            market_cap=round(market_cap, 1), as_of_date="2026-07-30"
        ))

    pd.DataFrame(companies_rows).to_csv(os.path.join(OUT_DIR, "companies.csv"), index=False)
    pd.DataFrame(financials_rows).to_csv(os.path.join(OUT_DIR, "financials.csv"), index=False)
    pd.DataFrame(market_rows).to_csv(os.path.join(OUT_DIR, "market_data.csv"), index=False)

    print(f"Generated {len(companies_rows)} companies, {len(financials_rows)} financial-year rows.")

if __name__ == "__main__":
    main()
