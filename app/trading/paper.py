from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass
class PaperTrade:
 symbol:str;entry:float;stop_loss:float;tp1:float;tp2:float;tp3:float;status:str='OPEN';pnl_pct:float=0;r_multiple:float=0;opened_at:datetime|None=None;closed_at:datetime|None=None
class PaperTradingEngine:
 def __init__(self,slippage_bps=5):self.slippage_bps=slippage_bps
 def simulated_entry(self,next_bar_open):return None if next_bar_open is None else next_bar_open*(1+self.slippage_bps/10000)
 def check_bar(self,t,high,low):
  e=[]
  if t.status=='OPEN' and high>=t.tp1:t.status='TP1';e.append('TP1')
  if t.status=='TP1' and high>=t.tp2:t.status='TP2';e.append('TP2')
  if low<=t.stop_loss:t.status='CLOSED';t.closed_at=datetime.now(timezone.utc);e.append('SL')
  elif t.status=='TP2' and high>=t.tp3:t.status='CLOSED';t.closed_at=datetime.now(timezone.utc);e.append('TP3')
  return e
