"""Turn raw headlines into an explained view of which stocks they move, and why.

The engine is deliberately rule-based and offline: it runs in ~50ms for a full
news batch, costs nothing, needs no API key, and its reasoning is fully
auditable - every claim it makes traces back to a phrase in
`config.EVENT_LEXICON` or an edge in `config.PEER_GRAPH`.

Pipeline per headline:
  1. resolve  - which companies are actually named (alias matching)
  2. classify - which known market events the text describes
  3. score    - net direction, magnitude, and confidence
  4. ripple   - propagate through the peer / supply-chain graph
  5. narrate  - write the plain-English "so what" a human can act on
"""
import re

import config
import db

# Bump when the lexicon, peer graph, or scoring changes. Stored alongside the
# results so a cached database (GitHub Actions restores one between runs)
# re-analyses its backlog against the new engine instead of serving stale reads.
ENGINE_VERSION = 4

# Matched before the lexicon so "failed to beat estimates" is not read as a beat.
NEGATIONS = ("fails to", "failed to", "fall short of", "falls short of",
             "misses out on", "no longer", "unlikely to", "denies", "denied",
             "rules out", "walks away from", "not expected to")

# Sources whose headlines are opinion/analysis rather than reported fact.
SOFT_SOURCES = ("seeking_alpha_news",)

TICKER_RE = re.compile(r"\(([A-Z]{1,5})\)|\bNASDAQ:\s*([A-Z]{1,5})\b|\bNYSE:\s*([A-Z]{1,5})\b")

# Phrases are matched on word boundaries, never as substrings - otherwise
# "fine" fires on "fine-tuning" and "strike" fires on "striking".
_LEXICON_RE = {
    phrase: re.compile(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])")
    for phrase in config.EVENT_LEXICON
}


# ------------------------------------------------------------------ resolve
def resolve_tickers(text):
    """Find companies named in the text. Returns {ticker: matched_alias}."""
    low = f" {text.lower()} "
    hits = {}

    # 1. explicit ticker notation: "Nvidia (NVDA)", "NASDAQ: AAPL"
    for m in TICKER_RE.finditer(text):
        sym = next(g for g in m.groups() if g)
        if sym in config.TICKER_ALIASES or len(sym) >= 2:
            hits[sym] = sym

    # 2. company aliases, longest-first so "advanced micro devices" beats "amd"
    for ticker, aliases in config.TICKER_ALIASES.items():
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = r"(?<![a-z0-9])" + re.escape(alias.strip()) + r"(?![a-z0-9])"
            if re.search(pattern, low):
                hits.setdefault(ticker, alias.strip())
                break
    return hits


def resolve_proxies(text, already):
    """Implied exposure - mentions that touch a company without being about it."""
    low = f" {text.lower()} "
    hits = {}
    for ticker, aliases in config.PROXY_ALIASES.items():
        if ticker in already:
            continue
        for alias in aliases:
            if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", low):
                hits[ticker] = alias
                break
    return hits


# ----------------------------------------------------------------- classify
def classify_events(text, weight=1.0):
    """Match the text against the event lexicon. Returns a list of event dicts.

    `weight` scales the strength - callers pass a lower weight for the article
    summary than for the headline, because a phrase buried in body copy is much
    weaker evidence than the same phrase in the headline.
    """
    low = text.lower()
    events = []
    for phrase, (label, direction, strength, mechanism) in config.EVENT_LEXICON.items():
        m = _LEXICON_RE[phrase].search(low)
        if not m:
            continue
        window = low[max(0, m.start() - 40):m.start()]   # look just before the phrase
        flipped = any(neg in window for neg in NEGATIONS)
        events.append({
            "label": label,
            "phrase": phrase,
            "direction": -direction if flipped else direction,
            "strength": strength * (0.85 if flipped else 1.0) * weight,
            "mechanism": mechanism,
            "negated": flipped,
        })
    # keep the strongest reading of each event label
    best = {}
    for e in events:
        if e["label"] not in best or e["strength"] > best[e["label"]]["strength"]:
            best[e["label"]] = e
    return sorted(best.values(), key=lambda e: -e["strength"])


