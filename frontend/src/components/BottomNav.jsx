import React from 'react'
import { NavLink } from 'react-router-dom'

const items = [
  { to: '/', icon: '🔍', label: '검색', exact: true },
  { to: '/analyze/005930', icon: '📊', label: '분석' },
  { to: '/watchlist', icon: '⭐', label: '관심' },
  { to: '/history', icon: '🕒', label: '기록' },
  { to: '/settings', icon: '⚙️', label: '설정' },
]

export default function BottomNav() {
  return (
    <nav className="bottom-nav no-print">
      {items.map(it => (
        <NavLink
          key={it.to}
          to={it.to}
          end={it.exact}
          className={({ isActive }) => isActive ? 'active' : ''}
        >
          <div className="ico">{it.icon}</div>
          <div>{it.label}</div>
        </NavLink>
      ))}
    </nav>
  )
}
