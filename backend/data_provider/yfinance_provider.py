# Yahoo Finance 시세 프로바이더 — yfinance 라이브러리 없이 httpx로 직접 호출.
# (yfinance + pandas 의존성을 피해 Render 빌드 가볍게)
#
# Yahoo Finance Chart API:
#   https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?range=1y&interval=1d
# 한국 종목: 005930.KS (KOSPI), 247540.KQ (KOSDAQ)

import math
import httpx
from typing import Dict, Any, List, Optional

from .mock_provider import STOCK_MASTER
from ..utils.cache import memoize


_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _find_meta(stock_code: str) -> Dict[str, str]:
    for m in STOCK_MASTER:
        if m["stock_code"] == stock_code:
            return m
    return {"stock_code": stock_code, "stock_name": stock_code, "market": "KOSPI", "sector": ""}


def _suffix(market: str) -> str:
    return ".KQ" if (market or "").upper() == "KOSDAQ" else ".KS"


def _fetch_chart(symbol: str, range_: str = "1y") -> Optional[Dict[str, Any]]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": range_, "interval": "1d", "includePrePost": "false"}
    headers = {"User-Agent": _UA, "Accept": "application/json"}
    try:
        with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as c:
            r = c.get(url, params=params)
            if r.status_code != 200:
                return None
            data = r.json()
            result = (data.get("chart") or {}).get("result") or []
            if not result:
                return None
            return result[0]
    except Exception as e:
        print(f"[yahoo] {symbol} fetch 실패: {e}")
        return None


def _fetch_with_suffix_retry(stock_code: str, range_: str = "1y"):
    """KS 우선, 실패 시 KQ. (data, symbol) 반환."""
    hint = _find_meta(stock_code).get("market", "")
    order = [_suffix(hint)] + [s for s in (".KS", ".KQ") if s != _suffix(hint)]
    for s in order:
        sym = f"{stock_code}{s}"
        data = _fetch_chart(sym, range_)
        if data and (data.get("timestamp") or []):
            return data, sym
    return None, None


