// 백엔드 API 호출 래퍼.
// localStorage에 저장된 사용자 API 키를 매 요청 헤더에 자동 첨부.
// HTTP 헤더는 ISO-8859-1만 허용하므로 비ASCII/제어문자 값은 자동 제외.

const BASE = '';

const KEY_MAP = {
  'X-Anthropic-Key': 'srta_key_anthropic',
  'X-Gemini-Key':    'srta_key_gemini',
  'X-Dart-Key':      'srta_key_dart',
  'X-Naver-Id':      'srta_key_naver_id',
  'X-Naver-Secret':  'srta_key_naver_secret',
};

// 헤더로 안전하게 보낼 수 있는 값인지 검증 (printable ASCII만 허용)
function isHeaderSafe(v) {
  if (typeof v !== 'string' || !v) return false;
  // \x20-\x7E (스페이스 ~ ~) printable ASCII
  return /^[\x20-\x7E]+$/.test(v);
}

function getUserKeyHeaders() {
  const headers = {};
  for (const [header, lsKey] of Object.entries(KEY_MAP)) {
    try {
      let v = localStorage.getItem(lsKey);
      if (!v) continue;
      v = v.trim();
      if (!isHeaderSafe(v)) {
        console.warn(`[SRTA] ${lsKey} 값에 비ASCII 문자가 있어 헤더에 첨부하지 않습니다. 설정에서 다시 입력해주세요.`);
        continue;
      }
      headers[header] = v;
    } catch (_) {}
  }
  return headers;
}

async function request(path, opts = {}) {
  try {
    const userHeaders = getUserKeyHeaders();
    const res = await fetch(BASE + path, {
      ...opts,
      headers: {
        'Content-Type': 'application/json',
        ...userHeaders,
        ...(opts.headers || {}),
      },
    });
    if (!res.ok) {
      let detail = '서버 오류가 발생했습니다.';
      try {
        const j = await res.json();
        detail = j.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }
    return await res.json();
  } catch (e) {
    throw new Error(e.message || '네트워크 오류가 발생했습니다.');
  }
}

export const api = {
  search: (q) => request(`/api/search?query=${encodeURIComponent(q)}`),
  analyze: (code) => request(`/api/analyze/${encodeURIComponent(code)}`),
  report: (code) => request(`/api/report/${encodeURIComponent(code)}`),
  recent: () => request('/api/recent'),
  watchlist: () => request('/api/watchlist'),
  addWatchlist: (stock_code, stock_name) =>
    request('/api/watchlist', {
      method: 'POST',
      body: JSON.stringify({ stock_code, stock_name }),
    }),
  removeWatchlist: (code) =>
    request(`/api/watchlist/${encodeURIComponent(code)}`, { method: 'DELETE' }),
  history: (code) => request(`/api/history/${encodeURIComponent(code)}`),
  health: () => request('/health'),
  aiProviders: () => request('/api/ai/providers'),
  aiAdvise: (code, provider) =>
    request(`/api/ai/advise/${encodeURIComponent(code)}?provider=${encodeURIComponent(provider || 'auto')}`),
  dataStatus: () => request('/api/data/status'),
};

// 키 관리 헬퍼
export const userKeys = {
  get(name) {
    try { return localStorage.getItem('srta_key_' + name) || ''; }
    catch { return ''; }
  },
  set(name, value) {
    try {
      const cleaned = (value || '').trim();
      if (cleaned) localStorage.setItem('srta_key_' + name, cleaned);
      else localStorage.removeItem('srta_key_' + name);
    } catch {}
  },
  mask(value) {
    if (!value) return '';
    if (value.length <= 8) return '*'.repeat(value.length);
    return value.slice(0, 4) + '••••' + value.slice(-4);
  },
  // 검증: 값이 헤더로 보낼 수 있는지 (한글 등 비ASCII 감지)
  isValid(value) {
    if (!value) return false;
    return isHeaderSafe(value.trim());
  },
};
