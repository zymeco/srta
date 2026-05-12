# 실데이터 통합 프로바이더.
# 우선순위:
#   시세/차트:  Naver Finance > pykrx > Mock
#   재무:       pykrx(PER/PBR) + DART(부채/현금흐름/성장률) > Mock
#   수급:       pykrx > Mock
#   뉴스:       Naver 검색 > Mock
#   리스크:     DART 공시 + Naver 뉴스 보조 > Mock

from typing import Dict, Any, List

from .base_provider import BaseProvider
from .pykrx_provider import PykrxProvider
from .mock_provider import MockProvider
from . import dart_provider, naver_news_provider, naver_finance_provider
from ..keys.api_keys import has_dart, has_naver


class RealProvider(BaseProvider):
    def __init__(self):
        self.pykrx = PykrxProvider()
        self.mock = MockProvider()

    def search(self, query: str) -> List[Dict[str, Any]]:
        return self.pykrx.search(query)

    # ---- 시세: Naver 우선 ----
    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        naver = naver_finance_provider.get_stock_basic_info(stock_code)
        if naver and naver.get("current_price"):
            # 시총·시장구분은 pykrx에서 보강 시도
            try:
                pk = self.pykrx.get_stock_basic_info(stock_code)
                # pykrx가 mock 폴백을 안 한 경우만 (정상 응답일 때만) 시총 갱신
                if pk and pk.get("market_cap") and pk.get("market") in ("KOSPI", "KOSDAQ"):
                    naver["market_cap"] = pk["market_cap"]
                    naver["market_cap_type"] = pk["market_cap_type"]
                    naver["market"] = pk["market"]
                    naver["sector"] = pk.get("sector") or naver.get("sector", "")
            except Exception:
                pass
            return naver
        # 폴백
        return self.pykrx.get_stock_basic_info(stock_code)

    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        naver = naver_finance_provider.get_price_history(stock_code)
        if naver:
            return naver
        return self.pykrx.get_price_history(stock_code)

    # ---- 재무 ----
    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        base = self.pykrx.get_financial_data(stock_code)
        if has_dart():
            dart_fin = dart_provider.get_financial(stock_code)
            if dart_fin:
                base.update(dart_fin)
        return base

    # ---- 수급 ----
    def get_supply_data(self, stock_code: str) -> Dict[str, Any]:
        return self.pykrx.get_supply_data(stock_code)

    # ---- 뉴스 ----
    def get_news_data(self, stock_code: str) -> Dict[str, Any]:
        if has_naver():
            try:
                info = self.get_stock_basic_info(stock_code)
                name = info.get("stock_name") or stock_code
                n = naver_news_provider.get_news(name, stock_code)
                if n:
                    return n
            except Exception as e:
                print(f"[RealProvider] naver news 실패: {e}")
        return self.mock.get_news_data(stock_code)

    # ---- 리스크 ----
    def get_risk_data(self, stock_code: str) -> Dict[str, Any]:
        risk = self.pykrx.get_risk_data(stock_code)

        if has_dart():
            disc = dart_provider.get_disclosure_risks(stock_code)
            for k, v in disc.items():
                if v:
                    risk[k] = True

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

        if has_dart():
            fin = self.get_financial_data(stock_code)
            if fin.get("capital_impairment"):
                risk["capital_impairment"] = True
            if fin.get("three_year_loss"):
                risk["three_year_loss"] = True

        return risk