# -------------------------------------------------------------------- score
def score_events(events, in_headline_bonus=0.0):
    """Collapse events into (direction, magnitude 0-1)."""
    if not events:
        return 0, 0.0
    signed = sum(e["direction"] * e["strength"] for e in events)
    total = sum(e["strength"] for e in events)
    # magnitude: strongest single event, plus a small boost for corroborating events
    top = max(e["strength"] for e in events)
    magnitude = min(1.0, top + 0.08 * (len(events) - 1) + in_headline_bonus)
    if total == 0:
        return 0, 0.0
    direction = 1 if signed > 0.15 * total else (-1 if signed < -0.15 * total else 0)
    return direction, round(magnitude, 3)


def confidence_band(magnitude, n_tickers, n_events, soft_source, crypto_no_equity=False):
    score = magnitude
    if n_tickers:
        score += 0.10          # a specifically named company is far more actionable
    if n_events >= 2:
        score += 0.05
    if soft_source:
        score -= 0.10
    if crypto_no_equity:
        # A token story with no listed name attached is context, not an equity call.
        score = min(score, config.IMPACT_HIGH - 0.01)
    if score >= config.IMPACT_HIGH:
        return "HIGH", round(min(score, 1.0), 3)
    if score >= config.IMPACT_MEDIUM:
        return "MEDIUM", round(score, 3)
    return "LOW", round(max(score, 0.0), 3)


# ------------------------------------------------------------------- ripple
def _peer_reason(relation, source_ticker):
    """Phrase the relationship without repeating the ticker it already names."""
    if source_ticker in relation:
        return relation
    return f"{relation} of {source_ticker}"


def build_impacts(tickers, proxies, events, direction, magnitude):
    """Direct hits + implied exposure + peer ripple + macro sector baskets."""
    impacts = []
    seen = set()

    for ticker, alias in tickers.items():
        impacts.append({
            "ticker": ticker, "kind": "direct", "direction": direction,
            "magnitude": magnitude,
            "reason": f"named directly in the story (\"{alias}\")",
        })
        seen.add(ticker)

    for ticker, alias in proxies.items():
        if ticker in seen:
            continue
        impacts.append({
            "ticker": ticker, "kind": "indirect", "direction": direction,
            "magnitude": round(magnitude * config.PROXY_WEIGHT, 3),
            "reason": f"implied exposure via \"{alias}\" - not the subject of the story",
        })
        seen.add(ticker)

    # second order: who else does this touch, and through what relationship
    if direction != 0:
        for ticker in list(tickers):
            for peer, relation, coef in config.PEER_GRAPH.get(ticker, []):
                if peer in seen:
                    continue
                # competitors move opposite on company-specific wins; suppliers move with
                opposed = "rival" in relation or "competitor" in relation or "peer" in relation
                pdir = -direction if opposed and magnitude >= 0.5 else direction
                impacts.append({
                    "ticker": peer, "kind": "peer", "direction": pdir,
                    "magnitude": round(magnitude * coef, 3),
                    "reason": _peer_reason(relation, ticker),
                })
                seen.add(peer)

    # macro stories with no single company: hit the sector baskets
    for e in events:
        for basket, bdir, why in config.MACRO_IMPACTS.get(e["label"], []):
            for ticker in config.SECTOR_BASKETS.get(basket, [])[:4]:
                if ticker in seen:
                    continue
                impacts.append({
                    "ticker": ticker, "kind": "sector", "direction": bdir or direction,
                    "magnitude": round(e["strength"] * 0.7, 3),
                    "reason": f"{basket.replace('_', ' ')}: {why}",
                })
                seen.add(ticker)

    return sorted(impacts, key=lambda i: (-i["magnitude"], i["ticker"]))[:8]


