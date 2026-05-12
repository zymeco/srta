import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client.js'
import { formatPrice, formatPct, formatWon } from '../utils/formatters.js'
import PdfExportButton from '../components/PdfExportButton.jsx'

const POS_LABEL = {
  day_trading: '초단기', short_term: '단기', swing: '스윙', mid_term: '중기', long_term: '장기',
}

export default function ReportPage() {
  const { code } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  useEffect(() => {
    setLoading(true); setErr('')
    api.analyze(code)
      .then(setData)
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false))
  }, [code])

  if (loading) {
    return <div className="card center"><div className="spinner" /></div>
  }
  if (err) return <div className="error-banner">{err}</div>
  if (!data) return null

  const sw = data.strong_warning || {}
  const lv = `lv${data.risk_level || 0}`
  const pos = data.position_analysis || {}
  const strat = data.strategy || {}
  const forbidden = sw.is_buy_forbidden

  return (
    <div>
      <PdfExportButton
        targetId="pdf-report-area"
        stockName={data.stock_name}
        stockCode={data.stock_code}
      />

      <div id="pdf-report-area">
        <div className="pdf-title">📊 Stock Real Trader Analyzer 분석 리포트</div>
        <div className="pdf-sub">생성일시: {data.generated_at}</div>

        {data.risk_level >= 1 && sw.warning_title && (
          <div className={`pdf-banner ${lv}`}>
            <div style={{ fontSize: 16, marginBottom: 4 }}>{sw.warning_title}</div>
            <div style={{ fontSize: 13, fontWeight: 500 }}>{sw.warning_message}</div>
          </div>
        )}

        <div className="pdf-card">
          <div className="pdf-row"><span className="k">종목명</span><span className="v">{data.stock_name}</span></div>
          <div className="pdf-row"><span className="k">종목코드</span><span className="v">{data.stock_code}</span></div>
          <div className="pdf-row"><span className="k">시장 / 업종</span><span className="v">{data.market} / {data.sector}</span></div>
          <div className="pdf-row"><span className="k">현재가</span><span className="v">{formatPrice(data.current_price)}원 ({formatPct(data.change_rate)})</span></div>
          <div className="pdf-row"><span className="k">시가총액</span><span className="v">{formatWon(data.market_cap)}</span></div>
        </div>

        <div className="pdf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>종합 점수</div>
              <div className="pdf-score">{data.total_score} <span style={{ fontSize: 16 }}>/100</span></div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 12, color: '#6b7280' }}>등급 / 의견</div>
              <div style={{ fontSize: 20, fontWeight: 800 }}>{data.grade} · {data.final_opinion}</div>
            </div>
          </div>
        </div>

        <div className="pdf-card">
          <h3 style={{ marginTop: 0 }}>투자 포지션 판단</h3>
          <div className="pdf-row"><span className="k">추천 투자 방식</span><span className="v">{pos.recommended_position}</span></div>
          <div className="pdf-row"><span className="k">예상 보유 기간</span><span className="v">{pos.expected_holding_period}</span></div>
          <div className="pdf-row"><span className="k">현재 접근 판단</span><span className="v">{pos.current_entry_status}</span></div>
          <div className="pdf-row"><span className="k">최고 수익 전략</span><span className="v">{pos.best_profit_strategy}</span></div>
          <div style={{ marginTop: 8 }}>
            {Object.keys(POS_LABEL).map(k => (
              <div key={k} className="pdf-row">
                <span className="k">{POS_LABEL[k]}</span>
                <span className="v">{pos.position_scores?.[k] ?? '-'}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pdf-card">
          <h3 style={{ marginTop: 0 }}>매매 전략</h3>
          <div className="pdf-row"><span className="k">관심 매수가</span><span className="v">{forbidden ? '제시하지 않음' : strat.buy_zone}</span></div>
          <div className="pdf-row"><span className="k">1차 목표가</span><span className="v">{forbidden ? '-' : formatPrice(strat.target_price_1) + '원'}</span></div>
          <div className="pdf-row"><span className="k">2차 목표가</span><span className="v">{forbidden ? '-' : formatPrice(strat.target_price_2) + '원'}</span></div>
          <div className="pdf-row"><span className="k">손절가</span><span className="v">{typeof strat.stop_loss === 'number' ? formatPrice(strat.stop_loss) + '원' : strat.stop_loss}</span></div>
          <div className="pdf-row"><span className="k">손익비</span><span className="v">{strat.risk_reward_ratio ?? '-'}</span></div>
          <div className="pdf-row"><span className="k">권장 전략</span><span className="v">{strat.strategy_type}</span></div>
          <div className="pdf-row"><span className="k">추격매수 위험도</span><span className="v">{strat.chasing_risk}</span></div>
        </div>

        <div className="pdf-card">
          <h3 style={{ marginTop: 0 }}>핵심 요약</h3>
          <div><b style={{ color: '#059669' }}>긍정 요인</b>
            <ul>{(data.summary?.positive || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
          </div>
          <div><b style={{ color: '#dc2626' }}>부정 요인</b>
            <ul>{(data.summary?.negative || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
          </div>
          <div><b style={{ color: '#b45309' }}>주의할 점</b>
            <ul>{(data.summary?.warning || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
          </div>
        </div>

        <div className="pdf-card">
          <h3 style={{ marginTop: 0 }}>항목별 점수</h3>
          {Object.entries(data.scores || {}).map(([k, v]) => (
            <div key={k} className="pdf-row"><span className="k">{k}</span><span className="v">{v}</span></div>
          ))}
        </div>

        <div className="pdf-card">
          <h3 style={{ marginTop: 0 }}>리스크 플래그</h3>
          {Object.entries(data.risk_flags || {}).filter(([, v]) => v).length === 0
            ? <div style={{ color: '#059669' }}>감지된 리스크가 없습니다.</div>
            : (
              <ul>
                {Object.entries(data.risk_flags || {}).filter(([, v]) => v).map(([k]) => (
                  <li key={k}>{k}</li>
                ))}
              </ul>
            )
          }
        </div>

        <div className="pdf-card">
          <h3 style={{ marginTop: 0 }}>최종 판단</h3>
          <div style={{ lineHeight: 1.6 }}>{data.final_comment}</div>
        </div>

        <div className="pdf-disclaimer">
          {data.disclaimer} 최종 투자 결정은 본인의 책임 하에 이루어져야 합니다.
        </div>
      </div>

      <PdfExportButton
        targetId="pdf-report-area"
        stockName={data.stock_name}
        stockCode={data.stock_code}
      />
    </div>
  )
}
