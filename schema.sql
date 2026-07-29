-- ============================================================
-- Equity Research Dashboard — Database Schema
-- ============================================================

DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS financials;
DROP TABLE IF EXISTS market_data;
DROP TABLE IF EXISTS metrics;

-- Master list of covered companies
CREATE TABLE companies (
    ticker       TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    sector       TEXT NOT NULL,
    industry     TEXT,
    country      TEXT,
    currency     TEXT DEFAULT 'INR'
);

-- 5-year annual financial statement data (as-reported, in INR crore)
CREATE TABLE financials (
    ticker              TEXT NOT NULL,
    fiscal_year         INTEGER NOT NULL,
    revenue             REAL,
    ebitda              REAL,
    ebit                REAL,
    net_income          REAL,
    total_assets        REAL,
    total_equity        REAL,
    total_debt          REAL,
    cash_and_equiv      REAL,
    current_assets      REAL,
    current_liabilities REAL,
    capex               REAL,
    operating_cash_flow REAL,
    shares_outstanding  REAL,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Latest market data snapshot used for valuation multiples
CREATE TABLE market_data (
    ticker          TEXT PRIMARY KEY,
    price           REAL,
    market_cap      REAL,
    as_of_date      TEXT,
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);

-- Computed metrics store (populated by scripts/metrics.py)
CREATE TABLE metrics (
    ticker              TEXT NOT NULL,
    fiscal_year         INTEGER NOT NULL,
    revenue_growth      REAL,
    ebitda_margin       REAL,
    net_margin          REAL,
    roe                 REAL,
    roa                 REAL,
    debt_to_equity      REAL,
    current_ratio       REAL,
    fcf                 REAL,
    fcf_yield           REAL,
    pe_ratio            REAL,
    ev_ebitda           REAL,
    pb_ratio            REAL,
    PRIMARY KEY (ticker, fiscal_year),
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);