# ------------------------------------------------------------------ narrate
ARROW = {1: "upward", -1: "downward", 0: "two-sided"}
VERB = {1: "supports", -1: "pressures", 0: "adds volatility to"}


def _size_words(magnitude):
    if magnitude >= 0.75:
        return "a large", "This is the kind of headline that reprices a stock in a single session"
    if magnitude >= 0.5:
        return "a meaningful", "Expect a visible move rather than a drift"
    if magnitude >= 0.3:
        return "a modest", "More likely to shade sentiment than to drive the tape"
    return "a marginal", "Background colour rather than a tradable catalyst"


def narrate(title, tickers, events, direction, magnitude, impacts, price_ctx,
            is_crypto=False):
    """Write the paragraph a human actually reads."""
    if not events and not tickers:
        return ("No named company or recognised market event in this headline, so there is "
                "no clean read-through to a specific ticker. Filed as context.")

    lines = []
    size, size_note = _size_words(magnitude)

    # 1. what happened
    if events:
        ev = events[0]
        others = [e["label"] for e in events[1:3]]
        head = f"**What this is:** {ev['label'].lower()}"
        if others:
            head += f" (also reads as {', '.join(o.lower() for o in others)})"
        lines.append(head + ".")
        lines.append(f"**Mechanism:** {ev['mechanism']}")
        if ev["negated"]:
            lines.append("*Note: the phrasing is negated, so the usual sign of this event is inverted.*")
    else:
        lines.append("**What this is:** company news with no standard event pattern matched.")

    if is_crypto:
        lines.append("*This is a crypto-native story. Equity mechanics like earnings per share "
                     "do not apply directly - the read-through to listed markets runs through "
                     "crypto-levered equities (COIN, MSTR) and overall risk appetite.*")

    # 2. who it hits
    direct = [i for i in impacts if i["kind"] == "direct"]
    indirect = [i for i in impacts if i["kind"] == "indirect"]
    peers = [i for i in impacts if i["kind"] == "peer"]
    sector = [i for i in impacts if i["kind"] == "sector"]

    if direct:
        names = ", ".join(i["ticker"] for i in direct)
        lines.append(
            f"**Direct read-through:** {names} - {size} {ARROW[direction]} skew. "
            f"{size_note}."
        )
    if indirect:
        names = ", ".join(i["ticker"] for i in indirect)
        lines.append(
            f"**Indirect exposure:** {names} - mentioned only by association, so treat the "
            f"read-through as weak. Worth a look, not a position."
        )
    if peers:
        bits = [f"{i['ticker']} ({'+' if i['direction'] > 0 else '-' if i['direction'] < 0 else '~'}, {i['reason']})"
                for i in peers[:4]]
        lines.append("**Ripple effects:** " + "; ".join(bits) + ".")
    if sector and not direct:
        bits = [f"{i['ticker']}" for i in sector[:5]]
        lines.append(
            f"**Macro read-through:** no single company named, so this {VERB[direction]} "
            f"the basket - {', '.join(bits)}. " + (sector[0]["reason"].split(': ', 1)[-1].capitalize() + ".")
        )

    # 3. cross-check against what the tape is already doing
    for tkr, ctx in price_ctx.items():
        if not any(i["ticker"] == tkr for i in direct):
            continue
        chg = ctx["change_pct"]
        if direction > 0 and chg >= 2:
            lines.append(f"**Already moving:** {tkr} is up {chg:+.1f}% today - much of this may already be in the price. Chasing it here is the expensive entry.")
        elif direction < 0 and chg <= -2:
            lines.append(f"**Already moving:** {tkr} is down {chg:+.1f}% today - the market has begun discounting this. The question is whether it overshoots.")
        elif direction != 0 and abs(chg) < 0.5:
            lines.append(f"**Not yet reflected:** {tkr} is only {chg:+.1f}% today despite this news. Either the market disagrees with the read, or it has not caught up.")

    # 4. what to watch
    watch = _watch_for(events, direct)
    if watch:
        lines.append(f"**Watch next:** {watch}")

    return "\n".join(lines)


