# PDF 리포트용 데이터 가공기.
# MVP는 프론트에서 화면 캡처 방식 PDF 생성. 백엔드는 데이터 정리만 제공.

from typing import Dict, Any
from .report_template import PDF_TEMPLATE_DISCLAIMER


def build_report_data(analysis: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": "Stock Real Trader Analyzer 분석 리포트",
        "stock_name": analysis.get("stock_name"),
        "stock_code": analysis.get("stock_code"),
        "current_price": analysis.get("current_price"),
        "total_score": analysis.get("total_score"),
        "grade": analysis.get("grade"),
        "final_opinion": analysis.get("final_opinion"),
        "strong_warning": analysis.get("strong_warning"),
        "position_analysis": analysis.get("position_analysis"),
        "strategy": analysis.get("strategy"),
        "summary": analysis.get("summary"),
        "scores": analysis.get("scores"),
        "risk_flags": analysis.get("risk_flags"),
        "final_comment": analysis.get("final_comment"),
        "disclaimer": PDF_TEMPLATE_DISCLAIMER,
        "generated_at": analysis.get("generated_at"),
    }
