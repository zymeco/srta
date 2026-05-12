import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function VolumeChart({ volumes }) {
  if (!volumes || volumes.length === 0) return null
  const data = volumes.slice(-60)
  return (
    <div className="card">
      <h3>거래량 (최근 60일)</h3>
      <div style={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis dataKey="date" stroke="#9ca3af" fontSize={10} hide />
            <YAxis
              stroke="#9ca3af" fontSize={10} width={56}
              tickFormatter={(v) => {
                const n = Number(v)
                if (n >= 1e8) return (n / 1e8).toFixed(1) + '억'
                if (n >= 1e4) return (n / 1e4).toFixed(0) + '만'
                return n.toLocaleString('ko-KR')
              }}
            />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: '1px solid #334155', borderRadius: 8 }}
              formatter={(v) => Number(v).toLocaleString('ko-KR')}
            />
            <Bar dataKey="volume" fill="#60a5fa" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
