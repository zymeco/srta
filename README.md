# Stock Real Trader Analyzer

한국 주식 종목을 입력하면 재무·실적·밸류에이션·차트·거래량·수급·뉴스·리스크·투자 포지션·매매 전략을 자동으로 분석해 주는 모바일 중심 PWA 웹앱입니다.

> ⚠️ 본 도구는 **투자 추천이 아닌 투자 판단 보조 도구**입니다. 최종 투자 결정은 본인의 책임 하에 이루어져야 합니다.

---

## 1. 주요 기능

- 종목명/종목코드 입력 → 한 번에 종합 분석
- 100점 만점 종합 점수 (소수점 1자리)
- 단기/스윙/중기/장기 **투자 포지션 자동 판단**
- 매수가 / 1·2차 목표가 / 손절가 / 손익비 자동 산출
- **매수 금지·접근 금지 강력 경고 배너** (리스크 우선 원칙)
- Recharts 기반 차트/게이지 시각화
- **PDF 리포트 저장** (한글 깨짐 방지 화면 캡처 방식)
- 관심종목 / 분석 이력 / 최근 검색 저장 (SQLite)
- **PWA**: 안드로이드 Chrome 홈 화면 추가 가능

---

## 2. 폴더 구조

```
stock-real-trader-analyzer/
├─ backend/        FastAPI + 분석 엔진 + SQLite + MockProvider
├─ frontend/       Vite + React + Recharts + html2canvas/jsPDF
├─ run_dev.bat     백/프론트 동시 실행 스크립트
└─ README.md
```

