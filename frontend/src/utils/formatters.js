export function formatWon(v) {
  if (v == null || isNaN(v)) return '-';
  const n = Number(v);
  if (Math.abs(n) >= 1e12) return (n / 1e12).toFixed(2) + '조';
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(1) + '억';
  return n.toLocaleString('ko-KR');
}

export function formatPrice(v) {
  if (v == null || isNaN(v)) return '-';
  return Number(v).toLocaleString('ko-KR');
}

export function formatPct(v) {
  if (v == null || isNaN(v)) return '-';
  const n = Number(v);
  const sign = n > 0 ? '+' : '';
  return sign + n.toFixed(2) + '%';
}

export function formatNumber(v, digits = 1) {
  if (v == null || isNaN(v)) return '-';
  return Number(v).toLocaleString('ko-KR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function todayStr() {
  const d = new Date();
  const p = (n) => (n < 10 ? '0' + n : '' + n);
  return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate());
}

export function gradeColor(grade) {
  return {
    S: '#a78bfa',
    A: '#34d399',
    B: '#60a5fa',
    C: '#fbbf24',
    D: '#f87171',
  }[grade] || '#9ca3af';
}

export function marketCapLabel(t) {
  return { large: '대형주', mid: '중형주', small: '소형주' }[t] || t;
}
