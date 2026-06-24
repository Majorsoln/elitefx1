"""
event_library.py — KJ Event Library (signals). Single source of truth ya events.

Events 9 za doctrine (V5) zikitokana na `Event Library.md` (Kevin J. Davey).
Kila signal: +1 = long, -1 = short, 0 = hakuna. Zote NO-LOOKAHEAD (zinatumia
close/high/low za SASA na ZILIZOPITA tu). Signature sare: fn(close, high, low).
Long/short zime-mirror.

Ramani (V5 name -> KJ rule):
  pullback             -> KJ #1  Trade The Pullback   (close vs close[5], close[20])
  deep_pullback        -> KJ #2  With Trend Pullback  (with-trend variant)
  breakout             -> KJ #4  Super Simple Breakout (highest(high,x))
  volatility_breakout  -> KJ #6  Big Range Big Mo     (big range + momentum)
  trend_continuation   -> SMA + momentum (KJ #5 spirit)
  volatility_expansion -> range expansion + direction
  news_shock           -> KJ #7  Report Play PROXY (return shock; HAKUNA news calendar)
  mean_reversion       -> KJ #8  Low Vol Reversals    (N-bar extreme)
  pattern_completion   -> KJ #9  Simple Pattern       (3 rising lows + breakout)

> ⚠️ news_shock ni PROXY ya volatility-shock (data haina news calendar). Itabadilishwa
> tukipata calendar. Vigezo (LEN/mult) ni adjustable; ni definitions, sio tuning.
"""
from __future__ import annotations
import numpy as np

# --- vigezo (KJ Event Library + EliteFX) ---
SHORT_LEN, LONG_LEN = 5, 20      # pullback / deep_pullback (KJ #1/#2)
BREAKOUT_LEN = 10                # breakout (KJ #4, x)
BIGRANGE_LEN, BIGRANGE_BACK = 5, 10   # volatility_breakout (KJ #6: xr, daysback)
MA_LEN, MOM_LEN = 20, 5          # trend_continuation
EXPAND_LEN, EXPAND_MULT = 10, 1.5     # volatility_expansion
SHOCK_LEN, SHOCK_K = 20, 3.0     # news_shock proxy
MEANREV_LEN = 10                 # mean_reversion (EliteFX: 10, sawa na Phase 1.9/1.95)


def pullback_signals(close, high=None, low=None) -> np.ndarray:
    """KJ #1. Long: close>close[short] AND close<close[long]; short = mirror."""
    n = len(close); s = np.zeros(n, dtype=int)
    for i in range(LONG_LEN, n):
        cs, cl = close[i - SHORT_LEN], close[i - LONG_LEN]
        if close[i] > cs and close[i] < cl: s[i] = 1
        elif close[i] < cs and close[i] > cl: s[i] = -1
    return s


def deep_pullback_signals(close, high=None, low=None) -> np.ndarray:
    """KJ #2 (With Trend Pullback). Long: close<close[short] AND close>close[long]."""
    n = len(close); s = np.zeros(n, dtype=int)
    for i in range(LONG_LEN, n):
        cs, cl = close[i - SHORT_LEN], close[i - LONG_LEN]
        if close[i] < cs and close[i] > cl: s[i] = 1
        elif close[i] > cs and close[i] < cl: s[i] = -1
    return s


def breakout_signals(close, high, low) -> np.ndarray:
    """KJ #4. Long: close > highest(high, x) ya bars zilizopita; short mirror."""
    n = len(close); s = np.zeros(n, dtype=int); x = BREAKOUT_LEN
    for i in range(x, n):
        if close[i] > np.max(high[i - x:i]): s[i] = 1
        elif close[i] < np.min(low[i - x:i]): s[i] = -1
    return s


def volatility_breakout_signals(close, high, low) -> np.ndarray:
    """KJ #6 (Big Range Big Mo). big_range = range > 2*std+mean (xr); + momentum."""
    n = len(close); s = np.zeros(n, dtype=int)
    rng = high - low; xr, db = BIGRANGE_LEN, BIGRANGE_BACK
    for i in range(max(xr, db), n):
        w = rng[i - xr:i]                                  # PAST xr bars (excl. i) — spike inajitokeza
        if rng[i] > 2 * np.std(w) + np.mean(w):
            if close[i] > close[i - db]: s[i] = 1
            elif close[i] < close[i - db]: s[i] = -1
    return s


