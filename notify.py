"""Push the digest to your phone.

What a phone notification can and cannot do
-------------------------------------------
A push notification is drawn by the phone's operating system, so FinBot cannot
give it custom fonts, colours, or a layout - that part is not up to the app.
What ntfy *does* support, and what this module uses:

  * Markdown       - bold, headings and lists render in the ntfy Android app and
                     the web app (iOS shows the plain text, which still reads fine)
  * Tags           - emoji, so the digest is scannable before you open it
  * Priority       - urgent digests break through Do Not Disturb, quiet ones do not
  * Click          - tapping the notification opens the dashboard
  * Actions        - buttons under the notification

So the notification is the *signal* - short, ranked, scannable - and the
dashboard it links to is the *substance*. Set DASHBOARD_URL to your GitHub Pages
address and the whole digest becomes one tap away from the full analysis.

Channels, by environment variable:
  ntfy.sh   -> NTFY_TOPIC (pick a long, unguessable topic and subscribe in the app)
  Telegram  -> TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID (Telegram renders full HTML)
"""
import datetime as dt
import hashlib
import os
import unicodedata

import requests

import config
import db
from analysis.plainspeak import plain_breadth, plain_event, plain_pattern

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "")
# Plain wording by default. Set NOTIFY_STYLE=expert for the analyst phrasing.
PLAIN_STYLE = os.environ.get("NOTIFY_STYLE", "plain").lower() != "expert"
# How far back a run looks for new material. Duplicate pushes are prevented by
# the `notified` table, not by this window, so it should be set comfortably
# wider than the schedule interval: a delayed or dropped run then still picks
# up whatever it missed instead of the item falling through the gap.
try:
    NOTIFY_WINDOW = max(5, int(os.environ.get("NOTIFY_WINDOW_MINUTES", "70")))
except ValueError:
    NOTIFY_WINDOW = 70

MAX_BODY = 3800   # ntfy caps the message body; stay comfortably under it

DIR_EMOJI = {1: "🟢", -1: "🔴", 0: "🟡"}
DIR_WORD = {1: "bullish", -1: "bearish", 0: "two-sided"}


# HTTP headers are latin-1 only, so a typographic dash or curly quote in the
# Title raises UnicodeEncodeError and the notification is dropped with nothing
# but a log line. Everything that goes in a header gets flattened first.
_TRANSLIT = {
    "\u2014": "-", "\u2013": "-", "\u2012": "-", "\u2212": "-",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2026": "...", "\u00a0": " ",
    "\u25b2": "^", "\u25bc": "v", "\u25c6": "*",
}


def _header_safe(text, limit=200):
    """Flatten a string to something an HTTP header can actually carry."""
    out = "".join(_TRANSLIT.get(ch, ch) for ch in str(text))
    out = unicodedata.normalize("NFKD", out)
    out = out.encode("ascii", "ignore").decode("ascii")
    out = " ".join(out.split())            # collapse newlines and runs of space
    return out[:limit]


# ------------------------------------------------------------------ sending
def send(title, body, tags=None, priority=3, click=None, actions=None):
    """Deliver to every configured channel. Returns True if any succeeded."""
    sent = False

    if NTFY_TOPIC:
        headers = {
            "Title": _header_safe(title),
            "User-Agent": _header_safe(config.USER_AGENT),
            "Markdown": "yes",                    # bold/headings render in-app
            "Priority": str(priority),
        }
        if tags:
            headers["Tags"] = _header_safe(",".join(tags))
        if click:
            headers["Click"] = _header_safe(click, 500)
        if actions:
            headers["Actions"] = _header_safe("; ".join(actions), 500)
        try:
            requests.post(
                f"{NTFY_SERVER}/{NTFY_TOPIC}",
                data=body.encode("utf-8"), headers=headers,
                timeout=config.REQUEST_TIMEOUT,
            ).raise_for_status()
            sent = True
        except Exception as ex:
            print(f"[notify] ntfy failed: {ex}")

    if TG_TOKEN and TG_CHAT:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={"chat_id": TG_CHAT, "text": f"*{title}*\n\n{body}",
                      "parse_mode": "Markdown", "disable_web_page_preview": True},
                timeout=config.REQUEST_TIMEOUT,
            ).raise_for_status()
            sent = True
        except Exception as ex:
            print(f"[notify] telegram failed: {ex}")

    if not sent:
        print("[notify] no channel configured (set NTFY_TOPIC or the Telegram vars)")
    return sent


# ------------------------------------------------------------- new-only gate
def _today():
    return dt.date.today().isoformat()


def _key(kind, text):
    return f"{kind}:{hashlib.sha1(text.encode('utf-8')).hexdigest()[:16]}"


