from pydantic import BaseModel
from typing import Optional

class Trade(BaseModel):
    trade_id: Optional[str] = None
    trade_status: Optional[str] = None
    time: Optional[str] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    exchange: str
    order_type: str
    currency_pair: str
    limit_order_price: float
    take_profit_price: float
    stop_loss: float
    amount: float
    leverage: int
    user: str
