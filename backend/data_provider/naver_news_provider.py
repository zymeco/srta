# 네이버 검색 API 뉴스 + 간이 감성 분석.
# 키 없으면 빈 결과 반환.

import re
import html
import httpx
from datetime import datetime
from typing import Dict, Any, List

from ..keys.api_keys import get_key, has_naver
from ..utils.cache import memoize


POS_WORDS = [
    "호실적", "최대 실적", "사상최대", "어닝서프라이즈", "흑자전환", "성장", "급등", "수주",
    "수혜", "호재", "상승", "확대", "신고가", "강세", "매수", "긍정", "개선", "기대",
    "돌파", "회복", "반등", "추천", "목표가 상향", "공급계약",
]
NEG_WORDS = [
    "어닝쇼크", "적자", "실적 부진", "유상증자", "전환사채", "감자", "감사의견 거절",
    "관리종목", "투자경고", "투자위험", "거래정지", "급락", "악재", "하락", "약세",
    "매도", "부정", "악화", "위험", "위기", "리콜", "소송", "횡령", "분식회계",
    "신저가", "최대주주변경", "워크아웃", "법정관리", "상장폐지", "공매도",
]


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return html.unescape(s).strip()


def _classify(text: str) -> str:
    t = text
    pos_hit = sum(1 for w in POS_WORDS if w in t)
    neg_hit = sum(1 for w in NEG_WORDS if w in t)
    if pos_hit > neg_hit and pos_hit >= 1:
        return "positive"
    if neg_hit > pos_hit and neg_hit >= 1:
        return "negative"
    return "neutral"


def _theme_guess(items: List[Dict[str, Any]]) -> List[str]:
    """뉴스 제목 키워드 빈도로 테마 추정."""
    text = " ".join(it.get("title", "") + " " + it.get("description", "") for it in items)
    theme_kws = {
        "AI": ["AI", "인공지능", "LLM", "GPT"],
        "반도체": ["반도체", "메모리", "HBM", "파운드리"],
        "2차전지": ["2차전지", "배터리", "양극재", "음극재"],
        "방산": ["방산", "수출무기", "K2", "K9"],
        "원전": ["원전", "SMR"],
        "로봇": ["로봇", "휴머노이드"],
        "바이오": ["바이오", "신약", "임상"],
        "전기차": ["전기차", "EV"],
        "조선": ["조선", "선박"],
        "금융": ["금융", "은행", "보험"],
        "엔터": ["엔터", "K-POP", "콘서트"],
    }
    found = []
    for name, kws in theme_kws.items():
        if any(k in text for k in kws):
            found.append(name)
    return found[:5]


def get_news(stock_name: str, stock_code: str = "", display: int = 15) -> Dict[str, Any]:
    if not has_naver() or not stock_name:
        return {}

    def factory():
        try:
            params = {
                "query": stock_name,
                "display": display,
                "sort": "date",
            }
            headers = {
                "X-Naver-Client-Id": get_key("NAVER_CLIENT_ID"),
                "X-Naver-Client-Secret": get_key("NAVER_CLIENT_SECRET"),
            }
            with httpx.Client(timeout=10.0) as c:
                r = c.get("https://openapi.naver.com/v1/search/news.json",
                          params=params, headers=headers)
                r.raise_for_status()
                data = r.json()

            items_raw = data.get("items", []) or []
            items: List[Dict[str, Any]] = []
            counts = {"positive": 0, "neutral": 0, "negative": 0}
            for it in items_raw:
                title = _strip_html(it.get("title"))
                desc = _strip_html(it.get("description"))
                sent = _classify(title + " " + desc)
                counts[sent] += 1
                pub = it.get("pubDate", "")
                try:
                    dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %z")
                    date_str = dt.strftime("%Y-%m-%d")
                except Exception:
                    date_str = pub[:16]
                items.append({
                    "title": title,
                    "description": desc,
                    "sentiment": sent,
                    "source": "네이버뉴스",
                    "link": it.get("link", ""),
                    "date": date_str,
                })

            # 위험성 공시 키워드 (뉴스 기반 보조 신호)
            joined = " ".join(it["title"] + " " + it.get("description", "") for it in items)
            rights_issue = bool(re.search(r"유상증자", joined))
            convertible_bond = bool(re.search(r"전환사채|CB발행", joined))
            warrant = bool(re.search(r"신주인수권|BW", joined))
            largest_change = bool(re.search(r"최대주주.{0,4}변경", joined))

            return {
                "items": items,
                "sentiment_counts": counts,
                "themes": _theme_guess(items),
                "policy_benefit": bool(re.search(r"정책 수혜|정부 발표|육성", joined)),
                "disclosure_risk": rights_issue or convertible_bond or warrant or largest_change,
                "rights_issue": rights_issue,
                "convertible_bond": convertible_bond,
                "warrant": warrant,
                "largest_shareholder_change": largest_change,
                "_meta": {"source": "Naver"},
            }
        except httpx.HTTPStatusError as e:
            print(f"[Naver] news HTTP {e.response.status_code}")
            return {}
        except Exception as e:
            print(f"[Naver] news 실패: {e}")
            return {}

    return memoize(f"naver:news:{stock_code or stock_name}", 60 * 10, factory) or {}
