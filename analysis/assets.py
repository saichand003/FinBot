"""What each tracked thing actually is, in plain words.

Written for someone who has never bought a share. Every entry answers three
questions a beginner actually has: what am I looking at, how risky is it, and
what should I know before I touch it.

`risk` is a 1-5 scale describing how much the price bounces around and how much
of your money could realistically vanish:
  1  government bonds - very steady, small returns
  2  broad index funds - owns hundreds of companies, the standard starting point
  3  sector funds and steady large companies
  4  individual growth companies - big swings are normal
  5  speculative - can halve, and has
"""

RISK_WORDS = {
    1: ("Very low", "Moves slowly. The main risk is that inflation outpaces your return."),
    2: ("Low", "Spread across hundreds of companies, so no single failure hurts much."),
    3: ("Medium", "Concentrated in one industry or one large company. Bumpier than a broad fund."),
    4: ("High", "A single company. Double-digit moves in a day are normal here."),
    5: ("Very high", "Speculative. Losing a large share of the money is a realistic outcome."),
}

KIND_WORDS = {
    "broad_etf": "Broad index fund",
    "intl_etf": "International index fund",
    "dividend_etf": "Dividend fund",
    "sector_etf": "Sector fund",
    "commodity_etf": "Commodity fund",
    "growth_etf": "High-risk growth fund",
    "stock": "Individual company",
    "bond_fund": "Bond fund",
    "bond_yield": "Government bond interest rate",
    "index": "Market index",
    "volatility": "Fear gauge",
}

# ---------------------------------------------------------------- the funds
FUNDS = {
    "SPY": ("broad_etf", 2, "S&P 500 fund",
            "One fund that owns a slice of the 500 largest US companies. Buying it means "
            "you own a little of Apple, Microsoft, JPMorgan and 497 others at once."),
    "VOO": ("broad_etf", 2, "S&P 500 fund (Vanguard)",
            "The same 500 companies as SPY, run by Vanguard at a slightly lower annual fee. "
            "For a long-term holder the cheaper fee is the only real difference."),
    "VTI": ("broad_etf", 2, "Total US market fund",
            "Owns essentially every public US company - around 3,600 of them, not just the "
            "biggest 500. The broadest single bet on the US economy you can make."),
    "QQQ": ("broad_etf", 3, "Nasdaq 100 fund",
            "The 100 largest non-financial companies on the Nasdaq, which in practice means "
            "heavily weighted toward technology. Rises faster than the S&P 500 in good years "
            "and falls harder in bad ones."),
    "IWM": ("broad_etf", 3, "Small company fund",
            "Owns 2,000 smaller US companies. Small companies are more sensitive to the "
            "economy and to interest rates, so this swings more than the S&P 500."),
    "DIA": ("broad_etf", 2, "Dow Jones fund",
            "Owns the 30 companies in the Dow Jones index - large, established, mostly "
            "profitable names. Narrower than the S&P 500 but similar in character."),
    "VT":  ("broad_etf", 2, "Whole world fund",
            "Owns companies from every major market on earth, US and international. The "
            "single most diversified fund on this list."),
    "VEA": ("intl_etf", 2, "Developed markets fund",
            "Companies in Europe, Japan, Australia and Canada. Held mainly so your money is "
            "not entirely dependent on the US economy."),
    "VWO": ("intl_etf", 3, "Emerging markets fund",
            "Companies in China, India, Brazil, Taiwan and similar economies. Higher "
            "potential growth, and more political and currency risk."),
    "SCHD": ("dividend_etf", 2, "Dividend fund",
             "Owns around 100 established companies chosen for paying reliable dividends - "
             "regular cash payments to shareholders. Tends to fall less in downturns."),
    "VIG": ("dividend_etf", 2, "Dividend growth fund",
            "Companies that have raised their dividend every year for at least a decade. "
            "A filter for financial durability more than for high income."),
    "VYM": ("dividend_etf", 2, "High dividend fund",
            "Companies paying above-average dividends. More income now, usually less growth."),
    "XLK": ("sector_etf", 3, "Technology sector fund",
            "Only technology companies. Concentrated, so it rises and falls with one industry."),
    "XLF": ("sector_etf", 3, "Financial sector fund",
            "Banks, insurers and payment companies. Sensitive to interest rates - banks "
            "generally earn more when rates are higher."),
    "XLE": ("sector_etf", 4, "Energy sector fund",
            "Oil and gas companies. Tracks the price of crude oil closely, which is driven by "
            "global politics as much as by business performance."),
    "XLV": ("sector_etf", 2, "Healthcare sector fund",
            "Drug makers, insurers and device companies. Demand for healthcare holds up in "
            "recessions, so this is one of the steadier sectors."),
    "XLY": ("sector_etf", 3, "Consumer discretionary fund",
            "Things people buy when they feel well off - cars, restaurants, travel, retail. "
            "One of the first sectors to suffer when the economy slows."),
    "XLP": ("sector_etf", 2, "Consumer staples fund",
            "Food, drinks, household goods - things people buy regardless of the economy. "
            "Boring by design, which is why it holds up in downturns."),
    "XLI": ("sector_etf", 3, "Industrial sector fund",
            "Machinery, airlines, railroads, defence. Rises and falls with the wider economy."),
    "XLU": ("sector_etf", 2, "Utilities sector fund",
            "Electricity, water and gas providers. Steady demand and reliable dividends, but "
            "it competes with bonds for income investors, so it falls when interest rates rise."),
    "ARKK": ("growth_etf", 5, "Speculative innovation fund",
             "Concentrated bets on unprofitable, fast-growing technology companies. It has "
             "both tripled and lost roughly three-quarters of its value within a few years. "
             "Genuinely high risk."),
    "GLD": ("commodity_etf", 3, "Gold fund",
            "Tracks the price of gold. Pays no dividend and produces nothing - people hold it "
            "as insurance against inflation and crises, not for growth."),
    "SLV": ("commodity_etf", 4, "Silver fund",
            "Tracks silver. Behaves like gold but swings roughly twice as hard, because "
            "silver is also an industrial metal."),
}

