# FinBot

A modular bot that gathers business/finance/tech news, congressional and institutional portfolios, market data, and detects common technical patterns.

## Data sources (all public / official)

| Module | Source | What it gets |
|---|---|---|
| news | RSS feeds (CNBC, Yahoo, MarketWatch, TechCrunch, CoinDesk...) | Headlines + summaries |
| congress | STOCK Act disclosure datasets (Senate/House Stock Watcher) | Trades by Pelosi & other tracked politicians |
| 13f | SEC EDGAR | Quarterly 13F portfolio filings for Berkshire, ARK, Bridgewater, Tiger Global, etc. |
| markets | yfinance | Stocks, indexes, ETFs/funds, bond yields |
| crypto | CoinGecko free API | Price, market cap, 1h/24h/7d/30d changes |
| patterns | computed | Golden/death cross, RSI extremes, 52-wk breakouts, volume spikes |

## Setup

```bash
cd finbot
pip install -r requirements.txt
# Edit config.py: set your contact email in USER_AGENT (required by SEC),
# and adjust tracked tickers, politicians, and funds.
python main.py run        # run everything once
python main.py report     # view results
python main.py schedule   # run continuously on intervals
```

Everything is stored in `finbot.db` (SQLite).

## Extending it

- Add tickers/coins/funds/politicians in `config.py`
- Add a new crawler in `crawlers/` and register it in `main.py`'s `JOBS` dict
- 13F filings are indexed with direct document URLs; parse the XML info tables if you want per-holding data
- Add alerting (email/Telegram) by hooking into `detect_patterns` results

## Free cloud + hourly phone notifications

**Option A - GitHub Actions (recommended, zero servers):**
1. Push this folder to a private GitHub repo (the workflow is already in `.github/workflows/finbot.yml`).
2. Install the **ntfy** app on your phone, subscribe to a long random topic name (e.g. `finbot-a8x3k29q`).
3. In the repo: Settings → Secrets and variables → Actions → add secret `NTFY_TOPIC` with that name. (Or add `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` instead.)
4. Done. It crawls every hour and pushes a digest of new patterns, big movers, crypto swings, fresh congress disclosures, and headlines. Nothing new = no ping.
5. Test it: Actions tab → "FinBot hourly" → Run workflow.

Notes: Actions cron can drift 5-15 min under load; private-repo free tier gives 2,000 min/month (this uses ~1-2 min/run, well within it). The SQLite DB is persisted between runs via the cache action.

**Option B - a free always-on VM** (Oracle Cloud Always Free or GCP e2-micro): clone the repo, `pip install -r requirements.txt`, set the env vars, and run `python main.py schedule` under systemd or tmux. Better if you want tighter intervals or no cron drift.

## Notes

- Be polite: keep the crawl delay, keep a real User-Agent, respect each API's rate limits.
- Congressional data comes from mandatory public disclosures; amounts are ranges, and filings lag trades by up to 45 days.
- Pattern detection is informational only, not investment advice.
