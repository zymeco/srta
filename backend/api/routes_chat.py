# AI 챗봇 — 종목 분석 결과를 기반으로 사용자 추가 질문에 답함.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

from ..analysis.final_report_builder import build_analysis
from ..analysis import ai_advisor
from ..keys.api_keys import get_key

router = APIRouter()


class ChatRequest(BaseModel):
    stock_code: str
    question: str
    history: List[Dict[str, str]] = []  # [{"role":"user|assistant", "content":"..."}]
    provider: str = "auto"


SYSTEM_PROMPT = (
    "당신은 한국 주식 시장의 전문 분석가입니다. "
    "아래에 주어지는 종목 분석 데이터(JSON)를 근거로 사용자의 질문에 한국어로 답합니다.\n"
    "규칙:\n"
    "1) 데이터에 없는 내용은 추측하지 말고 '데이터에 없습니다'라고 말한다.\n"
    "2) 매수가/목표가/손절가는 데이터 그대로 인용. 새로 만들지 않는다.\n"
    "3) 답변은 5문장 이내로 간결하게.\n"
    "4) 마지막 줄에 '본 답변은 투자 판단 보조 정보입니다.'를 붙인다."
)


def _build_context(analysis):
    return {
        "stock_name": analysis.get("stock_name"),
        "stock_code": analysis.get("stock_code"),
        "current_price": analysis.get("current_price"),
        "change_rate": analysis.get("change_rate"),
        "total_score": analysis.get("total_score"),
        "grade": analysis.get("grade"),
        "final_opinion": analysis.get("final_opinion"),
        "risk_level": analysis.get("risk_level"),
        "risk_label": analysis.get("risk_label"),
        "strategy": analysis.get("strategy"),
        "position_analysis": analysis.get("position_analysis"),
        "summary": analysis.get("summary"),
        "investor_styles": analysis.get("investor_styles", {}).get("styles"),
        "financial": analysis.get("financial_detail"),
        "advanced_metrics": analysis.get("advanced_metrics"),
        "peer_comparison_avg_per": (analysis.get("peer_comparison") or {}).get("avg_per"),
        "consensus_target": (analysis.get("consensus") or {}).get("target_price"),
        "market_state": (analysis.get("market_context") or {}).get("state"),
    }


def _call_claude(messages, system):
    api_key = get_key("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 600,
        "system": system,
        "messages": messages,
    }
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    with httpx.Client(timeout=30.0) as c:
        r = c.post(url, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
    parts = data.get("content") or []
    return "\n".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()


def _call_gemini(messages, system):
    api_key = get_key("GEMINI_API_KEY")
    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    # Gemini는 system을 systemInstruction으로
    gemini_contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        gemini_contents.append({"role": role, "parts": [{"text": m["content"]}]})
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": gemini_contents,
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800},
    }
    with httpx.Client(timeout=30.0) as c:
        r = c.post(url, json=body)
        r.raise_for_status()
        data = r.json()
    cands = data.get("candidates") or []
    if not cands:
        return ""
    parts = (cands[0].get("content") or {}).get("parts") or []
    return "\n".join(p.get("text", "") for p in parts).strip()


@router.post("/chat")
def chat(req: ChatRequest):
    provider = ai_advisor.resolve_ai_provider(req.provider)
    if not provider:
        return {"answer": "", "error": "AI 키가 설정되지 않았습니다. 설정에서 Claude 또는 Gemini 키를 등록하세요."}

    try:
        analysis = build_analysis(req.stock_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 데이터 생성 실패: {e}")

    ctx = _build_context(analysis)
    import json as _json
    context_msg = (
        f"종목 분석 데이터(JSON):\n{_json.dumps(ctx, ensure_ascii=False, indent=2)}\n\n"
        f"사용자 질문: {req.question}"
    )

    # history + 현재 질문 결합
    messages = []
    for h in (req.history or [])[-6:]:  # 최근 6개만
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": context_msg})

    try:
        if provider == "claude":
            answer = _call_claude(messages, SYSTEM_PROMPT)
        else:
            answer = _call_gemini(messages, SYSTEM_PROMPT)
    except httpx.HTTPStatusError as e:
        try:
            body = e.response.text[:300]
        except Exception:
            body = ""
        return {"answer": "", "error": f"AI API 오류({e.response.status_code}): {body}"}
    except Exception as e:
        return {"answer": "", "error": f"AI 호출 실패: {e}"}

    return {"answer": answer, "provider": provider, "error": ""}