# ---------------------------------------------------------------- the bonds
BONDS = {
    "SHY": ("bond_fund", 1, "Short-term government bonds",
            "US government debt maturing in 1-3 years. About the safest place to park money "
            "that is not a bank account. Barely moves."),
    "IEF": ("bond_fund", 1, "Medium-term government bonds",
            "US government debt maturing in 7-10 years. Safe from default, but the price does "
            "move when interest rates change."),
    "TLT": ("bond_fund", 3, "Long-term government bonds",
            "US government debt maturing in 20+ years. Counter-intuitively volatile: the "
            "government will repay you, but if interest rates rise the price can fall 20% or "
            "more before then."),
    "BND": ("bond_fund", 1, "Total bond market fund",
            "A mix of government and high-quality corporate bonds across all maturities. The "
            "standard single bond holding for a beginner portfolio."),
    "AGG": ("bond_fund", 1, "Total bond market fund",
            "Nearly identical to BND, run by a different company. Either one does the job."),
    "LQD": ("bond_fund", 2, "Corporate bond fund",
            "Debt issued by financially solid companies rather than the government. Pays more "
            "than Treasuries, and carries some risk the company struggles."),
    "TIP": ("bond_fund", 1, "Inflation-protected bonds",
            "Government bonds whose value rises with inflation. Held specifically to stop "
            "inflation quietly eroding your savings."),
    "HYG": ("bond_fund", 3, "High-yield ('junk') bond fund",
            "Debt from companies with weaker finances. Pays noticeably more interest because "
            "some of these companies do default. Behaves more like stocks than like bonds in "
            "a crisis."),
    "^TNX": ("bond_yield", 1, "10-year Treasury rate",
             "The interest rate the US government pays to borrow for 10 years. It is the "
             "reference rate for mortgages, loans and how expensive every stock looks. When "
             "this rises, stocks usually get cheaper."),
    "^TYX": ("bond_yield", 1, "30-year Treasury rate",
             "The government's 30-year borrowing rate. Reflects long-run expectations for "
             "growth and inflation."),
    "^IRX": ("bond_yield", 1, "3-month Treasury rate",
             "The government's short-term borrowing rate, which tracks Federal Reserve policy "
             "closely. Roughly what a savings account should pay you."),
}

# -------------------------------------------------------------- the indexes
INDEXES = {
    "^GSPC": ("index", 2, "S&P 500 index",
              "The scoreboard for the 500 largest US companies. When people say 'the market' "
              "was up, they usually mean this. You cannot buy it directly - SPY or VOO is how."),
    "^DJI": ("index", 2, "Dow Jones index",
             "An older, narrower scoreboard of 30 large companies. Quoted often out of habit; "
             "the S&P 500 is the better measure."),
    "^IXIC": ("index", 3, "Nasdaq Composite index",
              "A scoreboard weighted toward technology companies. Moves more than the S&P 500."),
    "^RUT": ("index", 3, "Russell 2000 index",
             "The scoreboard for 2,000 smaller US companies. Often read as a health check on "
             "the domestic economy."),
    "^VIX": ("volatility", 3, "The 'fear gauge'",
             "Measures how much movement traders expect in the next month. It is not something "
             "to buy - it is a mood reading. Below 15 means calm, above 30 means fear."),
}

