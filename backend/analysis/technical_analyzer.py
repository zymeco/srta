# 기술적 분석 (배점 15점)

from typing import Dict, Any
from ..utils.number_utils import round1, clamp
from ..utils.safe_calc import safe_last


def analyze(price_data: Dict[str, Any], current_price: float) -> Dict[str, Any]:
    score = 7.5
    reasons, warnings = [], []

    closes = [p["close"] for p in price_data.get("prices", [])]
    last = current_price or safe_last(closes, 0)
    ma5 = safe_last([v for v in price_data.get("ma5", []) if v is not None], last)
    ma20 = safe_last([v for v in price_data.get("ma20", []) if v is not None], last)
    ma60 = safe_last([v for v in price_data.get("ma60", []) if v is not None], last)
    ma120 = safe_last([v for v in price_data.get("ma120", []) if v is not None], last)
    rsi = safe_last([v for v in price_data.get("rsi", []) if v is not None], 50)
    bb_upper = safe_last([v for v in price_data.get("bb_upper", []) if v is not None], last * 1.1)
    bb_lower = safe_last([v for v in price_data.get("bb_lower", []) if v is not None], last * 0.9)

    # 추세 점수
    if last > ma5 > ma20 > ma60:
        score += 3.5
        reasons.append("정배열(5>20>60일선) 강한 상승 추세입니다.")
    elif last > ma20 > ma60:
        score += 2.0
        reasons.append("20일선 위 우상향 추세입니다.")
    elif last < ma20 < ma60:
        score -= 3.0
        warnings.append("역배열 하락 추세입니다.")
    elif last < ma20:
        score -= 1.5

    if last > ma120:
        score += 1.0
    else:
        score -= 1.0

    # RSI
    if 40 <= rsi <= 60:
        score += 1.0
        reasons.append(f"RSI {rsi}로 안정 구간입니다.")
    elif 60 < rsi <= 70:
        score += 0.5
    elif rsi > 75:
        score -= 2.0
        warnings.append(f"RSI {rsi}로 과열 구간입니다. 추격매수 주의가 필요합니다.")
    elif rsi < 30:
        score += 0.5
        reasons.append(f"RSI {rsi}로 과매도 구간입니다.")

    # 볼린저밴드
    if last > bb_upper:
        score -= 1.0
        warnings.append("볼린저밴드 상단을 돌파한 단기 과열 상태입니다.")
    elif last < bb_lower:
        score += 0.5
        reasons.append("볼린저밴드 하단 부근으로 기술적 반등 가능성이 있습니다.")

    # 신고가/신저가
    high_52w = price_data.get("high_52w", last)
    low_52w = price_data.get("low_52w", last)
    if high_52w and last >= high_52w * 0.98:
        reasons.append("52주 신고가 부근으로 모멘텀이 강합니다.")
        score += 0.5
    if low_52w and last <= low_52w * 1.05:
        warnings.append("52주 저점 부근으로 추세 약세 상태입니다.")
        score -= 1.0

    score = clamp(score, 0, 15)
    if score >= 11: label = "강세"
    elif score >= 7: label = "보통"
    else: label = "약세"

    return {
        "score": round1(score),
        "label": label,
        "reasons": reasons,
        "warnings": warnings,
        "ma5": round1(ma5),
        "ma20": round1(ma20),
        "ma60": round1(ma60),
        "ma120": round1(ma120),
        "rsi": round1(rsi),
        "bb_upper": round1(bb_upper),
        "bb_lower": round1(bb_lower),
        "support": round1(min(ma20, ma60)),
        "resistance": round1(max(high_52w, bb_upper)),
    }
