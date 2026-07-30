//+------------------------------------------------------------------+
//|  KAIROS_CONDUIT.mq5 — ELITEFX conduit EA (Doctrine §9)            |
//|  docs/CONDUIT_BRIDGE_CHARTER.md — EA TUPU (HAINA strategy logic). |
//|                                                                    |
//|  MODEL (live_brain.py) INAAMUA; EA hii INATEKELEZA amri HASA:      |
//|   - inasoma <Files>\<bridge>\commands.json (ubongo)               |
//|   - PLACE_OCO -> BuyStop+SellStop (lots/SL/TP/magic; expiry ya UTC)|
//|   - CANCEL_ALL -> futa pending za magic zetu (kill-switch)         |
//|   - OCO: moja ikijaza -> futa nyingine; expiry -> EXPIRED          |
//|   - inaripoti PLACED/FILLED/CANCELLED/EXPIRED/REJECTED/CLOSED ->   |
//|     <Files>\<bridge>\results.jsonl (mstari mmoja/tukio)            |
//|                                                                    |
//|  HAKUNA nr7/ATR/indicators/decisions — IP §9 ipo Python. EA hii   |
//|  ndiyo itakayokodishwa (lessee anapata conduit TUPU).             |
//|                                                                    |
//|  DEMO PEKEE (OnInit guard). Live = Faza 4 (SAINI YA PD §3.1b/§9). |
//+------------------------------------------------------------------+
#property copyright "ELITEFX"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

//--- inputs ---------------------------------------------------------
input string InpBridgeDir   = "bridge";   // folda ndani ya MQL5\Files (= ELITEFX_BRIDGE_DIR)
input int    InpPollSeconds = 5;          // muda wa poll ya commands.json
input long   InpMagicFilter = 0;          // 0 = magics zote; vinginevyo magic moja
input bool   InpEnabled      = true;      // false = poll lakini usiweke PLACE_OCO (CANCEL bado inafanya)

//--- globals --------------------------------------------------------
CTrade g_trade;
long   g_lastSeq = -1;
string g_processed[];     // cmd_id zilizotekelezwa (idempotent kati ya restarts)

struct OcoPair
  {
   string cmd_id;
   string symbol;
   long   magic;
   ulong  buyTicket;
   ulong  sellTicket;
   ulong  posTicket;
   double lots;
   double sl_buy, tp_buy, sl_sell, tp_sell;
   long   expiry;         // epoch UTC (managed na EA, si broker)
   bool   filled;
  };
OcoPair g_oco[];

//+------------------------------------------------------------------+
string CommandsPath() { return(InpBridgeDir + "\\commands.json"); }
string ResultsPath()  { return(InpBridgeDir + "\\results.jsonl"); }
string ProcessedPath(){ return(InpBridgeDir + "\\processed.txt"); }

//--- flat JSON helpers (schema YETU pekee — hakuna JSON lib) --------
double JNum(const string s, const string key, const double def = 0.0)
  {
   int p = StringFind(s, "\"" + key + "\"");
   if(p < 0) return def;
   p = StringFind(s, ":", p);
   if(p < 0) return def;
   p++;
   int L = StringLen(s);
   while(p < L)
     {
      ushort ch = StringGetCharacter(s, p);
      if(ch == ' ' || ch == '\t') p++; else break;
     }
   int e = p;
   while(e < L)
     {
      ushort ch = StringGetCharacter(s, e);
      if((ch >= '0' && ch <= '9') || ch == '.' || ch == '-' || ch == '+' || ch == 'e' || ch == 'E')
         e++;
      else break;
     }
   if(e <= p) return def;
   return((double)StringToDouble(StringSubstr(s, p, e - p)));
  }

string JStr(const string s, const string key)
  {
   int p = StringFind(s, "\"" + key + "\"");
   if(p < 0) return "";
   p = StringFind(s, ":", p);
   if(p < 0) return "";
   p = StringFind(s, "\"", p);
   if(p < 0) return "";
   p++;
   int e = StringFind(s, "\"", p);
   if(e < 0) return "";
   return(StringSubstr(s, p, e - p));
  }

//--- processed set (idempotency) -----------------------------------
bool IsProcessed(const string cmd_id)
  {
   for(int i = 0; i < ArraySize(g_processed); i++)
      if(g_processed[i] == cmd_id) return(true);
   return(false);
  }

