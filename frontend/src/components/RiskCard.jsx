import React from 'react'

const LABELS = {
  management_stock: '관리종목',
  investment_warning: '투자경고',
  investment_danger: '투자위험',
  capital_impairment: '자본잠식',
  trading_halt_history: '거래정지 이력',
  audit_issue: '감사의견 문제',
  delisting_risk: '상장폐지 위험',
  unfaithful_disclosure: '불성실공시',
  three_year_loss: '3년 연속 적자',
  rights_issue: '유상증자',
  convertible_bond: '전환사채',
  warrant: '신주인수권',
  largest_shareholder_change: '최대주주 변경',
  credit_overheat: '신용잔고 과열',
  short_selling_spike: '공매도 급증',
  low_liquidity: '유동성 부족',
  manipulation_pattern: '작전주 의심',
  pump_then_volume_drop: '급등 후 거래량 감소',
}

// 위험 등급별 색상
const LEVEL_STYLE = {
  0: { color: '#6ee7b7', bg: 'rgba(52,211,153,0.14)', border: 'rgba(52,211,153,0.4)', label: '안전', icon: '✓' },
  1: { color: '#fde68a', bg: 'rgba(251,191,36,0.14)', border: 'rgba(251,191,36,0.4)', label: '주의', icon: '⚠️' },
  2: { color: '#fdba74', bg: 'rgba(251,146,60,0.14)', border: 'rgba(251,146,60,0.4)', label: '강한 주의', icon: '⚠️' },
  3: { color: '#fca5a5', bg: 'rgba(248,113,113,0.14)', border: 'rgba(248,113,113,0.5)', label: '매수 금지', icon: '🚫' },
  4: { color: '#fff',    bg: 'rgba(239,68,68,0.20)',  border: 'rgba(239,68,68,0.65)',  label: '접근 금지', icon: '🚨' },
}

export default function RiskCard({ flags, riskLevel, riskLabel }) {
  if (!flags) return null
  const onItems = Object.entries(flags).filter(([, v]) => v).map(([k]) => k)
  const onCount = onItems.length
  const lvl = LEVEL_STYLE[riskLevel] || LEVEL_STYLE[0]

  return (
    <div className="card" style={{ borderLeft: `3px solid ${lvl.color}` }}>
      <h3>리스크 필터</h3>

      {/* 위험 등급 배너 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 12,
        padding: '14px 16px',
        borderRadius: 14,
        background: lvl.bg,
        border: `1px solid ${lvl.border}`,
        marginBottom: 14,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          <div style={{ fontSize: 28, lineHeight: 1 }}>{lvl.icon}</div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 11, opacity: 0.8, textTransform: 'uppercase', letterSpacing: '0.08em', color: lvl.color }}>
              위험 등급 {riskLevel} 단계
            </div>
            <div style={{ fontSize: 18, fontWeight: 800, color: lvl.color, marginTop: 2 }}>
              {riskLabel || lvl.label}
            </div>
          </div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: 11, opacity: 0.8, color: lvl.color, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            감지된 플래그
          </div>
          <div style={{ fontSize: 26, fontWeight: 900, color: lvl.color, fontVariantNumeric: 'tabular-nums' }}>
            {onCount}<span style={{ fontSize: 14, opacity: 0.7 }}> / {Object.keys(LABELS).length}</span>
          </div>
        </div>
      </div>

      {/* 감지된 항목 우선 표시 */}
      {onCount > 0 && (
        <div style={{ marginBottom: 12 }}>
          <div className="subtle" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
            ⚠️ 감지된 위험 ({onCount})
          </div>
          <div className="row wrap" style={{ gap: 6 }}>
            {onItems.map(k => (
              <span key={k} className="tag red">{LABELS[k] || k}</span>
            ))}
          </div>
        </div>
      )}

      {onCount === 0 && (
        <div style={{
          padding: '14px',
          borderRadius: 12,
          background: 'rgba(52,211,153,0.08)',
          border: '1px solid rgba(52,211,153,0.25)',
          color: '#6ee7b7',
          textAlign: 'center',
          marginBottom: 12,
          fontWeight: 600,
        }}>
          ✓ 현재 감지된 치명적 리스크 없음
        </div>
      )}

      {/* 전체 18종 체크리스트 */}
      <div className="subtle" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
        전체 리스크 체크리스트
      </div>
      <div className="flag-grid">
        {Object.keys(LABELS).map(k => (
          <div key={k} className={`flag ${flags[k] ? 'on' : ''}`}>
            <span>{LABELS[k]}</span>
            <span className="dot" />
          </div>
        ))}
      </div>
    </div>
  )
}
