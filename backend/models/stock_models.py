# 종목 관련 Pydantic 모델

from pydantic import BaseModel
from typing import Optional, List


class StockBasicInfo(BaseModel):
    stock_code: str
    stock_name: str
    market: str = "KOSPI"
    sector: str = ""
    current_price: float = 0
    change_rate: float = 0
    volume: int = 0
    trading_value: int = 0
    market_cap: int = 0
    market_cap_type: str = "mid"
    high_52w: float = 0
    low_52w: float = 0


class WatchlistAddRequest(BaseModel):
    stock_code: str
    stock_name: Optional[str] = ""


class SearchResultItem(BaseModel):
    stock_code: str
    stock_name: str
    market: str = "KOSPI"
