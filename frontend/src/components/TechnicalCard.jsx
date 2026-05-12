import React from 'react'

export default function TechnicalCard({ data }) {
  if (!data) return null
  return (
    <div className="card">
      <h3>차트/기술적 분석</h3>
      <div className="kv"><span className="k">5일선</span><span className="v">{data.ma5}</span></div>
      <div className="kv"><span className="k">20일선</span><span className="v">{data.ma20}</span></div>
      <div className="kv"><span className="k">60일선</span><span className="v">{data.ma60}</span></div>
      <div className="kv"><span className="k">120일선</span><span className="v">{data.ma120}</span></div>
      <div className="kv"><span className="k">RSI</span><span className="v">{data.rsi}</span></div>
      <div className="kv"><span className="k">볼린저 상단</span><span className="v">{data.bb_upper}</span></div>
      <div className="kv"><span className="k">볼린저 하단</span><span className="v">{data.bb_lower}</span></div>
      <div className="kv"><span className="k">지지선</span><span className="v">{data.support}</span></div>
      <div className="kv"><span className="k">저항선</span><span className="v">{data.resistance}</span></div>
    </div>
  )
}
