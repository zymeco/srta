# 시장 컨텍스트 — KOSPI/KOSDAQ 추세를 분석에 반영.
# 상승장에서는 추격매수 위험 완화, 약세장에서는 가치주 가중 등.

from typing import Dict, Any
from ..data_provider import yfinance_provider
from ..utils.cache import memoize


# 야후 심볼: KOSPI=^KS11, KOSDAQ=^KQ11
INDEX_MAP = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
}


def _trend_of(closes):
    if not closes or len(closes) < 60:
        return None
    cur = closes[-1]
    m20 = sum(closes[-20:]) / 20
    m60 = sum(closes[-60:]) / 60
    chg5 = (closes[-1] - closes[-6]) / closes[-6] * 100 if len(closes) >= 6 and closes[-6] else 0
    chg20 = (closes[-1] - closes[-21]) / closes[-21] * 100 if len(closes) >= 21 and closes[-21] else 0
    chg60 = (closes[-1] - closes[-61]) / closes[-61] * 100 if len(closes) >= 61 and closes[-61] else 0

    if cur > m20 > m60 and chg60 > 10:
        state = "강한 상승장"; score = 85
    elif cur > m20 > m60 and chg60 > 3:
        state = "상승장"; score = 70
    elif cur > m20 > m60:
        state = "약한 상승"; score = 60
    elif cur < m20 < m60 and chg60 < -10:
        state = "강한 하락장"; score = 15
    elif cur < m20 < m60:
        state = "하락장"; score = 35
    else:
        state = "횡보"; score = 50
    return {
        "state": state, "score": score,
        "current": round(cur, 2),
        "ma20": round(m20, 2), "ma60": round(m60, 2),
        "change_5d": round(chg5, 2),
        "change_20d": round(chg20, 2),
        "change_60d": round(chg60, 2),
    }


def _fetch_index(symbol):
    # yfinance_provider에 일반 종목용 함수가 KS suffix를 붙이므로
    # 인덱스는 직접 야후 URL 호출
    import httpx
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "1y", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as c:
            r = c.get(url, params=params)
            if r.status_code != 200:
                return None
            data = r.json()
            res = (data.get("chart") or {}).get("result") or []
            if not res:
                return None
            ind = (((res[0].get("indicators") or {}).get("quote") or [{}])[0]) or {}
            closes = [c for c in (ind.get("close") or []) if c is not None]
            return closes
    except Exception as e:
        print(f"[market_context] {symbol} 실패: {e}")
        return None


def get_market_context(market: str = "KOSPI") -> Dict[str, Any]:
    def factory():
        sym = INDEX_MAP.get(market, "^KS11")
        closes = _fetch_index(sym)
        if not closes:
            return {"state": "정보부족", "score": 50, "_source": "fallback"}
        trend = _trend_of(closes)
        if not trend:
            return {"state": "정보부족", "score": 50}
        trend["market"] = market
        trend["_source"] = "yahoo"
        return trend
    return memoize(f"market_ctx:{market}", 600, factory) or {"state": "정보부족", "score": 50}


def get_both_markets() -> Dict[str, Any]:
    return {
        "kospi": get_market_context("KOSPI"),
        "kosdaq": get_market_context("KOSDAQ"),
    }


def market_adjustment_multiplier(market_score: int, sector_category: str) -> Dict[str, float]:
    """시장 상태에 따른 점수/위험 보정 multiplier."""
    if market_score >= 75:  # 강한 상승장
        if sector_category.startswith("growth"):
            return {"score": 1.05, "chasing_risk": 0.7}  # 성장주 가중 + 추격위험 30% 완화
        return {"score": 1.02, "chasing_risk": 0.85}
    if market_score >= 60:  # 상승장
        return {"score": 1.0, "chasing_risk": 0.9}
    if market_score <= 25:  # 하락장
        if sector_category.startswith("value"):
            return {"score": 1.05, "chasing_risk": 1.1}
        return {"score": 0.95, "chasing_risk": 1.2}
    return {"score": 1.0, "chasing_risk": 1.0}
