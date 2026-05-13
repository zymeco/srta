# 투자 스타일별 점수 (각 100점 만점).
# 한 종목이 어떤 투자 스타일에 잘 맞는지 다각도로 평가.
#
# - Graham (가치투자): 저PER, 저PBR, 안정 배당, 안전마진, 부채 적음
# - Buffett (퀄리티): 높은 ROE, 안정 영업이익률, 낮은 부채, 일관된 성장
# - Lynch (성장가치): PEG < 1, 매출/이익 성장, 합리적 밸류에이션
# - Momentum (모멘텀): 추세, 신고가 근접, 거래량, RS

from typing import Dict, Any, List
from ..utils.number_utils import round1, clamp


def graham_score(financial: Dict[str, Any]) -> Dict[str, Any]:
    """벤저민 그레이엄 가치투자 점수."""
    per = financial.get("forward_per") or financial.get("per") or 0
    pbr = financial.get("pbr") or 0
    debt = financial.get("debt_ratio") or 100
    current = financial.get("current_ratio") or 100
    div = financial.get("dividend_yield") or 0
    op_margin = financial.get("operating_margin") or 0

    s = 0
    notes = []

    # PER < 15 (그레이엄 기준)
    if 0 < per < 10: s += 25; notes.append(f"PER {per} 매우 저평가")
    elif 0 < per < 15: s += 18; notes.append(f"PER {per} 저평가")
    elif 0 < per < 20: s += 10
    elif per > 30: notes.append("PER 고평가")

    # PBR < 1.5
    if 0 < pbr < 1: s += 25; notes.append(f"PBR {pbr} 순자산 미만")
    elif 0 < pbr < 1.5: s += 18
    elif 0 < pbr < 2.5: s += 10
    elif pbr > 4: notes.append("PBR 부담")

    # 부채비율
    if debt < 50: s += 15; notes.append("재무 매우 안정")
    elif debt < 100: s += 10
    elif debt < 150: s += 5
    elif debt > 250: notes.append("부채 과다")

    # 유동비율 ≥ 200% (그레이엄 기준)
    if current >= 200: s += 10
    elif current >= 150: s += 5

    # 배당
    if div > 4: s += 15; notes.append(f"배당수익률 {div}%")
    elif div > 2: s += 10
    elif div > 0: s += 3

    # 흑자
    if op_margin > 5: s += 10

    return {"score": round1(clamp(s, 0, 100)), "reasons": notes}


def buffett_score(financial: Dict[str, Any]) -> Dict[str, Any]:
    """워런 버핏 퀄리티 투자 점수."""
    roe = financial.get("roe") or 0
    op_margin = financial.get("operating_margin") or 0
    debt = financial.get("debt_ratio") or 100
    ocf = financial.get("operating_cash_flow") or 0
    rev_growth = financial.get("revenue_growth") or 0
    op_growth = financial.get("operating_growth") or 0
    per = financial.get("forward_per") or financial.get("per") or 0

    s = 0
    notes = []

    # ROE 지속적 15%+ (해자 지표)
    if roe >= 20: s += 30; notes.append(f"ROE {roe}% 매우 우수")
    elif roe >= 15: s += 22; notes.append(f"ROE {roe}% 양호")
    elif roe >= 10: s += 12
    elif roe < 0: notes.append("ROE 마이너스")

    # 영업이익률
    if op_margin > 20: s += 22; notes.append("높은 영업이익률")
    elif op_margin > 12: s += 15
    elif op_margin > 6: s += 8
    elif op_margin < 0: notes.append("영업적자")

    # 부채비율 — 보수적
    if debt < 50: s += 15
    elif debt < 100: s += 10
    elif debt > 200: s -= 5

    # 영업 현금흐름 양수
    if ocf > 0: s += 10

    # 성장 일관성
    if rev_growth > 8 and op_growth > 8: s += 13; notes.append("매출·이익 동반 성장")
    elif rev_growth > 5: s += 6

    # 합리적 가격 (PER 25 미만)
    if 0 < per < 25: s += 10
    elif per > 40: s -= 5

    return {"score": round1(clamp(s, 0, 100)), "reasons": notes}


