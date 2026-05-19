import React from 'react'
import { formatPct, formatNumber } from '../utils/formatters.js'

const STATE_COLOR = {
  '강한 상승장': '#34d399',
  '상승장': '#86efac',
  '약한 상승': '#a7f3d0',
  '단기 조정 / 추세 유지': '#fbbf24',
  '횡보': '#94a3b8',
  '조정 중': '#fb923c',
  '하락장': '#fb923c',
  '강한 하락장': '#f87171',
  '급락 / 강한 하락': '#ef4444',
  '정보부족': '#64748b',
}

export default function MarketContextCard({ market, macroText, adjustment }) {
  if (!market) return null
  const color = STATE_COLOR[market.state] || '#94a3b8'
  return (
    <div className="card" style={{ borderLeft: `3px solid ${color}` }}>
      <h3>🌐 시장 컨텍스트</h3>
      <div className="row space" style={{ marginBottom: 8 }}>
        <div>
          <div className="subtle" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            {market.market || 'KOSPI'} 추세
          </div>
          <div style={{ fontSize: 20, fontWeight: 800, color, marginTop: 2 }}>
            {market.state}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="subtle" style={{ fontSize: 11 }}>지수</div>
          <div style={{ fontSize: 18, fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
            {formatNumber(market.current, 2)}
          </div>
        </div>
      </div>
      <div className="row" style={{ gap: 6, flexWrap: 'wrap' }}>
        <span className={'tag ' + (market.change_5d >= 0 ? 'green' : 'red')}>5일 {formatPct(market.change_5d)}</span>
        <span className={'tag ' + (market.change_20d >= 0 ? 'green' : 'red')}>20일 {formatPct(market.change_20d)}</span>
        <span className={'tag ' + (market.change_60d >= 0 ? 'green' : 'red')}>60일 {formatPct(market.change_60d)}</span>
      </div>

      {adjustment && adjustment.before_adjust != null && (
        <div className="subtle" style={{ fontSize: 12, marginTop: 10, padding: 8, background: 'rgba(15,19,28,0.45)', borderRadius: 8 }}>
          시장 보정: 점수 {formatNumber(adjustment.before_adjust, 1)} →
          <b style={{ color, marginLeft: 4 }}>{formatNumber(adjustment.after_adjust, 1)}</b>
          {adjustment.chasing_multiplier !== 1.0 && (
            <span style={{ marginLeft: 8 }}>· 추격위험 {adjustment.chasing_multiplier > 1 ? '↑' : '↓'} 보정</span>
          )}
        </div>
      )}

      {macroText && macroText !== '특이사항 없음' && (
        <div className="subtle" style={{ fontSize: 12, marginTop: 6 }}>
          💱 글로벌: {macroText}
        </div>
      )}
    </div>
  )
}
