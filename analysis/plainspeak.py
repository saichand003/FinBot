"""Explain the market in words a beginner actually uses.

Two jobs:

  1. `GLOSSARY` - every piece of jargon on the dashboard, defined in one plain
     sentence, so a term can be tapped rather than googled.

  2. `beginner_read()` - an honest assessment of what an asset looks like right
     now: what it is, how risky, what the numbers say in plain words, and the
     mistake people most often make with this *kind* of thing.

On the question this is really answering - "should I buy it?" - the honest
position is that nobody can tell you that from price data alone. It depends on
your timeline, your income, your existing savings and your tolerance for a bad
year. So this module does the useful, truthful version instead: it tells you
what kind of thing you are looking at, how much it can hurt you, whether the
price is stretched or beaten down right now, and the specific error beginners
make with that category. Judgement stays with you, but it is an informed one.
"""
from analysis.assets import info

# --------------------------------------------------------------- glossary
GLOSSARY = {
    "ETF": "A fund you buy like a single share, which itself owns hundreds of "
           "different companies. One purchase, instant diversification.",
    "index fund": "A fund that simply owns everything in a market index rather than "
                  "trying to pick winners. Cheap, and historically hard to beat.",
    "dividend": "A cash payment a company sends its shareholders, usually quarterly. "
                "Your share of the profits.",
    "bond": "A loan you make to a government or company. They pay you interest and "
            "return your money on an agreed date.",
    "yield": "The annual interest a bond pays, as a percentage of its price.",
    "volume": "How many shares changed hands. High volume means a lot of people acted, "
              "so the price move is more likely to stick.",
    "RSI": "A 0-100 score of how hard something has been bought or sold lately. Above 70 "
           "means it has run up fast; below 30 means it has been sold off hard. Neither "
           "is a signal on its own.",
    "moving average": "The average price over the last N days, which smooths out daily "
                      "noise so you can see the underlying direction.",
    "50-day average": "The average closing price over the last 50 trading days - a read on "
                      "the medium-term direction.",
    "200-day average": "The average closing price over the last 200 trading days. Trading "
                       "above it is generally considered a healthy long-term trend.",
    "golden cross": "When the 50-day average rises above the 200-day average. Traders read "
                    "it as a trend turning positive. It describes the past, not the future.",
    "death cross": "When the 50-day average falls below the 200-day average - the negative "
                   "mirror of a golden cross.",
    "52-week high": "The highest price over the past year.",
    "52-week low": "The lowest price over the past year.",
    "market cap": "The total value of a company: share price times number of shares.",
    "VIX": "The 'fear gauge'. It measures how much movement traders expect over the next "
           "month. Below 15 is calm, above 30 is fear.",
    "S&P 500": "An index tracking the 500 largest US companies. The usual shorthand for "
               "'the US stock market'.",
    "the Fed": "The US central bank. It sets the interest rate that ripples through "
               "mortgages, savings accounts and every stock price.",
    "interest rates": "The cost of borrowing money. When rates rise, borrowing gets "
                      "expensive, and stocks generally become less attractive versus bonds.",
    "inflation": "The rate at which prices rise. It decides what the Fed does with interest "
                 "rates, which is why markets react so sharply to inflation reports.",
    "earnings": "A company's quarterly profit report. The most-watched scheduled event for "
                "any individual stock.",
    "guidance": "A company's own forecast for its next quarter. Often moves the share price "
                "more than the profit it just reported.",
    "consensus": "The average forecast of the analysts who cover a stock. 'Beating "
                 "estimates' means doing better than this number.",
    "volatility": "How much a price swings around. High volatility means large moves in "
                  "both directions.",
    "diversification": "Spreading money across many different things so no single failure "
                       "can badly hurt you. The one thing nearly all advisers agree on.",
    "dollar-cost averaging": "Investing a fixed amount on a fixed schedule regardless of "
                             "price. It removes the need to guess the right moment to buy.",
    "bull / bullish": "Expecting prices to rise.",
    "bear / bearish": "Expecting prices to fall.",
    "overbought": "Has risen quickly and may be due a pause. Not a reliable sell signal - "
                  "strong things stay overbought for a long time.",
    "oversold": "Has fallen quickly and may be due a bounce. Not a reliable buy signal - "
                "cheap things can get cheaper.",
    "13F filing": "A form large investment funds must file quarterly, listing what they own. "
                  "It is up to 45 days old by the time you see it.",
    "STOCK Act": "The law requiring members of Congress to disclose their trades, within 45 "
                 "days of making them.",
}

