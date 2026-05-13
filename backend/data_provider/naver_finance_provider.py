# 네이버 금융 시세 프로바이더 (현재가 + 일별 OHLCV).
# pykrx가 KRX 직접 호출에 막힐 때(클라우드 IP 차단 등) 가장 안정적인 대안.
#   - polling.finance.naver.com:  현재가/등락 (EUC-KR JSON)
#   - fchart.stock.naver.com:     일별 OHLCV (EUC-KR XML)
# 키 불필요, 무료.

import re
import json
import math
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional

from .mock_provider import STOCK_MASTER
from ..utils.cache import memoize

POLLING_URL = "https://polling.finance.naver.com/api/realtime"
FCHART_URL = "https://fchart.stock.naver.com/sise.nhn"

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

def _find_meta(stock_code: str):
    for m in STOCK_MASTER:
        if m["stock_code"] == stock_code:
            return m
    return {"stock_code": stock_code, "stock_name": stock_code, "market": "KOSPI", "sector": ""}


def _headers():
    return {
        "User-Agent": _UA,
        "Referer": "https://finance.naver.com/",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }


def _decode(b: bytes) -> str:
    for enc in ("euc-kr", "cp949", "utf-8-sig", "utf-8"):
        try:
            return b.decode(enc)
        except Exception:
            continue
    return b.decode("euc-kr", errors="replace")


def get_quote(stock_code: str) -> Optional[Dict[str, Any]]:
    """현재가/전일종가/등락폭/등락률/거래량. 실패 시 None."""
    def factory():
        try:
            params = {"query": f"SERVICE_ITEM:{stock_code}"}
            with httpx.Client(timeout=8.0, headers=_headers()) as c:
                r = c.get(POLLING_URL, params=params)
                r.raise_for_status()
                text = _decode(r.content)
            data = json.loads(text)
            datas = (data.get("result") or {}).get("areas") or []
            if not datas or not datas[0].get("datas"):
                return None
            it = datas[0]["datas"][0]
            # rf: 1=상한 2=상승 3=보합 4=하한 5=하락
            rf = it.get("rf", "3")
            sign = 1 if rf in ("1", "2") else (-1 if rf in ("4", "5") else 0)
            cr = float(it.get("cr", 0))
            change_rate = sign * cr if sign != 0 else 0.0
            return {
                "stock_code": stock_code,
                "stock_name": it.get("nm", ""),
                "current_price": float(it.get("nv", 0)),
                "prev_close": float(it.get("pcv", 0)),
                "change": sign * float(it.get("cv", 0)),
                "change_rate": round(change_rate, 2),
                "open": float(it.get("ov", 0)),
                "high": float(it.get("hv", 0)),
                "low": float(it.get("lv", 0)),
                "volume": int(it.get("aq", 0)),
                "upper_limit": float(it.get("ul", 0)),
                "lower_limit": float(it.get("ll", 0)),
                "market_state": it.get("ms", ""),
            }
        except Exception as e:
            print(f"[Naver quote] 실패({stock_code}): {e}")
            return None

    # 30초 캐시
    return memoize(f"naver:quote:{stock_code}", 30, factory)


def get_daily_ohlcv(stock_code: str, count: int = 150) -> List[Dict[str, Any]]:
    """일별 OHLCV. 실패 시 빈 리스트."""
    def factory():
        try:
            params = {
                "symbol": stock_code,
                "timeframe": "day",
                "count": count,
                "requestType": "0",
            }
            with httpx.Client(timeout=10.0, headers=_headers()) as c:
                r = c.get(FCHART_URL, params=params)
                r.raise_for_status()
                text = _decode(r.content)
            # <item data="20250925|84400|86200|84100|86100|19665151" />
            items = []
            for m in re.finditer(r'<item data="([^"]+)"', text):
                parts = m.group(1).split("|")
                if len(parts) < 6:
                    continue
                try:
                    date_str = parts[0]
                    # YYYYMMDD → YYYY-MM-DD
                    date_iso = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    items.append({
                        "date": date_iso,
                        "open":  float(parts[1]),
                        "high":  float(parts[2]),
                        "low":   float(parts[3]),
                        "close": float(parts[4]),
                        "volume": int(parts[5] or 0),
                    })
                except Exception:
                    continue
            return items
        except Exception as e:
            print(f"[Naver ohlcv] 실패({stock_code}): {e}")
            return []

    # 10분 캐시
    return memoize(f"naver:ohlcv:{stock_code}:{count}", 600, factory) or []


def _parse_korean_money(s: str) -> int:
    """'1,408조 2,999억' 같은 문자열 → 원 단위 정수."""
    if not s:
        return 0
    s = s.replace(",", "").replace(" ", "")
    total = 0
    import re
    m = re.search(r"(\d+(?:\.\d+)?)조", s)
    if m:
        total += int(float(m.group(1)) * 1_0000_0000_0000)
    m = re.search(r"(\d+(?:\.\d+)?)억", s)
    if m:
        total += int(float(m.group(1)) * 1_0000_0000)
    if total == 0:
        try:
            total = int(s.replace("원", ""))
        except Exception:
            pass
    return total


def _parse_num(s: str) -> float:
    if not s:
        return 0.0
    s = str(s).replace(",", "").replace("배", "").replace("%", "").replace("원", "").replace(" ", "")
    try:
        return float(s)
    except Exception:
        return 0.0


