"""Turn numbers into sentences.

A raw feed says "NVDA -3.2%". That is data, not information. This module says
what -3.2% means *given everything else we know*: whether volume confirmed it,
where it sits against the 50- and 200-day, how far it is from the highs, whether
momentum was already stretched, and what would change the read.

Every function here returns commentary rows: {kind, symbol, headline, body,
severity}. They are stored so the dashboard and the phone digest read from the
same source of truth.
"""
import config
import db

# How big a daily move has to be before it is worth narrating, by asset class.
MOVE_THRESHOLD = {"stock": 2.0, "etf_fund": 1.5, "index": 1.0, "bond": 1.5}

PATTERN_MEANING = {
    "golden_cross": (
        "Golden cross",
        "The 50-day average has crossed above the 200-day. It is a lagging signal - by "
        "definition the move already happened - but it marks the point where the "
        "intermediate trend structurally flips positive, and a lot of systematic and "
        "trend-following money uses exactly this trigger. Its value is less prediction "
        "than confirmation: it tells you the buyers have held control long enough to "
        "reshape the averages.",
        "The false-signal rate is high in choppy, sideways markets, where the averages "
        "cross back and forth. It works best when price is also making higher lows.",
    ),
    "death_cross": (
        "Death cross",
        "The 50-day average has crossed below the 200-day - the mirror image, and the "
        "signal that risk desks watch for de-grossing. It usually arrives well after the "
        "top, so it is a poor exit trigger on its own, but persistent trade below both "
        "averages is what turns a pullback into a downtrend.",
        "Historically a meaningful share of death crosses mark the low rather than the "
        "start of the decline. Confirm with volume and with whether the 200-day itself "
        "has started rolling over.",
    ),
    "rsi_overbought": (
        "Momentum stretched",
        "RSI above 70 means recent up-days have overwhelmed down-days to an unusual "
        "degree. The common misreading is that this means 'sell'. In a strong uptrend, "
        "RSI can sit above 70 for weeks and the stock keeps climbing - overbought is a "
        "feature of strength, not a top signal. What it does tell you is that the "
        "risk/reward of a *new* entry here is poor: you are paying up after the move.",
        "The actionable version is divergence - price making a new high while RSI makes "
        "a lower high. That is when stretched momentum starts to matter.",
    ),
    "rsi_oversold": (
        "Momentum washed out",
        "RSI below 30 means selling has been persistent and one-sided. Like its mirror, "
        "it is not a buy signal by itself - things that are cheap can get cheaper, and "
        "in a genuine downtrend RSI stays pinned low. It marks a zone where bounces "
        "become more likely because the marginal seller is running out.",
        "Look for the first higher low after the oversold print rather than buying the "
        "print itself. Catching the exact bottom is not the edge here.",
    ),
    "52wk_high": (
        "New 52-week high",
        "The stock is trading at the top of its one-year range. This is one of the more "
        "counter-intuitive signals in markets: stocks at 52-week highs have historically "
        "tended to keep outperforming over the following months, because a new high means "
        "nobody who owns it is underwater and therefore nobody is waiting to sell into "
        "strength at break-even. There is no overhead supply.",
        "The exception is a blow-off high on extreme volume after a vertical run, which "
        "is more often exhaustion than continuation.",
    ),
    "52wk_low": (
        "New 52-week low",
        "The stock is at the bottom of its one-year range. The mirror logic applies and "
        "it is unkind: everyone who bought in the last year is underwater, so every "
        "rally meets sellers trying to get back to flat. That overhead supply is why new "
        "lows tend to beget new lows.",
        "Worth separating company-specific breakdown from sector-wide selling - check "
        "whether the peers are at lows too before concluding it is idiosyncratic.",
    ),
    "volume_spike": (
        "Volume spike",
        "Today's volume is far above the 20-day norm. Volume is the conviction behind a "
        "price move: the same 3% gain means something completely different on half-normal "
        "volume than on triple. Heavy volume means institutions are repositioning, and "
        "moves made on heavy volume tend to persist, while moves on thin volume tend to "
        "mean-revert.",
        "Check whether the spike came with a price move or without one. Huge volume with "
        "a flat close is distribution - someone large is being absorbed.",
    ),
}


# "range-bound" is an adjective, "uptrend" a noun - one takes an article, one does not.
_ADJECTIVE_TRENDS = {"range-bound", "insufficient history"}


def _trend_phrase(trend):
    return trend if trend in _ADJECTIVE_TRENDS else f"in {'an' if trend[0] in 'aeiou' else 'a'} {trend}"


def _is_index(sym):
    """Index and volatility symbols do not have shareholders, so the language differs."""
    return sym.startswith("^")


