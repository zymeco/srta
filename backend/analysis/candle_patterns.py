# 캔들 패턴 자동 인식.
# 최근 5일 OHLC로 주요 패턴 감지.

from typing import Dict, Any, List


def _body(o, c): return abs(c - o)
def _range(h, l): return max(0.001, h - l)
def _upper_shadow(o, h, c): return h - max(o, c)
def _lower_shadow(o, l, c): return min(o, c) - l


def detect_patterns(ohlcv: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """최근 5개 캔들에서 주요 패턴 감지."""
    if not ohlcv or len(ohlcv) < 3:
        return []

    patterns = []
    n = len(ohlcv)
    last = ohlcv[-1]
    prev = ohlcv[-2]

    o, h, l, c = last["open"], last["high"], last["low"], last["close"]
    po, ph, pl, pc = prev["open"], prev["high"], prev["low"], prev["close"]
    body = _body(o, c)
    rng = _range(h, l)
    upper = _upper_shadow(o, h, c)
    lower = _lower_shadow(o, l, c)

    # 도지 (Doji): 시가 ≈ 종가
    if rng > 0 and body / rng < 0.1:
        patterns.append({"name": "도지", "signal": "추세 전환 가능성", "type": "neutral"})

    # 망치형 (Hammer): 짧은 몸통 + 긴 아래꼬리 (하락 후)
    if body / rng < 0.35 and lower > body * 2 and upper < body:
        # 하락 추세 후
        if n >= 3 and ohlcv[-2]["close"] < ohlcv[-3]["close"]:
            patterns.append({"name": "망치형", "signal": "단기 반등 신호", "type": "bullish"})

    # 역망치 (Inverted Hammer): 짧은 몸통 + 긴 위꼬리 (하락 후)
    if body / rng < 0.35 and upper > body * 2 and lower < body:
        if n >= 3 and ohlcv[-2]["close"] < ohlcv[-3]["close"]:
            patterns.append({"name": "역망치형", "signal": "반등 시도", "type": "bullish"})

    # 잉걸이형 (Engulfing): 전일 캔들을 완전히 감쌈
    if c > o and pc < po and o < pc and c > po:
        patterns.append({"name": "상승 잉걸이", "signal": "강한 매수 신호", "type": "bullish"})
    if c < o and pc > po and o > pc and c < po:
        patterns.append({"name": "하락 잉걸이", "signal": "강한 매도 신호", "type": "bearish"})

    # 흑운형 (Dark Cloud Cover): 양봉 후 음봉이 중간 이상 침투
    if pc > po and c < o and o > pc and c < (po + pc) / 2:
        patterns.append({"name": "흑운형", "signal": "조정 신호", "type": "bearish"})

    # 관통형 (Piercing): 음봉 후 양봉이 중간 이상 침투
    if pc < po and c > o and o < pc and c > (po + pc) / 2:
        patterns.append({"name": "관통형", "signal": "반등 신호", "type": "bullish"})

    # 십자별 (Doji Star): 도지 + 시초가 갭
    if body / rng < 0.1 and n >= 3:
        prev_body = _body(po, pc)
        if prev_body > 0 and abs(o - pc) / pc > 0.005:
            patterns.append({"name": "십자별", "signal": "추세 반전 가능성", "type": "neutral"})

    # 마무리 캔들 (Marubozu): 꼬리 거의 없음
    if rng > 0 and body / rng > 0.9:
        if c > o:
            patterns.append({"name": "강한 양봉", "signal": "매수세 강함", "type": "bullish"})
        else:
            patterns.append({"name": "강한 음봉", "signal": "매도세 강함", "type": "bearish"})

    return patterns


def analyze(price_data: Dict[str, Any]) -> Dict[str, Any]:
    prices = price_data.get("prices", []) or []
    if not prices:
        return {"patterns": [], "signal": "정보 부족"}

    # OHLC 재구성
    ohlcv = []
    for p in prices[-10:]:
        ohlcv.append({
            "open":  p.get("open", p["close"]),
            "high":  p.get("high", p["close"]),
            "low":   p.get("low", p["close"]),
            "close": p["close"],
        })

    patterns = detect_patterns(ohlcv)
    bull = sum(1 for p in patterns if p["type"] == "bullish")
    bear = sum(1 for p in patterns if p["type"] == "bearish")
    if bull > bear:
        signal = "상승 신호"
    elif bear > bull:
        signal = "하락 신호"
    elif patterns:
        signal = "중립 / 추세 전환 가능"
    else:
        signal = "특별한 패턴 없음"

    return {"patterns": patterns, "signal": signal, "count": len(patterns)}
