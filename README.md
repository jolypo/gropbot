# Saudi TASI AI Signal System

Foundation for Saudi TASI technical signals, paper trading, auditability and performance reporting.

## Current state
- Signals Only + Paper Trading; no real orders.
- SAHMK is isolated behind `SahmkDataProvider`.
- Delayed-mode requests are explicit and stale data is rejected.
- EMA 9/20/50/200, RSI14, MACD, ATR14, volume ratio and basic structure.
- Score is separate from Probability.
- Probability remains `N/A` until sufficient historical outcomes exist.
- Paper entry uses the next available bar plus configurable slippage.
- SQLAlchemy SQLite/PostgreSQL-ready foundation.
- FastAPI `/health`.
- Docker/Render configuration.
- Offline unit tests.

## Run
```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
pytest -q
python -m app.main
```

## Important
Verify the exact SAHMK endpoints and plan entitlements before live integration. The official SAHMK docs currently show the API base as `https://api.sahmk.sa/api/v1`, delayed prices for Free/Starter, and historical OHLCV as Starter+. No live API key is embedded in this repository.

## Production gates
1. Verify the user's SAHMK plan and endpoint access.
2. Add Saudi market calendar/session scheduler.
3. Complete the four Telegram services.
4. Add full trade-event ledger/restart recovery.
5. Calibrate Probability with train/validation/out-of-sample data.
6. Add walk-forward backtesting with fees/slippage/delay.
7. Use PostgreSQL for persistent hosting and a separate worker for scanning.
8. Run an extended paper-trading period before any real execution consideration.
