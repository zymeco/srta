import React from 'react'

/**
 * 이용약관 (Play Store 권장 페이지)
 */
export default function TermsPage() {
  return (
    <div>
      <h1 className="title-big" style={{ marginTop: 4 }}>이용약관</h1>
      <div className="subtle" style={{ marginBottom: 12 }}>최종 업데이트: 2026-05-12</div>

      <div className="card">
        <h3>1. 서비스 소개</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          Stock Real Trader Analyzer(이하 "본 서비스")는 한국 주식 종목의 재무, 차트, 수급, 뉴스, 리스크 정보를
          분석하여 시각화하는 <b>투자 판단 보조 도구</b>입니다. 본 서비스는 특정 종목의 매수/매도를 권유하지 않습니다.
        </div>
      </div>

      <div className="card">
        <h3>2. 면책 조항</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 서비스가 제공하는 모든 분석 결과, 점수, 매매 전략, 추천 포지션 등은 참고 자료이며 정확성과 적시성을 보장하지 않습니다.<br /><br />
          본 서비스를 이용한 투자 결정으로 발생한 손익은 전적으로 사용자 본인의 책임이며,
          본 서비스 및 개발자는 어떠한 법적 책임도 지지 않습니다.
        </div>
      </div>

      <div className="card">
        <h3>3. 데이터 출처</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 서비스는 KRX, 네이버 금융, 금융감독원 DART 등 공개된 데이터 소스를 활용합니다.
          데이터 제공처의 정책 변경 또는 일시적 장애로 인해 서비스가 제한될 수 있습니다.
        </div>
      </div>

      <div className="card">
        <h3>4. 사용 제한</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 서비스를 상업적 재배포, 무단 크롤링, 자동화된 대량 요청 등에 사용할 수 없습니다.
        </div>
      </div>

      <div className="card">
        <h3>5. 약관 변경</h3>
        <div style={{ lineHeight: 1.7, color: 'var(--text-2)', fontSize: 14 }}>
          본 약관은 사전 통지 없이 변경될 수 있으며, 변경된 약관은 본 앱 내 게시 시점부터 효력을 가집니다.
        </div>
      </div>
    </div>
  )
}
