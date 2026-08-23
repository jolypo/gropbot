from dataclasses import dataclass
@dataclass
class ScoreResult: total:float; components:dict; reasons:list
W={'trend':20,'momentum':15,'volume':15,'structure':20,'breakout':15,'risk_reward':10,'data_quality':5}
def score_row(r,weights=None):
 w=weights or W;c={'trend':w['trend'] if r.close>r.ema20>r.ema50 else 0,'momentum':w['momentum'] if r.rsi14>=55 and r.macd_hist>0 else 0,'volume':w['volume'] if r.volume_ratio>=1.2 else 0,'structure':w['structure'] if r.higher_high and r.higher_low else 0,'breakout':w['breakout'] if r.resistance20 and r.close>r.resistance20 else 0,'risk_reward':w['risk_reward'],'data_quality':w['data_quality']};labels={'trend':'اتجاه صاعد','momentum':'Momentum إيجابي','volume':'حجم تداول مرتفع','structure':'هيكل سعري إيجابي','breakout':'اختراق مقاومة'};return ScoreResult(round(sum(c.values()),2),c,[labels[k] for k in labels if c[k]])
