# 포트폴리오 (보유 종목) 관리.
# SQLite에 저장 + 실시간 시세로 평가손익 계산.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db.database import get_conn
from ..data_provider import naver_finance_provider

router = APIRouter()


class PortfolioItem(BaseModel):
    stock_code: str
    stock_name: str = ""
    avg_price: float
    quantity: float


def _ensure_table():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                stock_code TEXT PRIMARY KEY,
                stock_name TEXT,
                avg_price REAL,
                quantity REAL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


@router.get("/portfolio")
def list_portfolio():
    try:
        _ensure_table()
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM portfolio ORDER BY added_at DESC").fetchall()
            items = []
            total_cost = 0.0
            total_value = 0.0
            for r in rows:
                d = dict(r)
                # 실시간 가격 조회
                quote = naver_finance_provider.get_quote(d["stock_code"]) or {}
                cur = float(quote.get("current_price") or 0)
                d["current_price"] = cur
                cost = (d["avg_price"] or 0) * (d["quantity"] or 0)
                value = cur * (d["quantity"] or 0)
                d["cost"] = round(cost, 2)
                d["value"] = round(value, 2)
                d["pnl"] = round(value - cost, 2)
                d["pnl_rate"] = round((value - cost) / cost * 100, 2) if cost else 0
                d["change_rate"] = quote.get("change_rate") or 0
                items.append(d)
                total_cost += cost
                total_value += value
            total_pnl = total_value - total_cost
            return {
                "items": items,
                "summary": {
                    "total_cost": round(total_cost, 2),
                    "total_value": round(total_value, 2),
                    "total_pnl": round(total_pnl, 2),
                    "total_pnl_rate": round(total_pnl / total_cost * 100, 2) if total_cost else 0,
                    "count": len(items),
                },
            }
    except Exception as e:
        return {"items": [], "summary": {}, "error": str(e)}


@router.post("/portfolio")
def add_or_update(req: PortfolioItem):
    try:
        _ensure_table()
        name = req.stock_name
        if not name:
            quote = naver_finance_provider.get_quote(req.stock_code) or {}
            name = quote.get("stock_name") or req.stock_code
        with get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO portfolio (stock_code, stock_name, avg_price, quantity) VALUES (?, ?, ?, ?)",
                (req.stock_code, name, req.avg_price, req.quantity),
            )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/portfolio/{stock_code}")
def delete_position(stock_code: str):
    try:
        _ensure_table()
        with get_conn() as conn:
            conn.execute("DELETE FROM portfolio WHERE stock_code = ?", (stock_code,))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
