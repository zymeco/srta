# 실제 뉴스 API 연동용 구조 (현재는 빈 구현).

from typing import Dict, Any


class NewsProvider:
    def get_news_data(self, stock_code: str) -> Dict[str, Any]:
        raise NotImplementedError("실제 뉴스 API 미연동")
