import React from 'react'

export default function SummaryCard({ summary }) {
  if (!summary) return null
  return (
    <div className="card">
      <h3>핵심 요약</h3>
      <div className="summary-cols">
        <div className="summary-col pos">
          <h4 className="pos">✅ 긍정 요인</h4>
          <ul>{(summary.positive || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
        <div className="summary-col neg">
          <h4 className="neg">⛔ 부정 요인</h4>
          <ul>{(summary.negative || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
        <div className="summary-col warn">
          <h4 className="warn">⚠️ 주의할 점</h4>
          <ul>{(summary.warning || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
      </div>
    </div>
  )
}
