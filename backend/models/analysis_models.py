# 분석 결과 Pydantic 모델 (응답 구조 문서화용)

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class StrongWarning(BaseModel):
    is_buy_forbidden: bool = False
    warning_level: str = "안전"
    warning_title: str = ""
    warning_message: str = ""


class Summary(BaseModel):
    positive: List[str] = []
    negative: List[str] = []
    warning: List[str] = []


class Strategy(BaseModel):
    buy_zone: Any = ""
    target_price_1: Any = None
    target_price_2: Any = None
    stop_loss: Any = None
    risk_reward_ratio: Any = None
    target_return_rate: Any = None
    stop_loss_rate: Any = None
    strategy_type: str = ""
    chasing_risk: str = ""


class PositionAnalysis(BaseModel):
    recommended_position: str = ""
    expected_holding_period: str = ""
    current_entry_status: str = ""
    best_profit_strategy: str = ""
    position_scores: Dict[str, float] = {}
    reason: List[str] = []


class AnalysisResponse(BaseModel):
    stock_name: str
    stock_code: str
    market: str = "KOSPI"
    sector: str = ""
    current_price: float = 0
    change_rate: float = 0
    market_cap: int = 0
    market_cap_type: str = "mid"
    total_score: float = 0
    grade: str = "C"
    final_opinion: str = ""
    risk_level: int = 0
    risk_label: str = "안전"
    strong_warning: StrongWarning
    summary: Summary
    scores: Dict[str, float]
    position_analysis: PositionAnalysis
    strategy: Strategy
    risk_flags: Dict[str, bool]
    charts: Dict[str, Any]
    final_comment: str = ""
    disclaimer: str = "본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다."
