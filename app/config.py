from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =====================================================
    # TELEGRAM
    # =====================================================

    signal_bot_token: str = ""
    profit_bot_token: str = ""
    loss_bot_token: str = ""
    report_bot_token: str = ""

    telegram_chat_id: str = ""


    # =====================================================
    # SAHMK
    # =====================================================

    sahmk_api_key: str = ""


    # =====================================================
    # TASI SYMBOLS
    # =====================================================

    tasi_symbols: str = (
        "2222,1120,2010,2020,2030,"
        "2040,2050,2060,2070,2080,"
        "2090,2100,2110,2120,2130,"
        "2140,2150,2160,2170,2180,"
        "2190,2200,2210,2220,2230"
    )


    # =====================================================
    # DATABASE
    # =====================================================

    database_url: str = "sqlite:///trading.db"


    # =====================================================
    # SYSTEM
    # =====================================================

    health_interval: int = 600

    min_score: float = 75

    min_probability: float = 65

    max_daily_signals: int = 3

    max_open_trades: int = 5

    max_risk_per_trade: float = 0.01

    data_max_delay_minutes: int = 30

    min_rr: float = 1.5


    # =====================================================
    # TAKE PROFITS
    # =====================================================

    tp1_percent: float = 30

    tp2_percent: float = 30

    tp3_percent: float = 40


    # =====================================================
    # COSTS
    # =====================================================

    slippage_bps: float = 5

    fee_bps: float = 15


    # =====================================================
    # ENV
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
