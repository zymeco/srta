// 백엔드 API 호출 래퍼.
// localStorage에 저장된 사용자 API 키를 매 요청 헤더에 자동 첨부.

const BASE = ''; // 같은 출처

// localStorage 키 매핑
const KEY_MAP = {
  'X-Anthropic-Key': 'srta_key_anthropic',
  'X-Gemini-Key':    'srta_key_gemini',
  'X-Dart-Key':      'srta_key_dart',
  'X-Naver-Id':      'srta_key_naver_id',
  'X-Naver-Secret':  'srta_key_naver_secret',
};

function getUserKeyHeaders() {
  const headers = {};
  for (const [header, lsKey] of Object.entries(KEY_MAP)) {
    try {
      const v = localStorage.getItem(lsKey);
      if (v) headers[header] = v;
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

// 키 관리 헬퍼 (UI에서 사용)
export const userKeys = {
  get(name) {
    try { return localStorage.getItem('srta_key_' + name) || ''; }
    catch { return ''; }
  },
  set(name, value) {
    try {
      if (value) localStorage.setItem('srta_key_' + name, value);
      else localStorage.removeItem('srta_key_' + name);
    } catch {}
  },
  // UI 표시용 (앞뒤 몇 자리만, 가운데 마스킹)
  mask(value) {
    if (!value) return '';
    if (value.length <= 8) return '*'.repeat(value.length);
    return value.slice(0, 4) + '••••' + value.slice(-4);
  },
};