def _sev(magnitude, hi, mid):
    return "HIGH" if magnitude >= hi else ("MEDIUM" if magnitude >= mid else "LOW")


def _stats():
    with db.conn() as c:
        return {r["symbol"]: dict(r) for r in c.execute("SELECT * FROM symbol_stats")}


# --------------------------------------------------------------- the movers
def _explain_move(sym, chg, asset_class, st):
    """The core narration: what does this % actually mean?"""
    d = "rose" if chg > 0 else "fell"
    body = [f"{sym} {d} {abs(chg):.2f}% today."]

    # 1. is this move large *for this stock*? ATR is the honest yardstick.
    atr = (st or {}).get("atr_pct")
    if atr:
        ratio = abs(chg) / atr if atr else 0
        if ratio >= 2:
            body.append(f"That is roughly {ratio:.1f}x its average daily range of {atr:.1f}% - "
                        f"a genuine outlier session, not noise.")
        elif ratio >= 1.2:
            body.append(f"Against an average daily range of {atr:.1f}%, this is a {ratio:.1f}x day - "
                        f"larger than normal but within what this name does.")
        else:
            body.append(f"Its average daily range is {atr:.1f}%, so despite the headline number "
                        f"this is an ordinary session for {sym}. Do not over-read it.")

    # 2. did volume confirm it?
    vm = (st or {}).get("vol_mult")
    if vm:
        if vm >= 1.8:
            body.append(f"Volume ran {vm:.1f}x the 20-day average, so real size was behind the move. "
                        f"Moves with volume behind them tend to follow through.")
        elif vm <= 0.7:
            body.append(f"Volume was only {vm:.1f}x normal. A move this size on light participation "
                        f"is the profile that usually fades - treat it as provisional.")
        else:
            body.append(f"Volume was about normal ({vm:.1f}x the 20-day average), so no strong "
                        f"conviction signal either way.")

    # 3. where does it sit structurally?
    if st and st.get("sma50") and st.get("sma200"):
        px, s50, s200 = st["price"], st["sma50"], st["sma200"]
        body.append(
            f"Structurally it is {_trend_phrase(st['trend'])}: price {px:,.2f} versus the "
            f"50-day at {s50:,.2f} ({(px/s50-1)*100:+.1f}%) and the 200-day at {s200:,.2f} "
            f"({(px/s200-1)*100:+.1f}%)."
        )

    # 4. momentum + position in the range
    rsi, from_hi = (st or {}).get("rsi"), (st or {}).get("pct_from_hi")
    if rsi is not None:
        if rsi >= 70:
            body.append(f"RSI is {rsi:.0f} - momentum is stretched, so new entries here carry poor odds.")
        elif rsi <= 30:
            body.append(f"RSI is {rsi:.0f} - washed out, which raises bounce odds without making it a bottom.")
        else:
            body.append(f"RSI at {rsi:.0f} is neutral: there is room to move in either direction "
                        f"before momentum becomes a constraint.")
    if from_hi is not None:
        if from_hi >= -1:
            body.append("It is sitting at its 52-week high" +
                        ("." if _is_index(sym) else ", where there is no overhead supply - "
                         "nobody who owns it is underwater and waiting to sell at break-even."))
        elif from_hi <= -20:
            tail = ("" if _is_index(sym) else
                    " - a long way back, and every level on the way up has trapped buyers "
                    "waiting to sell into strength")
            body.append(f"It sits {abs(from_hi):.0f}% below its 52-week high{tail}.")
        else:
            body.append(f"It sits {abs(from_hi):.0f}% off the 52-week high.")

    # 5. is today consistent with the trend, or against it?
    r1m = (st or {}).get("ret_1m")
    if r1m is not None:
        if (chg > 0) == (r1m > 0):
            body.append(f"Today extends the one-month trend ({r1m:+.1f}%) rather than fighting it.")
        else:
            body.append(f"Today cuts against the one-month trend ({r1m:+.1f}%), which makes it a "
                        f"potential inflection rather than a continuation.")

    # 6. the stance
    if abs(chg) >= 4 and vm and vm >= 1.8:
        body.append("**Read:** high-conviction repositioning. Find the catalyst before assuming "
                    "it mean-reverts.")
    elif abs(chg) >= 3 and vm and vm < 0.9:
        body.append("**Read:** a big number on thin volume. The base rate favours retracement.")
    else:
        body.append("**Read:** one data point. It matters if it repeats; it does not if it does not.")

    return " ".join(body)


