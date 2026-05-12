# 리스크 필터 (배점 10점 + 매수 금지 판정)
#
# 가장 중요한 분석기. 점수가 높아도 치명적 리스크가 있으면 매수 금지로 강제 변경한다.

from typing import Dict, Any
from ..utils.number_utils import round1, clamp


# 치명적 리스크 (접근 금지) 항목
CRITICAL_RISKS = {
    "management_stock": "관리종목",
    "investment_danger": "투자위험 종목",
    "capital_impairment": "자본잠식",
    "delisting_risk": "상장폐지 위험",
    "audit_issue": "감사의견 문제",
    "trading_halt_history": "거래정지 이력",
}

# 강한 주의 (매수 금지) 항목
STRONG_RISKS = {
    "investment_warning": "투자경고",
    "rights_issue": "대규모 유상증자",
    "convertible_bond": "전환사채 물량 부담",
    "warrant": "신주인수권 물량 부담",
    "unfaithful_disclosure": "불성실공시",
    "three_year_loss": "3년 연속 적자",
    "credit_overheat": "신용잔고 과열",
    "short_selling_spike": "공매도 급증",
    "manipulation_pattern": "작전주 의심 패턴",
    "pump_then_volume_drop": "단기 급등 후 거래량 감소",
    "largest_shareholder_change": "최대주주 잦은 변경",
    "low_liquidity": "유동성 부족",
}


def analyze(risk: Dict[str, Any], financial: Dict[str, Any]) -> Dict[str, Any]:
    score = 10.0
    triggered_critical = []
    triggered_strong = []
    flags = {}

    for k, label in CRITICAL_RISKS.items():
        v = bool(risk.get(k, False))
        flags[k] = v
        if v:
            triggered_critical.append(label)
            score -= 4

    for k, label in STRONG_RISKS.items():
        v = bool(risk.get(k, False))
        flags[k] = v
        if v:
            triggered_strong.append(label)
            score -= 2

    if financial.get("capital_impairment"):
        flags["capital_impairment"] = True
        if "자본잠식" not in triggered_critical:
            triggered_critical.append("자본잠식")
            score -= 4

    score = clamp(score, 0, 10)

    # 등급 결정
    if triggered_critical:
        risk_level = 4
        risk_label = "접근 금지"
        is_forbidden = True
    elif len(triggered_strong) >= 2:
        risk_level = 3
        risk_label = "매수 금지"
        is_forbidden = True
    elif len(triggered_strong) == 1:
        risk_level = 2
        risk_label = "강한 주의"
        is_forbidden = False
    elif score < 7:
        risk_level = 1
        risk_label = "주의"
        is_forbidden = False
    else:
        risk_level = 0
        risk_label = "안전"
        is_forbidden = False

    # 경고 메시지
    if risk_level == 4:
        warn_title = "🚨 접근 금지"
        warn_msg = "다음 치명적 리스크가 확인되었습니다: " + ", ".join(triggered_critical)
    elif risk_level == 3:
        warn_title = "🚫 매수 금지"
        warn_msg = "다음 리스크 요인이 다수 발견되어 신규 매수에 적합하지 않습니다: " + ", ".join(triggered_strong)
    elif risk_level == 2:
        warn_title = "⚠️ 강한 주의"
        warn_msg = "다음 리스크 요인이 존재합니다: " + ", ".join(triggered_strong)
    elif risk_level == 1:
        warn_title = "주의"
        warn_msg = "일부 리스크 지표가 평균 이하입니다. 진입 전 추가 점검이 필요합니다."
    else:
        warn_title = ""
        warn_msg = ""

    return {
        "score": round1(score),
        "flags": flags,
        "triggered_critical": triggered_critical,
        "triggered_strong": triggered_strong,
        "risk_level": risk_level,
        "risk_label": risk_label,
        "is_buy_forbidden": is_forbidden,
        "warning_title": warn_title,
        "warning_message": warn_msg,
    }
