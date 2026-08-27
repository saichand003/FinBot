"""Render the collected data into the dashboard page."""
import html
import re

from dashboard.style import CSS, FONTS

DIR_LABEL = {1: "bullish", -1: "bearish", 0: "two-sided"}
DIR_MARK = {1: "▲", -1: "▼", 0: "◆"}
DIR_VAR = {1: "var(--up)", -1: "var(--down)", 0: "var(--vol)"}

TAPE_ORDER = ["^GSPC", "^IXIC", "^DJI", "^RUT", "^VIX", "^TNX",
              "SPY", "QQQ", "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META",
              "TSLA", "AVGO", "VTI", "ARKK", "XLK", "XLF", "TLT", "HYG",
              "^TYX", "^IRX"]

PRETTY = {"^GSPC": "S&P 500", "^IXIC": "Nasdaq", "^DJI": "Dow", "^RUT": "Russell",
          "^VIX": "VIX", "^TNX": "US 10Y", "^TYX": "US 30Y", "^IRX": "US 3M"}


def e(s):
    return html.escape(str(s if s is not None else ""))


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITAL = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")


def md(text):
    """The narrative uses **bold** / *italic*; convert to HTML, escaping first."""
    out = e(text)
    out = _BOLD.sub(r"<b>\1</b>", out)
    out = _ITAL.sub(r"<em>\1</em>", out)
    return "".join(f"<p>{line}</p>" for line in out.split("\n") if line.strip())


def pct(v, digits=2):
    return "—" if v is None else f"{v:+.{digits}f}%"


def cls(v):
    return "up" if (v or 0) > 0 else ("down" if (v or 0) < 0 else "")


def money(v):
    if v is None:
        return "—"
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if abs(v) >= 1:
        return f"{v:,.2f}"
    return f"{v:,.4f}"


# ------------------------------------------------------------------- tape
def render_tape(markets):
    by = {m["symbol"]: m for m in markets}
    order = [s for s in TAPE_ORDER if s in by] + [s for s in by if s not in TAPE_ORDER]
    out = []
    for sym in order:
        m = by[sym]
        chg = m["change_pct"]
        out.append(
            f'<button class="tick" data-ticker="{e(sym)}" aria-pressed="false" '
            f'title="Filter the wire to {e(sym)}">'
            f'<span class="tick-sym">{e(PRETTY.get(sym, sym))}</span>'
            f'<span class="tick-px">{money(m["price"])}</span>'
            f'<span class="tick-chg {cls(chg)}">{pct(chg)}</span></button>'
        )
    return f'<div class="tape"><div class="tape-scroll">{"".join(out)}</div></div>'


# ----------------------------------------------------------------- leader
def render_leader(d):
    lead = d["lead"]
    counts = d["counts"]
    by = {m["symbol"]: m for m in d["markets"]}

    headline = e(lead["headline"]) if lead else "No market read available yet"
    body = md(lead["body"]) if lead else "<p>Run a crawl to populate the dashboard.</p>"

    gauges = []

    def gauge(key, value, tone="", note=""):
        gauges.append(
            f'<div class="gauge"><span class="gauge-k">{e(key)}</span>'
            f'<span class="gauge-v {tone}">{value}</span></div>'
            + (f'<div class="gauge-note">{e(note)}</div>' if note else "")
        )

    eq = [m for m in d["markets"] if m["asset_class"] in ("stock", "etf_fund")
          and m["change_pct"] is not None]
    if eq:
        up = sum(1 for m in eq if m["change_pct"] > 0)
        gauge("Breadth", f"{up}/{len(eq)}", cls(up - len(eq) / 2),
              "Tracked equities advancing. Wide participation is the healthy kind of rally.")
    if "^VIX" in by and by["^VIX"]["price"]:
        v = by["^VIX"]["price"]
        gauge("VIX", f"{v:.1f}", "",
              "Under 15 is complacency; over 30 is panic, which is historically closer to lows.")
    if "^TNX" in by and by["^TNX"]["price"]:
        y = by["^TNX"]["price"]
        gauge("US 10Y", f"{y:.2f}%", "",
              "The denominator in every equity valuation. Growth reacts to this before it reacts to itself.")
    btc = next((c for c in d["crypto"] if c["coin"] == "bitcoin"), None)
    if btc:
        gauge("Bitcoin", f"${btc['price']:,.0f}", cls(btc["chg_24h"]),
              f"{pct(btc['chg_24h'], 1)} over 24h. Sets the beta for the whole crypto complex.")
    gauge("Analysed", f"{counts['high']}/{counts['analysed']}", "",
          "High-conviction stories out of every headline read this cycle.")

    return f"""
<section class="leader"><div class="wrap"><div class="leader-grid">
  <div>
    <div class="slug">The read &middot; {e(d['generated'])}</div>
    <h2>{headline}</h2>
    <div class="leader-body">{body}</div>
  </div>
  <aside class="gauges">{''.join(gauges)}</aside>
</div></div></section>"""


