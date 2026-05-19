# 최종 분석 응답 빌더.
# 각 analyzer 결과를 모아서 프론트 API 응답 JSON으로 변환한다.

from typing import Dict, Any
from datetime import datetime

from ..data_provider.mock_provider import MockProvider
from ..keys.api_keys import DATA_PROVIDER
from . import (
    financial_analyzer,
    growth_analyzer,
    valuation_analyzer,
    technical_analyzer,
    volume_analyzer,
    supply_analyzer,
    news_analyzer,
    risk_analyzer,
    position_analyzer,
    score_engine,
    strategy_engine,
    advanced_metrics,
    investor_style,
    market_context,
    peer_comparison,
    consensus,
    candle_patterns,
    backtest,
    macro,
    earnings,
)


def _summary(positive_pool, negative_pool, warning_pool):
    def top(arr, n=3):
        seen = []
        for x in arr:
            if x and x not in seen:
                seen.append(x)
            if len(seen) >= n:
                break
        while len(seen) < n:
            seen.append("-")
        return seen

    return {
        "positive": top(positive_pool),
        "negative": top(negative_pool),
        "warning": top(warning_pool),
    }


def _one_liner(stock_name, scored, strat, risk, styles, adv, fin, market_ctx=None):
    """한 줄 결론 — 핵심만 추출."""
    if risk.get("is_buy_forbidden"):
        return f"❌ 매수 금지: {risk.get('warning_message', '')[:60]}"

    opinion = scored.get("final_opinion", "")
    style_lbl = styles.get("best_style_label", "")
    style_score = styles.get("best_style_score", 0)
    chasing = strat.get("chasing_risk", "")

    parts = []

    # 시장 상태 우선 표시
    if market_ctx:
        m_state = market_ctx.get("state", "")
        if m_state in ("강한 하락장", "급락 / 강한 하락"):
            parts.append(f"⚠ 시장 {m_state}")
        elif m_state in ("하락장", "조정 중"):
            parts.append(f"시장 {m_state}")
        elif m_state in ("강한 상승장",):
            parts.append(f"시장 {m_state}")

    per = fin.get("forward_per") or fin.get("per") or 0
    peg = adv.get("peg") or 0
    near_high = adv.get("near_high_pct") or 0

    if 0 < per < 10:
        parts.append(f"PER {per:.1f}배 매우 저평가")
    elif 0 < per < 15:
        parts.append(f"PER {per:.1f}배 저평가")
    elif per > 30:
        parts.append(f"PER {per:.1f}배 고평가")

    if 0 < peg < 1:
        parts.append(f"PEG {peg} 성장가치")

    if near_high >= 95:
        parts.append("52주 신고가 근접")
    elif near_high <= 60:
        parts.append("52주 저점 부근")

    if styles.get("best_style") == "momentum" and style_score >= 70:
        parts.append("강한 모멘텀")
    if styles.get("best_style") == "graham" and style_score >= 70:
        parts.append("가치주 적합")
    if styles.get("best_style") == "buffett" and style_score >= 70:
        parts.append("퀄리티 우수")

    if chasing in ("높음", "매우 높음"):
        parts.append(f"추격매수 {chasing}")

    parts_str = " · ".join(parts) if parts else style_lbl
    return f"{opinion} ({parts_str})"


def _final_comment(stock_name, opinion, position, strategy, risk):
    if risk.get("is_buy_forbidden"):
        return (
            f"{stock_name}은(는) 현재 치명적 리스크가 확인되어 신규 매수에 적합하지 않습니다. "
            f"리스크 해소가 확인되기 전까지는 관찰만 권장됩니다."
        )
    rec = position.get("recommended_position", "스윙")
    st = strategy.get("strategy_type", "관찰")
    return (
        f"{stock_name}은(는) 현재 종합 의견 '{opinion}'으로 분류되며, "
        f"가장 유리한 투자 방식은 '{rec}' 입니다. 매매 전략은 '{st}' 방향이 적합하며, "
        f"손익비 {strategy.get('risk_reward_ratio')}, "
        f"추격매수 위험도는 '{strategy.get('chasing_risk')}' 입니다."
    )


