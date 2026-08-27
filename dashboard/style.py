"""The design system: one token set, both themes, all three theme states.

Concept - "the annotated wire". FinBot reads the wires and writes the margin
notes, so the page is built like a wire service that annotates itself: priority
flags, datelines, slugs. Brass is the identity accent and is never used to mean
up or down; jade / rust / slate-violet carry direction, so colour always means
exactly one thing.
"""

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400"
         "&family=IBM+Plex+Sans:wght@400;500;600;700"
         "&family=IBM+Plex+Mono:wght@400;500;600"
         "&display=swap")

CSS = r"""
/* ============================ tokens ============================ */
:root {
  /* light: warm wire-copy paper */
  --ground:#F7F4EE; --surface:#FFFDF9; --raised:#F1ECE1; --line:#E2DACB;
  --line-soft:#EDE7DA;
  --ink:#191C21; --ink-2:#4A4E56; --muted:#7A7264;
  --accent:#9A6F1E; --accent-soft:#F0E4C9; --accent-ink:#6E4E12;
  --up:#1E7D5C; --up-soft:#DCEFE6; --down:#B23A2E; --down-soft:#F7E2DE;
  --vol:#4F55A8; --vol-soft:#E4E5F5;
  --shadow:0 1px 2px rgba(25,28,33,.06), 0 8px 24px -16px rgba(25,28,33,.28);
  --radius:10px; --radius-sm:6px;
  --font-display:"Newsreader", Georgia, "Times New Roman", serif;
  --font-body:"IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono:"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground:#101418; --surface:#171C22; --raised:#1E242C; --line:#2A323C;
    --line-soft:#222933;
    --ink:#E8EBEF; --ink-2:#B4BCC7; --muted:#8792A1;
    --accent:#C89B4A; --accent-soft:#2C2618; --accent-ink:#E0B96F;
    --up:#4CB98C; --up-soft:#15261F; --down:#E2695E; --down-soft:#2A1917;
    --vol:#8D93DC; --vol-soft:#1C1D2C;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -18px rgba(0,0,0,.8);
  }
}
:root[data-theme="dark"] {
  --ground:#101418; --surface:#171C22; --raised:#1E242C; --line:#2A323C;
  --line-soft:#222933;
  --ink:#E8EBEF; --ink-2:#B4BCC7; --muted:#8792A1;
  --accent:#C89B4A; --accent-soft:#2C2618; --accent-ink:#E0B96F;
  --up:#4CB98C; --up-soft:#15261F; --down:#E2695E; --down-soft:#2A1917;
  --vol:#8D93DC; --vol-soft:#1C1D2C;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -18px rgba(0,0,0,.8);
}

/* ============================ base ============================ */
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--font-body); font-size:15px; line-height:1.55;
  -webkit-font-smoothing:antialiased;
}
h1,h2,h3,h4{margin:0; text-wrap:balance; font-weight:600}
p{margin:0}
a{color:inherit}
button{font:inherit; color:inherit; background:none; border:none; cursor:pointer}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px; border-radius:3px}
.num{font-family:var(--font-mono); font-variant-numeric:tabular-nums; letter-spacing:-.01em}
.up{color:var(--up)} .down{color:var(--down)} .vol{color:var(--vol)}
.wrap{max-width:1280px; margin:0 auto; padding:0 20px}

/* eyebrow / slug: the wire-service label */
.slug{
  font-family:var(--font-mono); font-size:10.5px; font-weight:600;
  letter-spacing:.14em; text-transform:uppercase; color:var(--muted);
}

/* ============================ masthead ============================ */
.masthead{
  position:sticky; top:0; z-index:50; background:var(--ground);
  border-bottom:1px solid var(--line);
}
.masthead-in{display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; padding:14px 20px;
  max-width:1280px; margin:0 auto}
.brand{font-family:var(--font-display); font-size:26px; font-weight:600; letter-spacing:-.01em}
.brand em{font-style:normal; color:var(--accent)}
.dateline{font-family:var(--font-mono); font-size:11.5px; color:var(--muted);
  letter-spacing:.04em; text-transform:uppercase}
.mast-stats{margin-left:auto; display:flex; gap:16px; align-items:baseline; flex-wrap:wrap}
.mast-stat{font-family:var(--font-mono); font-size:11.5px; color:var(--muted); white-space:nowrap}
.mast-stat b{color:var(--ink); font-weight:600}
.theme-toggle{
  border:1px solid var(--line); border-radius:var(--radius-sm); padding:5px 10px;
  font-family:var(--font-mono); font-size:11px; color:var(--muted); letter-spacing:.06em;
}
.theme-toggle:hover{border-color:var(--accent); color:var(--accent)}

/* ============================ the tape ============================ */
.tape{border-bottom:1px solid var(--line); background:var(--surface); overflow:hidden}
.tape-scroll{display:flex; gap:0; overflow-x:auto; scrollbar-width:thin;
  max-width:1280px; margin:0 auto; padding:0 8px}
.tape-scroll::-webkit-scrollbar{height:4px}
.tape-scroll::-webkit-scrollbar-thumb{background:var(--line); border-radius:2px}
.tick{
  flex:0 0 auto; display:flex; align-items:baseline; gap:8px; padding:10px 14px;
  border-right:1px solid var(--line-soft); white-space:nowrap; cursor:pointer;
  transition:background .12s ease;
}
.tick:hover{background:var(--raised)}
.tick[aria-pressed="true"]{background:var(--accent-soft)}
.tick-sym{font-family:var(--font-mono); font-size:12px; font-weight:600; letter-spacing:.02em}
.tick-px{font-family:var(--font-mono); font-size:12px; color:var(--ink-2);
  font-variant-numeric:tabular-nums}
.tick-chg{font-family:var(--font-mono); font-size:11.5px; font-weight:600;
  font-variant-numeric:tabular-nums}

/* ============================ leader ============================ */
.leader{border-bottom:1px solid var(--line); padding:34px 0 30px; background:var(--surface)}
.leader-grid{display:grid; grid-template-columns:minmax(0,1fr) 300px; gap:40px; align-items:start}
.leader h2{
  font-family:var(--font-display); font-size:clamp(23px,3vw,31px); font-weight:500;
  line-height:1.28; letter-spacing:-.012em; margin:10px 0 14px;
}
.leader-body{font-size:16px; line-height:1.68; color:var(--ink-2); max-width:66ch}
.leader-body b{color:var(--ink); font-weight:600}
.gauges{display:flex; flex-direction:column; gap:2px; border-left:2px solid var(--accent);
  padding-left:16px}
.gauge{display:flex; justify-content:space-between; align-items:baseline; gap:14px;
  padding:7px 0; border-bottom:1px solid var(--line-soft)}
.gauge:last-child{border-bottom:none}
.gauge-k{font-family:var(--font-mono); font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted)}
.gauge-v{font-family:var(--font-mono); font-size:15px; font-weight:600;
  font-variant-numeric:tabular-nums}
.gauge-note{font-size:11.5px; color:var(--muted); line-height:1.4; padding:2px 0 8px}

/* ============================ layout ============================ */
.main{display:grid; grid-template-columns:minmax(0,1fr) 348px; gap:36px;
  padding:32px 0 64px; align-items:start}
.section-head{display:flex; align-items:baseline; gap:12px; margin-bottom:14px;
  padding-bottom:9px; border-bottom:2px solid var(--ink)}
.section-head h3{font-family:var(--font-display); font-size:19px; font-weight:600;
  letter-spacing:-.01em}
.section-head .count{margin-left:auto; font-family:var(--font-mono); font-size:11px;
  color:var(--muted)}
.rail{display:flex; flex-direction:column; gap:26px; position:sticky; top:74px}
.rail .section-head{border-bottom-width:1px; border-bottom-color:var(--line)}

/* ============================ controls ============================ */
.controls{display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:16px}
.search{
  flex:1 1 210px; min-width:170px; display:flex; align-items:center; gap:8px;
  background:var(--surface); border:1px solid var(--line); border-radius:var(--radius-sm);
  padding:7px 11px;
}
.search:focus-within{border-color:var(--accent)}
.search input{flex:1; border:none; background:none; outline:none; color:var(--ink);
  font-family:var(--font-body); font-size:13.5px; min-width:0}
.search input::placeholder{color:var(--muted)}
.search kbd{font-family:var(--font-mono); font-size:10px; color:var(--muted);
  border:1px solid var(--line); border-radius:3px; padding:1px 5px}
.chip{
  border:1px solid var(--line); background:var(--surface); border-radius:100px;
  padding:5px 12px; font-family:var(--font-mono); font-size:11px; font-weight:500;
  letter-spacing:.04em; color:var(--muted); transition:all .12s ease; white-space:nowrap;
}
.chip:hover{border-color:var(--accent); color:var(--accent)}
.chip[aria-pressed="true"]{background:var(--ink); border-color:var(--ink); color:var(--ground)}
.chip.f-bull[aria-pressed="true"]{background:var(--up); border-color:var(--up); color:#fff}
.chip.f-bear[aria-pressed="true"]{background:var(--down); border-color:var(--down); color:#fff}
.chip.f-vol[aria-pressed="true"]{background:var(--vol); border-color:var(--vol); color:#fff}
.activefilter{
  display:none; align-items:center; gap:10px; margin-bottom:14px; padding:9px 13px;
  background:var(--accent-soft); border-left:3px solid var(--accent);
  border-radius:0 var(--radius-sm) var(--radius-sm) 0; font-size:13px;
}
.activefilter.on{display:flex}
.activefilter b{font-family:var(--font-mono); color:var(--accent-ink)}
.activefilter button{margin-left:auto; font-family:var(--font-mono); font-size:11px;
  color:var(--accent-ink); text-decoration:underline; letter-spacing:.04em}

/* ============================ wire items ============================ */
.wire{display:flex; flex-direction:column; gap:0}
.item{border-bottom:1px solid var(--line-soft); padding:16px 0 15px}
.item[hidden]{display:none}
.item-top{display:flex; align-items:center; gap:9px; margin-bottom:7px; flex-wrap:wrap}
.flag{
  font-family:var(--font-mono); font-size:9.5px; font-weight:600; letter-spacing:.12em;
  padding:2.5px 7px; border-radius:3px; text-transform:uppercase;
}
.flag-HIGH{background:var(--ink); color:var(--ground)}
.flag-MEDIUM{background:var(--raised); color:var(--ink-2); border:1px solid var(--line)}
.flag-LOW{background:none; color:var(--muted); border:1px solid var(--line)}
.dir{font-family:var(--font-mono); font-size:10.5px; font-weight:600; letter-spacing:.08em;
  text-transform:uppercase}
.dir-1{color:var(--up)} .dir--1{color:var(--down)} .dir-0{color:var(--vol)}
.src{font-family:var(--font-mono); font-size:10.5px; color:var(--muted); letter-spacing:.05em}
.item-title{
  font-family:var(--font-display); font-size:17.5px; font-weight:500; line-height:1.34;
  letter-spacing:-.008em; cursor:pointer; margin-bottom:8px;
}
.item-title:hover{color:var(--accent)}
.tkrs{display:flex; gap:5px; flex-wrap:wrap; align-items:center}
.tkr{
  font-family:var(--font-mono); font-size:11px; font-weight:600; letter-spacing:.03em;
  padding:2.5px 7px; border-radius:3px; border:1px solid var(--line);
  background:var(--surface); color:var(--ink-2); cursor:pointer;
}
.tkr:hover{border-color:var(--accent); color:var(--accent)}
.tkr.k-direct{border-color:var(--accent); color:var(--accent-ink); background:var(--accent-soft)}
.tkr.k-indirect{opacity:.72; border-style:dashed}
.evt{font-family:var(--font-mono); font-size:10.5px; color:var(--muted); letter-spacing:.03em}

.detail{display:none; margin-top:13px; padding-left:15px; border-left:2px solid var(--line)}
.item.open .detail{display:block}
.detail p{font-size:14.2px; line-height:1.66; color:var(--ink-2); margin-bottom:9px; max-width:68ch}
.detail p b{color:var(--ink); font-weight:600}
.detail p em{color:var(--muted)}

.ladder{margin:14px 0 12px}
.ladder-h{font-family:var(--font-mono); font-size:10px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--muted); margin-bottom:8px}
.rung{display:grid; grid-template-columns:58px 76px 1fr; gap:11px; align-items:center;
  padding:3.5px 0; font-size:12.5px}
.rung-sym{font-family:var(--font-mono); font-size:11.5px; font-weight:600; cursor:pointer}
.rung-sym:hover{color:var(--accent)}
.bar{height:5px; background:var(--raised); border-radius:3px; overflow:hidden}
.bar span{display:block; height:100%; border-radius:3px}
.rung-why{color:var(--muted); font-size:12px; line-height:1.4}
.stance{
  margin-top:12px; padding:11px 13px; background:var(--raised); border-radius:var(--radius-sm);
  font-size:13.4px; line-height:1.58; color:var(--ink-2);
}
.stance strong{font-family:var(--font-mono); font-size:10px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--muted); display:block; margin-bottom:4px}
.readmore{font-family:var(--font-mono); font-size:11px; color:var(--accent);
  letter-spacing:.05em; margin-top:11px; display:inline-block; text-decoration:none}
.readmore:hover{text-decoration:underline}
.empty{padding:40px 0; text-align:center; color:var(--muted); font-size:14px}

/* ============================ rail cards ============================ */
.card{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  overflow:hidden; box-shadow:var(--shadow)}
.note{padding:13px 15px; border-bottom:1px solid var(--line-soft); cursor:pointer}
.note:last-child{border-bottom:none}
.note:hover{background:var(--raised)}
.note-h{display:flex; align-items:baseline; gap:8px; font-size:13.4px; font-weight:600;
  line-height:1.4}
.note-h .sev{width:6px; height:6px; border-radius:50%; flex:0 0 auto; margin-top:6px}
.sev-HIGH{background:var(--accent)} .sev-MEDIUM{background:var(--muted)}
.sev-LOW{background:var(--line)}
.note-b{display:none; margin-top:8px; font-size:12.8px; line-height:1.6; color:var(--ink-2)}
.note-b b{color:var(--ink)}
.note.open .note-b{display:block}
.mom{display:flex; gap:3px; margin-top:9px; align-items:flex-end; height:26px}
.mom-c{flex:1; display:flex; flex-direction:column; align-items:center; gap:3px}
.mom-b{width:100%; border-radius:2px; min-height:2px}
.mom-l{font-family:var(--font-mono); font-size:8.5px; color:var(--muted); letter-spacing:.04em}
.crumb{font-family:var(--font-mono); font-size:10.5px; color:var(--muted); margin-top:5px}

/* ============================ footer ============================ */
.foot{border-top:1px solid var(--line); padding:26px 0 44px; color:var(--muted); font-size:12.5px}
.foot-grid{display:flex; gap:28px; flex-wrap:wrap; align-items:baseline}
.foot a{color:var(--accent)}
.disclaimer{margin-top:12px; max-width:74ch; line-height:1.6}

/* ============================ responsive ============================ */
@media (max-width:1000px){
  .main{grid-template-columns:1fr; gap:32px}
  .leader-grid{grid-template-columns:1fr; gap:24px}
  .rail{position:static}
  .gauges{border-left:none; border-top:2px solid var(--accent); padding-left:0; padding-top:12px}
}
@media (max-width:620px){
  body{font-size:14.5px}
  .wrap{padding:0 15px}
  .masthead-in{padding:12px 15px; gap:10px}
  .brand{font-size:21px}
  .mast-stats{width:100%; margin-left:0; gap:12px}
  .item-title{font-size:16px}
  .rung{grid-template-columns:52px 58px 1fr; gap:8px}
  .rung-why{font-size:11.5px}
  .leader h2{font-size:21px}
  .leader-body{font-size:15px}
}
@media (prefers-reduced-motion:reduce){
  *{animation:none !important; transition:none !important; scroll-behavior:auto !important}
}
"""


