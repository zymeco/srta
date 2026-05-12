# Play Store 배포 가이드 — SRTA

이 문서는 **Stock Real Trader Analyzer**를 Google Play Store에 출시하는 전체 과정을 단계별로 안내합니다.

> 총 소요 시간: 코딩 0분(이미 준비됨) + 배포·검수 1~3일 + 심사 1~7일
> 비용: Google Play 개발자 계정 **$25 (1회 결제, 평생)**

---

## 📋 전체 흐름

```
[A] 클라우드 배포 (Render)          ← 공개 HTTPS URL 발급
[B] PWA 품질 확인 (이미 준비 완료)   ← 매니페스트·아이콘·SW
[C] PWABuilder로 .aab 빌드           ← 클릭 몇 번
[D] Google Play Console 가입         ← $25
[E] 앱 등록 / 자료 업로드            ← 스크린샷·설명
[F] Internal Testing → Production    ← 심사
```

---

## A. 클라우드 배포 (Render.com)

### 1) GitHub에 코드 push
```cmd
cd C:\☆코딩\종목분석기
git init
git add .
git commit -m "initial commit"
```

GitHub에서 새 저장소 생성 후:
```cmd
git remote add origin https://github.com/<본인계정>/srta.git
git branch -M main
git push -u origin main
```

> Git 미설치: https://git-scm.com/download/win

### 2) Render 배포
1. https://render.com 가입 (GitHub 로그인)
2. 우측 상단 **New + → Blueprint**
3. 위 저장소 선택 → `render.yaml` 자동 감지 → **Apply**
4. 빌드 5~10분 대기

### 3) 환경변수 입력
서비스 → **Environment** 탭에서 키 입력 (선택):
- `ANTHROPIC_API_KEY` 또는 `GEMINI_API_KEY`
- `DART_API_KEY`
- `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`

### 4) URL 확인
배포 완료 시 `https://srta.onrender.com` 같은 주소 발급 — 이 URL을 메모해두세요.

> ⚠️ Play Store에 등록할 URL은 HTTPS여야 함. Render는 HTTPS 자동 제공.
> ⚠️ 무료 플랜은 15분 비활성 후 sleep. 첫 접속 5~10초 대기.
> 유료($7/월)는 sleep 없음.

---

## B. PWA 품질 검증

### Lighthouse 점수 확인
배포된 URL에서 Chrome 개발자 도구 → **Lighthouse** → "Progressive Web App" 체크 → Analyze.

목표: **PWA 인증 마크 ✓ 통과**

체크 항목 (이미 코드에 모두 구현됨):
- ✅ manifest.json (id, name, short_name, start_url, scope, display, icons[192,512,maskable])
- ✅ service-worker 등록
- ✅ HTTPS (Render 자동)
- ✅ theme_color, background_color
- ✅ apple-touch-icon
- ✅ description, lang

### PWABuilder 점수 확인
1. https://www.pwabuilder.com 접속
2. 배포 URL 입력 → **Start**
3. 점수 확인 — 30점 이상이면 Android 패키지 생성 가능
4. 본 프로젝트는 **80~95점**이 기본으로 나옴

---

## C. PWABuilder로 .aab 빌드

1. https://www.pwabuilder.com 에서 URL 입력 후 분석
2. 상단 **Package For Stores** 클릭
3. **Android** 탭 선택
4. 설정 입력:
   - **Package ID**: `com.yourname.srta` (역도메인 형식, 변경 불가)
   - **App name**: Stock Real Trader Analyzer
   - **Launcher name**: SRTA
   - **App version**: 1.0.0
   - **App version code**: 1
   - **Display mode**: Standalone
   - **Status bar color**: #0c1018
   - **Splash color**: #07090f
   - **Signing key**: **"Create new"** 선택 (PWABuilder가 자동 생성)
   - ⚠️ **생성된 signing key는 반드시 안전한 곳에 백업하세요. 분실 시 업데이트 불가**
5. **Generate** → ZIP 다운로드
6. ZIP 내 `app-release-signed.aab` 파일이 Play Store 업로드용

---

## D. Google Play Console 가입

1. https://play.google.com/console 접속
2. Google 계정으로 로그인
3. **개발자 등록** → 개인/사업자 선택
4. $25 결제 (Visa/Master 카드)
5. 신원 확인 (개인: 신분증, 사업자: 사업자등록증)
6. 승인까지 보통 1~2일

---

## E. 앱 등록

### 1) 앱 만들기
Play Console → **앱 만들기**:
- 앱 이름: Stock Real Trader Analyzer
- 기본 언어: 한국어
- 앱/게임: 앱
- 무료/유료: 무료

### 2) 필수 정보 (좌측 메뉴 순서대로)

#### 앱 콘텐츠
| 항목 | 내용 |
|------|------|
| 개인정보처리방침 URL | `https://your-domain.onrender.com/privacy` |
| 앱 액세스 권한 | 모든 기능 무료 사용 가능 |
| 광고 | 광고 없음 |
| 콘텐츠 등급 설문 | "유틸리티/생산성/통신" 선택, 모든 항목 "아니요" → 보통 3세 이상 |
| 타겟층 | 18세 이상 (금융 정보 특성) |
| 뉴스 앱 | 아니요 |
| COVID-19 / 의료 | 아니요 |
| 데이터 보안 | 수집 데이터 없음으로 신고 가능 (관심종목/이력은 서버 측 저장이고 개인 식별 불가) |
| 정부 앱 | 아니요 |
| 금융 기능 | "투자 자문 제공 안 함" 체크 — 본 앱은 분석 도구일 뿐이므로 |

