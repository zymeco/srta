import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'

const POS_LABEL = {
  day_trading: '초단기',
  short_term: '단기',
  swing: '스윙',
  mid_term: '중기',
  long_term: '장기',
}

export default function PositionCard({ position }) {
  if (!position) return null
  const scores = position.position_scores || {}
  const data = Object.keys(POS_LABEL).map(k => ({ name: POS_LABEL[k], score: scores[k] || 0, key: k }))
  const maxKey = data.reduce((a, b) => (a.score >= b.score ? a : b)).key

  return (
    <div className="card">
      <h3>투자 포지션 판단</h3>

      <div className="row space" style={{ marginBottom: 10 }}>
        <div>
          <div className="subtle" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            추천 투자 방식
          </div>
          <div className="title-big" style={{ margin: '2px 0 0', background: 'var(--grad-brand)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>
            {position.recommended_position}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="subtle" style={{ fontSize: 11 }}>예상 보유 기간</div>
          <div style={{ fontWeight: 700, fontSize: 16, marginTop: 2 }}>{position.expected_holding_period}</div>
        </div>
      </div>

      <div className="kv"><span className="k">현재 접근 판단</span><span className="v">{position.current_entry_status}</span></div>
      <div style={{ padding: '8px 0' }}>
        <div className="subtle" style={{ marginBottom: 4, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          최고 수익 전략
        </div>
        <div style={{ color: 'var(--text-2)', fontSize: 14, lineHeight: 1.6 }}>{position.best_profit_strategy}</div>
      </div>

      <div style={{ width: '100%', height: 200, marginTop: 6 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
            <defs>
              <linearGradient id="posBest" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#f472b6" />
                <stop offset="100%" stopColor="#c084fc" />
              </linearGradient>
              <linearGradient id="posOther" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#60a5fa" stopOpacity={0.85} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.65} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.08)" vertical={false} />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} />
            <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} tickLine={false} />
            <Tooltip
              contentStyle={{ background: 'rgba(15,19,28,0.95)', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 10 }}
              labelStyle={{ color: '#cbd5e1' }}
            />
            <Bar dataKey="score" radius={[8, 8, 0, 0]}>
              {data.map(d => (
                <Cell key={d.key} fill={d.key === maxKey ? 'url(#posBest)' : 'url(#posOther)'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {position.reason && position.reason.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div className="subtle" style={{ marginBottom: 4, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            추천 이유
          </div>
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {position.reason.map((r, i) => <li key={i} style={{ marginBottom: 4, fontSize: 13, color: 'var(--text-2)' }}>{r}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}