def _extract_ohlcv(chart_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Yahoo chart 결과 → OHLCV 리스트."""
    import datetime as _dt
    ts = chart_result.get("timestamp") or []
    q = (((chart_result.get("indicators") or {}).get("quote") or [{}])[0]) or {}
    opens = q.get("open") or []
    highs = q.get("high") or []
    lows = q.get("low") or []
    closes = q.get("close") or []
    volumes = q.get("volume") or []

    out = []
    for i, t in enumerate(ts):
        try:
            c = closes[i]
            if c is None:
                continue
            d = _dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d")
            out.append({
                "date": d,
                "open":  float(opens[i] if opens[i] is not None else c),
                "high":  float(highs[i] if highs[i] is not None else c),
                "low":   float(lows[i] if lows[i] is not None else c),
                "close": float(c),
                "volume": int(volumes[i] or 0) if i < len(volumes) and volumes[i] is not None else 0,
            })
        except Exception:
            continue
    return out


def get_quote(stock_code: str) -> Optional[Dict[str, Any]]:
    def factory():
        data, sym = _fetch_with_suffix_retry(stock_code, "5d")
        if not data:
            return None
        meta = data.get("meta") or {}
        rows = _extract_ohlcv(data)
        if not rows:
            return None
        last = rows[-1]
        prev = rows[-2] if len(rows) >= 2 else last
        close = float(meta.get("regularMarketPrice") or last["close"])
        # 직전 거래일 종가 (chartPreviousClose는 range 첫 시점이라 부정확)
        prev_close = float(prev["close"]) if prev else float(meta.get("previousClose") or close)
        change = close - prev_close
        return {
            "stock_code": stock_code,
            "current_price": close,
            "prev_close": prev_close,
            "change": change,
            "change_rate": round((change / prev_close * 100) if prev_close else 0, 2),
            "open": last["open"],
            "high": last["high"],
            "low": last["low"],
            "volume": last["volume"],
            "_symbol": sym,
        }

    return memoize(f"yf:quote:{stock_code}", 60, factory)


def get_daily_ohlcv(stock_code: str, range_: str = "1y") -> List[Dict[str, Any]]:
    def factory():
        data, _ = _fetch_with_suffix_retry(stock_code, range_)
        return _extract_ohlcv(data) if data else []

    return memoize(f"yf:ohlcv:{stock_code}:{range_}", 600, factory) or []


def get_stock_basic_info(stock_code: str) -> Optional[Dict[str, Any]]:
    def factory():
        data, sym = _fetch_with_suffix_retry(stock_code, "1y")
        if not data:
            return None
        meta = data.get("meta") or {}
        rows = _extract_ohlcv(data)
        if not rows:
            return None

        last = rows[-1]
        prev = rows[-2] if len(rows) >= 2 else last
        close = float(meta.get("regularMarketPrice") or last["close"])
        # 직전 거래일 종가 (chartPreviousClose는 range 첫 시점이라 부정확)
        prev_close = float(prev["close"]) if prev else float(meta.get("previousClose") or close)
        change_rate = round(((close - prev_close) / prev_close * 100) if prev_close else 0, 2)

        high_52w = float(meta.get("fiftyTwoWeekHigh") or max(r["high"] for r in rows))
        low_52w = float(meta.get("fiftyTwoWeekLow") or min(r["low"] for r in rows))

        # 시가총액: meta.marketCap > shares × close
        market_cap = 0
        try:
            market_cap = int(meta.get("marketCap") or 0)
        except Exception:
            pass
        if not market_cap:
            shares = 0
            try:
                shares = int(meta.get("sharesOutstanding") or 0)
            except Exception:
                pass
            if shares:
                market_cap = int(shares * close)

        if market_cap >= 5_000_000_000_000:
            cap_type = "large"
        elif market_cap >= 500_000_000_000:
            cap_type = "mid"
        else:
            cap_type = "small"

        meta_master = _find_meta(stock_code)
        exch = (meta.get("fullExchangeName") or meta.get("exchangeName") or "").upper()
        if "KOSDAQ" in exch or "KOE" in exch:
            market = "KOSDAQ"
        elif "KSC" in exch or "KOSPI" in exch or "KRX" in exch:
            market = "KOSPI"
        else:
            market = meta_master.get("market", "KOSPI")

        return {
            "stock_code": stock_code,
            "stock_name": meta_master.get("stock_name") or stock_code,
            "market": market,
            "sector": meta_master.get("sector", ""),
            "current_price": close,
            "change_rate": change_rate,
            "volume": last["volume"],
            "trading_value": int(close * last["volume"]),
            "market_cap": market_cap,
            "market_cap_type": cap_type,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "_source": "yahoo",
            "_symbol": sym,
        }

    return memoize(f"yf:basic:{stock_code}", 60, factory)


def get_price_history(stock_code: str) -> Optional[Dict[str, Any]]:
    raw = get_daily_ohlcv(stock_code, "1y")
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

    gains, losses = [], []
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        gains.append(max(ch, 0))
        losses.append(max(-ch, 0))
    rsi_values = [None]
    period = 14
    for i in range(len(gains)):
        if i < period - 1:
            rsi_values.append(None); continue
        avg_g = sum(gains[i - period + 1:i + 1]) / period
        avg_l = sum(losses[i - period + 1:i + 1]) / period
        if avg_l == 0:
            rsi_values.append(100.0)
        else:
            rs = avg_g / avg_l
            rsi_values.append(round(100 - 100 / (1 + rs), 2))

    def ema(data, period):
        k = 2 / (period + 1); out = []; prev = None
        for v in data:
            if v is None:
                out.append(None); continue
            prev = v if prev is None else v * k + prev * (1 - k)
            out.append(prev)
        return out

    ema12 = ema(closes, 12); ema26 = ema(closes, 26)
    macd = [(ema12[i] - ema26[i]) if (ema12[i] is not None and ema26[i] is not None) else None
            for i in range(len(closes))]
    signal = ema([m if m is not None else 0 for m in macd], 9)

    bb_upper, bb_lower = [], []
    for i in range(len(closes)):
        if i < 19:
            bb_upper.append(None); bb_lower.append(None); continue
        w = closes[i - 19:i + 1]
        m = sum(w) / 20
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / 20)
        bb_upper.append(round(m + 2 * sd, 2))
        bb_lower.append(round(m - 2 * sd, 2))

    return {
        "prices": prices, "volumes": volumes,
        "ma5": ma5, "ma20": ma20, "ma60": ma60, "ma120": ma120,
        "rsi": rsi_values, "macd": macd, "macd_signal": signal,
        "bb_upper": bb_upper, "bb_lower": bb_lower,
        "high_52w": max(closes), "low_52w": min(closes),
        "_source": "yahoo",
    }