# ------------------------------------------------------------- the companies
_SECTOR = {
    "AAPL": "iPhones, Macs and a large services business",
    "MSFT": "Windows, Office and Azure cloud computing",
    "NVDA": "the chips that nearly all AI systems run on",
    "GOOGL": "Google Search, YouTube and Android",
    "AMZN": "online retail and AWS cloud computing",
    "META": "Facebook, Instagram and WhatsApp",
    "TSLA": "electric cars, batteries and self-driving software",
    "AVGO": "networking and custom AI chips, plus enterprise software",
    "AMD": "computer and AI chips, Nvidia's main rival",
    "INTC": "computer chips; the former leader, now trying to catch up",
    "TSM": "the factory that physically makes most advanced chips",
    "MU": "memory chips, including the memory AI systems need",
    "ORCL": "database software and cloud computing",
    "CRM": "Salesforce customer-management software",
    "ADBE": "Photoshop, Acrobat and creative software",
    "QCOM": "the chips and patents inside most smartphones",
    "TXN": "the unglamorous analog chips inside cars and machines",
    "NFLX": "Netflix streaming",
    "UBER": "ride-hailing and food delivery",
    "PLTR": "data analysis software for governments and large companies",
    "COIN": "a cryptocurrency exchange; effectively a bet on crypto",
    "JPM": "the largest US bank",
    "BAC": "a large consumer and commercial bank",
    "GS": "investment banking and trading",
    "V": "the Visa payment network - it takes a fee on card transactions",
    "MA": "the Mastercard payment network",
    "LLY": "drugs, including the Zepbound and Mounjaro weight-loss treatments",
    "UNH": "health insurance and healthcare services",
    "JNJ": "medicines and medical devices",
    "PFE": "vaccines and medicines",
    "WMT": "Walmart stores and a growing online business",
    "COST": "Costco membership warehouses",
    "HD": "Home Depot home improvement stores",
    "MCD": "McDonald's restaurants, largely a franchising and property business",
    "NKE": "Nike footwear and clothing",
    "SBUX": "Starbucks coffee shops",
    "KO": "Coca-Cola drinks",
    "PG": "Tide, Gillette, Pampers and other household brands",
    "DIS": "Disney films, theme parks and streaming",
    "XOM": "ExxonMobil oil and gas",
    "CVX": "Chevron oil and gas",
    # not in the tracked watchlist, but they turn up in the news
    "WBD": "Warner Bros. Discovery - HBO, CNN and film studios",
    "PARA": "Paramount - CBS, film studios and streaming",
    "CMCSA": "Comcast - cable, broadband and NBCUniversal",
    "DKS": "Dick's Sporting Goods retail stores",
    "LULU": "Lululemon athletic clothing",
    "BBY": "Best Buy electronics stores",
    "TGT": "Target retail stores",
    "SNAP": "Snapchat",
    "PINS": "Pinterest",
    "RBLX": "the Roblox gaming platform",
    "ABNB": "Airbnb short-stay rentals",
    "DASH": "DoorDash food delivery",
    "LYFT": "Lyft ride-hailing",
    "SPOT": "Spotify music streaming",
    "HOOD": "the Robinhood trading app",
    "MRVL": "Marvell custom data-centre chips",
    "SMCI": "Super Micro AI servers",
    "ASML": "the machines that print the world's most advanced chips",
    "ARM": "the chip designs inside almost every phone",
    "DELL": "Dell computers and servers",
    "SHOP": "Shopify online-store software",
    "SNOW": "Snowflake cloud data software",
    "CRWD": "CrowdStrike cybersecurity",
    "PANW": "Palo Alto Networks cybersecurity",
    "NOW": "ServiceNow workflow software",
    "IBM": "IBM enterprise computing and consulting",
    "NVO": "Novo Nordisk - Ozempic and Wegovy",
    "MSTR": "a company that mostly holds bitcoin",
    "F": "Ford cars and trucks",
    "GM": "General Motors cars and trucks",
    "RIVN": "Rivian electric trucks",
    "LCID": "Lucid electric cars",
    "BA": "Boeing aircraft",
    "LMT": "Lockheed Martin defence systems",
    "RTX": "RTX aerospace and defence",
    "CAT": "Caterpillar construction machinery",
    "BABA": "Alibaba - Chinese e-commerce",
    "PYPL": "PayPal online payments",
    "MS": "Morgan Stanley investment banking",
    "WFC": "Wells Fargo banking",
    "C": "Citigroup banking",
    "BRK-B": "Berkshire Hathaway - Warren Buffett's holding company",
    "VST": "Vistra electricity generation",
    "CEG": "Constellation Energy - nuclear power",
    "NEE": "NextEra - utilities and renewable energy",
}

