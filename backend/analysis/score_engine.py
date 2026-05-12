# 종합 점수 엔진 (100점 만점)
#
# 시가총액별 가중치 적용:
#  - 대형주: 재무/실적/밸류/수급에 가중
#  - 중형주: 균형
#  - 소형주: 거래량/뉴스/리스크에 가중

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def _timing_score(technical: Dict[str, Any], volume: Dict[str, Any]) -> float:
    rsi = technical.get("rsi", 50)
    vol_ratio = volume.get("ratio", 1.0)
    score = 2.5
    if 40 <= rsi <= 60: score += 1.5
    elif rsi > 75: score -= 1.5
    if 1.0 <= vol_ratio <= 2.0: score += 1.0
    elif vol_ratio > 3.5: score -= 0.5
    return clamp(score, 0, 5)


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

    # 시총별 가중치
    weights = {
        "large": {"financial": 1.15, "growth": 1.05, "valuation": 1.1, "technical": 0.95,
                  "volume": 0.9, "supply": 1.15, "news_theme": 0.9, "risk": 1.0, "timing": 1.0},
        "mid":   {"financial": 1.0, "growth": 1.05, "valuation": 1.0, "technical": 1.05,
                  "volume": 1.05, "supply": 1.05, "news_theme": 1.0, "risk": 1.0, "timing": 1.0},
        "small": {"financial": 0.9, "growth": 0.95, "valuation": 0.9, "technical": 1.1,
                  "volume": 1.2, "supply": 0.95, "news_theme": 1.15, "risk": 1.25, "timing": 1.05},
    }
    w = weights.get(market_cap_type, weights["mid"])

    # 가중치 적용 후 다시 정상 배점으로 정규화
    base_max = {"financial": 15, "growth": 15, "valuation": 10, "technical": 15,
                "volume": 10, "supply": 10, "news_theme": 10, "risk": 10, "timing": 5}

    weighted_total = 0.0
    weighted_max = 0.0
    for k in scores:
        weighted_total += scores[k] * w[k]
        weighted_max += base_max[k] * w[k]

    total_100 = (weighted_total / weighted_max) * 100 if weighted_max > 0 else 0
    total_100 = clamp(total_100, 0, 100)

    if total_100 >= 90: grade = "S"; opinion = "강력 관심"
    elif total_100 >= 80: grade = "A"; opinion = "관심매수"
    elif total_100 >= 70: grade = "B"; opinion = "관찰"
    elif total_100 >= 60: grade = "C"; opinion = "보류"
    else: grade = "D"; opinion = "제외"

    # 표시용 raw 점수(15/15/10/...) - 합산 시 100점 만점이 되도록 그대로 노출
    display_scores = {k: round1(scores[k]) for k in scores}

    return {
        "scores": display_scores,
        "total_score": round1(total_100),
        "grade": grade,
        "final_opinion": opinion,
    }