# ------------------------------------------------------------------- wire
def render_item(ins, idx):
    d = ins["direction"] or 0
    tickers = ins["ticker_list"]
    impacts = ins["impacts"]

    # ticker chips, direct hits highlighted over implied exposure
    kinds = {i["ticker"]: i["kind"] for i in impacts}
    chips = "".join(
        f'<button class="tkr k-{e(kinds.get(t, "direct"))}" data-ticker="{e(t)}">{e(t)}</button>'
        for t in tickers[:6]
    )
    if not tickers and impacts:
        chips = "".join(
            f'<button class="tkr k-{e(i["kind"])}" data-ticker="{e(i["ticker"])}">{e(i["ticker"])}</button>'
            for i in impacts[:5]
        )

    events = " &middot; ".join(e(x) for x in ins["event_list"][:3])

    # the impact ladder: real magnitudes, coloured by direction
    rungs = []
    for i in impacts:
        w = max(4, min(100, round(i["magnitude"] * 100)))
        rungs.append(
            f'<div class="rung">'
            f'<button class="rung-sym" data-ticker="{e(i["ticker"])}">{e(i["ticker"])}</button>'
            f'<div class="bar"><span style="width:{w}%;background:{DIR_VAR[i["direction"]]}"></span></div>'
            f'<div class="rung-why">{DIR_MARK[i["direction"]]} {e(i["reason"])}</div>'
            f'</div>'
        )
    ladder = ""
    if rungs:
        ladder = (f'<div class="ladder"><div class="ladder-h">Expected impact &middot; '
                  f'bar length = estimated magnitude</div>{"".join(rungs)}</div>')

    link = (f'<a class="readmore" href="{e(ins["url"])}" target="_blank" '
            f'rel="noopener noreferrer">Read the source story &rarr;</a>'
            if ins.get("url") else "")

    search_blob = e(f"{ins['title']} {ins['tickers']} {ins['event_labels']} {ins['narrative']}").lower()

    return f"""
<article class="item" data-idx="{idx}" data-dir="{d}" data-conf="{e(ins['confidence'])}"
         data-score="{ins['score'] or 0}" data-tickers="{e(','.join(t for t in tickers) or ','.join(i['ticker'] for i in impacts))}"
         data-text="{search_blob}">
  <div class="item-top">
    <span class="flag flag-{e(ins['confidence'])}">{e(ins['confidence'])}</span>
    <span class="dir dir-{d}">{DIR_MARK[d]} {e(DIR_LABEL[d])}</span>
    <span class="src">{e(ins['source'])}</span>
    {f'<span class="evt">{events}</span>' if events else ''}
  </div>
  <h4 class="item-title" role="button" tabindex="0">{e(ins['title'])}</h4>
  <div class="tkrs">{chips}</div>
  <div class="detail">
    {md(ins['narrative'])}
    {ladder}
    <div class="stance"><strong>Stance</strong>{e(ins['suggestion'])}</div>
    {link}
  </div>
</article>"""


