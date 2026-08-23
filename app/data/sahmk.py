from datetime import datetime,timezone
import httpx,pandas as pd
class SahmkDataProvider:
    BASE_URL='https://api.sahmk.sa/api/v1'
    def __init__(self,api_key,timeout=15):self.api_key=api_key;self.timeout=timeout
    async def quote(self,symbol):
        if not self.api_key: raise RuntimeError('SAHMK_API_KEY is not configured')
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r=await c.get(f'{self.BASE_URL}/quote/{symbol}/',headers={'X-API-Key':self.api_key},params={'data_mode':'delayed'});r.raise_for_status();d=r.json()
        received=datetime.now(timezone.utc); raw=d.get('updated_at') or d.get('timestamp') or d.get('data_timestamp')
        if not raw: raise ValueError('SAHMK response has no verifiable timestamp')
        from .models import Quote
        return Quote(str(d['symbol']),d.get('name',''),float(d['price']),float(d.get('volume') or 0),datetime.fromisoformat(str(raw).replace('Z','+00:00')),received,'SAHMK',bool(d.get('is_delayed',True)))
    async def historical(self,symbol,interval='1d',start=None,end=None):
        if not self.api_key: raise RuntimeError('SAHMK_API_KEY is not configured')
        p={'interval':interval,'data_mode':'delayed'}; p.update({k:v for k,v in {'start':start,'end':end}.items() if v})
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            r=await c.get(f'{self.BASE_URL}/historical/{symbol}/',headers={'X-API-Key':self.api_key},params=p);r.raise_for_status();d=r.json()
        rows=d.get('data',d if isinstance(d,list) else []); df=pd.DataFrame(rows)
        required={'timestamp','open','high','low','close','volume'}
        if not required.issubset(df.columns): raise ValueError(f'Missing OHLCV: {required-set(df.columns)}')
        df['timestamp']=pd.to_datetime(df['timestamp'],utc=True)
        for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
        return df.dropna(subset=['timestamp','open','high','low','close']).sort_values('timestamp')
