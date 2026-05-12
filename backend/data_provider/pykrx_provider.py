# pykrx 기반 실제 데이터 프로바이더.
# pykrx는 KRX 사이트를 크롤링하므로 호출이 느릴 수 있어 결과를 캐시한다.
# 누락 영역(뉴스 등)은 안전한 기본값으로 채워 분석 파이프라인이 멈추지 않게 한다.

import os
import json
import math
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .base_provider import BaseProvider
from .mock_provider import MockProvider, STOCK_MASTER
from ..utils import cache as memcache
from ..utils.cache import memoize


# 디스크 캐시 경로 (한 번 받으면 다음 실행에 즉시 사용)
_TICKER_CACHE_FILE = os.path.join(os.path.dirname(__file__), "_krx_master_cache.json")


# ---- 캐시 TTL ----
TTL_SHORT = 60          # 1분: 현재가/거래량
TTL_MED = 60 * 15       # 15분: 시세 히스토리
TTL_LONG = 60 * 60 * 6  # 6시간: 종목 마스터/재무


def _try_import_pykrx():
    try:
        from pykrx import stock as pkstock
        return pkstock
    except Exception:
        return None


_mock = MockProvider()


def _today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def _back_days(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).strftime("%Y%m%d")


def _safe(fn, default):
    try:
        v = fn()
        return v if v is not None else default
    except Exception:
        return default


