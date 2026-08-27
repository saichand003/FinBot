# FinBot

A personal financial wire service. It gathers news, market data, crypto, congressional
disclosures and institutional filings, then does the part that actually takes work:
**it explains what the numbers mean and which stocks each headline is likely to move.**

Output is a dashboard you read on your phone, plus a push notification when something
genuinely new happens.

## What it does that a price feed doesn't

**Every headline gets an impact read.** For each story FinBot resolves which companies
are named, matches the text against a lexicon of ~90 market events (guidance cuts, FDA
approvals, export controls, rate decisions...), assigns a direction and magnitude, then
propagates the effect through a peer and supply-chain graph. An Nvidia story is also a
TSMC, SMCI and AMD story, and FinBot says so, with the relationship spelled out.

> **Fed officials saw need for rate hike if inflation doesn't cool** — `HIGH` `bearish`
> **Mechanism:** higher discount rates compress valuation multiples, hitting growth hardest.
> **Macro read-through:** ARKK ▼, QQQ ▼ (long-duration growth de-rates), JPM ▲, BAC ▲, GS ▲
> (wider net interest margin), TLT ▼, HYG ▼ (bond prices fall as yields rise).
> **Watch next:** the 2-year yield and the fed funds futures curve — equities follow those,
> not the headline.

**Every number gets narrated.** "NVDA +7.94%" is data. FinBot writes the information:

> NVDA rose 7.94% today. That is roughly 2.8x its average daily range of 2.9% — a genuine
> outlier session, not noise. Volume ran 1.9x the 20-day average, so real size was behind
> the move. Structurally it is in an uptrend: price 226.27 versus the 50-day at 208.13
> (+8.7%) and the 200-day at 195.56 (+15.7%). RSI at 52 is neutral. Today extends the
> one-month trend (+19.1%) rather than fighting it.
> **Read:** high-conviction repositioning. Find the catalyst before assuming it mean-reverts.

Pattern signals come with their failure modes, not just the signal. The golden-cross note
tells you it is a lagging indicator with a high false-signal rate in choppy markets.

## Data sources (all public / official)

| Module | Source | What it gets |
|---|---|---|
| news | RSS feeds (CNBC, Yahoo, MarketWatch, TechCrunch, CoinDesk...) | Headlines + summaries |
| congress | House Clerk financial disclosures | Periodic Transaction Reports + filing PDFs |
| 13f | SEC EDGAR | Quarterly 13F filings for Berkshire, ARK, Bridgewater, Tiger Global |
| markets | yfinance | Stocks, indexes, ETFs, bond yields |
| crypto | CoinGecko free API | Price, market cap, 1h/24h/7d/30d changes |
| patterns | computed | Golden/death cross, RSI extremes, 52-wk breaks, volume spikes |
| insights | computed | Per-headline stock impact, direction, magnitude, ripple effects |
| commentary | computed | Narrated movers, patterns, breadth, crypto, congress |

## Setup

```bash
pip install -r requirements.txt
# Set your contact email in config.py USER_AGENT (SEC requires a real one),
# then adjust tracked tickers, politicians, and funds.

python main.py run          # run everything once
python main.py report       # the narrated brief, in the terminal
python main.py dashboard    # build site/index.html
python main.py schedule     # run continuously on intervals
python main.py hourly       # one cloud pass: crawl, analyse, build, notify
```

Everything is stored in `finbot.db` (SQLite).

## The dashboard

`python main.py dashboard --open` builds `site/index.html` — a self-contained page with
no build step and no runtime dependencies.

- **The tape** — click any ticker to filter the whole wire to stories touching it
- **The read** — the market-wide paragraph, plus gauges that explain what VIX and the
  10-year yield actually mean for equities
- **The annotated wire** — every headline, filterable by direction (bullish / bearish /
  two-sided) and conviction, searchable, each expanding to the full analysis with an
  impact ladder showing per-ticker direction and estimated magnitude
- **Instrument rail** — movers, patterns, crypto and congress filings, each expanding
  to its narration

Light and dark themes, responsive to phone width, keyboard accessible (`/` focuses search).

## Free cloud + hourly phone notifications

**GitHub Actions (zero servers).** The workflow in `.github/workflows/finbot.yml` crawls
hourly, publishes the dashboard to GitHub Pages, and pushes a digest.

1. Push this repo to GitHub.
2. **Settings → Pages → Source: GitHub Actions.** This is what makes the dashboard
   reachable from your phone.
3. Install **ntfy** and subscribe to a long random topic (e.g. `finbot-a8x3k29q`).
4. **Settings → Secrets and variables → Actions** → add `NTFY_TOPIC` with that name.
   (Or `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` instead.)
5. Test it: **Actions → FinBot hourly → Run workflow.**

`DASHBOARD_URL` is set automatically by the workflow, so the notification links straight
to your dashboard.

### What a push notification can and cannot look like

The notification itself is drawn by your phone's operating system, so no app — FinBot
included — can give it custom fonts, colours, or layout. What ntfy *does* support, and
what FinBot uses:

| Feature | Support |
|---|---|
| **Markdown** (bold, headings, lists) | ntfy **Android** app and web app. iOS shows plain text, which still reads cleanly. |
| **Emoji tags** | Everywhere — the digest is scannable before you open it |
| **Priority** | Urgent digests break through Do Not Disturb; routine ones stay quiet |
| **Click action** | Tapping the notification opens your dashboard |
| **Action buttons** | An "Open dashboard" button under the notification |
| Custom fonts / colours | **Not possible** — OS-controlled, on every push service |

So the split is deliberate: the notification is the *signal* — ranked, scannable, under
4KB. The dashboard one tap away is the *substance*. That is the best available answer to
"can it look good on the ntfy app", and it is why Pages setup is step 2 above.

Nothing new in an hour means no ping. Items already pushed are never re-sent, so a mover
that persists across runs notifies once, not every hour.

**Alternative — a free always-on VM** (Oracle Cloud Always Free, GCP e2-micro): clone,
install, set the env vars, run `python main.py schedule` under systemd or tmux. Better if
you want tighter intervals or no cron drift.

## Extending it

- Tickers, coins, funds and politicians: `config.py`
- Teach it a new event type: add a phrase to `EVENT_LEXICON` with its direction, strength,
  and a one-line mechanism. It takes effect immediately.
- Teach it a new relationship: add an edge to `PEER_GRAPH` as
  `(peer, "how they are related", coefficient)`.
- Bump `analysis/insights.ENGINE_VERSION` after changing either — stored insights are then
  re-analysed against the new rules instead of serving stale reads.
- New crawler: add to `crawlers/` and register it in `main.py`'s `JOBS` dict.

## Notes and limits

- The impact engine is rule-based and fully auditable — every claim traces to a phrase in
  the lexicon or an edge in the peer graph. It describes how these events have typically
  propagated, not a forecast.
- It can be confidently wrong. Ambiguous headlines, sarcasm, and stories about private
  companies that merely mention a public one are the common failure modes.
- Congressional disclosures lag trades by up to 45 days, amounts are ranges, and many
  filings cover a spouse's account. The public index publishes that a report was filed;
  the line items are in the linked PDF.
- Be polite: keep the crawl delay, keep a real User-Agent, respect each API's rate limits.
- **Not investment advice.** Nothing here is reviewed by a human before it reaches you.
