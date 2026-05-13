# AI 자연어 분석 모듈.
# Gemini와 Claude를 동시에 지원. httpx로 직접 API 호출 (SDK 미사용 → 가벼움).
# 키가 없으면 예외 없이 None / 안내문을 반환해 앱이 멈추지 않는다.

import json
import httpx
from typing import Dict, Any, Optional

from ..keys.api_keys import (
    get_key,
    has_claude,
    has_gemini,
    resolve_ai_provider,
)


SYSTEM_PROMPT = (
    "당신은 20년 경력의 한국 주식 시장 분석가입니다. "
    "다음 종목 분석 데이터를 검토하고, 일반 투자자가 이해할 수 있는 한국어로 "
    "5~8문장 이내의 핵심 코멘트를 작성하세요. 다음을 반드시 지키세요:\n"
    "1) 리스크가 있으면 가장 먼저 언급한다.\n"
    "2) 추천 투자 포지션(단기/스윙/중기/장기)의 근거를 데이터로 설명한다.\n"
    "3) 매수가/목표가/손절가는 데이터에 제시된 값만 인용한다. 마음대로 새 가격을 만들지 않는다.\n"
    "4) 매수 금지/접근 금지 종목은 신규 진입을 권하지 않는다.\n"
    "5) 마지막 줄에 '본 의견은 투자 추천이 아닌 참고용입니다.' 를 붙인다.\n"
    "6) 마크다운 헤더는 쓰지 말고 평문으로 작성한다."
)


def _build_user_prompt(analysis: Dict[str, Any]) -> str:
    pos = analysis.get("position_analysis", {}) or {}
    strat = analysis.get("strategy", {}) or {}
    summary = analysis.get("summary", {}) or {}
    sw = analysis.get("strong_warning", {}) or {}

    lines = [
        f"종목: {analysis.get('stock_name')} ({analysis.get('stock_code')})",
        f"시장/업종: {analysis.get('market')} / {analysis.get('sector')}",
        f"현재가: {analysis.get('current_price')} ({analysis.get('change_rate')}%)",
        f"시가총액 구분: {analysis.get('market_cap_type')}",
        f"종합 점수: {analysis.get('total_score')} / 100 (등급 {analysis.get('grade')}, 의견 '{analysis.get('final_opinion')}')",
        f"위험 등급: {analysis.get('risk_level')}단계 - {analysis.get('risk_label')}",
        f"경고 배너: {sw.get('warning_title','')} | {sw.get('warning_message','')}",
        f"추천 포지션: {pos.get('recommended_position')} (기간 {pos.get('expected_holding_period')})",
        f"현재 진입 판단: {pos.get('current_entry_status')}",
        f"전략 유형: {strat.get('strategy_type')}",
        f"관심 매수가: {strat.get('buy_zone')}",
        f"1차 목표가: {strat.get('target_price_1')}",
        f"2차 목표가: {strat.get('target_price_2')}",
        f"손절가: {strat.get('stop_loss')}",
        f"손익비: {strat.get('risk_reward_ratio')}",
        f"추격매수 위험도: {strat.get('chasing_risk')}",
        f"긍정 요인: {', '.join(summary.get('positive', []) or [])}",
        f"부정 요인: {', '.join(summary.get('negative', []) or [])}",
        f"주의 요인: {', '.join(summary.get('warning', []) or [])}",
    ]
    flags_on = [k for k, v in (analysis.get("risk_flags") or {}).items() if v]
    if flags_on:
        lines.append(f"감지된 리스크 플래그: {', '.join(flags_on)}")
    return "\n".join(lines)


def _call_claude(prompt: str, timeout: float = 30.0) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": get_key("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 600,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }
    with httpx.Client(timeout=timeout) as c:
        r = c.post(url, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
    parts = data.get("content") or []
    texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
    return "\n".join(t for t in texts if t).strip()


def _call_gemini(prompt: str, timeout: float = 30.0) -> str:
    model = "gemini-2.5-flash"
    api_key = get_key("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800},
    }
    with httpx.Client(timeout=timeout) as c:
        r = c.post(url, json=body)
        r.raise_for_status()
        data = r.json()
    cands = data.get("candidates") or []
    if not cands:
        return ""
    parts = (cands[0].get("content") or {}).get("parts") or []
    return "\n".join(p.get("text", "") for p in parts).strip()


def get_ai_comment(analysis: Dict[str, Any], provider: str = "") -> Dict[str, Any]:
    """AI 코멘트를 반환. provider: 'claude' | 'gemini' | 'auto'.
    실패 시 error 키만 채워서 반환 (앱은 멈추지 않음).
    """
    resolved = resolve_ai_provider(provider)
    if not resolved:
        return {
            "provider": "",
            "comment": "",
            "error": "AI 키가 설정되지 않았습니다. backend/keys/api_keys.py 또는 환경변수에 GEMINI_API_KEY 또는 ANTHROPIC_API_KEY를 설정하세요.",
        }
    prompt = _build_user_prompt(analysis)
    try:
        if resolved == "claude":
            text = _call_claude(prompt)
        else:
            text = _call_gemini(prompt)
        if not text:
            return {"provider": resolved, "comment": "", "error": "AI 응답이 비어 있습니다."}
        return {"provider": resolved, "comment": text, "error": ""}
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        try:
            body = e.response.text[:300]
        except Exception:
            body = ""

        # 사용자 친화적 한국어 메시지
        if status == 429:
            if resolved == "gemini":
                friendly = (
                    "Gemini API 할당량 또는 지출 한도(Spend Cap)를 초과했습니다.\n"
                    "→ https://ai.studio/spend 에서 한도 조정\n"
                    "또는 Claude 키를 등록해 사용하세요."
                )
            else:
                friendly = (
                    "Claude API 사용량/크레딧을 초과했습니다.\n"
                    "→ https://console.anthropic.com 에서 결제/한도 확인하세요."
                )
        elif status in (401, 403):
            friendly = f"AI API 키가 유효하지 않습니다({status}). 설정에서 키를 다시 등록하세요. ({body[:200]})"
        elif status == 400:
            # 400은 모델명/요청 형식 문제. 원본 메시지를 보여줘야 진단 가능
            friendly = f"AI API 오류({status}, {resolved}): {body[:280]}"
        elif status == 404:
            friendly = f"AI 모델을 찾을 수 없습니다({status}). 모델 이름이 변경되었을 수 있습니다. ({body[:200]})"
        else:
            friendly = f"AI API 오류({status}, {resolved}): {body[:200]}"

        return {"provider": resolved, "comment": "", "error": friendly}
    except httpx.ConnectError:
        return {"provider": resolved, "comment": "", "error": "AI 서버에 연결할 수 없습니다. 네트워크 확인 후 다시 시도하세요."}
    except httpx.TimeoutException:
        return {"provider": resolved, "comment": "", "error": "AI 응답이 너무 오래 걸립니다. 잠시 후 다시 시도하세요."}
    except Exception as e:
        return {"provider": resolved, "comment": "", "error": f"AI 호출 실패: {e}"}


def available_providers() -> Dict[str, bool]:
    return {
        "claude": has_claude(),
        "gemini": has_gemini(),
    }
