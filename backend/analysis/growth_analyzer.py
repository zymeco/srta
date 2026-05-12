# 실적 성장성 분석 (배점 15점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(financial: Dict[str, Any]) -> Dict[str, Any]:
    score = 7.5
    reasons, warnings = [], []

    rev = financial.get("revenue_growth", 0)
    op = financial.get("operating_growth", 0)
    net = financial.get("net_income_growth", 0)
    margin = financial.get("operating_margin", 0)
    roe = financial.get("roe", 0)
    eps = financial.get("eps_growth", 0)

    if rev > 20: score += 2.5; reasons.append(f"매출 성장률 {rev}%로 매우 높습니다.")
    elif rev > 8: score += 1.5; reasons.append(f"매출 성장률 {rev}%로 양호합니다.")
    elif rev < -5: score -= 2; warnings.append(f"매출이 {rev}%로 역성장하고 있습니다.")

    if op > 20: score += 2.5; reasons.append(f"영업이익 {op}% 증가했습니다.")
    elif op > 5: score += 1.0
    elif op < -10: score -= 2.5; warnings.append(f"영업이익이 {op}%로 크게 감소했습니다.")

    if net > 0: score += 1.0
    elif net < -20: score -= 1.5; warnings.append("순이익이 크게 감소했습니다.")

    if margin > 15: score += 1.5; reasons.append(f"영업이익률 {margin}%로 수익성이 우수합니다.")
    elif margin < 0: score -= 2; warnings.append("영업이익률이 마이너스입니다.")

    if roe > 15: score += 1.5; reasons.append(f"ROE {roe}%로 자본 효율성이 높습니다.")
    elif roe < 0: score -= 1.5

    if eps > 20: score += 1.0
    elif eps < -20: score -= 1.0

    score = clamp(score, 0, 15)
    label = "양호" if score >= 11 else ("보통" if score >= 7 else "주의")
    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
    }