def get_fundamentals(stock_code: str) -> Optional[Dict[str, Any]]:
    """네이버 종목 종합 정보에서 PER/PBR/EPS/BPS/시총/외인소진율 등 받음."""
    def factory():
        try:
            url = f"https://m.stock.naver.com/api/stock/{stock_code}/integration"
            with httpx.Client(timeout=8.0, headers=_headers()) as c:
                r = c.get(url)
                r.raise_for_status()
                d = r.json()
            kv = {}
            for ti in d.get("totalInfos", []) or []:
                k = (ti.get("key") or "").strip()
                v = ti.get("value") or ""
                kv[k] = v
            return {
                "per": _parse_num(kv.get("PER")),
                "forward_per": _parse_num(kv.get("추정PER")),
                "eps": _parse_num(kv.get("EPS")),
                "forward_eps": _parse_num(kv.get("추정EPS")),
                "pbr": _parse_num(kv.get("PBR")),
                "bps": _parse_num(kv.get("BPS")),
                "dividend_yield": _parse_num(kv.get("배당수익률")),
                "dividend_per_share": _parse_num(kv.get("주당배당금")),
                "market_cap": _parse_korean_money(kv.get("시총", "")),
                "foreign_ratio": _parse_num(kv.get("외인소진율")),
                "_source": "naver_integration",
            }
        except Exception as e:
            print(f"[Naver fundamentals] 실패({stock_code}): {e}")
            return None

    return memoize(f"naver:fund:{stock_code}", 600, factory)


def get_market_cap_class(market_cap: float) -> str:
    if market_cap >= 5_000_000_000_000:
        return "large"
    if market_cap >= 500_000_000_000:
        return "mid"
    return "small"


def get_stock_basic_info(stock_code: str, fallback_name: str = "") -> Optional[Dict[str, Any]]:
    """기본 정보. 현재가 + 일별 시세에서 52주 고/저 산출."""
    quote = get_quote(stock_code)
    if not quote:
        return None
    ohlcv = get_daily_ohlcv(stock_code, count=260)  # 약 1년
    if ohlcv:
        highs = [o["high"] for o in ohlcv]
        lows = [o["low"] for o in ohlcv]
        high_52w = max(highs) if highs else quote["high"]
        low_52w = min(lows) if lows else quote["low"]
    else:
        high_52w = quote["high"]
        low_52w = quote["low"]

    meta = _find_meta(stock_code)

    # 시총 / 외인소진율 등은 integration API에서
    fund = get_fundamentals(stock_code) or {}
    market_cap = int(fund.get("market_cap") or 0)
    if market_cap >= 5_000_000_000_000:
        cap_type = "large"
    elif market_cap >= 500_000_000_000:
        cap_type = "mid"
    else:
        cap_type = "small"

    return {
        "stock_code": stock_code,
        "stock_name": quote["stock_name"] or fallback_name or meta.get("stock_name") or stock_code,
        "market": meta.get("market", "KOSPI"),
        "sector": meta.get("sector", ""),
        "current_price": quote["current_price"],
        "change_rate": quote["change_rate"],
        "volume": quote["volume"],
        "trading_value": int(quote["current_price"] * quote["volume"]),
        "market_cap": market_cap,
        "market_cap_type": cap_type,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "_source": "naver",
    }


def get_price_history(stock_code: str) -> Optional[Dict[str, Any]]:
    """일별 시세 + 이동평균/RSI/MACD/볼린저밴드 계산."""
    raw = get_daily_ohlcv(stock_code, count=200)
    if not raw or len(raw) < 30:
        return None

    raw = raw[-150:]
    prices = [{"date": d["date"], "close": d["close"]} for d in raw]
    volumes = [{"date": d["date"], "volume": d["volume"]} for d in raw]
    closes = [d["close"] for d in raw]

    def sma(period):
        out = []
        for i in range(len(closes)):
            if i < period - 1:
                out.append(None)
            else:
                out.append(round(sum(closes[i - period + 1:i + 1]) / period, 2))
        return out

    ma5, ma20, ma60, ma120 = sma(5), sma(20), sma(60), sma(120)

    # RSI(14)
    gains, losses = [], []
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains.append(max(ch, 0))
        losses.append(max(-ch, 0))
    rsi_values = [None]
    period = 14
    for i in range(len(gains)):
        if i < period - 1:
            rsi_values.append(None)
            continue
        avg_g = sum(gains[i - period + 1:i + 1]) / period
        avg_l = sum(losses[i - period + 1:i + 1]) / period
        if avg_l == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_g / avg_l
            rsi_values.append(round(100 - 100 / (1 + rs), 2))

    # EMA
    def ema(data, period):
        k = 2 / (period + 1)
        out = []
        prev = None
        for v in data:
            if v is None:
                out.append(None)
                continue
            prev = v if prev is None else v * k + prev * (1 - k)
            out.append(prev)
        return out

    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd = [
        (ema12[i] - ema26[i]) if (ema12[i] is not None and ema26[i] is not None) else None
        for i in range(len(closes))
    ]
    signal = ema([m if m is not None else 0 for m in macd], 9)

    bb_upper, bb_lower = [], []
    for i in range(len(closes)):
        if i < 19:
            bb_upper.append(None)
            bb_lower.append(None)
            continue
        w = closes[i - 19:i + 1]
        m = sum(w) / 20
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / 20)
        bb_upper.append(round(m + 2 * sd, 2))
        bb_lower.append(round(m - 2 * sd, 2))

    high_52w = max(closes)
    low_52w = min(closes)

    return {
        "prices": prices,
        "volumes": volumes,
        "ma5": ma5, "ma20": ma20, "ma60": ma60, "ma120": ma120,
        "rsi": rsi_values, "macd": macd, "macd_signal": signal,
        "bb_upper": bb_upper, "bb_lower": bb_lower,
        "high_52w": high_52w, "low_52w": low_52w,
        "_source": "naver",
    }
