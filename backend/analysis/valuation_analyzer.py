# 밸류에이션 분석 (배점 10점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(financial: Dict[str, Any]) -> Dict[str, Any]:
    score = 5.0
    reasons, warnings = [], []

    per = financial.get("per", 15)
    pbr = financial.get("pbr", 1.5)
    psr = financial.get("psr", 1.0)
    ev = financial.get("ev_ebitda", 10)
    sec_per = financial.get("sector_per", 15)
    roe = financial.get("roe", 0)

    if per is None or per <= 0:
        warnings.append("PER이 마이너스(적자)입니다.")
        score -= 2
    else:
        if per < sec_per * 0.7:
            score += 2.0
            reasons.append(f"PER {per}로 업종 평균({sec_per}) 대비 저평가 구간입니다.")
        elif per < sec_per * 1.2:
            score += 1.0
        elif per > sec_per * 2:
            score -= 2.0
            warnings.append(f"PER {per}로 업종 평균 대비 매우 고평가 상태입니다.")

    if pbr < 1.0: score += 1.5; reasons.append(f"PBR {pbr}로 순자산 가치 대비 저평가입니다.")
    elif pbr > 4: score -= 1.5; warnings.append(f"PBR {pbr}로 자산 대비 부담스러운 수준입니다.")

    if psr < 1: score += 0.5
    elif psr > 5: score -= 1

    if ev < 8: score += 1
    elif ev > 20: score -= 1

    if per and per > 0 and roe > 0:
        if roe / per > 1.5:
            score += 1.0
            reasons.append("ROE 대비 PER 효율이 좋습니다.")

    score = clamp(score, 0, 10)
    label = "저평가" if score >= 7 else ("적정" if score >= 4 else "고평가")
    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
    }
