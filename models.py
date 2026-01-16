from pydantic import BaseModel
from typing import Literal

class Instrument(BaseModel):
    ticker: str
    type: Literal['future', 'option']
    strike: float = 0.0
    expiry: float = 0.0  
    is_call: bool = True

class Position(BaseModel):
    instrument: Instrument
    quantity: int  
    entry_price: float

class MarketTick(BaseModel):
    ticker: str
    price: float
    volatility: float