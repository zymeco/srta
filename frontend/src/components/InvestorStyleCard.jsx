import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'

const STYLE_META = {
  graham:   { label: '그레이엄',  desc: '저PER·저PBR·배당·안전마진',     color: '#34d399', icon: '📘' },
  buffett:  { label: '버핏',      desc: '높은 ROE·안정 마진·낮은 부채',   color: '#fbbf24', icon: '🛡️' },
  lynch:    { label: '린치',      desc: 'PEG·성장가치(GARP)',           color: '#60a5fa', icon: '🚀' },
  momentum: { label: '모멘텀',    desc: '추세·신고가·거래량',             color: '#f472b6', icon: '⚡' },
}

export default function InvestorStyleCard({ investorStyles }) {
  if (!investorStyles?.styles) return null
  const styles = investorStyles.styles
  const bestKey = investorStyles.best_style

  const data = Object.entries(styles).map(([k, v]) => ({
    name: STYLE_META[k].label,
    key: k,
    score: v.score,
    color: STYLE_META[k].color,
  }))

  const bestReasons = styles[bestKey]?.reasons || []

  return (
    <div className="card">
      <h3>투자 스타일 평가</h3>

      <div style={{
        padding: '12px 14px',
        borderRadius: 12,
        background: `${STYLE_META[bestKey].color}22`,
        border: `1px solid ${STYLE_META[bestKey].color}55`,
        marginBottom: 12,
      }}>
        <div className="row" style={{ alignItems: 'center', gap: 10 }}>
          <div style={{ fontSize: 24 }}>{STYLE_META[bestKey].icon}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 11, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              가장 적합한 스타일
            </div>
            <div style={{ fontSize: 17, fontWeight: 800, color: STYLE_META[bestKey].color }}>
              {STYLE_META[bestKey].label} ({styles[bestKey].score}점)
            </div>
            <div className="subtle" style={{ fontSize: 12, marginTop: 2 }}>
              {STYLE_META[bestKey].desc}
            </div>
          </div>
        </div>
      </div>

      <div style={{ width: '100%', height: 180 }}>
        <ResponsiveContainer>
          <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, bottom: 0, left: 50 }}>
            <CartesianGrid stroke="rgba(148,163,184,0.08)" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" fontSize={11} />
            <YAxis type="category" dataKey="name" stroke="#cbd5e1" fontSize={12} tickLine={false} width={60} />
            <Tooltip
              contentStyle={{ background: 'rgba(15,19,28,0.95)', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 10 }}
              cursor={{ fill: 'rgba(148,163,184,0.08)' }}
            />
            <Bar dataKey="score" radius={[0, 8, 8, 0]} barSize={20}>
              {data.map((d) => <Cell key={d.key} fill={d.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {bestReasons.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div className="subtle" style={{ fontSize: 11, marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>주요 이유</div>
          <div className="row wrap" style={{ gap: 4 }}>
            {bestReasons.map((r, i) => (
              <span key={i} className="tag" style={{ background: `${STYLE_META[bestKey].color}1a`, color: STYLE_META[bestKey].color, borderColor: `${STYLE_META[bestKey].color}55` }}>{r}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
