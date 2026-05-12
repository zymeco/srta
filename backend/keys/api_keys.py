# API 키 관리.
# 우선순위: OS 환경변수 > 본 파일의 기본값
# 클라우드 배포(Render 등) 시 환경변수만 등록하면 코드 수정 없이 동작.

import os

# ---- AI 키 ----
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
AI_PROVIDER_DEFAULT = os.environ.get("AI_PROVIDER_DEFAULT", "auto")

# ---- 데이터 공급자 ----
# "mock" | "pykrx" | "real"  (real = pykrx + DART + Naver 통합)
DATA_PROVIDER = os.environ.get("DATA_PROVIDER", "real")

# ---- DART OpenAPI (재무·공시·관리종목 정확도) ----
# 발급: https://opendart.fss.or.kr/  (무료, 1일 1만건)
DART_API_KEY = os.environ.get("DART_API_KEY", "")

# ---- 네이버 검색 API (뉴스 감성) ----
# 발급: https://developers.naver.com/apps/  (무료, 일 25,000건)
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")

# ---- 알림 (선택) ----
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def has_gemini() -> bool:
    return bool(GEMINI_API_KEY)


def has_claude() -> bool:
    return bool(ANTHROPIC_API_KEY)


def has_dart() -> bool:
    return bool(DART_API_KEY)


def has_naver() -> bool:
    return bool(NAVER_CLIENT_ID and NAVER_CLIENT_SECRET)


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
