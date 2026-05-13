import React from 'react'
import { formatNumber } from '../utils/formatters.js'

// 고급 지표 — 한눈에 보는 그리드
export default function AdvancedMetricsCard({ metrics }) {
  if (!metrics) return null

  const items = [
    { label: 'PEG',        value: metrics.peg, fmt: (v) => v ? `${v}` : '-', tip: 'PER / 이익성장률, 1 미만 저평가 성장주' },
    { label: '최대낙폭',    value: metrics.mdd, fmt: (v) => `${v}%`, tip: '52주 내 최대 하락폭' },
    { label: 'ATR (14)',   value: metrics.atr, fmt: (v) => formatNumber(v, 0), tip: '평균 일일 변동폭' },
    { label: '연환산변동성', value: metrics.volatility_20d, fmt: (v) => `${v}%`, tip: '20일 수익률 표준편차의 연환산' },
    { label: '20일 모멘텀', value: metrics.momentum_20d, fmt: (v) => `${v}%`, color: true, tip: '최근 20거래일 수익률' },
    { label: '60일 모멘텀', value: metrics.momentum_60d, fmt: (v) => `${v}%`, color: true, tip: '최근 60거래일 수익률' },
    { label: 'OBV 추세',   value: metrics.obv_trend, fmt: (v) => v, tip: 'On-Balance Volume — 거래량 추세' },
    { label: '52주 신고가 근접', value: metrics.near_high_pct, fmt: (v) => `${v}%`, tip: '100%이면 신고가' },
  ]

  function colorOf(item) {
    if (!item.color) return 'var(--text)'
    const n = Number(item.value)
    if (!isFinite(n)) return 'var(--text)'
    if (n > 0) return 'var(--green)'
    if (n < 0) return 'var(--red)'
    return 'var(--text)'
  }

  return (
    <div className="card">
      <h3>고급 지표</h3>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: 8,
      }}>
        {items.map((it, i) => (
          <div key={i} style={{
            padding: '10px 12px',
            borderRadius: 12,
            background: 'rgba(15,19,28,0.45)',
            border: '1px solid var(--border)',
          }} title={it.tip}>
            <div style={{ fontSize: 11, color: 'var(--text-mute)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {it.label}
            </div>
            <div style={{
              fontSize: 16, fontWeight: 700, marginTop: 2,
              fontVariantNumeric: 'tabular-nums',
              color: colorOf(it),
            }}>
              {it.value != null ? it.fmt(it.value) : '-'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
