import React from 'react'

/**
 * 개인정보처리방침
 * Play Store 배포에 필수. URL: https://your-domain/privacy
 * 회사명/연락처는 배포 전 본인 정보로 수정하세요.
 */
export default function PrivacyPage() {
  return (
    <div>
      <h1 className="title-big" style={{ marginTop: 4 }}>개인정보처리방침</h1>
      <div className="subtle" style={{ marginBottom: 12 }}>최종 업데이트: 2026-05-12</div>

      <div className="card">
        <h3>1. 수집하는 정보</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 앱(Stock Real Trader Analyzer, 이하 "본 앱")은 사용자의 개인 식별 정보를 수집하지 않습니다.<br /><br />
          본 앱은 사용자의 종목 검색 기록, 관심종목, 분석 결과 이력을 <b>사용자의 로컬 디바이스 또는 서버 측 SQLite 데이터베이스</b>에 저장합니다.
          이 데이터는 사용자 식별 정보를 포함하지 않으며 외부로 전송되지 않습니다.
        </div>
      </div>

      <div className="card">
        <h3>2. 외부 API 사용</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 앱은 다음 외부 서비스를 분석 목적으로만 호출합니다:
          <ul>
            <li>한국거래소(KRX) · 네이버 금융: 종목 마스터 / 시세 / 뉴스</li>
            <li>금융감독원 DART OpenAPI: 재무·공시 데이터</li>
            <li>Anthropic Claude API / Google Gemini API: 분석 결과의 자연어 해설 (선택 기능)</li>
          </ul>
          위 호출에는 사용자 개인 정보가 포함되지 않으며, 분석 대상 종목 코드와 분석 결과 일부만 전송됩니다.
        </div>
      </div>

      <div className="card">
        <h3>3. 광고 / 추적</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 앱은 광고를 표시하지 않으며 사용자 행동 추적 도구를 사용하지 않습니다.
        </div>
      </div>

      <div className="card">
        <h3>4. 투자 면책</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 앱이 제공하는 분석 결과는 <b>투자 추천이 아닌 투자 판단 보조 도구</b>이며,
          본 앱의 정보를 기반으로 한 모든 투자 결정의 결과 책임은 사용자 본인에게 있습니다.
          본 앱은 투자 손실에 대해 책임지지 않습니다.
        </div>
      </div>

      <div className="card">
        <h3>5. 문의</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          개인정보 처리 관련 문의: <b>zymeco@gmail.com</b>
        </div>
      </div>

      <div className="subtle center" style={{ marginTop: 16, fontSize: 12 }}>
        © 2026 Stock Real Trader Analyzer
      </div>
    </div>
  )
}
