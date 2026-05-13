# 백테스트 시뮬레이션.
# 과거 N일 전 매수 시 현재 수익률을 계산.

from typing import Dict, Any, List


def compute(price_data: Dict[str, Any]) -> Dict[str, Any]:
    prices = price_data.get("prices", []) or []
    if not prices or len(prices) < 5:
        return {"available": False}

    closes = [p["close"] for p in prices]
    cur = closes[-1]

    def back_n(n):
        if len(closes) <= n:
            return None
        base = closes[-n - 1]
        if not base:
            return None
        return round((cur - base) / base * 100, 2)

    points = {
        "1주 전":  back_n(5),
        "1개월 전": back_n(20),
        "3개월 전": back_n(60),
        "6개월 전": back_n(120),
        "1년 전":   back_n(min(252, len(closes) - 1)),
    }

    # 시계열 (그래프용)
    series = []
    base_idx = max(0, len(closes) - 252)
    base = closes[base_idx]
    for i in range(base_idx, len(closes)):
        if not base:
            continue
        pct = (closes[i] - base) / base * 100
        series.append({"date": prices[i]["date"], "return_pct": round(pct, 2)})

    return {
        "available": True,
        "current_price": cur,
        "returns": {k: v for k, v in points.items() if v is not None},
        "series": series,
    }
