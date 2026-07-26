//+------------------------------------------------------------------+
//|  KAIROS.mq5 — ELITEFX KAIROS EA (STRAT-001/002 port; MQL5)        |
//|  docs/KAIROS_EA_CHARTER.md — PORT HALISI kutoka Python (parity).   |
//|                                                                    |
//|  Strategy (byte-for-byte na src/research):                         |
//|   - nr7_break (event_library_v2): range(bar)=high-low; nr =        |
//|     range[signal] <= MIN(range za bars InpNR zilizofungwa,         |
//|     INCLUSIVE). buy-stop = high+tick, sell-stop = low-tick (OCO).  |
//|   - no-LATE (_mask_context): session ya bar ya ENTRY (i+1) LAZIMA  |
//|     0-16 (ASIA/LONDON/NY). Python inatumia _sess(hour[i+1]) (ex-    |
//|     ante schedule). Kwa H1 EA entry bar = shift 0. hour >=          |
//|     InpNoLateStart (17) = LATE -> HAKUNA order.                     |
//|   - ATR = Wilder(InpATR). SL/TP kwa ATR ya SIGNAL bar (Python:     |
//|     a=atr[i], i=signal). tie -> SL (worst case).                   |
//|   - Variants (INPUT, si EA mbili): KAIROS-1 USDCHF SL2.0/TP1.0 ·   |
//|     KAIROS-2 USDJPY SL1.0/TP1.0.                                    |
//|                                                                    |
//|  Demo/backtest PEKEE (live = Faza 4, SAINI YA PD §3.1b/§9).        |
//+------------------------------------------------------------------+
#property copyright "ELITEFX"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

//--- inputs ---------------------------------------------------------
input int    InpNR            = 7;      // nr window (bars zilizofungwa, inclusive)
input int    InpATR           = 14;     // Wilder ATR period
input double InpSL_mult       = 2.0;    // SL = mult x ATR (KAIROS-1=2.0, KAIROS-2=1.0)
input double InpTP_mult       = 1.0;    // TP = mult x ATR
input double InpRiskPct       = 0.5;    // risk % ya balance kwa trade (<=0 -> min lot)
input int    InpMaxPositions  = 1;      // positions max kwa symbol/magic
input double InpDailyLossPct  = 5.0;    // daily-loss guard (% ya balance ya mwanzo wa siku)
input long   InpMagic         = 20260726; // magic per instance
input int    InpNoLateStart   = 17;     // server-hour ya kwanza ya LATE (>=17 -> hakuna entry)
input double InpTick          = 0.1;    // stop offset (PIPS) juu/chini ya level (Python TICK=0.1)
input bool   InpSignalLog     = true;   // andika signal-log CSV (parity EA-2)

//--- globals --------------------------------------------------------
CTrade   trade;
int      atrHandle = INVALID_HANDLE;
datetime lastBar   = 0;
ulong    buyTicket = 0, sellTicket = 0;   // pending OCO tickets
int      logHandle = INVALID_HANDLE;
int      curDay    = -1;
double   dayStartBalance = 0.0;

//+------------------------------------------------------------------+
double PipSize()
  {
   int    d  = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double pt = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   return((d == 3 || d == 5) ? pt * 10.0 : pt);
  }

//--- session (event_quality_report._sess): ASIA 0-6, LONDON 7-11, NY 12-16, LATE 17-23
string Sess(const int hr)
  {
   if(hr >= 0  && hr <= 6)  return("ASIA");
   if(hr >= 7  && hr <= 11) return("LONDON");
   if(hr >= 12 && hr <= 16) return("NY");
   return("LATE");
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   trade.SetExpertMagicNumber((ulong)InpMagic);
   trade.SetTypeFillingBySymbol(_Symbol);
   atrHandle = iATR(_Symbol, PERIOD_H1, InpATR);
   if(atrHandle == INVALID_HANDLE)
     {
      Print("KAIROS: iATR handle imeshindwa"); return(INIT_FAILED);
     }
   if(InpSignalLog)
     {
      string fn = StringFormat("KAIROS_signals_%s_%I64d.csv", _Symbol, InpMagic);
      logHandle = FileOpen(fn, FILE_WRITE | FILE_CSV | FILE_ANSI, ',');
      if(logHandle != INVALID_HANDLE)
         FileWrite(logHandle, "ts", "range_pips", "rmin_pips", "nr",
                   "atr_pips", "session", "long_level_pips", "short_level_pips");
      else
         Print("KAIROS: signal-log FileOpen imeshindwa (endelea bila log)");
     }
   PrintFormat("KAIROS init: %s NR=%d ATR=%d SL=%.2f TP=%.2f risk=%.2f%% magic=%I64d noLate>=%d",
               _Symbol, InpNR, InpATR, InpSL_mult, InpTP_mult, InpRiskPct, InpMagic, InpNoLateStart);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
   if(logHandle != INVALID_HANDLE) FileClose(logHandle);
  }

