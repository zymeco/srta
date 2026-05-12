# DART OpenAPI 연동.
# - corp_code 매핑(전체 기업 목록 zip 다운로드 후 캐시)
# - 최근 사업보고서 기반 재무지표
# - 공시 검색으로 유상증자/전환사채/감사의견/관리종목 등 위험 플래그 판정
#
# 키 없으면 모든 함수가 빈 dict/False를 반환해 안전하게 동작.

import os
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import httpx

from ..keys.api_keys import get_key, has_dart
from ..utils.cache import memoize


BASE = "https://opendart.fss.or.kr/api"
CORP_CODE_PATH = os.path.join(os.path.dirname(__file__), "_dart_corpcode.xml")


def _load_corp_code_map() -> Dict[str, str]:
    """종목코드(6자리) → DART 고유번호(8자리) 맵."""
    if not has_dart():
        return {}

    def factory():
        try:
            if not os.path.exists(CORP_CODE_PATH):
                url = f"{BASE}/corpCode.xml?crtfc_key={get_key("DART_API_KEY")}"
                with httpx.Client(timeout=30.0) as c:
                    r = c.get(url)
                    r.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    name = z.namelist()[0]
                    data = z.read(name)
                with open(CORP_CODE_PATH, "wb") as f:
                    f.write(data)
            root = ET.parse(CORP_CODE_PATH).getroot()
            mp: Dict[str, str] = {}
            for el in root.findall("list"):
                stock = (el.findtext("stock_code") or "").strip()
                corp = (el.findtext("corp_code") or "").strip()
                if stock and corp and stock != " ":
                    mp[stock] = corp
            return mp
        except Exception as e:
            print(f"[DART] corp_code 로드 실패: {e}")
            return {}

    # 24시간 캐시 (파일도 따로 저장)
    return memoize("dart:corp_map", 60 * 60 * 24, factory) or {}


def _corp_code_for(stock_code: str) -> str:
    return _load_corp_code_map().get(stock_code, "")


