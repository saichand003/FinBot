"""Detect popular technical patterns on tracked symbols.

Patterns: golden/death cross, RSI overbought/oversold, 52-week
breakout/breakdown, volume spikes. Informational only - not advice.
"""
import numpy as np
import yfinance as yf

import config
import db


def _rsi(closes, period=14):
    delta = np.diff(closes)
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.convolve(gain, np.ones(period) / period, mode="valid")
    avg_loss = np.convolve(loss, np.ones(period) / period, mode="valid")
    rs = avg_gain / np.where(avg_loss == 0, 1e-9, avg_loss)
    return 100 - 100 / (1 + rs)


def detect_patterns():
    symbols = config.STOCKS + config.INDEXES + config.ETFS_FUNDS
    found = []
    data = yf.download(symbols, period=f"{config.PATTERN_LOOKBACK_DAYS}d",
                       group_by="ticker", progress=False, auto_adjust=True)
    for sym in symbols:
        try:
            hist = data[sym].dropna()
            if len(hist) < 60:
                continue
            close = hist["Close"].values
            vol = hist["Volume"].values

            sma50 = np.convolve(close, np.ones(50) / 50, mode="valid")
            if len(close) >= 200:
                sma200 = np.convolve(close, np.ones(200) / 200, mode="valid")
                a50, a200 = sma50[-len(sma200):], sma200
                if a50[-2] <= a200[-2] and a50[-1] > a200[-1]:
                    found.append((sym, "golden_cross", "SMA50 crossed above SMA200"))
                if a50[-2] >= a200[-2] and a50[-1] < a200[-1]:
                    found.append((sym, "death_cross", "SMA50 crossed below SMA200"))

            rsi = _rsi(close, config.RSI_PERIOD)
            if rsi[-1] >= 70:
                found.append((sym, "rsi_overbought", f"RSI={rsi[-1]:.0f}"))
            elif rsi[-1] <= 30:
                found.append((sym, "rsi_oversold", f"RSI={rsi[-1]:.0f}"))

            if close[-1] >= close.max() * 0.999:
                found.append((sym, "52wk_high", f"close={close[-1]:.2f}"))
            elif close[-1] <= close.min() * 1.001:
                found.append((sym, "52wk_low", f"close={close[-1]:.2f}"))

            if len(vol) > 21 and vol[-21:-1].mean() > 0:
                mult = vol[-1] / vol[-21:-1].mean()
                if mult >= config.VOLUME_SPIKE_MULT:
                    found.append((sym, "volume_spike", f"{mult:.1f}x 20d avg"))
        except Exception as ex:
            print(f"[patterns] {sym} failed: {ex}")

    rows = [{"symbol": s, "pattern": p, "detail": d} for s, p, d in found]
    n = db.insert_many("patterns", rows)
    for s, p, d in found:
        print(f"[patterns] {s}: {p} ({d})")
    print(f"[patterns] {n} stored")
    return n
