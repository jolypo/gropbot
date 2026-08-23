from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    signal_bot_token:str=''; profit_bot_token:str=''; loss_bot_token:str=''; report_bot_token:str=''; telegram_chat_id:str=''; sahmk_api_key:str=''
    database_url:str='sqlite:///trading.db'; health_interval:int=600; min_score:float=75; min_probability:float=65
    max_daily_signals:int=3; max_open_trades:int=5; max_risk_per_trade:float=.01; data_max_delay_minutes:int=30; min_rr:float=1.5
    tp1_percent:float=30; tp2_percent:float=30; tp3_percent:float=40; slippage_bps:float=5; fee_bps:float=15
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
settings=Settings()
