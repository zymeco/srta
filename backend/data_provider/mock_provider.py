# 더미 데이터 프로바이더.
# 종목 코드에 따라 결정론적으로 다른 데이터가 나오도록 seed 기반 난수 사용.

import random
import math
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .base_provider import BaseProvider


# 검색용 대표 종목 마스터 (이름 → 코드)
STOCK_MASTER = [
    # ---- KOSPI 시총 상위 ----
    {"stock_code": "005930", "stock_name": "삼성전자", "market": "KOSPI", "sector": "반도체"},
    {"stock_code": "000660", "stock_name": "SK하이닉스", "market": "KOSPI", "sector": "반도체"},
    {"stock_code": "207940", "stock_name": "삼성바이오로직스", "market": "KOSPI", "sector": "바이오"},
    {"stock_code": "373220", "stock_name": "LG에너지솔루션", "market": "KOSPI", "sector": "2차전지"},
    {"stock_code": "005380", "stock_name": "현대차", "market": "KOSPI", "sector": "자동차"},
    {"stock_code": "000270", "stock_name": "기아", "market": "KOSPI", "sector": "자동차"},
    {"stock_code": "005935", "stock_name": "삼성전자우", "market": "KOSPI", "sector": "반도체"},
    {"stock_code": "012450", "stock_name": "한화에어로스페이스", "market": "KOSPI", "sector": "방산"},
    {"stock_code": "105560", "stock_name": "KB금융", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "055550", "stock_name": "신한지주", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "035420", "stock_name": "NAVER", "market": "KOSPI", "sector": "IT서비스"},
    {"stock_code": "006400", "stock_name": "삼성SDI", "market": "KOSPI", "sector": "2차전지"},
    {"stock_code": "035720", "stock_name": "카카오", "market": "KOSPI", "sector": "IT서비스"},
    {"stock_code": "028260", "stock_name": "삼성물산", "market": "KOSPI", "sector": "건설"},
    {"stock_code": "051910", "stock_name": "LG화학", "market": "KOSPI", "sector": "화학"},
    {"stock_code": "032830", "stock_name": "삼성생명", "market": "KOSPI", "sector": "보험"},
    {"stock_code": "003670", "stock_name": "포스코퓨처엠", "market": "KOSPI", "sector": "2차전지소재"},
    {"stock_code": "009540", "stock_name": "HD한국조선해양", "market": "KOSPI", "sector": "조선"},
    {"stock_code": "066570", "stock_name": "LG전자", "market": "KOSPI", "sector": "가전"},
    {"stock_code": "015760", "stock_name": "한국전력", "market": "KOSPI", "sector": "전력"},
    {"stock_code": "138040", "stock_name": "메리츠금융지주", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "086790", "stock_name": "하나금융지주", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "024110", "stock_name": "기업은행", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "033780", "stock_name": "KT&G", "market": "KOSPI", "sector": "담배"},
    {"stock_code": "017670", "stock_name": "SK텔레콤", "market": "KOSPI", "sector": "통신"},
    {"stock_code": "003550", "stock_name": "LG", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "259960", "stock_name": "크래프톤", "market": "KOSPI", "sector": "게임"},
    {"stock_code": "018260", "stock_name": "삼성에스디에스", "market": "KOSPI", "sector": "IT서비스"},
    {"stock_code": "000810", "stock_name": "삼성화재", "market": "KOSPI", "sector": "보험"},
    {"stock_code": "316140", "stock_name": "우리금융지주", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "402340", "stock_name": "SK스퀘어", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "267260", "stock_name": "HD현대일렉트릭", "market": "KOSPI", "sector": "전력"},
    {"stock_code": "267250", "stock_name": "HD현대", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "047810", "stock_name": "한국항공우주", "market": "KOSPI", "sector": "방산"},
    {"stock_code": "064350", "stock_name": "현대로템", "market": "KOSPI", "sector": "방산"},
    {"stock_code": "009830", "stock_name": "한화솔루션", "market": "KOSPI", "sector": "태양광"},
    {"stock_code": "029780", "stock_name": "삼성카드", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "036570", "stock_name": "엔씨소프트", "market": "KOSPI", "sector": "게임"},
    {"stock_code": "000720", "stock_name": "현대건설", "market": "KOSPI", "sector": "건설"},
    {"stock_code": "003490", "stock_name": "대한항공", "market": "KOSPI", "sector": "항공"},
    {"stock_code": "377300", "stock_name": "카카오페이", "market": "KOSPI", "sector": "핀테크"},
    {"stock_code": "180640", "stock_name": "한진칼", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "011200", "stock_name": "HMM", "market": "KOSPI", "sector": "해운"},
    {"stock_code": "034730", "stock_name": "SK", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "030200", "stock_name": "KT", "market": "KOSPI", "sector": "통신"},
    {"stock_code": "010130", "stock_name": "고려아연", "market": "KOSPI", "sector": "비철금속"},
    {"stock_code": "006800", "stock_name": "미래에셋증권", "market": "KOSPI", "sector": "증권"},
    {"stock_code": "352820", "stock_name": "하이브", "market": "KOSPI", "sector": "엔터"},
    {"stock_code": "241560", "stock_name": "두산밥캣", "market": "KOSPI", "sector": "기계"},
    {"stock_code": "271560", "stock_name": "오리온", "market": "KOSPI", "sector": "식품"},
    {"stock_code": "326030", "stock_name": "SK바이오팜", "market": "KOSPI", "sector": "바이오"},
    {"stock_code": "078930", "stock_name": "GS", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "047050", "stock_name": "포스코인터내셔널", "market": "KOSPI", "sector": "상사"},
    {"stock_code": "009150", "stock_name": "삼성전기", "market": "KOSPI", "sector": "전자부품"},
    {"stock_code": "010140", "stock_name": "삼성중공업", "market": "KOSPI", "sector": "조선"},
    {"stock_code": "161390", "stock_name": "한국타이어앤테크놀로지", "market": "KOSPI", "sector": "타이어"},
    {"stock_code": "000100", "stock_name": "유한양행", "market": "KOSPI", "sector": "제약"},
    {"stock_code": "032640", "stock_name": "LG유플러스", "market": "KOSPI", "sector": "통신"},
    {"stock_code": "139480", "stock_name": "이마트", "market": "KOSPI", "sector": "유통"},
    {"stock_code": "004020", "stock_name": "현대제철", "market": "KOSPI", "sector": "철강"},
    {"stock_code": "192820", "stock_name": "코스맥스", "market": "KOSPI", "sector": "화장품"},
    {"stock_code": "023530", "stock_name": "롯데쇼핑", "market": "KOSPI", "sector": "유통"},
    {"stock_code": "018880", "stock_name": "한온시스템", "market": "KOSPI", "sector": "자동차부품"},
    {"stock_code": "021240", "stock_name": "코웨이", "market": "KOSPI", "sector": "생활가전"},
    {"stock_code": "028670", "stock_name": "팬오션", "market": "KOSPI", "sector": "해운"},
    {"stock_code": "000150", "stock_name": "두산", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "008770", "stock_name": "호텔신라", "market": "KOSPI", "sector": "면세"},
    {"stock_code": "006360", "stock_name": "GS건설", "market": "KOSPI", "sector": "건설"},
    {"stock_code": "047040", "stock_name": "대우건설", "market": "KOSPI", "sector": "건설"},
    {"stock_code": "000880", "stock_name": "한화", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "032350", "stock_name": "롯데관광개발", "market": "KOSPI", "sector": "관광"},
    {"stock_code": "006260", "stock_name": "LS", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "035250", "stock_name": "강원랜드", "market": "KOSPI", "sector": "레저"},
    {"stock_code": "008560", "stock_name": "메리츠증권", "market": "KOSPI", "sector": "증권"},
    {"stock_code": "006690", "stock_name": "GC셀", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "036460", "stock_name": "한국가스공사", "market": "KOSPI", "sector": "가스"},
    {"stock_code": "001040", "stock_name": "CJ", "market": "KOSPI", "sector": "지주"},
    {"stock_code": "097950", "stock_name": "CJ제일제당", "market": "KOSPI", "sector": "식품"},
    {"stock_code": "078340", "stock_name": "컴투스", "market": "KOSDAQ", "sector": "게임"},
    {"stock_code": "251270", "stock_name": "넷마블", "market": "KOSPI", "sector": "게임"},
    {"stock_code": "012330", "stock_name": "현대모비스", "market": "KOSPI", "sector": "자동차부품"},
    {"stock_code": "010950", "stock_name": "S-Oil", "market": "KOSPI", "sector": "정유"},
    {"stock_code": "096770", "stock_name": "SK이노베이션", "market": "KOSPI", "sector": "정유"},
    {"stock_code": "005490", "stock_name": "POSCO홀딩스", "market": "KOSPI", "sector": "철강"},
    {"stock_code": "068270", "stock_name": "셀트리온", "market": "KOSPI", "sector": "바이오"},
    {"stock_code": "302440", "stock_name": "SK바이오사이언스", "market": "KOSPI", "sector": "바이오"},
    {"stock_code": "010060", "stock_name": "OCI홀딩스", "market": "KOSPI", "sector": "화학"},
    {"stock_code": "011170", "stock_name": "롯데케미칼", "market": "KOSPI", "sector": "화학"},
    {"stock_code": "011070", "stock_name": "LG이노텍", "market": "KOSPI", "sector": "전자부품"},
    {"stock_code": "034220", "stock_name": "LG디스플레이", "market": "KOSPI", "sector": "디스플레이"},
    {"stock_code": "001450", "stock_name": "현대해상", "market": "KOSPI", "sector": "보험"},
    {"stock_code": "088350", "stock_name": "한화생명", "market": "KOSPI", "sector": "보험"},
    {"stock_code": "071050", "stock_name": "한국금융지주", "market": "KOSPI", "sector": "금융"},
    {"stock_code": "030000", "stock_name": "제일기획", "market": "KOSPI", "sector": "광고"},
    {"stock_code": "086280", "stock_name": "현대글로비스", "market": "KOSPI", "sector": "물류"},
    {"stock_code": "377740", "stock_name": "이수페타시스", "market": "KOSPI", "sector": "전자부품"},

    # ---- KOSDAQ 시총/거래대금 상위 ----
    {"stock_code": "247540", "stock_name": "에코프로비엠", "market": "KOSDAQ", "sector": "2차전지소재"},
    {"stock_code": "086520", "stock_name": "에코프로", "market": "KOSDAQ", "sector": "2차전지소재"},
    {"stock_code": "091990", "stock_name": "셀트리온헬스케어", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "066970", "stock_name": "엘앤에프", "market": "KOSDAQ", "sector": "2차전지소재"},
    {"stock_code": "196170", "stock_name": "알테오젠", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "028300", "stock_name": "HLB", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "039030", "stock_name": "이오테크닉스", "market": "KOSDAQ", "sector": "반도체장비"},
    {"stock_code": "067310", "stock_name": "하나마이크론", "market": "KOSDAQ", "sector": "반도체"},
    {"stock_code": "178320", "stock_name": "서진시스템", "market": "KOSDAQ", "sector": "기계"},
    {"stock_code": "214150", "stock_name": "클래시스", "market": "KOSDAQ", "sector": "의료기기"},
    {"stock_code": "357780", "stock_name": "솔브레인", "market": "KOSDAQ", "sector": "반도체소재"},
    {"stock_code": "278280", "stock_name": "천보", "market": "KOSDAQ", "sector": "2차전지소재"},
    {"stock_code": "145020", "stock_name": "휴젤", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "240810", "stock_name": "원익IPS", "market": "KOSDAQ", "sector": "반도체장비"},
    {"stock_code": "035900", "stock_name": "JYP Ent.", "market": "KOSDAQ", "sector": "엔터"},
    {"stock_code": "067160", "stock_name": "아프리카TV", "market": "KOSDAQ", "sector": "방송"},
    {"stock_code": "041510", "stock_name": "에스엠", "market": "KOSDAQ", "sector": "엔터"},
    {"stock_code": "122870", "stock_name": "와이지엔터테인먼트", "market": "KOSDAQ", "sector": "엔터"},
    {"stock_code": "214450", "stock_name": "파마리서치", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "348370", "stock_name": "엔켐", "market": "KOSDAQ", "sector": "2차전지소재"},
    {"stock_code": "085660", "stock_name": "차바이오텍", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "141080", "stock_name": "리가켐바이오", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "036930", "stock_name": "주성엔지니어링", "market": "KOSDAQ", "sector": "반도체장비"},
    {"stock_code": "095610", "stock_name": "테스", "market": "KOSDAQ", "sector": "반도체장비"},
    {"stock_code": "058470", "stock_name": "리노공업", "market": "KOSDAQ", "sector": "반도체"},
    {"stock_code": "095340", "stock_name": "ISC", "market": "KOSDAQ", "sector": "반도체"},
    {"stock_code": "393890", "stock_name": "더블유씨피", "market": "KOSDAQ", "sector": "2차전지소재"},
    {"stock_code": "112040", "stock_name": "위메이드", "market": "KOSDAQ", "sector": "게임"},
    {"stock_code": "293490", "stock_name": "카카오게임즈", "market": "KOSDAQ", "sector": "게임"},
    {"stock_code": "263750", "stock_name": "펄어비스", "market": "KOSDAQ", "sector": "게임"},
    {"stock_code": "041960", "stock_name": "코미팜", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "950140", "stock_name": "잉글우드랩", "market": "KOSDAQ", "sector": "화장품"},
    {"stock_code": "131290", "stock_name": "티에스이", "market": "KOSDAQ", "sector": "반도체"},
    {"stock_code": "058820", "stock_name": "CMG제약", "market": "KOSDAQ", "sector": "제약"},
    {"stock_code": "086900", "stock_name": "메디톡스", "market": "KOSDAQ", "sector": "바이오"},
    {"stock_code": "298540", "stock_name": "더블유에스아이", "market": "KOSDAQ", "sector": "전자"},
    {"stock_code": "317330", "stock_name": "덕산테코피아", "market": "KOSDAQ", "sector": "디스플레이"},
    {"stock_code": "131970", "stock_name": "두산테스나", "market": "KOSDAQ", "sector": "반도체"},
    {"stock_code": "418550", "stock_name": "제이엔비", "market": "KOSDAQ", "sector": "2차전지"},
    {"stock_code": "457550", "stock_name": "에이치브이엠", "market": "KOSDAQ", "sector": "방산"},
    {"stock_code": "475580", "stock_name": "에이펙스", "market": "KOSDAQ", "sector": "반도체"},

    # ---- 테스트용 ----
    {"stock_code": "000000", "stock_name": "위험종목", "market": "KOSDAQ", "sector": "기타"},
    {"stock_code": "111111", "stock_name": "관리종목테스트", "market": "KOSDAQ", "sector": "기타"},
]