def comment_on_movers():
    rows = []
    stats = _stats()
    with db.conn() as c:
        movers = c.execute(
            "SELECT symbol, asset_class, price, change_pct, MAX(snapshot_at) AS at "
            "FROM market_snapshots GROUP BY symbol"
        ).fetchall()
    for m in movers:
        chg = m["change_pct"]
        if chg is None:
            continue
        if abs(chg) < MOVE_THRESHOLD.get(m["asset_class"], 2.0):
            continue
        st = stats.get(m["symbol"])
        arrow = "▲" if chg > 0 else "▼"
        rows.append({
            "kind": "mover", "symbol": m["symbol"],
            "headline": f"{arrow} {m['symbol']} {chg:+.2f}% at {m['price']:,.2f}",
            "body": _explain_move(m["symbol"], chg, m["asset_class"], st),
            "severity": _sev(abs(chg), 4.0, 2.5),
        })
    return rows


# ------------------------------------------------------------- the patterns
def comment_on_patterns(since_minutes=90):
    rows = []
    stats = _stats()
    with db.conn() as c:
        pats = c.execute(
            "SELECT symbol, pattern, detail FROM patterns "
            "WHERE detected_at >= datetime('now', ?) ORDER BY detected_at DESC",
            (f"-{since_minutes} minutes",),
        ).fetchall()
    for p in pats:
        name, meaning, caveat = PATTERN_MEANING.get(
            p["pattern"], (p["pattern"], "", ""))
        st = stats.get(p["symbol"], {})
        ctx = ""
        if st.get("trend"):
            ctx = (f" Context for {p['symbol']}: currently {_trend_phrase(st['trend'])}, "
                   f"{abs(st.get('pct_from_hi') or 0):.0f}% off the 52-week high, "
                   f"one-month return {st.get('ret_1m') or 0:+.1f}%.")
        rows.append({
            "kind": "pattern", "symbol": p["symbol"],
            "headline": f"{p['symbol']}: {name} - {p['detail']}",
            "body": f"{meaning}{ctx} **Caveat:** {caveat}",
            "severity": "HIGH" if p["pattern"] in ("golden_cross", "death_cross",
                                                   "52wk_high", "52wk_low") else "MEDIUM",
        })
    return rows


# ---------------------------------------------------------------- the tape
def comment_on_breadth():
    """One paragraph on what the whole tape is saying."""
    with db.conn() as c:
        snaps = c.execute(
            "SELECT symbol, asset_class, change_pct, price, MAX(snapshot_at) "
            "FROM market_snapshots GROUP BY symbol"
        ).fetchall()
    eq = [r for r in snaps if r["asset_class"] in ("stock", "etf_fund")
          and r["change_pct"] is not None]
    if len(eq) < 4:
        return []
    up = sum(1 for r in eq if r["change_pct"] > 0)
    total = len(eq)
    pct_up = up / total * 100
    avg = sum(r["change_pct"] for r in eq) / total
    by = {r["symbol"]: r for r in snaps}

    if pct_up >= 75:
        tone, read = "broad risk-on", ("Participation is wide, which is the healthy kind of rally - "
                                       "gains spread across names rather than concentrated in two or three.")
    elif pct_up <= 25:
        tone, read = "broad risk-off", ("Selling is indiscriminate rather than name-specific, which "
                                        "usually points at a macro driver - rates, policy, or positioning - "
                                        "not at company fundamentals.")
    else:
        tone, read = "mixed and rotational", ("No single direction. Money is moving between names rather "
                                              "than into or out of equities as a whole, which is the "
                                              "signature of a rotation, not a trend.")

    body = [f"{up} of {total} tracked equities are higher ({pct_up:.0f}%), average move {avg:+.2f}%. "
            f"This is a {tone} tape. {read}"]

    vix = by.get("^VIX")
    if vix and vix["price"]:
        v = vix["price"]
        if v < 15:
            vread = ("complacent - options are cheap, which makes hedging inexpensive and "
                     "makes the market fragile to a surprise")
        elif v < 20:
            vread = "normal - no stress being priced"
        elif v < 30:
            vread = "elevated - real hedging demand, expect wider daily ranges"
        else:
            vread = "in panic territory, which historically has been closer to lows than to tops"
        body.append(f"VIX at {v:.1f} is {vread}.")

    tnx = by.get("^TNX")
    if tnx and tnx["price"]:
        y = tnx["price"]
        chg = tnx["change_pct"] or 0.0
        bp = y - y / (1 + chg / 100) if chg != -100 else 0.0
        body.append(
            f"The 10-year yield is {y:.2f}%, a move of {bp*100:+.0f} basis points today. Yields are the "
            f"denominator in every equity valuation: when they rise, the present value of "
            f"far-off earnings falls, which is why high-multiple growth reacts to the bond "
            f"market before it reacts to its own fundamentals."
        )

    return [{"kind": "breadth", "symbol": "MARKET",
             "headline": f"Tape: {tone} - {up}/{total} advancing, avg {avg:+.2f}%",
             "body": " ".join(body),
             "severity": "HIGH" if pct_up >= 80 or pct_up <= 20 else "MEDIUM"}]


