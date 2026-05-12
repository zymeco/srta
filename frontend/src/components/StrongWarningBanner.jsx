import React from 'react'

const ICONS = {
  1: '⚠️',
  2: '⚠️',
  3: '🚫',
  4: '🚨',
}

export default function StrongWarningBanner({ riskLevel, warning }) {
  if (!warning || riskLevel === 0) return null
  const lv = `lv${riskLevel}`
  const ico = ICONS[riskLevel] || '⚠️'
  return (
    <div className={`banner ${lv}`}>
      <div className="title">
        <span style={{ fontSize: 22 }}>{ico}</span>
        <span>{warning.warning_title || warning.warning_level}</span>
      </div>
      <div className="msg">{warning.warning_message}</div>
    </div>
  )
}
