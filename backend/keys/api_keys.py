# API 키 관리.
# 우선순위: (요청 헤더로 들어온 키) > (OS 환경변수) > (본 파일 기본값)
#
# 요청별 헤더 키 격리: contextvars 사용.
# 미들웨어(main.py)가 요청마다 키를 설정 → 요청 끝나면 자동 클리어.

import os
import contextvars
from typing import Dict

# ---- 기본값 (코드에 박을 수 있음, 보통 비워둠) ----
GEMINI_API_KEY_DEFAULT = ""
ANTHROPIC_API_KEY_DEFAULT = ""
DART_API_KEY_DEFAULT = ""
NAVER_CLIENT_ID_DEFAULT = ""
NAVER_CLIENT_SECRET_DEFAULT = ""

# ---- 설정값 (모듈 레벨, OS 환경변수 우선) ----
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY_DEFAULT)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY_DEFAULT)
DART_API_KEY = os.environ.get("DART_API_KEY", DART_API_KEY_DEFAULT)
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", NAVER_CLIENT_ID_DEFAULT)
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", NAVER_CLIENT_SECRET_DEFAULT)

AI_PROVIDER_DEFAULT = os.environ.get("AI_PROVIDER_DEFAULT", "auto")
DATA_PROVIDER = os.environ.get("DATA_PROVIDER", "real")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ---- 요청별 키 (contextvars) ----
_request_keys: contextvars.ContextVar[Dict[str, str]] = contextvars.ContextVar(
    "request_keys", default={}
)


def set_request_keys(keys: Dict[str, str]):
    """미들웨어에서 호출. 빈 값은 자동으로 무시."""
    cleaned = {k: v for k, v in (keys or {}).items() if v}
    return _request_keys.set(cleaned)


def reset_request_keys(token):
    _request_keys.reset(token)


def get_key(name: str) -> str:
    """요청 헤더 키 > 환경변수 > 빈 문자열 순서로 반환."""
    keys = _request_keys.get()
    v = keys.get(name)
    if v:
        return v
    # 모듈 변수 (환경변수가 이미 반영됨)
    return globals().get(name, "") or ""


def has_gemini() -> bool:
    return bool(get_key("GEMINI_API_KEY"))


def has_claude() -> bool:
    return bool(get_key("ANTHROPIC_API_KEY"))


def has_dart() -> bool:
    return bool(get_key("DART_API_KEY"))


def has_naver() -> bool:
    return bool(get_key("NAVER_CLIENT_ID") and get_key("NAVER_CLIENT_SECRET"))


def resolve_ai_provider(requested: str = "") -> str:
    req = (requested or AI_PROVIDER_DEFAULT or "auto").lower()
    if req == "claude" and has_claude():
        return "claude"
    if req == "gemini" and has_gemini():
        return "gemini"
    if req in ("auto", ""):
        if has_claude():
            return "claude"
        if has_gemini():
            return "gemini"
    if has_claude():
        return "claude"
    if has_gemini():
        return "gemini"
    return ""
