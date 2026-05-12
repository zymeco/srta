# 매매 전략 엔진: 매수가/목표가/손절가/손익비 산출

from typing import Dict, Any
from ..utils.number_utils import round1


def compute(
    basic: Dict[str, Any],
    technical: Dict[str, Any],
    risk: Dict[str, Any],
    position: Dict[str, Any],
) -> Dict[str, Any]:
    price = float(basic.get("current_price", 0) or 0)
    ma20 = float(technical.get("ma20") or price * 0.97)
    ma60 = float(technical.get("ma60") or price * 0.93)
    rsi = float(technical.get("rsi", 50))
    high_52w = float(basic.get("high_52w") or price * 1.2)

    # 매수 금지 종목은 가격 제시 X
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

    # 매수 구간: 20일선 근처 (~ 현재가 사이)
    buy_low = min(price, ma20)
    buy_high = max(buy_low * 1.01, price)
    buy_zone = f"{int(buy_low):,}~{int(buy_high):,}"

    # 손절가: 20일선 또는 60일선 하단 -3~6%
    base_stop = min(ma20, ma60) * 0.97 if rec in ("스윙", "중기") else price * 0.95
    if rec == "장기":
        base_stop = price * 0.90
    if rec == "단기" or rec == "초단기":
        base_stop = price * 0.97

    stop_loss = max(1, int(base_stop))

    # 목표가: 포지션별 다른 멀티
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

    # 추격매수 위험도
    if rsi > 75:
        chasing = "매우 높음"
    elif rsi > 68 or price >= high_52w * 0.97:
        chasing = "높음"
    elif rsi > 60:
        chasing = "중간"
    else:
        chasing = "낮음"

    # 전략 타입
    if rsi > 75:
        strategy_type = "관찰 (단기 과열로 추격매수 금지)"
    elif risk.get("risk_level", 0) == 2:
        strategy_type = "보류 (강한 주의 단계)"
    elif rr >= 2.0:
        strategy_type = "눌림목 분할매수"
    elif rr >= 1.5:
        strategy_type = "돌파 확인 후 매수"
    else:
        strategy_type = "관찰"

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