def _fetch_json(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    params = {**params, "crtfc_key": get_key("DART_API_KEY")}
    with httpx.Client(timeout=20.0) as c:
        r = c.get(f"{BASE}/{path}", params=params)
        r.raise_for_status()
        return r.json()


def _latest_bsns_year() -> int:
    now = datetime.now()
    # 사업보고서 공시 시점 고려: 4월 이후엔 작년, 그 이전엔 재작년
    return now.year - 1 if now.month >= 4 else now.year - 2


def _num(s):
    if s is None:
        return 0
    s = str(s).replace(",", "").replace(" ", "")
    if s in ("", "-"):
        return 0
    try:
        return float(s)
    except Exception:
        return 0


def get_financial(stock_code: str) -> Dict[str, Any]:
    """DART 단일회사 전체 재무제표(사업보고서) 기반 재무 지표.
    반환 키 예: debt_ratio, current_ratio, retained_ratio, operating_cash_flow,
                interest_coverage, capital_impairment, three_year_loss,
                revenue_growth, operating_growth, net_income_growth,
                operating_margin, roe, eps_growth
    실패/키없음 시 {} 반환.
    """
    if not has_dart():
        return {}
    corp = _corp_code_for(stock_code)
    if not corp:
        return {}

    def factory():
        try:
            year = _latest_bsns_year()
            # 사업보고서 = 11011, 반기보고서 11012, 분기 11013/11014
            data = _fetch_json("fnlttSinglAcntAll.json", {
                "corp_code": corp,
                "bsns_year": str(year),
                "reprt_code": "11011",
                "fs_div": "OFS",  # 별도재무제표 (CFS=연결)
            })
            if data.get("status") not in ("000",):
                # 별도 실패 시 연결 시도
                data = _fetch_json("fnlttSinglAcntAll.json", {
                    "corp_code": corp,
                    "bsns_year": str(year),
                    "reprt_code": "11011",
                    "fs_div": "CFS",
                })
            items = data.get("list", []) or []
            if not items:
                return {}

            # 항목 추출 헬퍼 (계정명 매칭)
            def find_amt(account_names, sj_div=None, prefer_current=True):
                for it in items:
                    nm = (it.get("account_nm") or "").replace(" ", "")
                    if any(an.replace(" ", "") in nm for an in account_names):
                        if sj_div and it.get("sj_div") != sj_div:
                            continue
                        amt = _num(it.get("thstrm_amount") if prefer_current else it.get("frmtrm_amount"))
                        return amt
                return 0

            # 재무상태표(BS)
            total_assets = find_amt(["자산총계"], "BS")
            total_liab = find_amt(["부채총계"], "BS")
            total_equity = find_amt(["자본총계"], "BS")
            current_assets = find_amt(["유동자산"], "BS")
            current_liab = find_amt(["유동부채"], "BS")
            inventory = find_amt(["재고자산"], "BS")
            retained = find_amt(["이익잉여금"], "BS")
            capital = find_amt(["자본금"], "BS")

            # 손익계산서(IS / CIS)
            revenue = find_amt(["매출액", "수익(매출액)", "영업수익"], None)
            operating = find_amt(["영업이익", "영업이익(손실)"], None)
            net_income = find_amt(["당기순이익", "당기순이익(손실)"], None)
            interest_expense = find_amt(["이자비용"], None)

            # 현금흐름표(CF)
            ocf = find_amt(["영업활동현금흐름", "영업활동으로인한현금흐름"], "CF")

            # 전기 값 (성장률 산출)
            def find_prev(account_names, sj_div=None):
                for it in items:
                    nm = (it.get("account_nm") or "").replace(" ", "")
                    if any(an.replace(" ", "") in nm for an in account_names):
                        if sj_div and it.get("sj_div") != sj_div:
                            continue
                        return _num(it.get("frmtrm_amount"))
                return 0

            prev_revenue = find_prev(["매출액", "수익(매출액)", "영업수익"])
            prev_operating = find_prev(["영업이익"])
            prev_net = find_prev(["당기순이익"])

            def safe_div(a, b):
                return (a / b) if b else 0

            def growth(cur, prev):
                if not prev:
                    return 0.0
                return round((cur - prev) / abs(prev) * 100, 1)

            debt_ratio = round(safe_div(total_liab, total_equity) * 100, 1) if total_equity else 0
            current_ratio = round(safe_div(current_assets, current_liab) * 100, 1) if current_liab else 0
            quick_ratio = round(safe_div(current_assets - inventory, current_liab) * 100, 1) if current_liab else 0
            retained_ratio = round(safe_div(retained, capital) * 100, 1) if capital else 0
            interest_cov = round(safe_div(operating, interest_expense), 2) if interest_expense else 999.0
            operating_margin = round(safe_div(operating, revenue) * 100, 1) if revenue else 0
            roe = round(safe_div(net_income, total_equity) * 100, 1) if total_equity else 0

            # 자본잠식: 자본총계 ≤ 0 또는 자본총계 < 자본금
            capital_impairment = (total_equity is not None) and (total_equity <= 0 or (capital > 0 and total_equity < capital))

            return {
                "debt_ratio": debt_ratio,
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
                "retained_ratio": retained_ratio,
                "operating_cash_flow": int(ocf),
                "interest_coverage": interest_cov,
                "capital_impairment": bool(capital_impairment),
                "three_year_loss": bool(net_income < 0 and prev_net < 0),  # 근사
                "revenue_growth": growth(revenue, prev_revenue),
                "operating_growth": growth(operating, prev_operating),
                "net_income_growth": growth(net_income, prev_net),
                "operating_margin": operating_margin,
                "roe": roe,
                "eps_growth": growth(net_income, prev_net),  # 근사
                "_meta": {"year": year, "source": "DART"},
            }
        except httpx.HTTPStatusError as e:
            print(f"[DART] financial HTTP {e.response.status_code}: {e.response.text[:200]}")
            return {}
        except Exception as e:
            print(f"[DART] financial 실패({stock_code}): {e}")
            return {}

    return memoize(f"dart:fin:{stock_code}", 60 * 60 * 12, factory) or {}


# ---- 공시 기반 리스크 플래그 ----

RISK_KEYWORDS = {
    "rights_issue": ["유상증자", "주주배정", "제3자배정"],
    "convertible_bond": ["전환사채", "CB발행"],
    "warrant": ["신주인수권", "BW", "워런트"],
    "audit_issue": ["감사의견 한정", "감사의견 거절", "감사의견 부적정"],
    "management_stock": ["관리종목 지정"],
    "investment_warning": ["투자경고종목 지정"],
    "investment_danger": ["투자위험종목 지정"],
    "delisting_risk": ["상장폐지"],
    "trading_halt_history": ["매매거래정지"],
    "unfaithful_disclosure": ["불성실공시법인 지정"],
    "largest_shareholder_change": ["최대주주변경"],
}


def get_disclosure_risks(stock_code: str, days: int = 180) -> Dict[str, Any]:
    """최근 days일 내 공시 제목 검색으로 위험 플래그 판정.
    키 없거나 실패 시 모든 키 False.
    """
    base = {k: False for k in RISK_KEYWORDS.keys()}
    if not has_dart():
        return base
    corp = _corp_code_for(stock_code)
    if not corp:
        return base

    def factory():
        try:
            end = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            data = _fetch_json("list.json", {
                "corp_code": corp,
                "bgn_de": start,
                "end_de": end,
                "page_no": "1",
                "page_count": "100",
            })
            items = data.get("list", []) or []
            titles = [(it.get("report_nm") or "") for it in items]
            flags = dict(base)
            for k, kws in RISK_KEYWORDS.items():
                for title in titles:
                    if any(kw in title for kw in kws):
                        flags[k] = True
                        break
            return flags
        except Exception as e:
            print(f"[DART] disclosures 실패({stock_code}): {e}")
            return base

    return memoize(f"dart:disc:{stock_code}", 60 * 60 * 6, factory) or base
