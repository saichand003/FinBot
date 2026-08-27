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
# Primary source: the House Clerk publishes a yearly ZIP containing an XML index
# of every financial disclosure filed. Filing type "P" is a Periodic Transaction
# Report - the form a member must file within 45 days of a trade.
#
# (The old senate-stock-watcher / house-stock-watcher S3 mirrors now return 403,
# so FinBot reads the official primary source instead.)
HOUSE_FD_ZIP_URL = "https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.zip"
HOUSE_PTR_PDF_URL = "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/{doc_id}.pdf"
HOUSE_FD_YEARS = 1          # how many years back to pull (1 = current year only)

# Surnames to track. Empty list = every member who filed a transaction report.
TRACKED_POLITICIANS = [
    "Pelosi", "Crenshaw", "Gottheimer", "Green", "Khanna",
    "Moore", "Mccaul", "Garbarino", "Kustoff", "Fallon",
]
MAX_CONGRESS_FILINGS = 120  # cap per run so the digest stays readable

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
# A wider universe so there is something here for every risk appetite: broad
# index funds, sector funds, individual companies, and the bond market.
STOCKS = [
    # megacap technology
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    # other technology
    "AMD", "INTC", "TSM", "MU", "ORCL", "CRM", "ADBE", "QCOM", "TXN",
    "NFLX", "UBER", "PLTR", "COIN",
    # financials
    "JPM", "BAC", "GS", "V", "MA",
    # healthcare
    "LLY", "UNH", "JNJ", "PFE",
    # consumer and industrial
    "WMT", "COST", "HD", "MCD", "NKE", "SBUX", "KO", "PG", "DIS",
    # energy
    "XOM", "CVX",
]
INDEXES = ["^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX"]
ETFS_FUNDS = [
    # broad market - the "own everything" funds
    "SPY", "VOO", "VTI", "QQQ", "IWM", "DIA", "VT",
    # international
    "VEA", "VWO",
    # dividend and lower-volatility tilts
    "SCHD", "VIG", "VYM",
    # sectors
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU",
    # high risk / commodities
    "ARKK", "GLD", "SLV",
]
BONDS = [
    "^TNX", "^TYX", "^IRX",              # US Treasury yields (10y, 30y, 3m)
    "SHY", "IEF", "TLT",                 # short, medium, long government bonds
    "BND", "AGG", "LQD", "TIP", "HYG",   # total market, corporate, inflation, high yield
]

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


# =====================================================================
#  INSIGHT ENGINE - knowledge base for "how does this news hit stocks?"
# =====================================================================

