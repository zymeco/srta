# 매크로 지표: USD/KRW 환율, 미국 S&P500/나스닥, VIX, SOX(반도체 인덱스).

import httpx
from typing import Dict, Any
from ..utils.cache import memoize


MACRO_SYMBOLS = {
    "usd_krw":   {"symbol": "KRW=X",  "name": "USD/KRW 환율",  "unit": "원"},
    "sp500":     {"symbol": "^GSPC",  "name": "S&P 500",      "unit": ""},
    "nasdaq":    {"symbol": "^IXIC",  "name": "나스닥",         "unit": ""},
    "vix":       {"symbol": "^VIX",   "name": "VIX (변동성)",   "unit": ""},
    "sox":       {"symbol": "^SOX",   "name": "필라델피아 반도체", "unit": ""},
    "dow":       {"symbol": "^DJI",   "name": "다우존스",        "unit": ""},
}


def _fetch_one(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "1mo", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        with httpx.Client(timeout=8.0, headers=headers, follow_redirects=True) as c:
            r = c.get(url, params=params)
            if r.status_code != 200:
                return None
            data = r.json()
            res = (data.get("chart") or {}).get("result") or []
            if not res:
                return None
            meta = res[0].get("meta") or {}
            ind = (((res[0].get("indicators") or {}).get("quote") or [{}])[0]) or {}
            closes = [c for c in (ind.get("close") or []) if c is not None]
            if not closes:
                return None
            cur = float(meta.get("regularMarketPrice") or closes[-1])
            prev = float(closes[-2]) if len(closes) >= 2 else cur
            change = cur - prev
            change_rate = (change / prev * 100) if prev else 0
            # 한 달 추세
            m_first = closes[0] if closes else cur
            month_chg = (cur - m_first) / m_first * 100 if m_first else 0
            return {
                "current": round(cur, 2),
                "change": round(change, 2),
                "change_rate": round(change_rate, 2),
                "month_change": round(month_chg, 2),
            }
    except Exception as e:
        print(f"[macro] {symbol} 실패: {e}")
        return None


def get_macro() -> Dict[str, Any]:
    def factory():
        out = {}
        for key, info in MACRO_SYMBOLS.items():
            d = _fetch_one(info["symbol"])
            if d:
                d["name"] = info["name"]
                d["unit"] = info["unit"]
                d["symbol"] = info["symbol"]
                out[key] = d
        return out
    return memoize("macro_all", 600, factory) or {}


def get_macro_context_text(macro: Dict[str, Any]) -> str:
    """매크로 상황을 한 줄 텍스트로."""
    parts = []
    if "vix" in macro:
        v = macro["vix"]["current"]
        if v > 25:
            parts.append(f"VIX {v} 변동성 높음")
        elif v < 15:
            parts.append(f"VIX {v} 안정")
    if "usd_krw" in macro:
        u = macro["usd_krw"]
        if abs(u.get("month_change", 0)) > 3:
            parts.append(f"환율 {u['month_change']:+.1f}%")
    if "sox" in macro:
        s = macro["sox"]
        if s.get("month_change", 0) > 5:
            parts.append(f"반도체섹터 {s['month_change']:+.1f}%")
        elif s.get("month_change", 0) < -5:
            parts.append(f"반도체섹터 {s['month_change']:+.1f}%")
    return " · ".join(parts) if parts else "특이사항 없음"
