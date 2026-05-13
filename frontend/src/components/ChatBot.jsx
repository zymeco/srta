import React, { useState, useRef, useEffect } from 'react'

const SUGGESTED = [
  '이 종목 왜 매수 보류야?',
  '동종 업종 대비 저평가야?',
  '비슷한 종목 추천해줘',
  '단기·중기·장기 중 어떤 게 좋아?',
  '리스크가 뭐야?',
]

export default function ChatBot({ stockCode, stockName }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function send(q) {
    const question = (q ?? input).trim()
    if (!question) return
    setErr('')
    const newMessages = [...messages, { role: 'user', content: question }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      // localStorage 키 헤더 첨부
      const headers = { 'Content-Type': 'application/json' }
      const keyMap = {
        'X-Anthropic-Key': 'srta_key_anthropic',
        'X-Gemini-Key':    'srta_key_gemini',
      }
      for (const [h, k] of Object.entries(keyMap)) {
        const v = localStorage.getItem(k)
        if (v && /^[\x20-\x7E]+$/.test(v)) headers[h] = v
      }
      const provider = localStorage.getItem('ai_provider') || 'auto'

      const r = await fetch('/api/chat', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          stock_code: stockCode,
          question,
          history: newMessages.slice(-6),
          provider,
        }),
      })
      const d = await r.json()
      if (d.error) {
        setErr(d.error)
      } else {
        setMessages([...newMessages, { role: 'assistant', content: d.answer }])
      }
    } catch (e) {
      setErr(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3>💬 AI 챗봇 — {stockName} 에 대해 질문</h3>

      <div style={{ maxHeight: 380, overflowY: 'auto', marginBottom: 10, padding: 4 }}>
        {messages.length === 0 && (
          <div className="subtle" style={{ fontSize: 13, textAlign: 'center', padding: 12 }}>
            분석 결과에 대해 자유롭게 질문하세요.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: 6,
          }}>
            <div style={{
              maxWidth: '85%',
              padding: '10px 12px',
              borderRadius: 14,
              fontSize: 13,
              lineHeight: 1.55,
              whiteSpace: 'pre-wrap',
              background: m.role === 'user' ? 'var(--grad-brand)' : 'rgba(15,19,28,0.7)',
              color: m.role === 'user' ? '#0b0d15' : 'var(--text-2)',
              border: m.role === 'user' ? 'none' : '1px solid var(--border)',
            }}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="row" style={{ padding: 8, gap: 8 }}>
            <div className="spinner" /> <span className="subtle">생각 중...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {err && <div className="error-banner">{err}</div>}

      {messages.length === 0 && (
        <div className="row wrap" style={{ gap: 4, marginBottom: 8 }}>
          {SUGGESTED.map((s, i) => (
            <span key={i} className="tag brand" style={{ cursor: 'pointer' }} onClick={() => send(s)}>
              {s}
            </span>
          ))}
        </div>
      )}

      <div className="row" style={{ gap: 6 }}>
        <input
          className="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="질문 입력..."
          style={{ flex: 1, height: 44 }}
        />
        <button className="btn primary" onClick={() => send()} disabled={loading || !input.trim()}>
          전송
        </button>
      </div>
    </div>
  )
}
