# 검색/최근 종목 라우트

from fastapi import APIRouter, Query, HTTPException
from ..analysis.final_report_builder import _get_provider
from ..db.database import get_conn

router = APIRouter()


@router.get("/search")
def search(query: str = Query("", description="종목명 또는 종목코드")):
    try:
        provider = _get_provider()
        items = provider.search(query)
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {e}")


@router.get("/recent")
def recent():
    try:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT stock_code, stock_name, MAX(searched_at) AS searched_at "
                "FROM recent_searches GROUP BY stock_code "
                "ORDER BY searched_at DESC LIMIT 20"
            ).fetchall()
            return {"items": [dict(r) for r in rows]}
    except Exception as e:
        return {"items": [], "error": f"최근 검색 조회 실패: {e}"}
