"""
event_library_v2.py — Event Library V2 (Chief direct, 2026-07-08). Maboresho ya entries.

KWA NINI V2 (ukaguzi wa Chief juu ya event_library.py + evidence za Phase 3/12):
  D1. V1 events ni CONDITIONS, sio EVENTS: pullback inawaka bars 334/1000,
      trend_continuation 738/1000 (Phase 3). Sampuli zinazo-overlap + spread
      inalipwa kila bar -> EV negative kila mahali (Phase 12: 0/5 proven).
      SULUHISHO: EDGE-TRIGGER (fire kwenye TRANSITION tu) + REARM (cooldown)
      -> episodes chache, karibu-huru, zinazofanana na trading halisi.
  D2. Uaminifu wa KJ ulipotea kwenye port ya V1: #3 Jump Off (stop-entry) HAIPO;
      #4 breakout inatumia close-confirm badala ya STOP kwenye level (entry mbaya
      zaidi, inakosa intrabar breakouts); #5 Second Chance percentile logic
      ilibadilishwa na SMA+momentum (inawaka 74% ya bars); #7 Report Play haina
      session structure; #8 volume filter iliondolewa. V2 inazirudisha ZOTE.
  D3. Hakuna time-of-day V1: FX ina session structure kali (spread/vol hutofautiana
      3-5x kati ya Asia na London). V2: session_orb (opening-range breakout) +
      hour inapatikana kwa kila event (S1 inaweza ku-grid session filters).
  D4. Pockets pekee zilizothibitishwa (Phase 12): mean_reversion x EURUSD (P100),
      deep_pullback x EURUSD (P97). V2 inaongeza matoleo makali zaidi ya familia
      hizo mbili: mr_zscore (ATR-stretch, sio N-bar-low tu) na trend_resume
      (pullback + resumption bar — KJ #2 modification rasmi).
  D5. (directive ya PD 2026-07-09) KJ 9 si ulimwengu wote wa entries. Mbinu 5 MPYA
      za familia tofauti: rsi2_pullback (MR-ndani-ya-trend, Connors), bb_fade
      (band reversion + re-entry confirmation), engulf_extreme (price-action
      reversal kwenye extreme), inside_break + nr7_break (compression->expansion,
      Crabel). Jumla: entries 16 katika familia 7 (trend-pullback, breakout,
      compression, session, shock, mean-reversion, price-action).

MKATABA (API):
  Bei zote (o,h,l,c) ziko katika PIPS (kama event_reality: price/pip). hour = saa
  ya bar (server/UTC). tc = tick count (volume proxy). Zote arrays za urefu n.
  Market events: fn(o,h,l,c,tc=None,hour=None) -> {"sig": int array (+1/-1/0)}
                 fire = agizo la MARKET kwenye OPEN ya bar inayofuata.
  Stop events:   fn(...) -> {"long_level": float, "short_level": float} (arrays;
                 NaN = haija-arm). Fill: bar INAYOFUATA ikigusa level
                 (h>=long_level / l<=short_level); entry = max(level, open) kwa
                 long (gap-honest), min(level, open) kwa short.
  NO-LOOKAHEAD: value ya index i inatumia data ya <= i TU. Params zote ni inputs
  za grid ya S1 (defaults = KJ/FX-sensible) — definitions, SIO tuning.
"""
from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

REARM_DEFAULT = 5   # bars za cooldown baada ya fire (episode discipline)
TICK = 0.1          # pips — offset ya stop juu/chini ya level (KJ: "1-2 ticks")


# ---------- helpers (zote no-lookahead) ----------

def _shift(x, k):
    out = np.full(len(x), np.nan)
    if k < len(x):
        out[k:] = x[:-k] if k > 0 else x
    return out


