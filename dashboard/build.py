"""Assemble the dashboard page and write it to disk."""
import pathlib

from dashboard import data, render
from dashboard.script import JS
from dashboard.style import CSS, FONTS

TITLE = "FinBot Wire"
DESCRIPTION = ("Every headline read for what it moves, with the numbers explained "
               "instead of just printed.")


def render_body(d):
    """The page content, without the document shell.

    Kept separate so the same markup can be published as an Artifact, which
    supplies its own <html>/<head>/<body>.
    """
    counts = d["counts"]
    return f"""
<header class="masthead"><div class="masthead-in">
  <div>
    <div class="brand">Fin<em>Bot</em></div>
  </div>
  <div class="dateline">{render.e(d['generated'])}</div>
  <div class="mast-stats">
    <span class="mast-stat"><b>{counts['analysed']}</b> headlines read</span>
    <span class="mast-stat"><b>{counts['high']}</b> high conviction</span>
    <span class="mast-stat"><b>{counts['symbols']}</b> symbols tracked</span>
    <button class="theme-toggle" id="theme" aria-label="Switch colour theme">DARK</button>
  </div>
</div></header>

{render.render_tape(d['markets'])}
{render.render_leader(d)}

<div class="wrap"><div class="main">
  <main>{render.render_wire(d['insights'])}</main>
  <div class="rail">
    {render.render_notes("Movers", "what the number actually means",
                         d['movers'], d['stats'], 8)}
    {render.render_notes("Patterns", "signals, with their failure modes",
                         d['pattern_notes'], d['stats'], 6)}
    {render.render_notes("Crypto", "24-hour swings in context",
                         d['crypto_notes'], None, 6)}
    {render.render_congress(d['congress'])}
    {render.render_filings(d['filings'])}
  </div>
</div></div>

<footer class="foot"><div class="wrap">
  <div class="foot-grid">
    <span class="slug">FinBot &middot; generated {render.e(d['generated_iso'])}</span>
    <span>Sources: RSS newswires, yfinance, CoinGecko, SEC EDGAR, House Clerk disclosures.</span>
  </div>
  <p class="disclaimer">Every impact estimate on this page is produced by a rule-based
  engine matching known event patterns against a peer and supply-chain graph. It reflects
  how these events have typically propagated, not a forecast of what will happen. Nothing
  here is investment advice, none of it has been reviewed by a human, and the analysis can
  be confidently wrong. Verify against the source story before acting on anything.</p>
</div></footer>

<script>{JS}</script>"""


def build_dashboard(path="index.html", title=TITLE):
    d = data.collect()
    body = render_body(d)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{render.e(DESCRIPTION)}">
<meta name="color-scheme" content="light dark">
<title>{render.e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""
    out = pathlib.Path(path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"[dashboard] wrote {out} ({len(doc)//1024} KB, "
          f"{len(d['insights'])} stories, {len(d['commentary'])} notes)")
    return out


def build_fragment(path):
    """Body-only build for publishing as an Artifact."""
    d = data.collect()
    frag = (f'<title>{render.e(TITLE)}</title>\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n'
            f'<style>{CSS}</style>\n{render_body(d)}')
    out = pathlib.Path(path).resolve()
    out.write_text(frag, encoding="utf-8")
    print(f"[dashboard] wrote fragment {out} ({len(frag)//1024} KB)")
    return out
