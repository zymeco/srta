# 실적 발표 캘린더 — 다음 분기 발표 예정일 추정.
# Yahoo Finance에서 받을 수 있지만 한국 종목은 정확도 떨어짐 → 단순 분기 패턴 추정.

from datetime import datetime
from typing import Dict, Any


def estimate_next_earnings() -> Dict[str, Any]:
    """한국 상장사 일반 분기 실적 발표 패턴.
       Q1: 4월 말~5월 중, Q2: 7월 말~8월, Q3: 10월 말~11월, Q4: 2월 중순"""
    now = datetime.now()
    y, m = now.year, now.month

    # 다음 분기 마감 후 예상 발표 시즌
    if m <= 2:
        # 작년 Q4 실적 발표 (~2월 말)
        return {"period": f"{y-1} Q4", "expected_window": f"{y}-02-01 ~ {y}-02-28"}
    if m <= 5:
        return {"period": f"{y} Q1", "expected_window": f"{y}-04-15 ~ {y}-05-15"}
    if m <= 8:
        return {"period": f"{y} Q2", "expected_window": f"{y}-07-25 ~ {y}-08-20"}
    if m <= 11:
        return {"period": f"{y} Q3", "expected_window": f"{y}-10-25 ~ {y}-11-20"}
    # Dec
    return {"period": f"{y+1} Q4", "expected_window": f"{y+1}-02-01 ~ {y+1}-02-28"}


def days_until_earnings() -> int:
    """발표 예상까지 남은 일수 (대략)."""
    e = estimate_next_earnings()
    try:
        end = datetime.strptime(e["expected_window"].split(" ~ ")[1], "%Y-%m-%d")
        return max(0, (end - datetime.now()).days)
    except Exception:
        return -1


def get_earnings_info(stock_code: str) -> Dict[str, Any]:
    e = estimate_next_earnings()
    days = days_until_earnings()
    is_imminent = 0 <= days <= 7
    is_soon = 0 <= days <= 21
    note = ""
    if is_imminent:
        note = f"⚠ 실적 발표 임박 (D-{days}) — 변동성 주의"
    elif is_soon:
        note = f"실적 발표 예정 (D-{days})"
    else:
        note = f"다음 발표 예상: {e['period']}"
    return {
        "next_period": e["period"],
        "expected_window": e["expected_window"],
        "days_until": days,
        "is_imminent": is_imminent,
        "note": note,
    }
