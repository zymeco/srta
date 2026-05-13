# 텔레그램 알림 라우트.

from fastapi import APIRouter
from pydantic import BaseModel
from ..analysis import telegram_notify
from ..analysis.final_report_builder import build_analysis
from ..keys.api_keys import get_key

router = APIRouter()


class NotifyRequest(BaseModel):
    message: str = ""
    stock_code: str = ""  # 비어 있으면 message만 발송


@router.get("/notify/status")
def status():
    return {
        "configured": bool(get_key("TELEGRAM_BOT_TOKEN") and get_key("TELEGRAM_CHAT_ID")),
    }


@router.post("/notify/test")
def test_notify():
    return telegram_notify.send("🔔 SRTA 테스트 알림\n연결이 정상입니다.")


@router.post("/notify/send")
def send(req: NotifyRequest):
    text = req.message
    if req.stock_code and not text:
        try:
            r = build_analysis(req.stock_code)
            sw = r.get("strong_warning") or {}
            text = (
                f"📊 *{r['stock_name']}* ({r['stock_code']})\n"
                f"현재가: {r['current_price']:,}원 ({r['change_rate']:+.2f}%)\n"
                f"점수: *{r['total_score']}* / 등급 *{r['grade']}* / {r['final_opinion']}\n"
                f"위험: {r['risk_label']} ({r['risk_level']}단계)\n"
            )
            if sw.get("warning_title"):
                text += f"\n{sw['warning_title']}: {sw['warning_message']}"
            text += f"\n\n_매수가_ {r['strategy']['buy_zone']}\n_목표가_ {r['strategy'].get('target_price_1') or '-'}\n_손절가_ {r['strategy'].get('stop_loss') or '-'}"
        except Exception as e:
            text = f"분석 실패: {e}"

    if not text:
        return {"ok": False, "error": "보낼 메시지가 없습니다."}
    return telegram_notify.send(text)