# ---------- Company / keyword -> ticker resolution ----------
# Longest alias wins, matched case-insensitively on word boundaries.
TICKER_ALIASES = {
    "AAPL":  ["apple", "iphone", "ipad", "mac book", "macbook", "app store", "tim cook", "vision pro"],
    "MSFT":  ["microsoft", "azure", "copilot", "windows", "xbox", "satya nadella"],
    "NVDA":  ["nvidia", "jensen huang", "blackwell", "hopper", "h100", "h200", "gb200", "cuda"],
    "GOOGL": ["google", "alphabet", "youtube", "gemini", "waymo", "deepmind", "sundar pichai"],
    "AMZN":  ["amazon", "aws", "andy jassy", "prime video", "alexa"],
    "META":  ["meta platforms", "facebook", "instagram", "whatsapp", "zuckerberg", "llama", "threads"],
    "TSLA":  ["tesla", "elon musk", "cybertruck", "robotaxi", "model y", "full self-driving"],
    "AVGO":  ["broadcom", "hock tan", "vmware"],
    "AMD":   ["advanced micro devices", "lisa su", "instinct mi300", " amd "],
    "INTC":  ["intel", "pat gelsinger", "lip-bu tan"],
    "TSM":   ["tsmc", "taiwan semiconductor"],
    "MU":    ["micron"],
    "SMCI":  ["super micro", "supermicro"],
    "ORCL":  ["oracle", "safra catz"],
    "CRM":   ["salesforce", "marc benioff"],
    "ADBE":  ["adobe"],
    "NFLX":  ["netflix"],
    "WBD":   ["warner bros", "warner brothers", "hbo max", "discovery inc"],
    "PARA":  ["paramount", "cbs news", "paramount skydance"],
    "CMCSA": ["comcast", "nbcuniversal", "peacock"],
    "DKS":   ["dick's sporting", "dicks sporting goods"],
    "LULU":  ["lululemon"],
    "GPS":   ["gap inc"],
    "M":     ["macy's"],
    "KSS":   ["kohl's"],
    "BBY":   ["best buy"],
    "CVS":   ["cvs health"],
    "T":     ["at&t"],
    "VZ":    ["verizon"],
    "SNAP":  ["snap inc", "snapchat"],
    "PINS":  ["pinterest"],
    "RBLX":  ["roblox"],
    "ABNB":  ["airbnb"],
    "DASH":  ["doordash"],
    "LYFT":  ["lyft"],
    "SPOT":  ["spotify"],
    "HOOD":  ["robinhood"],
    "MRVL":  ["marvell"],
    "DDOG":  ["datadog"],
    "NET":   ["cloudflare"],
    "ZS":    ["zscaler"],
    "MDB":   ["mongodb"],
    "DIS":   ["disney", "bob iger", "espn"],
    "UBER":  ["uber technologies", "uber eats"],
    "COIN":  ["coinbase", "brian armstrong"],
    "MSTR":  ["microstrategy", "strategy inc", "michael saylor"],
    "PLTR":  ["palantir", "alex karp"],
    "JPM":   ["jpmorgan", "jp morgan", "jamie dimon"],
    "BAC":   ["bank of america"],
    "GS":    ["goldman sachs"],
    "MS":    ["morgan stanley"],
    "WFC":   ["wells fargo"],
    "BRK-B": ["berkshire hathaway", "warren buffett", "greg abel"],
    "V":     ["visa inc"],
    "MA":    ["mastercard"],
    "PYPL":  ["paypal"],
    "XOM":   ["exxon", "exxonmobil"],
    "CVX":   ["chevron"],
    "LLY":   ["eli lilly", "zepbound", "mounjaro", "tirzepatide"],
    "NVO":   ["novo nordisk", "ozempic", "wegovy"],
    "PFE":   ["pfizer"],
    "UNH":   ["unitedhealth"],
    "JNJ":   ["johnson & johnson", "johnson and johnson"],
    "WMT":   ["walmart"],
    "COST":  ["costco"],
    "TGT":   ["target corp"],
    "HD":    ["home depot"],
    "NKE":   ["nike"],
    "SBUX":  ["starbucks"],
    "MCD":   ["mcdonald"],
    "KO":    ["coca-cola", "coca cola"],
    "PEP":   ["pepsico", "pepsi"],
    "BA":    ["boeing"],
    "LMT":   ["lockheed martin"],
    "RTX":   ["raytheon", "rtx corp"],
    "CAT":   ["caterpillar"],
    "DE":    ["deere & co", "john deere"],
    "F":     ["ford motor"],
    "GM":    ["general motors"],
    "RIVN":  ["rivian"],
    "LCID":  ["lucid motors", "lucid group"],
    "NIO":   ["nio inc"],
    "BABA":  ["alibaba"],
    "PDD":   ["pinduoduo", "temu"],
    "SHOP":  ["shopify"],
    "SQ":    ["block inc", "square inc"],
    "SNOW":  ["snowflake"],
    "CRWD":  ["crowdstrike"],
    "PANW":  ["palo alto networks"],
    "NOW":   ["servicenow"],
    "IBM":   ["ibm ", "international business machines"],
    "QCOM":  ["qualcomm"],
    "TXN":   ["texas instruments"],
    "ASML":  ["asml"],
    "ARM":   ["arm holdings"],
    "DELL":  ["dell technologies"],
    "HPE":   ["hewlett packard enterprise"],
    "VST":   ["vistra"],
    "CEG":   ["constellation energy"],
    "NEE":   ["nextera"],
}

