import React, { useEffect, useState } from 'react'
import { api } from '../api/client.js'

export default function HistoryPage() {
  const [code, setCode] = useState('005930')
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')

  async function load() {
    setErr('')
    try {
      const r = await api.history(code)
      setData(r)
    } catch (e) { setErr(e.message) }
  }
  useEffect(() => { load() }, [])

  return (
    <div>
      <h1 className="title-big">🕒 분석 이력</h1>
      <div className="row" style={{ gap: 8 }}>
        <input className="input" value={code} onChange={e => setCode(e.target.value)} placeholder="종목코드" />
        <button className="btn primary" onClick={load}>조회</button>
      </div>
      {err && <div className="error-banner" style={{ marginTop: 10 }}>{err}</div>}

      {data && (
        <>
          <div className="card">
            <h3>점수 변화</h3>
            {(data.score_history || []).length === 0 && <div className="subtle">기록 없음</div>}
            {(data.score_history || []).map((h, i) => (
              <div key={i} className="kv"><span className="k">{h.created_at}</span><span className="v">{h.total_score} ({h.grade})</span></div>
            ))}
          </div>
          <div className="card">
            <h3>리스크 등급 변화</h3>
            {(data.risk_history || []).map((h, i) => (
              <div key={i} className="kv"><span className="k">{h.created_at}</span><span className="v">{h.risk_label} ({h.risk_level}단계)</span></div>
            ))}
          </div>
          <div className="card">
            <h3>포지션 판단 이력</h3>
            {(data.position_history || []).map((h, i) => (
              <div key={i} className="kv"><span className="k">{h.created_at}</span><span className="v">{h.recommended_position}</span></div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