void MarkProcessed(const string cmd_id)
  {
   int n = ArraySize(g_processed);
   ArrayResize(g_processed, n + 1);
   g_processed[n] = cmd_id;
   int h = FileOpen(ProcessedPath(), FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(h != INVALID_HANDLE)
     {
      FileSeek(h, 0, SEEK_END);
      FileWriteString(h, cmd_id + "\n");
      FileClose(h);
     }
  }

void LoadProcessed()
  {
   ArrayResize(g_processed, 0);
   if(!FileIsExist(ProcessedPath())) return;
   int h = FileOpen(ProcessedPath(), FILE_READ | FILE_TXT | FILE_ANSI);
   if(h == INVALID_HANDLE) return;
   while(!FileIsEnding(h))
     {
      string line = FileReadString(h);
      if(StringLen(line) > 0)
        {
         int n = ArraySize(g_processed);
         ArrayResize(g_processed, n + 1);
         g_processed[n] = line;
        }
     }
   FileClose(h);
  }

//--- results writer (EA pekee inaandika; ubongo unasoma) -----------
void WriteResult(const string json_line)
  {
   int h = FileOpen(ResultsPath(), FILE_READ | FILE_WRITE | FILE_TXT | FILE_ANSI);
   if(h == INVALID_HANDLE) { Print("KAIROS_CONDUIT: results.jsonl open fail"); return; }
   FileSeek(h, 0, SEEK_END);
   FileWriteString(h, json_line + "\n");
   FileClose(h);
  }

long NowUtc() { return((long)TimeGMT()); }

//+------------------------------------------------------------------+
int OnInit()
  {
   // DEMO-ONLY guard — HAKUNA njia ya kuipita (Faza 4 live = SAINI YA PD)
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
     {
      Print("KAIROS_CONDUIT: account SI DEMO — imezuiwa. LIVE inahitaji SAINI YA PD (Faza 4, §3.1b/§9).");
      return(INIT_FAILED);
     }
   LoadProcessed();
   EventSetTimer(MathMax(1, InpPollSeconds));
   PrintFormat("KAIROS_CONDUIT init: bridge=%s poll=%ds magicFilter=%I64d enabled=%s (DEMO, conduit TUPU)",
               InpBridgeDir, InpPollSeconds, InpMagicFilter, (InpEnabled ? "true" : "false"));
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { EventKillTimer(); }

//+------------------------------------------------------------------+
int FindByOrder(const ulong order)
  {
   for(int i = 0; i < ArraySize(g_oco); i++)
      if(g_oco[i].buyTicket == order || g_oco[i].sellTicket == order) return(i);
   return(-1);
  }

int FindByPos(const long posid)
  {
   for(int i = 0; i < ArraySize(g_oco); i++)
      if((long)g_oco[i].posTicket == posid) return(i);
   return(-1);
  }

void RemoveOco(const int idx)
  {
   int n = ArraySize(g_oco);
   if(idx < 0 || idx >= n) return;
   for(int i = idx; i < n - 1; i++) g_oco[i] = g_oco[i + 1];
   ArrayResize(g_oco, n - 1);
  }

bool MagicOurs(const long magic)
  {
   return(InpMagicFilter == 0 || magic == InpMagicFilter);
  }

//--- CANCEL_ALL: futa pending za magic zetu + emit CANCELLED --------
void DoCancelAll(const string cmd_id)
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong tk = OrderGetTicket(i);
      if(tk == 0) continue;
      if(MagicOurs(OrderGetInteger(ORDER_MAGIC)))
         g_trade.OrderDelete(tk);
     }
   for(int i = ArraySize(g_oco) - 1; i >= 0; i--)
      if(!g_oco[i].filled)
        {
         WriteResult(StringFormat("{\"cmd_id\":\"%s\",\"event\":\"CANCELLED\",\"order_id\":\"%s\",\"symbol\":\"%s\",\"ts\":%I64d}",
                                  g_oco[i].cmd_id, g_oco[i].cmd_id, g_oco[i].symbol, NowUtc()));
         RemoveOco(i);
        }
   if(cmd_id != "") MarkProcessed(cmd_id);
  }

