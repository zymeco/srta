import React from 'react'

export default function ValuationCard({ data }) {
  if (!data) return null
  return (
    <div className="card">
      <h3>밸류에이션</h3>
      <div className="kv"><span className="k">PER</span><span className="v">{data.per}</span></div>
      <div className="kv"><span className="k">PBR</span><span className="v">{data.pbr}</span></div>
      <div className="kv"><span className="k">PSR</span><span className="v">{data.psr}</span></div>
      <div className="kv"><span className="k">EV/EBITDA</span><span className="v">{data.ev_ebitda}</span></div>
      <div className="kv"><span className="k">업종 평균 PER</span><span className="v">{data.sector_per}</span></div>
    </div>
  )
}