# Mentions that *imply* exposure without the story being about the company.
# These produce a reduced-weight "indirect" impact instead of a direct hit, so a
# story about OpenAI is not filed as a Microsoft story.
PROXY_ALIASES = {
    "MSFT":  ["openai", "chatgpt", "sam altman"],
    "NVDA":  ["ai chips", "gpu shortage", "ai capex", "data center buildout"],
    "GOOGL": ["anthropic"],
    "AMZN":  ["anthropic"],
    "COIN":  ["crypto exchange"],
    "TSM":   ["taiwan", "chip fab", "foundry"],
    "AAPL":  ["smartphone market"],
}
PROXY_WEIGHT = 0.45   # an implied mention is worth this fraction of a direct hit

# Feeds whose stories are about tokens, not equities - equity mechanisms
# (EPS, buybacks, dividends) do not transfer, so they get reframed.
CRYPTO_SOURCES = ("coindesk",)

# ---------- Peer / supply-chain graph: ripple effects ----------
# ticker -> [(peer, relationship, coefficient)]
# coefficient = how much of the primary move typically bleeds across (0-1).
PEER_GRAPH = {
    "NVDA":  [("AMD", "closest AI-GPU competitor", 0.5), ("AVGO", "custom AI silicon rival", 0.4),
              ("TSM", "manufactures its chips", 0.45), ("SMCI", "builds servers around its GPUs", 0.6),
              ("MU", "supplies HBM memory", 0.45), ("ARM", "shares AI-compute narrative", 0.35)],
    "AMD":   [("NVDA", "market-share rival", 0.35), ("INTC", "x86 competitor", 0.4), ("TSM", "foundry partner", 0.3)],
    "TSM":   [("NVDA", "largest foundry customer", 0.3), ("AAPL", "biggest-volume foundry customer", 0.25), ("ASML", "sole supplier of EUV lithography", 0.5),
              ("AMD", "foundry customer", 0.3), ("INTC", "foundry rival", 0.3)],
    "AAPL":  [("QCOM", "modem supplier", 0.35), ("AVGO", "RF component supplier", 0.3),
              ("TSM", "sole chip fabricator", 0.25), ("GOOGL", "pays for default search placement", 0.2)],
    "MSFT":  [("GOOGL", "cloud + AI rival", 0.3), ("AMZN", "cloud rival", 0.35), ("NVDA", "sells into the AI capex budget", 0.4),
              ("ORCL", "enterprise cloud rival", 0.3), ("CRM", "enterprise software peer", 0.25)],
    "GOOGL": [("META", "digital-ad duopoly partner", 0.5), ("MSFT", "search + AI rival", 0.3), ("AMZN", "ad + cloud rival", 0.3)],
    "META":  [("GOOGL", "digital-ad duopoly partner", 0.5), ("SNAP", "ad-budget competitor", 0.55), ("PINS", "ad-budget competitor", 0.5)],
    "AMZN":  [("WMT", "retail rival", 0.35), ("MSFT", "cloud rival", 0.3), ("SHOP", "e-commerce peer", 0.4), ("TGT", "retail rival", 0.3)],
    "TSLA":  [("RIVN", "EV peer", 0.5), ("LCID", "EV peer", 0.5), ("NIO", "EV peer", 0.4),
              ("F", "legacy-auto EV exposure", 0.25), ("GM", "legacy-auto EV exposure", 0.25)],
    "JPM":   [("BAC", "money-center bank peer", 0.7), ("WFC", "money-center bank peer", 0.65),
              ("C", "money-center bank peer", 0.6), ("GS", "capital-markets peer", 0.5)],
    "LLY":   [("NVO", "GLP-1 duopoly rival", 0.6), ("PFE", "large-cap pharma peer", 0.25)],
    "NVO":   [("LLY", "GLP-1 duopoly rival", 0.6)],
    "COIN":  [("MSTR", "crypto-beta proxy", 0.6), ("HOOD", "retail-trading peer", 0.5)],
    "AVGO":  [("NVDA", "AI-silicon peer", 0.35), ("QCOM", "semi peer", 0.35), ("MRVL", "custom-silicon rival", 0.6)],
    "WMT":   [("TGT", "big-box peer", 0.7), ("COST", "big-box peer", 0.5), ("AMZN", "retail rival", 0.3)],
    "BA":    [("RTX", "aero supplier/peer", 0.35), ("LMT", "defense peer", 0.25)],
    "XOM":   [("CVX", "integrated-major peer", 0.75)],
    "CVX":   [("XOM", "integrated-major peer", 0.75)],
}

