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
from . import dart_provider, naver_news_provider, naver_finance_provider, yfinance_provider
from ..keys.api_keys import has_dart, has_naver


class RealProvider(BaseProvider):
    def __init__(self):
        self.pykrx = PykrxProvider()
        self.mock = MockProvider()

    def search(self, query: str) -> List[Dict[str, Any]]:
        return self.pykrx.search(query)

    # ---- 시세: Naver > yfinance > pykrx > Mock ----
    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        # 1순위: 네이버 (한국 IP 환경에서 최적)
        try:
            naver = naver_finance_provider.get_stock_basic_info(stock_code)
            if naver and naver.get("current_price"):
                self._augment_with_pykrx(naver, stock_code)
                return naver
        except Exception as e:
            print(f"[RealProvider] naver basic 실패: {e}")

        # 2순위: yfinance (해외 IP 환경 대비)
        try:
            yf = yfinance_provider.get_stock_basic_info(stock_code)
            if yf and yf.get("current_price"):
                self._augment_with_pykrx(yf, stock_code)
                return yf
        except Exception as e:
            print(f"[RealProvider] yfinance basic 실패: {e}")

        # 3순위: pykrx → Mock (이미 pykrx 내부에서 mock 폴백)
        return self.pykrx.get_stock_basic_info(stock_code)

    def _augment_with_pykrx(self, base: Dict[str, Any], stock_code: str):
        """시총/시장구분/섹터를 pykrx로 보강 (실패 무시)."""
        try:
            pk = self.pykrx.get_stock_basic_info(stock_code)
            if pk and pk.get("market_cap") and pk.get("market") in ("KOSPI", "KOSDAQ"):
                base["market_cap"] = pk["market_cap"]
                base["market_cap_type"] = pk["market_cap_type"]
                base["market"] = pk["market"]
                if not base.get("sector"):
                    base["sector"] = pk.get("sector", "")
        except Exception:
            pass

    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        # 1순위: 네이버
        try:
            naver = naver_finance_provider.get_price_history(stock_code)
            if naver and len(naver.get("prices", [])) >= 30:
                return naver
        except Exception as e:
            print(f"[RealProvider] naver history 실패: {e}")

        # 2순위: yfinance
        try:
            yf = yfinance_provider.get_price_history(stock_code)
            if yf and len(yf.get("prices", [])) >= 30:
                return yf
        except Exception as e:
            print(f"[RealProvider] yfinance history 실패: {e}")

        # 3순위: pykrx → Mock
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
