# 실데이터 통합 프로바이더.
# pykrx(시세/수급) + DART(재무/공시) + Naver(뉴스) 를 조합하고
# 누락 영역만 Mock 데이터로 폴백.

from typing import Dict, Any, List

from .base_provider import BaseProvider
from .pykrx_provider import PykrxProvider
from .mock_provider import MockProvider
from . import dart_provider, naver_news_provider
from ..keys.api_keys import has_dart, has_naver


class RealProvider(BaseProvider):
    def __init__(self):
        self.pykrx = PykrxProvider()
        self.mock = MockProvider()

    def search(self, query: str) -> List[Dict[str, Any]]:
        return self.pykrx.search(query)

    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        return self.pykrx.get_stock_basic_info(stock_code)

    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        return self.pykrx.get_price_history(stock_code)

    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        base = self.pykrx.get_financial_data(stock_code)  # PER/PBR/EPS/BPS 등
        if has_dart():
            dart_fin = dart_provider.get_financial(stock_code)
            if dart_fin:
                # DART 값으로 덮어쓰기 (재무 안정성/성장성 영역)
                base.update(dart_fin)
        return base

    def get_supply_data(self, stock_code: str) -> Dict[str, Any]:
        return self.pykrx.get_supply_data(stock_code)

    def get_news_data(self, stock_code: str) -> Dict[str, Any]:
        if has_naver():
            try:
                # 종목명 조회를 위해 basic_info 사용 (캐시되어 있음)
                info = self.get_stock_basic_info(stock_code)
                name = info.get("stock_name") or stock_code
                naver = naver_news_provider.get_news(name, stock_code)
                if naver:
                    return naver
            except Exception as e:
                print(f"[RealProvider] naver news 실패: {e}")
        return self.mock.get_news_data(stock_code)

    def get_risk_data(self, stock_code: str) -> Dict[str, Any]:
        # pykrx 폴백 risk 기본값 (대부분 False)
        risk = self.pykrx.get_risk_data(stock_code)

        # DART 공시 키워드 기반 위험 플래그 (정확)
        if has_dart():
            disc = dart_provider.get_disclosure_risks(stock_code)
            for k, v in disc.items():
                if v:
                    risk[k] = True

        # 네이버 뉴스에서 보조 신호
        if has_naver():
            try:
                info = self.get_stock_basic_info(stock_code)
                name = info.get("stock_name") or stock_code
                news = naver_news_provider.get_news(name, stock_code)
                for k in ("rights_issue", "convertible_bond", "warrant", "largest_shareholder_change"):
                    if news.get(k):
                        risk[k] = True
            except Exception:
                pass

        # 재무 기반 위험 보강
        if has_dart():
            fin = self.get_financial_data(stock_code)
            if fin.get("capital_impairment"):
                risk["capital_impairment"] = True
            if fin.get("three_year_loss"):
                risk["three_year_loss"] = True

        return risk
