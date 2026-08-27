"""Read the database into the plain dicts the renderer draws from.

Kept separate from rendering so the numbers can be tested without HTML, and so
the same payload can feed a different front-end later.
"""
import datetime as dt

import config
import db

DIRECTION_WORD = {1: "bullish", -1: "bearish", 0: "two-sided"}


def _rows(c, sql, args=()):
    return [dict(r) for r in c.execute(sql, args)]


def collect():
    with db.conn() as c:
        stats = {r["symbol"]: r for r in _rows(c, "SELECT * FROM symbol_stats")}

        markets = _rows(c, """
            SELECT symbol, asset_class, price, change_pct, volume, MAX(snapshot_at) AS at
            FROM market_snapshots GROUP BY symbol
        """)
        for m in markets:
            m["stats"] = stats.get(m["symbol"], {})

        crypto = _rows(c, """
            SELECT coin, price, mcap, chg_1h, chg_24h, chg_7d, chg_30d,
                   MAX(snapshot_at) AS at
            FROM crypto_snapshots GROUP BY coin ORDER BY mcap DESC
        """)

        insights = _rows(c, """
            SELECT i.*, n.title, n.source, n.url, n.published, n.summary
            FROM news_insights i JOIN news n ON n.id = i.news_id
            ORDER BY i.score DESC, i.news_id DESC LIMIT 90
        """)
        for i in insights:
            i["impacts"] = db.loads(i["impacts"])
            i["ticker_list"] = [t for t in (i["tickers"] or "").split(",") if t]
            i["event_list"] = [e for e in (i["event_labels"] or "").split(",") if e]
            i["dir_word"] = DIRECTION_WORD.get(i["direction"], "two-sided")

        commentary = _rows(c, """
            SELECT * FROM commentary ORDER BY
              CASE severity WHEN 'HIGH' THEN 0 WHEN 'MEDIUM' THEN 1 ELSE 2 END,
              created_at DESC LIMIT 60
        """)

        patterns = _rows(c, """
            SELECT * FROM patterns ORDER BY detected_at DESC LIMIT 25
        """)

        congress = _rows(c, """
            SELECT * FROM congress_trades ORDER BY disclosed DESC LIMIT 12
        """)

        filings = _rows(c, """
            SELECT * FROM fund_filings ORDER BY filing_date DESC LIMIT 10
        """)

        counts = dict(
            news=c.execute("SELECT COUNT(*) FROM news").fetchone()[0],
            analysed=c.execute("SELECT COUNT(*) FROM news_insights").fetchone()[0],
            high=c.execute(
                "SELECT COUNT(*) FROM news_insights WHERE confidence='HIGH'").fetchone()[0],
            symbols=len(stats),
        )

    lead = next((x for x in commentary if x["kind"] == "breadth"), None)
    return {
        "generated": dt.datetime.now().strftime("%A %d %B %Y, %H:%M"),
        "generated_iso": dt.datetime.now().isoformat(timespec="seconds"),
        "stats": stats,
        "markets": markets,
        "crypto": crypto,
        "insights": insights,
        "commentary": commentary,
        "lead": lead,
        "movers": [x for x in commentary if x["kind"] == "mover"],
        "pattern_notes": [x for x in commentary if x["kind"] == "pattern"],
        "crypto_notes": [x for x in commentary if x["kind"] == "crypto"],
        "congress_notes": [x for x in commentary if x["kind"] == "congress"],
        "patterns": patterns,
        "congress": congress,
        "filings": filings,
        "counts": counts,
    }
