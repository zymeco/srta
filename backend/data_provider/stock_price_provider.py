# 실제 시세 API 연동용 구조 (현재는 빈 구현).
# 향후 pykrx, KRX, yfinance, 증권사 OpenAPI 등으로 교체.

from typing import Dict, Any


class StockPriceProvider:
    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        # TODO: 실제 시세 API 호출 구현
        raise NotImplementedError("실제 시세 API 미연동")
