# 데이터 프로바이더 추상 베이스.
# 모든 분석기는 이 인터페이스만 보고 동작하므로
# 실제 API로 교체할 때도 분석 로직은 변경하지 않는다.

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseProvider(ABC):
    @abstractmethod
    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]: ...

    @abstractmethod
    def get_price_history(self, stock_code: str) -> Dict[str, Any]: ...

    @abstractmethod
    def get_financial_data(self, stock_code: str) -> Dict[str, Any]: ...

    @abstractmethod
    def get_supply_data(self, stock_code: str) -> Dict[str, Any]: ...

    @abstractmethod
    def get_news_data(self, stock_code: str) -> Dict[str, Any]: ...

    @abstractmethod
    def get_risk_data(self, stock_code: str) -> Dict[str, Any]: ...

    @abstractmethod
    def search(self, query: str): ...