# ---------- Sector baskets: for macro news with no single company ----------
SECTOR_BASKETS = {
    "semis":       ["NVDA", "AMD", "AVGO", "TSM", "MU", "INTC", "QCOM", "ASML"],
    "megacap_tech":["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA"],
    "banks":       ["JPM", "BAC", "GS", "MS", "WFC"],
    "energy":      ["XOM", "CVX"],
    "retail":      ["WMT", "COST", "TGT", "HD", "AMZN"],
    "ev_auto":     ["TSLA", "RIVN", "LCID", "F", "GM"],
    "crypto_eq":   ["COIN", "MSTR"],
    "defense":     ["LMT", "RTX", "BA"],
    "pharma":      ["LLY", "NVO", "PFE", "JNJ", "UNH"],
    "ai_power":    ["VST", "CEG", "NEE"],
    "software":    ["CRM", "NOW", "SNOW", "ORCL", "ADBE", "PLTR"],
    "growth_proxy":["QQQ", "ARKK"],
    "broad_market":["SPY", "^GSPC", "QQQ"],
    "bonds":       ["TLT", "^TNX", "HYG"],
}

# ---------- Event lexicon ----------
# phrase -> (event_label, direction, strength 0-1, plain-English mechanism)
# direction: +1 bullish for the named company, -1 bearish, 0 volatility-only.
EVENT_LEXICON = {
    # --- earnings & guidance ---
    "beats estimates":      ("Earnings beat",        +1, 0.75, "Reported profit came in above what analysts modelled, so forward estimates get revised up."),
    "beat expectations":    ("Earnings beat",        +1, 0.75, "Results cleared the consensus bar, which usually pulls analyst price targets higher."),
    "tops estimates":       ("Earnings beat",        +1, 0.7,  "Revenue/EPS above consensus - the number the street was anchored on moves up."),
    "misses estimates":     ("Earnings miss",        -1, 0.8,  "Profit fell short of consensus; the multiple usually compresses until guidance is re-established."),
    "misses expectations":  ("Earnings miss",        -1, 0.8,  "Shortfall vs consensus forces analysts to cut forward estimates."),
    "cuts guidance":        ("Guidance cut",         -1, 0.9,  "Management lowered its own forecast - the single most reliably negative earnings signal."),
    "lowers outlook":       ("Guidance cut",         -1, 0.85, "Forward outlook reduced, so every future-year model gets marked down."),
    "raises guidance":      ("Guidance raise",       +1, 0.9,  "Management raised its own forecast - the strongest bullish earnings signal there is."),
    "raises outlook":       ("Guidance raise",       +1, 0.85, "Higher forward outlook lifts the entire discounted-cash-flow base."),
    "record revenue":       ("Record revenue",       +1, 0.6,  "Top-line record signals demand is still accelerating."),
    "record profit":        ("Record profit",        +1, 0.65, "Peak earnings power; supports a higher multiple if margins hold."),
    "profit warning":       ("Profit warning",       -1, 0.9,  "Pre-announced shortfall - the market prices it in immediately."),
    "earnings":             ("Earnings event",        0, 0.35, "An earnings print is a scheduled volatility event; options are usually priced for a large move."),
    "raised guidance":      ("Guidance raise",       +1, 0.9,  "Management raised its own forecast - the strongest bullish earnings signal there is."),
    "raised its outlook":   ("Guidance raise",       +1, 0.85, "Higher forward outlook lifts the entire discounted-cash-flow base."),
    "raised full-year":     ("Guidance raise",       +1, 0.85, "Raising the full-year bar mid-course signals demand is running ahead of plan."),
    "cut guidance":         ("Guidance cut",         -1, 0.9,  "Management lowered its own forecast - the most reliably negative earnings signal."),
    "lowered its outlook":  ("Guidance cut",         -1, 0.85, "A reduced outlook marks down every forward-year model."),
    "beat estimates":       ("Earnings beat",        +1, 0.75, "Reported profit came in above what analysts modelled, so forward estimates get revised up."),
    "topped estimates":     ("Earnings beat",        +1, 0.7,  "Revenue/EPS above consensus - the number the street was anchored on moves up."),
    "missed estimates":     ("Earnings miss",        -1, 0.8,  "Profit fell short of consensus; the multiple compresses until guidance is re-established."),
    "missed expectations":  ("Earnings miss",        -1, 0.8,  "A shortfall against consensus forces analysts to cut forward estimates."),
    "upgraded":             ("Analyst upgrade",      +1, 0.45, "Rating upgrades pull in mandate-constrained institutional buyers."),
    "downgraded":           ("Analyst downgrade",    -1, 0.5,  "Downgrades trigger mechanical selling from funds that track ratings."),
    # --- corporate actions ---
    "acquire":              ("M&A",                   0, 0.5,  "Deals cut both ways: the target gaps toward the offer price while the acquirer usually dips on deal cost and integration risk. Which side the named company is on decides the sign."),
    "acquisition":          ("M&A",                   0, 0.5,  "Deal news re-rates the target toward the bid and pressures the buyer on deal cost. Check which side the named company is on before assigning a sign."),
    "merger":               ("M&A",                   0, 0.55, "Consolidation reduces competition, which helps sector pricing power - but the buyer carries the integration risk."),
    "takeover":             ("M&A target",           +1, 0.6,  "Takeover interest puts a floor under the target's share price - bidders rarely come in below market."),
    "buyback":              ("Buyback",              +1, 0.6,  "Share repurchases shrink the float, mechanically lifting earnings per share."),
    "share repurchase":     ("Buyback",              +1, 0.6,  "Fewer shares outstanding means the same profit spread over a smaller base."),
    "dividend increase":    ("Dividend hike",        +1, 0.5,  "A raised dividend is management signalling confidence in durable cash flow."),
    "raises dividend":      ("Dividend hike",        +1, 0.5,  "Higher payout signals confident free-cash-flow guidance."),
    "cuts dividend":        ("Dividend cut",         -1, 0.8,  "Dividend cuts signal cash stress and trigger forced selling by income funds."),
    "stock split":          ("Stock split",          +1, 0.3,  "Cosmetic for valuation, but historically draws retail flow and index attention."),
    "spin-off":             ("Spin-off",             +1, 0.4,  "Separating a business unit often unlocks a sum-of-the-parts discount."),
    "ipo debut":            ("IPO",                   0, 0.3,  "New supply of shares in the sector; watch for read-through comps on valuation."),
    "bankruptcy":           ("Bankruptcy",           -1, 1.0,  "Equity is usually wiped out; creditors take the assets."),
    "chapter 11":           ("Bankruptcy",           -1, 1.0,  "Restructuring under Chapter 11 typically leaves common shareholders with nothing."),
    # --- operations ---
    "layoffs":              ("Layoffs",              +1, 0.4,  "Short-term cost cuts lift margins, though large layoffs can also signal weakening demand."),
    "job cuts":             ("Layoffs",              +1, 0.4,  "Headcount reduction is margin-accretive near term; read the reason carefully."),
    "recall":               ("Product recall",       -1, 0.7,  "Recalls carry direct remediation cost plus brand and warranty liability."),
    "outage":               ("Service outage",       -1, 0.4,  "Downtime hits revenue and, for infrastructure names, customer trust."),
    "data breach":          ("Data breach",          -1, 0.65, "Breach means regulatory fines, remediation cost, and customer churn."),
    "hacked":               ("Cyber incident",       -1, 0.55, "Security incidents carry direct cost plus reputational damage."),
    "workers strike":       ("Labour strike",        -1, 0.6,  "Work stoppage halts output and usually ends in higher structural labour cost."),
    "goes on strike":       ("Labour strike",        -1, 0.6,  "Work stoppage halts output and usually ends in higher structural labour cost."),
    "union strike":         ("Labour strike",        -1, 0.6,  "Organised labour action stops production and raises the structural cost base."),
    "production halt":      ("Production halt",      -1, 0.7,  "Lost units are rarely fully recovered; it flows straight through to the quarter."),
    "supply chain":         ("Supply chain",          0, 0.4,  "Supply constraints cap upside revenue even when demand is strong."),
    "price increase":       ("Pricing power",        +1, 0.5,  "Raising prices without losing volume is the cleanest evidence of pricing power."),
    "price cut":            ("Price cut",            -1, 0.6,  "Discounting defends volume at the cost of gross margin."),
    "partnership":          ("Partnership",          +1, 0.45, "Named partnerships create a revenue channel and validate the product."),
    "contract win":         ("Contract win",         +1, 0.6,  "Booked backlog converts into visible future revenue."),
    "wins contract":        ("Contract win",         +1, 0.6,  "New award adds to backlog and de-risks forward guidance."),
    # --- analyst / flows ---
    "upgrade":              ("Analyst upgrade",      +1, 0.45, "Rating upgrades pull in mandate-constrained institutional buyers."),
    "downgrade":            ("Analyst downgrade",    -1, 0.5,  "Downgrades trigger mechanical selling from funds that track ratings."),
    "price target":         ("Target change",         0, 0.3,  "Target revisions reset the anchor the street trades around."),
    "initiated coverage":   ("New coverage",         +1, 0.3,  "Fresh analyst coverage widens the institutional buyer base."),
    "short seller":         ("Short report",         -1, 0.7,  "Public short theses force a burden of proof onto management."),
    "insider selling":      ("Insider selling",      -1, 0.4,  "Insiders selling in size is a soft negative signal on near-term prospects."),
    "insider buying":       ("Insider buying",       +1, 0.5,  "Open-market insider purchases are one of the better-documented bullish signals."),
    "index inclusion":      ("Index inclusion",      +1, 0.7,  "Passive funds must buy the name, creating forced non-discretionary demand."),
    "s&p 500 inclusion":    ("Index inclusion",      +1, 0.75, "Every S&P 500 tracker has to buy it - a large mechanical bid."),
    # --- legal / regulatory ---
    "antitrust":            ("Antitrust",            -1, 0.6,  "Antitrust action threatens the business model, not just a one-off fine."),
    "lawsuit":              ("Litigation",           -1, 0.45, "Legal overhang adds a discount until the liability is quantifiable."),
    "sec investigation":    ("Regulatory probe",     -1, 0.7,  "An SEC probe raises the risk of restatement and governance discount."),
    "federal investigation":("Investigation",        -1, 0.5,  "Open investigations create headline risk and a valuation overhang."),
    "fined":                ("Regulatory fine",      -1, 0.45, "A fine is a one-time cash hit but often signals ongoing compliance cost."),
    "settlement":           ("Legal settlement",     +1, 0.4,  "Settling removes uncertainty, which the market usually rewards."),
    "fda approval":         ("FDA approval",         +1, 0.9,  "Approval converts a pipeline asset into an actual revenue line."),
    "fda rejection":        ("FDA rejection",        -1, 0.9,  "A rejection erases the modelled revenue for that drug entirely."),
    "clinical trial":       ("Trial data",            0, 0.6,  "Trial readouts are binary events - position sizing matters more than direction."),
    "export controls":      ("Export controls",      -1, 0.75, "Restricting where chips can be sold directly removes addressable market."),
    "export restrictions":  ("Export controls",      -1, 0.75, "Blocked end-markets cut revenue with no near-term substitute."),
    "tariff":               ("Tariffs",              -1, 0.65, "Tariffs raise input cost; whoever cannot pass it on eats the margin."),
    "sanctions":            ("Sanctions",            -1, 0.6,  "Sanctions close markets and complicate supply chains."),
    "new regulation":       ("Regulation",           -1, 0.4,  "New rules usually mean compliance cost and slower product velocity."),
    # --- macro ---
    "rate cut":             ("Rate cut",             +1, 0.8,  "Lower discount rates raise the present value of far-off cash flows - long-duration growth and small caps benefit most."),
    "cuts rates":           ("Rate cut",             +1, 0.8,  "Cheaper money lifts equity multiples, especially for unprofitable growth."),
    "rate hike":            ("Rate hike",            -1, 0.8,  "Higher discount rates compress valuation multiples, hitting growth hardest."),
    "raises rates":         ("Rate hike",            -1, 0.8,  "Tighter policy pressures multiples and raises corporate financing cost."),
    "inflation":            ("Inflation data",        0, 0.6,  "Inflation prints set the Fed path, which sets the discount rate for every equity."),
    "cpi":                  ("CPI print",             0, 0.65, "CPI is the single biggest scheduled macro driver of index-level moves."),
    "jobs report":          ("Jobs data",             0, 0.55, "Payrolls drive rate expectations: hot data is good for earnings, bad for multiples."),
    "unemployment":         ("Labour data",           0, 0.5,  "Rising unemployment softens consumer demand but pulls rate cuts forward."),
    "recession":            ("Recession risk",       -1, 0.7,  "Recession fear compresses cyclical earnings estimates first."),
    "gdp":                  ("GDP data",              0, 0.45, "Growth data recalibrates the earnings base for cyclicals."),
    "federal reserve":      ("Fed policy",            0, 0.6,  "Fed language moves the whole rates complex, and equities follow rates."),
    "fomc":                 ("FOMC",                  0, 0.7,  "FOMC decisions and dot plots reset the entire discount-rate assumption."),
    "treasury yield":       ("Rates move",            0, 0.5,  "Moves in the 10-year yield are the mechanical input to equity valuation."),
    "oil prices":           ("Oil move",              0, 0.5,  "Crude is a cost input for transport and industrials, revenue for energy names."),
    "opec":                 ("OPEC",                  0, 0.55, "Supply decisions set the crude price that flows into energy earnings and CPI."),
    "china":                ("China exposure",        0, 0.45, "China demand and policy is a swing factor for semis, luxury, and industrials."),
    "trade war":            ("Trade tension",        -1, 0.6,  "Escalating trade barriers raise cost and fragment supply chains."),
    "government shutdown":  ("Shutdown risk",        -1, 0.4,  "Shutdowns delay data and federal contract payments; historically short-lived for markets."),
    # --- crypto ---
    "bitcoin etf":          ("Crypto ETF flows",     +1, 0.6,  "Spot ETF flows are now the marginal buyer of bitcoin - and of crypto-levered equities."),
    "halving":              ("Bitcoin halving",      +1, 0.5,  "Issuance halves while demand is unchanged, a supply-side tailwind."),
    "sec approves":         ("Regulatory approval",  +1, 0.7,  "Approval opens a regulated distribution channel to institutional money."),
    "stablecoin":           ("Stablecoin policy",     0, 0.4,  "Stablecoin rules determine how crypto connects to the banking system."),
}

