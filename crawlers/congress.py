"""Congressional stock trades from public STOCK Act disclosure datasets.

These are legally mandated public filings; the S3 datasets mirror the
official House/Senate clerk disclosures.
"""
import requests

import config
import db

HEADERS = {"User-Agent": config.USER_AGENT}


def _fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def crawl_congress_trades():
    rows = []
    for chamber, url in (("senate", config.SENATE_TRADES_URL),
                         ("house", config.HOUSE_TRADES_URL)):
        try:
            data = _fetch(url)
        except Exception as ex:
            print(f"[congress] {chamber} fetch failed: {ex}")
            continue
        for t in data:
            name = t.get("senator") or t.get("representative") or ""
            if config.TRACKED_POLITICIANS and not any(
                p.lower() in name.lower() for p in config.TRACKED_POLITICIANS
            ):
                continue
            rows.append({
                "chamber": chamber,
                "politician": name,
                "ticker": (t.get("ticker") or "").strip("-$ "),
                "asset": t.get("asset_description", ""),
                "tx_type": t.get("type", ""),
                "tx_date": t.get("transaction_date", ""),
                "amount": t.get("amount", ""),
                "disclosed": t.get("disclosure_date", ""),
            })
    n = db.insert_many("congress_trades", rows)
    print(f"[congress] {n} new trades stored ({len(rows)} matched filter)")
    return n