# ----------------------------------------------- events, without the jargon
# Keyed on the event label the insight engine produces. The expert version
# explains the mechanism; this explains the consequence.
PLAIN_EVENT = {
    "Earnings beat": "The company made more profit than experts expected. Usually good for the share price.",
    "Earnings miss": "The company made less profit than experts expected. Usually bad for the share price.",
    "Earnings event": "The company is reporting its quarterly profits. The price often jumps either way on the day.",
    "Guidance raise": "The company told investors it expects to do better than it previously said. This is one of the strongest good signs there is.",
    "Guidance cut": "The company told investors it expects to do worse than it previously said. This is one of the strongest bad signs there is.",
    "Record revenue": "The company sold more than ever before.",
    "Record profit": "The company earned more than ever before.",
    "Profit warning": "The company warned in advance that profits will disappoint.",
    "M&A": "One company is buying another. The company being bought usually jumps; the buyer often dips because it is spending money and taking on risk.",
    "M&A target": "Someone wants to buy this company. Buyers normally have to offer more than the current price, which puts a floor under it.",
    "Buyback": "The company is buying back its own shares. Fewer shares means each remaining one owns a bigger slice of the profits.",
    "Dividend hike": "The company is raising the cash payment it sends shareholders - a sign management is confident.",
    "Dividend cut": "The company is reducing the cash it pays shareholders, which usually means it is short of money.",
    "Stock split": "The company is dividing its shares into more, cheaper ones. Nothing about the business changes.",
    "Spin-off": "The company is splitting off part of itself into a separate business.",
    "Bankruptcy": "The company cannot pay its debts. Shareholders usually lose everything.",
    "Layoffs": "The company is cutting jobs. Lower costs help profits short term, but it can also mean business is slowing.",
    "Product recall": "The company has to take a product back and fix it. That costs money and damages trust.",
    "Service outage": "The company's service stopped working, which costs it revenue and credibility.",
    "Data breach": "Customer data was stolen. Expect fines, repair costs and lost customers.",
    "Cyber incident": "The company was attacked by hackers.",
    "Labour strike": "Workers have stopped working, so the company cannot produce as much.",
    "Production halt": "The company has stopped making something. Those lost sales rarely come back.",
    "Supply chain": "The company is struggling to get the parts or goods it needs.",
    "Pricing power": "The company raised prices and customers kept buying - a genuinely strong sign.",
    "Price cut": "The company cut prices, which usually means it is fighting to keep customers.",
    "Partnership": "The company has teamed up with another, which normally means new customers or credibility.",
    "Contract win": "The company won new business, so future revenue is more certain.",
    "Analyst upgrade": "A professional analyst became more positive on the stock. Big funds often follow.",
    "Analyst downgrade": "A professional analyst became more negative on the stock. Big funds often follow.",
    "Target change": "Analysts changed their estimate of what the share is worth.",
    "New coverage": "Analysts have started covering this stock, which brings it to more investors' attention.",
    "Short report": "An investor who profits if the price falls has published claims against the company.",
    "Insider selling": "People who run the company are selling their own shares. Mildly worrying.",
    "Insider buying": "People who run the company are buying its shares with their own money. One of the more trustworthy good signs.",
    "Index inclusion": "The company is joining a major index, so every fund tracking that index has to buy it.",
    "Antitrust": "Regulators say the company has too much market power. This threatens how it makes money, not just its cash.",
    "Litigation": "The company is being sued.",
    "Regulatory probe": "An official investigation has been opened into the company.",
    "Investigation": "Authorities are looking into the company.",
    "Regulatory fine": "The company has to pay a penalty.",
    "Legal settlement": "The company settled a legal dispute, which removes uncertainty.",
    "FDA approval": "A drug was approved for sale. It can now actually make money.",
    "FDA rejection": "A drug was refused approval, so the sales everyone expected disappear.",
    "Trial data": "Results from a medical trial. These are all-or-nothing events for drug companies.",
    "Export controls": "The government is restricting what can be sold abroad, which removes customers.",
    "Tariffs": "Taxes on imported goods. Someone has to absorb the extra cost - the company or you.",
    "Sanctions": "Countries or companies are barred from doing business, closing off markets.",
    "Regulation": "New rules the company must follow, which usually costs money.",
    "Rate cut": "The central bank is making borrowing cheaper. Good for shares in general, especially fast-growing companies. Bad for savings account rates.",
    "Rate hike": "The central bank is making borrowing more expensive. Generally bad for shares, especially fast-growing ones. Good for savings rates and banks.",
    "Inflation data": "New figures on how fast prices are rising. This decides what the central bank does next, which moves everything.",
    "CPI print": "The main inflation report. One of the biggest scheduled events for the whole market.",
    "Jobs data": "Employment figures. A strong job market is good for company profits but can mean interest rates stay high.",
    "Labour data": "Figures on employment and wages.",
    "Recession risk": "Concern the economy will shrink. Company profits fall in a recession.",
    "GDP data": "A measure of how fast the economy is growing.",
    "Fed policy": "News about the US central bank, which sets the interest rate everything else is priced against.",
    "FOMC": "The meeting where the US central bank sets interest rates. One of the biggest scheduled market events.",
    "Rates move": "Interest rates on government debt have moved, which changes how expensive shares look.",
    "Oil move": "The oil price has moved. It is a cost for airlines and manufacturers, and revenue for energy companies.",
    "OPEC": "The group of oil-producing countries has made a decision about supply, which moves the oil price.",
    "China exposure": "Something involving China, a huge market for chipmakers, luxury goods and industrial firms.",
    "Trade tension": "Countries are putting up barriers to trade, which raises costs.",
    "Shutdown risk": "The US government may run out of funding. Historically markets shrug this off.",
    "Crypto ETF flows": "Money moving into or out of bitcoin funds, currently the main driver of the crypto price.",
    "Bitcoin halving": "A scheduled event that halves the rate of new bitcoin creation - less new supply.",
    "Regulatory approval": "Regulators approved something, opening it up to large institutional money.",
    "Stablecoin policy": "Rules about crypto tokens pegged to the dollar, which connect crypto to normal banking.",
    "IPO": "A company is listing on the stock market for the first time.",
}


