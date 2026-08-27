"""SQLite storage for FinBot."""
import sqlite3
from contextlib import contextmanager

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY,
    source TEXT, title TEXT, url TEXT UNIQUE,
    published TEXT, summary TEXT, fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS congress_trades (
    id INTEGER PRIMARY KEY,
    chamber TEXT, politician TEXT, ticker TEXT, asset TEXT,
    tx_type TEXT, tx_date TEXT, amount TEXT, disclosed TEXT,
    UNIQUE(politician, ticker, tx_date, tx_type, amount)
);
CREATE TABLE IF NOT EXISTS fund_filings (
    id INTEGER PRIMARY KEY,
    fund TEXT, cik TEXT, form TEXT, filing_date TEXT,
    accession TEXT UNIQUE, doc_url TEXT
);
CREATE TABLE IF NOT EXISTS market_snapshots (
    id INTEGER PRIMARY KEY,
    symbol TEXT, asset_class TEXT, price REAL, change_pct REAL,
    volume REAL, snapshot_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS crypto_snapshots (
    id INTEGER PRIMARY KEY,
    coin TEXT, price REAL, mcap REAL,
    chg_1h REAL, chg_24h REAL, chg_7d REAL, chg_30d REAL,
    snapshot_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY,
    symbol TEXT, pattern TEXT, detail TEXT,
    detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, pattern, detected_at)
);
"""


@contextmanager
def conn():
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init():
    with conn() as c:
        c.executescript(SCHEMA)


def insert_many(table, rows):
    """Insert dicts, ignoring duplicates. Returns number inserted."""
    if not rows:
        return 0
    cols = rows[0].keys()
    sql = f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
    with conn() as c:
        cur = c.executemany(sql, [tuple(r[k] for k in cols) for r in rows])
        return cur.rowcount