def _sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(np.asarray(x, float), 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def _roll(x, n, fn, incl=True):
    """Rolling fn juu ya window n. incl=True: window inaishia i (pamoja na i);
    incl=False: window ni bars ZILIZOPITA tu (i-n..i-1)."""
    out = np.full(len(x), np.nan)
    if incl:
        if len(x) >= n:
            out[n - 1:] = fn(sliding_window_view(x, n), axis=1)
    else:
        if len(x) > n:
            out[n:] = fn(sliding_window_view(x[:-1], n), axis=1)
    return out


def wilder_rsi(c, n=2):
    """RSI ya Wilder (no-lookahead). n=2 = Connors-style mean reversion."""
    c = np.asarray(c, float)
    d = np.diff(c, prepend=c[0])
    up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    au = np.empty_like(up); ad = np.empty_like(dn)
    au[0] = up[0]; ad[0] = dn[0]; a = 1.0 / n
    for i in range(1, len(c)):
        au[i] = a * up[i] + (1 - a) * au[i - 1]
        ad[i] = a * dn[i] + (1 - a) * ad[i - 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        rsi = 100.0 - 100.0 / (1.0 + au / ad)
    rsi[ad == 0] = 100.0
    rsi[(au == 0) & (ad == 0)] = 50.0
    return rsi


def wilder_atr(h, l, c, n=14):
    h = np.asarray(h, float); l = np.asarray(l, float); c = np.asarray(c, float)
    cp = np.roll(c, 1); cp[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - cp), np.abs(l - cp)))
    atr = np.empty_like(tr); atr[0] = tr[0]; a = 1.0 / n
    for i in range(1, len(tr)):
        atr[i] = a * tr[i] + (1 - a) * atr[i - 1]
    return atr


def _edge(long_c, short_c, rearm):
    """Edge-trigger: fire kwenye TRANSITION ya condition (false->true) tu, na
    rearm bars za cooldown baada ya fire yoyote. Hii ndiyo inayogeuza CONDITION
    (D1) kuwa EVENT halisi."""
    n = len(long_c); s = np.zeros(n, dtype=int)
    last = -rearm - 1; pl_ = ps_ = False
    for i in range(n):
        lc = bool(long_c[i]); sc = bool(short_c[i]); f = 0
        if lc and not pl_:
            f = 1
        elif sc and not ps_:
            f = -1
        if f != 0 and (i - last) > rearm:
            s[i] = f; last = i
        pl_, ps_ = lc, sc
    return s


# ---------- MARKET events ----------

def pullback_v2(o, h, l, c, tc=None, hour=None, short_len=5, long_len=20, rearm=REARM_DEFAULT):
    """KJ #1 (Trade The Pullback), edge-triggered. Long: c>c[s] AND c<c[L]."""
    cs = _shift(c, short_len); cl = _shift(c, long_len)
    with np.errstate(invalid="ignore"):
        lc = (c > cs) & (c < cl); sc = (c < cs) & (c > cl)
    return {"sig": _edge(lc, sc, rearm)}


def trend_resume(o, h, l, c, tc=None, hour=None, ma_len=20, rearm=REARM_DEFAULT):
    """KJ #2 + modification rasmi (D4): trend up (c>SMA) + pullback imetokea
    (c[1]<c[3]) + RESUMPTION bar (c>high[1]). Toleo kali la deep_pullback
    (pocket EURUSD P97 ya Phase 12)."""
    sma = _sma(c, ma_len)
    c1 = _shift(c, 1); c3 = _shift(c, 3); h1 = _shift(h, 1); l1 = _shift(l, 1)
    with np.errstate(invalid="ignore"):
        lc = (c > sma) & (c1 < c3) & (c > h1)
        sc = (c < sma) & (c1 > c3) & (c < l1)
    return {"sig": _edge(lc, sc, rearm)}


def second_chance(o, h, l, c, tc=None, hour=None, x=10, y=15, q=0.10, rearm=REARM_DEFAULT):
    """KJ #5 (Second Chance Trend) — percentile logic HALISI (V1 iliipoteza, D2).
    Long: c>SMA(x) AND (c < percentile(q, c, y) AU 3 down closes)."""
    sma = _sma(c, x)
    plo = _roll(c, y, lambda w, axis: np.quantile(w, q, axis=axis))
    phi = _roll(c, y, lambda w, axis: np.quantile(w, 1 - q, axis=axis))
    c1 = _shift(c, 1); c2 = _shift(c, 2); c3 = _shift(c, 3)
    with np.errstate(invalid="ignore"):
        dn3 = (c < c1) & (c1 < c2) & (c2 < c3)
        up3 = (c > c1) & (c1 > c2) & (c2 > c3)
        lc = (c > sma) & ((c < plo) | dn3)
        sc = (c < sma) & ((c > phi) | up3)
    return {"sig": _edge(lc, sc, rearm)}


