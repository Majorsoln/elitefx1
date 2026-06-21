# 9 Event (plain text)

Source: Kevin J. Davey — "9 Terrific Trading Entries, 7 Sensible Exits"
Notation: `close[n]` = close n bars ago. Orders execute "next bar". All directions are mirrored long/short.

---

## Events

### Event #1 – Trade The Pullback
- Inputs: short_len = 5, long_len = 20
- Long: close > close[short_len] AND close < close[long_len] → buy next bar at market
- Short: close < close[short_len] AND close > close[long_len] → sell short next bar at market
- Modifications to try:
  - Use moving averages instead of momentum to define the trends (watch for MA lag).
  - Use trendlines to define the trends (harder to code).
  - Add filters such as RSI, Stochastics, or ADX to screen out bad signals (caution: too many filters usually improves the backtest but worsens real-time results).

### Event #2 – With Trend Pullback
- Inputs: short_len = 5, long_len = 20
- Long: close < close[short_len] AND close > close[long_len] → buy next bar at market
- Short: close > close[short_len] AND close < close[long_len] → sell short next bar at market
- Modifications to try:
  - Wait for the market to reverse out of the pullback before entering — e.g., in an uptrend wait for a small downtrend, then enter once the uptrend shows signs of resuming (such as a bullish candlestick pattern).

### Event #3 – Jump Off
- Inputs: pbasebar = 10, trendbar = 20, atrmult = 2
- pbase = (highest(high, pbasebar) + lowest(low, pbasebar)) / 2
- Long: close > close[trendbar] → buy next bar at (pbase + atrmult * ATR(15)) stop
- Short: close < close[trendbar] → sell short next bar at (pbase − atrmult * ATR(15)) stop
- Modifications to try:
  - Remove the momentum/trend filter and take the breakout above/below the base regardless of trend (one fewer input to optimize).

### Event #4 – Super Simple Breakout
- Inputs: x = 10
- Long: buy next bar at highest(high, x) stop
- Short: sell short next bar at lowest(low, x) stop
- Modifications to try:
  - Add filters (RSI, ADX, etc.) to eliminate poor signals (most breakouts fail, but the ones that work tend to be very good).

### Event  #5 – Second Chance Trend
- Inputs: X = 10, Y = 15
- Condition1 = close > average(close, X)
- Condition2 = close < percentile(0.10, close, Y)
- Condition3 = close < close[1] AND close[1] < close[2] AND close[2] < close[3]   (3 down bars)
- Long: Condition1 AND (Condition2 OR Condition3) → buy next bar at market
- Condition4 = close < average(close, X)
- Condition5 = close > percentile(0.90, close, Y)
- Condition6 = close > close[1] AND close[1] > close[2] AND close[2] > close[3]   (3 up bars)
- Short: Condition4 AND (Condition5 OR Condition6) → sell short next bar at market
- Modifications to try:
  - Make the 10th / 90th percentile levels into inputs (variables).
  - Instead of 3 consecutive up/down bars, try 2 bars, 4 bars, or "3 of the last 4" bars up/down.

### Event #6 – Big Range, Big Mo
- Inputs: xr = 5, daysback = 10
- rrange = high − low
- big_range = rrange > 2 * stddev(rrange, xr) + average(rrange, xr)
- Long: big_range AND close > close[daysback] → buy next bar at market
- Short: big_range AND close < close[daysback] → sell short next bar at market
- Modifications to try:
  - Try a different standard-deviation multiplier than 2 (e.g., 1.0 or 1.5) to define a "big" range and allow more trades.

### Event #7 – The Report Play
- Inputs: trigger_time = 930
- At time = trigger_time: buyprice = high + 0.01 (1–2 ticks), sellprice = low − 0.01
- At time = trigger_time:
  - buy next bar at buyprice stop
  - sell short next bar at sellprice stop
- Modifications to try:
  - Use limit orders instead of stop orders (note: a limit buy sits below market, so it is hard to catch an upside breakout and you may miss it).
  - Instead of triggering on the report, trigger on standard time bars — e.g., activate the orders only at the start of each hour (every 4 bars on a 15-minute chart).

###Event #8 – Low Vol Reversals
- Inputs: len = 5
- Filter: volume < average(volume, 5)
- When filter true:
  - Long: close = lowest(close, len) → buy next bar at market
  - Short: close = highest(close, len) → sell short next bar at market
- Modifications to try:
  - Reverse the logic: sell short (instead of buy) when a local low is hit.
  - Require a high-volume bar instead of a low-volume bar for the signal.

### Event #9 – Simple Pattern
- Long: low[3] > low[2] AND low[2] > low[1] AND close > high[1] → buy next bar at market
- Short: high[3] < high[2] AND high[2] < high[1] AND close < low[1] → sell short next bar at market
- Modifications to try:
  - Build your own patterns from candlesticks or OHLC prices (most patterns are roughly zero-sum / ~50%, so test before relying on them).
