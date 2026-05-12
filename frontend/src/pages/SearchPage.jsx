import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import SearchBox from '../components/SearchBox.jsx'
import { api } from '../api/client.js'

export default function SearchPage() {
  const [recent, setRecent] = useState([])
  const [watch, setWatch] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    api.recent().then(r => setRecent(r.items || [])).catch(() => {})
    api.watchlist().then(r => setWatch(r.items || [])).catch(() => {})
  }, [])

  // 빠른 종목 칩
  const quickPicks = [
    { code: '005930', name: '삼성전자' },
    { code: '000660', name: 'SK하이닉스' },
    { code: '247540', name: '에코프로비엠' },
    { code: '373220', name: 'LG에너지솔루션' },
    { code: '035420', name: 'NAVER' },
    { code: '012450', name: '한화에어로스페이스' },
  ]

  return (
    <div>
      <div className="logo-hero">
        <span className="badge">✨ AI Powered · Korean Stocks</span>
        <h1>Stock Real Trader Analyzer</h1>
        <p>종목명·코드 입력 한 번으로 재무·차트·수급·리스크·AI 해설까지</p>
      </div>

      <div className="card glow">
        <SearchBox />
        <div className="row wrap" style={{ marginTop: 12, gap: 6 }}>
          {quickPicks.map(q => (
            <span
              key={q.code}
              className="tag brand"
              style={{ cursor: 'pointer' }}
              onClick={() => navigate(`/analyze/${q.code}`)}
            >
              {q.name}
            </span>
          ))}
        </div>
      </div>

      {recent.length > 0 && (
        <div className="card">
          <h3>최근 검색</h3>
          {recent.slice(0, 6).map(r => (
            <div key={r.stock_code} className="list-row" onClick={() => navigate(`/analyze/${r.stock_code}`)}>
              <div>
                <div style={{ fontWeight: 700 }}>{r.stock_name}</div>
                <div className="subtle">{r.stock_code}</div>
              </div>
              <span className="tag brand">분석 →</span>
            </div>
          ))}
        </div>
      )}

      {watch.length > 0 && (
        <div className="card">
          <h3>⭐ 관심종목</h3>
          {watch.map(r => (
            <div key={r.stock_code} className="list-row" onClick={() => navigate(`/analyze/${r.stock_code}`)}>
              <div>
                <div style={{ fontWeight: 700 }}>{r.stock_name}</div>
                <div className="subtle">{r.stock_code}</div>
              </div>
              <span className="tag green">⭐</span>
            </div>
          ))}
        </div>
      )}

      <div className="subtle center" style={{ marginTop: 18, fontSize: 11, padding: '0 12px' }}>
        본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다.
      </div>
    </div>
  )
}
