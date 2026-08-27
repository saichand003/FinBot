"""Read the database into the plain dicts the renderer draws from.

Kept separate from rendering so the numbers can be tested without HTML, and so
the same payload can feed a different front-end later.
"""
import datetime as dt

import config
import db
from analysis.assets import info, _SECTOR
from analysis.plainspeak import beginner_read, plain_event

DIRECTION_WORD = {1: "bullish", -1: "bearish", 0: "two-sided"}


def _rows(c, sql, args=()):
    return [dict(r) for r in c.execute(sql, args)]


# Which groups appear in the "what you could invest in" browser, in the order a
# beginner should meet them: broadest and safest first, speculative last.
BROWSE_GROUPS = [
    ("broad_etf", "Whole-market funds",
     "One purchase spreads your money across hundreds of companies. This is where most "
     "beginner guidance starts."),
    ("intl_etf", "International funds",
     "The same idea, but outside the US - so your savings do not depend on one country."),
    ("dividend_etf", "Dividend funds",
     "Companies that pay out regular cash. Steadier, usually slower growing."),
    ("bond_fund", "Bonds and cash-like",
     "Lending money rather than owning companies. The steadying part of a portfolio."),
    ("sector_etf", "Single-industry funds",
     "A bet that one industry beats the rest. More focused, so bumpier."),
    ("commodity_etf", "Gold and silver",
     "Owned as insurance against inflation and crises, not for growth."),
    ("stock", "Individual companies",
     "Owning one business directly. The highest reward and the highest single-point risk."),
    ("growth_etf", "High-risk funds",
     "Concentrated bets on unprofitable, fast-growing companies. Money you can afford to lose."),
    ("bond_yield", "Interest rates",
     "Not things you buy - the backdrop that prices everything else."),
    ("index", "Market scoreboards",
     "How the market as a whole is doing."),
    ("volatility", "The fear gauge",
     "How nervous the market is right now."),
]


def _plain_story(insight):
    """A jargon-free version of what a headline means and who it touches."""
    labels = [e for e in (insight["event_labels"] or "").split(",") if e]
    lines = []
    for lbl in labels[:2]:
        txt = plain_event(lbl)
        if txt:
            lines.append(txt)

    tickers = [t for t in (insight["tickers"] or "").split(",") if t]
    if tickers:
        named = []
        for t in tickers[:3]:
            desc = info(t)["plain"].rstrip(".").replace("A single company: ", "")
            # Only add the parenthetical when it actually says something.
            named.append(f"{t} ({desc})" if "individual public company" not in desc else t)
        word = {1: "good news for", -1: "bad news for", 0: "a wildcard for"}[insight["direction"]]
        lines.append(f"FinBot reads this as {word} {'; '.join(named)}.")
    else:
        impacts = insight["impacts"]
        if isinstance(impacts, str):
            impacts = db.loads(impacts)
        if impacts:
            syms = ", ".join(i["ticker"] for i in impacts[:4])
            word = {1: "lift", -1: "weigh on", 0: "shake up"}[insight["direction"]]
            lines.append(f"No single company is named, so this is the kind of news that tends to "
                         f"{word} a whole group at once - here, {syms}.")
        else:
            lines.append("FinBot could not tie this to anything it tracks, so treat it as "
                         "background reading rather than something to act on.")

    if insight["confidence"] == "LOW":
        lines.append("Confidence is low - this is a weak signal, not something to act on.")
    return lines


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
            i["plain"] = _plain_story(i)

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

    # The browsable universe, each with a plain-English read.
    browse = []
    for kind, title, blurb in BROWSE_GROUPS:
        rows = []
        for sym, st in sorted(stats.items()):
            meta = info(sym)
            if meta["kind"] != kind:
                continue
            read = beginner_read(sym, st)
            # For a company, "what they do" is far more useful under the name
            # than repeating the category.
            read["sub"] = _SECTOR.get(sym) if meta["kind"] == "stock" else meta["kind_label"]
            read["price"] = st.get("price")
            read["chg_1d"] = st.get("chg_1d")
            read["ret_1m"] = st.get("ret_1m")
            read["ret_6m"] = st.get("ret_6m")
            rows.append(read)
        rows.sort(key=lambda r: (r["risk"], r["symbol"]))
        if rows:
            browse.append({"kind": kind, "title": title, "blurb": blurb, "rows": rows})

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
        "browse": browse,
    }