# Technical signals, said plainly. The caveat matters as much as the signal.
PLAIN_PATTERN = {
    "rsi_overbought": "has been bought hard lately. It may keep climbing, but buying now "
                      "means paying up after the move.",
    "rsi_oversold": "has been sold off hard lately. Bounces get more likely from here, "
                    "though something cheap can always get cheaper.",
    "golden_cross": "just had its medium-term trend turn upward. This describes what has "
                    "already happened rather than predicting what comes next.",
    "death_cross": "just had its medium-term trend turn downward. It is a late signal - "
                   "often the fall has already happened.",
    "52wk_high": "hit its highest price in a year. Nobody holding it is losing money, so "
                 "there is less pressure to sell.",
    "52wk_low": "hit its lowest price in a year. Everyone who bought in the past year is "
                "down, and many will sell on any recovery.",
    "volume_spike": "traded far more than usual, which means large investors were moving. "
                    "Something happened worth reading about.",
}


def plain_pattern(name):
    return PLAIN_PATTERN.get(name, name.replace("_", " "))


def plain_breadth(up, total, avg, vix=None):
    """The market-wide read, without the trading-desk vocabulary."""
    pct_up = up / total * 100 if total else 0
    if pct_up >= 70:
        mood = "Most things went up today"
    elif pct_up >= 55:
        mood = "Slightly more things went up than down"
    elif pct_up >= 45:
        mood = "The market was split roughly evenly"
    elif pct_up >= 30:
        mood = "Slightly more things went down than up"
    else:
        mood = "Most things went down today"
    out = (f"{mood}: {up} of the {total} companies and funds FinBot tracks rose, "
           f"averaging {avg:+.2f}%.")
    if vix is not None:
        if vix < 15:
            out += (f" The market's nervousness gauge is low at {vix:.0f}, meaning investors "
                    f"are calm - which is also when surprises hurt most.")
        elif vix < 20:
            out += f" The nervousness gauge is normal at {vix:.0f}."
        elif vix < 30:
            out += (f" The nervousness gauge is raised at {vix:.0f} - expect bigger daily "
                    f"swings than usual.")
        else:
            out += (f" The nervousness gauge is high at {vix:.0f}, which means real fear. "
                    f"Historically these periods have been closer to lows than to tops.")
    return out


