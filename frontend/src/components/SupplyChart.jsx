import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'

export default function SupplyChart({ supply, detail }) {
  if (!supply || supply.length === 0) return null
  // 누적 수급 라인
  const data = []
  let f = 0, i = 0, ind = 0
  supply.forEach(d => {
    f += d.foreign || 0
    i += d.institution || 0
    ind += d.individual || 0
    data.push({ date: d.date, 외국인: f, 기관: i, 개인: ind })
  })

  return (
    <div className="card">
      <h3>수급 분석 (누적, 20일)</h3>
      <div className="kv"><span className="k">외국인 5일 순매수</span><span className="v">{detail?.foreign_5d?.toLocaleString?.()}</span></div>
      <div className="kv"><span className="k">외국인 20일 순매수</span><span className="v">{detail?.foreign_20d?.toLocaleString?.()}</span></div>
      <div className="kv"><span className="k">기관 5일 순매수</span><span className="v">{detail?.institution_5d?.toLocaleString?.()}</span></div>
      <div className="kv"><span className="k">기관 20일 순매수</span><span className="v">{detail?.institution_20d?.toLocaleString?.()}</span></div>
      <div className="kv"><span className="k">공매도 비중</span><span className="v">{detail?.short_selling_ratio}%</span></div>
      <div className="kv"><span className="k">신용잔고</span><span className="v">{detail?.credit_balance_ratio}%</span></div>

      <div style={{ width: '100%', height: 220, marginTop: 10 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis dataKey="date" stroke="#9ca3af" fontSize={10} hide />
            <YAxis
              stroke="#9ca3af" fontSize={10} width={56}
              tickFormatter={(v) => Number(v).toLocaleString('ko-KR')}
            />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: '1px solid #334155', borderRadius: 8 }}
              formatter={(v) => Number(v).toLocaleString('ko-KR')}
            />
            <Legend />
            <Line dataKey="외국인" stroke="#60a5fa" dot={false} />
            <Line dataKey="기관" stroke="#a78bfa" dot={false} />
            <Line dataKey="개인" stroke="#fbbf24" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