def _unseen(kind, items, label):
    """Filter to what has not been pushed before.

    Commentary is rebuilt every run, so without this the same mover would be
    re-sent every hour. `label` picks the field that identifies an item.
    """
    with db.conn() as c:
        known = {r["key"] for r in c.execute("SELECT key FROM notified")}
    fresh, keys, batch = [], [], set()
    for it in items:
        k = _key(kind, label(it))
        # `batch` also guards within this run: patterns accumulate a row per
        # crawl, so the same signal can appear twice in one query result.
        if k in known or k in batch:
            continue
        batch.add(k)
        fresh.append(it)
        keys.append((k, kind))
    return fresh, keys


def _mark(keys):
    if not keys:
        return
    with db.conn() as c:
        c.executemany("INSERT OR IGNORE INTO notified (key, kind) VALUES (?,?)", keys)
        # keep the table from growing without bound
        c.execute("DELETE FROM notified WHERE sent_at < datetime('now', '-30 days')")


# ------------------------------------------------------------------- digest
def _first_sentences(text, n=2):
    """Trim a narrative down to what fits on a lock screen."""
    clean = " ".join(text.replace("**", "").replace("*", "").split("\n"))
    parts = clean.split(". ")
    out = ". ".join(parts[:n]).strip()
    return out + ("." if out and not out.endswith(".") else "")


