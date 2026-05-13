import React from 'react'
import { formatPrice, formatPct, formatNumber, formatWon } from '../utils/formatters.js'

export default function PeerComparisonCard({ peer }) {
  if (!peer || !peer.available) {
    return (
      <div className="card">
        <h3>📊 동종 업종 비교</h3>
        <div className="subtle">{peer?.reason || '비교 데이터 없음'}</div>
      </div>
    )
  }
  const rows = peer.rows || []
  return (
    <div className="card">
      <h3>📊 동종 업종 비교 ({peer.sector})</h3>
      <div className="row" style={{ gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
        <span className="tag">평균 PER {formatNumber(peer.avg_per, 2)}</span>
        <span className="tag">평균 PBR {formatNumber(peer.avg_pbr, 2)}</span>
        {peer.avg_div_yield > 0 && <span className="tag">평균 배당 {formatNumber(peer.avg_div_yield, 2)}%</span>}
        {peer.self_per_rank > 0 && <span className="tag brand">PER 순위 {peer.self_per_rank}/{peer.total_count}</span>}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ color: 'var(--text-dim)', textAlign: 'left' }}>
              <th style={{ padding: '6px 4px' }}>종목</th>
              <th style={{ padding: '6px 4px', textAlign: 'right' }}>현재가</th>
              <th style={{ padding: '6px 4px', textAlign: 'right' }}>등락</th>
              <th style={{ padding: '6px 4px', textAlign: 'right' }}>PER</th>
              <th style={{ padding: '6px 4px', textAlign: 'right' }}>PBR</th>
              <th style={{ padding: '6px 4px', textAlign: 'right' }}>시총</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.stock_code} style={{
                background: r.is_self ? 'rgba(129,140,248,0.15)' : 'transparent',
                borderTop: '1px solid var(--border)',
              }}>
                <td style={{ padding: '6px 4px', fontWeight: r.is_self ? 700 : 500 }}>
                  {r.is_self && '★ '}{r.stock_name}
                </td>
                <td style={{ padding: '6px 4px', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{formatPrice(r.current_price)}</td>
                <td style={{ padding: '6px 4px', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }} className={r.change_rate >= 0 ? 'pos' : 'neg'}>
                  {formatPct(r.change_rate)}
                </td>
                <td style={{ padding: '6px 4px', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{formatNumber(r.per, 2)}</td>
                <td style={{ padding: '6px 4px', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{formatNumber(r.pbr, 2)}</td>
                <td style={{ padding: '6px 4px', textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{formatWon(r.market_cap)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
