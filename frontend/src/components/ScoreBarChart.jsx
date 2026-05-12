import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const LABELS = {
  financial: '재무',
  growth: '성장',
  valuation: '밸류',
  technical: '차트',
  volume: '거래량',
  supply: '수급',
  news_theme: '뉴스',
  risk: '리스크',
  timing: '타이밍',
}
const MAX = {
  financial: 15, growth: 15, valuation: 10, technical: 15,
  volume: 10, supply: 10, news_theme: 10, risk: 10, timing: 5,
}

export default function ScoreBarChart({ scores }) {
  if (!scores) return null
  const data = Object.keys(LABELS).map(k => ({
    name: LABELS[k],
    score: scores[k] || 0,
    max: MAX[k],
    pct: ((scores[k] || 0) / MAX[k]) * 100,
  }))
  return (
    <div style={{ width: '100%', height: 240 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
          <defs>
            <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"   stopColor="#c084fc" />
              <stop offset="100%" stopColor="#818cf8" />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(148,163,184,0.08)" vertical={false} />
          <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
          <YAxis stroke="#94a3b8" fontSize={11} domain={[0, 100]} tickLine={false} />
          <Tooltip
            contentStyle={{
              background: 'rgba(15,19,28,0.95)',
              border: '1px solid rgba(148,163,184,0.2)',
              borderRadius: 10,
            }}
            formatter={(v, _name, props) => [`${props.payload.score} / ${props.payload.max}`, '점수']}
            labelStyle={{ color: '#cbd5e1' }}
          />
          <Bar dataKey="pct" fill="url(#barGrad)" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
