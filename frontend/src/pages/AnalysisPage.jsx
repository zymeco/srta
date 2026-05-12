import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { formatPrice, formatPct, formatWon, marketCapLabel } from '../utils/formatters.js'
import StrongWarningBanner from '../components/StrongWarningBanner.jsx'
import ScoreGauge from '../components/ScoreGauge.jsx'
import ScoreBarChart from '../components/ScoreBarChart.jsx'
import PositionCard from '../components/PositionCard.jsx'
import SummaryCard from '../components/SummaryCard.jsx'
import StrategyCard from '../components/StrategyCard.jsx'
import RiskCard from '../components/RiskCard.jsx'
import FinancialCard from '../components/FinancialCard.jsx'
import GrowthCard from '../components/GrowthCard.jsx'
import ValuationCard from '../components/ValuationCard.jsx'
import TechnicalCard from '../components/TechnicalCard.jsx'
import VolumeChart from '../components/VolumeChart.jsx'
import SupplyChart from '../components/SupplyChart.jsx'
import NewsCard from '../components/NewsCard.jsx'
import ChartCard from '../components/ChartCard.jsx'
import AiAdvisorCard from '../components/AiAdvisorCard.jsx'

export default function AnalysisPage() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  useEffect(() => {
    let alive = true
    setLoading(true); setErr('')
    api.analyze(code)
      .then(d => { if (alive) setData(d) })
      .catch(e => { if (alive) setErr(e.message) })
      .finally(() => { if (alive) setLoading(false) })
    return () => { alive = false }
  }, [code])

  if (loading) {
    return (
      <div className="card center">
        <div className="spinner" />
        <div style={{ marginTop: 8 }} className="subtle">분석 중…</div>
      </div>
    )
  }
  if (err) {
    return <div className="error-banner">분석 실패: {err}</div>
  }
  if (!data) return null

  const forbidden = data.strong_warning?.is_buy_forbidden

  return (
    <div>
      <StrongWarningBanner riskLevel={data.risk_level} warning={data.strong_warning} />

      <div className="hero-card">
        <div className="row space" style={{ alignItems: 'flex-start' }}>
          <div style={{ minWidth: 0 }}>
            <div className="ticker-name">{data.stock_name}</div>
            <div className="ticker-meta">
              {data.stock_code} · {data.market} · {data.sector || '—'} · {marketCapLabel(data.market_cap_type)}
            </div>
          </div>
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <div className="price">{formatPrice(data.current_price)}<span style={{ fontSize: 16, color: 'var(--text-dim)', marginLeft: 4 }}>원</span></div>
            <div style={{ marginTop: 6 }}>
              <span className={'change ' + (Number(data.change_rate) >= 0 ? 'up' : 'down')}>
                {Number(data.change_rate) >= 0 ? '▲' : '▼'} {formatPct(data.change_rate)}
              </span>
            </div>
          </div>
        </div>

        <div className="stat-grid">
          <div className="stat">
            <div className="label">시가총액</div>
            <div className="value">{formatWon(data.market_cap)}</div>
          </div>
          <div className="stat">
            <div className="label">거래량</div>
            <div className="value">{formatWon(data.volume)}</div>
          </div>
          <div className="stat">
            <div className="label">52주 고가</div>
            <div className="value">{formatPrice(data.high_52w)}</div>
          </div>
          <div className="stat">
            <div className="label">52주 저가</div>
            <div className="value">{formatPrice(data.low_52w)}</div>
          </div>
        </div>
      </div>

      <div className="card glow">
        <h3>종합 점수</h3>
        <ScoreGauge score={data.total_score} grade={data.grade} opinion={data.final_opinion} />
      </div>

      <div className="card">
        <h3>항목별 점수</h3>
        <ScoreBarChart scores={data.scores} />
      </div>

      <PositionCard position={data.position_analysis} />

      <SummaryCard summary={data.summary} />

      <AiAdvisorCard stockCode={data.stock_code} />

      <StrategyCard strategy={data.strategy} currentPrice={data.current_price} forbidden={forbidden} />

      <FinancialCard data={data.financial_detail} />
      <GrowthCard data={data.financial_detail} growthTrend={data.charts?.growth} />
      <ValuationCard data={data.financial_detail} />
      <TechnicalCard data={data.technical_detail} />

      <ChartCard ma={data.charts?.moving_average} />
      <VolumeChart volumes={data.charts?.volume} />
      <SupplyChart supply={data.charts?.supply} detail={data.supply_detail} />
      <NewsCard news={data.news} />

      <RiskCard flags={data.risk_flags} riskLevel={data.risk_level} riskLabel={data.risk_label} />

      <div className="card">
        <h3>최종 판단</h3>
        <div style={{ fontSize: 15, lineHeight: 1.6 }}>{data.final_comment}</div>
        <div className="subtle" style={{ marginTop: 10, fontSize: 12 }}>
          {data.disclaimer}
        </div>
      </div>

      <div className="row" style={{ gap: 8 }}>
        <button className="btn full" onClick={() => api.addWatchlist(data.stock_code, data.stock_name).then(() => alert('관심종목에 추가했습니다.')).catch(e => alert(e.message))}>
          ⭐ 관심종목 추가
        </button>
        <button className="btn primary full" onClick={() => navigate(`/report/${data.stock_code}`)}>
          📄 PDF 리포트 보기
        </button>
      </div>

      <div className="subtle center" style={{ marginTop: 16, fontSize: 12 }}>
        본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다.
      </div>
    </div>
  )
}
