# 투자 포지션 판단 엔진.
# 단기/스윙/중기/장기/초단기 각각 적합도를 100점 만점으로 계산한다.

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


def analyze(
    basic: Dict[str, Any],
    technical: Dict[str, Any],
    volume: Dict[str, Any],
    supply: Dict[str, Any],
    financial: Dict[str, Any],
    news: Dict[str, Any],
    risk: Dict[str, Any],
) -> Dict[str, Any]:
    rsi = technical.get("rsi", 50)
    vol_ratio = volume.get("ratio", 1.0)
    ma20 = technical.get("ma20", 0)
    ma60 = technical.get("ma60", 0)
    ma120 = technical.get("ma120", 0)
    price = basic.get("current_price", 0)

    debt = financial.get("debt_ratio", 100)
    roe = financial.get("roe", 0)
    rev_growth = financial.get("revenue_growth", 0)
    op_growth = financial.get("operating_growth", 0)

    # 초단기/데이트레이딩 (변동성, 거래량 폭증, 뉴스)
    day_trading = 40.0
    if vol_ratio >= 3: day_trading += 25
    elif vol_ratio >= 2: day_trading += 15
    elif vol_ratio < 1: day_trading -= 15
    if rsi > 70: day_trading += 10
    if abs(basic.get("change_rate", 0)) > 5: day_trading += 10
    if news.get("themes"): day_trading += 5

    # 단기 (1~5일 모멘텀)
    short_term = 45.0
    if price > ma20: short_term += 15
    if 40 <= rsi <= 65: short_term += 10
    elif rsi > 75: short_term -= 10
    if vol_ratio >= 1.5: short_term += 10
    if supply.get("foreign_5d", 0) > 0: short_term += 5
    if technical.get("score", 0) >= 11: short_term += 8

    # 스윙 (1~4주)
    swing = 50.0
    if price > ma20 and ma20 > ma60: swing += 18
    if 35 <= rsi <= 65: swing += 10
    if vol_ratio >= 1.2: swing += 7
    if supply.get("foreign_20d", 0) > 0 or supply.get("institution_20d", 0) > 0: swing += 8
    if rev_growth > 5: swing += 5
    if news.get("score", 0) >= 6: swing += 5
    if rsi > 78: swing -= 12

    # 중기 (1~6개월)
    mid_term = 45.0
    if ma60 and ma120 and ma60 > ma120: mid_term += 15
    if op_growth > 5: mid_term += 10
    if roe > 8: mid_term += 10
    if debt < 150: mid_term += 5
    if supply.get("institution_20d", 0) > 0: mid_term += 7
    if rev_growth > 10: mid_term += 8

    # 장기 (6개월+)
    long_term = 40.0
    if debt < 100: long_term += 12
    if roe > 10: long_term += 12
    if financial.get("operating_cash_flow", 0) > 0: long_term += 8
    if op_growth > 3: long_term += 8
    if financial.get("operating_margin", 0) > 10: long_term += 8
    if basic.get("market_cap_type") == "large": long_term += 5
    if financial.get("three_year_loss"): long_term -= 25

    # 리스크 페널티
    if risk.get("risk_level", 0) >= 2:
        for k in ("day_trading", "short_term", "swing", "mid_term", "long_term"):
            pass  # 아래서 한 번에
    risk_penalty = risk.get("risk_level", 0) * 10
    day_trading -= risk_penalty
    short_term -= risk_penalty
    swing -= risk_penalty
    mid_term -= risk_penalty * 1.2
    long_term -= risk_penalty * 1.5

    scores = {
        "day_trading": round1(clamp(day_trading, 0, 100)),
        "short_term": round1(clamp(short_term, 0, 100)),
        "swing": round1(clamp(swing, 0, 100)),
        "mid_term": round1(clamp(mid_term, 0, 100)),
        "long_term": round1(clamp(long_term, 0, 100)),
    }

    # 추천 포지션
    name_map = {
        "day_trading": "초단기",
        "short_term": "단기",
        "swing": "스윙",
        "mid_term": "중기",
        "long_term": "장기",
    }
    period_map = {
        "day_trading": "당일~익일",
        "short_term": "1일~5거래일",
        "swing": "1주~4주",
        "mid_term": "1개월~6개월",
        "long_term": "6개월 이상",
    }

    if risk.get("is_buy_forbidden"):
        recommended = "접근 금지"
        period = "해당 없음"
        entry_status = "신규 진입 금지"
        best_strategy = "관찰만 가능하며 리스크 해소 전 접근하지 않는 것이 유리합니다."
    else:
        best_key = max(scores, key=scores.get)
        recommended = name_map[best_key]
        period = period_map[best_key]
        entry_status = _entry_status(best_key, technical, volume)
        best_strategy = _best_strategy(best_key, technical, volume)

    reason = _build_reason(scores, technical, volume, supply, financial, risk)

    return {
        "recommended_position": recommended,
        "expected_holding_period": period,
        "current_entry_status": entry_status,
        "best_profit_strategy": best_strategy,
        "position_scores": scores,
        "reason": reason,
    }


def _entry_status(key, technical, volume):
    rsi = technical.get("rsi", 50)
    if rsi > 75:
        return "단기 과열, 추격매수 금지"
    if rsi < 35:
        return "과매도 반등 가능 구간"
    if volume.get("ratio", 1.0) >= 2.0:
        return "거래량 동반 상승 진행 중"
    if key in ("swing", "mid_term"):
        return "눌림목 대기"
    return "관찰 가능"


def _best_strategy(key, technical, volume):
    if key == "day_trading":
        return "변동성 활용 빠른 매매. 손절가 엄격 적용."
    if key == "short_term":
        return "5일선 지지 시 진입, 단기 저항선에서 분할 익절."
    if key == "swing":
        return "20일선 눌림목에서 분할매수 후 전고점 돌파 시 일부 익절."
    if key == "mid_term":
        return "60일선 추세 유지 시 분할매수, 실적 발표 기준으로 비중 조절."
    if key == "long_term":
        return "분기 실적 확인하며 적립식 분할매수, 6개월 이상 보유."
    return "관찰"


def _build_reason(scores, technical, volume, supply, financial, risk):
    out = []
    if risk.get("is_buy_forbidden"):
        out.append("리스크 필터에서 치명적 위험이 감지되어 신규 매수가 불가합니다.")
        for t in risk.get("triggered_critical", []) + risk.get("triggered_strong", []):
            out.append(f"리스크: {t}")
        return out

    best_key = max(scores, key=scores.get)
    rsi = technical.get("rsi", 50)
    if best_key == "swing":
        out.append("20일선 위 추세를 유지하며 단기 과열은 크지 않습니다.")
    if best_key == "long_term":
        out.append(f"ROE {financial.get('roe', 0)}%와 영업이익률 {financial.get('operating_margin', 0)}%로 장기 보유 적합 종목입니다.")
    if supply.get("foreign_20d", 0) > 0:
        out.append("외국인 20일 누적 순매수 유입 중입니다.")
    if supply.get("institution_20d", 0) > 0:
        out.append("기관 20일 누적 순매수 유입 중입니다.")
    if volume.get("ratio", 1.0) >= 1.3:
        out.append(f"거래량이 평균 대비 {round(volume.get('ratio',1)*100)}% 수준으로 활발합니다.")
    if rsi > 70:
        out.append(f"RSI {rsi}로 단기 과열 가능성이 있어 추격매수는 권하지 않습니다.")
    return out or ["분석 데이터 기반 일반적인 판단입니다."]
