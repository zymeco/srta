# 거래량 분석 (배점 10점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(price_data: Dict[str, Any], basic: Dict[str, Any]) -> Dict[str, Any]:
    score = 5.0
    reasons, warnings = [], []

    volumes = [v.get("volume", 0) for v in price_data.get("volumes", [])]
    today_vol = basic.get("volume", 0)
    if not volumes:
        return {"score": 5.0, "label": "보통", "reasons": [], "warnings": [], "avg_20d": 0, "ratio": 1.0}

    avg_20 = sum(volumes[-20:]) / max(1, len(volumes[-20:]))
    ratio = today_vol / avg_20 if avg_20 > 0 else 1.0

    if ratio >= 3.0:
        score += 3.0
        reasons.append(f"거래량이 20일 평균 대비 {round(ratio*100)}%로 급증하고 있습니다.")
    elif ratio >= 1.8:
        score += 2.0
        reasons.append(f"거래량이 평균 대비 {round(ratio*100)}% 증가했습니다.")
    elif ratio >= 1.2:
        score += 1.0
    elif ratio < 0.5:
        score -= 2.5
        warnings.append("거래량이 평균 대비 크게 감소했습니다. 관심도 저하 상태입니다.")
    elif ratio < 0.8:
        score -= 1.0

    # 단기 급등 + 거래량 감소 패턴
    closes_dates = price_data.get("prices", [])
    if len(closes_dates) >= 6:
        recent_change = (closes_dates[-1]["close"] - closes_dates[-6]["close"]) / max(1, closes_dates[-6]["close"]) * 100
        recent_vol_ratio = (sum(volumes[-3:]) / 3) / max(1, sum(volumes[-10:-3]) / 7)
        if recent_change > 20 and recent_vol_ratio < 0.7:
            score -= 2.0
            warnings.append("단기 급등 후 거래량 감소 패턴이 관찰됩니다.")

    score = clamp(score, 0, 10)
    label = "활발" if score >= 7 else ("보통" if score >= 4 else "한산")

    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
        "avg_20d": int(avg_20),
        "ratio": round1(ratio),
    }
