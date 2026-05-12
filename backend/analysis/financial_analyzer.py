# 재무 안정성 분석 (배점 15점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(financial: Dict[str, Any]) -> Dict[str, Any]:
    score = 15.0
    reasons, warnings = [], []

    debt = financial.get("debt_ratio", 100)
    if debt < 80:
        reasons.append(f"부채비율 {debt}%로 매우 안정적입니다.")
    elif debt < 150:
        reasons.append(f"부채비율 {debt}%로 양호합니다.")
        score -= 1.5
    elif debt < 250:
        warnings.append(f"부채비율 {debt}%로 다소 높습니다.")
        score -= 4
    else:
        warnings.append(f"부채비율 {debt}%로 매우 높아 재무 위험이 있습니다.")
        score -= 7

    cr = financial.get("current_ratio", 100)
    if cr < 80:
        warnings.append(f"유동비율 {cr}%로 단기 지급 능력이 부족합니다.")
        score -= 3
    elif cr < 120:
        score -= 1

    ocf = financial.get("operating_cash_flow", 0)
    if ocf < 0:
        warnings.append("영업현금흐름이 마이너스입니다.")
        score -= 3

    ic = financial.get("interest_coverage", 1.5)
    if ic < 1.5:
        warnings.append(f"이자보상배율 {ic}로 영업이익으로 이자 감당이 어렵습니다.")
        score -= 3

    if financial.get("capital_impairment"):
        warnings.append("자본잠식 상태입니다.")
        score -= 6
    if financial.get("three_year_loss"):
        warnings.append("3년 연속 적자 가능성이 있습니다.")
        score -= 3

    score = clamp(score, 0, 15)
    label = "양호" if score >= 11 else ("보통" if score >= 7 else "주의")
    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
    }
