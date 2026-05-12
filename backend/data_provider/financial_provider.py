# 실제 재무 API 연동용 구조 (현재는 빈 구현).
# 향후 DART OpenAPI 등으로 교체.

from typing import Dict, Any


class FinancialProvider:
    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        raise NotImplementedError("실제 재무 API 미연동")
