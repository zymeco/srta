# 증권사 컨센서스 (목표가 평균, 투자의견 비율).
# 네이버 종합정보 페이지에서 consensusInfo 추출.

import httpx
from typing import Dict, Any
from ..utils.cache import memoize


def get_consensus(stock_code: str) -> Dict[str, Any]:
    def factory():
        try:
            url = f"https://m.stock.naver.com/api/stock/{stock_code}/integration"
            r = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8.0)
            r.raise_for_status()
            d = r.json()
            ci = d.get("consensusInfo") or {}
            researches = d.get("researches") or []

            target_price = ci.get("consensusTargetPrice") or 0
            current_price = ci.get("currentPrice") or 0
            upside = 0
            if target_price and current_price:
                upside = round((target_price - current_price) / current_price * 100, 2)

            # 의견 분포 (있다면)
            opinion = ci.get("consensusOpinion") or ""

            # 최근 리포트 5개
            recent_reports = []
            for r in researches[:5]:
                recent_reports.append({
                    "broker": r.get("brokerName") or r.get("brokerage") or "",
                    "title": r.get("title", "")[:80],
                    "target_price": r.get("targetPrice") or 0,
                    "opinion": r.get("opinion") or r.get("opinionStr") or "",
                    "date": r.get("publishDate") or "",
                })

            return {
                "available": bool(target_price),
                "target_price": int(target_price) if target_price else 0,
                "current_price": int(current_price) if current_price else 0,
                "upside_pct": upside,
                "opinion": opinion,
                "report_count": len(researches),
                "recent_reports": recent_reports,
            }
        except Exception as e:
            print(f"[consensus] {stock_code} 실패: {e}")
            return {"available": False}

    return memoize(f"consensus:{stock_code}", 600, factory) or {"available": False}
