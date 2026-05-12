import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function GrowthCard({ data, growthTrend }) {
  if (!data) return null
  return (
    <div className="card">
      <h3>실적 성장성</h3>
      <div className="kv"><span className="k">매출 성장률</span><span className="v">{data.revenue_growth}%</span></div>
      <div className="kv"><span className="k">영업이익 성장률</span><span className="v">{data.operating_growth}%</span></div>
      <div className="kv"><span className="k">순이익 성장률</span><span className="v">{data.net_income_growth}%</span></div>
      <div className="kv"><span className="k">영업이익률</span><span className="v">{data.operating_margin}%</span></div>
      <div className="kv"><span className="k">ROE</span><span className="v">{data.roe}%</span></div>
      <div className="kv"><span className="k">EPS 성장률</span><span className="v">{data.eps_growth}%</span></div>

      {growthTrend && growthTrend.length > 0 && (
        <div style={{ width: '100%', height: 180, marginTop: 10 }}>
          <ResponsiveContainer>
            <BarChart data={growthTrend} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
              <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
              <XAxis dataKey="year" stroke="#9ca3af" fontSize={11} />
              <YAxis stroke="#9ca3af" fontSize={11} />
              <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #334155', borderRadius: 8 }} />
              <Bar dataKey="value" fill="#60a5fa" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
