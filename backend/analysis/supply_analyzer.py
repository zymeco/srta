# 수급 분석 (배점 10점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(supply: Dict[str, Any]) -> Dict[str, Any]:
    score = 5.0
    reasons, warnings = [], []

    f5 = supply.get("foreign_5d", 0)
    f20 = supply.get("foreign_20d", 0)
    i5 = supply.get("institution_5d", 0)
    i20 = supply.get("institution_20d", 0)

    if f5 > 0: score += 1.5; reasons.append("외국인 5일 순매수 유입 중입니다.")
    elif f5 < -500: score -= 1.5; warnings.append("외국인 5일 매도세가 강합니다.")
    if f20 > 0: score += 1.0
    elif f20 < -1500: score -= 1.0

    if i5 > 0: score += 1.5; reasons.append("기관 5일 순매수 유입 중입니다.")
    elif i5 < -400: score -= 1.5; warnings.append("기관 매도세가 강합니다.")
    if i20 > 0: score += 0.5

    short_ratio = supply.get("short_selling_ratio", 1.0)
    if short_ratio > 10:
        score -= 1.5
        warnings.append(f"공매도 비중 {short_ratio}%로 매우 높습니다.")
    elif short_ratio > 5:
        score -= 0.5

    credit = supply.get("credit_balance_ratio", 1.0)
    if credit > 8:
        score -= 1.5
        warnings.append(f"신용잔고 {credit}%로 과열 상태입니다.")
    elif credit > 5:
        score -= 0.5

    score = clamp(score, 0, 10)
    label = "우호적" if score >= 7 else ("중립" if score >= 4 else "비우호적")
    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
    }
