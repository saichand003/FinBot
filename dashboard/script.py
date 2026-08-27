"""Client-side behaviour: filtering, search, and progressive disclosure.

No framework and no external requests - the page has to work as a local file,
on GitHub Pages, and inside an Artifact sandbox with a strict CSP.
"""

JS = r"""
(function () {
  var wire = document.getElementById('wire');
  if (!wire) return;
  var items = Array.prototype.slice.call(wire.querySelectorAll('.item'));
  var q = document.getElementById('q');
  var countEl = document.getElementById('wire-count');
  var emptyEl = document.getElementById('empty');
  var afEl = document.getElementById('activefilter');
  var afLabel = document.getElementById('af-label');

  var state = { dir: 'all', conf: null, ticker: null, text: '' };

  function apply() {
    var shown = 0;
    items.forEach(function (el) {
      var ok = true;
      if (state.dir !== 'all' && el.dataset.dir !== state.dir) ok = false;
      if (ok && state.conf && el.dataset.conf !== state.conf) ok = false;
      if (ok && state.ticker) {
        var list = (el.dataset.tickers || '').split(',');
        if (list.indexOf(state.ticker) === -1) ok = false;
      }
      if (ok && state.text && el.dataset.text.indexOf(state.text) === -1) ok = false;
      el.hidden = !ok;
      if (ok) shown++;
    });
    countEl.textContent = shown + (shown === 1 ? ' story' : ' stories');
    emptyEl.hidden = shown !== 0;

    var bits = [];
    if (state.ticker) bits.push(state.ticker);
    if (state.conf) bits.push(state.conf.toLowerCase() + ' conviction');
    if (state.text) bits.push('"' + state.text + '"');
    if (bits.length) { afLabel.textContent = bits.join(' + '); afEl.classList.add('on'); }
    else afEl.classList.remove('on');

    document.querySelectorAll('.tick').forEach(function (t) {
      t.setAttribute('aria-pressed', String(t.dataset.ticker === state.ticker));
    });
  }

  // direction + conviction chips
  document.querySelectorAll('.chip[data-filter]').forEach(function (b) {
    b.addEventListener('click', function () {
      state.dir = b.dataset.filter;
      document.querySelectorAll('.chip[data-filter]').forEach(function (o) {
        o.setAttribute('aria-pressed', String(o === b));
      });
      apply();
    });
  });
  document.querySelectorAll('.chip[data-conf]').forEach(function (b) {
    b.addEventListener('click', function () {
      state.conf = state.conf ? null : b.dataset.conf;
      b.setAttribute('aria-pressed', String(!!state.conf));
      apply();
    });
  });

  // any ticker anywhere on the page filters the wire
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest('[data-ticker]');
    if (!t) return;
    state.ticker = (state.ticker === t.dataset.ticker) ? null : t.dataset.ticker;
    apply();
    if (state.ticker) wire.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  document.getElementById('af-clear').addEventListener('click', function () {
    state.ticker = null; state.conf = null; state.text = ''; state.dir = 'all';
    if (q) q.value = '';
    document.querySelectorAll('.chip[data-conf]').forEach(function (o) {
      o.setAttribute('aria-pressed', 'false');
    });
    document.querySelectorAll('.chip[data-filter]').forEach(function (o) {
      o.setAttribute('aria-pressed', String(o.dataset.filter === 'all'));
    });
    apply();
  });

  if (q) {
    q.addEventListener('input', function () {
      state.text = q.value.trim().toLowerCase();
      apply();
    });
    q.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') { q.value = ''; state.text = ''; apply(); q.blur(); }
    });
  }
  document.addEventListener('keydown', function (ev) {
    if (ev.key === '/' && document.activeElement !== q) { ev.preventDefault(); q && q.focus(); }
  });

  // progressive disclosure: headline -> full analysis
  function toggle(el) { el.classList.toggle('open'); }
  wire.addEventListener('click', function (ev) {
    if (ev.target.closest('[data-ticker]') || ev.target.closest('a')) return;
    var title = ev.target.closest('.item-title');
    if (title) toggle(title.parentElement);
  });
  wire.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Enter' && ev.key !== ' ') return;
    var title = ev.target.closest('.item-title');
    if (title) { ev.preventDefault(); toggle(title.parentElement); }
  });

  var expand = document.getElementById('expand-all');
  if (expand) {
    expand.addEventListener('click', function () {
      var open = expand.getAttribute('aria-pressed') !== 'true';
      items.forEach(function (el) { el.classList.toggle('open', open); });
      expand.setAttribute('aria-pressed', String(open));
      expand.textContent = open ? 'Collapse all' : 'Expand all';
    });
  }

  // rail notes expand too
  document.querySelectorAll('.note').forEach(function (n) {
    if (!n.querySelector('.note-b')) return;
    n.addEventListener('click', function (ev) {
      if (ev.target.closest('a')) return;
      n.classList.toggle('open');
    });
    n.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); n.classList.toggle('open'); }
    });
  });

  // theme toggle: overrides the OS preference, remembers the choice
  var root = document.documentElement;
  var btn = document.getElementById('theme');
  function currentTheme() {
    return root.getAttribute('data-theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }
  if (btn) {
    var saved = null;
    try { saved = localStorage.getItem('finbot-theme'); } catch (err) {}
    if (saved) root.setAttribute('data-theme', saved);
    function label() { btn.textContent = currentTheme() === 'dark' ? 'LIGHT' : 'DARK'; }
    label();
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('finbot-theme', next); } catch (err) {}
      label();
    });
  }

  apply();
})();
"""