# --------------------------------------------------------------- the crypto
def comment_on_crypto():
    rows = []
    with db.conn() as c:
        coins = c.execute(
            "SELECT coin, price, mcap, chg_1h, chg_24h, chg_7d, chg_30d, MAX(snapshot_at) "
            "FROM crypto_snapshots GROUP BY coin"
        ).fetchall()
    for c_ in coins:
        d24 = c_["chg_24h"] or 0
        if abs(d24) < 4:
            continue
        d7, d30, d1h = c_["chg_7d"] or 0, c_["chg_30d"] or 0, c_["chg_1h"] or 0
        name = c_["coin"].replace("-", " ").title()
        parts = [f"{name} is {d24:+.1f}% over 24h at ${c_['price']:,.2f}."]

        if abs(d1h) > abs(d24) * 0.5 and abs(d1h) > 1:
            parts.append(f"Most of that ({d1h:+.1f}%) happened in the last hour, so this is an "
                         f"impulse move on a specific catalyst rather than a slow drift.")
        if (d24 > 0) == (d7 > 0):
            parts.append(f"It runs with the weekly trend ({d7:+.1f}%), and the month sits at {d30:+.1f}%.")
        else:
            parts.append(f"It runs against the weekly trend ({d7:+.1f}%), so this is a reversal "
                         f"attempt rather than continuation. Month-to-date: {d30:+.1f}%.")

        if c_["coin"] == "bitcoin":
            parts.append("Bitcoin sets the beta for the whole complex - alts typically amplify its "
                         "direction by 1.5-3x, and crypto-levered equities (COIN, MSTR) track it "
                         "with leverage during the US session.")
        else:
            parts.append("Alt moves are usually derivative of bitcoin. Check whether BTC moved "
                         "first: if it did, this is beta, not a coin-specific story.")

        parts.append(f"Market cap ${(c_['mcap'] or 0)/1e9:,.1f}B.")
        rows.append({"kind": "crypto", "symbol": c_["coin"].upper(),
                     "headline": f"{name} {d24:+.1f}% (24h) @ ${c_['price']:,.2f}",
                     "body": " ".join(parts),
                     "severity": _sev(abs(d24), 10, 6)})
    return rows


# -------------------------------------------------------------- the congress
def comment_on_congress(days=7):
    rows = []
    with db.conn() as c:
        trades = c.execute(
            "SELECT politician, chamber, ticker, asset, tx_type, tx_date, amount, disclosed "
            "FROM congress_trades WHERE disclosed >= date('now', ?) "
            "ORDER BY disclosed DESC LIMIT 15", (f"-{days} days",),
        ).fetchall()
    for t in trades:
        rows.append({
            "kind": "congress", "symbol": t["politician"].split()[-1].upper(),
            "headline": f"{t['politician']} filed a transaction report ({t['disclosed']})",
            "body": (
                f"{t['politician']} ({t['chamber'].title()}) filed a Periodic Transaction Report "
                f"on {t['disclosed']}. Under the STOCK Act a member has up to 45 days to disclose "
                f"a trade, so the transaction itself happened at some point in the preceding six "
                f"weeks - whatever edge the trade may have carried is usually spent by the time "
                f"the filing appears. The line items (ticker, buy or sell, and the dollar range) "
                f"are in the filing PDF; the public index only publishes that a report was filed. "
                f"Amounts are always disclosed as broad ranges, and many filings cover a spouse's "
                f"account rather than the member's own. Read it as a sentiment datapoint, "
                f"not a trade to copy."),
            "severity": "MEDIUM",
        })
    return rows


# ------------------------------------------------------------------- driver
def generate_commentary():
    """Rebuild the commentary table from current state.

    Commentary describes how things stand right now, not a log of events, so
    each run replaces the previous one. Keeping only the current read is what
    stops the same mover appearing five times in the digest and the dashboard.
    """
    rows = (comment_on_breadth() + comment_on_movers() + comment_on_patterns()
            + comment_on_crypto() + comment_on_congress())
    with db.conn() as c:
        c.execute("DELETE FROM commentary")
    n = db.insert_many("commentary", rows)
    print(f"[commentary] {n} narrated items written")
    return n
