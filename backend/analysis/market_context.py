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
    """시장 추세 판정 — 단기(5일) > 중기(20일) > 장기(60일) 순으로 가중.
    60일이 강세여도 최근 5일이 -3% 이상 하락이면 '조정 중' 또는 '하락장'으로 판정.
    사용자가 체감하는 '지금' 시장에 더 가깝게."""
    if not closes or len(closes) < 60:
        return None
    cur = closes[-1]
    m5  = sum(closes[-5:]) / 5
    m20 = sum(closes[-20:]) / 20
    m60 = sum(closes[-60:]) / 60
    chg5  = (closes[-1] - closes[-6])  / closes[-6]  * 100 if len(closes) >= 6  and closes[-6]  else 0
    chg20 = (closes[-1] - closes[-21]) / closes[-21] * 100 if len(closes) >= 21 and closes[-21] else 0
    chg60 = (closes[-1] - closes[-61]) / closes[-61] * 100 if len(closes) >= 61 and closes[-61] else 0
    short_above_mid = m5 > m20

    # 우선순위: 단기 위험 신호부터
    if chg5 <= -7:
        state, score = "급락 / 강한 하락", 12
    elif chg5 <= -5 and chg20 <= 0:
        state, score = "강한 하락장", 18
    elif chg5 <= -3:
        # 단기 3% 이상 하락 — 60일이 강세여도 '조정' 판정
        state, score = "조정 중", 38
    elif chg5 < 0 and chg20 < 0:
        state, score = "하락장", 30
    elif chg5 < 0 and cur > m20:
        state, score = "단기 조정 / 추세 유지", 50
    elif chg5 > 1 and chg20 > 3 and chg60 > 10 and cur > m20 > m60 and short_above_mid:
        state, score = "강한 상승장", 85
    elif chg5 > 0 and chg20 > 2 and cur > m20:
        state, score = "상승장", 70
    elif chg5 > 0 and cur > m20:
        state, score = "약한 상승", 60
    elif cur < m20 < m60:
        state, score = "하락장", 30
    else:
        state, score = "횡보", 50

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
    if market_score >= 80:  # 강한 상승장
        if sector_category.startswith("growth"):
            return {"score": 1.05, "chasing_risk": 0.7}
        return {"score": 1.02, "chasing_risk": 0.85}
    if market_score >= 65:  # 상승장
        return {"score": 1.0, "chasing_risk": 0.9}
    if market_score <= 20:  # 강한 하락장 / 급락
        if sector_category.startswith("value") or sector_category.startswith("defensive"):
            return {"score": 1.05, "chasing_risk": 1.15}
        return {"score": 0.90, "chasing_risk": 1.35}
    if market_score <= 35:  # 하락장 / 조정
        if sector_category.startswith("value") or sector_category.startswith("defensive"):
            return {"score": 1.02, "chasing_risk": 1.1}
        return {"score": 0.95, "chasing_risk": 1.2}
    if market_score <= 45:  # 조정 중
        return {"score": 0.98, "chasing_risk": 1.1}
    return {"score": 1.0, "chasing_risk": 1.0}
