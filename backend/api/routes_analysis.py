# 종목 분석 라우트

from fastapi import APIRouter, HTTPException
from ..analysis.final_report_builder import build_analysis
from ..db.database import get_conn

router = APIRouter()


@router.get("/analyze/{stock_code}")
def analyze(stock_code: str):
    try:
        result = build_analysis(stock_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {e}")

    # DB 기록 (실패해도 분석 결과는 반환)
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO recent_searches (stock_code, stock_name) VALUES (?, ?)",
                (result["stock_code"], result["stock_name"]),
            )
            conn.execute(
                "INSERT INTO analysis_history (stock_code, stock_name, total_score, grade, final_opinion) "
                "VALUES (?, ?, ?, ?, ?)",
                (result["stock_code"], result["stock_name"], result["total_score"],
                 result["grade"], result["final_opinion"]),
            )
            conn.execute(
                "INSERT INTO score_history (stock_code, total_score, grade) VALUES (?, ?, ?)",
                (result["stock_code"], result["total_score"], result["grade"]),
            )
            conn.execute(
                "INSERT INTO risk_history (stock_code, risk_level, risk_label) VALUES (?, ?, ?)",
                (result["stock_code"], result["risk_level"], result["risk_label"]),
            )
            conn.execute(
                "INSERT INTO position_history (stock_code, recommended_position) VALUES (?, ?)",
                (result["stock_code"], result["position_analysis"]["recommended_position"]),
            )
    except Exception as e:
        print(f"[DB] 기록 실패(무시): {e}")

    return result
