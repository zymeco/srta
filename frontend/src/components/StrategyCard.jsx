import React from 'react'
import { formatPrice, formatPct } from '../utils/formatters.js'

export default function StrategyCard({ strategy, currentPrice, forbidden }) {
  if (!strategy) return null
  return (
    <div className="card">
      <h3>매매 전략</h3>
      <div className="kv"><span className="k">현재가</span><span className="v">{formatPrice(currentPrice)}원</span></div>
      <div className="kv"><span className="k">관심 매수가</span><span className="v">{forbidden ? '제시하지 않음' : strategy.buy_zone}</span></div>
      <div className="kv"><span className="k">1차 목표가</span><span className="v pos">{forbidden ? '-' : formatPrice(strategy.target_price_1) + '원'}</span></div>
      <div className="kv"><span className="k">2차 목표가</span><span className="v pos">{forbidden ? '-' : formatPrice(strategy.target_price_2) + '원'}</span></div>
      <div className="kv"><span className="k">손절가</span><span className="v neg">{typeof strategy.stop_loss === 'number' ? formatPrice(strategy.stop_loss) + '원' : strategy.stop_loss}</span></div>
      <div className="kv"><span className="k">예상 손익비</span><span className="v">{strategy.risk_reward_ratio ?? '-'}</span></div>
      {!forbidden && (
        <>
          <div className="kv"><span className="k">목표 수익률</span><span className="v pos">{formatPct(strategy.target_return_rate)}</span></div>
          <div className="kv"><span className="k">예상 손절률</span><span className="v neg">{formatPct(strategy.stop_loss_rate)}</span></div>
        </>
      )}
      <div className="kv"><span className="k">추격매수 위험도</span>
        <span className={
          'tag ' + (
            strategy.chasing_risk === '낮음' ? 'green' :
            strategy.chasing_risk === '중간' ? 'yellow' : 'red'
          )
        }>{strategy.chasing_risk}</span>
      </div>
      <div className="kv"><span className="k">권장 전략</span><span className="v">{strategy.strategy_type}</span></div>
    </div>
  )
}