def get_provider():
    """설정값에 따라 데이터 프로바이더 선택.
    real = pykrx + DART + Naver 통합 (키 있는 만큼 실데이터, 없는 영역은 Mock 폴백)
    pykrx = 시세/수급만 실데이터, 재무/뉴스는 Mock
    mock = 전부 더미
    """
    mode = (DATA_PROVIDER or "real").lower()
    if mode == "real":
        try:
            from ..data_provider.real_provider import RealProvider
            return RealProvider()
        except Exception as e:
            print(f"[provider] real 로드 실패 → Mock 사용: {e}")
    if mode == "pykrx":
        try:
            from ..data_provider.pykrx_provider import PykrxProvider
            p = PykrxProvider()
            if p.available:
                return p
            print("[provider] pykrx 미설치 → Mock 사용")
        except Exception as e:
            print(f"[provider] pykrx 로드 실패 → Mock 사용: {e}")
    return MockProvider()


# 하위 호환 alias (외부에서 _get_provider 로 import 하는 곳이 있음)
_get_provider = get_provider


def build_analysis(stock_code: str) -> Dict[str, Any]:
    provider = get_provider()

    basic = provider.get_stock_basic_info(stock_code)
    price = provider.get_price_history(stock_code)
    fin = provider.get_financial_data(stock_code)
    sup = provider.get_supply_data(stock_code)
    news_raw = provider.get_news_data(stock_code)
    risk_raw = provider.get_risk_data(stock_code)

    fa = financial_analyzer.analyze(fin)
    ga = growth_analyzer.analyze(fin)
    va = valuation_analyzer.analyze(fin)
    ta = technical_analyzer.analyze(price, basic.get("current_price", 0))
    vola = volume_analyzer.analyze(price, basic)
    sa = supply_analyzer.analyze(sup)
    na = news_analyzer.analyze(news_raw)
    ra = risk_analyzer.analyze(risk_raw, fin)

    scored = score_engine.compute(
        fa, ga, va, ta, vola, sa, na, ra,
        market_cap_type=basic.get("market_cap_type", "mid"),
        sector=basic.get("sector", ""),
        themes=(news_raw.get("themes") if isinstance(news_raw, dict) else []) or [],
        financial_raw=fin,
    )

    # 고급 지표 (MDD/ATR/OBV/PEG/모멘텀/변동성)
    adv = advanced_metrics.compute_advanced(price, basic, fin)

    # 투자 스타일 점수 (그레이엄/버핏/린치/모멘텀)
    styles = investor_style.compute_all_styles(fin, ta, vola, adv, sup)

    # 시장 컨텍스트
    market_ctx = market_context.get_market_context(basic.get("market", "KOSPI"))

    # 동종 업종 비교
    peer = peer_comparison.get_peer_comparison(stock_code, basic.get("sector", ""))

    # 증권사 컨센서스
    cons = consensus.get_consensus(stock_code)

    # 캔들 패턴
    candles = candle_patterns.analyze(price)

    # 백테스트
    bt = backtest.compute(price)

    # 매크로 지표 (자주 안 바뀌니 캐시 됨)
    macro_data = macro.get_macro()
    macro_text = macro.get_macro_context_text(macro_data)

    # 실적 캘린더
    earnings_info = earnings.get_earnings_info(stock_code)

    pa = position_analyzer.analyze(basic, ta, vola, sa, fin, na, ra)
    strat = strategy_engine.compute(basic, ta, ra, pa, financial=fin)

    # ---- 시장 상태에 따른 점수·전략 보정 ----
    sector_cat = scored.get("sector_category", "default")
    market_score = market_ctx.get("score", 50)
    adjust = market_context.market_adjustment_multiplier(market_score, sector_cat)

    # 점수 보정 (소수점 1자리)
    orig_score = scored["total_score"]
    adj_score = max(0, min(100, orig_score * adjust["score"]))
    scored["market_adjustment"] = {
        "market_state": market_ctx.get("state"),
        "market_score": market_score,
        "score_multiplier": adjust["score"],
        "chasing_multiplier": adjust["chasing_risk"],
        "before_adjust": orig_score,
        "after_adjust": round(adj_score, 1),
    }
    scored["total_score"] = round(adj_score, 1)
    # 등급/의견 재산정
    ts = scored["total_score"]
    if ts >= 90: scored["grade"], scored["final_opinion"] = "S", "강력 관심"
    elif ts >= 80: scored["grade"], scored["final_opinion"] = "A", "관심매수"
    elif ts >= 70: scored["grade"], scored["final_opinion"] = "B", "관찰"
    elif ts >= 60: scored["grade"], scored["final_opinion"] = "C", "보류"
    else: scored["grade"], scored["final_opinion"] = "D", "제외"

    # 추격매수 위험도 보정 (하락장에서는 위험도 ↑, 상승장에서는 ↓)
    chase_mult = adjust["chasing_risk"]
    if chase_mult != 1.0:
        levels = ["낮음", "중간", "높음", "매우 높음"]
        cur = strat.get("chasing_risk", "낮음")
        if cur in levels:
            idx = levels.index(cur)
            if chase_mult > 1.1:   # 위험 한 단계 ↑
                idx = min(len(levels) - 1, idx + 1)
            elif chase_mult < 0.85:  # 위험 한 단계 ↓
                idx = max(0, idx - 1)
            strat["chasing_risk"] = levels[idx]

    # 의견은 리스크 우선 원칙으로 강제 변경
    if ra.get("risk_level") == 4:
        scored["final_opinion"] = "접근 금지"
    elif ra.get("risk_level") == 3:
        scored["final_opinion"] = "매수 금지"
    elif ra.get("risk_level") == 2 and scored["final_opinion"] in ("관심매수", "강력 관심"):
        scored["final_opinion"] = "관찰"

    # 강력 경고 배너
    if ra.get("risk_level") >= 2:
        strong_warning = {
            "is_buy_forbidden": ra.get("is_buy_forbidden", False),
            "warning_level": ra.get("risk_label"),
            "warning_title": ra.get("warning_title", ""),
            "warning_message": ra.get("warning_message", ""),
        }
    elif strat.get("chasing_risk") in ("높음", "매우 높음"):
        strong_warning = {
            "is_buy_forbidden": False,
            "warning_level": "주의",
            "warning_title": "⚠️ 추격매수 주의",
            "warning_message": "단기 과열 구간으로 추격매수 위험이 큽니다. 눌림목 확인 후 진입을 권장합니다.",
        }
    else:
        strong_warning = {
            "is_buy_forbidden": False,
            "warning_level": "안전",
            "warning_title": "",
            "warning_message": "",
        }

    # 요약
    pos_pool = (
        fa["reasons"] + ga["reasons"] + va["reasons"] +
        ta["reasons"] + vola["reasons"] + sa["reasons"] + na["reasons"]
    )
    neg_pool = (
        fa["warnings"] + ga["warnings"] + va["warnings"] +
        sa["warnings"] + na["warnings"]
    )
    warn_pool = ta["warnings"] + vola["warnings"] + [
        f"리스크: {x}" for x in ra.get("triggered_strong", []) + ra.get("triggered_critical", [])
    ]
    summary = _summary(pos_pool, neg_pool, warn_pool)

    # 차트 데이터
    charts = {
        "price": price.get("prices", []),
        "moving_average": [
            {
                "date": p["date"],
                "close": p["close"],
                "ma5": price["ma5"][i],
                "ma20": price["ma20"][i],
                "ma60": price["ma60"][i],
                "ma120": price["ma120"][i],
            }
            for i, p in enumerate(price.get("prices", []))
        ],
        "volume": price.get("volumes", []),
        "rsi": [
            {"date": price["prices"][i]["date"], "rsi": price["rsi"][i]}
            for i in range(len(price.get("prices", [])))
            if price["rsi"][i] is not None
        ],
        "supply": sup.get("series", []),
        "financial": [
            {"name": "부채비율", "value": fin.get("debt_ratio", 0)},
            {"name": "유동비율", "value": fin.get("current_ratio", 0)},
            {"name": "ROE", "value": fin.get("roe", 0)},
            {"name": "영업이익률", "value": fin.get("operating_margin", 0)},
        ],
        "growth": fin.get("revenue_trend", []),
        "news_sentiment": [
            {"name": "긍정", "value": news_raw["sentiment_counts"].get("positive", 0)},
            {"name": "중립", "value": news_raw["sentiment_counts"].get("neutral", 0)},
            {"name": "부정", "value": news_raw["sentiment_counts"].get("negative", 0)},
        ],
    }

    risk_flags = {
        "management_stock": bool(ra["flags"].get("management_stock")),
        "investment_warning": bool(ra["flags"].get("investment_warning")),
        "investment_danger": bool(ra["flags"].get("investment_danger")),
        "capital_impairment": bool(ra["flags"].get("capital_impairment")),
        "trading_halt_history": bool(ra["flags"].get("trading_halt_history")),
        "rights_issue": bool(ra["flags"].get("rights_issue")),
        "convertible_bond": bool(ra["flags"].get("convertible_bond")),
        "warrant": bool(ra["flags"].get("warrant")),
        "audit_issue": bool(ra["flags"].get("audit_issue")),
        "delisting_risk": bool(ra["flags"].get("delisting_risk")),
        "credit_overheat": bool(ra["flags"].get("credit_overheat")),
        "short_selling_spike": bool(ra["flags"].get("short_selling_spike")),
        "unfaithful_disclosure": bool(ra["flags"].get("unfaithful_disclosure")),
        "three_year_loss": bool(ra["flags"].get("three_year_loss")),
        "low_liquidity": bool(ra["flags"].get("low_liquidity")),
        "manipulation_pattern": bool(ra["flags"].get("manipulation_pattern")),
        "pump_then_volume_drop": bool(ra["flags"].get("pump_then_volume_drop")),
        "largest_shareholder_change": bool(ra["flags"].get("largest_shareholder_change")),
    }

    final_comment = _final_comment(basic["stock_name"], scored["final_opinion"], pa, strat, ra)
    one_liner = _one_liner(basic["stock_name"], scored, strat, ra, styles, adv, fin, market_ctx)

    return {
        "stock_name": basic["stock_name"],
        "stock_code": basic["stock_code"],
        "market": basic["market"],
        "sector": basic["sector"],
        "current_price": basic["current_price"],
        "change_rate": basic["change_rate"],
        "volume": basic["volume"],
        "trading_value": basic["trading_value"],
        "market_cap": basic["market_cap"],
        "market_cap_type": basic["market_cap_type"],
        "high_52w": basic["high_52w"],
        "low_52w": basic["low_52w"],
        "total_score": scored["total_score"],
        "grade": scored["grade"],
        "final_opinion": scored["final_opinion"],
        "sector_category": scored.get("sector_category", "default"),
        "score_bonus": scored.get("bonus", {}),
        "risk_level": ra["risk_level"],
        "risk_label": ra["risk_label"],
        "strong_warning": strong_warning,
        "summary": summary,
        "scores": scored["scores"],
        "position_analysis": pa,
        "strategy": strat,
        "risk_flags": risk_flags,
        "financial_detail": {
            "debt_ratio": fin.get("debt_ratio"),
            "current_ratio": fin.get("current_ratio"),
            "quick_ratio": fin.get("quick_ratio"),
            "retained_ratio": fin.get("retained_ratio"),
            "operating_cash_flow": fin.get("operating_cash_flow"),
            "interest_coverage": fin.get("interest_coverage"),
            "roe": fin.get("roe"),
            "operating_margin": fin.get("operating_margin"),
            "revenue_growth": fin.get("revenue_growth"),
            "operating_growth": fin.get("operating_growth"),
            "net_income_growth": fin.get("net_income_growth"),
            "eps_growth": fin.get("eps_growth"),
            "per": fin.get("per"),
            "forward_per": fin.get("forward_per"),
            "pbr": fin.get("pbr"),
            "psr": fin.get("psr"),
            "ev_ebitda": fin.get("ev_ebitda"),
            "sector_per": fin.get("sector_per"),
            "eps": fin.get("eps"),
            "forward_eps": fin.get("forward_eps"),
            "bps": fin.get("bps"),
            "dividend_yield": fin.get("dividend_yield"),
            "foreign_ratio": fin.get("foreign_ratio"),
        },
        "technical_detail": {
            "ma5": ta["ma5"], "ma20": ta["ma20"], "ma60": ta["ma60"], "ma120": ta["ma120"],
            "rsi": ta["rsi"], "bb_upper": ta["bb_upper"], "bb_lower": ta["bb_lower"],
            "support": ta["support"], "resistance": ta["resistance"],
        },
        "volume_detail": {
            "today": basic.get("volume"),
            "avg_20d": vola.get("avg_20d"),
            "ratio": vola.get("ratio"),
        },
        "supply_detail": {
            "foreign_5d": sup.get("foreign_5d"),
            "foreign_20d": sup.get("foreign_20d"),
            "institution_5d": sup.get("institution_5d"),
            "institution_20d": sup.get("institution_20d"),
            "individual_20d": sup.get("individual_20d"),
            "program": sup.get("program"),
            "short_selling_ratio": sup.get("short_selling_ratio"),
            "credit_balance_ratio": sup.get("credit_balance_ratio"),
        },
        "news": news_raw,
        "charts": charts,
        "final_comment": final_comment,
        "one_liner": one_liner,
        "investor_styles": styles,
        "advanced_metrics": adv,
        "market_context": market_ctx,
        "market_adjustment": scored.get("market_adjustment"),
        "peer_comparison": peer,
        "consensus": cons,
        "candle_patterns": candles,
        "backtest": bt,
        "macro": macro_data,
        "macro_text": macro_text,
        "earnings": earnings_info,
        "disclaimer": "본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다.",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