def trend_continuation_signals(close, high=None, low=None) -> np.ndarray:
    """SMA + momentum. Long: close>SMA(close,MA) AND close>close[MOM]."""
    n = len(close); s = np.zeros(n, dtype=int)
    for i in range(MA_LEN, n):
        ma = np.mean(close[i - MA_LEN + 1:i + 1])
        if close[i] > ma and close[i] > close[i - MOM_LEN]: s[i] = 1
        elif close[i] < ma and close[i] < close[i - MOM_LEN]: s[i] = -1
    return s


def volatility_expansion_signals(close, high, low) -> np.ndarray:
    """Range expansion + direction. range[i] > mult*mean(range, LEN) -> dir ya bar."""
    n = len(close); s = np.zeros(n, dtype=int); rng = high - low; L = EXPAND_LEN
    for i in range(L, n):
        base = np.mean(rng[i - L + 1:i + 1])
        if base > 0 and rng[i] > EXPAND_MULT * base:
            if close[i] > close[i - 1]: s[i] = 1
            elif close[i] < close[i - 1]: s[i] = -1
    return s


def news_shock_signals(close, high=None, low=None) -> np.ndarray:
    """PROXY ya KJ #7 (hakuna news calendar). |ret| > K*std(ret, LEN) -> shock."""
    n = len(close); s = np.zeros(n, dtype=int)
    ret = np.diff(close, prepend=close[0])
    for i in range(SHOCK_LEN, n):
        sd = np.std(ret[i - SHOCK_LEN:i])
        if sd > 0 and abs(ret[i]) > SHOCK_K * sd:
            s[i] = 1 if ret[i] > 0 else -1
    return s


def mean_reversion_signals(close, high=None, low=None) -> np.ndarray:
    """KJ #8 (Low Vol Reversals core). Long pale close = lowest(close, N) -> bounce."""
    n = len(close); s = np.zeros(n, dtype=int); N = MEANREV_LEN
    for i in range(N - 1, n):
        w = close[i - N + 1:i + 1]
        if close[i] <= w.min(): s[i] = 1
        elif close[i] >= w.max(): s[i] = -1
    return s


def pattern_completion_signals(close, high, low) -> np.ndarray:
    """KJ #9 (Simple Pattern). Long: low[3]>low[2]>low[1] AND close>high[1]."""
    n = len(close); s = np.zeros(n, dtype=int)
    for i in range(3, n):
        if low[i - 3] > low[i - 2] > low[i - 1] and close[i] > high[i - 1]: s[i] = 1
        elif high[i - 3] < high[i - 2] < high[i - 1] and close[i] < low[i - 1]: s[i] = -1
    return s


# Registry rasmi ya events 9 (mpangilio wa doctrine V5).
EVENTS_ALL = {
    "pullback":             pullback_signals,
    "deep_pullback":        deep_pullback_signals,
    "breakout":             breakout_signals,
    "volatility_breakout":  volatility_breakout_signals,
    "trend_continuation":   trend_continuation_signals,
    "volatility_expansion": volatility_expansion_signals,
    "news_shock":           news_shock_signals,
    "mean_reversion":       mean_reversion_signals,
    "pattern_completion":   pattern_completion_signals,
}


def self_test():
    """Events zote 9 zinatoa signals halali (+1/-1/0), no-lookahead, kwenye bei bandia."""
    rng = np.random.default_rng(0); n = 2000
    # heteroskedastic: vol-clusters + spikes ili events ZOTE (pia big-range) ziwake
    vol = 0.5 + 1.5 * (rng.random(n) < 0.1)                 # 10% bars = high-vol
    rets = rng.normal(0, vol)
    close = np.cumsum(rets) + 1000.0
    rng_bar = np.abs(rets) + np.abs(rng.normal(0, 0.4 * vol))   # range inakua na vol
    high = close + rng_bar; low = close - rng_bar
    ok = True
    for nm, fn in EVENTS_ALL.items():
        s = fn(close, high, low)
        valid = set(np.unique(s)).issubset({-1, 0, 1}) and len(s) == n
        fired = int((s != 0).sum())
        # no-lookahead spot-check: signal[i] haitegemei data baada ya i
        s_trunc = fn(close[:600], high[:600], low[:600])
        nolook = np.array_equal(s[:600], s_trunc)
        ok = ok and valid and fired > 0 and nolook
        print(f"  {nm:22s} fired={fired:4d} valid={valid} nolook={nolook}")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test())
