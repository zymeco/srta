# FastAPI 진입점
#
# 실행: 프로젝트 루트에서
#   python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
#
# 빌드된 frontend/dist 가 있으면 자동으로 SPA를 함께 서빙한다.
# (run_dev.bat 한 번 실행으로 백+프론트가 같은 8000 포트에서 동작)

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from ..db.database import init_db
from . import routes_stock, routes_analysis, routes_watchlist, routes_history, routes_report, routes_ai

app = FastAPI(title="Stock Real Trader Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ---- 요청 헤더 → API 키 contextvar 주입 ----
# 클라이언트가 X-*-Key 헤더로 자신의 API 키를 보내면 그 요청에만 사용.
# 키는 서버 메모리/DB에 저장되지 않는다.
from ..keys import api_keys


@app.middleware("http")
async def inject_user_keys(request, call_next):
    h = request.headers
    keys = {
        "ANTHROPIC_API_KEY":   h.get("x-anthropic-key", ""),
        "GEMINI_API_KEY":      h.get("x-gemini-key", ""),
        "DART_API_KEY":        h.get("x-dart-key", ""),
        "NAVER_CLIENT_ID":     h.get("x-naver-id", ""),
        "NAVER_CLIENT_SECRET": h.get("x-naver-secret", ""),
    }
    token = api_keys.set_request_keys(keys)
    try:
        return await call_next(request)
    finally:
        api_keys.reset_request_keys(token)


@app.on_event("startup")
def startup():
    init_db()
    # 종목 마스터를 백그라운드에서 자동 다운로드 (첫 실행 시 ~10초, 이후는 디스크 캐시)
    try:
        from ..data_provider.pykrx_provider import PykrxProvider
        PykrxProvider()._prefetch_all_tickers_async()
    except Exception as e:
        print(f"[startup] 마스터 prefetch 트리거 실패: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(routes_stock.router, prefix="/api", tags=["stock"])
app.include_router(routes_analysis.router, prefix="/api", tags=["analysis"])
app.include_router(routes_watchlist.router, prefix="/api", tags=["watchlist"])
app.include_router(routes_history.router, prefix="/api", tags=["history"])
app.include_router(routes_report.router, prefix="/api", tags=["report"])
app.include_router(routes_ai.router, prefix="/api", tags=["ai"])


# ----- SPA 정적 서빙 -----
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIST_DIR = os.path.join(ROOT_DIR, "frontend", "dist")
INDEX_HTML = os.path.join(DIST_DIR, "index.html")


if os.path.isdir(DIST_DIR):
    # 정적 자산
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # PWA 루트 파일들 (manifest, service-worker, icons)
    @app.get("/manifest.json")
    def _manifest():
        p = os.path.join(DIST_DIR, "manifest.json")
        return FileResponse(p) if os.path.exists(p) else FileResponse(INDEX_HTML)

    @app.get("/service-worker.js")
    def _sw():
        p = os.path.join(DIST_DIR, "service-worker.js")
        return FileResponse(p, media_type="application/javascript") if os.path.exists(p) else FileResponse(INDEX_HTML)

    icons_dir = os.path.join(DIST_DIR, "icons")
    if os.path.isdir(icons_dir):
        app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")

    # SPA fallback: /api, /health 이외의 GET 은 모두 index.html
    @app.get("/{full_path:path}")
    def spa(full_path: str, request: Request):
        if full_path.startswith("api") or full_path.startswith("health"):
            # 라우터에 없는 API 경로는 그대로 404
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(INDEX_HTML)
