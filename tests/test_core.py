from datetime import datetime,timezone,timedelta
from types import SimpleNamespace
from app.data.models import Quote
from app.data.validation import validate_quote
from app.strategy.scoring import score_row
from app.strategy.probability import ProbabilityCalibrator
from app.risk.engine import build_levels
from app.trading.paper import PaperTrade,PaperTradingEngine
def test_stale():
 n=datetime.now(timezone.utc);assert validate_quote(Quote('1120','',100,1,n-timedelta(minutes=31),n),30)==(False,'STALE_DATA')
def test_score():
 r=SimpleNamespace(close=110,ema20=100,ema50=90,rsi14=60,macd_hist=1,volume_ratio=1.5,higher_high=True,higher_low=True,resistance20=105);assert score_row(r).total==100
def test_probability():assert ProbabilityCalibrator(100).fit([1]*20) is None
def test_risk():
 x=build_levels(100,2);assert x.stop_loss<100<x.tp3 and x.rr>=1.5
def test_paper():
 t=PaperTrade('1120',100,95,102,104,106);assert 'TP1' in PaperTradingEngine().check_bar(t,103,99)
