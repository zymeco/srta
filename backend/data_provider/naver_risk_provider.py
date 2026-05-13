# 네이버 금융 위험 종목 리스트 프로바이더.
# DART 키 없이도 관리종목/거래정지 같은 핵심 위험 정보를 받는다.
#
# 페이지:
#   관리종목: https://finance.naver.com/sise/management.naver
#   거래정지: https://finance.naver.com/sise/trading_halt.naver
#
# 매일 한 번 갱신되므로 24시간 캐시.

import re
import httpx
from typing import Set, Dict, Any

from ..utils.cache import memoize

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
_HEADERS = {"User-Agent": _UA, "Referer": "https://finance.naver.com/"}

_CODE_RE = re.compile(r'/item/main\.naver\?code=(\d{6})')


def _fetch_codes(url: str) -> Set[str]:
    try:
        with httpx.Client(timeout=10.0, headers=_HEADERS, follow_redirects=True) as c:
            r = c.get(url)
            if r.status_code != 200:
                return set()
            text = r.content.decode("euc-kr", errors="replace")
            return set(_CODE_RE.findall(text))
    except Exception as e:
        print(f"[Naver risk] {url[-40:]} 실패: {e}")
        return set()


def get_management_stocks() -> Set[str]:
    """관리종목 코드 집합 (24h 캐시)."""
    return memoize(
        "naver_risk:management",
        60 * 60 * 24,
        lambda: _fetch_codes("https://finance.naver.com/sise/management.naver"),
    ) or set()


def get_trading_halt_stocks() -> Set[str]:
    """거래정지 코드 집합 (24h 캐시)."""
    return memoize(
        "naver_risk:halt",
        60 * 60 * 24,
        lambda: _fetch_codes("https://finance.naver.com/sise/trading_halt.naver"),
    ) or set()


def get_all_risk_flags(stock_code: str) -> Dict[str, bool]:
    """주어진 종목이 어떤 공개 리스크 카테고리에 속하는지."""
    code = (stock_code or "").strip()
    flags = {
        "management_stock": False,
        "trading_halt_history": False,
        "investment_warning": False,
        "investment_danger": False,
        "delisting_risk": False,
    }
    if not code:
        return flags
    try:
        if code in get_management_stocks():
            flags["management_stock"] = True
            # 관리종목은 상장폐지 위험도 동반하는 경우가 많음
            flags["delisting_risk"] = True
    except Exception:
        pass
    try:
        if code in get_trading_halt_stocks():
            flags["trading_halt_history"] = True
    except Exception:
        pass
    return flags
