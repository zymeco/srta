import React from 'react'
import { formatNumber } from '../utils/formatters.js'

export default function ValuationCard({ data }) {
  if (!data) return null
  return (
    <div className="card">
      <h3>밸류에이션</h3>
      <div className="kv"><span className="k">PER</span><span className="v">{formatNumber(data.per, 2)} 배</span></div>
      {data.forward_per != null && data.forward_per > 0 && <div className="kv"><span className="k">추정 PER (Forward)</span><span className="v pos">{formatNumber(data.forward_per, 2)} 배</span></div>}
      <div className="kv"><span className="k">PBR</span><span className="v">{formatNumber(data.pbr, 2)} 배</span></div>
      <div className="kv"><span className="k">PSR</span><span className="v">{formatNumber(data.psr, 2)} 배</span></div>
      <div className="kv"><span className="k">EV/EBITDA</span><span className="v">{formatNumber(data.ev_ebitda, 2)}</span></div>
      <div className="kv"><span className="k">업종 평균 PER</span><span className="v">{formatNumber(data.sector_per, 2)} 배</span></div>
      {data.eps != null && <div className="kv"><span className="k">EPS</span><span className="v">{formatNumber(data.eps, 0)}</span></div>}
      {data.bps != null && <div className="kv"><span className="k">BPS</span><span className="v">{formatNumber(data.bps, 0)}</span></div>}
      {data.dividend_yield != null && <div className="kv"><span className="k">배당수익률</span><span className="v">{formatNumber(data.dividend_yield, 2)} %</span></div>}
    </div>
  )
}