# ---------- Macro phrase -> which baskets it hits, and which way ----------
MACRO_IMPACTS = {
    "Rate cut":        [("growth_proxy", +1, "long-duration growth re-rates hardest when rates fall"),
                        ("banks", -1, "lower rates compress net interest margin"),
                        ("bonds", +1, "bond prices rise as yields fall")],
    "Rate hike":       [("growth_proxy", -1, "high-multiple growth de-rates when the discount rate rises"),
                        ("banks", +1, "wider net interest margin on loan books"),
                        ("bonds", -1, "bond prices fall as yields rise")],
    "Export controls": [("semis", -1, "chip export limits directly remove addressable revenue")],
    "Tariffs":         [("retail", -1, "importers absorb or pass through higher landed cost"),
                        ("ev_auto", -1, "auto supply chains are heavily cross-border")],
    "Oil move":        [("energy", +1, "energy earnings track the crude strip almost one-for-one")],
    "OPEC":            [("energy", +1, "OPEC supply policy sets the price energy names realise")],
    "CPI print":       [("broad_market", 0, "index-level volatility event; direction depends on the surprise")],
    "FOMC":            [("broad_market", 0, "the whole market re-prices off the dot plot")],
    "Crypto ETF flows":[("crypto_eq", +1, "crypto-levered equities trade as high-beta bitcoin proxies")],
    "Recession risk":  [("banks", -1, "credit losses rise in a downturn"),
                        ("retail", -1, "discretionary spend contracts first")],
    "China exposure":  [("semis", 0, "China is a large but politically fragile end-market for chips")],
}

# ---------- Scoring thresholds ----------
IMPACT_HIGH = 0.60      # >= this -> "HIGH" conviction badge
IMPACT_MEDIUM = 0.32    # >= this -> "MEDIUM"
MAX_INSIGHT_NEWS = 200   # how many recent headlines to analyse per run