def _watch_for(events, direct):
    labels = {e["label"] for e in events}
    tkr = direct[0]["ticker"] if direct else "the sector"
    if "Earnings beat" in labels or "Earnings miss" in labels:
        return f"the guidance line, not the headline EPS - {tkr} trades off next quarter, not last."
    if "Guidance cut" in labels or "Guidance raise" in labels:
        return f"whether analysts follow with estimate revisions over the next 48h; that is what actually moves {tkr}."
    if "M&A" in labels:
        return "the spread between the offer price and where the target trades - it prices the market's odds the deal closes."
    if "Export controls" in labels:
        return "company disclosure of the revenue share exposed to the restricted region."
    if "Rate cut" in labels or "Rate hike" in labels or "FOMC" in labels:
        return "the 2-year yield and the fed funds futures curve - equities are following those, not the headline."
    if "CPI print" in labels:
        return "core month-over-month, not the headline year-over-year figure. That is what the Fed reacts to."
    if "FDA approval" in labels or "FDA rejection" in labels or "Trial data" in labels:
        return "the label language and the addressable-patient math, which decide the real revenue number."
    if "Layoffs" in labels:
        return "whether the cuts are framed as efficiency (bullish) or as demand weakness (bearish)."
    if "Short report" in labels:
        return "management's rebuttal within 24-48h; silence is usually read as confirmation."
    if "Analyst upgrade" in labels or "Analyst downgrade" in labels:
        return "whether other desks follow - a lone rating change rarely holds a move past a day."
    if direct:
        return f"volume on {tkr}. A move on light volume tends to fade; on 2x+ volume it tends to trend."
    return ""


# --------------------------------------------------------------- suggestion
def suggestion(direction, magnitude, band, impacts):
    """A stance, stated as a stance - never a directive to trade."""
    if band == "LOW" or magnitude < config.IMPACT_MEDIUM:
        return "No action implied. Informational only."
    if not impacts:
        # A recognised event with no company resolved: say so rather than
        # inventing a "sector" that was never identified.
        d = {1: "positive", -1: "negative", 0: "two-sided"}[direction]
        return (f"A {d} event, but FinBot could not resolve it to a tracked ticker - the "
                f"company is either outside the watchlist or not named in a form it "
                f"recognises. Read the source before drawing a conclusion.")
    tkrs = ", ".join(i["ticker"] for i in impacts[:3])
    if direction > 0 and band == "HIGH":
        return (f"Bullish skew on {tkrs}. If you already hold it, this supports the thesis; "
                f"if you don't, wait for the opening gap to fill rather than paying the news premium.")
    if direction > 0:
        return f"Mildly constructive for {tkrs}. Not a standalone reason to buy - treat it as one input."
    if direction < 0 and band == "HIGH":
        return (f"Bearish skew on {tkrs}. Worth checking position size and stop levels before the open; "
                f"high-magnitude negatives tend to see follow-through selling on day two.")
    if direction < 0:
        return f"Mildly negative for {tkrs}. Watch for confirmation before acting on it alone."
    return (f"Direction is genuinely two-sided for {tkrs} - this is a volatility event, not a directional one. "
            f"Sizing matters more than picking a side.")


# ------------------------------------------------------------------- driver
def _price_context():
    """Latest close/change for every symbol we have a snapshot for."""
    ctx = {}
    with db.conn() as c:
        for r in c.execute(
            "SELECT symbol, price, change_pct, volume, MAX(snapshot_at) "
            "FROM market_snapshots GROUP BY symbol"
        ):
            ctx[r["symbol"]] = {"price": r["price"], "change_pct": r["change_pct"] or 0.0,
                                "volume": r["volume"]}
    return ctx


