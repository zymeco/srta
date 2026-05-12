import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

const COLORS = { '긍정': '#34d399', '중립': '#9ca3af', '부정': '#f87171' }

export default function NewsCard({ news }) {
  if (!news) return null
  const items = news.items || []
  const sc = news.sentiment_counts || {}
  const pie = [
    { name: '긍정', value: sc.positive || 0 },
    { name: '중립', value: sc.neutral || 0 },
    { name: '부정', value: sc.negative || 0 },
  ]
  return (
    <div className="card">
      <h3>뉴스 / 공시 / 테마</h3>
      <div className="row" style={{ flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
        {(news.themes || []).map((t, i) => <span key={i} className="tag blue">#{t}</span>)}
        {news.policy_benefit && <span className="tag green">정책 수혜</span>}
        {news.disclosure_risk && <span className="tag red">공시 위험</span>}
        {news.rights_issue && <span className="tag red">유상증자</span>}
        {news.convertible_bond && <span className="tag red">전환사채</span>}
      </div>

      <div style={{ width: '100%', height: 160 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie data={pie} dataKey="value" nameKey="name" outerRadius={60} label>
              {pie.map((d, i) => <Cell key={i} fill={COLORS[d.name]} />)}
            </Pie>
            <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #334155', borderRadius: 8 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: 6 }}>
        {items.slice(0, 6).map((n, i) => (
          <div key={i} className="list-row" style={{ marginBottom: 6 }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>{n.title}</div>
              <div className="subtle">{n.source} · {n.date}</div>
            </div>
            <span className={
              'tag ' + (n.sentiment === 'positive' ? 'green' : n.sentiment === 'negative' ? 'red' : '')
            }>
              {n.sentiment === 'positive' ? '긍정' : n.sentiment === 'negative' ? '부정' : '중립'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
