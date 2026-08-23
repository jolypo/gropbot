from datetime import datetime,timezone
from fastapi import FastAPI
from app.config import settings
app=FastAPI(title='Saudi TASI AI Signal System')
@app.get('/health')
async def health():return {'status':'alive','timestamp':datetime.now(timezone.utc).isoformat(),'database':'configured' if settings.database_url else 'missing','data_provider':'configured' if settings.sahmk_api_key else 'not_configured'}
