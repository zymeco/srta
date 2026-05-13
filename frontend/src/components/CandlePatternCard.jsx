import React from 'react'

const TYPE_COLOR = {
  bullish: { bg: 'rgba(52,211,153,0.15)', color: '#6ee7b7', border: 'rgba(52,211,153,0.4)' },
  bearish: { bg: 'rgba(248,113,113,0.15)', color: '#fca5a5', border: 'rgba(248,113,113,0.4)' },
  neutral: { bg: 'rgba(148,163,184,0.15)', color: '#cbd5e1', border: 'rgba(148,163,184,0.4)' },
}

export default function CandlePatternCard({ candles }) {
  if (!candles) return null
  const patterns = candles.patterns || []
  return (
    <div className="card">
      <h3>🕯️ 캔들 패턴 분석</h3>
      <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 8 }}>{candles.signal}</div>
      {patterns.length === 0 ? (
        <div className="subtle">특별한 캔들 패턴이 감지되지 않았습니다.</div>
      ) : (
        <div className="row wrap" style={{ gap: 6 }}>
          {patterns.map((p, i) => {
            const s = TYPE_COLOR[p.type] || TYPE_COLOR.neutral
            return (
              <div key={i} style={{
                padding: '8px 12px',
                borderRadius: 10,
                background: s.bg,
                border: `1px solid ${s.border}`,
                color: s.color,
                fontSize: 13,
              }}>
                <b>{p.name}</b> · {p.signal}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
