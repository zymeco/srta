import React from 'react'
import { formatPrice, formatPct } from '../utils/formatters.js'

export default function ConsensusCard({ consensus }) {
  if (!consensus || !consensus.available) return null
  const upside = consensus.upside_pct || 0
  const color = upside > 10 ? 'var(--green)' : upside > 0 ? 'var(--blue)' : 'var(--red)'
  return (
    <div className="card">
      <h3>🎯 증권사 컨센서스 ({consensus.report_count}개 리포트)</h3>
      <div className="row space" style={{ alignItems: 'center' }}>
        <div>
          <div className="subtle" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>평균 목표가</div>
          <div style={{ fontSize: 26, fontWeight: 900, color, fontVariantNumeric: 'tabular-nums' }}>
            {formatPrice(consensus.target_price)}원
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="subtle" style={{ fontSize: 11 }}>상승 여력</div>
          <div style={{ fontSize: 22, fontWeight: 800, color, fontVariantNumeric: 'tabular-nums' }}>
            {formatPct(upside)}
          </div>
        </div>
      </div>
      {consensus.opinion && (
        <div className="kv" style={{ marginTop: 8 }}>
          <span className="k">투자의견</span><span className="v">{consensus.opinion}</span>
        </div>
      )}
      {consensus.recent_reports?.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div className="subtle" style={{ fontSize: 11, marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>최근 리포트</div>
          {consensus.recent_reports.map((r, i) => (
            <div key={i} className="list-row" style={{ marginBottom: 6, padding: 8 }}>
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{r.title}</div>
                <div className="subtle" style={{ fontSize: 11 }}>{r.broker} · {r.date}</div>
              </div>
              {r.target_price > 0 && (
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: 13 }}>{formatPrice(r.target_price)}</div>
                  {r.opinion && <div className="subtle" style={{ fontSize: 11 }}>{r.opinion}</div>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
