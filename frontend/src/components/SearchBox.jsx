import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

export default function SearchBox() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')
  const navigate = useNavigate()

  async function doSearch(e) {
    if (e) e.preventDefault()
    setErr('')
    setLoading(true)
    try {
      // 종목코드 형식이면 바로 분석으로
      if (/^\d{6}$/.test(q.trim())) {
        navigate(`/analyze/${q.trim()}`)
        return
      }
      const r = await api.search(q)
      setResults(r.items || [])
      if ((r.items || []).length === 1) {
        navigate(`/analyze/${r.items[0].stock_code}`)
      }
    } catch (ex) {
      setErr(ex.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={doSearch} className="row" style={{ gap: 8 }}>
        <input
          className="input"
          placeholder="종목명 또는 종목코드 입력 (예: 삼성전자, 005930)"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          inputMode="search"
        />
        <button className="btn primary" type="submit" disabled={loading || !q.trim()}>
          {loading ? '…' : '검색'}
        </button>
      </form>

      {err && <div className="error-banner" style={{ marginTop: 10 }}>{err}</div>}

      {results.length > 0 && (
        <div style={{ marginTop: 12 }}>
          {results.map(r => (
            <div
              key={r.stock_code}
              className="list-row"
              onClick={() => navigate(`/analyze/${r.stock_code}`)}
              style={{ cursor: 'pointer' }}
            >
              <div>
                <div style={{ fontWeight: 700 }}>{r.stock_name}</div>
                <div className="subtle">{r.stock_code} · {r.market}</div>
              </div>
              <div className="tag blue">분석</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