def big_range_mo(o, h, l, c, tc=None, hour=None, xr=5, daysback=10, k=2.0, rearm=REARM_DEFAULT):
    """KJ #6 (Big Range Big Mo), edge-triggered. big_range = range > k*std+mean
    (za PAST xr bars) + momentum ya daysback."""
    rng_ = h - l
    mu = _roll(rng_, xr, np.mean, incl=False)
    sd = _roll(rng_, xr, np.std, incl=False)
    cd = _shift(c, daysback)
    with np.errstate(invalid="ignore"):
        big = rng_ > k * sd + mu
        lc = big & (c > cd); sc = big & (c < cd)
    return {"sig": _edge(lc, sc, rearm)}


def lowvol_reversal(o, h, l, c, tc=None, hour=None, len_=5, vlen=5, rearm=REARM_DEFAULT):
    """KJ #8 (Low Vol Reversals) NA volume filter halisi (V1 iliiondoa, D2):
    tc < SMA(tc, vlen) AND c = lowest(c, len_) -> long (mirror short)."""
    n = len(c)
    if tc is None:
        return {"sig": np.zeros(n, dtype=int)}
    tc = np.asarray(tc, float)
    vs = _sma(tc, vlen)
    cmin = _roll(c, len_, np.min); cmax = _roll(c, len_, np.max)
    with np.errstate(invalid="ignore"):
        lowv = tc < vs
        lc = lowv & (c <= cmin); sc = lowv & (c >= cmax)
    return {"sig": _edge(lc, sc, rearm)}


def pattern_3lows(o, h, l, c, tc=None, hour=None, rearm=3):
    """KJ #9 (Simple Pattern): 3 rising lows + close juu ya high[1]."""
    l1 = _shift(l, 1); l2 = _shift(l, 2); l3 = _shift(l, 3)
    h1 = _shift(h, 1); h2 = _shift(h, 2); h3 = _shift(h, 3)
    with np.errstate(invalid="ignore"):
        lc = (l3 > l2) & (l2 > l1) & (c > h1)
        sc = (h3 < h2) & (h2 < h1) & (c < l1)
    return {"sig": _edge(lc, sc, rearm)}


def mr_zscore(o, h, l, c, tc=None, hour=None, ma_len=20, atr_len=14, k=1.5, rearm=10):
    """Mean-reversion V2 (D4 — toleo kali la pocket EURUSD P100): entry inahitaji
    STRETCH halisi kutoka SMA kwa units za ATR (sio N-bar-low inayowaka kila bar).
    Long: (SMA - c)/ATR >= k."""
    sma = _sma(c, ma_len); atr = wilder_atr(h, l, c, atr_len)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (sma - c) / np.where(atr > 0, atr, np.nan)
        lc = z >= k; sc = z <= -k
    return {"sig": _edge(lc, sc, rearm)}


def shock_follow(o, h, l, c, tc=None, hour=None, len_=20, k=3.0, rearm=10):
    """news_shock V2 (proxy — bado hakuna news calendar): |ret| > k*std(ret, len_
    za PAST) -> fuata mwelekeo. Edge-triggered + rearm (V1 ilihesabu kila bar)."""
    ret = np.diff(c, prepend=c[0])
    sd = _roll(ret, len_, np.std, incl=False)
    with np.errstate(invalid="ignore"):
        lc = ret > k * sd; sc = ret < -k * sd
    return {"sig": _edge(lc, sc, rearm)}


def rsi2_pullback(o, h, l, c, tc=None, hour=None, ma_len=100, rsi_len=2, lo=10.0, rearm=5):
    """MBINU MPYA (familia: mean-reversion-ndani-ya-trend, Connors RSI-2):
    trend up (c>SMA) + oversold kali ya muda mfupi (RSI(2)<lo) -> long. Tofauti na
    mr_zscore: inatumia velocity ya returns, sio umbali wa bei."""
    sma = _sma(c, ma_len); r = wilder_rsi(c, rsi_len)
    with np.errstate(invalid="ignore"):
        lc = (c > sma) & (r < lo)
        sc = (c < sma) & (r > 100.0 - lo)
    return {"sig": _edge(lc, sc, rearm)}


