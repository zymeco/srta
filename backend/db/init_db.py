# 단독 실행용 DB 초기화 스크립트
from .database import init_db

if __name__ == "__main__":
    init_db()
    print("DB initialized.")