# A beginner should not have to know that AVGO means Broadcom.
COMPANY_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon", "META": "Meta (Facebook)", "TSLA": "Tesla", "AVGO": "Broadcom",
    "AMD": "AMD", "INTC": "Intel", "TSM": "TSMC", "MU": "Micron", "ORCL": "Oracle",
    "CRM": "Salesforce", "ADBE": "Adobe", "QCOM": "Qualcomm", "TXN": "Texas Instruments",
    "NFLX": "Netflix", "UBER": "Uber", "PLTR": "Palantir", "COIN": "Coinbase",
    "JPM": "JPMorgan Chase", "BAC": "Bank of America", "GS": "Goldman Sachs",
    "V": "Visa", "MA": "Mastercard", "LLY": "Eli Lilly", "UNH": "UnitedHealth",
    "JNJ": "Johnson & Johnson", "PFE": "Pfizer", "WMT": "Walmart", "COST": "Costco",
    "HD": "Home Depot", "MCD": "McDonald's", "NKE": "Nike", "SBUX": "Starbucks",
    "KO": "Coca-Cola", "PG": "Procter & Gamble", "DIS": "Disney", "XOM": "ExxonMobil",
    "CVX": "Chevron",
    # news-only names
    "WBD": "Warner Bros. Discovery", "PARA": "Paramount", "CMCSA": "Comcast",
    "DKS": "Dick's Sporting Goods", "LULU": "Lululemon", "BBY": "Best Buy",
    "TGT": "Target", "SNAP": "Snap", "PINS": "Pinterest", "RBLX": "Roblox",
    "ABNB": "Airbnb", "DASH": "DoorDash", "LYFT": "Lyft", "SPOT": "Spotify",
    "HOOD": "Robinhood", "MRVL": "Marvell", "SMCI": "Super Micro", "ASML": "ASML",
    "ARM": "Arm Holdings", "DELL": "Dell", "SHOP": "Shopify", "SNOW": "Snowflake",
    "CRWD": "CrowdStrike", "PANW": "Palo Alto Networks", "NOW": "ServiceNow",
    "IBM": "IBM", "NVO": "Novo Nordisk", "MSTR": "Strategy (MicroStrategy)",
    "F": "Ford", "GM": "General Motors", "RIVN": "Rivian", "LCID": "Lucid",
    "BA": "Boeing", "LMT": "Lockheed Martin", "RTX": "RTX", "CAT": "Caterpillar",
    "BABA": "Alibaba", "PYPL": "PayPal", "MS": "Morgan Stanley", "WFC": "Wells Fargo",
    "C": "Citigroup", "BRK-B": "Berkshire Hathaway", "VST": "Vistra",
    "CEG": "Constellation Energy", "NEE": "NextEra Energy",
}

# Large, profitable, slow-moving companies carry less risk than growth names.
_STEADY = {"JNJ", "PG", "KO", "MCD", "WMT", "COST", "V", "MA", "JPM", "UNH", "HD", "XOM", "CVX"}
_VOLATILE = {"TSLA", "COIN", "PLTR", "ARKK", "MU", "INTC", "AMD"}


def _stock_entry(sym):
    what = _SECTOR.get(sym, "an individual public company")
    risk = 3 if sym in _STEADY else (5 if sym in _VOLATILE else 4)
    return ("stock", risk, COMPANY_NAMES.get(sym, sym), f"A single company: {what}.")


def blurb(symbol):
    """The one-line 'what they actually do', for use under the name."""
    entry = ASSETS.get(symbol)
    if entry is not None:
        return entry[0]
    return _SECTOR.get(symbol, "")


ASSETS = {}
ASSETS.update(FUNDS)
ASSETS.update(BONDS)
ASSETS.update(INDEXES)


def info(symbol):
    """Return {kind, kind_label, risk, risk_label, risk_note, name, plain}."""
    entry = ASSETS.get(symbol)
    if entry is None:
        entry = _stock_entry(symbol)
    kind, risk, name, plain = entry
    risk_label, risk_note = RISK_WORDS[risk]
    return {
        "symbol": symbol, "kind": kind, "kind_label": KIND_WORDS.get(kind, kind),
        "risk": risk, "risk_label": risk_label, "risk_note": risk_note,
        "name": name, "plain": plain,
    }