def _seed_for(stock_code: str) -> int:
    h = hashlib.md5(stock_code.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _rand(stock_code: str) -> random.Random:
    return random.Random(_seed_for(stock_code))


def _find_master(stock_code: str) -> Dict[str, str]:
    for m in STOCK_MASTER:
        if m["stock_code"] == stock_code:
            return m
    return {
        "stock_code": stock_code,
        "stock_name": f"종목{stock_code}",
        "market": "KOSPI",
        "sector": "기타",
    }


class MockProvider(BaseProvider):
    def search(self, query: str) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        # 대소문자 무시 + 공백 무시 매칭
        ql = q.lower().replace(" ", "")
        results = []
        for m in STOCK_MASTER:
            name_norm = m["stock_name"].lower().replace(" ", "")
            if q == m["stock_code"] or ql in name_norm:
                results.append(m)
        return results[:20]

    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        r = _rand(stock_code)
        master = _find_master(stock_code)

        # 코드 기반 결정론적 시세
        base_price = 10000 + r.randint(0, 200000)
        change_rate = round(r.uniform(-7, 7), 2)
        current_price = int(base_price * (1 + change_rate / 100.0))
        volume = r.randint(100_000, 30_000_000)
        trading_value = current_price * volume

        # 시총 결정
        mc_kind = r.choice(["large", "large", "mid", "mid", "small", "small"])
        if mc_kind == "large":
            market_cap = r.randint(5_000_000_000_000, 600_000_000_000_000)
        elif mc_kind == "mid":
            market_cap = r.randint(500_000_000_000, 5_000_000_000_000)
        else:
            market_cap = r.randint(30_000_000_000, 500_000_000_000)

        high_52w = int(current_price * r.uniform(1.05, 1.6))
        low_52w = int(current_price * r.uniform(0.55, 0.95))

        return {
            "stock_code": stock_code,
            "stock_name": master["stock_name"],
            "market": master["market"],
            "sector": master["sector"],
            "current_price": current_price,
            "change_rate": change_rate,
            "volume": volume,
            "trading_value": trading_value,
            "market_cap": market_cap,
            "market_cap_type": mc_kind,
            "high_52w": high_52w,
            "low_52w": low_52w,
        }

    def get_price_history(self, stock_code: str) -> Dict[str, Any]:
        r = _rand(stock_code + "_price")
        info = self.get_stock_basic_info(stock_code)
        current = info["current_price"]

        days = 120
        prices: List[Dict[str, Any]] = []
        volumes: List[Dict[str, Any]] = []
        p = current * r.uniform(0.7, 0.95)
        today = datetime.now()

        for i in range(days):
            d = today - timedelta(days=days - i)
            drift = r.uniform(-0.025, 0.030)
            p = max(100, p * (1 + drift))
            vol = max(10_000, int(info["volume"] * r.uniform(0.4, 1.6)))
            date_str = d.strftime("%Y-%m-%d")
            prices.append({"date": date_str, "close": round(p, 2)})
            volumes.append({"date": date_str, "volume": vol})

        # 마지막 종가를 현재가로 살짝 보정
        prices[-1]["close"] = current

        closes = [x["close"] for x in prices]

        def sma(period):
            out = []
            for i in range(len(closes)):
                if i < period - 1:
                    out.append(None)
                else:
                    out.append(round(sum(closes[i - period + 1:i + 1]) / period, 2))
            return out

        ma5 = sma(5)
        ma20 = sma(20)
        ma60 = sma(60)
        ma120 = sma(120)

        # RSI(14)
        rsis: List[Any] = []
        gains, losses = [], []
        for i in range(1, len(closes)):
            ch = closes[i] - closes[i - 1]
            gains.append(max(ch, 0))
            losses.append(max(-ch, 0))
        rsi_values: List[Any] = [None]
        period = 14
        for i in range(len(gains)):
            if i < period - 1:
                rsi_values.append(None)
                continue
            avg_gain = sum(gains[i - period + 1:i + 1]) / period
            avg_loss = sum(losses[i - period + 1:i + 1]) / period
            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(round(100 - 100 / (1 + rs), 2))

        # MACD (12,26,9) 단순 EMA
        def ema(data, period):
            k = 2 / (period + 1)
            out = []
            prev = None
            for v in data:
                if v is None:
                    out.append(None)
                    continue
                if prev is None:
                    prev = v
                else:
                    prev = v * k + prev * (1 - k)
                out.append(prev)
            return out

        ema12 = ema(closes, 12)
        ema26 = ema(closes, 26)
        macd = [
            (ema12[i] - ema26[i]) if (ema12[i] is not None and ema26[i] is not None) else None
            for i in range(len(closes))
        ]
        signal = ema([m if m is not None else 0 for m in macd], 9)

        # 볼린저밴드 (20, 2)
        bb_upper, bb_lower = [], []
        for i in range(len(closes)):
            if i < 19:
                bb_upper.append(None)
                bb_lower.append(None)
                continue
            window = closes[i - 19:i + 1]
            m = sum(window) / 20
            sd = math.sqrt(sum((x - m) ** 2 for x in window) / 20)
            bb_upper.append(round(m + 2 * sd, 2))
            bb_lower.append(round(m - 2 * sd, 2))

        return {
            "prices": prices,
            "volumes": volumes,
            "ma5": ma5,
            "ma20": ma20,
            "ma60": ma60,
            "ma120": ma120,
            "rsi": rsi_values,
            "macd": macd,
            "macd_signal": signal,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "high_52w": info["high_52w"],
            "low_52w": info["low_52w"],
        }

    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        r = _rand(stock_code + "_fin")
        is_risky = stock_code in ("000000", "111111")
        debt_ratio = r.uniform(20, 220) if not is_risky else r.uniform(280, 500)
        current_ratio = r.uniform(80, 280) if not is_risky else r.uniform(30, 90)
        quick_ratio = max(20, current_ratio - r.uniform(10, 80))
        retained_ratio = r.uniform(200, 4000) if not is_risky else r.uniform(-300, 100)
        ocf = r.randint(-50, 800) * 100_000_000 if not is_risky else r.randint(-300, 50) * 100_000_000
        interest_cov = r.uniform(1, 25) if not is_risky else r.uniform(-1, 1.5)
        capital_impairment = is_risky and r.random() < 0.7
        three_year_loss = is_risky and r.random() < 0.6

        revenue_growth = r.uniform(-15, 35) if not is_risky else r.uniform(-30, 5)
        op_growth = r.uniform(-20, 45) if not is_risky else r.uniform(-50, 0)
        net_growth = r.uniform(-25, 50) if not is_risky else r.uniform(-60, -5)
        op_margin = r.uniform(-5, 25) if not is_risky else r.uniform(-20, 2)
        roe = r.uniform(-5, 22) if not is_risky else r.uniform(-30, 0)
        eps_growth = r.uniform(-30, 60) if not is_risky else r.uniform(-50, -10)

        per = round(r.uniform(5, 35), 1) if not is_risky else round(r.uniform(-30, -3), 1)
        pbr = round(r.uniform(0.5, 4.5), 2)
        psr = round(r.uniform(0.3, 6.0), 2)
        ev_ebitda = round(r.uniform(3, 25), 1)
        sector_per = round(r.uniform(8, 25), 1)

        # 3년 실적 추이
        revenue_trend = []
        op_trend = []
        base_rev = r.randint(500, 50000)
        base_op = r.randint(20, 5000)
        for year_off in range(3, 0, -1):
            yr = datetime.now().year - year_off + 1
            mul = 1 + r.uniform(-0.1, 0.15)
            base_rev = max(10, int(base_rev * mul))
            base_op = int(base_op * (1 + r.uniform(-0.2, 0.25)))
            revenue_trend.append({"year": str(yr), "value": base_rev})
            op_trend.append({"year": str(yr), "value": base_op})

        return {
            "debt_ratio": round(debt_ratio, 1),
            "current_ratio": round(current_ratio, 1),
            "quick_ratio": round(quick_ratio, 1),
            "retained_ratio": round(retained_ratio, 1),
            "operating_cash_flow": ocf,
            "interest_coverage": round(interest_cov, 2),
            "capital_impairment": capital_impairment,
            "three_year_loss": three_year_loss,
            "revenue_growth": round(revenue_growth, 1),
            "operating_growth": round(op_growth, 1),
            "net_income_growth": round(net_growth, 1),
            "operating_margin": round(op_margin, 1),
            "roe": round(roe, 1),
            "eps_growth": round(eps_growth, 1),
            "per": per,
            "pbr": pbr,
            "psr": psr,
            "ev_ebitda": ev_ebitda,
            "sector_per": sector_per,
            "revenue_trend": revenue_trend,
            "operating_trend": op_trend,
        }

    def get_supply_data(self, stock_code: str) -> Dict[str, Any]:
        r = _rand(stock_code + "_sup")
        is_risky = stock_code in ("000000", "111111")

        def make_series(days, bias):
            out = []
            today = datetime.now()
            for i in range(days):
                d = today - timedelta(days=days - i)
                out.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "foreign": r.randint(-500, 800) + bias,
                    "institution": r.randint(-400, 600) + bias // 2,
                    "individual": r.randint(-700, 700) - bias,
                })
            return out

        bias = r.randint(-200, 300) if not is_risky else r.randint(-400, -100)
        series = make_series(20, bias)

        f5 = sum(x["foreign"] for x in series[-5:])
        f20 = sum(x["foreign"] for x in series)
        i5 = sum(x["institution"] for x in series[-5:])
        i20 = sum(x["institution"] for x in series)
        ind = sum(x["individual"] for x in series)

        short_ratio = round(r.uniform(0.5, 9.0), 2) if not is_risky else round(r.uniform(8, 25), 2)
        credit_balance = round(r.uniform(0.5, 5.0), 2) if not is_risky else round(r.uniform(6, 15), 2)
        program = r.randint(-300, 500)

        return {
            "series": series,
            "foreign_5d": f5,
            "foreign_20d": f20,
            "institution_5d": i5,
            "institution_20d": i20,
            "individual_20d": ind,
            "program": program,
            "short_selling_ratio": short_ratio,
            "credit_balance_ratio": credit_balance,
        }

    def get_news_data(self, stock_code: str) -> Dict[str, Any]:
        r = _rand(stock_code + "_news")
        is_risky = stock_code in ("000000", "111111")

        sample_pos = [
            "분기 실적 시장 기대치 상회",
            "신규 수주 계약 체결",
            "정부 정책 수혜 기대감",
            "외국인 매수세 유입 지속",
            "해외 진출 본격화",
        ]
        sample_neu = [
            "업종 평균 수준의 거래량",
            "특별한 이슈 없음",
            "분석기관 목표가 유지",
        ]
        sample_neg = [
            "전환사채 발행 결정",
            "유상증자 우려 부각",
            "최대주주 지분 매도",
            "감사의견 한정 우려",
            "단기 차익실현 매물 출회",
        ]

        items = []
        sentiments = {"positive": 0, "neutral": 0, "negative": 0}
        for _ in range(8):
            if is_risky:
                s = r.choices(["positive", "neutral", "negative"], weights=[1, 2, 7])[0]
            else:
                s = r.choices(["positive", "neutral", "negative"], weights=[5, 3, 2])[0]
            sentiments[s] += 1
            title = r.choice({"positive": sample_pos, "neutral": sample_neu, "negative": sample_neg}[s])
            items.append({
                "title": title,
                "sentiment": s,
                "source": r.choice(["연합뉴스", "한국경제", "매일경제", "이데일리"]),
                "date": (datetime.now() - timedelta(days=r.randint(0, 7))).strftime("%Y-%m-%d"),
            })

        themes = r.sample(
            ["AI", "반도체", "2차전지", "방산", "원전", "로봇", "바이오", "전기차", "조선", "금융"],
            k=3,
        )

        return {
            "items": items,
            "sentiment_counts": sentiments,
            "themes": themes,
            "policy_benefit": r.random() < 0.4,
            "disclosure_risk": is_risky or r.random() < 0.15,
            "rights_issue": is_risky and r.random() < 0.7,
            "convertible_bond": is_risky and r.random() < 0.7,
            "warrant": is_risky and r.random() < 0.5,
            "largest_shareholder_change": is_risky and r.random() < 0.4,
        }

    def get_risk_data(self, stock_code: str) -> Dict[str, Any]:
        r = _rand(stock_code + "_risk")
        is_management = stock_code == "111111"
        is_risky = stock_code in ("000000", "111111")

        return {
            "management_stock": is_management,
            "investment_warning": is_risky and r.random() < 0.5,
            "investment_danger": is_management,
            "capital_impairment": is_management or (is_risky and r.random() < 0.4),
            "trading_halt_history": is_risky and r.random() < 0.5,
            "audit_issue": is_management or (is_risky and r.random() < 0.3),
            "delisting_risk": is_management and r.random() < 0.7,
            "unfaithful_disclosure": is_risky and r.random() < 0.3,
            "three_year_loss": is_risky and r.random() < 0.6,
            "rights_issue": is_risky and r.random() < 0.6,
            "convertible_bond": is_risky and r.random() < 0.6,
            "warrant": is_risky and r.random() < 0.4,
            "largest_shareholder_change": is_risky and r.random() < 0.4,
            "credit_overheat": is_risky and r.random() < 0.5,
            "short_selling_spike": is_risky and r.random() < 0.4,
            "low_liquidity": is_risky and r.random() < 0.4,
            "manipulation_pattern": is_risky and r.random() < 0.3,
            "pump_then_volume_drop": is_risky and r.random() < 0.5,
        }