//--- PLACE_OCO: BuyStop + SellStop HASA kama amri --------------------
void DoPlaceOco(const string chunk, const string cmd_id)
  {
   long   magic  = (long)JNum(chunk, "magic");
   if(!MagicOurs(magic)) return;                 // instance nyingine inashughulikia (usimark)
   string symbol = JStr(chunk, "symbol");
   double lots   = JNum(chunk, "lots");
   double buy    = JNum(chunk, "buy_stop"),  sell = JNum(chunk, "sell_stop");
   double slB    = JNum(chunk, "sl_buy"),    tpB  = JNum(chunk, "tp_buy");
   double slS    = JNum(chunk, "sl_sell"),   tpS  = JNum(chunk, "tp_sell");
   long   expiry = (long)JNum(chunk, "expiry_utc");
   if(symbol == "" || lots <= 0.0) { MarkProcessed(cmd_id); return; }
   SymbolSelect(symbol, true);

   g_trade.SetExpertMagicNumber((ulong)magic);
   bool okB = g_trade.BuyStop(lots, buy, symbol, slB, tpB, ORDER_TIME_GTC, 0, cmd_id);
   ulong bt = okB ? g_trade.ResultOrder() : 0;
   bool okS = g_trade.SellStop(lots, sell, symbol, slS, tpS, ORDER_TIME_GTC, 0, cmd_id);
   ulong st = okS ? g_trade.ResultOrder() : 0;

   if(!okB && !okS)
     {
      WriteResult(StringFormat("{\"cmd_id\":\"%s\",\"event\":\"REJECTED\",\"order_id\":\"%s\",\"symbol\":\"%s\",\"ts\":%I64d,\"error\":\"%s\"}",
                               cmd_id, cmd_id, symbol, NowUtc(), g_trade.ResultRetcodeDescription()));
      MarkProcessed(cmd_id);
      return;
     }
   int n = ArraySize(g_oco);
   ArrayResize(g_oco, n + 1);
   g_oco[n].cmd_id = cmd_id; g_oco[n].symbol = symbol; g_oco[n].magic = magic;
   g_oco[n].buyTicket = bt;  g_oco[n].sellTicket = st; g_oco[n].posTicket = 0;
   g_oco[n].lots = lots; g_oco[n].sl_buy = slB; g_oco[n].tp_buy = tpB;
   g_oco[n].sl_sell = slS; g_oco[n].tp_sell = tpS; g_oco[n].expiry = expiry; g_oco[n].filled = false;

   WriteResult(StringFormat("{\"cmd_id\":\"%s\",\"event\":\"PLACED\",\"order_id\":\"%I64u\",\"symbol\":\"%s\",\"ts\":%I64d}",
                            cmd_id, (bt ? bt : st), symbol, NowUtc()));
   MarkProcessed(cmd_id);
  }

//--- parse commands.json -> tekeleza amri mpya ----------------------
void PollCommands()
  {
   if(!FileIsExist(CommandsPath())) return;
   int h = FileOpen(CommandsPath(), FILE_READ | FILE_TXT | FILE_ANSI);
   if(h == INVALID_HANDLE) return;
   string text = "";
   while(!FileIsEnding(h)) text += FileReadString(h) + "\n";
   FileClose(h);
   if(StringLen(text) == 0) return;

   long seq = (long)JNum(text, "seq", -1);
   if(seq >= 0 && seq == g_lastSeq) return;       // seq ile ile -> usisome tena (idempotent)

   int pos = 0;
   while(true)
     {
      int c = StringFind(text, "\"cmd_id\"", pos);
      if(c < 0) break;
      int nxt = StringFind(text, "\"cmd_id\"", c + 8);
      string chunk = (nxt < 0) ? StringSubstr(text, c) : StringSubstr(text, c, nxt - c);
      string cmd_id = JStr(chunk, "cmd_id");
      string action = JStr(chunk, "action");
      if(cmd_id != "" && !IsProcessed(cmd_id))
        {
         if(action == "CANCEL_ALL")            DoCancelAll(cmd_id);       // kill-switch (daima)
         else if(action == "PLACE_OCO" && InpEnabled) DoPlaceOco(chunk, cmd_id);
        }
      if(nxt < 0) break;
      pos = nxt;
     }
   if(seq >= 0) g_lastSeq = seq;
  }

