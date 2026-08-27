"""Stocks, indexes, ETFs/funds, and bond yields via yfinance."""
import yfinance as yf

import config
import db

ASSET_GROUPS = {
    "stock": config.STOCKS,
    "index": config.INDEXES,
    "etf_fund": config.ETFS_FUNDS,
    "bond": config.BONDS,
}


def crawl_markets():
    rows = []
    for asset_class, symbols in ASSET_GROUPS.items():
        data = yf.download(
            symbols, period="5d", interval="1d",
            group_by="ticker", progress=False, auto_adjust=True,
        )
        for sym in symbols:
            try:
                hist = data[sym].dropna()
                if len(hist) < 2:
                    continue
                last, prev = hist.iloc[-1], hist.iloc[-2]
                rows.append({
                    "symbol": sym,
                    "asset_class": asset_class,
                    "price": float(last["Close"]),
                    "change_pct": float((last["Close"] / prev["Close"] - 1) * 100),
                    "volume": float(last.get("Volume", 0) or 0),
                })
            except Exception as ex:
                print(f"[markets] {sym} failed: {ex}")
    n = db.insert_many("market_snapshots", rows)
    print(f"[markets] {n} snapshots stored")
    return n
