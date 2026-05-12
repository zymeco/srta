import React from 'react'
import { ComposedChart, Area, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'

export default function ChartCard({ ma }) {
  if (!ma || ma.length === 0) return null
  const data = ma.slice(-90)
  return (
    <div className="card">
      <h3>주가 / 이동평균선 (최근 90일)</h3>
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <ComposedChart data={data} margin={{ top: 10, right: 12, bottom: 0, left: -10 }}>
            <defs>
              <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#818cf8" stopOpacity={0.5}/>
                <stop offset="100%" stopColor="#818cf8" stopOpacity={0.0}/>
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.08)" vertical={false} />
            <XAxis dataKey="date" stroke="#64748b" fontSize={10} hide />
            <YAxis
              stroke="#64748b" fontSize={10} domain={['auto', 'auto']} width={64}
              tickFormatter={(v) => {
                const n = Number(v)
                if (Math.abs(n) >= 100000) return (n / 10000).toFixed(0) + '만'
                return n.toLocaleString('ko-KR')
              }}
            />
            <Tooltip
              contentStyle={{
                background: 'rgba(15,19,28,0.95)',
                border: '1px solid rgba(148,163,184,0.2)',
                borderRadius: 10,
                backdropFilter: 'blur(8px)',
              }}
              labelStyle={{ color: '#cbd5e1' }}
              formatter={(v) => Number(v).toLocaleString('ko-KR')}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
            <Area type="monotone" dataKey="close" stroke="#c7d2fe" fill="url(#priceFill)" strokeWidth={2} name="종가" />
            <Line type="monotone" dataKey="ma5"  stroke="#fbbf24" dot={false} strokeWidth={1.4} name="MA5" />
            <Line type="monotone" dataKey="ma20" stroke="#34d399" dot={false} strokeWidth={1.4} name="MA20" />
            <Line type="monotone" dataKey="ma60" stroke="#60a5fa" dot={false} strokeWidth={1.4} name="MA60" />
            <Line type="monotone" dataKey="ma120" stroke="#f472b6" dot={false} strokeWidth={1.4} name="MA120" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
