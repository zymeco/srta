import React from 'react'

export default function EarningsCard({ earnings }) {
  if (!earnings) return null
  const imminent = earnings.is_imminent
  const days = earnings.days_until
  const color = imminent ? '#f87171' : days <= 21 ? '#fbbf24' : '#94a3b8'
  return (
    <div className="card" style={{ borderLeft: `3px solid ${color}` }}>
      <h3>📅 실적 발표 캘린더</h3>
      <div className="kv"><span className="k">다음 발표 분기</span><span className="v">{earnings.next_period}</span></div>
      <div className="kv"><span className="k">예상 발표 시즌</span><span className="v">{earnings.expected_window}</span></div>
      {days >= 0 && (
        <div className="kv"><span className="k">남은 일수</span><span className="v" style={{ color }}>D-{days}</span></div>
      )}
      {imminent && (
        <div style={{
          padding: 10,
          background: 'rgba(248,113,113,0.15)',
          border: '1px solid rgba(248,113,113,0.4)',
          color: '#fca5a5',
          borderRadius: 10,
          marginTop: 8,
          fontSize: 13,
          fontWeight: 700,
        }}>
          {earnings.note}
        </div>
      )}
    </div>
  )
}
