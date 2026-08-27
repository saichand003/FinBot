"""Crypto market data via CoinGecko's free public API."""
import requests

import config
import db


def crawl_crypto():
    url = config.COINGECKO_MARKETS_URL.format(ids=",".join(config.CRYPTO_IDS))
    try:
        r = requests.get(url, headers={"User-Agent": config.USER_AGENT},
                         timeout=config.REQUEST_TIMEOUT)
        r.raise_for_status()
        coins = r.json()
    except Exception as ex:
        print(f"[crypto] fetch failed: {ex}")
        return 0
    rows = [{
        "coin": c["id"],
        "price": c.get("current_price"),
        "mcap": c.get("market_cap"),
        "chg_1h": c.get("price_change_percentage_1h_in_currency"),
        "chg_24h": c.get("price_change_percentage_24h_in_currency"),
        "chg_7d": c.get("price_change_percentage_7d_in_currency"),
        "chg_30d": c.get("price_change_percentage_30d_in_currency"),
    } for c in coins]
    n = db.insert_many("crypto_snapshots", rows)
    print(f"[crypto] {n} snapshots stored")
    return n
