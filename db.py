"""SQLite storage for FinBot."""
import json
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

-- One analysed read-through per headline: which tickers it moves and why.
CREATE TABLE IF NOT EXISTS news_insights (
    id INTEGER PRIMARY KEY,
    news_id INTEGER UNIQUE REFERENCES news(id),
    tickers TEXT,           -- comma-separated symbols named in the story
    event_labels TEXT,      -- comma-separated matched event types
    direction INTEGER,      -- +1 bullish / -1 bearish / 0 two-sided
    magnitude REAL,         -- 0-1 expected size of the move
    confidence TEXT,        -- HIGH / MEDIUM / LOW
    score REAL,             -- combined conviction score
    impacts TEXT,           -- JSON list of {ticker, kind, direction, magnitude, reason}
    narrative TEXT,         -- the plain-English explanation
    suggestion TEXT,        -- the stance, stated as a stance
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_insights_score ON news_insights(score DESC);

-- Content already pushed to the phone, so an hourly run does not re-send
-- the same mover five times. Keyed by a stable hash of the item.
CREATE TABLE IF NOT EXISTS notified (
    key TEXT PRIMARY KEY,
    kind TEXT,
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Small key/value store for pipeline bookkeeping (engine versions, run marks).
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

-- Rolling technical/statistical context per symbol, refreshed each pattern run.
CREATE TABLE IF NOT EXISTS symbol_stats (
    symbol TEXT PRIMARY KEY,
    price REAL, chg_1d REAL, ret_1w REAL, ret_1m REAL, ret_3m REAL, ret_6m REAL,
    sma20 REAL, sma50 REAL, sma200 REAL,
    rsi REAL, atr_pct REAL,
    hi_52w REAL, lo_52w REAL, pct_from_hi REAL, pct_from_lo REAL,
    vol REAL, avg_vol20 REAL, vol_mult REAL,
    trend TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Narrated commentary on a number (a mover, a pattern, a crypto swing).
CREATE TABLE IF NOT EXISTS commentary (
    id INTEGER PRIMARY KEY,
    kind TEXT,              -- mover / pattern / crypto / breadth / rates
    symbol TEXT,
    headline TEXT,
    body TEXT,
    severity TEXT,          -- HIGH / MEDIUM / LOW
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kind, symbol, headline, created_at)
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


# Columns added after the first release. Applied on every init so an existing
# finbot.db (including the one cached by GitHub Actions) upgrades in place.
MIGRATIONS = [
    ("congress_trades", "doc_url", "TEXT"),
    ("congress_trades", "source", "TEXT"),
]


def init():
    with conn() as c:
        c.executescript(SCHEMA)
        for table, col, coltype in MIGRATIONS:
            existing = {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
            if col not in existing:
                c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")


def dumps(obj):
    """Compact JSON for the columns that hold structured payloads."""
    return json.dumps(obj, separators=(",", ":"))


def loads(text, default=None):
    try:
        return json.loads(text) if text else (default if default is not None else [])
    except (TypeError, ValueError):
        return default if default is not None else []


def insert_many(table, rows):
    """Insert dicts, ignoring duplicates. Returns number inserted."""
    if not rows:
        return 0
    cols = rows[0].keys()
    sql = f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
    with conn() as c:
        cur = c.executemany(sql, [tuple(r[k] for k in cols) for r in rows])
        return cur.rowcount