SUMMARY_WEIGHT = 0.55   # a phrase in body copy is much weaker evidence than in the headline


def analyse(title, summary="", source=""):
    """Analyse one headline. Pure function - handy for testing."""
    summary = summary or ""
    text = f"{title}. {summary}"
    is_crypto = source in config.CRYPTO_SOURCES

    # Companies named in the headline are the story; ones only in the body are context.
    headline_tickers = resolve_tickers(title)
    tickers = headline_tickers or resolve_tickers(text)
    proxies = resolve_proxies(text, tickers)

    # Merge headline and summary events, keeping the higher-weighted reading.
    events = {e["label"]: e for e in classify_events(summary, SUMMARY_WEIGHT)}
    for e in classify_events(title, 1.0):
        events[e["label"]] = e
    events = sorted(events.values(), key=lambda e: -e["strength"])

    bonus = 0.08 if any(e["strength"] >= 0.5 for e in events) else 0.0
    direction, magnitude = score_events(events, bonus)
    band, score = confidence_band(magnitude, len(headline_tickers), len(events),
                                  source in SOFT_SOURCES,
                                  crypto_no_equity=is_crypto and not tickers)
    impacts = build_impacts(tickers, proxies, events, direction, magnitude)
    return {
        "tickers": tickers, "proxies": proxies, "events": events, "direction": direction,
        "magnitude": magnitude, "band": band, "score": score, "impacts": impacts,
        "is_crypto": is_crypto,
    }


def _stale_engine():
    """True when stored insights were produced by an older engine version."""
    with db.conn() as c:
        row = c.execute(
            "SELECT value FROM meta WHERE key = 'insights_engine_version'"
        ).fetchone()
    return (int(row["value"]) if row else 0) != ENGINE_VERSION


def _mark_engine():
    with db.conn() as c:
        c.execute("INSERT INTO meta (key, value) VALUES ('insights_engine_version', ?) "
                  "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                  (str(ENGINE_VERSION),))


def generate_insights(limit=None, force=False):
    """Analyse un-analysed headlines and store the results.

    Rebuilds everything when the engine version has moved on, so a lexicon fix
    takes effect on the existing backlog rather than only on future stories.
    """
    limit = limit or config.MAX_INSIGHT_NEWS
    if force or _stale_engine():
        with db.conn() as c:
            c.execute("DELETE FROM news_insights")
        print(f"[insights] engine v{ENGINE_VERSION}: re-analysing the backlog")

    price_ctx = _price_context()
    rows = []
    with db.conn() as c:
        news = c.execute(
            "SELECT n.id, n.source, n.title, n.summary, n.url FROM news n "
            "LEFT JOIN news_insights i ON i.news_id = n.id "
            "WHERE i.id IS NULL ORDER BY n.id DESC LIMIT ?", (limit,)
        ).fetchall()

    for n in news:
        a = analyse(n["title"], n["summary"] or "", n["source"])
        ctx = {t: price_ctx[t] for t in a["tickers"] if t in price_ctx}
        rows.append({
            "news_id": n["id"],
            "tickers": ",".join(a["tickers"]) or "",
            "event_labels": ",".join(e["label"] for e in a["events"]) or "",
            "direction": a["direction"],
            "magnitude": a["magnitude"],
            "confidence": a["band"],
            "score": a["score"],
            "impacts": db.dumps(a["impacts"]),
            "narrative": narrate(n["title"], a["tickers"], a["events"], a["direction"],
                                 a["magnitude"], a["impacts"], ctx, a["is_crypto"]),
            "suggestion": suggestion(a["direction"], a["magnitude"], a["band"], a["impacts"]),
        })

    n_ins = db.insert_many("news_insights", rows)
    _mark_engine()
    high = sum(1 for r in rows if r["confidence"] == "HIGH")
    print(f"[insights] analysed {len(rows)} headlines, stored {n_ins} ({high} high-conviction)")
    return n_ins
