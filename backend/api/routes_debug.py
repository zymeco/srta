# 시세 소스 진단 라우트.
# Render 등 클라우드 환경에서 어떤 외부 API가 막혀 있는지 즉시 확인.

from fastapi import APIRouter
from ..data_provider import naver_finance_provider, yfinance_provider
from ..data_provider.pykrx_provider import PykrxProvider

router = APIRouter()


@router.get("/debug/source/{stock_code}")
def debug_source(stock_code: str):
    out = {"stock_code": stock_code}

    # 1. Naver polling
    try:
        q = naver_finance_provider.get_quote(stock_code)
        out["naver_quote"] = {"ok": bool(q), "data": q}
    except Exception as e:
        out["naver_quote"] = {"ok": False, "error": str(e)}

    # 2. Naver fchart
    try:
        o = naver_finance_provider.get_daily_ohlcv(stock_code, count=10)
        out["naver_ohlcv"] = {"ok": bool(o), "count": len(o or []), "last": (o or [None])[-1] if o else None}
    except Exception as e:
        out["naver_ohlcv"] = {"ok": False, "error": str(e)}

    # 3. yfinance
    try:
        yq = yfinance_provider.get_quote(stock_code)
        out["yfinance_quote"] = {"ok": bool(yq), "price": yq.get("current_price") if yq else None, "symbol": yq.get("_symbol") if yq else None}
    except Exception as e:
        out["yfinance_quote"] = {"ok": False, "error": str(e)}

    # 4. pykrx 가용성
    try:
        pk = PykrxProvider()
        out["pykrx_available"] = pk.available
        try:
            info = pk.get_stock_basic_info(stock_code)
            out["pykrx_basic"] = {"price": info.get("current_price"), "name": info.get("stock_name")}
        except Exception as e:
            out["pykrx_basic"] = {"error": str(e)}
    except Exception as e:
        out["pykrx_available"] = False
        out["pykrx_error"] = str(e)

    return out
