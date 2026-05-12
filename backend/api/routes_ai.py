# AI 자연어 분석 라우트.
# 사용 가능한 공급자 조회 / 분석 코멘트 요청.

from fastapi import APIRouter, Query, HTTPException
from ..analysis.final_report_builder import build_analysis
from ..analysis import ai_advisor
from ..keys.api_keys import has_dart, has_naver, DATA_PROVIDER, resolve_ai_provider

router = APIRouter()


@router.get("/ai/providers")
def providers():
    """현재 키가 설정된 공급자 목록을 반환."""
    return {
        "available": ai_advisor.available_providers(),
    }


@router.get("/data/status")
def data_status():
    """데이터 공급자 키 상태."""
    return {
        "data_provider": DATA_PROVIDER,
        "dart": has_dart(),
        "naver_news": has_naver(),
    }


@router.get("/ai/advise/{stock_code}")
def advise(stock_code: str, provider: str = Query("auto", description="claude | gemini | auto")):
    # 키가 하나도 없으면 분석을 돌리지 않고 즉시 안내 (비용 절약 + 빠른 응답)
    if not ai_advisor.resolve_ai_provider(provider):
        return {
            "stock_code": stock_code,
            "stock_name": "",
            "provider": "",
            "comment": "",
            "error": "AI 키가 설정되지 않았습니다. backend/keys/api_keys.py 또는 환경변수에 GEMINI_API_KEY 또는 ANTHROPIC_API_KEY를 설정하세요.",
        }
    try:
        analysis = build_analysis(stock_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 데이터 생성 실패: {e}")

    result = ai_advisor.get_ai_comment(analysis, provider=provider)
    return {
        "stock_code": stock_code,
        "stock_name": analysis.get("stock_name"),
        **result,
    }
