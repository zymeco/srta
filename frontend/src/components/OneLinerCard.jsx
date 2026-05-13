import React from 'react'
import { gradeColor } from '../utils/formatters.js'

// 한 줄 결론 — 가장 먼저 봐야 할 핵심
export default function OneLinerCard({ oneLiner, opinion, grade, totalScore }) {
  if (!oneLiner) return null
  const color = gradeColor(grade)
  return (
    <div className="card glow" style={{
      background: `linear-gradient(135deg, ${color}22 0%, rgba(28,34,49,0.6) 100%)`,
      borderLeft: `3px solid ${color}`,
    }}>
      <div className="row" style={{ alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
        <div className="grade-pill" style={{ background: color, flexShrink: 0 }}>{grade}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 11, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>한 줄 결론</div>
          <div style={{ fontSize: 17, fontWeight: 800, lineHeight: 1.4, marginTop: 2 }}>{oneLiner}</div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>종합</div>
          <div style={{ fontSize: 22, fontWeight: 900, color: color, fontVariantNumeric: 'tabular-nums' }}>{totalScore}</div>
        </div>
      </div>
    </div>
  )
}