def plain_event(label):
    return PLAIN_EVENT.get(label, "")


# --------------------------------------------------------- number → plain words
def _price_story(st):
    """Translate the statistics into sentences with no jargon in them."""
    out = []
    if not st:
        return out

    from_hi, r1m, r6m = st.get("pct_from_hi"), st.get("ret_1m"), st.get("ret_6m")
    rsi, trend = st.get("rsi"), st.get("trend")

    if from_hi is not None:
        if from_hi >= -2:
            out.append("It is at, or very near, its highest price of the past year.")
        elif from_hi >= -10:
            out.append(f"It is {abs(from_hi):.0f}% below its highest price of the past year - "
                       f"close to the top of its range.")
        elif from_hi >= -25:
            out.append(f"It is {abs(from_hi):.0f}% below its high for the year, so it has given "
                       f"back a meaningful part of its gains.")
        else:
            out.append(f"It is {abs(from_hi):.0f}% below its high for the year. Something has "
                       f"gone wrong, or the whole sector is out of favour.")

    if r1m is not None and r6m is not None:
        if r1m > 10:
            out.append(f"It has risen {r1m:.0f}% in the past month alone ({r6m:+.0f}% over six "
                       f"months). That is a fast move, and fast moves often pause.")
        elif r1m < -10:
            out.append(f"It has fallen {abs(r1m):.0f}% in the past month ({r6m:+.0f}% over six "
                       f"months).")
        else:
            out.append(f"Over the past month it is {r1m:+.0f}%, and over six months {r6m:+.0f}%.")

    if trend and trend not in ("insufficient history",):
        plain = {
            "uptrend": "The general direction over recent months has been upward.",
            "downtrend": "The general direction over recent months has been downward.",
            "pullback in uptrend": "The longer trend is upward, but it has dipped recently.",
            "bounce in downtrend": "The longer trend is downward, though it has bounced lately.",
            "range-bound": "It has been moving sideways rather than trending.",
            "short-term uptrend": "It has been rising recently, but there is not enough history "
                                  "to judge the longer trend.",
        }.get(trend)
        if plain:
            out.append(plain)

    if rsi is not None:
        if rsi >= 70:
            out.append("Buyers have been in control recently - it has been bought hard. This "
                       "does not mean it will fall, but you would be paying up after the move.")
        elif rsi <= 30:
            out.append("Sellers have been in control recently - it has been sold off hard. That "
                       "raises the odds of a bounce, but does not make it a bargain.")
    return out


