# 리포트 데이터 라우트

from fastapi import APIRouter, HTTPException
from ..analysis.final_report_builder import build_analysis
from ..report.report_builder import build_report_data
from ..db.database import get_conn

router = APIRouter()


@router.get("/report/{stock_code}")
def report(stock_code: str):
    try:
        analysis = build_analysis(stock_code)
        data = build_report_data(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리포트 생성 실패: {e}")

    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO report_history (stock_code, stock_name) VALUES (?, ?)",
                (data["stock_code"], data["stock_name"]),
            )
    except Exception as e:
        print(f"[DB] 리포트 이력 기록 실패(무시): {e}")

    return data
