# 뉴스/공시/테마 분석 (배점 10점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(news: Dict[str, Any]) -> Dict[str, Any]:
    score = 5.0
    reasons, warnings = [], []

    sc = news.get("sentiment_counts", {"positive": 0, "neutral": 0, "negative": 0})
    pos = sc.get("positive", 0)
    neg = sc.get("negative", 0)
    total = max(1, pos + neg + sc.get("neutral", 0))

    if pos > neg * 2:
        score += 2.5
        reasons.append(f"긍정 뉴스 비중 {pos}/{total}로 분위기가 양호합니다.")
    elif pos > neg:
        score += 1.0
    elif neg > pos * 2:
        score -= 2.5
        warnings.append(f"부정 뉴스 비중 {neg}/{total}로 분위기가 좋지 않습니다.")
    elif neg > pos:
        score -= 1.0

    if news.get("policy_benefit"):
        score += 1.5
        reasons.append("정부 정책 수혜 가능성이 있습니다.")

    if news.get("disclosure_risk"):
        score -= 1.5
        warnings.append("공시 관련 위험 요인이 존재합니다.")
    if news.get("rights_issue"):
        score -= 2.0
        warnings.append("유상증자 이슈가 있어 주가에 부담입니다.")
    if news.get("convertible_bond"):
        score -= 1.5
        warnings.append("전환사채 발행으로 물량 부담이 있습니다.")
    if news.get("warrant"):
        score -= 1.0
        warnings.append("신주인수권 관련 물량 부담이 존재합니다.")
    if news.get("largest_shareholder_change"):
        score -= 1.0
        warnings.append("최대주주 변경 이력이 있어 주의가 필요합니다.")

    themes = news.get("themes", [])
    if themes:
        reasons.append(f"관련 테마: {', '.join(themes)}")

    score = clamp(score, 0, 10)
    label = "긍정" if score >= 7 else ("중립" if score >= 4 else "부정")
    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
        "themes": themes,
    }