# ------------------------------------------------------------ the honest read
def _category_warning(meta, st):
    """The mistake people actually make with this *kind* of asset."""
    kind, risk = meta["kind"], meta["risk"]
    r1m = (st or {}).get("ret_1m")

    if kind in ("broad_etf", "intl_etf") and risk <= 2:
        return ("This is the category most people are pointed to when they start, because one "
                "purchase spreads your money across hundreds of companies. The usual approach "
                "with a fund like this is not to guess the right day, but to buy a fixed amount "
                "on a regular schedule and leave it alone for years.")
    if kind == "dividend_etf":
        return ("Dividend funds pay you cash regularly, which feels reassuring. The trade-off is "
                "usually slower growth - and dividends are taxable in most accounts, so check "
                "how that works where you live before choosing these over a broad fund.")
    if kind == "sector_etf":
        return ("A sector fund is a bet that one industry beats the rest. It is more "
                "concentrated than a broad fund, so it can lag the market for years. Most "
                "beginners are better served owning the whole market first, and adding sector "
                "bets later if they have a specific view.")
    if kind == "commodity_etf":
        return ("This produces nothing and pays no dividend - its price only moves because "
                "someone else will pay more or less for it. People hold it as insurance against "
                "inflation and crises, not as a way to grow money over decades.")
    if kind == "growth_etf" or risk == 5:
        return ("Genuinely high risk. This kind of holding has lost most of its value before and "
                "can do so again. If you own it, it should be money you can lose entirely "
                "without changing your life.")
    if kind == "bond_fund":
        if meta["symbol"] in ("TLT",):
            return ("The trap here is assuming 'government bond' means 'safe from losses'. You "
                    "will be repaid, but if interest rates rise the price can fall sharply in "
                    "the meantime. Long-dated bonds are for a specific view on rates, not for "
                    "parking cash.")
        if meta["symbol"] == "HYG":
            return ("Despite being a bond fund, this behaves like stocks when markets fall - the "
                    "companies borrowing here are the ones most likely to struggle in a "
                    "downturn. It does not provide the cushion people expect from bonds.")
        return ("Bonds are the steadying part of a portfolio. They will not make you rich; they "
                "reduce how much your total savings swing when stocks fall.")
    if kind == "bond_yield":
        return ("This is an interest rate, not something you can buy. Watch it because it sets "
                "the backdrop: when it rises, stocks generally get cheaper, and savings "
                "accounts get more attractive.")
    if kind in ("index", "volatility"):
        return ("This is a scoreboard, not a purchase. It tells you how the market is doing "
                "overall - useful context for everything else on this page.")
    if kind == "stock":
        base = ("Owning one company means one bad quarter, one lawsuit or one failed product can "
                "hit you hard - a risk that owning a broad fund spreads away. Common guidance is "
                "to keep individual stocks to a small slice of your total savings.")
        if r1m is not None and r1m > 15:
            base += (" It has also run up sharply in the past month, and buying right after a "
                     "steep rise is the single most common beginner mistake.")
        return base
    return ""


def _stance(meta, st):
    """A short label plus one honest sentence. Never a directive to trade."""
    risk = meta["risk"]
    kind = meta["kind"]
    from_hi = (st or {}).get("pct_from_hi")
    r1m = (st or {}).get("ret_1m")

    if kind in ("index", "volatility", "bond_yield"):
        return ("Context, not a purchase",
                "You cannot buy this. It is here to tell you what the wider market is doing.")

    if risk >= 5:
        return ("Not a beginner holding",
                "High enough risk that it should not be an early purchase, whatever the chart "
                "is doing right now.")

    if risk <= 2 and kind in ("broad_etf", "intl_etf", "dividend_etf", "bond_fund"):
        if r1m is not None and r1m > 12:
            return ("Sensible category, hot moment",
                    "The category is a reasonable long-term starting point, but it has just run "
                    "up sharply. If you are investing regularly, that matters far less than it "
                    "feels like it does.")
        return ("Reasonable starting point",
                "This is the kind of holding most beginner guidance is built around: broad, "
                "cheap, and boring on purpose.")

    if risk == 3:
        if from_hi is not None and from_hi <= -25:
            return ("Out of favour",
                    "Well off its highs. That is either an opportunity or a warning, and price "
                    "data alone cannot tell you which - you would need a view on why it fell.")
        return ("Concentrated bet",
                "More focused than a broad fund, so expect a bumpier ride and be clear about "
                "why you want this specifically.")

    if r1m is not None and r1m > 15:
        return ("Expensive to chase",
                "A single company that has just risen sharply. Chasing a move like this is the "
                "most common way beginners lose money.")
    if from_hi is not None and from_hi <= -30:
        return ("Beaten down",
                "A single company a long way off its high. Cheap and broken look identical on a "
                "chart - the difference is in the business, not the price.")
    return ("Single-company risk",
            "One company's fortunes. Fine as a small position, risky as a large one.")


def beginner_read(symbol, stats=None):
    """The full plain-English assessment for one symbol."""
    meta = info(symbol)
    label, verdict = _stance(meta, stats)
    return {
        **meta,
        "story": _price_story(stats),
        "warning": _category_warning(meta, stats),
        "stance_label": label,
        "stance": verdict,
    }
