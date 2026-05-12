// 백엔드 API 호출 래퍼. 모든 호출에 예외 처리를 한다.

const BASE = ''; // Vite proxy 사용

async function request(path, opts = {}) {
  try {
    const res = await fetch(BASE + path, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
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
