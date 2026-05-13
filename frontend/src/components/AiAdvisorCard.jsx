import React, { useEffect, useState } from 'react'
import { api } from '../api/client.js'

// localStorage 키 — SettingsPage 토글과 공유
const AI_ENABLED_KEY = 'ai_enabled'

export function isAiEnabled() {
  // 기본값: ON (true). 'false' 문자열로 저장되어 있을 때만 OFF.
  return localStorage.getItem(AI_ENABLED_KEY) !== 'false'
}

export default function AiAdvisorCard({ stockCode }) {
  const [providers, setProviders] = useState({ claude: false, gemini: false })
  const [provider, setProvider] = useState(localStorage.getItem('ai_provider') || 'auto')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [err, setErr] = useState('')
  const [aiEnabled, setAiEnabled] = useState(isAiEnabled())

  useEffect(() => {
    if (!aiEnabled) return
    api.aiProviders().then(d => setProviders(d.available || {})).catch(() => {})
  }, [aiEnabled])

  // 다른 탭/페이지에서 토글 변경 시 즉시 반영
  useEffect(() => {
    function onStorage(e) {
      if (e.key === AI_ENABLED_KEY) setAiEnabled(isAiEnabled())
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  // AI OFF — 카드 자체를 렌더하지 않음 (깔끔)
  if (!aiEnabled) return null

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
