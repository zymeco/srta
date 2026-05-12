# 관심종목 라우트

from fastapi import APIRouter, HTTPException
from ..models.stock_models import WatchlistAddRequest
from ..db.database import get_conn
from ..analysis.final_report_builder import _get_provider

router = APIRouter()


@router.get("/watchlist")
def list_watchlist():
    try:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT stock_code, stock_name, added_at FROM watchlist ORDER BY added_at DESC"
            ).fetchall()
            return {"items": [dict(r) for r in rows]}
    except Exception as e:
        return {"items": [], "error": f"관심종목 조회 실패: {e}"}


@router.post("/watchlist")
def add_watchlist(req: WatchlistAddRequest):
    try:
        name = req.stock_name or ""
        if not name:
            info = _get_provider().get_stock_basic_info(req.stock_code)
            name = info.get("stock_name", "")
        with get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO watchlist (stock_code, stock_name) VALUES (?, ?)",
                (req.stock_code, name),
            )
        return {"ok": True, "stock_code": req.stock_code, "stock_name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관심종목 추가 실패: {e}")


@router.delete("/watchlist/{stock_code}")
def delete_watchlist(stock_code: str):
    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM watchlist WHERE stock_code = ?", (stock_code,))
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관심종목 삭제 실패: {e}")
