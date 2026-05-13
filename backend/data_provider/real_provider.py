# 실데이터 통합 프로바이더.
#
# 시세/차트: Naver Finance → yfinance (둘 다 실패 시 RuntimeError)
# 재무:      pykrx(PER/PBR) + DART (선택)
# 수급:      pykrx
# 뉴스:      Naver 검색 (키 있을 때)
# 리스크:    DART 공시 + Naver 뉴스 보조
#
# pykrx/Mock 시세 폴백은 사용하지 않음 — 진짜 시세 아니면 명확한 에러.

from typing import Dict, Any, List

from .base_provider import BaseProvider
from .pykrx_provider import PykrxProvider
from .mock_provider import MockProvider
from . import (
    dart_provider,
    naver_news_provider,
    naver_finance_provider,
    yfinance_provider,
    naver_risk_provider,
)
from ..keys.api_keys import has_dart, has_naver


class NoMarketDataError(RuntimeError):
    """모든 시세 소스에서 데이터를 받지 못함."""
    pass


class RealProvider(BaseProvider):
    def __init__(self):
        self.pykrx = PykrxProvider()  # 재무·수급용
        self.mock = MockProvider()    # 검색(전체 종목 마스터)·뉴스 폴백용

    def search(self, query: str) -> List[Dict[str, Any]]:
        return self.pykrx.search(query)

    # ---- 시세: Naver → yfinance (Mock 폴백 없음) ----
    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        # 1순위: Naver Finance
        try:
            naver = naver_finance_provider.get_stock_basic_info(stock_code)
            if naver and naver.get("current_price"):
                self._enrich_market_cap_from_yf(naver, stock_code)
                return naver
        except Exception as e:
            print(f"[RealProvider] naver basic 실패: {e}")

        # 2순위: yfinance
        try:
            yf = yfinance_provider.get_stock_basic_info(stock_code)
            if yf and yf.get("current_price"):
                return yf
        except Exception as e:
            print(f"[RealProvider] yfinance basic 실패: {e}")

        raise NoMarketDataError(
            f"실시간 시세를 가져올 수 없습니다 (Naver/Yahoo 모두 실패): {stock_code}"
        )

    def _enrich_market_cap_from_yf(self, base: Dict[str, Any], stock_code: str):
        """네이버에 없는 시총을 yfinance에서 가져와 채움 (실패 무시)."""
        if base.get("market_cap"):
            return
        try:
            yf = yfinance_provider.get_stock_basic_info(stock_code)
            if yf and yf.get("market_cap"):
                base["market_cap"] = yf["market_cap"]
                base["market_cap_type"] = yf["market_cap_type"]
                if yf.get("market"):
                    base["market"] = yf["market"]
        except Exception:
            pass

    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        # 1순위: Naver
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

        raise NoMarketDataError(
            f"차트 데이터를 가져올 수 없습니다 (Naver/Yahoo 모두 실패): {stock_code}"
        )

    # ---- 재무 (pykrx + DART) ----
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

        # 1. 네이버 공개 리스크 페이지 (관리종목/거래정지) — 키 불필요, 항상 사용
        try:
            naver_flags = naver_risk_provider.get_all_risk_flags(stock_code)
            for k, v in naver_flags.items():
                if v:
                    risk[k] = True
        except Exception as e:
            print(f"[RealProvider] naver risk 실패: {e}")

        # 2. DART 공시 (키 있을 때) — 유상증자/전환사채/감사의견 등
        if has_dart():
            disc = dart_provider.get_disclosure_risks(stock_code)
            for k, v in disc.items():
                if v:
                    risk[k] = True

        # 3. Naver 검색 뉴스 (키 있을 때) — 보조 신호
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

        # 4. DART 재무 보강 (자본잠식/3년 적자)
        if has_dart():
            fin = self.get_financial_data(stock_code)
            if fin.get("capital_impairment"):
                risk["capital_impairment"] = True
            if fin.get("three_year_loss"):
                risk["three_year_loss"] = True

        return risk
