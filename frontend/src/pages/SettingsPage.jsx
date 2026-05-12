import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'

export default function SettingsPage() {
  const [health, setHealth] = useState('확인 중…')
  const [providers, setProviders] = useState({ claude: false, gemini: false })
  const [provider, setProvider] = useState(localStorage.getItem('ai_provider') || 'auto')
  const [dataStatus, setDataStatus] = useState({ data_provider: '-', dart: false, naver_news: false })

  useEffect(() => {
    api.health().then(() => setHealth('정상')).catch(() => setHealth('오류 (백엔드 미실행 가능성)'))
    api.aiProviders().then(d => setProviders(d.available || {})).catch(() => {})
    api.dataStatus().then(setDataStatus).catch(() => {})
  }, [])

  function changeProvider(v) {
    setProvider(v)
    localStorage.setItem('ai_provider', v)
  }

  return (
    <div>
      <h1 className="title-big">⚙️ 설정</h1>

      <div className="card">
        <h3>서버 상태</h3>
        <div className="kv"><span className="k">/health</span><span className="v">{health}</span></div>
      </div>

      <div className="card">
        <h3>🤖 AI 공급자</h3>
        <div className="kv"><span className="k">Claude</span><span className={'tag ' + (providers.claude ? 'green' : 'red')}>{providers.claude ? '사용 가능' : '미설정'}</span></div>
        <div className="kv"><span className="k">Gemini</span><span className={'tag ' + (providers.gemini ? 'green' : 'red')}>{providers.gemini ? '사용 가능' : '미설정'}</span></div>
        <div style={{ marginTop: 10 }}>
          <div className="subtle" style={{ marginBottom: 6 }}>기본 공급자 선택</div>
          <select className="input" value={provider} onChange={e => changeProvider(e.target.value)} style={{ height: 44 }}>
            <option value="auto">자동 선택 (Claude 우선)</option>
            <option value="claude" disabled={!providers.claude}>Claude</option>
            <option value="gemini" disabled={!providers.gemini}>Gemini</option>
          </select>
        </div>
        <div className="subtle" style={{ marginTop: 8, fontSize: 12 }}>
          키 등록 방법: <br />
          • 로컬 실행: <code>backend/keys/api_keys.py</code> 의 ANTHROPIC_API_KEY / GEMINI_API_KEY 값 입력<br />
          • 클라우드 배포: 환경변수 <code>ANTHROPIC_API_KEY</code>, <code>GEMINI_API_KEY</code> 등록
        </div>
      </div>

      <div className="card">
        <h3>📊 데이터 공급자</h3>
        <div className="kv"><span className="k">모드</span><span className="v">{dataStatus.data_provider}</span></div>
        <div className="kv"><span className="k">pykrx (시세/수급)</span><span className="tag green">기본 사용</span></div>
        <div className="kv"><span className="k">DART (재무·공시·관리종목)</span><span className={'tag ' + (dataStatus.dart ? 'green' : 'red')}>{dataStatus.dart ? '연결됨' : '미설정'}</span></div>
        <div className="kv"><span className="k">네이버 뉴스</span><span className={'tag ' + (dataStatus.naver_news ? 'green' : 'red')}>{dataStatus.naver_news ? '연결됨' : '미설정'}</span></div>
        <div className="subtle" style={{ marginTop: 10, fontSize: 12 }}>
          키 발급:<br />
          • DART: <code>https://opendart.fss.or.kr</code> → <code>DART_API_KEY</code><br />
          • 네이버: <code>https://developers.naver.com/apps</code> → <code>NAVER_CLIENT_ID</code>, <code>NAVER_CLIENT_SECRET</code><br />
          모든 키는 <code>backend/keys/api_keys.py</code> 또는 환경변수로 설정합니다.
        </div>
      </div>

      <div className="card">
        <h3>📱 PWA 설치 (앱처럼 사용)</h3>
        <div className="subtle">
          갤럭시 Chrome에서 우측 상단 ⋮ 메뉴 → <b>"홈 화면에 추가"</b> 를 누르면 앱 아이콘이 생기고,
          standalone 모드(주소창 없는 풀스크린)로 일반 앱처럼 동작합니다.
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
