import React, { useEffect, useState } from 'react'
import { gradeColor } from '../utils/formatters.js'

// 부드러운 카운트업 + 그라데이션 stroke + 글로우 효과
export default function ScoreGauge({ score, grade, opinion }) {
  const target = Math.max(0, Math.min(100, Number(score) || 0))
  const [animated, setAnimated] = useState(0)

  useEffect(() => {
    let raf
    const start = performance.now()
    const duration = 900
    function step(t) {
      const p = Math.min(1, (t - start) / duration)
      const eased = 1 - Math.pow(1 - p, 3)
      setAnimated(target * eased)
      if (p < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [target])

  const r = 64
  const c = 2 * Math.PI * r
  const offset = c - (animated / 100) * c
  const color = gradeColor(grade)

  return (
    <div className="score-row">
      <div style={{ position: 'relative', width: 168, height: 168, flexShrink: 0 }}>
        <svg width="168" height="168" viewBox="0 0 168 168" style={{ display: 'block' }}>
          <defs>
            <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stopColor="#818cf8" />
              <stop offset="50%"  stopColor="#c084fc" />
              <stop offset="100%" stopColor="#f472b6" />
            </linearGradient>
            <filter id="gaugeGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="3.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* track */}
          <circle cx="84" cy="84" r={r}
            stroke="rgba(148,163,184,0.16)"
            strokeWidth="12" fill="none" />

          {/* progress */}
          <circle cx="84" cy="84" r={r}
            stroke="url(#gaugeGrad)"
            strokeWidth="12" fill="none"
            strokeLinecap="round"
            strokeDasharray={c}
            strokeDashoffset={offset}
            transform="rotate(-90 84 84)"
            filter="url(#gaugeGlow)"
            style={{ transition: 'stroke-dashoffset 0.3s ease' }}
          />

          {/* center text */}
          <text x="84" y="84" textAnchor="middle" dominantBaseline="middle"
            fontSize="38" fontWeight="900" fill="#f1f5f9"
            style={{ fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.03em' }}>
            {animated.toFixed(1)}
          </text>
          <text x="84" y="112" textAnchor="middle" fontSize="11" fill="#64748b"
            letterSpacing="0.1em">/ 100</text>
        </svg>
      </div>

      <div className="score-meta">
        <div className="subtle" style={{ textTransform: 'uppercase', letterSpacing: '0.08em', fontSize: 11 }}>
          종합 등급
        </div>
        <div className="row" style={{ alignItems: 'center', gap: 12, marginTop: 6 }}>
          <div className="grade-pill" style={{ background: color }}>{grade}</div>
          <div className="opinion-text">{opinion}</div>
        </div>
        <div className="subtle" style={{ marginTop: 10, fontSize: 12 }}>
          {target >= 80 && '강한 매수 후보'}
          {target >= 70 && target < 80 && '관찰 추천 구간'}
          {target >= 60 && target < 70 && '보류 / 추가 점검 필요'}
          {target < 60 && '진입 부적합 / 위험 우선'}
        </div>
      </div>
    </div>
  )
}
