# yfinance(Yahoo Finance) 시세 프로바이더.
# 네이버 차단 시 두 번째 폴백. Yahoo는 글로벌 서비스라 클라우드 IP 차단 거의 없음.
# 한국 종목: 005930.KS (KOSPI), 247540.KQ (KOSDAQ)

import math
from datetime import datetime
from typing import Dict, Any, List, Optional

from .mock_provider import MockProvider, STOCK_MASTER
from ..utils.cache import memoize


def _try_yf():
    try:
        import yfinance as yf
        return yf
    except Exception:
        return None


_mock = MockProvider()


def _find_market(stock_code: str) -> str:
    for m in STOCK_MASTER:
        if m["stock_code"] == stock_code:
            return m["market"]
    return "KOSPI"


def _suffix(market: str) -> str:
    return ".KQ" if (market or "").upper() == "KOSDAQ" else ".KS"


def _fetch_history(stock_code: str, period: str = "1y"):
    yf = _try_yf()
    if yf is None:
        return None, None
    # 두 suffix 모두 시도
    suffixes = [_suffix(_find_market(stock_code)), ".KS", ".KQ"]
    seen = set()
    for s in suffixes:
        if s in seen:
            continue
        seen.add(s)
        try:
            symbol = f"{stock_code}{s}"
            t = yf.Ticker(symbol)
            hist = t.history(period=period, auto_adjust=False)
            if hist is not None and len(hist) > 0:
                return hist, symbol
        except Exception as e:
            print(f"[yfinance] {symbol} 실패: {e}")
    return None, None


def get_quote(stock_code: str) -> Optional[Dict[str, Any]]:
    def factory():
        hist, symbol = _fetch_history(stock_code, "5d")
        if hist is None or len(hist) == 0:
            return None
        try:
            last = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else last
            close = float(last["Close"])
            prev_close = float(prev["Close"])
            change = close - prev_close
            change_rate = (change / prev_close * 100) if prev_close else 0
            return {
                "stock_code": stock_code,
                "stock_name": "",
                "current_price": close,
                "prev_close": prev_close,
                "change": change,
                "change_rate": round(change_rate, 2),
                "open": float(last["Open"]),
                "high": float(last["High"]),
                "low": float(last["Low"]),
                "volume": int(last["Volume"] or 0),
                "_symbol": symbol,
            }
        except Exception as e:
            print(f"[yfinance quote] 파싱 실패({stock_code}): {e}")
            return None

    return memoize(f"yf:quote:{stock_code}", 60, factory)


def get_daily_ohlcv(stock_code: str, period: str = "1y") -> List[Dict[str, Any]]:
    def factory():
        hist, _ = _fetch_history(stock_code, period)
        if hist is None or len(hist) == 0:
            return []
        out = []
        for idx, row in hist.iterrows():
            try:
                date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
                out.append({
                    "date": date_str,
                    "open":  float(row["Open"]),
                    "high":  float(row["High"]),
                    "low":   float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"] or 0),
                })
            except Exception:
                continue
        return out

    return memoize(f"yf:ohlcv:{stock_code}:{period}", 600, factory) or []


def get_stock_basic_info(stock_code: str) -> Optional[Dict[str, Any]]:
    quote = get_quote(stock_code)
    if not quote:
        return None
    ohlcv = get_daily_ohlcv(stock_code, "1y")
    if ohlcv:
        highs = [o["high"] for o in ohlcv]
        lows = [o["low"] for o in ohlcv]
        high_52w = max(highs)
        low_52w = min(lows)
    else:
        high_52w = quote["high"]
        low_52w = quote["low"]

    # 종목명/시총은 mock에서 보조
    mock_info = _mock.get_stock_basic_info(stock_code)
    market_cap = mock_info.get("market_cap", 0)
    if market_cap >= 5_000_000_000_000:
        cap_type = "large"
    elif market_cap >= 500_000_000_000:
        cap_type = "mid"
    else:
        cap_type = "small"

    return {
        "stock_code": stock_code,
        "stock_name": mock_info.get("stock_name", stock_code),
        "market": mock_info.get("market", "KOSPI"),
        "sector": mock_info.get("sector", ""),
        "current_price": quote["current_price"],
        "change_rate": quote["change_rate"],
        "volume": quote["volume"],
        "trading_value": int(quote["current_price"] * quote["volume"]),
        "market_cap": market_cap,
        "market_cap_type": cap_type,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "_source": "yfinance",
    }


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
        "_source": "yfinance",
    }
