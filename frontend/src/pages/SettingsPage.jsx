import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, userKeys } from '../api/client.js'
import { isAiEnabled } from '../components/AiAdvisorCard.jsx'

// 동일 키를 AiAdvisorCard 와 공유
const AI_ENABLED_KEY = 'ai_enabled'

// 키 등록 카드 (재사용)
function KeyInput({ name, label, desc, link, type = 'password', value, onSave, onClear }) {
  const [v, setV] = useState(value || '')
  const [editing, setEditing] = useState(!value)
  const [saved, setSaved] = useState('')
  const [err, setErr] = useState('')

  const invalid = value && !userKeys.isValid(value)

  function save() {
    setErr('')
    const cleaned = v.trim()
    if (!cleaned) {
      setErr('키 값을 입력해주세요.')
      return
    }
    if (!userKeys.isValid(cleaned)) {
      setErr('한글 또는 특수문자가 섞여 있습니다. 영문/숫자/기호만 포함된 키를 입력해주세요.')
      return
    }
    onSave(cleaned)
    setEditing(false)
    setSaved('저장됨')
    setTimeout(() => setSaved(''), 1500)
  }
  function clear() {
    onClear()
    setV('')
    setEditing(true)
    setErr('')
  }

  return (
    <div style={{
      padding: 14,
      borderRadius: 12,
      background: 'rgba(15,19,28,0.45)',
      border: '1px solid var(--border)',
      marginBottom: 10,
    }}>
      <div className="row space" style={{ marginBottom: 6 }}>
        <div style={{ fontWeight: 700, fontSize: 14 }}>{label}</div>
        <div>
          {invalid && <span className="tag red">⚠ 잘못된 값</span>}
          {value && !editing && !invalid && <span className="tag green">✓ 등록됨</span>}
          {!value && <span className="tag" style={{ opacity: 0.6 }}>미등록</span>}
          {saved && <span className="tag green" style={{ marginLeft: 4 }}>{saved}</span>}
        </div>
      </div>
      <div className="subtle" style={{ fontSize: 12, marginBottom: 8 }}>
        {desc}
        {link && (
          <> · <a href={link} target="_blank" rel="noreferrer" style={{ color: 'var(--brand)', textDecoration: 'underline' }}>키 발급받기 ↗</a></>
        )}
      </div>

      {!editing && value ? (
        <div className="row" style={{ gap: 8 }}>
          <div style={{
            flex: 1,
            padding: '10px 14px',
            background: 'rgba(0,0,0,0.25)',
            borderRadius: 10,
            fontFamily: 'monospace',
            fontSize: 13,
            letterSpacing: '0.05em',
          }}>
            {userKeys.mask(value)}
          </div>
          <button className="btn ghost" onClick={() => setEditing(true)}>변경</button>
          <button className="btn ghost" onClick={clear} style={{ color: 'var(--red)' }}>삭제</button>
        </div>
      ) : (
        <div className="row" style={{ gap: 8 }}>
          <input
            type={type}
            className="input"
            value={v}
            onChange={(e) => setV(e.target.value)}
            placeholder={`${label} 입력`}
            style={{ flex: 1, height: 44 }}
            autoComplete="off"
            spellCheck={false}
          />
          <button className="btn primary" onClick={save} disabled={!v.trim()}>저장</button>
          {value && <button className="btn ghost" onClick={() => { setEditing(false); setV(value); setErr(''); }}>취소</button>}
        </div>
      )}
      {err && <div className="error-banner" style={{ marginTop: 8, fontSize: 13 }}>{err}</div>}
      {invalid && !editing && (
        <div className="error-banner" style={{ marginTop: 8, fontSize: 13 }}>
          저장된 키 값이 손상되어 있습니다 (한글/제어문자 포함). 삭제 후 다시 입력하세요.
        </div>
      )}
    </div>
  )
}