def lynch_score(financial: Dict[str, Any], advanced: Dict[str, Any]) -> Dict[str, Any]:
    """피터 린치 PEG 기반 성장가치 점수."""
    peg = advanced.get("peg") or 0
    rev_growth = financial.get("revenue_growth") or 0
    op_growth = financial.get("operating_growth") or 0
    roe = financial.get("roe") or 0
    per = financial.get("forward_per") or financial.get("per") or 0

    s = 0
    notes = []

    # PEG (린치의 핵심): < 1 이면 GARP (Growth At Reasonable Price)
    if 0 < peg < 0.5: s += 35; notes.append(f"PEG {peg} GARP 종목")
    elif 0 < peg < 1: s += 28; notes.append(f"PEG {peg} 저평가 성장")
    elif 0 < peg < 1.5: s += 18
    elif peg > 3: notes.append(f"PEG {peg} 부담")
    elif peg == 0 and per > 0 and 0 < op_growth < 15:
        # PEG 계산 불가 케이스 보조 평가
        s += 5

    # 성장률
    if rev_growth > 20: s += 25; notes.append(f"매출 +{rev_growth}%")
    elif rev_growth > 10: s += 18
    elif rev_growth > 5: s += 10
    elif rev_growth < -5: notes.append("매출 역성장")

    if op_growth > 25: s += 20; notes.append(f"영업이익 +{op_growth}%")
    elif op_growth > 10: s += 12
    elif op_growth > 0: s += 5

    # ROE
    if roe > 15: s += 12
    elif roe > 10: s += 6

    # 저PER 보너스
    if 0 < per < 12: s += 8

    return {"score": round1(clamp(s, 0, 100)), "reasons": notes}


def momentum_score(financial: Dict[str, Any], technical: Dict[str, Any], volume: Dict[str, Any],
                   advanced: Dict[str, Any], supply: Dict[str, Any]) -> Dict[str, Any]:
    """모멘텀(추세 추종) 점수."""
    rsi = technical.get("rsi") or 50
    ma5 = technical.get("ma5") or 0
    ma20 = technical.get("ma20") or 0
    ma60 = technical.get("ma60") or 0
    vol_ratio = volume.get("ratio") or 1.0
    near_high = advanced.get("near_high_pct") or 0
    mom20 = advanced.get("momentum_20d") or 0
    mom60 = advanced.get("momentum_60d") or 0
    obv = advanced.get("obv_trend", "횡보")
    foreign_5d = supply.get("foreign_5d") or 0

    s = 0
    notes = []

    # 정배열
    if ma5 > ma20 > ma60 > 0: s += 25; notes.append("이동평균 정배열")
    elif ma5 > ma20 > 0: s += 15
    elif ma5 < ma20 < ma60: s -= 10; notes.append("역배열")

    # 모멘텀
    if mom20 > 10: s += 15; notes.append(f"20일 +{mom20}%")
    elif mom20 > 3: s += 8
    elif mom20 < -10: s -= 10

    if mom60 > 20: s += 12; notes.append(f"60일 +{mom60}%")
    elif mom60 > 5: s += 6

    # 신고가 근접
    if near_high >= 95: s += 18; notes.append(f"신고가 {near_high}% 근접")
    elif near_high >= 85: s += 10
    elif near_high < 60: s -= 5

    # 거래량 동반
    if vol_ratio >= 1.5: s += 10; notes.append("거래량 급증")
    elif vol_ratio >= 1.2: s += 5

    # OBV
    if obv == "상승": s += 8; notes.append("OBV 상승")
    elif obv == "하락": s -= 5

    # RSI (40~70 권장 구간)
    if 40 <= rsi <= 70: s += 8
    elif rsi > 80: s -= 5; notes.append("RSI 과열")

    # 외국인 매수 동반
    if foreign_5d > 0: s += 5

    return {"score": round1(clamp(s, 0, 100)), "reasons": notes}


def compute_all_styles(financial, technical, volume, advanced, supply) -> Dict[str, Any]:
    styles = {
        "graham": graham_score(financial),
        "buffett": buffett_score(financial),
        "lynch": lynch_score(financial, advanced),
        "momentum": momentum_score(financial, technical, volume, advanced, supply),
    }
    # 최고 적합 스타일
    best = max(styles.items(), key=lambda kv: kv[1]["score"])
    style_label = {
        "graham": "그레이엄 가치투자",
        "buffett": "버핏 퀄리티",
        "lynch": "린치 성장가치",
        "momentum": "모멘텀 추종",
    }
    return {
        "styles": styles,
        "best_style": best[0],
        "best_style_label": style_label.get(best[0], best[0]),
        "best_style_score": best[1]["score"],
    }