#### 스토어 등록정보
- **앱 이름**: Stock Real Trader Analyzer (30자 이내)
- **간단한 설명** (80자):
  > 한국 주식 종목 종합 분석 — 재무·차트·수급·리스크·AI 해설을 한 번에
- **자세한 설명** (4000자 이내): 아래 [F. 설명 템플릿] 참고
- **앱 아이콘**: `frontend/public/icons/icon-512.png` 업로드
- **그래픽 이미지** (Feature Graphic, 1024 × 500 PNG): 별도 제작 필요 (Canva, Figma 등)
- **스크린샷**: 폰 2~8장 필수 (1080 × 1920 권장)
  - 갤럭시에서 PWA 실행 후 캡처
  - 검색, 분석 결과, 매매 전략, 리스크 필터 화면 등
- **카테고리**: 금융
- **태그**: 주식, 증권, 분석, 핀테크

#### 출시 트랙
1. **내부 테스트** (Internal Testing) — 최대 100명, 즉시 사용 가능
   - `app-release-signed.aab` 업로드
   - 테스터 Gmail 추가 (본인 계정 포함)
   - 테스트 URL 받아서 갤럭시에서 설치
2. 검증 끝나면 **프로덕션 트랙**으로 승격
3. 첫 프로덕션 출시는 **검수 1~7일** 소요

---

## F. 자세한 설명 템플릿 (복붙용)

```
📊 Stock Real Trader Analyzer

한국 주식 종목 하나를 입력하면 재무 안정성, 실적 성장성, 차트 추세, 거래량, 수급, 뉴스, 리스크, 투자 포지션, 매수가/목표가/손절가, 손익비, 종합 점수까지 한 번에 분석해주는 모바일 중심 투자 보조 앱입니다.

[ 주요 기능 ]
- 100점 만점 종합 점수 (소수점 1자리, S/A/B/C/D 등급)
- 단기·스윙·중기·장기 투자 포지션 자동 판단
- 매수가 / 1·2차 목표가 / 손절가 / 손익비 자동 산출
- 매수 금지 · 접근 금지 강력 경고 (리스크 우선 원칙)
- KOSPI + KOSDAQ 3,900+ 종목 실시간 검색
- 재무·공시 (DART), 시세 (pykrx), 뉴스 (네이버) 통합 분석
- Claude / Gemini AI 자연어 해설 (선택 기능)
- PDF 분석 리포트 다운로드
- 관심종목·분석 이력 저장
- 다크 모드 모바일 최적화 UI

[ 분석 항목 ]
재무 안정성: 부채비율, 유동비율, 현금흐름, 자본잠식 검사
실적 성장성: 매출/영업이익/순이익 성장률, ROE
밸류에이션: PER, PBR, PSR, EV/EBITDA, 업종 비교
기술적 분석: 이동평균(5/20/60/120), RSI, MACD, 볼린저밴드
거래량: 평균 대비 비율, 단기 급등 후 감소 패턴
수급: 외국인/기관/개인, 공매도, 신용잔고
뉴스/테마: 긍정/부정 감성, 정책 수혜, 공시 위험
리스크 필터 18종: 관리종목, 자본잠식, 감사의견, 유상증자, 전환사채, 신주인수권, 거래정지 이력, 작전주 패턴 등

[ 중요 ]
본 앱은 투자 추천이 아닌 투자 판단 보조 도구입니다.
최종 투자 결정의 책임은 본인에게 있으며, 본 앱의 분석 결과로 인한 손실에 대해 책임지지 않습니다.

문의: zymeco@gmail.com
```

---

## G. 빠른 체크리스트

배포 전 마지막 점검:

- [ ] Render에 배포 완료 (HTTPS URL 확보)
- [ ] `/privacy` 페이지 접근 가능
- [ ] PWABuilder 점수 30+ 확인
- [ ] `.aab` 파일 생성 & signing key 백업 (안전한 곳에 보관)
- [ ] 스크린샷 2~8장 준비
- [ ] Feature Graphic 1024×500 준비
- [ ] 앱 아이콘 512×512 준비 (이미 있음: `icon-512.png`)
- [ ] Play Console $25 결제 완료
- [ ] 개인정보처리방침 URL 입력
- [ ] 콘텐츠 등급 설문 완료
- [ ] Internal Testing으로 본인 갤럭시에서 한 번 설치 테스트
- [ ] 정상 동작 확인 후 Production 승격

---

## 자주 묻는 질문

**Q. Render 무료 플랜의 sleep이 Play Store 심사에 영향?**
A. 영향 있을 수 있습니다. 심사 시 앱이 즉시 동작해야 하므로, 심사 기간 동안만 Render 유료($7/월)로 잠시 올리거나, Fly.io · Railway 등 sleep 없는 무료 옵션을 사용하세요.

**Q. signing key를 잃어버리면?**
A. **앱을 영영 업데이트할 수 없습니다.** Play App Signing(자동)으로 가입 권장 — Google이 키를 대신 보관해줍니다.

**Q. 광고 넣고 싶으면?**
A. Google AdMob 연동. 단 광고 정책 + 콘텐츠 등급 재신고 필요.

**Q. iOS 앱도 만들 수 있나?**
A. PWABuilder가 iOS 패키징도 지원하지만 App Store는 PWA 직접 등록을 사실상 막아둠. iOS는 Safari "홈 화면에 추가" 방식 권장.

**Q. 출시 후 업데이트는?**
A. 코드 수정 → Render 자동 재배포 → 사용자는 새로고침으로 즉시 반영됨 (PWA의 장점).
앱 자체 업데이트(예: Package ID 변경)는 새 `.aab` 빌드 후 Play Console에서 새 버전 업로드.
```