# Layered on top of CSS: the beginner-facing surfaces and the plain/expert switch.
CSS_PLAIN = r"""
/* ---------------------- mode switch ---------------------- */
.modebar{
  display:flex; align-items:center; gap:10px; flex-wrap:wrap;
  padding:11px 0; border-bottom:1px solid var(--line);
}
.modebar .slug{margin-right:2px}
.seg{display:inline-flex; border:1px solid var(--line); border-radius:100px; overflow:hidden}
.seg button{
  padding:6px 15px; font-family:var(--font-mono); font-size:11px; letter-spacing:.05em;
  color:var(--muted); background:var(--surface); transition:all .12s ease;
}
.seg button[aria-pressed="true"]{background:var(--accent); color:#fff}
:root[data-theme="dark"] .seg button[aria-pressed="true"]{color:#151109}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]) .seg button[aria-pressed="true"]{color:#151109}
}
.modehint{font-size:12.5px; color:var(--muted)}

/* Plain is the default with no JS involved, so the page never flashes both
   versions before the script runs. */
body:not(.mode-expert) .expert-only{display:none !important}
body.mode-expert .plain-only{display:none !important}

/* ---------------------- primer ---------------------- */
.primer{border-bottom:1px solid var(--line); background:var(--raised)}
.primer-in{padding:26px 0 30px}
.primer h3{font-family:var(--font-display); font-size:22px; margin:8px 0 6px}
.primer .lede{font-size:15px; color:var(--ink-2); max-width:70ch; line-height:1.65; margin-bottom:20px}
.cards3{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px}
.pcard{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); padding:15px 17px}
.pcard h4{font-family:var(--font-display); font-size:16.5px; margin-bottom:6px}
.pcard p{font-size:13.4px; line-height:1.6; color:var(--ink-2)}
.ladder-risk{display:flex; flex-direction:column; gap:7px; margin-top:18px}
.lr{display:grid; grid-template-columns:76px 108px 1fr; gap:12px; align-items:baseline;
  padding:7px 0; border-bottom:1px solid var(--line-soft); font-size:13.2px}
.lr:last-child{border-bottom:none}
.lr-name{font-family:var(--font-mono); font-size:11px; letter-spacing:.06em;
  text-transform:uppercase; color:var(--muted)}
.lr-why{color:var(--ink-2); line-height:1.5}

/* ---------------------- risk dots ---------------------- */
.dots{display:inline-flex; gap:3px; align-items:center}
.dot{width:6px; height:6px; border-radius:50%; background:var(--line)}
.dot.on-1{background:var(--up)} .dot.on-2{background:var(--up)}
.dot.on-3{background:var(--accent)} .dot.on-4{background:var(--down)}
.dot.on-5{background:var(--down)}

/* ---------------------- browse ---------------------- */
.group{margin-bottom:26px}
.group-h{display:flex; align-items:baseline; gap:10px; flex-wrap:wrap; margin-bottom:4px}
.group-h h4{font-family:var(--font-display); font-size:18px}
.group-h .n{font-family:var(--font-mono); font-size:11px; color:var(--muted)}
.group-blurb{font-size:13.4px; color:var(--muted); line-height:1.55; margin-bottom:11px; max-width:72ch}
.assets{border:1px solid var(--line); border-radius:var(--radius); overflow:hidden;
  background:var(--surface)}
.asset{border-bottom:1px solid var(--line-soft)}
.asset:last-child{border-bottom:none}
.asset[hidden]{display:none}
.asset-row{
  display:grid; grid-template-columns:66px 1fr 84px 78px 62px; gap:12px; align-items:center;
  padding:11px 15px; cursor:pointer; text-align:left; width:100%;
}
.asset-row:hover{background:var(--raised)}
.asset-sym{font-family:var(--font-mono); font-size:12.5px; font-weight:600}
.asset-name{font-size:13.6px; line-height:1.35}
.asset-name small{display:block; color:var(--muted); font-size:11.5px; margin-top:1px}
.asset-px{font-family:var(--font-mono); font-size:12.5px; text-align:right;
  font-variant-numeric:tabular-nums}
.asset-chg{font-family:var(--font-mono); font-size:12.5px; font-weight:600; text-align:right;
  font-variant-numeric:tabular-nums}
.asset-risk{display:flex; justify-content:flex-end}
.asset-body{display:none; padding:2px 15px 17px; border-top:1px dashed var(--line)}
.asset.open .asset-body{display:block}
.asset-body p{font-size:13.8px; line-height:1.65; color:var(--ink-2); margin:10px 0 0; max-width:70ch}
.tag{
  display:inline-block; font-family:var(--font-mono); font-size:10px; letter-spacing:.09em;
  text-transform:uppercase; padding:3px 9px; border-radius:100px; margin:12px 0 2px;
  background:var(--accent-soft); color:var(--accent-ink); border:1px solid var(--accent);
}
.watch{margin-top:12px; padding:11px 13px; border-left:3px solid var(--down);
  background:var(--down-soft); border-radius:0 var(--radius-sm) var(--radius-sm) 0;
  font-size:13.2px; line-height:1.6; color:var(--ink-2)}
.watch b{color:var(--ink)}
.facts{display:flex; gap:20px; flex-wrap:wrap; margin-top:12px}
.fact{font-size:12px; color:var(--muted)}
.fact b{display:block; font-family:var(--font-mono); font-size:14px; color:var(--ink);
  font-variant-numeric:tabular-nums; margin-top:2px}

/* ---------------------- glossary ---------------------- */
.term{
  border-bottom:1px dotted var(--accent); cursor:help; color:inherit;
  text-decoration:none; padding:0;
}
.term:hover{background:var(--accent-soft)}
dialog.gloss{
  border:1px solid var(--line); border-radius:var(--radius); background:var(--surface);
  color:var(--ink); max-width:400px; padding:20px 22px; box-shadow:var(--shadow);
}
dialog.gloss::backdrop{background:rgba(0,0,0,.5)}
dialog.gloss h5{font-family:var(--font-display); font-size:19px; margin-bottom:9px}
dialog.gloss p{font-size:14.2px; line-height:1.62; color:var(--ink-2)}
dialog.gloss button{margin-top:16px; font-family:var(--font-mono); font-size:11px;
  letter-spacing:.06em; color:var(--accent); text-decoration:underline}

/* ---------------------- plain news ---------------------- */
.plainbox{margin-top:11px; padding:12px 14px; background:var(--raised);
  border-radius:var(--radius-sm)}
.plainbox p{font-size:14px; line-height:1.62; color:var(--ink-2); margin-bottom:7px; max-width:68ch}
.plainbox p:last-child{margin-bottom:0}
.meaning{margin-top:11px; font-size:13.4px; line-height:1.6; color:var(--muted)}

@media (max-width:620px){
  .asset-row{grid-template-columns:56px 1fr 70px; gap:9px; row-gap:3px}
  .asset-chg{grid-column:3; text-align:right}
  .asset-px{display:none}
  .asset-risk{grid-column:2 / 4; justify-content:flex-start; margin-top:2px}
  .lr{grid-template-columns:1fr; gap:2px}
}
"""
