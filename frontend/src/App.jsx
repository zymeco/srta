import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import SearchPage from './pages/SearchPage.jsx'
import AnalysisPage from './pages/AnalysisPage.jsx'
import ReportPage from './pages/ReportPage.jsx'
import WatchlistPage from './pages/WatchlistPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import PortfolioPage from './pages/PortfolioPage.jsx'
import PrivacyPage from './pages/PrivacyPage.jsx'
import TermsPage from './pages/TermsPage.jsx'
import BottomNav from './components/BottomNav.jsx'

export default function App() {
  return (
    <div className="app-root">
      <div className="app-main">
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/analyze/:code" element={<AnalysisPage />} />
          <Route path="/report/:code" element={<ReportPage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <BottomNav />
    </div>
  )
}