def render_wire(insights):
    items = "".join(render_item(i, n) for n, i in enumerate(insights))
    return f"""
<section>
  <div class="section-head">
    <h3>The annotated wire</h3>
    <span class="slug">every headline, read for what it moves</span>
    <span class="count" id="wire-count">{len(insights)} stories</span>
  </div>
  <div class="controls">
    <label class="search">
      <span class="slug">Find</span>
      <input type="search" id="q" placeholder="ticker, company, or event…"
             aria-label="Search headlines and analysis">
      <kbd>/</kbd>
    </label>
    <button class="chip f-all" data-filter="all" aria-pressed="true">All</button>
    <button class="chip f-bull" data-filter="1" aria-pressed="false">Bullish</button>
    <button class="chip f-bear" data-filter="-1" aria-pressed="false">Bearish</button>
    <button class="chip f-vol" data-filter="0" aria-pressed="false">Two-sided</button>
    <button class="chip" data-conf="HIGH" aria-pressed="false">High conviction</button>
    <button class="chip" id="expand-all" aria-pressed="false">Expand all</button>
  </div>
  <div class="activefilter" id="activefilter">
    Filtered to <b id="af-label"></b>
    <button id="af-clear">clear</button>
  </div>
  <div class="wire" id="wire">{items}</div>
  <div class="empty" id="empty" hidden>Nothing matches that filter.</div>
</section>"""


# ------------------------------------------------------------------- rail
def momentum(stats):
    """Four real returns as bars - honest data, not a decorative sparkline."""
    keys = [("ret_1w", "1W"), ("ret_1m", "1M"), ("ret_3m", "3M"), ("ret_6m", "6M")]
    vals = [(stats.get(k), lbl) for k, lbl in keys]
    if not any(v is not None for v, _ in vals):
        return ""
    peak = max((abs(v) for v, _ in vals if v is not None), default=1) or 1
    cols = []
    for v, lbl in vals:
        h = 2 if v is None else max(2, round(abs(v) / peak * 22))
        colour = "var(--line)" if v is None else (
            "var(--up)" if v > 0 else "var(--down)")
        title = "no data" if v is None else f"{lbl} {v:+.1f}%"
        cols.append(f'<div class="mom-c" title="{e(title)}">'
                    f'<div class="mom-b" style="height:{h}px;background:{colour}"></div>'
                    f'<div class="mom-l">{lbl}</div></div>')
    return f'<div class="mom">{"".join(cols)}</div>'


def render_notes(title, slug, notes, stats=None, limit=8):
    if not notes:
        return ""
    out = []
    for n in notes[:limit]:
        mom = momentum(stats.get(n["symbol"], {})) if stats and n["symbol"] in (stats or {}) else ""
        out.append(
            f'<div class="note" role="button" tabindex="0">'
            f'<div class="note-h"><span class="sev sev-{e(n["severity"])}"></span>'
            f'<span>{e(n["headline"])}</span></div>'
            f'<div class="note-b">{md(n["body"])}{mom}</div></div>'
        )
    return f"""
<section>
  <div class="section-head"><h3>{e(title)}</h3><span class="count">{len(notes)}</span></div>
  <div class="slug" style="margin-bottom:10px">{e(slug)}</div>
  <div class="card">{''.join(out)}</div>
</section>"""


def render_congress(rows):
    if not rows:
        return ""
    out = []
    for r in rows[:8]:
        link = (f'<a href="{e(r["doc_url"])}" target="_blank" rel="noopener noreferrer">'
                f'view filing &rarr;</a>' if r.get("doc_url") else "")
        out.append(
            f'<div class="note"><div class="note-h"><span class="sev sev-MEDIUM"></span>'
            f'<span>{e(r["politician"])}</span></div>'
            f'<div class="crumb">{e(r["disclosed"])} &middot; {e(r["tx_type"])} &middot; {link}</div>'
            f'</div>')
    return f"""
<section>
  <div class="section-head"><h3>Congress</h3><span class="count">{len(rows)}</span></div>
  <div class="slug" style="margin-bottom:10px">STOCK Act filings &middot; House Clerk</div>
  <div class="card">{''.join(out)}</div>
</section>"""


def render_filings(rows):
    if not rows:
        return ""
    out = []
    for r in rows[:6]:
        out.append(
            f'<div class="note"><div class="note-h"><span class="sev sev-LOW"></span>'
            f'<span>{e(r["fund"])}</span></div>'
            f'<div class="crumb">{e(r["filing_date"])} &middot; {e(r["form"])} &middot; '
            f'<a href="{e(r["doc_url"])}" target="_blank" rel="noopener noreferrer">'
            f'SEC filing &rarr;</a></div></div>')
    return f"""
<section>
  <div class="section-head"><h3>13F filings</h3><span class="count">{len(rows)}</span></div>
  <div class="slug" style="margin-bottom:10px">Institutional portfolios &middot; SEC EDGAR</div>
  <div class="card">{''.join(out)}</div>
</section>"""
