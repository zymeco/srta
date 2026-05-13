# 종합 점수 엔진 (100점 만점)
#
# 가중치 계층:
#   1) 시가총액별 (대형주/중형주/소형주)
#   2) 섹터별 (성장/가치/사이클/방어)
#   3) 테마 보너스 (AI/반도체/2차전지/방산/원전 등)
#   4) 펀더멘털 강세 보너스 (저PER + 성장 + ROE)
#   5) 추세 강세 보너스 (이동평균 정배열 + 거래량 동반)

from typing import Dict, Any, List
from ..utils.number_utils import round1, clamp
from .sector_profile import get_category_weights, get_theme_bonus, is_growth_sector, is_value_sector


def _timing_score(technical: Dict[str, Any], volume: Dict[str, Any]) -> float:
    rsi = technical.get("rsi", 50)
    vol_ratio = volume.get("ratio", 1.0)
    score = 2.5
    if 40 <= rsi <= 60: score += 1.5
    elif rsi > 75: score -= 1.5
    if 1.0 <= vol_ratio <= 2.0: score += 1.0
    elif vol_ratio > 3.5: score -= 0.5
    return clamp(score, 0, 5)


def _fundamental_bonus(financial: Dict[str, Any], sector: str) -> float:
    """저평가 + 성장 결합 시 보너스. SK하이닉스(forward PER 7배) 같은 케이스 구제."""
    bonus = 0.0
    per = financial.get("per", 0) or 0
    forward_per = financial.get("forward_per", 0) or 0
    roe = financial.get("roe", 0) or 0
    op_growth = financial.get("operating_growth", 0) or 0
    rev_growth = financial.get("revenue_growth", 0) or 0
    op_margin = financial.get("operating_margin", 0) or 0
    div_yield = financial.get("dividend_yield", 0) or 0

    # 효과 PER: forward가 있으면 그것 사용 (시장이 매기는 미래 가치)
    effective_per = forward_per if 0 < forward_per < 50 else per

    # 저PER 강한 보너스
    if 0 < effective_per < 8:
        bonus += 4.5
    elif 0 < effective_per < 12:
        bonus += 3.0
    elif 0 < effective_per < 18:
        bonus += 1.5

    # 성장 + 저PER 결합 추가 보너스
    if 0 < effective_per < 15 and (rev_growth > 8 or op_growth > 12):
        bonus += 1.5

    # ROE 매우 높음 + 영업이익률 양호
    if roe > 18 and op_margin > 12:
        bonus += 1.5

    # 고배당 가치주 보너스 (가치 섹터)
    if div_yield > 4:
        bonus += 1.0

    return bonus


def _trend_strength_bonus(technical: Dict[str, Any], volume: Dict[str, Any]) -> float:
    """이동평균 정배열 + 거래량 동반 시 추세 보너스."""
    bonus = 0.0
    ma5 = technical.get("ma5", 0) or 0
    ma20 = technical.get("ma20", 0) or 0
    ma60 = technical.get("ma60", 0) or 0
    ma120 = technical.get("ma120", 0) or 0
    vol_ratio = volume.get("ratio", 1.0)

    if ma5 > ma20 > ma60 > ma120 and ma120 > 0:
        # 완전 정배열
        bonus += 1.5
        if vol_ratio >= 1.2:
            bonus += 1.0  # 거래량 동반
    return bonus


def compute(
    financial_a: Dict[str, Any],
    growth_a: Dict[str, Any],
    valuation_a: Dict[str, Any],
    technical_a: Dict[str, Any],
    volume_a: Dict[str, Any],
    supply_a: Dict[str, Any],
    news_a: Dict[str, Any],
    risk_a: Dict[str, Any],
    market_cap_type: str = "mid",
    sector: str = "",
    themes: List[str] = None,
    financial_raw: Dict[str, Any] = None,
) -> Dict[str, Any]:
    timing = _timing_score(technical_a, volume_a)

    scores = {
        "financial": float(financial_a.get("score", 0)),
        "growth": float(growth_a.get("score", 0)),
        "valuation": float(valuation_a.get("score", 0)),
        "technical": float(technical_a.get("score", 0)),
        "volume": float(volume_a.get("score", 0)),
        "supply": float(supply_a.get("score", 0)),
        "news_theme": float(news_a.get("score", 0)),
        "risk": float(risk_a.get("score", 0)),
        "timing": float(timing),
    }

    # ---- 1) 시총별 가중치 ----
    cap_weights = {
        "large": {"financial": 1.15, "growth": 1.05, "valuation": 1.10, "technical": 0.95,
                  "volume": 0.90, "supply": 1.15, "news_theme": 0.90, "risk": 1.00, "timing": 1.00},
        "mid":   {"financial": 1.00, "growth": 1.05, "valuation": 1.00, "technical": 1.05,
                  "volume": 1.05, "supply": 1.05, "news_theme": 1.00, "risk": 1.00, "timing": 1.00},
        "small": {"financial": 0.90, "growth": 0.95, "valuation": 0.90, "technical": 1.10,
                  "volume": 1.20, "supply": 0.95, "news_theme": 1.15, "risk": 1.25, "timing": 1.05},
    }
    cw = cap_weights.get(market_cap_type, cap_weights["mid"])

    # ---- 2) 섹터별 가중치 ----
    sw = get_category_weights(sector)

    # 최종 가중치 = 시총 × 섹터
    combined = {k: cw[k] * sw.get(k, 1.0) for k in cw}

    base_max = {"financial": 15, "growth": 15, "valuation": 10, "technical": 15,
                "volume": 10, "supply": 10, "news_theme": 10, "risk": 10, "timing": 5}

    weighted_total = 0.0
    weighted_max = 0.0
    for k in scores:
        weighted_total += scores[k] * combined[k]
        weighted_max += base_max[k] * combined[k]

    total_100 = (weighted_total / weighted_max) * 100 if weighted_max > 0 else 0

    # ---- 3) 테마 보너스 ----
    theme_bonus = get_theme_bonus(themes or [])
    total_100 += theme_bonus

    # ---- 4) 펀더멘털 강세 보너스 ----
    fundamental_bonus = 0.0
    if financial_raw:
        fundamental_bonus = _fundamental_bonus(financial_raw, sector)
        total_100 += fundamental_bonus

    # ---- 5) 추세 강세 보너스 ----
    trend_bonus = _trend_strength_bonus(technical_a, volume_a)
    total_100 += trend_bonus

    total_100 = clamp(total_100, 0, 100)

    if total_100 >= 90: grade = "S"; opinion = "강력 관심"
    elif total_100 >= 80: grade = "A"; opinion = "관심매수"
    elif total_100 >= 70: grade = "B"; opinion = "관찰"
    elif total_100 >= 60: grade = "C"; opinion = "보류"
    else: grade = "D"; opinion = "제외"

    display_scores = {k: round1(scores[k]) for k in scores}

    return {
        "scores": display_scores,
        "total_score": round1(total_100),
        "grade": grade,
        "final_opinion": opinion,
        "bonus": {
            "theme": round1(theme_bonus),
            "fundamental": round1(fundamental_bonus),
            "trend": round1(trend_bonus),
        },
        "sector_category": "growth" if is_growth_sector(sector) else "value" if is_value_sector(sector) else "default",
    }
