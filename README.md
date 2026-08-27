# FinBot

A personal financial wire service. It gathers news, market data, crypto, congressional
disclosures and institutional filings, then does the part that actually takes work:
**it explains what the numbers mean and which stocks each headline is likely to move.**

Output is a dashboard you read on your phone, plus a push notification when something
genuinely new happens.

## Written for someone who is new to this

The dashboard opens in **plain-English mode**. Jargon is replaced with ordinary words,
every technical term is tappable for a one-sentence definition, and each of the 80 tracked
assets carries a beginner read: what it actually is, how risky it is on a 1-5 scale, what
the price is doing in plain words, and the mistake people most often make with that *kind*
of holding.

> **NVDA · Nvidia** — *Expensive to chase* · Risk 4/5
> **What it is.** A single company: the chips that nearly all AI systems run on.
> It has risen 19% in the past month alone. That is a fast move, and fast moves often pause.
> **Watch out:** owning one company means one bad quarter or one failed product can hit you
> hard — a risk owning a broad fund spreads away. It has also run up sharply, and buying
> right after a steep rise is the single most common beginner mistake.

A **Full detail** switch restores the analyst wording for when you want it.

**On "should I buy this?"** — nothing here can answer that, and anything that claims to is
selling you something. It depends on your income, your timeline, and how you would feel in
a bad year. What FinBot does instead is the honest, useful version: it tells you what kind
of thing you are looking at, how much it could realistically hurt you, whether the price is
stretched or beaten down right now, and the specific error beginners make with that
category. The judgement stays yours, but it is an informed one.

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
| markets | yfinance | 41 stocks, 5 indexes, 23 ETFs, 11 bond funds and yields |
| crypto | CoinGecko free API | Price, market cap, 1h/24h/7d/30d changes |
| patterns | computed | Golden/death cross, RSI extremes, 52-wk breaks, volume spikes |
| insights | computed | Per-headline stock impact, direction, magnitude, ripple effects |
| commentary | computed | Narrated movers, patterns, breadth, crypto, congress |
| plainspeak | computed | Jargon glossary, plain-English event meanings, beginner risk reads |

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

- **Start here** — a short primer on what a share, a fund and a bond actually are, plus the
  1-5 risk scale used everywhere on the page
- **What you could invest in** — all 80 tracked assets grouped from safest to most
  speculative (whole-market funds → international → dividend → bonds → sectors → gold →
  individual companies → high risk). Search it, filter to lower-risk only, tap any row for
  the full plain-English read
- **The tape** — click any ticker to filter the whole wire to stories touching it
- **The read** — the market-wide paragraph, plus gauges that explain what VIX and the
  10-year yield actually mean for equities
- **The annotated wire** — every headline, filterable by direction (bullish / bearish /
  two-sided) and conviction, searchable, each expanding to the full analysis with an
  impact ladder showing per-ticker direction and estimated magnitude
- **Instrument rail** — movers, patterns, crypto and congress filings, each expanding
  to its narration

Light and dark themes, responsive to phone width, keyboard accessible (`/` focuses search).
The reading level and theme are both remembered between visits.

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

The digest is written in plain English by default. Set `NOTIFY_STYLE=expert` if you would
rather have the analyst phrasing.

Nothing new in an hour means no ping. Items already pushed are never re-sent, so a mover
that persists across runs notifies once, not every hour.

**Alternative — a free always-on VM** (Oracle Cloud Always Free, GCP e2-micro): clone,
install, set the env vars, run `python main.py schedule` under systemd or tmux. Better if
you want tighter intervals or no cron drift.

## Extending it

- Tickers, coins, funds and politicians: `config.py`
- Plain-English descriptions and risk levels for a new asset: `analysis/assets.py`
- New glossary term or event explanation: `analysis/plainspeak.py`
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
