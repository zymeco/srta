import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { formatPrice, formatPct, formatWon, marketCapLabel } from '../utils/formatters.js'

import StrongWarningBanner from '../components/StrongWarningBanner.jsx'
import OneLinerCard from '../components/OneLinerCard.jsx'
import ScoreGauge from '../components/ScoreGauge.jsx'
import InvestorStyleCard from '../components/InvestorStyleCard.jsx'
import PositionCard from '../components/PositionCard.jsx'
import SummaryCard from '../components/SummaryCard.jsx'
import StrategyCard from '../components/StrategyCard.jsx'
import RiskCard from '../components/RiskCard.jsx'
import AiAdvisorCard from '../components/AiAdvisorCard.jsx'
import AdvancedMetricsCard from '../components/AdvancedMetricsCard.jsx'
import MarketContextCard from '../components/MarketContextCard.jsx'
import PeerComparisonCard from '../components/PeerComparisonCard.jsx'
import ConsensusCard from '../components/ConsensusCard.jsx'
import CandlePatternCard from '../components/CandlePatternCard.jsx'
import BacktestCard from '../components/BacktestCard.jsx'
import MacroCard from '../components/MacroCard.jsx'
import EarningsCard from '../components/EarningsCard.jsx'
import ChatBot from '../components/ChatBot.jsx'
import CollapsibleSection from '../components/CollapsibleSection.jsx'

import ScoreBarChart from '../components/ScoreBarChart.jsx'
import FinancialCard from '../components/FinancialCard.jsx'
import GrowthCard from '../components/GrowthCard.jsx'
import ValuationCard from '../components/ValuationCard.jsx'
import TechnicalCard from '../components/TechnicalCard.jsx'
import VolumeChart from '../components/VolumeChart.jsx'
import SupplyChart from '../components/SupplyChart.jsx'
import NewsCard from '../components/NewsCard.jsx'
import ChartCard from '../components/ChartCard.jsx'

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
      {/* === 최상단: 강력 경고 + 종목 헤더 === */}
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
          <div className="stat"><div className="label">시가총액</div><div className="value">{formatWon(data.market_cap)}</div></div>
          <div className="stat"><div className="label">거래량</div><div className="value">{formatWon(data.volume)}</div></div>
          <div className="stat"><div className="label">52주 고가</div><div className="value">{formatPrice(data.high_52w)}</div></div>
          <div className="stat"><div className="label">52주 저가</div><div className="value">{formatPrice(data.low_52w)}</div></div>
        </div>
      </div>

      {/* === 핵심: 한 줄 결론 === */}
      <OneLinerCard
        oneLiner={data.one_liner}
        opinion={data.final_opinion}
        grade={data.grade}
        totalScore={data.total_score}
      />

      {/* === 종합 점수 게이지 === */}
      <div className="card glow">
        <h3>종합 점수</h3>
        <ScoreGauge score={data.total_score} grade={data.grade} opinion={data.final_opinion} />
      </div>

      {/* === 시장 컨텍스트 + 컨센서스 (의사결정 핵심) === */}
      <MarketContextCard market={data.market_context} macroText={data.macro_text} />
      <ConsensusCard consensus={data.consensus} />

      {/* === 투자 스타일 4종 === */}
      <InvestorStyleCard investorStyles={data.investor_styles} />

      {/* === 매매 전략 === */}
      <StrategyCard strategy={data.strategy} currentPrice={data.current_price} forbidden={forbidden} />

      {/* === 동종 업종 비교 === */}
      <PeerComparisonCard peer={data.peer_comparison} />

      {/* === 실적 발표 캘린더 === */}
      <EarningsCard earnings={data.earnings} />

      {/* === 핵심 요약 === */}
      <SummaryCard summary={data.summary} />

      {/* === 포지션 판단 === */}
      <PositionCard position={data.position_analysis} />

      {/* === 캔들 패턴 === */}
      <CandlePatternCard candles={data.candle_patterns} />

      {/* === AI 자연어 분석 + 챗봇 === */}
      <AiAdvisorCard stockCode={data.stock_code} />
      <ChatBot stockCode={data.stock_code} stockName={data.stock_name} />

      {/* === 리스크 필터 === */}
      <RiskCard flags={data.risk_flags} riskLevel={data.risk_level} riskLabel={data.risk_label} />

      {/* === 접기: 고급 지표 + 세부 데이터 === */}
      <CollapsibleSection title="📈 고급 지표 (PEG · MDD · ATR · 모멘텀 · 변동성 · OBV)">
        <AdvancedMetricsCard metrics={data.advanced_metrics} />
      </CollapsibleSection>

      <CollapsibleSection title="📊 주가 차트 / 이동평균선" defaultOpen={true}>
        <ChartCard ma={data.charts?.moving_average} />
      </CollapsibleSection>

      <CollapsibleSection title="📉 항목별 점수 분해 (재무 · 성장 · 밸류 · 차트 · 거래량 · 수급 · 뉴스 · 리스크 · 타이밍)">
        <div className="card">
          <h3>항목별 점수</h3>
          <ScoreBarChart scores={data.scores} />
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="💰 재무 · 성장 · 밸류에이션">
        <FinancialCard data={data.financial_detail} />
        <GrowthCard data={data.financial_detail} growthTrend={data.charts?.growth} />
        <ValuationCard data={data.financial_detail} />
      </CollapsibleSection>

      <CollapsibleSection title="🔬 기술적 지표">
        <TechnicalCard data={data.technical_detail} />
      </CollapsibleSection>

      <CollapsibleSection title="📊 거래량 · 수급">
        <VolumeChart volumes={data.charts?.volume} />
        <SupplyChart supply={data.charts?.supply} detail={data.supply_detail} />
      </CollapsibleSection>

      <CollapsibleSection title="⏱️ 과거 진입 시뮬레이션 (백테스트)">
        <BacktestCard bt={data.backtest} />
      </CollapsibleSection>

      <CollapsibleSection title="🌍 매크로 지표 (환율 · 미국시장 · VIX)">
        <MacroCard macro={data.macro} />
      </CollapsibleSection>

      <CollapsibleSection title="📰 뉴스 · 테마">
        <NewsCard news={data.news} />
      </CollapsibleSection>

      {/* === 최종 자연어 판단 === */}
      <div className="card">
        <h3>최종 판단</h3>
        <div style={{ fontSize: 15, lineHeight: 1.6 }}>{data.final_comment}</div>
        <div className="subtle" style={{ marginTop: 10, fontSize: 12 }}>
          {data.disclaimer}
        </div>
      </div>

      {/* === 액션 버튼 === */}
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
