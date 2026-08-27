"""Push notifications to your phone.

Supports two free channels, controlled by environment variables:

  ntfy.sh   -> set NTFY_TOPIC (pick a long, unguessable topic name,
               e.g. finbot-a8x3k29q, and subscribe to it in the ntfy app)
  Telegram  -> set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
               (create a bot with @BotFather, message it once, get your
               chat id from https://api.telegram.org/bot<TOKEN>/getUpdates)
"""
import os

import requests

import config
import db

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")


def send(title, body):
    sent = False
    if NTFY_TOPIC:
        try:
            requests.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                data=body.encode("utf-8"),
                headers={"Title": title, "User-Agent": config.USER_AGENT},
                timeout=config.REQUEST_TIMEOUT,
            ).raise_for_status()
            sent = True
        except Exception as ex:
            print(f"[notify] ntfy failed: {ex}")
    if TG_TOKEN and TG_CHAT:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={"chat_id": TG_CHAT, "text": f"{title}\n\n{body}"},
                timeout=config.REQUEST_TIMEOUT,
            ).raise_for_status()
            sent = True
        except Exception as ex:
            print(f"[notify] telegram failed: {ex}")
    if not sent:
        print("[notify] no channel configured (set NTFY_TOPIC or Telegram vars)")
    return sent


def build_digest(since_minutes=70):
    """Summarize what's new in the last crawl window."""
    parts = []
    with db.conn() as c:
        pats = c.execute(
            "SELECT symbol, pattern, detail FROM patterns "
            "WHERE detected_at >= datetime('now', ?)",
            (f"-{since_minutes} minutes",),
        ).fetchall()
        if pats:
            parts.append("PATTERNS:\n" + "\n".join(
                f"• {r['symbol']}: {r['pattern']} ({r['detail']})" for r in pats))

        trades = c.execute(
            "SELECT politician, tx_type, ticker, tx_date, amount "
            "FROM congress_trades WHERE disclosed >= date('now', '-2 days') "
            "ORDER BY disclosed DESC LIMIT 10",
        ).fetchall()
        if trades:
            parts.append("NEW CONGRESS DISCLOSURES:\n" + "\n".join(
                f"• {r['politician']}: {r['tx_type']} {r['ticker']} "
                f"{r['amount']} ({r['tx_date']})" for r in trades))

        movers = c.execute(
            "SELECT symbol, change_pct FROM market_snapshots "
            "WHERE snapshot_at >= datetime('now', ?) "
            "AND ABS(change_pct) >= 2 ORDER BY ABS(change_pct) DESC LIMIT 8",
            (f"-{since_minutes} minutes",),
        ).fetchall()
        if movers:
            parts.append("BIG MOVERS (>2%):\n" + "\n".join(
                f"• {r['symbol']}: {r['change_pct']:+.1f}%" for r in movers))

        cryptos = c.execute(
            "SELECT coin, price, chg_24h FROM crypto_snapshots "
            "WHERE snapshot_at >= datetime('now', ?) "
            "AND ABS(COALESCE(chg_24h,0)) >= 5",
            (f"-{since_minutes} minutes",),
        ).fetchall()
        if cryptos:
            parts.append("CRYPTO (>5% 24h):\n" + "\n".join(
                f"• {r['coin']}: ${r['price']:,.0f} ({r['chg_24h']:+.1f}%)"
                for r in cryptos))

        heads = c.execute(
            "SELECT source, title FROM news "
            "WHERE fetched_at >= datetime('now', ?) LIMIT 5",
            (f"-{since_minutes} minutes",),
        ).fetchall()
        if heads:
            parts.append("TOP NEW HEADLINES:\n" + "\n".join(
                f"• [{r['source']}] {r['title'][:80]}" for r in heads))

    return "\n\n".join(parts) if parts else ""


def notify_digest():
    body = build_digest()
    if body:
        send("FinBot hourly digest", body[:3800])
    else:
        print("[notify] nothing new this hour, skipping push")