def bb_fade(o, h, l, c, tc=None, hour=None, n=20, k=2.0, rearm=5):
    """MBINU MPYA (familia: band reversion + CONFIRMATION): close ilifunga NJE ya
    Bollinger band (n,k) bar iliyopita, na sasa imerudi NDANI -> fade. Re-entry
    ndiyo confirmation (haishiki kisu kinachoanguka)."""
    ma = _sma(c, n); sd = _roll(c, n, np.std)
    lower = ma - k * sd; upper = ma + k * sd
    c1 = _shift(c, 1); lo1 = _shift(lower, 1); up1 = _shift(upper, 1)
    with np.errstate(invalid="ignore"):
        lc = (c1 < lo1) & (c > lower)
        sc = (c1 > up1) & (c < upper)
    return {"sig": _edge(lc, sc, rearm)}


def engulf_extreme(o, h, l, c, tc=None, hour=None, ext=10, rearm=5):
    """MBINU MPYA (familia: price-action reversal kwenye extreme): bullish engulfing
    (body ya sasa inameza body ya bar iliyopita) IKITOKEA kwenye low ya ext-bars
    -> long (mirror short kwenye high). Pattern + location, sio pattern peke yake."""
    o1 = _shift(o, 1); c1 = _shift(c, 1)
    lmin = _roll(l, ext, np.min); hmax = _roll(h, ext, np.max)
    with np.errstate(invalid="ignore"):
        bull = (c1 < o1) & (c > o) & (o <= c1) & (c >= o1)
        bear = (c1 > o1) & (c < o) & (o >= c1) & (c <= o1)
        lc = bull & (l <= lmin)
        sc = bear & (h >= hmax)
    return {"sig": _edge(lc, sc, rearm)}


# ---------- STOP events (intrabar-honest entries — D2) ----------

def inside_break(o, h, l, c, tc=None, hour=None, tick=TICK):
    """MBINU MPYA (familia: compression -> expansion): inside bar (range ndani ya
    bar-mama) -> stop orders kwenye high/low za bar-mama (OCO). Volatility
    contraction hutangulia expansion."""
    n = len(c)
    h1 = _shift(h, 1); l1 = _shift(l, 1)
    LL = np.full(n, np.nan); SS = np.full(n, np.nan)
    with np.errstate(invalid="ignore"):
        inside = (h < h1) & (l > l1)
    LL[inside] = h1[inside] + tick
    SS[inside] = l1[inside] - tick
    return {"long_level": LL, "short_level": SS}


def nr7_break(o, h, l, c, tc=None, hour=None, n=7, tick=TICK):
    """MBINU MPYA (familia: compression -> expansion, Crabel NR7): range ya bar hii
    ndiyo NYEMBAMBA zaidi ya bars n -> stop orders juu/chini ya bar hii (OCO)."""
    m = len(c)
    rng_ = h - l
    rmin = _roll(rng_, n, np.min)
    LL = np.full(m, np.nan); SS = np.full(m, np.nan)
    with np.errstate(invalid="ignore"):
        nr = rng_ <= rmin
    LL[nr] = h[nr] + tick
    SS[nr] = l[nr] - tick
    return {"long_level": LL, "short_level": SS}


def jump_off(o, h, l, c, tc=None, hour=None, pbasebar=10, trendbar=20, atrmult=2.0, atr_len=15):
    """KJ #3 (Jump Off) — HAIKUWEPO V1 (D2). pbase = (HH+LL)/2 ya pbasebar;
    trend up -> buy STOP kwenye pbase + atrmult*ATR."""
    n = len(c)
    hh = _roll(h, pbasebar, np.max); ll = _roll(l, pbasebar, np.min)
    pbase = (hh + ll) / 2.0
    atr = wilder_atr(h, l, c, atr_len)
    cd = _shift(c, trendbar)
    LL = np.full(n, np.nan); SS = np.full(n, np.nan)
    with np.errstate(invalid="ignore"):
        up = (c > cd) & np.isfinite(pbase)
        dn = (c < cd) & np.isfinite(pbase)
    LL[up] = pbase[up] + atrmult * atr[up]
    SS[dn] = pbase[dn] - atrmult * atr[dn]
    return {"long_level": LL, "short_level": SS}


def breakout_stop(o, h, l, c, tc=None, hour=None, x=10, tick=TICK):
    """KJ #4 (Super Simple Breakout) — STOP kwenye band halisi (V1 ilisubiri
    close-confirm: entry mbaya zaidi + inakosa intrabar breakouts, D2).
    Buy stop = HH(x) + tick; sell stop = LL(x) - tick (OCO)."""
    LL = _roll(h, x, np.max) + tick
    SS = _roll(l, x, np.min) - tick
    return {"long_level": LL, "short_level": SS}


