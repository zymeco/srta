# 종목 마스터 다운로드 모듈.
# 우선순위: KRX 직접 호출 → 네이버 금융 크롤링 → 빈 결과
# 받은 결과는 디스크 캐시에 저장돼서 다음 실행부터는 즉시 사용.

import os
import io
import re
import csv
import json
import httpx
from typing import List, Dict


KRX_OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
KRX_CSV_URL = "http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd"
KRX_REFERER = "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd"

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _fetch_market(mkt_id: str) -> List[Dict[str, str]]:
    """mkt_id: STK(코스피) | KSQ(코스닥) | KNX(코넥스)."""
    market_label = {"STK": "KOSPI", "KSQ": "KOSDAQ", "KNX": "KONEX"}.get(mkt_id, mkt_id)

    otp_payload = {
        "mktId": mkt_id,
        "share": "1",
        "csvxls_isNo": "false",
        "name": "fileDown",
        "url": "dbms/MDC/STAT/standard/MDCSTAT01901",
    }
    headers_common = {
        "User-Agent": _UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    headers_otp = {
        **headers_common,
        "Referer": KRX_REFERER,
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://data.krx.co.kr",
    }

    with httpx.Client(timeout=20.0, follow_redirects=True, headers=headers_common) as c:
        # 1) 세션 쿠키 발급을 위해 메인 페이지 먼저 방문 (KRX 봇 차단 우회)
        try:
            c.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201")
        except Exception:
            pass

        r = c.post(KRX_OTP_URL, data=otp_payload, headers=headers_otp)
        r.raise_for_status()
        otp = r.text.strip()
        if not otp or len(otp) < 20 or "LOGOUT" in otp.upper():
            raise RuntimeError(f"OTP 발급 실패(응답={otp[:40]!r})")

        headers_csv = {
            **headers_common,
            "Referer": KRX_REFERER,
            "Origin": "http://data.krx.co.kr",
        }
        r2 = c.post(KRX_CSV_URL, data={"code": otp}, headers=headers_csv)
        r2.raise_for_status()
        raw = r2.content
        if len(raw) < 100:
            raise RuntimeError(f"CSV 응답 비정상(size={len(raw)})")

    # EUC-KR 또는 UTF-8 자동 디코드
    text = None
    for enc in ("euc-kr", "cp949", "utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc)
            break
        except Exception:
            continue
    if text is None:
        raise RuntimeError("CSV 디코딩 실패")

    reader = csv.DictReader(io.StringIO(text))
    out: List[Dict[str, str]] = []
    for row in reader:
        # KRX CSV 컬럼은 시기에 따라 한글이 약간 다를 수 있어 fallback 다중 매핑
        code = (
            row.get("단축코드") or row.get("종목코드") or row.get("표준코드")
            or row.get("티커") or ""
        ).strip()
        name = (
            row.get("한글 종목명") or row.get("한글종목명") or row.get("종목명")
            or row.get("한글 종목약명") or ""
        ).strip()
        if not code or not name:
            continue
        if len(code) > 6 and code.isdigit():
            # 표준코드(12자리)일 경우 마지막 6자리
            code = code[-6:]
        if len(code) != 6:
            continue
        out.append({
            "stock_code": code,
            "stock_name": name,
            "market": market_label,
            "sector": "",
        })
    return out


def fetch_all_krx_tickers() -> List[Dict[str, str]]:
    """KRX 직접 호출. 실패 시 빈 리스트."""
    result: List[Dict[str, str]] = []
    seen = set()
    for mkt in ("STK", "KSQ"):
        try:
            items = _fetch_market(mkt)
            for it in items:
                if it["stock_code"] in seen:
                    continue
                seen.add(it["stock_code"])
                result.append(it)
            print(f"[KRX] {mkt} 종목 {len(items)}개 수신")
        except Exception as e:
            print(f"[KRX] {mkt} 다운로드 실패: {e}")
    return result


# ---------- 네이버 금융 크롤링 (가장 안정적 폴백) ----------

NAVER_SISE_URL = "https://finance.naver.com/sise/sise_market_sum.naver"
# /item/main.naver?code=005930">삼성전자</a>
_NAVER_RE = re.compile(r'/item/main\.naver\?code=(\d{6})[^>]*>([^<]+)</a>')


def _fetch_naver_market(sosok: int, market_label: str, max_pages: int = 60) -> List[Dict[str, str]]:
    """sosok: 0=KOSPI, 1=KOSDAQ. 페이지를 끝까지 순회."""
    out: List[Dict[str, str]] = []
    seen = set()
    headers = {
        "User-Agent": _UA,
        "Referer": "https://finance.naver.com/",
        "Accept-Language": "ko-KR,ko;q=0.9",
    }
    with httpx.Client(timeout=10.0, headers=headers, follow_redirects=True) as c:
        for page in range(1, max_pages + 1):
            try:
                r = c.get(NAVER_SISE_URL, params={"sosok": sosok, "page": page})
                r.raise_for_status()
                # 네이버 금융은 EUC-KR
                text = r.content.decode("euc-kr", errors="replace")
            except Exception as e:
                print(f"[Naver] {market_label} p{page} 실패: {e}")
                break

            found = _NAVER_RE.findall(text)
            new_count = 0
            for code, name in found:
                name = name.strip()
                if not code or not name or code in seen:
                    continue
                seen.add(code)
                out.append({
                    "stock_code": code,
                    "stock_name": name,
                    "market": market_label,
                    "sector": "",
                })
                new_count += 1
            if new_count == 0:
                # 이 페이지에서 새로 추가된 게 없으면 끝
                break
    return out


def fetch_all_naver_tickers() -> List[Dict[str, str]]:
    """네이버 금융 시가총액 페이지에서 KOSPI+KOSDAQ 전체 종목 수집."""
    result: List[Dict[str, str]] = []
    seen = set()
    for sosok, label in ((0, "KOSPI"), (1, "KOSDAQ")):
        try:
            items = _fetch_naver_market(sosok, label)
            for it in items:
                if it["stock_code"] in seen:
                    continue
                seen.add(it["stock_code"])
                result.append(it)
            print(f"[Naver] {label} 종목 {len(items)}개 수신")
        except Exception as e:
            print(f"[Naver] {label} 다운로드 실패: {e}")
    return result


def fetch_master_with_fallback() -> List[Dict[str, str]]:
    """KRX 직접 호출 → 네이버 폴백."""
    items = fetch_all_krx_tickers()
    if items:
        return items
    return fetch_all_naver_tickers()
