from dataclasses import dataclass
@dataclass
class TradeLevels: entry_low:float;entry_high:float;stop_loss:float;tp1:float;tp2:float;tp3:float;rr:float
def build_levels(price,atr,min_rr=1.5):
 if atr<=0:raise ValueError('ATR_UNAVAILABLE')
 lo,hi=price*.999,price*1.001;stop=price-1.5*atr;risk=price-stop;tp1=price+risk;tp2=price+2*risk;tp3=price+3*risk;rr=(tp3-price)/risk
 if rr<min_rr:raise ValueError('RR_BELOW_MINIMUM')
 return TradeLevels(lo,hi,stop,tp1,tp2,tp3,rr)
