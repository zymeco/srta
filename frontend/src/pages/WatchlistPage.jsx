import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

export default function WatchlistPage() {
  const [items, setItems] = useState([])
  const [err, setErr] = useState('')
  const navigate = useNavigate()

  function load() {
    api.watchlist().then(r => setItems(r.items || [])).catch(e => setErr(e.message))
  }
  useEffect(() => { load() }, [])

  async function remove(code) {
    try {
      await api.removeWatchlist(code)
      load()
    } catch (e) { setErr(e.message) }
  }

  return (
    <div>
      <h1 className="title-big">⭐ 관심종목</h1>
      {err && <div className="error-banner">{err}</div>}
      {items.length === 0 && <div className="subtle">관심종목이 없습니다. 분석 화면에서 추가해 주세요.</div>}
      {items.map(it => (
        <div key={it.stock_code} className="list-row">
          <div onClick={() => navigate(`/analyze/${it.stock_code}`)} style={{ cursor: 'pointer', flex: 1 }}>
            <div style={{ fontWeight: 700 }}>{it.stock_name}</div>
            <div className="subtle">{it.stock_code}</div>
          </div>
          <button className="btn" onClick={() => remove(it.stock_code)}>삭제</button>
        </div>
      ))}
    </div>
  )
}
