import React from 'react'
import { formatPrice, formatNumber } from '../utils/formatters.js'

export default function TechnicalCard({ data }) {
  if (!data) return null
  return (
    <div className="card">
      <h3>차트/기술적 분석</h3>
      <div className="kv"><span className="k">5일 이동평균선</span><span className="v">{formatPrice(data.ma5)}</span></div>
      <div className="kv"><span className="k">20일 이동평균선</span><span className="v">{formatPrice(data.ma20)}</span></div>
      <div className="kv"><span className="k">60일 이동평균선</span><span className="v">{formatPrice(data.ma60)}</span></div>
      <div className="kv"><span className="k">120일 이동평균선</span><span className="v">{formatPrice(data.ma120)}</span></div>
      <div className="kv"><span className="k">RSI (14)</span><span className="v">{formatNumber(data.rsi, 1)}</span></div>
      <div className="kv"><span className="k">볼린저 상단</span><span className="v">{formatPrice(data.bb_upper)}</span></div>
      <div className="kv"><span className="k">볼린저 하단</span><span className="v">{formatPrice(data.bb_lower)}</span></div>
      <div className="kv"><span className="k">지지선</span><span className="v">{formatPrice(data.support)}</span></div>
      <div className="kv"><span className="k">저항선</span><span className="v">{formatPrice(data.resistance)}</span></div>
    </div>
  )
}