# Beginner-mode behaviour: reading-level switch, the asset browser, and the
# tappable glossary. Kept separate from the wire logic above.
JS_PLAIN = r"""
(function () {
  var body = document.body;

  /* ---------- reading level ---------- */
  var plainBtn = document.getElementById('m-plain');
  var expertBtn = document.getElementById('m-expert');
  var hint = document.getElementById('modehint');
  var HINTS = {
    plain: 'Jargon is explained. Dotted words can be tapped.',
    expert: 'Full analyst wording, with the mechanism spelled out.'
  };
  function setMode(mode) {
    body.classList.toggle('mode-plain', mode === 'plain');
    body.classList.toggle('mode-expert', mode === 'expert');
    if (plainBtn) plainBtn.setAttribute('aria-pressed', String(mode === 'plain'));
    if (expertBtn) expertBtn.setAttribute('aria-pressed', String(mode === 'expert'));
    if (hint) hint.textContent = HINTS[mode];
    try { localStorage.setItem('finbot-mode', mode); } catch (err) {}
  }
  var savedMode = 'plain';
  try { savedMode = localStorage.getItem('finbot-mode') || 'plain'; } catch (err) {}
  setMode(savedMode);
  if (plainBtn) plainBtn.addEventListener('click', function () { setMode('plain'); });
  if (expertBtn) expertBtn.addEventListener('click', function () { setMode('expert'); });

  /* ---------- asset browser ---------- */
  var assets = Array.prototype.slice.call(document.querySelectorAll('.asset'));
  assets.forEach(function (a) {
    var row = a.querySelector('.asset-row');
    if (!row) return;
    row.addEventListener('click', function () {
      var open = !a.classList.contains('open');
      a.classList.toggle('open', open);
      row.setAttribute('aria-expanded', String(open));
    });
  });

  var bq = document.getElementById('bq');
  var riskState = 'all';
  function applyBrowse() {
    var q = bq ? bq.value.trim().toLowerCase() : '';
    document.querySelectorAll('.group').forEach(function (g) {
      var shown = 0;
      g.querySelectorAll('.asset').forEach(function (a) {
        var text = a.textContent.toLowerCase();
        var risk = (a.querySelector('.dots') || {}).getAttribute
          ? parseInt(a.querySelector('.dots').getAttribute('aria-label').replace(/\D+/, ''), 10)
          : 3;
        var ok = (!q || text.indexOf(q) !== -1) &&
                 (riskState === 'all' || risk <= 2);
        a.hidden = !ok;
        if (ok) shown++;
      });
      g.hidden = shown === 0;
      var n = g.querySelector('.n');
      if (n) n.textContent = shown;
    });
  }
  if (bq) bq.addEventListener('input', applyBrowse);
  document.querySelectorAll('.chip[data-risk]').forEach(function (b) {
    b.addEventListener('click', function () {
      riskState = b.dataset.risk;
      document.querySelectorAll('.chip[data-risk]').forEach(function (o) {
        o.setAttribute('aria-pressed', String(o === b));
      });
      applyBrowse();
    });
  });

  /* ---------- glossary ---------- */
  var terms = {};
  document.querySelectorAll('script[id^="g-"]').forEach(function (el) {
    var raw = el.textContent.split('|');
    if (raw.length >= 2) terms[raw[0].toLowerCase()] = raw.slice(1).join('|');
  });
  var dlg = document.getElementById('gloss');
  var dlgT = document.getElementById('gloss-t');
  var dlgD = document.getElementById('gloss-d');
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest('.term');
    if (!t || !dlg) return;
    ev.preventDefault();
    var key = t.dataset.term;
    var def = terms[key];
    if (!def) {
      // the linked word may be a variant, e.g. "bull / bullish"
      Object.keys(terms).forEach(function (k) {
        if (!def && k.indexOf(key) !== -1) def = terms[k];
      });
    }
    if (!def) return;
    dlgT.textContent = t.textContent;
    dlgD.textContent = def;
    if (typeof dlg.showModal === 'function') dlg.showModal();
  });
  var close = document.getElementById('gloss-x');
  if (close && dlg) close.addEventListener('click', function () { dlg.close(); });
  if (dlg) dlg.addEventListener('click', function (ev) {
    if (ev.target === dlg) dlg.close();
  });

  applyBrowse();
})();
"""
