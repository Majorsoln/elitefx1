# 9 Entries & Exits — Rules / Conditions (plain text)

Source: Kevin J. Davey — "9 Terrific Trading Entries, 7 Sensible Exits"
Notation: `close[n]` = close n bars ago. Orders execute "next bar". All directions are mirrored long/short.

---

## ENTRIES

### Entry #1 – Trade The Pullback
- Inputs: short_len = 5, long_len = 20
- Long: close > close[short_len] AND close < close[long_len] → buy next bar at market
- Short: close < close[short_len] AND close > close[long_len] → sell short next bar at market

### Entry #2 – With Trend Pullback
- Inputs: short_len = 5, long_len = 20
- Long: close < close[short_len] AND close > close[long_len] → buy next bar at market
- Short: close > close[short_len] AND close < close[long_len] → sell short next bar at market

### Entry #3 – Jump Off
- Inputs: pbasebar = 10, trendbar = 20, atrmult = 2
- pbase = (highest(high, pbasebar) + lowest(low, pbasebar)) / 2
- Long: close > close[trendbar] → buy next bar at (pbase + atrmult * ATR(15)) stop
- Short: close < close[trendbar] → sell short next bar at (pbase − atrmult * ATR(15)) stop

### Entry #4 – Super Simple Breakout
- Inputs: x = 10
- Long: buy next bar at highest(high, x) stop
- Short: sell short next bar at lowest(low, x) stop

### Entry #5 – Second Chance Trend
- Inputs: X = 10, Y = 15
- Condition1 = close > average(close, X)
- Condition2 = close < percentile(0.10, close, Y)
- Condition3 = close < close[1] AND close[1] < close[2] AND close[2] < close[3]   (3 down bars)
- Long: Condition1 AND (Condition2 OR Condition3) → buy next bar at market
- Condition4 = close < average(close, X)
- Condition5 = close > percentile(0.90, close, Y)
- Condition6 = close > close[1] AND close[1] > close[2] AND close[2] > close[3]   (3 up bars)
- Short: Condition4 AND (Condition5 OR Condition6) → sell short next bar at market

### Entry #6 – Big Range, Big Mo
- Inputs: xr = 5, daysback = 10
- rrange = high − low
- big_range = rrange > 2 * stddev(rrange, xr) + average(rrange, xr)
- Long: big_range AND close > close[daysback] → buy next bar at market
- Short: big_range AND close < close[daysback] → sell short next bar at market

### Entry #7 – The Report Play
- Inputs: trigger_time = 930
- At time = trigger_time: buyprice = high + 0.01 (1–2 ticks), sellprice = low − 0.01
- At time = trigger_time:
  - buy next bar at buyprice stop
  - sell short next bar at sellprice stop

### Entry #8 – Low Vol Reversals
- Inputs: len = 5
- Filter: volume < average(volume, 5)
- When filter true:
  - Long: close = lowest(close, len) → buy next bar at market
  - Short: close = highest(close, len) → sell short next bar at market

### Entry #9 – Simple Pattern
- Long: low[3] > low[2] AND low[2] > low[1] AND close > high[1] → buy next bar at market
- Short: high[3] < high[2] AND high[2] < high[1] AND close < low[1] → sell short next bar at market

---

## EXITS

### Exit #1 – Simple and Sweet (stop loss)
- Input: stop_amt = 1000
- SetStopLoss(stop_amt) per contract (dollars)
- Alternative: stop = 3 * ATR(15) * BigPointValue

### Exit #2 – Hit That Target! (profit target)
- Input: profit_amt = 1000
- SetProfitTarget(profit_amt) per contract (dollars)

### Exit #3 – At Least Breakeven (breakeven stop)
- Input: be_amt = 1000
- SetBreakeven(be_amt): once max profit exceeds be_amt, trail with a breakeven stop
- (use combined with other exits, not alone)

### Exit #4 – Trailblazer (trailing stop)
- Input: trail_amt = 1000
- Long exit: sell next bar at close − (trail_amt / BigPointValue) stop
- Short exit: buy to cover next bar at close + (trail_amt / BigPointValue) stop

### Exit #5 – John Henry Exit (time / bars in trade)
- Input: X = 10
- If BarsSinceEntry >= X:
  - sell next bar at market
  - buy to cover next bar at market

### Exit #6 – Stop! (and Reverse)
- Option 1 (stop and reverse):
  - close > close[5] → buy next bar at market
  - close < close[5] → sell short next bar at market
- Option 2 (no reverse, stop loss only):
  - marketposition = 0 AND close > close[5] → buy next bar at market
  - marketposition = 0 AND close < close[5] → sell short next bar at market
  - SetStopLoss(1000)

### Exit #7 – Entries as Exits
- Inputs: X = 5, XX = 7
- Entries:
  - close > close[X] → buy next bar at market
  - close < close[X] → sell short next bar at market
- Exits:
  - close crosses below average(close, XX) → sell next bar at market
  - close crosses above average(close, XX) → buy to cover next bar at market

### Exit #8 – BONUS – Exit on Close
- SetExitOnClose
- Note: must use with a custom session that ends a few minutes before the exchange close for real-time execution; custom sessions require intraday (XX-minute) bars, not daily bars.

### Big Combo Exit
- Inputs: stop_amt = 1000, profit_amt = 1000, be_amt = 1000
- SetStopLoss(stop_amt)
- SetProfitTarget(profit_amt)
- SetBreakeven(be_amt)
