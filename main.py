"""FinBot - run once or on a schedule.

Usage:
  python main.py run              # run every crawler once
  python main.py run news         # run one module
  python main.py schedule         # keep running on intervals
  python main.py report           # print latest findings
"""
import sys

import db
from crawlers.news import crawl_news
from crawlers.congress import crawl_congress_trades
from crawlers.sec_13f import crawl_13f_filings
from crawlers.markets import crawl_markets
from crawlers.crypto import crawl_crypto
from analysis.patterns import detect_patterns

JOBS = {
    "news": crawl_news,
    "congress": crawl_congress_trades,
    "13f": crawl_13f_filings,
    "markets": crawl_markets,
    "crypto": crawl_crypto,
    "patterns": detect_patterns,
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
    with db.conn() as c:
        print("\n--- Latest patterns ---")
        for r in c.execute("SELECT * FROM patterns ORDER BY detected_at DESC LIMIT 15"):
            print(f"{r['symbol']:8} {r['pattern']:16} {r['detail']}")
        print("\n--- Latest congress trades ---")
        for r in c.execute("SELECT * FROM congress_trades ORDER BY tx_date DESC LIMIT 10"):
            print(f"{r['tx_date']} {r['politician'][:24]:24} {r['tx_type']:16} "
                  f"{r['ticker']:6} {r['amount']}")
        print("\n--- Latest headlines ---")
        for r in c.execute("SELECT * FROM news ORDER BY id DESC LIMIT 10"):
            print(f"[{r['source']}] {r['title'][:90]}")


def hourly():
    """One cloud-friendly pass: crawl fast sources, detect, push to phone."""
    db.init()
    for name in ("news", "crypto", "markets", "congress", "patterns"):
        try:
            JOBS[name]()
        except Exception as ex:
            print(f"{name} crashed: {ex}")
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
    else:
        print(__doc__)
