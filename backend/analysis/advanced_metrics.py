# 추가 기술적·통계적 지표 계산.
# - MDD (Maximum Drawdown)
# - ATR (Average True Range, 변동성)
# - OBV (On-Balance Volume, 누적 거래량)
# - 모멘텀 (n일 수익률)
# - 변동성 (표준편차)
# - 신고가 근접도
# - 베타는 시장 지수 데이터 필요 → 향후 확장

import math
from typing import Dict, Any, List


def compute_mdd(closes: List[float]) -> float:
    """최대 낙폭 (%)."""
    if not closes or len(closes) < 2:
        return 0.0
    peak = closes[0]
    max_dd = 0.0
    for c in closes:
        if c > peak:
            peak = c
        dd = (peak - c) / peak * 100 if peak else 0
        if dd > max_dd:
            max_dd = dd
    return round(max_dd, 2)


def compute_atr(ohlcv: List[Dict[str, Any]], period: int = 14) -> float:
    """평균 진폭 (ATR) — 변동성."""
    if not ohlcv or len(ohlcv) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(ohlcv)):
        h = ohlcv[i].get("high", 0) or 0
        l = ohlcv[i].get("low", 0) or 0
        pc = ohlcv[i - 1].get("close", 0) or 0
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    if len(trs) < period:
        return round(sum(trs) / len(trs), 2)
    atr = sum(trs[-period:]) / period
    return round(atr, 2)


def compute_obv_trend(ohlcv: List[Dict[str, Any]], lookback: int = 20) -> str:
    """OBV(On-Balance Volume) 추세."""
    if not ohlcv or len(ohlcv) < lookback + 1:
        return "정보부족"
    obv = 0
    series = [0]
    for i in range(1, len(ohlcv)):
        c = ohlcv[i].get("close", 0) or 0
        pc = ohlcv[i - 1].get("close", 0) or 0
        v = ohlcv[i].get("volume", 0) or 0
        if c > pc:
            obv += v
        elif c < pc:
            obv -= v
        series.append(obv)
    recent = series[-lookback:]
    if recent[-1] > recent[0] * 1.05:
        return "상승"
    if recent[-1] < recent[0] * 0.95:
        return "하락"
    return "횡보"


def compute_momentum(closes: List[float], days: int = 20) -> float:
    """n일 수익률 (%)."""
    if not closes or len(closes) <= days:
        return 0.0
    base = closes[-days - 1]
    cur = closes[-1]
    if not base:
        return 0.0
    return round((cur - base) / base * 100, 2)


def compute_volatility(closes: List[float], days: int = 20) -> float:
    """일별 수익률 표준편차 × √252 = 연환산 변동성 (%)."""
    if not closes or len(closes) < days + 1:
        return 0.0
    returns = []
    for i in range(1, len(closes)):
        if closes[i - 1]:
            returns.append((closes[i] - closes[i - 1]) / closes[i - 1])
    recent = returns[-days:]
    if len(recent) < 2:
        return 0.0
    mean = sum(recent) / len(recent)
    var = sum((r - mean) ** 2 for r in recent) / (len(recent) - 1)
    std = math.sqrt(var)
    return round(std * math.sqrt(252) * 100, 2)


def compute_near_high_pct(price: float, high_52w: float) -> float:
    """52주 고점 대비 현재가 비율 (%). 100이면 신고가."""
    if not high_52w:
        return 0.0
    return round(price / high_52w * 100, 1)


def compute_near_low_pct(price: float, low_52w: float) -> float:
    """52주 저점 대비 현재가가 몇 % 위에 있는지."""
    if not low_52w:
        return 0.0
    return round((price - low_52w) / low_52w * 100, 1)


def compute_peg(per: float, eps_growth: float) -> float:
    """PEG 비율 (린치 스타일). 1 미만이면 저평가 성장주."""
    if per is None or per <= 0 or not eps_growth:
        return 0.0
    if eps_growth <= 0:
        return 0.0  # 적자/역성장 종목은 PEG 의미 없음
    return round(per / eps_growth, 2)


def compute_advanced(price_data: Dict[str, Any], basic: Dict[str, Any], financial: Dict[str, Any]) -> Dict[str, Any]:
    """모든 고급 지표 한 번에."""
    prices = price_data.get("prices", []) or []
    closes = [p["close"] for p in prices]

    # OHLCV 구조 재구성 (price + volume 결합)
    volumes = price_data.get("volumes", []) or []
    ohlcv = []
    for i, p in enumerate(prices):
        v = volumes[i]["volume"] if i < len(volumes) else 0
        ohlcv.append({
            "close": p["close"], "high": p["close"], "low": p["close"], "volume": v
        })

    cur_price = float(basic.get("current_price", 0) or 0)
    high_52w = float(basic.get("high_52w", 0) or 0)
    low_52w = float(basic.get("low_52w", 0) or 0)

    per = financial.get("forward_per") or financial.get("per") or 0
    eps_growth = financial.get("eps_growth") or financial.get("operating_growth") or 0

    return {
        "mdd": compute_mdd(closes),
        "atr": compute_atr(ohlcv, 14),
        "obv_trend": compute_obv_trend(ohlcv, 20),
        "momentum_20d": compute_momentum(closes, 20),
        "momentum_60d": compute_momentum(closes, 60),
        "volatility_20d": compute_volatility(closes, 20),
        "near_high_pct": compute_near_high_pct(cur_price, high_52w),
        "near_low_pct": compute_near_low_pct(cur_price, low_52w),
        "peg": compute_peg(per, eps_growth),
    }
