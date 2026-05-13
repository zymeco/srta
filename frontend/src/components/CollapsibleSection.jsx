import React, { useState } from 'react'

// 접기/펼치기 섹션 — 세부 카드들을 깔끔하게 묶을 때 사용
export default function CollapsibleSection({ title, children, defaultOpen = false, icon = '▸' }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div style={{ marginBottom: 14 }}>
      <button
        onClick={() => setOpen(!open)}
        className="card"
        style={{
          width: '100%',
          textAlign: 'left',
          margin: 0,
          marginBottom: open ? 10 : 0,
          padding: '14px 16px',
          cursor: 'pointer',
          background: open ? 'var(--surface-2)' : 'var(--grad-surface)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          border: '1px solid var(--border)',
        }}
      >
        <span style={{ fontWeight: 700, fontSize: 14, letterSpacing: '0.01em' }}>{title}</span>
        <span style={{
          color: 'var(--text-dim)',
          fontSize: 14,
          transform: open ? 'rotate(90deg)' : 'rotate(0deg)',
          transition: 'transform 0.2s ease',
          display: 'inline-block',
        }}>{icon}</span>
      </button>
      {open && <div>{children}</div>}
    </div>
  )
}
