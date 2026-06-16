"""
test_no_lookahead.py — Test ya msingi: candles HAZINA lookahead.

Hatari kubwa kuliko zote kwenye trading ML: data ya baadaye kuingia kwenye bar
ya sasa. Bucket lazima iwe HALF-OPEN: bar yenye bar_open=T inajumuisha ticks
za [T, T+interval) TU — hakuna tick ya T+interval au zaidi inayoingia.

Test inaweka tick yenye bei ya kipekee KWENYE mpaka kamili wa dakika, kisha
inathibitisha:
  1. Bei hiyo inaonekana kwenye bar ya dakika yake — SI bar iliyotangulia
     (hakuna backward-leak = hakuna lookahead kwa bar iliyopita).
  2. close ya bar iliyotangulia = tick ya mwisho KABLA ya mpaka.
  3. open ya bar mpya = tick ya kwanza KWENYE/baada ya mpaka.

Endesha: python tests\\test_no_lookahead.py   (au: pytest tests/)
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data.build_candles import build_1m_sql, load_config  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_SYMBOL = "__LOOKAHEAD_TEST__"


def _setup(cfg) -> Path:
    """Tengeneza ticks: dakika 0 bei ~1.10, kisha SPIKE 9.99 hasa saa 00:02:00."""
    leaf = (REPO_ROOT / cfg["paths"]["raw_ticks"] /
            f"symbol={TEST_SYMBOL}" / "year=2020" / "month=01" / "day=06")
    leaf.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"""
        COPY (
          -- ticks za kawaida kila sekunde 5 kwa dakika 3 (1.10 hadi 1.10x)
          SELECT TIMESTAMPTZ '2020-01-06 00:00:00+00' + (i * INTERVAL 5 SECOND) AS timestamp,
                 CAST(1.10000 + (i % 10) * 0.00001 AS DOUBLE) AS bid,
                 CAST(1.10000 + (i % 10) * 0.00001 + 0.00005 AS DOUBLE) AS ask,
                 CAST(1.0 AS FLOAT) AS bid_vol, CAST(1.0 AS FLOAT) AS ask_vol,
                 '06' AS day, '01' AS month, '{TEST_SYMBOL}' AS symbol, 2020 AS year
          FROM range(0, 36) t(i)
          UNION ALL
          -- SPIKE moja hasa saa 00:02:00.000 (mwanzo wa dakika ya 3)
          SELECT TIMESTAMPTZ '2020-01-06 00:02:00.000+00',
                 9.99000, 9.99005, CAST(1.0 AS FLOAT), CAST(1.0 AS FLOAT),
                 '06', '01', '{TEST_SYMBOL}', 2020
        ) TO '{leaf.as_posix()}/ticks.parquet' (FORMAT PARQUET);
    """)
    return leaf


def _teardown(cfg):
    p = REPO_ROOT / cfg["paths"]["raw_ticks"] / f"symbol={TEST_SYMBOL}"
    if p.exists():
        shutil.rmtree(p)


def test_no_lookahead():
    cfg = load_config()
    _setup(cfg)
    try:
        con = duckdb.connect()
        bars = con.execute(build_1m_sql(TEST_SYMBOL, cfg)).fetchall()
        # columns: symbol,tf,bar_open,open,high,low,close,...
        by_min = {b[2].minute: {"open": float(b[3]), "high": float(b[4]),
                                "low": float(b[5]), "close": float(b[6])} for b in bars}

        # Dakika 0 na 1 zipo, na dakika 2 (spike) ipo
        assert 0 in by_min and 1 in by_min and 2 in by_min, by_min.keys()

        # 1. SPIKE (9.99) iko kwenye dakika 2 TU — si dakika 1 (hakuna backward-leak)
        assert by_min[2]["high"] == 9.99, f"spike haiko dakika 2: {by_min[2]}"
        assert by_min[1]["high"] < 2.0, f"LOOKAHEAD! spike imevuja dakika 1: {by_min[1]}"
        assert by_min[0]["high"] < 2.0, f"LOOKAHEAD! spike imevuja dakika 0: {by_min[0]}"

        # 2. open ya dakika 2 = spike yenyewe (tick ya kwanza saa 00:02:00)
        assert by_min[2]["open"] == 9.99, f"open ya dakika 2 si spike: {by_min[2]}"

        # 3. close ya dakika 1 = tick ya mwisho KABLA ya 00:02:00 (< 2.0, si spike)
        assert by_min[1]["close"] < 2.0, f"close ya dakika 1 imechukua spike: {by_min[1]}"

        print("PASS: hakuna lookahead — bucket ni half-open [T, T+1min), spike "
              "haikuvuja kwenye bar iliyotangulia.")
    finally:
        _teardown(cfg)


if __name__ == "__main__":
    test_no_lookahead()
    print("\n✅ test_no_lookahead OK")
