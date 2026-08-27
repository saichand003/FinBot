"""Technical pattern detection plus a rolling statistical profile per symbol.

Two outputs per run:
  * `patterns`     - discrete events worth a notification (crosses, RSI extremes,
                     52-week breaks, volume spikes)
  * `symbol_stats` - the continuous context every other module narrates against:
                     trend, momentum, volatility, distance from the highs, and
                     how today's volume compares to normal.

Informational only - not investment advice.
"""
import numpy as np
import yfinance as yf

import config
import db


def _sma(arr, n):
    if len(arr) < n:
        return None
    return float(np.convolve(arr, np.ones(n) / n, mode="valid")[-1])


def _rsi_series(closes, period=14):
    delta = np.diff(closes)
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.convolve(gain, np.ones(period) / period, mode="valid")
    avg_loss = np.convolve(loss, np.ones(period) / period, mode="valid")
    rs = avg_gain / np.where(avg_loss == 0, 1e-9, avg_loss)
    return 100 - 100 / (1 + rs)


def _pct(a, b):
    """Percent change from b to a, guarding against zero/NaN."""
    if not b or not np.isfinite(b) or not np.isfinite(a):
        return None
    return float((a / b - 1) * 100)


def _ret(close, days):
    return _pct(close[-1], close[-days - 1]) if len(close) > days else None


def _trend_label(price, s20, s50, s200):
    """A one-word read on structure, using the moving-average stack."""
    if None in (s50, s200):
        if s20 and price > s20:
            return "short-term uptrend"
        return "insufficient history"
    if price > s50 > s200:
        return "uptrend"
    if price < s50 < s200:
        return "downtrend"
    if price > s200 and price < s50:
        return "pullback in uptrend"
    if price < s200 and price > s50:
        return "bounce in downtrend"
    return "range-bound"


def _profile(sym, hist):
    """Build the full statistical profile for one symbol."""
    close = hist["Close"].values.astype(float)
    high = hist["High"].values.astype(float) if "High" in hist else close
    low = hist["Low"].values.astype(float) if "Low" in hist else close
    vol = hist["Volume"].values.astype(float) if "Volume" in hist else np.zeros_like(close)

    price = float(close[-1])
    s20, s50, s200 = _sma(close, 20), _sma(close, 50), _sma(close, 200)
    rsi = _rsi_series(close, config.RSI_PERIOD)
    hi52, lo52 = float(close.max()), float(close.min())

    tr = np.maximum(high[1:] - low[1:], np.abs(high[1:] - close[:-1]))
    tr = np.maximum(tr, np.abs(low[1:] - close[:-1]))
    atr_pct = float(tr[-14:].mean() / price * 100) if len(tr) >= 14 and price else None

    avg_vol20 = float(vol[-21:-1].mean()) if len(vol) > 21 else None

    return {
        "symbol": sym,
        "price": price,
        "chg_1d": _pct(close[-1], close[-2]) if len(close) > 1 else None,
        "ret_1w": _ret(close, 5), "ret_1m": _ret(close, 21),
        "ret_3m": _ret(close, 63), "ret_6m": _ret(close, 126),
        "sma20": s20, "sma50": s50, "sma200": s200,
        "rsi": float(rsi[-1]) if len(rsi) else None,
        "atr_pct": atr_pct,
        "hi_52w": hi52, "lo_52w": lo52,
        "pct_from_hi": _pct(price, hi52), "pct_from_lo": _pct(price, lo52),
        "vol": float(vol[-1]) if len(vol) else None,
        "avg_vol20": avg_vol20,
        "vol_mult": float(vol[-1] / avg_vol20) if avg_vol20 else None,
        "trend": _trend_label(price, s20, s50, s200),
    }


def _save_stats(profiles):
    cols = ("symbol price chg_1d ret_1w ret_1m ret_3m ret_6m sma20 sma50 sma200 rsi "
            "atr_pct hi_52w lo_52w pct_from_hi pct_from_lo vol avg_vol20 vol_mult trend").split()
    sql = (f"INSERT INTO symbol_stats ({','.join(cols)},updated_at) "
           f"VALUES ({','.join('?' for _ in cols)},CURRENT_TIMESTAMP) "
           f"ON CONFLICT(symbol) DO UPDATE SET "
           + ",".join(f"{c}=excluded.{c}" for c in cols[1:])
           + ",updated_at=CURRENT_TIMESTAMP")
    with db.conn() as c:
        c.executemany(sql, [tuple(p[k] for k in cols) for p in profiles])


def detect_patterns():
    symbols = config.STOCKS + config.INDEXES + config.ETFS_FUNDS
    found, profiles = [], []
    data = yf.download(symbols, period=f"{config.PATTERN_LOOKBACK_DAYS}d",
                       group_by="ticker", progress=False, auto_adjust=True)

    for sym in symbols:
        try:
            hist = data[sym].dropna()
            if len(hist) < 60:
                continue
            p = _profile(sym, hist)
            profiles.append(p)

            close = hist["Close"].values.astype(float)

            if len(close) >= 200:
                sma50 = np.convolve(close, np.ones(50) / 50, mode="valid")
                sma200 = np.convolve(close, np.ones(200) / 200, mode="valid")
                a50, a200 = sma50[-len(sma200):], sma200
                gap = (a50[-1] / a200[-1] - 1) * 100
                if a50[-2] <= a200[-2] and a50[-1] > a200[-1]:
                    found.append((sym, "golden_cross",
                                  f"SMA50 ({a50[-1]:.2f}) crossed above SMA200 ({a200[-1]:.2f}), now +{gap:.2f}% above"))
                if a50[-2] >= a200[-2] and a50[-1] < a200[-1]:
                    found.append((sym, "death_cross",
                                  f"SMA50 ({a50[-1]:.2f}) crossed below SMA200 ({a200[-1]:.2f}), now {gap:.2f}% below"))

            if p["rsi"] is not None:
                if p["rsi"] >= 70:
                    found.append((sym, "rsi_overbought", f"RSI={p['rsi']:.0f} (>70), {p['trend']}"))
                elif p["rsi"] <= 30:
                    found.append((sym, "rsi_oversold", f"RSI={p['rsi']:.0f} (<30), {p['trend']}"))

            if p["pct_from_hi"] is not None and p["pct_from_hi"] >= -0.1:
                found.append((sym, "52wk_high", f"close={p['price']:.2f} at the 52-week high"))
            elif p["pct_from_lo"] is not None and p["pct_from_lo"] <= 0.1:
                found.append((sym, "52wk_low", f"close={p['price']:.2f} at the 52-week low"))

            if p["vol_mult"] and p["vol_mult"] >= config.VOLUME_SPIKE_MULT:
                found.append((sym, "volume_spike",
                              f"{p['vol_mult']:.1f}x the 20-day average volume on a {p['chg_1d']:+.2f}% day"))
        except Exception as ex:
            print(f"[patterns] {sym} failed: {ex}")

    if profiles:
        _save_stats(profiles)
    rows = [{"symbol": s, "pattern": p, "detail": d} for s, p, d in found]
    n = db.insert_many("patterns", rows)
    for s, p, d in found:
        print(f"[patterns] {s}: {p} ({d})")
    print(f"[patterns] {n} stored, {len(profiles)} symbol profiles refreshed")
    return n
