"""Congressional stock trades from the official House Clerk disclosures.

Members of Congress must file a Periodic Transaction Report (PTR) within 45
days of any trade over $1,000 - that is the STOCK Act. The House Clerk publishes
a yearly ZIP containing an XML index of every filing, which is what we read.

The XML index gives us who filed, when, and the document ID. The per-trade
detail (ticker, amount range, buy/sell) lives in the linked PDF, so FinBot
records the filing plus a direct link rather than pretending to know the ticker.
That is an honest representation of what the free public feed actually offers.
"""
import io
import zipfile
import datetime as dt
import xml.etree.ElementTree as ET

import requests

import config
import db

HEADERS = {"User-Agent": config.USER_AGENT}

FILING_TYPES = {
    "P": "Periodic Transaction Report",
    "A": "Annual Report",
    "C": "Candidate Report",
    "D": "Termination Report",
    "O": "Original Report",
    "X": "Extension",
    "T": "Trust Report",
    "W": "Withdrawal",
}


def _fetch_year(year):
    """Download and parse one year's disclosure index."""
    url = config.HOUSE_FD_ZIP_URL.format(year=year)
    r = requests.get(url, headers=HEADERS, timeout=config.REQUEST_TIMEOUT * 2)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".xml"))
        return ET.fromstring(z.read(name))


def _iso(us_date):
    """The Clerk emits M/D/YYYY; store ISO so date comparisons work in SQL."""
    try:
        return dt.datetime.strptime(us_date.strip(), "%m/%d/%Y").date().isoformat()
    except (ValueError, AttributeError):
        return us_date or ""


def crawl_congress_trades():
    rows = []
    this_year = dt.date.today().year
    years = [this_year - i for i in range(max(1, config.HOUSE_FD_YEARS))]

    for year in years:
        try:
            root = _fetch_year(year)
        except Exception as ex:
            print(f"[congress] {year} index fetch failed: {ex}")
            continue

        for m in root:
            ftype = (m.findtext("FilingType") or "").strip()
            if ftype != "P":            # only transaction reports move markets
                continue
            last = (m.findtext("Last") or "").strip()
            first = (m.findtext("First") or "").strip()
            name = f"{first} {last}".strip()
            if config.TRACKED_POLITICIANS and not any(
                p.lower() == last.lower() for p in config.TRACKED_POLITICIANS
            ):
                continue
            doc_id = (m.findtext("DocID") or "").strip()
            filed = _iso(m.findtext("FilingDate") or "")
            rows.append({
                "chamber": "house",
                "politician": name,
                "ticker": "",
                "asset": f"{FILING_TYPES.get(ftype, ftype)} ({m.findtext('StateDst') or '?'})",
                "tx_type": "Periodic Transaction Report",
                "tx_date": filed,
                "amount": "see filing",
                "disclosed": filed,
                "doc_url": config.HOUSE_PTR_PDF_URL.format(year=year, doc_id=doc_id),
                "source": "house_clerk",
            })

    rows.sort(key=lambda r: r["disclosed"], reverse=True)
    rows = rows[:config.MAX_CONGRESS_FILINGS]
    n = db.insert_many("congress_trades", rows)
    print(f"[congress] {n} new transaction reports stored ({len(rows)} matched filter)")
    return n
