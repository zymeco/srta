import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { formatWon } from '../utils/formatters.js'

export default function FinancialCard({ data }) {
  if (!data) return null
  return (
    <div className="card">
      <h3>재무 안정성</h3>
      <div className="kv"><span className="k">부채비율</span><span className="v">{data.debt_ratio}%</span></div>
      <div className="kv"><span className="k">유동비율</span><span className="v">{data.current_ratio}%</span></div>
      <div className="kv"><span className="k">당좌비율</span><span className="v">{data.quick_ratio}%</span></div>
      <div className="kv"><span className="k">유보율</span><span className="v">{data.retained_ratio}%</span></div>
      <div className="kv"><span className="k">영업현금흐름</span><span className="v">{formatWon(data.operating_cash_flow)}</span></div>
      <div className="kv"><span className="k">이자보상배율</span><span className="v">{data.interest_coverage}</span></div>

      <div style={{ width: '100%', height: 180, marginTop: 10 }}>
        <ResponsiveContainer>
          <BarChart data={[
            { name: '부채비율', value: data.debt_ratio || 0 },
            { name: '유동비율', value: data.current_ratio || 0 },
            { name: 'ROE', value: data.roe || 0 },
            { name: '영업이익률', value: data.operating_margin || 0 },
          ]} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis dataKey="name" stroke="#9ca3af" fontSize={11} />
            <YAxis stroke="#9ca3af" fontSize={11} />
            <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #334155', borderRadius: 8 }} />
            <Bar dataKey="value" fill="#34d399" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
