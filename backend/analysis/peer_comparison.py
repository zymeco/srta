# 동종 업종 비교.
# STOCK_MASTER에서 같은 sector 종목 추출 → 네이버 fundamentals 비교.

from typing import Dict, Any, List
from ..data_provider.mock_provider import STOCK_MASTER
from ..data_provider import naver_finance_provider
from ..utils.cache import memoize


def get_peer_list(stock_code: str, sector: str, max_peers: int = 6) -> List[str]:
    if not sector:
        return []
    peers = [m["stock_code"] for m in STOCK_MASTER
             if m.get("sector") == sector and m["stock_code"] != stock_code]
    return peers[:max_peers]


def get_peer_comparison(stock_code: str, sector: str) -> Dict[str, Any]:
    if not sector:
        return {"available": False, "reason": "섹터 정보 없음"}

    def factory():
        from concurrent.futures import ThreadPoolExecutor
        peers = get_peer_list(stock_code, sector)
        if not peers:
            return {"available": False, "reason": f"동종 업종 종목 없음 ({sector})"}

        codes = [stock_code] + peers

        def fetch_one(code):
            try:
                fund = naver_finance_provider.get_fundamentals(code) or {}
                quote = naver_finance_provider.get_quote(code) or {}
                meta = next((m for m in STOCK_MASTER if m["stock_code"] == code), {"stock_name": code})
                return {
                    "stock_code": code,
                    "stock_name": meta.get("stock_name", code),
                    "per": fund.get("forward_per") or fund.get("per") or 0,
                    "pbr": fund.get("pbr") or 0,
                    "eps": fund.get("eps") or 0,
                    "div_yield": fund.get("dividend_yield") or 0,
                    "market_cap": fund.get("market_cap") or 0,
                    "current_price": quote.get("current_price") or 0,
                    "change_rate": quote.get("change_rate") or 0,
                    "is_self": code == stock_code,
                }
            except Exception as e:
                print(f"[peer] {code} 실패: {e}")
                return None

        # 모든 동종 종목 병렬 조회
        rows = []
        with ThreadPoolExecutor(max_workers=min(8, len(codes))) as ex:
            futures = [ex.submit(fetch_one, c) for c in codes]
            for f in futures:
                try:
                    r = f.result(timeout=10)
                    if r: rows.append(r)
                except Exception:
                    pass

        # 평균
        valid_per = [r["per"] for r in rows if r["per"] > 0]
        valid_pbr = [r["pbr"] for r in rows if r["pbr"] > 0]
        valid_div = [r["div_yield"] for r in rows if r["div_yield"] > 0]
        avg_per = round(sum(valid_per) / len(valid_per), 2) if valid_per else 0
        avg_pbr = round(sum(valid_pbr) / len(valid_pbr), 2) if valid_pbr else 0
        avg_div = round(sum(valid_div) / len(valid_div), 2) if valid_div else 0

        # 본인 순위 (PER 낮은 순)
        self_row = next((r for r in rows if r["is_self"]), None)
        per_sorted = sorted([r for r in rows if r["per"] > 0], key=lambda r: r["per"])
        per_rank = (per_sorted.index(self_row) + 1) if self_row in per_sorted else 0

        return {
            "available": True,
            "sector": sector,
            "rows": rows,
            "avg_per": avg_per,
            "avg_pbr": avg_pbr,
            "avg_div_yield": avg_div,
            "self_per_rank": per_rank,
            "total_count": len(rows),
        }

    return memoize(f"peer:{stock_code}:{sector}", 600, factory) or {"available": False}
