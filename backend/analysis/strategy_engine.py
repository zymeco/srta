# 매매 전략 엔진: 매수가/목표가/손절가/손익비/추격매수 위험도
#
# 핵심 개선: 추격매수 위험도 산출 시 펀더멘털을 반영한다.
#   - PER 매우 낮음(저평가) + 매출/영업이익 성장 + 추세 상승 → 단기 RSI 과열이라도 위험 완화
#   - PER 매우 높음 + 적자 + 단기 급등 → 정말 위험

from typing import Dict, Any
from ..utils.number_utils import round1
from .sector_profile import is_growth_sector


def _chasing_risk(
    rsi: float,
    price: float,
    high_52w: float,
    financial: Dict[str, Any],
    sector: str,
) -> str:
    """추격매수 위험도 — 펀더멘털 종합 판단."""
    per = financial.get("per") or 0
    forward_per = financial.get("forward_per") or 0
    op_margin = financial.get("operating_margin") or 0
    rev_growth = financial.get("revenue_growth") or 0
    op_growth = financial.get("operating_growth") or 0

    # 효과 PER (forward 우선)
    eff_per = forward_per if 0 < forward_per < 50 else per

    # 펀더멘털 점수 (0~10)
    fund_score = 0
    if 0 < eff_per < 8:
        fund_score += 5   # 매우 저평가
    elif 0 < eff_per < 12:
        fund_score += 3
    elif 0 < eff_per < 18:
        fund_score += 1
    elif eff_per > 35:
        fund_score -= 2   # 매우 고평가
    elif eff_per <= 0:
        fund_score -= 2   # 적자

    if rev_growth > 15: fund_score += 2
    elif rev_growth > 5: fund_score += 1
    elif rev_growth < -5: fund_score -= 2

    if op_growth > 15: fund_score += 2
    elif op_growth < -10: fund_score -= 2

    if op_margin > 15: fund_score += 1
    elif op_margin < 0: fund_score -= 2

    # 가격 위치 (52주 고점 대비)
    near_high = high_52w and price >= high_52w * 0.97

    # 기본 위험도 (RSI 기반)
    if rsi > 80:
        base = "매우 높음"
    elif rsi > 73:
        base = "높음"
    elif rsi > 65:
        base = "중간"
    elif rsi > 50:
        base = "낮음"
    else:
        base = "낮음"

    # 펀더멘털이 강하면 한 단계 완화
    levels = ["낮음", "중간", "높음", "매우 높음"]
    cur_idx = levels.index(base)

    if fund_score >= 6:
        # 강력 저평가 + 성장 → 두 단계 완화
        cur_idx = max(0, cur_idx - 2)
    elif fund_score >= 3:
        # 양호한 펀더멘털 → 한 단계 완화
        cur_idx = max(0, cur_idx - 1)
    elif fund_score <= -3:
        # 펀더멘털 약함 + 단기 급등 → 한 단계 강화
        cur_idx = min(len(levels) - 1, cur_idx + 1)

    # 52주 신고가 부근이면 한 단계 강화 (단, 펀더멘털 매우 좋으면 유지)
    if near_high and fund_score < 6:
        cur_idx = min(len(levels) - 1, cur_idx + 1)

    return levels[cur_idx]


def compute(
    basic: Dict[str, Any],
    technical: Dict[str, Any],
    risk: Dict[str, Any],
    position: Dict[str, Any],
    financial: Dict[str, Any] = None,
) -> Dict[str, Any]:
    price = float(basic.get("current_price", 0) or 0)
    ma20 = float(technical.get("ma20") or price * 0.97)
    ma60 = float(technical.get("ma60") or price * 0.93)
    rsi = float(technical.get("rsi", 50))
    high_52w = float(basic.get("high_52w") or price * 1.2)
    sector = basic.get("sector", "")
    fin = financial or {}

    if risk.get("is_buy_forbidden"):
        return {
            "buy_zone": "제시하지 않음",
            "target_price_1": None,
            "target_price_2": None,
            "stop_loss": "보유자 기준 위험 관리 필요",
            "risk_reward_ratio": None,
            "target_return_rate": None,
            "stop_loss_rate": None,
            "strategy_type": "신규 매수 금지",
            "chasing_risk": "매우 높음",
        }

    rec = position.get("recommended_position", "스윙")

    buy_low = min(price, ma20)
    buy_high = max(buy_low * 1.01, price)
    buy_zone = f"{int(buy_low):,}~{int(buy_high):,}"

    base_stop = min(ma20, ma60) * 0.97 if rec in ("스윙", "중기") else price * 0.95
    if rec == "장기":
        base_stop = price * 0.90
    if rec in ("단기", "초단기"):
        base_stop = price * 0.97
    stop_loss = max(1, int(base_stop))

    multi_1 = {"초단기": 1.04, "단기": 1.07, "스윙": 1.12, "중기": 1.20, "장기": 1.35}
    multi_2 = {"초단기": 1.07, "단기": 1.13, "스윙": 1.20, "중기": 1.35, "장기": 1.60}
    m1 = multi_1.get(rec, 1.12)
    m2 = multi_2.get(rec, 1.20)
    target1 = int(max(price * m1, high_52w * 0.98))
    target2 = int(max(price * m2, high_52w * 1.05))

    target_return_rate = round1((target1 - price) / price * 100) if price else 0
    stop_loss_rate = round1((stop_loss - price) / price * 100) if price else 0

    if price > 0 and stop_loss < price:
        rr = (target1 - price) / max(1, (price - stop_loss))
    else:
        rr = 0
    rr = round1(rr)

    # 펀더멘털 반영한 추격매수 위험도
    chasing = _chasing_risk(rsi, price, high_52w, fin, sector)

    # 전략 타입 결정 — 펀더멘털 좋으면 단기 과열이라도 "분할매수" 또는 "눌림목"
    per = fin.get("per") or 0
    forward_per = fin.get("forward_per") or 0
    eff_per = forward_per if 0 < forward_per < 50 else per
    rev_growth = fin.get("revenue_growth") or 0
    op_growth = fin.get("operating_growth") or 0
    strong_fundamental = (0 < eff_per < 12)

    if risk.get("risk_level", 0) == 2:
        strategy_type = "보류 (강한 주의 단계)"
    elif chasing == "매우 높음":
        strategy_type = "관찰 (단기 과열)"
    elif chasing == "높음":
        if strong_fundamental:
            strategy_type = "눌림목 분할매수 (펀더멘털 양호)"
        else:
            strategy_type = "돌파 확인 후 매수"
    elif rr >= 2.0:
        strategy_type = "눌림목 분할매수"
    elif rr >= 1.5:
        strategy_type = "돌파 확인 후 매수"
    else:
        strategy_type = "관찰"

    # 성장 섹터 + 강한 펀더멘털 + 추세 상승 시 강한 매수 시그널
    if (
        is_growth_sector(sector)
        and strong_fundamental
        and rsi < 78
        and price > ma20
    ):
        strategy_type = "관심매수 (섹터 모멘텀 + 저평가)"

    return {
        "buy_zone": buy_zone,
        "target_price_1": target1,
        "target_price_2": target2,
        "stop_loss": stop_loss,
        "risk_reward_ratio": rr,
        "target_return_rate": target_return_rate,
        "stop_loss_rate": stop_loss_rate,
        "strategy_type": strategy_type,
        "chasing_risk": chasing,
    }
