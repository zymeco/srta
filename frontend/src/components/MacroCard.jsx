import React from 'react'
import { formatNumber, formatPct } from '../utils/formatters.js'

export default function MacroCard({ macro }) {
  if (!macro || Object.keys(macro).length === 0) return null
  const items = Object.entries(macro)
  return (
    <div className="card">
      <h3>🌍 매크로 지표</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
        {items.map(([k, v]) => (
          <div key={k} style={{
            padding: '10px 12px',
            borderRadius: 10,
            background: 'rgba(15,19,28,0.45)',
            border: '1px solid var(--border)',
          }}>
            <div className="subtle" style={{ fontSize: 11, marginBottom: 2 }}>{v.name}</div>
            <div style={{ fontSize: 15, fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
              {formatNumber(v.current, 2)} {v.unit || ''}
            </div>
            <div style={{ fontSize: 12, marginTop: 2, fontVariantNumeric: 'tabular-nums' }}>
              <span className={v.change_rate >= 0 ? 'pos' : 'neg'}>{formatPct(v.change_rate)}</span>
              <span className="subtle" style={{ marginLeft: 6 }}>1M {formatPct(v.month_change)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
