"""Institutional portfolios via SEC EDGAR 13F filings.

Note: SEC requires a descriptive User-Agent with contact info and
max ~10 requests/second. We stay far below that.
"""
import time

import requests

import config
import db

HEADERS = {"User-Agent": config.USER_AGENT}


def _fresh_enough(max_age_hours=24):
    """13F filings arrive quarterly, so re-checking hourly just wastes SEC's
    bandwidth. Skip if we already looked recently."""
    with db.conn() as c:
        row = c.execute(
            "SELECT value FROM meta WHERE key='last_13f_check'").fetchone()
        if not row:
            return False
        hit = c.execute(
            "SELECT 1 FROM meta WHERE key='last_13f_check' "
            "AND value >= datetime('now', ?)", (f"-{max_age_hours} hours",)).fetchone()
    return bool(hit)


def crawl_13f_filings(force=False):
    if not force and _fresh_enough():
        print("[13f] checked within the last day, skipping")
        return 0
    rows = []
    for fund, cik in config.TRACKED_FUNDS.items():
        url = config.SEC_SUBMISSIONS_URL.format(cik=cik.zfill(10))
        try:
            r = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT)
            r.raise_for_status()
            recent = r.json()["filings"]["recent"]
        except Exception as ex:
            print(f"[13f] {fund} failed: {ex}")
            continue
        for form, date, acc, doc in zip(
            recent["form"], recent["filingDate"],
            recent["accessionNumber"], recent["primaryDocument"],
        ):
            if not form.startswith("13F"):
                continue
            acc_clean = acc.replace("-", "")
            rows.append({
                "fund": fund,
                "cik": cik,
                "form": form,
                "filing_date": date,
                "accession": acc,
                "doc_url": (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{int(cik)}/{acc_clean}/{doc}"
                ),
            })
        time.sleep(config.CRAWL_DELAY_SECONDS)
    n = db.insert_many("fund_filings", rows)
    with db.conn() as c:
        c.execute("INSERT INTO meta (key, value) VALUES ('last_13f_check', datetime('now')) "
                  "ON CONFLICT(key) DO UPDATE SET value = excluded.value")
    print(f"[13f] {n} new filings indexed")
    return n
