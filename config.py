"""Central configuration for FinBot."""

DB_PATH = "finbot.db"

# Identify yourself politely. SEC EDGAR *requires* a real contact in User-Agent.
USER_AGENT = "FinBot/0.1 (personal research; contact: you@example.com)"

REQUEST_TIMEOUT = 20
CRAWL_DELAY_SECONDS = 1.0  # be polite between requests

# ---------- News (RSS - free, legal, no scraping needed) ----------
NEWS_FEEDS = {
    "cnbc_business": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
    "cnbc_tech": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910",
    "cnbc_finance": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
    "marketwatch_top": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "techcrunch": "https://techcrunch.com/feed/",
    "seeking_alpha_news": "https://seekingalpha.com/market_currents.xml",
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
}

# ---------- Congressional trading (STOCK Act disclosures) ----------
# Community-maintained mirrors of official House/Senate financial disclosures.
SENATE_TRADES_URL = (
    "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/"
    "aggregate/all_transactions.json"
)
HOUSE_TRADES_URL = (
    "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/"
    "data/all_transactions.json"
)
TRACKED_POLITICIANS = [
    "Pelosi",        # Nancy Pelosi (via spouse's disclosed trades)
    "Tuberville",
    "Crenshaw",
    "Ossoff",
]

# ---------- Institutional / VC portfolios (SEC 13F filings) ----------
# CIK numbers of managers whose quarterly 13F holdings you want.
TRACKED_FUNDS = {
    "Berkshire Hathaway": "0001067983",
    "ARK Investment": "0001697748",
    "Bridgewater": "0001350694",
    "Tiger Global": "0001167483",
    "Sequoia Fund": "0000089043",
}
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

# ---------- Markets ----------
STOCKS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO"]
INDEXES = ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"]
ETFS_FUNDS = ["SPY", "QQQ", "VTI", "ARKK", "XLK", "XLF"]
BONDS = ["^TNX", "^TYX", "^IRX", "TLT", "HYG"]  # yields + bond ETFs

# ---------- Crypto (CoinGecko free API) ----------
CRYPTO_IDS = ["bitcoin", "ethereum", "solana", "ripple", "cardano", "dogecoin"]
COINGECKO_MARKETS_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&ids={ids}&price_change_percentage=1h,24h,7d,30d"
)

# ---------- Pattern detection ----------
PATTERN_LOOKBACK_DAYS = 250  # ~1 trading year
RSI_PERIOD = 14
VOLUME_SPIKE_MULT = 2.5      # today's volume vs 20-day average
