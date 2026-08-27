"""FinBot - run once or on a schedule.

Usage:
  python main.py run              # run every crawler once
  python main.py run news         # run one module
  python main.py schedule         # keep running on intervals
  python main.py report           # print latest findings
  python main.py dashboard        # build + open the HTML dashboard
"""
import sys

import db
from crawlers.news import crawl_news
from crawlers.congress import crawl_congress_trades
from crawlers.sec_13f import crawl_13f_filings
from crawlers.markets import crawl_markets
from crawlers.crypto import crawl_crypto
from analysis.patterns import detect_patterns
from analysis.insights import generate_insights
from analysis.commentary import generate_commentary

# Order matters: crawl raw data, detect patterns, then interpret. The insight
# and commentary passes read what the crawlers just wrote.
JOBS = {
    "news": crawl_news,
    "congress": crawl_congress_trades,
    "13f": crawl_13f_filings,
    "markets": crawl_markets,
    "crypto": crawl_crypto,
    "patterns": detect_patterns,
    "insights": generate_insights,
    "commentary": generate_commentary,
}


def run(only=None):
    db.init()
    for name, fn in JOBS.items():
        if only and name != only:
            continue
        print(f"=== {name} ===")
        try:
            fn()
        except Exception as ex:
            print(f"{name} crashed: {ex}")


def schedule():
    from apscheduler.schedulers.blocking import BlockingScheduler
    db.init()
    s = BlockingScheduler()
    s.add_job(crawl_news, "interval", minutes=30)
    s.add_job(crawl_crypto, "interval", minutes=15)
    s.add_job(crawl_markets, "cron", hour="14-21", minute=5)   # UTC market hours
    s.add_job(detect_patterns, "cron", hour=21, minute=15)     # after US close
    s.add_job(crawl_congress_trades, "cron", hour=12)
    s.add_job(crawl_13f_filings, "cron", day_of_week="mon", hour=13)
    print("Scheduler started. Ctrl+C to stop.")
    s.start()


def report():
    """Print the narrated view - the same content the dashboard renders."""
    import textwrap

    def wrap(text, indent="    "):
        clean = text.replace("**", "")
        return "\n".join(textwrap.fill(p, 96, initial_indent=indent,
                                       subsequent_indent=indent)
                         for p in clean.split("\n") if p.strip())

    with db.conn() as c:
        print("\n" + "=" * 100)
        print("  MARKET COMMENTARY")
        print("=" * 100)
        for r in c.execute(
            "SELECT * FROM commentary ORDER BY "
            "CASE severity WHEN 'HIGH' THEN 0 WHEN 'MEDIUM' THEN 1 ELSE 2 END, "
            "created_at DESC LIMIT 12"
        ):
            print(f"\n[{r['severity']}] {r['headline']}")
            print(wrap(r["body"]))

        print("\n" + "=" * 100)
        print("  NEWS - WITH STOCK IMPACT")
        print("=" * 100)
        for r in c.execute(
            "SELECT i.*, n.title, n.source, n.url FROM news_insights i "
            "JOIN news n ON n.id = i.news_id "
            "WHERE i.confidence != 'LOW' ORDER BY i.score DESC LIMIT 10"
        ):
            sign = {1: "BULLISH", -1: "BEARISH", 0: "VOLATILE"}[r["direction"]]
            print(f"\n[{r['confidence']} / {sign}] {r['title'][:88]}")
            print(f"    source: {r['source']}  |  tickers: {r['tickers'] or '-'}")
            print(wrap(r["narrative"]))
            print(wrap(f"SUGGESTION: {r['suggestion']}"))

        print("\n" + "=" * 100)
        print("  RECENT CONGRESS DISCLOSURES")
        print("=" * 100)
        for r in c.execute("SELECT * FROM congress_trades ORDER BY disclosed DESC LIMIT 8"):
            print(f"  {r['disclosed']}  {r['politician'][:24]:24} {r['tx_type'][:14]:14} "
                  f"{(r['ticker'] or '-'):6} {r['amount']}")
        print()


def hourly():
    """One cloud-friendly pass: crawl fast sources, detect, push to phone."""
    db.init()
    # 13f self-throttles to one check a day, so it is cheap to list here.
    for name in ("news", "crypto", "markets", "congress", "13f", "patterns",
                 "insights", "commentary"):
        try:
            JOBS[name]()
        except Exception as ex:
            print(f"{name} crashed: {ex}")
    # Written into site/ because that is the directory GitHub Pages publishes.
    from dashboard import build_dashboard
    try:
        build_dashboard("site/index.html")
    except Exception as ex:
        print(f"dashboard failed: {ex}")
    from notify import notify_digest
    notify_digest()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "hourly":
        hourly()
    elif cmd == "run":
        run(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "schedule":
        schedule()
    elif cmd == "report":
        report()
    elif cmd == "dashboard":
        from dashboard import build_dashboard
        path = build_dashboard("site/index.html")
        print(f"Dashboard written to {path}")
        if "--open" in sys.argv:
            import webbrowser
            webbrowser.open(f"file://{path}")
    else:
        print(__doc__)