def build_digest(since_minutes=None, mark=True):
    """The ranked brief: what changed, what it means, in that order.

    Only genuinely new items are included. The market read is always attached as
    framing, but on its own it never triggers a push - no news means no ping.
    """
    if since_minutes is None:
        since_minutes = NOTIFY_WINDOW
    blocks, tags, pending = [], set(), []
    urgent = False
    newsworthy = False

    with db.conn() as c:
        # --- the market read: one paragraph that frames everything else ---
        lead = c.execute(
            "SELECT headline, body FROM commentary WHERE kind='breadth' "
            "ORDER BY id DESC LIMIT 1").fetchone()
        if lead:
            if PLAIN_STYLE:
                eq = c.execute(
                    "SELECT change_pct FROM market_snapshots WHERE asset_class IN "
                    "('stock','etf_fund') AND change_pct IS NOT NULL "
                    "GROUP BY symbol").fetchall()
                vix = c.execute(
                    "SELECT price FROM market_snapshots WHERE symbol='^VIX' "
                    "ORDER BY id DESC LIMIT 1").fetchone()
                if eq:
                    chgs = [r["change_pct"] for r in eq]
                    up = sum(1 for v in chgs if v > 0)
                    blocks.append("**TODAY'S MARKET**\n" + plain_breadth(
                        up, len(chgs), sum(chgs) / len(chgs),
                        vix["price"] if vix else None))
            else:
                blocks.append(f"**{lead['headline']}**\n{_first_sentences(lead['body'], 3)}")
            tags.add("chart_with_upwards_trend")

        # --- the stories that actually move something ---
        # Stories that resolved to a ticker rank first: a named company is the
        # actionable case, and a lock screen has room for about five lines.
        stories = c.execute("""
            SELECT i.direction, i.confidence, i.tickers, i.event_labels,
                   i.suggestion, n.title, n.source
            FROM news_insights i JOIN news n ON n.id = i.news_id
            WHERE i.confidence = 'HIGH' AND n.fetched_at >= datetime('now', ?)
            ORDER BY (i.tickers != '') DESC, i.score DESC LIMIT 5
        """, (f"-{since_minutes} minutes",)).fetchall()
        # Keyed on the headline, which is stable for the life of the story.
        stories, keys = _unseen("story", [dict(r) for r in stories], lambda r: r["title"])
        pending += keys
        if stories:
            newsworthy = True
            lines = ["**📰 STORIES THAT MOVE SOMETHING**"]
            for s in stories:
                dot = DIR_EMOJI.get(s["direction"], "🟡")
                lines.append(f"{dot} **{s['title'][:110]}**")
                label = (s["event_labels"] or "").split(",")[0]
                if PLAIN_STYLE:
                    # Say what the event means, not what a trader should do.
                    meaning = plain_event(label) if label else ""
                    who = f"`{s['tickers']}` — " if s["tickers"] else ""
                    lines.append(f"   {who}_{meaning or 'No plain summary available.'}_")
                elif s["tickers"]:
                    lines.append(f"   `{s['tickers']}` — _{_first_sentences(s['suggestion'], 1)}_")
                else:
                    lines.append(f"   _{(label or 'unclassified').lower()} — no tracked ticker named_")
                if s["direction"] > 0:
                    tags.add("green_circle")
                elif s["direction"] < 0:
                    tags.add("red_circle")
            blocks.append("\n".join(lines))
            urgent = True

        # --- patterns: discrete, high-signal events ---
        pats = c.execute(
            "SELECT symbol, pattern, detail FROM patterns "
            "WHERE detected_at >= datetime('now', ?)",
            (f"-{since_minutes} minutes",)).fetchall()
        # Keyed without `detail`: an RSI of 20 and 21 the next hour is the same
        # signal, and should notify once a day, not every run.
        pats, keys = _unseen("pattern", [dict(r) for r in pats],
                             lambda r: f"{r['symbol']}|{r['pattern']}|{_today()}")
        pending += keys
        if pats:
            newsworthy = True
            if PLAIN_STYLE:
                blocks.append("**📈 SIGNALS WORTH KNOWING**\n" + "\n".join(
                    f"• **{p['symbol']}** {plain_pattern(p['pattern'])}" for p in pats))
            else:
                blocks.append("**📈 PATTERNS**\n" + "\n".join(
                    f"• `{p['symbol']}` {p['pattern'].replace('_', ' ')} — {p['detail']}"
                    for p in pats))
            tags.add("bar_chart")
            if any(p["pattern"] in ("golden_cross", "death_cross") for p in pats):
                urgent = True

        # --- movers, each with the one line that explains the number ---
        movers = c.execute("""
            SELECT symbol, severity, headline, body FROM commentary
            WHERE kind='mover' AND severity IN ('HIGH','MEDIUM')
              AND created_at >= datetime('now', ?)
            ORDER BY CASE severity WHEN 'HIGH' THEN 0 ELSE 1 END LIMIT 5
        """, (f"-{since_minutes} minutes",)).fetchall()
        # Keyed on symbol + day + severity, not the headline: the headline
        # carries the live price, which drifts every run and would re-notify
        # the same mover hourly. An escalation to HIGH does notify again.
        movers, keys = _unseen("mover", [dict(r) for r in movers],
                               lambda r: f"{r['symbol']}|{_today()}|{r['severity']}")
        pending += keys
        if movers:
            newsworthy = True
            lines = ["**⚡ BIG MOVES TODAY**" if PLAIN_STYLE else "**⚡ MOVERS**"]
            for m in movers:
                lines.append(f"**{m['headline']}**")
                lines.append(f"   {_first_sentences(m['body'], 2)}")
            blocks.append("\n".join(lines))

        # --- crypto ---
        cryptos = c.execute("""
            SELECT symbol, severity, headline, body FROM commentary
            WHERE kind='crypto' AND created_at >= datetime('now', ?) LIMIT 3
        """, (f"-{since_minutes} minutes",)).fetchall()
        cryptos, keys = _unseen("crypto", [dict(r) for r in cryptos],
                                lambda r: f"{r['symbol']}|{_today()}|{r['severity']}")
        pending += keys
        if cryptos:
            newsworthy = True
            lines = ["**₿ CRYPTO**"]
            for x in cryptos:
                lines.append(f"**{x['headline']}**")
                lines.append(f"   {_first_sentences(x['body'], 2)}")
            blocks.append("\n".join(lines))
            tags.add("coin")

        # --- congress ---
        trades = c.execute(
            "SELECT politician, disclosed FROM congress_trades "
            "WHERE disclosed >= date('now', '-3 days') ORDER BY disclosed DESC LIMIT 5"
        ).fetchall()
        trades, keys = _unseen("congress", [dict(r) for r in trades],
                               lambda r: f"{r['politician']}{r['disclosed']}")
        pending += keys
        if trades:
            newsworthy = True
            blocks.append("**🏛 NEW CONGRESS FILINGS**\n" + "\n".join(
                f"• {t['politician']} — transaction report filed {t['disclosed']}"
                for t in trades))
            tags.add("classical_building")

    # The market read alone is not worth a notification.
    if not newsworthy:
        return "", [], 3
    if mark:
        _mark(pending)

    if DASHBOARD_URL:
        blocks.append(f"[Open the full dashboard →]({DASHBOARD_URL})")

    body = "\n\n".join(blocks)
    if len(body) > MAX_BODY:
        body = body[:MAX_BODY].rsplit("\n", 1)[0] + "\n\n_…trimmed. Full analysis on the dashboard._"

    return body, sorted(tags) or ["chart"], (4 if urgent else 3)


def _title():
    """Name the digest after the single most important thing in it."""
    with db.conn() as c:
        top = c.execute("""
            SELECT n.title, i.direction, i.tickers FROM news_insights i
            JOIN news n ON n.id = i.news_id
            WHERE i.confidence='HIGH' ORDER BY i.score DESC LIMIT 1
        """).fetchone()
        lead = c.execute("SELECT headline FROM commentary WHERE kind='breadth' "
                         "ORDER BY id DESC LIMIT 1").fetchone()
    if top and top["tickers"]:
        return f"FinBot: {top['tickers'].split(',')[0]} {DIR_WORD.get(top['direction'], '')}".strip()
    if lead:
        return f"FinBot: {lead['headline'][:60]}"
    return "FinBot digest"


def notify_digest(since_minutes=None):
    body, tags, priority = build_digest(since_minutes)
    if not body:
        print("[notify] nothing new in the last "
              f"{since_minutes or NOTIFY_WINDOW} minutes, skipping push")
        return False

    actions = []
    if DASHBOARD_URL:
        actions.append(f"view, Open dashboard, {DASHBOARD_URL}, clear=true")

    return send(_title(), body, tags=tags, priority=priority,
                click=DASHBOARD_URL or None, actions=actions or None)
