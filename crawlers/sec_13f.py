"""Institutional portfolios via SEC EDGAR 13F filings.

Note: SEC requires a descriptive User-Agent with contact info and
max ~10 requests/second. We stay far below that.
"""
import time

import requests

import config
import db

HEADERS = {"User-Agent": config.USER_AGENT}


def crawl_13f_filings():
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
    print(f"[13f] {n} new filings indexed")
    return n