def session_orb(o, h, l, c, tc=None, hour=None, range_hours=(7, 8), trade_hours=(9, 12), tick=TICK):
    """KJ #7 (Report Play) kwa FX — Opening Range Breakout ya session (D3):
    range = high/low ya saa za range_hours (default London open); stop orders
    pande zote wakati wa trade_hours; siku mpya = reset. Inahitaji hour."""
    n = len(c)
    LL = np.full(n, np.nan); SS = np.full(n, np.nan)
    if hour is None:
        return {"long_level": LL, "short_level": SS}
    hi = lo = np.nan
    for i in range(n):
        if i > 0 and hour[i] < hour[i - 1]:       # siku mpya
            hi = lo = np.nan
        if range_hours[0] <= hour[i] <= range_hours[1]:
            hi = h[i] if not np.isfinite(hi) else max(hi, h[i])
            lo = l[i] if not np.isfinite(lo) else min(lo, l[i])
        elif trade_hours[0] <= hour[i] <= trade_hours[1] and np.isfinite(hi):
            LL[i] = hi + tick; SS[i] = lo - tick
    return {"long_level": LL, "short_level": SS}


# ---------- CYCLE-2 events (Chief direct, 2026-07-09 — directive ya PD: "out of the box,
# trade za aina tofauti"). Mechanisms mpya, si variants za zilizopo ----------

def squeeze_break(o, h, l, c, tc=None, hour=None, bb_len=20, k=2.0, q=0.15,
                  look=100, brk=5, tick=TICK):
    """CYCLE-2 (familia F3+): MULTI-BAR squeeze — Bollinger-width ya chini kihistoria
    (quantile q ya widths za bars look zilizopita) -> stop orders kwenye HH/LL za bars brk.
    Tofauti na nr7 (bar MOJA nyembamba): hii ni mgandamizo wa WIKI, mlipuko mkubwa zaidi."""
    n = len(c)
    ma = _sma(c, bb_len); sd = _roll(c, bb_len, np.std)
    with np.errstate(invalid="ignore", divide="ignore"):
        width = (2 * k * sd) / np.where(ma > 0, ma, np.nan)
    wq = _roll(width, look, lambda w, axis: np.nanquantile(w, q, axis=axis), incl=False)
    hh = _roll(h, brk, np.max); ll = _roll(l, brk, np.min)
    LL = np.full(n, np.nan); SS = np.full(n, np.nan)
    with np.errstate(invalid="ignore"):
        squeezed = width <= wq
    LL[squeezed] = hh[squeezed] + tick
    SS[squeezed] = ll[squeezed] - tick
    return {"long_level": LL, "short_level": SS}


def nr4_inside(o, h, l, c, tc=None, hour=None, n_rng=4, tick=TICK):
    """CYCLE-2 (familia F3+, Crabel ID/NR4): inside bar AMBAYO PIA ni range nyembamba
    zaidi ya bars 4 — mgandamizo maradufu -> stops kwenye high/low za bar-mama."""
    m = len(c)
    h1 = _shift(h, 1); l1 = _shift(l, 1)
    rng_ = h - l
    rmin = _roll(rng_, n_rng, np.min)
    LL = np.full(m, np.nan); SS = np.full(m, np.nan)
    with np.errstate(invalid="ignore"):
        idnr = (h < h1) & (l > l1) & (rng_ <= rmin)
    LL[idnr] = h1[idnr] + tick
    SS[idnr] = l1[idnr] - tick
    return {"long_level": LL, "short_level": SS}


def gap_fade(o, h, l, c, tc=None, hour=None, k=0.5, atr_len=14, rearm=10):
    """CYCLE-2 (familia MPYA F8: LIQUIDITY-GAP REVERSION — aina tofauti ya trade kabisa):
    open ya bar ina-gap dhidi ya close iliyopita (> k*ATR — hasa Monday/rollover FX);
    bar ya gap ikianza kurudi (close dhidi ya open ya gap) -> fuata KURUDI kuelekea
    close ya zamani. Mechanism: gaps za FX hujazwa mara nyingi (liquidity vacuum)."""
    c1 = _shift(c, 1)
    atr = wilder_atr(h, l, c, atr_len)
    atr1 = _shift(atr, 1)
    with np.errstate(invalid="ignore"):
        gap = o - c1
        gap_up = gap > k * atr1
        gap_dn = gap < -k * atr1
        sc = gap_up & (c < o)      # gap juu + imeanza kurudi chini -> short (fade)
        lc = gap_dn & (c > o)      # gap chini + imeanza kurudi juu -> long
    return {"sig": _edge(lc, sc, rearm)}


