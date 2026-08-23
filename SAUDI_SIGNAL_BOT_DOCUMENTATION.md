# Saudi TASI AI Signal System — Documentation

## Purpose
Rule-based Saudi equity scanning with strict data-quality gates, paper trading and auditable results.

## Data
SAHMK access is isolated in `app/data/sahmk.py`. Strategy modules never call the provider directly. Every quote must have a verifiable timestamp; otherwise the system fails closed.

The official SAHMK documentation currently states that Free/Starter quote data is delayed approximately 15 minutes, while historical OHLCV is Starter+. The adapter explicitly requests delayed mode and does not fabricate historical data.

## Indicators
EMA 9/20/50/200, RSI14, MACD, ATR14, ATR%, average volume, volume ratio, support/resistance and basic higher-high/higher-low structure.

VWAP is intentionally absent until valid intraday session data is available.

## Score
Default research weights: Trend 20, Momentum 15, Volume 15, Structure 20, Breakout 15, Risk/Reward 10, Data Quality 5. These are hypotheses and must be tested, not assumed optimal.

## Probability
Probability is independent from score. Without enough historical outcomes it is `N/A`. Production probability should use calibration and out-of-sample validation.

## Delayed-data model
Signal data timestamp → signal publication → next available bar → simulated entry → slippage → monitoring. This prevents treating a delayed quote as an executable live price.

## Risk
Baseline ATR stop and 1R/2R/3R targets are research parameters only. They are not presented as proven optimal settings.

## Hosting
Render should be treated as hosting infrastructure, not as proof of 24/7 execution. For persistent production state use PostgreSQL; for continuous scanning use a background worker separate from the web health/API service.

## No fake results
The system must never invent Probability, win rate, profits, backtest results or performance images.
