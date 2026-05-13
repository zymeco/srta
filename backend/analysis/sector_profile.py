# 섹터/테마별 분석 가중치 및 보너스.
#
# 한국 주식은 섹터별 특성이 매우 다르다:
#   - 성장 섹터(반도체/2차전지/AI/방산): 모멘텀과 성장성에 가중치
#   - 가치 섹터(금융/통신/유틸리티): 밸류에이션과 배당에 가중치
#   - 사이클 섹터(화학/철강/조선): 업황 모멘텀
#   - 방어 섹터(식품/제약): 안정성
#
# 결과적으로 같은 RSI 75라도 섹터에 따라 의미가 다르다:
#   - 반도체 강세 사이클: 추격매수 위험 보통
#   - 가치주 일시 급등: 추격매수 위험 높음

from typing import Dict, List


# 섹터별 카테고리 분류
SECTOR_CATEGORY: Dict[str, str] = {
    # 성장 (Growth)
    "반도체": "growth",
    "반도체소재": "growth",
    "반도체장비": "growth",
    "2차전지": "growth",
    "2차전지소재": "growth",
    "IT서비스": "growth",
    "바이오": "growth_volatile",
    "제약": "growth_volatile",
    "디스플레이": "growth",
    "엔터": "growth_volatile",
    "게임": "growth_volatile",
    "방산": "growth_theme",
    "전기차": "growth",
    "로봇": "growth_theme",
    "원전": "growth_theme",

    # 가치 (Value)
    "금융": "value",
    "보험": "value",
    "증권": "value",
    "지주": "value",
    "통신": "value_defensive",
    "전력": "value_defensive",
    "가스": "value_defensive",
    "담배": "value_defensive",
    "유통": "value",

    # 사이클 (Cyclical)
    "화학": "cyclical",
    "철강": "cyclical",
    "조선": "cyclical",
    "자동차": "cyclical",
    "자동차부품": "cyclical",
    "정유": "cyclical",
    "타이어": "cyclical",
    "비철금속": "cyclical",
    "건설": "cyclical",
    "해운": "cyclical",
    "항공": "cyclical",

    # 방어 (Defensive)
    "식품": "defensive",
    "화장품": "defensive",
    "생활가전": "defensive",
    "면세": "defensive",
    "전자부품": "growth",
    "전자": "growth",
    "기계": "cyclical",
    "물류": "value",
    "광고": "value_defensive",
    "방송": "value_defensive",
    "의료기기": "growth",
    "태양광": "growth_theme",
}


# 카테고리별 점수 영역 가중치 (multiplier)
CATEGORY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "growth": {
        "financial": 0.95, "growth": 1.20, "valuation": 0.90,
        "technical": 1.10, "volume": 1.10, "supply": 1.05,
        "news_theme": 1.10, "risk": 1.00, "timing": 0.95,
    },
    "growth_theme": {
        "financial": 0.85, "growth": 1.10, "valuation": 0.80,
        "technical": 1.20, "volume": 1.20, "supply": 1.00,
        "news_theme": 1.30, "risk": 1.10, "timing": 0.90,
    },
    "growth_volatile": {
        "financial": 0.90, "growth": 1.10, "valuation": 0.85,
        "technical": 1.10, "volume": 1.15, "supply": 1.10,
        "news_theme": 1.10, "risk": 1.20, "timing": 0.95,
    },
    "value": {
        "financial": 1.20, "growth": 0.85, "valuation": 1.30,
        "technical": 0.85, "volume": 0.90, "supply": 1.10,
        "news_theme": 0.85, "risk": 1.00, "timing": 1.00,
    },
    "value_defensive": {
        "financial": 1.30, "growth": 0.80, "valuation": 1.25,
        "technical": 0.75, "volume": 0.85, "supply": 1.05,
        "news_theme": 0.75, "risk": 1.15, "timing": 1.00,
    },
    "cyclical": {
        "financial": 1.05, "growth": 1.05, "valuation": 1.05,
        "technical": 1.10, "volume": 1.05, "supply": 1.05,
        "news_theme": 1.10, "risk": 1.00, "timing": 1.10,
    },
    "defensive": {
        "financial": 1.20, "growth": 0.90, "valuation": 1.15,
        "technical": 0.85, "volume": 0.85, "supply": 1.00,
        "news_theme": 0.80, "risk": 1.10, "timing": 1.00,
    },
    "default": {
        "financial": 1.00, "growth": 1.00, "valuation": 1.00,
        "technical": 1.00, "volume": 1.00, "supply": 1.00,
        "news_theme": 1.00, "risk": 1.00, "timing": 1.00,
    },
}


# 테마별 점수 보너스 (총점에 가산)
THEME_BONUS = {
    "AI": 2.5,
    "반도체": 2.0,
    "2차전지": 1.5,
    "방산": 2.0,
    "원전": 1.8,
    "로봇": 1.5,
    "전기차": 1.0,
    "조선": 1.5,
    "바이오": 0.5,
    "엔터": 0.8,
    "금융": 0.5,
}


def get_sector_category(sector: str) -> str:
    if not sector:
        return "default"
    return SECTOR_CATEGORY.get(sector, "default")


def get_category_weights(sector: str) -> Dict[str, float]:
    return CATEGORY_WEIGHTS.get(get_sector_category(sector), CATEGORY_WEIGHTS["default"])


def get_theme_bonus(themes: List[str]) -> float:
    if not themes:
        return 0.0
    total = 0.0
    for t in themes:
        total += THEME_BONUS.get(t, 0)
    return min(total, 5.0)  # 보너스 상한 5점


def is_growth_sector(sector: str) -> bool:
    cat = get_sector_category(sector)
    return cat.startswith("growth")


def is_value_sector(sector: str) -> bool:
    cat = get_sector_category(sector)
    return cat.startswith("value")
