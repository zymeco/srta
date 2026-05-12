# 종목 분석 라우트

from fastapi import APIRouter, HTTPException
from ..analysis.final_report_builder import build_analysis
from ..data_provider.real_provider import NoMarketDataError
from ..db.database import get_conn

router = APIRouter()


@router.get("/analyze/{stock_code}")
def analyze(stock_code: str):
    try:
        result = build_analysis(stock_code)
    except NoMarketDataError as e:
        # 실시간 시세를 못 받음 — Mock으로 가짜 데이터 주지 않고 명확히 503
        raise HTTPException(
            status_code=503,
            detail=(
                "실시간 시세를 가져올 수 없습니다. "
                "잠시 후 다시 시도하거나 종목코드를 확인해주세요. "
                "(원인: 외부 시세 서버 일시 장애 또는 잘못된 종목코드)"
            ),
        )
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
