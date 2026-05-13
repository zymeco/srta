import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import { formatPct } from '../utils/formatters.js'

export default function BacktestCard({ bt }) {
  if (!bt || !bt.available) return null
  const returns = bt.returns || {}
  return (
    <div className="card">
      <h3>⏱️ 과거 진입 시뮬레이션</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8, marginBottom: 10 }}>
        {Object.entries(returns).map(([k, v]) => (
          <div key={k} style={{
            padding: '10px 12px',
            borderRadius: 10,
            background: 'rgba(15,19,28,0.45)',
            border: '1px solid var(--border)',
          }}>
            <div className="subtle" style={{ fontSize: 11 }}>{k} 매수 시</div>
            <div className={'pos' === (v > 0 ? 'pos' : 'neg') ? 'pos' : ''} style={{
              fontSize: 16, fontWeight: 700, marginTop: 2, fontVariantNumeric: 'tabular-nums',
              color: v > 0 ? 'var(--green)' : v < 0 ? 'var(--red)' : 'var(--text)',
            }}>
              {formatPct(v)}
            </div>
          </div>
        ))}
      </div>

      {bt.series && bt.series.length > 0 && (
        <div style={{ width: '100%', height: 180 }}>
          <ResponsiveContainer>
            <LineChart data={bt.series} margin={{ top: 10, right: 12, bottom: 0, left: -10 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.08)" vertical={false} />
              <XAxis dataKey="date" stroke="#94a3b8" fontSize={10} hide />
              <YAxis stroke="#94a3b8" fontSize={10} width={50} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{ background: 'rgba(15,19,28,0.95)', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 10 }}
                formatter={(v) => `${v}%`}
              />
              <ReferenceLine y={0} stroke="rgba(148,163,184,0.4)" />
              <Line type="monotone" dataKey="return_pct" stroke="#a78bfa" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
      <div className="subtle" style={{ fontSize: 11, marginTop: 6 }}>
        ※ 1년 전 매수가 기준 누적 수익률
      </div>
    </div>
  )
}