//+------------------------------------------------------------------+
//| positions za EA hii (magic+symbol)                               |
int MyPositions()
  {
   int c = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         PositionGetInteger(POSITION_MAGIC) == InpMagic)
         c++;
     }
   return(c);
  }

//--- futa pending zangu (zote au moja)
void DeleteMyPending(const ulong onlyTicket = 0)
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong tk = OrderGetTicket(i);
      if(tk == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol ||
         OrderGetInteger(ORDER_MAGIC) != InpMagic) continue;
      if(onlyTicket != 0 && tk != onlyTicket) continue;
      trade.OrderDelete(tk);
     }
   if(onlyTicket == 0 || onlyTicket == buyTicket)  buyTicket  = 0;
   if(onlyTicket == 0 || onlyTicket == sellTicket) sellTicket = 0;
  }

//--- OCO: position ikifunguliwa -> futa pending iliyobaki
void OcoCleanup()
  {
   if(MyPositions() > 0 && (buyTicket != 0 || sellTicket != 0))
      DeleteMyPending(0);
  }

//--- lot kwa risk% (SL distance kwa price)
double LotsForRisk(const double slDistPrice)
  {
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(InpRiskPct <= 0.0 || slDistPrice <= 0.0) return(minLot);
   double tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSz  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tickVal <= 0.0 || tickSz <= 0.0) return(minLot);
   double lossPerLot = slDistPrice / tickSz * tickVal;      // $ hasara kwa lot 1 kwenye SL
   if(lossPerLot <= 0.0) return(minLot);
   double risk = InpRiskPct / 100.0 * AccountInfoDouble(ACCOUNT_BALANCE);
   double lots = risk / lossPerLot;
   lots = MathFloor(lots / step) * step;                    // normalize kwa step
   if(lots < minLot) lots = minLot;
   if(lots > maxLot) lots = maxLot;
   return(lots);
  }

//--- daily-loss guard: block kama hasara ya leo >= InpDailyLossPct ya balance ya mwanzo wa siku
bool DailyLossBlocked(const int sigDay)
  {
   if(sigDay != curDay)                                     // siku mpya -> reset baseline
     {
      curDay = sigDay;
      dayStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);
     }
   if(InpDailyLossPct <= 0.0 || dayStartBalance <= 0.0) return(false);
   double loss = dayStartBalance - AccountInfoDouble(ACCOUNT_EQUITY);
   return(loss >= InpDailyLossPct / 100.0 * dayStartBalance);
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   OcoCleanup();                                            // OCO: moja ikijaza -> futa nyingine

   datetime t0 = iTime(_Symbol, PERIOD_H1, 0);
   if(t0 == lastBar) return;                                // si bar mpya
   lastBar = t0;
   ProcessNewBar();
  }