export default function SettingsPage() {
  const [health, setHealth] = useState('확인 중…')
  const [providers, setProviders] = useState({ claude: false, gemini: false })
  const [provider, setProvider] = useState(localStorage.getItem('ai_provider') || 'auto')
  const [dataStatus, setDataStatus] = useState({ data_provider: '-', dart: false, naver_news: false })
  const [aiEnabled, setAiEnabled] = useState(isAiEnabled())

  // 로컬 키 상태
  const [keys, setKeys] = useState({
    anthropic: userKeys.get('anthropic'),
    gemini: userKeys.get('gemini'),
    dart: userKeys.get('dart'),
    naver_id: userKeys.get('naver_id'),
    naver_secret: userKeys.get('naver_secret'),
  })

  function refreshStatus() {
    api.aiProviders().then(d => setProviders(d.available || {})).catch(() => {})
    api.dataStatus().then(setDataStatus).catch(() => {})
  }

  useEffect(() => {
    api.health().then(() => setHealth('정상')).catch(() => setHealth('오류'))
    refreshStatus()
  }, [])

  function changeProvider(v) {
    setProvider(v)
    localStorage.setItem('ai_provider', v)
  }

  function saveKey(name, value) {
    userKeys.set(name, value)
    setKeys({ ...keys, [name]: value })
    setTimeout(refreshStatus, 200)
  }

  function clearKey(name) {
    userKeys.set(name, '')
    setKeys({ ...keys, [name]: '' })
    setTimeout(refreshStatus, 200)
  }

  function toggleAi() {
    const next = !aiEnabled
    setAiEnabled(next)
    localStorage.setItem(AI_ENABLED_KEY, next ? 'true' : 'false')
    // 다른 탭(같은 도메인)에도 storage 이벤트로 즉시 전파됨
  }

  return (
    <div>
      <h1 className="title-big">⚙️ 설정</h1>

      <div className="card">
        <h3>서버 상태</h3>
        <div className="kv"><span className="k">/health</span><span className="v">{health}</span></div>
        <div className="kv"><span className="k">데이터 모드</span><span className="v">{dataStatus.data_provider}</span></div>
      </div>

      <div className="card">
        <h3>🔑 내 API 키 등록</h3>
        <div className="subtle" style={{ fontSize: 13, marginBottom: 14, lineHeight: 1.6 }}>
          여기에 입력한 키는 <b>이 폰의 브라우저에만 저장</b>됩니다. 서버에 저장되지 않으며,
          매 분석 요청 시 헤더로만 일시 전달됩니다. 다른 사람은 사용할 수 없습니다.
        </div>

        <KeyInput
          name="anthropic"
          label="Claude API Key"
          desc="Anthropic에서 발급 (sk-ant-…)"
          link="https://console.anthropic.com/settings/keys"
          value={keys.anthropic}
          onSave={(v) => saveKey('anthropic', v)}
          onClear={() => clearKey('anthropic')}
        />

        <KeyInput
          name="gemini"
          label="Gemini API Key"
          desc="Google AI Studio에서 발급 (AIza…)"
          link="https://aistudio.google.com/apikey"
          value={keys.gemini}
          onSave={(v) => saveKey('gemini', v)}
          onClear={() => clearKey('gemini')}
        />

        <KeyInput
          name="dart"
          label="DART API Key"
          desc="재무·공시 데이터 정확도 ↑ (40자 hex)"
          link="https://opendart.fss.or.kr/intro/main.do"
          value={keys.dart}
          onSave={(v) => saveKey('dart', v)}
          onClear={() => clearKey('dart')}
        />

        <KeyInput
          name="naver_id"
          label="Naver Client ID"
          desc="네이버 뉴스 실시간 감성 분석"
          link="https://developers.naver.com/apps"
          value={keys.naver_id}
          onSave={(v) => saveKey('naver_id', v)}
          onClear={() => clearKey('naver_id')}
        />

        <KeyInput
          name="naver_secret"
          label="Naver Client Secret"
          desc="위와 같은 앱의 Secret 값"
          link="https://developers.naver.com/apps"
          value={keys.naver_secret}
          onSave={(v) => saveKey('naver_secret', v)}
          onClear={() => clearKey('naver_secret')}
        />
      </div>

      <div className="card">
        <h3>🤖 AI 판단 사용</h3>
        <div className="row space" style={{ alignItems: 'center', marginBottom: 10 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
              AI 자연어 분석 {aiEnabled ? 'ON' : 'OFF'}
            </div>
            <div className="subtle" style={{ fontSize: 12, lineHeight: 1.5 }}>
              {aiEnabled
                ? '분석 화면에 AI 카드가 표시되며, 요청 시 외부 AI 호출이 발생합니다.'
                : 'AI 카드가 분석 화면에서 숨겨지고, 외부 AI 호출이 발생하지 않습니다.'}
            </div>
          </div>
          <button
            className={'btn ' + (aiEnabled ? 'primary' : 'ghost')}
            onClick={toggleAi}
            style={{
              minWidth: 80, height: 44,
              background: aiEnabled ? 'var(--brand)' : 'rgba(127,127,127,0.18)',
              color: aiEnabled ? 'white' : 'var(--text)',
              border: aiEnabled ? 'none' : '1px solid var(--border)',
              fontWeight: 700,
            }}
          >
            {aiEnabled ? 'ON' : 'OFF'}
          </button>
        </div>
        {!aiEnabled && (
          <div className="subtle" style={{
            fontSize: 12,
            padding: 10,
            background: 'rgba(127,127,127,0.10)',
            borderRadius: 8,
            marginTop: 6,
          }}>
            💡 OFF 상태에서는 기술/재무/뉴스 점수 기반 분석만 표시됩니다.
            AI 키 등록 여부와 무관하게 호출이 막힙니다.
          </div>
        )}
      </div>

      <div className="card" style={{ opacity: aiEnabled ? 1 : 0.5 }}>
        <h3>🤖 AI 공급자 {!aiEnabled && <span className="tag" style={{ marginLeft: 6, opacity: 0.7 }}>AI OFF</span>}</h3>
        <div className="kv"><span className="k">Claude</span><span className={'tag ' + (providers.claude ? 'green' : 'red')}>{providers.claude ? '사용 가능' : '미설정'}</span></div>
        <div className="kv"><span className="k">Gemini</span><span className={'tag ' + (providers.gemini ? 'green' : 'red')}>{providers.gemini ? '사용 가능' : '미설정'}</span></div>
        <div style={{ marginTop: 10 }}>
          <div className="subtle" style={{ marginBottom: 6 }}>기본 공급자 선택</div>
          <select
            className="input"
            value={provider}
            onChange={e => changeProvider(e.target.value)}
            style={{ height: 44 }}
            disabled={!aiEnabled}
          >
            <option value="auto">자동 선택 (Claude 우선)</option>
            <option value="claude" disabled={!providers.claude}>Claude</option>
            <option value="gemini" disabled={!providers.gemini}>Gemini</option>
          </select>
        </div>
      </div>

      <div className="card">
        <h3>📊 데이터 공급자</h3>
        <div className="kv"><span className="k">pykrx (시세/수급)</span><span className="tag green">기본 사용</span></div>
        <div className="kv"><span className="k">DART (재무·공시)</span><span className={'tag ' + (dataStatus.dart ? 'green' : 'red')}>{dataStatus.dart ? '연결됨' : '미설정'}</span></div>
        <div className="kv"><span className="k">네이버 뉴스</span><span className={'tag ' + (dataStatus.naver_news ? 'green' : 'red')}>{dataStatus.naver_news ? '연결됨' : '미설정'}</span></div>
      </div>

      <div className="card">
        <h3>📱 PWA 설치</h3>
        <div className="subtle">
          갤럭시 Chrome 우측 상단 ⋮ → <b>"홈 화면에 추가"</b> → 풀스크린 standalone 앱으로 실행됩니다.
        </div>
      </div>

      <div className="card">
        <h3>📄 약관 및 정책</h3>
        <Link to="/privacy" className="list-row" style={{ textDecoration: 'none' }}>
          <div>
            <div style={{ fontWeight: 700 }}>개인정보처리방침</div>
            <div className="subtle">데이터 수집·저장·외부 API 사용 안내</div>
          </div>
          <span className="tag brand">보기 →</span>
        </Link>
        <Link to="/terms" className="list-row" style={{ textDecoration: 'none' }}>
          <div>
            <div style={{ fontWeight: 700 }}>이용약관</div>
            <div className="subtle">면책 조항 포함</div>
          </div>
          <span className="tag brand">보기 →</span>
        </Link>
      </div>

      <div className="subtle center" style={{ marginTop: 16, fontSize: 12 }}>
        본 결과는 투자 추천이 아닌 투자 판단 보조 도구입니다.<br />
        v1.0.0 · © 2026 SRTA
      </div>
    </div>
  )
}