def london_drift(o, h, l, c, tc=None, hour=None, open_hr=8, mom=2, rearm=6):
    """CYCLE-2 (familia MPYA F9: SESSION-DRIFT — seasonality ya saa): kwenye close ya
    bar ya saa ya London open, mwelekeo wa bars mom za mwisho (Asia->London handoff)
    huendelea kipindi cha London/NY. Trade ya aina ya 'drift ya ratiba', si breakout."""
    n = len(c)
    if hour is None:
        return {"sig": np.zeros(n, dtype=int)}
    cm = _shift(c, mom)
    with np.errstate(invalid="ignore"):
        at_open = np.asarray(hour) == open_hr
        lc = at_open & (c > cm)
        sc = at_open & (c < cm)
    return {"sig": _edge(lc, sc, rearm)}


# ---------- Registry rasmi V2 ----------
# entry: "market" (sig -> open ya bar ijayo) | "stop" (levels -> touch ya bar ijayo)
# needs: data za ziada zinazohitajika ("tc" = volume, "hour" = time-of-day)
# v1:    jina la event ya V1 inayoboreshwa (None = mpya kabisa V2)
EVENTS_V2 = {
    "pullback_v2":     dict(fn=pullback_v2,     entry="market", needs=(),        v1="pullback"),
    "trend_resume":    dict(fn=trend_resume,    entry="market", needs=(),        v1="deep_pullback"),
    "jump_off":        dict(fn=jump_off,        entry="stop",   needs=(),        v1=None),
    "breakout_stop":   dict(fn=breakout_stop,   entry="stop",   needs=(),        v1="breakout"),
    "second_chance":   dict(fn=second_chance,   entry="market", needs=(),        v1="trend_continuation"),
    "big_range_mo":    dict(fn=big_range_mo,    entry="market", needs=(),        v1="volatility_breakout"),
    "session_orb":     dict(fn=session_orb,     entry="stop",   needs=("hour",), v1="news_shock"),
    "lowvol_reversal": dict(fn=lowvol_reversal, entry="market", needs=("tc",),   v1="mean_reversion"),
    "pattern_3lows":   dict(fn=pattern_3lows,   entry="market", needs=(),        v1="pattern_completion"),
    "mr_zscore":       dict(fn=mr_zscore,       entry="market", needs=(),        v1="mean_reversion"),
    "shock_follow":    dict(fn=shock_follow,    entry="market", needs=(),        v1="news_shock"),
    # --- mbinu MPYA kabisa (hazitokani na KJ 9 — familia za ziada, directive ya PD 2026-07-09) ---
    "rsi2_pullback":   dict(fn=rsi2_pullback,   entry="market", needs=(),        v1=None),
    "bb_fade":         dict(fn=bb_fade,         entry="market", needs=(),        v1=None),
    "engulf_extreme":  dict(fn=engulf_extreme,  entry="market", needs=(),        v1=None),
    "inside_break":    dict(fn=inside_break,    entry="stop",   needs=(),        v1=None),
    "nr7_break":       dict(fn=nr7_break,       entry="stop",   needs=(),        v1=None),
    # --- CYCLE-2 (2026-07-09, directive ya PD: diversification — trade za AINA tofauti).
    #     Grid ya cycle-2 ina registration YAKE (S1-C2); hazimo kwenye grid ya cycle-1. ---
    "squeeze_break":   dict(fn=squeeze_break,   entry="stop",   needs=(),        v1=None),
    "nr4_inside":      dict(fn=nr4_inside,      entry="stop",   needs=(),        v1=None),
    "gap_fade":        dict(fn=gap_fade,        entry="market", needs=(),        v1=None),
    "london_drift":    dict(fn=london_drift,    entry="market", needs=("hour",), v1=None),
}


# ---------- self-test ----------