//+------------------------------------------------------------------+
//| bar mpya imefungwa -> tathmini SIGNAL bar (shift=1)               |
void ProcessNewBar()
  {
   // pending za bar iliyopita zilikuwa za bar MOJA (entry window) -> zimeisha, futa
   DeleteMyPending(0);

   int need = MathMax(InpNR + 1, InpATR + 2);
   if(Bars(_Symbol, PERIOD_H1) < need + 2) return;

   double pip = PipSize();
   double tickOff = InpTick * pip;

   // --- nr7: range[1] <= MIN(range za bars 1..InpNR) (inclusive) ---
   double rngSig = iHigh(_Symbol, PERIOD_H1, 1) - iLow(_Symbol, PERIOD_H1, 1);
   double rmin   = rngSig;
   for(int s = 1; s <= InpNR; s++)
     {
      double r = iHigh(_Symbol, PERIOD_H1, s) - iLow(_Symbol, PERIOD_H1, s);
      if(r < rmin) rmin = r;
     }
   bool nr = (rngSig <= rmin);

   // --- no-LATE: Python _mask_context inatumia session ya bar ya ENTRY (i+1), si signal (i)
   //     ("Decidability EP-5: session = saa ya bar ya ENTRY i+1, ratiba ex-ante"). Kwa EA ya H1,
   //     entry bar = bar inayoundwa SASA (shift=0); signal bar = iliyofungwa (shift=1). ---
   MqlDateTime dt;      TimeToStruct(iTime(_Symbol, PERIOD_H1, 1), dt);    // signal bar (day/ts)
   MqlDateTime dtE;     TimeToStruct(iTime(_Symbol, PERIOD_H1, 0), dtE);   // ENTRY bar (session gate)
   string sess = Sess(dtE.hour);
   bool   late = (dtE.hour >= InpNoLateStart);

   // --- ATR (Wilder) ya SIGNAL bar (shift=1) ---
   double atrBuf[];
   double atrPrice = 0.0;
   if(CopyBuffer(atrHandle, 0, 1, 1, atrBuf) == 1) atrPrice = atrBuf[0];

   // --- levels (OCO stops) ---
   double buyStop  = iHigh(_Symbol, PERIOD_H1, 1) + tickOff;
   double sellStop = iLow(_Symbol,  PERIOD_H1, 1) - tickOff;

   // --- signal-log (kila closed bar; PIP-SPACE kwa parity na Python) ---
   if(logHandle != INVALID_HANDLE)
     {
      FileWrite(logHandle,
                (long)iTime(_Symbol, PERIOD_H1, 1),
                DoubleToString(rngSig / pip, 4),
                DoubleToString(rmin / pip, 4),
                (nr ? 1 : 0),
                DoubleToString(atrPrice / pip, 4),
                sess,
                DoubleToString(buyStop / pip, 4),
                DoubleToString(sellStop / pip, 4));
      FileFlush(logHandle);
     }

   // --- guards za kuweka order ---
   if(!nr || late)               return;                    // hakuna compression au LATE
   if(!(atrPrice > 0.0))         return;
   if(MyPositions() >= InpMaxPositions) return;             // position moja kwa symbol
   if(buyTicket != 0 || sellTicket != 0) return;            // tayari kuna OCO hai
   if(DailyLossBlocked(dt.day_of_year)) return;             // daily-loss guard

   // --- SL/TP kwa ATR ya SIGNAL bar; lot kwa risk ---
   double slDist = InpSL_mult * atrPrice;
   double tpDist = InpTP_mult * atrPrice;
   double lots   = LotsForRisk(slDist);
   int    dg     = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double slBuy  = NormalizeDouble(buyStop  - slDist, dg);
   double tpBuy  = NormalizeDouble(buyStop  + tpDist, dg);
   double slSell = NormalizeDouble(sellStop + slDist, dg);
   double tpSell = NormalizeDouble(sellStop - tpDist, dg);
   buyStop  = NormalizeDouble(buyStop,  dg);
   sellStop = NormalizeDouble(sellStop, dg);

   // expiration = mwisho wa bar ya sasa (entry window = bar MOJA, kama Python)
   datetime expiry = iTime(_Symbol, PERIOD_H1, 0) + PeriodSeconds(PERIOD_H1);

   if(trade.BuyStop(lots, buyStop, _Symbol, slBuy, tpBuy,
                    ORDER_TIME_SPECIFIED, expiry, "KAIROS nr7"))
      buyTicket = trade.ResultOrder();
   if(trade.SellStop(lots, sellStop, _Symbol, slSell, tpSell,
                     ORDER_TIME_SPECIFIED, expiry, "KAIROS nr7"))
      sellTicket = trade.ResultOrder();
  }
//+------------------------------------------------------------------+