//--- expiry scan: pending isiyojaza baada ya expiry -> EXPIRED -------
void ScanExpiry()
  {
   long now = NowUtc();
   for(int i = ArraySize(g_oco) - 1; i >= 0; i--)
     {
      if(g_oco[i].filled) continue;
      if(now < g_oco[i].expiry) continue;
      if(g_oco[i].buyTicket  != 0 && OrderSelect(g_oco[i].buyTicket))  g_trade.OrderDelete(g_oco[i].buyTicket);
      if(g_oco[i].sellTicket != 0 && OrderSelect(g_oco[i].sellTicket)) g_trade.OrderDelete(g_oco[i].sellTicket);
      WriteResult(StringFormat("{\"cmd_id\":\"%s\",\"event\":\"EXPIRED\",\"order_id\":\"%s\",\"symbol\":\"%s\",\"ts\":%I64d}",
                               g_oco[i].cmd_id, g_oco[i].cmd_id, g_oco[i].symbol, now));
      RemoveOco(i);
     }
  }

void OnTimer()
  {
   PollCommands();
   ScanExpiry();
  }

//+------------------------------------------------------------------+
//| fills/closes -> results (OCO + lifecycle)                        |
void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &req,
                        const MqlTradeResult &res)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD) return;
   ulong deal = trans.deal;
   if(!HistoryDealSelect(deal)) return;
   long dmagic = HistoryDealGetInteger(deal, DEAL_MAGIC);
   if(!MagicOurs(dmagic)) return;

   long   entry  = HistoryDealGetInteger(deal, DEAL_ENTRY);
   ulong  dorder = (ulong)HistoryDealGetInteger(deal, DEAL_ORDER);
   long   posid  = HistoryDealGetInteger(deal, DEAL_POSITION_ID);
   string sym    = HistoryDealGetString(deal, DEAL_SYMBOL);
   double price  = HistoryDealGetDouble(deal, DEAL_PRICE);
   double vol    = HistoryDealGetDouble(deal, DEAL_VOLUME);
   int    dg     = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);

   if(entry == DEAL_ENTRY_IN)                    // pending imejaza -> FILLED
     {
      int idx = FindByOrder(dorder);
      if(idx < 0) return;
      g_oco[idx].filled = true; g_oco[idx].posTicket = (ulong)posid;
      ulong other = (g_oco[idx].buyTicket == dorder) ? g_oco[idx].sellTicket : g_oco[idx].buyTicket;
      if(other != 0 && OrderSelect(other)) g_trade.OrderDelete(other);   // OCO: futa nyingine
      bool isBuy = (HistoryDealGetInteger(deal, DEAL_TYPE) == DEAL_TYPE_BUY);
      double sl = isBuy ? g_oco[idx].sl_buy : g_oco[idx].sl_sell;
      double tp = isBuy ? g_oco[idx].tp_buy : g_oco[idx].tp_sell;
      WriteResult(StringFormat(
         "{\"cmd_id\":\"%s\",\"event\":\"FILLED\",\"order_id\":\"%I64d\",\"symbol\":\"%s\",\"side\":\"%s\",\"price\":%s,\"qty\":%s,\"sl\":%s,\"tp\":%s,\"ts\":%I64d}",
         g_oco[idx].cmd_id, posid, sym, (isBuy ? "BUY" : "SELL"),
         DoubleToString(price, dg), DoubleToString(vol, 2),
         DoubleToString(sl, dg), DoubleToString(tp, dg), NowUtc()));
     }
   else if(entry == DEAL_ENTRY_OUT)              // position imefungwa -> CLOSED (+pnl)
     {
      int idx = FindByPos(posid);
      if(idx < 0) return;
      double pnl = HistoryDealGetDouble(deal, DEAL_PROFIT)
                 + HistoryDealGetDouble(deal, DEAL_SWAP)
                 + HistoryDealGetDouble(deal, DEAL_COMMISSION);
      WriteResult(StringFormat(
         "{\"cmd_id\":\"%s\",\"event\":\"CLOSED\",\"order_id\":\"%I64d\",\"symbol\":\"%s\",\"pnl\":%s,\"exit_price\":%s,\"ts\":%I64d}",
         g_oco[idx].cmd_id, posid, sym, DoubleToString(pnl, 2), DoubleToString(price, dg), NowUtc()));
      RemoveOco(idx);
     }
  }
//+------------------------------------------------------------------+
