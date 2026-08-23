from dataclasses import dataclass
from datetime import datetime
@dataclass
class Quote:
    symbol:str; name:str; price:float; volume:float; data_timestamp:datetime; received_at:datetime; source:str='SAHMK'; is_delayed:bool=False
    @property
    def delay_seconds(self): return max(0,(self.received_at-self.data_timestamp).total_seconds())