세부 구조는 요청 사양 그대로 생성되어 있습니다 (backend/analysis/*, data_provider/*, api/*, frontend/src/components/*, pages/* 등).

---

## 3. 사전 준비 (Windows)

### Python 3.10+ 설치 확인
```
python --version
```

### Node.js 18+ 설치 확인
```
node --version
npm --version
```

설치되어 있지 않다면:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

## 4. 실행 방법

### (A) 가장 쉬운 방법 — 배치 파일
프로젝트 루트에서:
```
run_dev.bat
```
백엔드/프론트엔드 창이 각각 새로 뜨고, 의존성 설치 후 자동 실행됩니다.

### (B) 수동 실행

**백엔드 (포트 8000)**
```cmd
cd C:\☆코딩\종목분석기
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**프론트엔드 (포트 5173)**
```cmd
cd C:\☆코딩\종목분석기\frontend
npm install
npm run dev -- --host 0.0.0.0
```

브라우저: http://localhost:5173

---

## 5. 안드로이드 스마트폰에서 접속

1. PC와 폰이 **같은 와이파이**에 연결되어 있어야 합니다.
2. PC에서 cmd 창을 열고 `ipconfig` 실행 → "IPv4 주소" 확인 (예: `192.168.0.12`).
3. 폰 Chrome에서 다음 주소로 접속:
   ```
   http://192.168.0.12:5173
   ```
4. 우측 상단 메뉴 → **"홈 화면에 추가"** 를 누르면 앱 아이콘이 생기고, 실행 시 standalone PWA로 동작합니다.

> Windows 방화벽 알림이 뜨면 "사설/홈 네트워크" 허용을 선택하세요.

---

## 6. PDF 리포트 저장 방법

1. 종목을 분석한 뒤, 화면 하단의 **"📄 PDF 리포트 보기"** 버튼을 누릅니다 (또는 직접 `/report/종목코드`).
2. 상단/하단의 **"📄 PDF 리포트 저장"** 버튼 클릭.
3. 잠시 기다리면 PDF가 자동 다운로드 됩니다.
   - 파일명: `종목명_종목코드_분석리포트_YYYYMMDD.pdf`
   - 안드로이드: Chrome **다운로드 폴더**에서 확인 가능.

분석 데이터가 없을 때 누르면 *"먼저 종목 분석을 실행해주세요."*, PDF 생성 실패 시 *"PDF 생성 중 오류가 발생했습니다. 다시 시도해주세요."* 가 표시됩니다.

---

## 7. API 키 설정 (AI + 데이터)

`backend/keys/api_keys.py` 또는 **환경변수**로 설정합니다 (환경변수가 우선).

| 변수 | 용도 | 발급처 (모두 무료) |
|------|------|--------|
| `ANTHROPIC_API_KEY` | Claude AI 자연어 분석 | https://console.anthropic.com |
| `GEMINI_API_KEY` | Gemini AI 자연어 분석 | https://aistudio.google.com/apikey |
| `DART_API_KEY` | **재무·공시·관리종목** (정확도 핵심) | https://opendart.fss.or.kr/ |
| `NAVER_CLIENT_ID` | 네이버 뉴스 검색 | https://developers.naver.com/apps |
| `NAVER_CLIENT_SECRET` | 네이버 뉴스 검색 | 위와 동일 |
| `AI_PROVIDER_DEFAULT` | `auto`/`claude`/`gemini` (기본 `auto`) | - |
| `DATA_PROVIDER` | `real`/`pykrx`/`mock` (기본 `real`) | - |

### 데이터 소스별 역할
- **pykrx** (자동, 키 불필요): 실시세, MA/RSI/MACD/볼린저, 거래량, 외국인·기관 수급, PER/PBR/EPS/BPS, 52주 고저
- **DART** (`DART_API_KEY`): 부채비율·유동비율·현금흐름·자본잠식·매출/영업이익 성장률 + 유상증자/전환사채/감사의견/관리종목/상장폐지 공시 자동 감지
- **네이버** (`NAVER_CLIENT_*`): 실시간 뉴스 · 긍정/부정 감성 · 테마 추출
- **AI** (`ANTHROPIC_API_KEY` 또는 `GEMINI_API_KEY`): 분석 결과를 한국어 자연어로 해설

키가 없는 영역은 자동으로 Mock 폴백되므로 일부만 등록해도 동작합니다. **5개 키 모두 등록하면 체크리스트의 18개 분석 항목이 전부 실데이터로 작동합니다.**

```python
# 로컬 실행 시
ANTHROPIC_API_KEY = "sk-ant-..."
GEMINI_API_KEY = "AIza..."
```

## 7-1. 클라우드 배포 (Render.com 무료)

폰 단독으로 어디서나 사용하려면 백엔드를 클라우드에 올리세요.

1. 이 프로젝트를 GitHub에 push
2. https://render.com 가입 → **New + → Blueprint** → 저장소 선택
3. `render.yaml` 자동 감지됨 → Deploy
4. 발급된 `https://xxx.onrender.com` 주소 확인
5. Render 대시보드 → Environment → `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` 입력 → Save
6. 갤럭시 Chrome에서 위 주소 접속 → **⋮ 메뉴 → "홈 화면에 추가"** → 끝

이제 PC를 켤 필요 없이 갤럭시 홈 아이콘 한 번으로 어디서나 실시간 분석 + AI 해설이 됩니다.

---

## 8. 더미 데이터 → 실제 API 교체 방법

분석 로직과 데이터 소스는 분리되어 있습니다. 분석 코드를 건드릴 필요가 없습니다.

1. `backend/data_provider/` 안의 `stock_price_provider.py`, `financial_provider.py`, `news_provider.py`, `supply_provider.py` 중 사용할 것을 골라 실제 API 호출을 구현합니다 (`raise NotImplementedError` 부분).
2. `MockProvider`와 동일한 함수 시그니처(`get_stock_basic_info`, `get_price_history`, `get_financial_data`, `get_supply_data`, `get_news_data`, `get_risk_data`)를 갖는 통합 Provider 클래스를 만들거나, 기존 MockProvider 메서드를 부분적으로 실 API로 교체합니다.
3. `backend/analysis/final_report_builder.py` 상단의 `MockProvider()` 인스턴스를 새 Provider로 교체합니다.

예시 후보 라이브러리:
- 시세/차트: `pykrx`, `yfinance`
- 재무: OpenDART API
- 뉴스: Naver Search API

---

## 9. 오류 발생 시 확인할 점

| 증상 | 점검 |
|------|------|
| 프론트에서 `네트워크 오류` | 백엔드(8000) 미실행 → `uvicorn` 창 확인 |
| 폰에서 PC IP 접속 안 됨 | Windows 방화벽에서 5173/8000 포트 허용 |
| `npm install` 실패 | Node 18 이상인지 확인 |
| `pip install` 실패 | Python 3.10 이상인지 확인 |
| PDF 한글 깨짐 | 본 앱은 화면 캡처(JPEG) 기반이라 한글이 항상 정상 표시됨 |
| 분석은 되는데 차트 빈 화면 | 한 번 새로고침 (Recharts 첫 렌더 이슈) |
| DB 관련 에러 | `backend/db/app.db` 삭제 후 재실행 (자동 재생성) |

---

## 10. 핵심 동작 원칙

이 프로그램은 **추천보다 리스크 관리가 우선**입니다.

- 점수가 높아도 **관리종목/자본잠식/감사의견 문제/거래정지** 등 치명적 리스크가 있으면 → 자동 **접근 금지**
- 점수가 높아도 **유상증자/전환사채/신주인수권/신용잔고 과열** 등 강한 리스크 2개 이상이면 → **매수 금지**
- 매수 금지 종목은 매수가/목표가를 **제시하지 않습니다.**
- 추격매수 위험이 크면 화면 상단에 **경고 배너**가 먼저 표시됩니다.

---

## 11. 테스트 종목 (Mock)

| 코드 | 이름 | 상태 |
|------|------|------|
| 005930 | 삼성전자 | 정상 |
| 000660 | SK하이닉스 | 정상 |
| 247540 | 에코프로비엠 | 정상 |
| 000000 | 위험종목 | 강한 리스크 발현 (매수 금지/접근 금지 테스트) |
| 111111 | 관리종목테스트 | 관리종목/자본잠식 (접근 금지 배너 테스트) |

---

본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다.
