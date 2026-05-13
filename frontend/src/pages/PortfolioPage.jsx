import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { formatPrice, formatPct, formatWon } from '../utils/formatters.js'

async function apiCall(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const keyMap = {
    'X-Anthropic-Key': 'srta_key_anthropic',
    'X-Gemini-Key':    'srta_key_gemini',
    'X-Dart-Key':      'srta_key_dart',
    'X-Naver-Id':      'srta_key_naver_id',
    'X-Naver-Secret':  'srta_key_naver_secret',
  }
  for (const [h, k] of Object.entries(keyMap)) {
    const v = localStorage.getItem(k)
    if (v && /^[\x20-\x7E]+$/.test(v)) headers[h] = v
  }
  const r = await fetch(path, { ...opts, headers })
  return r.json()
}

export default function PortfolioPage() {
  const [data, setData] = useState({ items: [], summary: {} })
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ stock_code: '', avg_price: '', quantity: '' })
  const [err, setErr] = useState('')
  const navigate = useNavigate()

  function load() {
    setErr('')
    apiCall('/api/portfolio').then(d => setData(d)).catch(e => setErr(e.message))
  }
  useEffect(() => { load() }, [])

  async function add() {
    setErr('')
    if (!form.stock_code || !form.avg_price || !form.quantity) {
      setErr('모든 항목을 입력하세요.')
      return
    }
    try {
      await apiCall('/api/portfolio', {
        method: 'POST',
        body: JSON.stringify({
          stock_code: form.stock_code,
          avg_price: Number(form.avg_price),
          quantity: Number(form.quantity),
        }),
      })
      setAdding(false)
      setForm({ stock_code: '', avg_price: '', quantity: '' })
      load()
    } catch (e) { setErr(e.message) }
  }

  async function remove(code) {
    try {
      await apiCall(`/api/portfolio/${code}`, { method: 'DELETE' })
      load()
    } catch (e) { setErr(e.message) }
  }

  const s = data.summary || {}
  const totalColor = (s.total_pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'

  return (
    <div>
      <h1 className="title-big">💼 포트폴리오</h1>

      <div className="card glow" style={{
        background: `linear-gradient(135deg, ${totalColor}22 0%, rgba(28,34,49,0.6) 100%)`,
        borderLeft: `3px solid ${totalColor}`,
      }}>
        <h3>전체 손익</h3>
        <div className="row space" style={{ alignItems: 'flex-end' }}>
          <div>
            <div className="subtle" style={{ fontSize: 11 }}>총 평가액</div>
            <div style={{ fontSize: 24, fontWeight: 900, fontVariantNumeric: 'tabular-nums' }}>
              {formatWon(s.total_value)}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="subtle" style={{ fontSize: 11 }}>총 손익</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: totalColor, fontVariantNumeric: 'tabular-nums' }}>
              {formatWon(s.total_pnl)} ({formatPct(s.total_pnl_rate)})
            </div>
          </div>
        </div>
        <div className="subtle" style={{ fontSize: 12, marginTop: 6 }}>
          총 매입 {formatWon(s.total_cost)} · 종목 {s.count || 0}개
        </div>
      </div>

      {err && <div className="error-banner">{err}</div>}

      {!adding && (
        <button className="btn primary full" onClick={() => setAdding(true)} style={{ marginBottom: 12 }}>
          ➕ 보유 종목 추가
        </button>
      )}

      {adding && (
        <div className="card">
          <h3>보유 종목 추가</h3>
          <input
            className="input"
            placeholder="종목코드 (예: 005930)"
            value={form.stock_code}
            onChange={(e) => setForm({ ...form, stock_code: e.target.value })}
            style={{ marginBottom: 8 }}
          />
          <input
            className="input"
            placeholder="평균 매수가"
            type="number"
            value={form.avg_price}
            onChange={(e) => setForm({ ...form, avg_price: e.target.value })}
            style={{ marginBottom: 8 }}
          />
          <input
            className="input"
            placeholder="수량"
            type="number"
            value={form.quantity}
            onChange={(e) => setForm({ ...form, quantity: e.target.value })}
            style={{ marginBottom: 8 }}
          />
          <div className="row" style={{ gap: 8 }}>
            <button className="btn primary full" onClick={add}>저장</button>
            <button className="btn ghost" onClick={() => setAdding(false)}>취소</button>
          </div>
        </div>
      )}

      {(data.items || []).map(it => {
        const c = (it.pnl || 0) >= 0 ? 'var(--green)' : 'var(--red)'
        return (
          <div key={it.stock_code} className="card" style={{ borderLeft: `3px solid ${c}` }}>
            <div className="row space" style={{ marginBottom: 6 }}>
              <div onClick={() => navigate(`/analyze/${it.stock_code}`)} style={{ cursor: 'pointer', flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: 16 }}>{it.stock_name}</div>
                <div className="subtle">{it.stock_code} · 수량 {it.quantity}</div>
              </div>
              <button className="btn ghost" onClick={() => remove(it.stock_code)}>삭제</button>
            </div>
            <div className="kv"><span className="k">평균 매수가</span><span className="v">{formatPrice(it.avg_price)}원</span></div>
            <div className="kv"><span className="k">현재가</span>
              <span className="v">
                {formatPrice(it.current_price)}원
                <span className={it.change_rate >= 0 ? 'pos' : 'neg'} style={{ marginLeft: 6, fontSize: 12 }}>
                  ({formatPct(it.change_rate)})
                </span>
              </span>
            </div>
            <div className="kv"><span className="k">평가액</span><span className="v">{formatWon(it.value)}</span></div>
            <div className="kv"><span className="k">평가손익</span>
              <span style={{ color: c, fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
                {formatWon(it.pnl)} ({formatPct(it.pnl_rate)})
              </span>
            </div>
          </div>
        )
      })}

      {(data.items || []).length === 0 && !adding && (
        <div className="subtle center" style={{ padding: 20 }}>보유 종목이 없습니다. 추가 버튼을 눌러주세요.</div>
      )}

      <div className="subtle center" style={{ marginTop: 16, fontSize: 12 }}>
        본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다.
      </div>
    </div>
  )
}
