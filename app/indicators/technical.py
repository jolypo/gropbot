import pandas as pd,numpy as np
def add_indicators(df):
 x=df.copy();c,h,l,v=x.close,x.high,x.low,x.volume
 for n in (9,20,50,200):x[f'ema{n}']=c.ewm(span=n,adjust=False).mean()
 d=c.diff();g=d.clip(lower=0).rolling(14).mean();loss=(-d.clip(upper=0)).rolling(14).mean();x['rsi14']=100-100/(1+g/loss.replace(0,np.nan))
 e12=c.ewm(span=12,adjust=False).mean();e26=c.ewm(span=26,adjust=False).mean();x['macd']=e12-e26;x['macd_signal']=x.macd.ewm(span=9,adjust=False).mean();x['macd_hist']=x.macd-x.macd_signal
 tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1);x['atr14']=tr.rolling(14).mean();x['atr_pct']=x.atr14/c*100
 x['avg_volume20']=v.rolling(20).mean();x['volume_ratio']=v/x.avg_volume20.replace(0,np.nan);x['support20']=l.rolling(20).min();x['resistance20']=h.rolling(20).max().shift(1);x['higher_high']=h>h.shift(1);x['higher_low']=l>l.shift(1);return x