def _synthetic(n=3000, seed=0):
    """OHLC bandia (pips): vol clusters + trends + session pattern ya volume."""
    rng = np.random.default_rng(seed)
    vol = 0.5 + 1.5 * (rng.random(n) < 0.1)
    drift = np.where((np.arange(n) // 300) % 2 == 0, 0.05, -0.05)
    rets = rng.normal(drift, vol)
    c = np.cumsum(rets) + 10000.0
    o = np.roll(c, 1); o[0] = c[0]
    # gaps za mara kwa mara (mf. Monday/rollover FX) — o ina-gap dhidi ya close iliyopita
    gap_idx = rng.choice(n - 1, size=max(4, n // 150), replace=False) + 1
    o[gap_idx] += rng.choice((-1, 1), len(gap_idx)) * rng.uniform(2.0, 5.0, len(gap_idx))
    spread_bar = np.abs(rets) + np.abs(rng.normal(0, 0.4 * vol, n))
    h = np.maximum(o, c) + spread_bar
    l = np.minimum(o, c) - spread_bar
    hour = np.arange(n) % 24
    tc = 500 + 400 * np.sin(hour / 24 * 2 * np.pi) + rng.normal(0, 60, n)
    return o, h, l, c, tc.clip(1), hour


def self_test():
    """(1) values halali + zinawaka; (2) NO-LOOKAHEAD (truncation invariance);
    (3) episode discipline: market events zinawaka << V1 conditions na gap>rearm;
    (4) stop events: levels sane (long>short kwa OCO); (5) needs zinaheshimiwa."""
    o, h, l, c, tc, hour = _synthetic()
    n = len(c); ok = True

    for nm, spec in EVENTS_V2.items():
        out = spec["fn"](o, h, l, c, tc, hour)
        out_t = spec["fn"](o[:900], h[:900], l[:900], c[:900], tc[:900], hour[:900])
        if spec["entry"] == "market":
            s = out["sig"]
            valid = set(np.unique(s)).issubset({-1, 0, 1}) and len(s) == n
            fired = int((s != 0).sum()); frac = fired / n
            idx = np.flatnonzero(s != 0)
            gaps_ok = bool(np.all(np.diff(idx) > 1)) if len(idx) > 1 else True
            nolook = np.array_equal(s[:900], out_t["sig"][:900])
            row_ok = valid and fired > 0 and frac < 0.15 and gaps_ok and nolook
            print(f"  {nm:16s} market fired={fired:4d} frac={frac:.3f} gaps>rearm={gaps_ok} nolook={nolook}")
        else:
            LL, SS = out["long_level"], out["short_level"]
            armed = np.isfinite(LL) | np.isfinite(SS)
            both = np.isfinite(LL) & np.isfinite(SS)
            sane = bool(np.all(LL[both] > SS[both])) if both.any() else True
            nolook = (np.array_equal(LL[:900], out_t["long_level"][:900], equal_nan=True)
                      and np.array_equal(SS[:900], out_t["short_level"][:900], equal_nan=True))
            row_ok = armed.any() and sane and nolook
            print(f"  {nm:16s} stop   armed={int(armed.sum()):4d} long>short={sane} nolook={nolook}")
        ok = ok and row_ok

    # (3b) uthibitisho wa D1: pullback_v2 inawaka mara chache SANA kuliko condition ya V1
    cs = _shift(c, 5); cl = _shift(c, 20)
    with np.errstate(invalid="ignore"):
        v1_frac = float(((c > cs) & (c < cl) | (c < cs) & (c > cl)).mean())
    v2_frac = float((pullback_v2(o, h, l, c)["sig"] != 0).mean())
    disc = v2_frac < 0.5 * v1_frac
    print(f"  D1 fix: pullback V1-condition frac={v1_frac:.3f} -> V2 episode frac={v2_frac:.3f} (<50%: {disc})")
    ok = ok and disc

    # (5) needs: bila tc/hour -> salama (hakuna crash, hakuna fire bandia)
    no_tc = lowvol_reversal(o, h, l, c, None, hour)["sig"]
    no_hr = session_orb(o, h, l, c, tc, None)
    needs_ok = (no_tc == 0).all() and not np.isfinite(no_hr["long_level"]).any()
    print(f"  needs: tc=None->0 fires={bool((no_tc == 0).all())}  hour=None->no arms={not np.isfinite(no_hr['long_level']).any()}")
    ok = ok and needs_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test())
