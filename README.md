# Equity Research Dashboard
**Python · SQL · Pandas** — automated financial & valuation analysis across 25+ listed companies

This project mirrors the resume line item: *"Developed a Python and SQL-based equity
research dashboard to analyze 25+ listed companies and automate 10+ financial &
valuation metrics; built interactive dashboards for 5-year financial analysis, peer
benchmarking, and comparative valuation."*

It is a fully working, end-to-end pipeline — not just a mockup:

```
generate_data.py  →  load_to_sql.py  →  metrics.py  →  build_dashboard_data.py  →  dashboard/index.html
   (source data)        (SQLite DB)      (Pandas analytics)    (JSON export)         (interactive UI)
```

## What it does

- **Coverage**: 25 companies across 6 sectors (IT Services, Banking & NBFC, Pharma,
  FMCG, Auto & Ancillary, EV/Clean Mobility), 5 fiscal years of financial statement
  line items each (125 company-year records).
- **SQL layer**: a normalized SQLite schema (`companies`, `financials`, `market_data`,
  `metrics`, `sector_benchmarks`, `comparative_valuation`) — all analysis reads from
  and writes back to the database.
- **12 automated metrics per company** (10+ required): revenue growth, EBITDA margin,
  net margin, ROE, ROA, debt-to-equity, current ratio, free cash flow, FCF yield,
  P/E, EV/EBITDA, P/B.
- **Peer benchmarking**: sector-level mean/median for every metric, computed with
  Pandas `groupby`.
- **Comparative valuation**: percentile-ranks each company against its sector peers
  on both valuation multiples (cheaper = better) and fundamental strength (higher =
  better), rolling them into a single composite score — this is the ranking logic
  behind the "Comparative Valuation" tab.
- **Interactive dashboard** (`dashboard/index.html`): a single static HTML file
  (Plotly.js for charts) — sortable company list, sector filters, 5-year trend
  charts, peer benchmarking bar charts, and a valuation leaderboard with a
  quality-vs-value diverging bar visualization plus a P/E-vs-ROE scatter map.

## Running it

```bash
pip install pandas numpy
python3 scripts/generate_data.py         # builds data/*.csv
python3 scripts/load_to_sql.py           # builds equity_research.db
python3 scripts/metrics.py               # computes metrics + peer + valuation tables
python3 scripts/build_dashboard_data.py  # exports dashboard/data.js
```

Then just open `dashboard/index.html` in a browser — it's fully static, no server
required (it reads `data.js` directly).

## Using real data instead of the sample set

`scripts/generate_data.py` is intentionally isolated: it's the **only** file that
invents numbers. It writes exactly three CSVs (`companies.csv`, `financials.csv`,
`market_data.csv`) with a fixed schema. To run this on real coverage, replace that
one script with a puller from a real source (e.g. `yfinance`, an NSE/BSE data
vendor, or an export from Screener.in / a terminal) that writes the same three
CSVs — nothing in `load_to_sql.py`, `metrics.py`, or the dashboard needs to change.

## File structure

```
equity_dashboard/
├── data/                     # generated input CSVs
├── sql/schema.sql            # database schema
├── scripts/
│   ├── generate_data.py      # sample data generator (swap point for real data)
│   ├── load_to_sql.py        # CSV → SQLite
│   ├── metrics.py            # Pandas analytics: 12 metrics + peer benchmarking + comparative valuation
│   └── build_dashboard_data.py  # SQLite → dashboard/data.js
├── dashboard/
│   ├── index.html            # interactive dashboard (Plotly.js)
│   └── data.js               # generated data payload (JSON)
├── equity_research.db        # SQLite database (generated)
└── README.md
```

## Notes on the sample data

Because this environment has no network access to live market-data providers, the
25 companies are realistic but synthetic (names like "TataCode Synergy" or
"Wipronix Global" are stand-ins, sector-calibrated growth/margin/leverage
assumptions). All formulas, the SQL schema, and the dashboard logic are
production-grade — only the input numbers are simulated. Swap in a real feed as
described above to point this at actual listed companies.
