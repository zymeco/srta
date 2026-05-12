import React, { useEffect, useState } from 'react'
import { api } from '../api/client.js'

export default function AiAdvisorCard({ stockCode }) {
  const [providers, setProviders] = useState({ claude: false, gemini: false })
  const [provider, setProvider] = useState(localStorage.getItem('ai_provider') || 'auto')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api.aiProviders().then(d => setProviders(d.available || {})).catch(() => {})
  }, [])

  const anyAvailable = providers.claude || providers.gemini

  async function request() {
    setErr(''); setLoading(true); setResult(null)
    try {
      const r = await api.aiAdvise(stockCode, provider)
      if (r.error) {
        setErr(r.error)
      } else {
        setResult(r)
      }
    } catch (e) {
      setErr(e.message)
    } finally {
      setLoading(false)
    }
  }

  function changeProvider(v) {
    setProvider(v)
    localStorage.setItem('ai_provider', v)
  }

  return (
    <div className="card">
      <h3>🤖 AI 자연어 분석</h3>

      {!anyAvailable ? (
        <div className="subtle">
          AI 키가 설정되지 않았습니다. 설정 화면에서 키 등록 방법을 확인하세요.
        </div>
      ) : (
        <>
          <div className="row" style={{ gap: 8, marginBottom: 8 }}>
            <select className="input" value={provider} onChange={e => changeProvider(e.target.value)} style={{ flex: 1, height: 44 }}>
              <option value="auto">자동 선택 (Claude 우선)</option>
              {providers.claude && <option value="claude">Claude</option>}
              {providers.gemini && <option value="gemini">Gemini</option>}
            </select>
            <button className="btn primary" onClick={request} disabled={loading}>
              {loading ? '분석 중…' : '🤖 AI 분석 요청'}
            </button>
          </div>
          {err && <div className="error-banner">{err}</div>}
          {result && result.comment && (
            <div className="ai-content">
              {result.comment}
              <div className="subtle" style={{ marginTop: 10, fontSize: 11, display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="tag brand">{result.provider}</span>
                <span>· AI 자연어 해설</span>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