class PykrxProvider(BaseProvider):
    """pykrx + (필요한 곳은) Mock 폴백."""

    def __init__(self):
        self.pk = _try_import_pykrx()
        self.available = self.pk is not None

    # ---------- 검색 ----------
    _prefetch_started = False
    _prefetch_lock = threading.Lock()

    def _load_disk_cache(self) -> List[Dict[str, str]]:
        try:
            if os.path.exists(_TICKER_CACHE_FILE):
                with open(_TICKER_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data
        except Exception as e:
            print(f"[pykrx] 디스크 캐시 로드 실패: {e}")
        return []

    def _save_disk_cache(self, data: List[Dict[str, str]]):
        try:
            with open(_TICKER_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print(f"[pykrx] 디스크 캐시 저장 실패: {e}")

    def _prefetch_all_tickers_async(self):
        """전체 KOSPI+KOSDAQ 종목 마스터를 백그라운드로 채움.
        KRX → 네이버 금융 → pykrx 순으로 시도."""
        with PykrxProvider._prefetch_lock:
            if PykrxProvider._prefetch_started:
                return
            PykrxProvider._prefetch_started = True

        def worker():
            try:
                # 1순위: KRX 직접 호출, 2순위: 네이버 금융 크롤링
                from .krx_master_fetcher import fetch_master_with_fallback
                out = fetch_master_with_fallback()

                # 3순위: pykrx
                if not out and self.available:
                    try:
                        out = []
                        today = _today_str()
                        for market in ("KOSPI", "KOSDAQ"):
                            try:
                                tickers = self.pk.get_market_ticker_list(date=today, market=market)
                                for t in tickers:
                                    try:
                                        name = self.pk.get_market_ticker_name(t)
                                    except Exception:
                                        name = t
                                    out.append({"stock_code": t, "stock_name": name,
                                                "market": market, "sector": ""})
                            except Exception:
                                continue
                    except Exception as e:
                        print(f"[pykrx prefetch 폴백 실패]: {e}")

                if out:
                    memcache.put("all_tickers", out, TTL_LONG)
                    self._save_disk_cache(out)
                    print(f"[종목마스터] {len(out)}개 캐시 완료 (디스크 저장)")
                else:
                    print(f"[종목마스터] 다운로드 실패 — STOCK_MASTER 폴백 유지")
            except Exception as e:
                print(f"[종목마스터 prefetch 실패]: {e}")
            finally:
                with PykrxProvider._prefetch_lock:
                    PykrxProvider._prefetch_started = False

        threading.Thread(target=worker, daemon=True).start()

    def _get_all_tickers_cached(self) -> List[Dict[str, str]]:
        """메모리 캐시 > 디스크 캐시 > STOCK_MASTER 폴백 (+ 백그라운드 갱신)."""
        cached = memcache.get("all_tickers")
        if cached:
            return cached
        # 디스크 캐시 사용
        disk = self._load_disk_cache()
        if disk:
            memcache.put("all_tickers", disk, TTL_LONG)
            # 백그라운드에서 최신 데이터 다시 받기 (성공 시 갱신)
            self._prefetch_all_tickers_async()
            return disk
        # 둘 다 없으면 STOCK_MASTER 즉시 반환 + prefetch
        self._prefetch_all_tickers_async()
        return STOCK_MASTER

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        # 대소문자/공백 무시 매칭
        ql = q.lower().replace(" ", "")
        master = self._get_all_tickers_cached()
        results = []
        seen = set()

        def match(m):
            name_norm = (m.get("stock_name") or "").lower().replace(" ", "")
            return q == m["stock_code"] or ql in name_norm

        for m in master:
            if match(m) and m["stock_code"] not in seen:
                seen.add(m["stock_code"])
                results.append(m)
                if len(results) >= 20:
                    break
        # 보조 매칭: STOCK_MASTER에 있는데 마스터에는 없는 종목까지 포함
        if len(results) < 20:
            for m in STOCK_MASTER:
                if m["stock_code"] in seen:
                    continue
                if match(m):
                    seen.add(m["stock_code"])
                    results.append(m)
                    if len(results) >= 20:
                        break
        return results

    # ---------- 기본 정보 ----------
    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        if not self.available:
            return _mock.get_stock_basic_info(stock_code)

        def factory():
            try:
                today = _today_str()
                start = _back_days(370)
                name = self.pk.get_market_ticker_name(stock_code)
                # 시장 구분
                market = "KOSPI"
                try:
                    if stock_code in self.pk.get_market_ticker_list(market="KOSDAQ"):
                        market = "KOSDAQ"
                except Exception:
                    pass

                # 최근 일자 OHLCV
                ohlcv = self.pk.get_market_ohlcv(start, today, stock_code)
                if ohlcv is None or len(ohlcv) == 0:
                    raise RuntimeError("OHLCV empty")
                last_row = ohlcv.iloc[-1]
                close = float(last_row["종가"])
                change = float(last_row.get("등락률", 0) or 0)
                volume = int(last_row.get("거래량", 0) or 0)
                trading_value = int(last_row.get("거래대금", close * volume) or close * volume)

                high_52w = float(ohlcv["고가"].max())
                low_52w = float(ohlcv["저가"].min())

                # 시가총액
                try:
                    cap_df = self.pk.get_market_cap(today, today, stock_code)
                    if cap_df is None or len(cap_df) == 0:
                        cap_df = self.pk.get_market_cap_by_date(_back_days(5), today, stock_code)
                    market_cap = int(cap_df.iloc[-1].get("시가총액", 0))
                except Exception:
                    market_cap = int(close * volume * 100)

                if market_cap >= 5_000_000_000_000:
                    cap_type = "large"
                elif market_cap >= 500_000_000_000:
                    cap_type = "mid"
                else:
                    cap_type = "small"

                return {
                    "stock_code": stock_code,
                    "stock_name": name,
                    "market": market,
                    "sector": "",
                    "current_price": close,
                    "change_rate": round(change, 2),
                    "volume": volume,
                    "trading_value": trading_value,
                    "market_cap": market_cap,
                    "market_cap_type": cap_type,
                    "high_52w": high_52w,
                    "low_52w": low_52w,
                }
            except Exception as e:
                print(f"[pykrx] basic_info 폴백({stock_code}): {e}")
                return _mock.get_stock_basic_info(stock_code)

        return memoize(f"basic:{stock_code}", TTL_SHORT, factory)

    # ---------- 시세 히스토리 ----------
    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        if not self.available:
            return _mock.get_price_history(stock_code)

        def factory():
            try:
                end = _today_str()
                start = _back_days(220)
                df = self.pk.get_market_ohlcv(start, end, stock_code)
                if df is None or len(df) == 0:
                    raise RuntimeError("OHLCV empty")

                df = df.tail(150)
                prices, volumes = [], []
                for idx, row in df.iterrows():
                    date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
                    prices.append({"date": date_str, "close": float(row["종가"])})
                    volumes.append({"date": date_str, "volume": int(row.get("거래량", 0) or 0)})

                closes = [p["close"] for p in prices]

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
                    gains.append(max(ch, 0)); losses.append(max(-ch, 0))
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

                # 52주 고/저는 basic_info에서 한번 더 일치
                high_52w = max(closes)
                low_52w = min(closes)

                return {
                    "prices": prices,
                    "volumes": volumes,
                    "ma5": ma5, "ma20": ma20, "ma60": ma60, "ma120": ma120,
                    "rsi": rsi_values, "macd": macd, "macd_signal": signal,
                    "bb_upper": bb_upper, "bb_lower": bb_lower,
                    "high_52w": high_52w, "low_52w": low_52w,
                }
            except Exception as e:
                print(f"[pykrx] price_history 폴백({stock_code}): {e}")
                return _mock.get_price_history(stock_code)

        return memoize(f"price:{stock_code}", TTL_MED, factory)

    # ---------- 재무 ----------
    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        if not self.available:
            return _mock.get_financial_data(stock_code)

        def factory():
            try:
                today = _today_str()
                fund = self.pk.get_market_fundamental(today, today, stock_code)
                if fund is None or len(fund) == 0:
                    fund = self.pk.get_market_fundamental_by_date(_back_days(7), today, stock_code)
                row = fund.iloc[-1]
                per = float(row.get("PER", 0) or 0)
                pbr = float(row.get("PBR", 0) or 0)
                eps = float(row.get("EPS", 0) or 0)
                bps = float(row.get("BPS", 0) or 0)
                div_yield = float(row.get("DIV", 0) or 0)

                # pykrx에서 부채비율/유동비율/현금흐름 등은 직접 제공하지 않음.
                # 분석 파이프라인이 기대하는 키를 안전한 기본값과 함께 채운다.
                # 추후 DART 연동 시 교체.
                fin = _mock.get_financial_data(stock_code)
                fin.update({
                    "per": round(per, 1) if per else fin.get("per"),
                    "pbr": round(pbr, 2) if pbr else fin.get("pbr"),
                    "eps": round(eps, 1),
                    "bps": round(bps, 1),
                    "dividend_yield": round(div_yield, 2),
                })
                return fin
            except Exception as e:
                print(f"[pykrx] financial 폴백({stock_code}): {e}")
                return _mock.get_financial_data(stock_code)

        return memoize(f"fin:{stock_code}", TTL_LONG, factory)

    # ---------- 수급 ----------
    def get_supply_data(self, stock_code: str) -> Dict[str, Any]:
        if not self.available:
            return _mock.get_supply_data(stock_code)

        def factory():
            try:
                end = _today_str()
                start = _back_days(40)
                df = self.pk.get_market_trading_value_by_date(start, end, stock_code)
                if df is None or len(df) == 0:
                    raise RuntimeError("trading_value empty")

                df = df.tail(20)
                # 컬럼 명은 pykrx 버전에 따라 다를 수 있어 안전 접근
                cols = {c: c for c in df.columns}
                def col(*names):
                    for n in names:
                        if n in cols:
                            return n
                    return None

                c_foreign = col("외국인", "외국인합계")
                c_inst = col("기관합계", "기관")
                c_indi = col("개인")

                series = []
                for idx, row in df.iterrows():
                    date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, "strftime") else str(idx)[:10]
                    series.append({
                        "date": date_str,
                        "foreign": int(row[c_foreign]) if c_foreign else 0,
                        "institution": int(row[c_inst]) if c_inst else 0,
                        "individual": int(row[c_indi]) if c_indi else 0,
                    })

                f5 = sum(x["foreign"] for x in series[-5:])
                f20 = sum(x["foreign"] for x in series)
                i5 = sum(x["institution"] for x in series[-5:])
                i20 = sum(x["institution"] for x in series)
                ind = sum(x["individual"] for x in series)

                # 공매도/신용잔고는 pykrx에 별도 함수가 있지만 실패 가능 → 안전 기본값
                short_ratio = 0.0
                try:
                    sd = self.pk.get_shorting_balance_by_date(_back_days(10), end, stock_code)
                    if sd is not None and len(sd) > 0:
                        last = sd.iloc[-1]
                        v = last.get("비중") or last.get("공매도잔고비중") or 0
                        short_ratio = float(v) if v is not None else 0.0
                except Exception:
                    pass

                return {
                    "series": series,
                    "foreign_5d": f5,
                    "foreign_20d": f20,
                    "institution_5d": i5,
                    "institution_20d": i20,
                    "individual_20d": ind,
                    "program": 0,
                    "short_selling_ratio": round(short_ratio, 2),
                    "credit_balance_ratio": 0.0,
                }
            except Exception as e:
                print(f"[pykrx] supply 폴백({stock_code}): {e}")
                return _mock.get_supply_data(stock_code)

        return memoize(f"sup:{stock_code}", TTL_SHORT, factory)

    # ---------- 뉴스 (pykrx 미제공 → Mock) ----------
    def get_news_data(self, stock_code: str) -> Dict[str, Any]:
        # 추후 네이버 검색 API로 교체
        return _mock.get_news_data(stock_code)

    # ---------- 리스크 (pykrx 미제공 → Mock 폴백, 단 실제 상태와 다를 수 있음) ----------
    def get_risk_data(self, stock_code: str) -> Dict[str, Any]:
        # 정확한 관리종목/감사의견 정보는 DART 등 별도 소스 필요.
        # 안전을 위해 일부 항목은 False로 시작.
        risk = _mock.get_risk_data(stock_code)
        # 실제로 검증 불가한 항목은 False로 (오탐 방지)
        for k in [
            "management_stock", "investment_warning", "investment_danger",
            "capital_impairment", "trading_halt_history", "audit_issue",
            "delisting_risk", "unfaithful_disclosure",
        ]:
            risk[k] = False
        return risk
