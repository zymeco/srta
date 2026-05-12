# 이력 조회 라우트

from fastapi import APIRouter
from ..db.database import get_conn

router = APIRouter()


@router.get("/history/{stock_code}")
def history(stock_code: str):
    try:
        with get_conn() as conn:
            score_rows = conn.execute(
                "SELECT total_score, grade, created_at FROM score_history "
                "WHERE stock_code = ? ORDER BY created_at DESC LIMIT 50",
                (stock_code,),
            ).fetchall()
            risk_rows = conn.execute(
                "SELECT risk_level, risk_label, created_at FROM risk_history "
                "WHERE stock_code = ? ORDER BY created_at DESC LIMIT 50",
                (stock_code,),
            ).fetchall()
            pos_rows = conn.execute(
                "SELECT recommended_position, created_at FROM position_history "
                "WHERE stock_code = ? ORDER BY created_at DESC LIMIT 50",
                (stock_code,),
            ).fetchall()
            return {
                "score_history": [dict(r) for r in score_rows],
                "risk_history": [dict(r) for r in risk_rows],
                "position_history": [dict(r) for r in pos_rows],
            }
    except Exception as e:
        return {"score_history": [], "risk_history": [], "position_history": [], "error": str(e)}
