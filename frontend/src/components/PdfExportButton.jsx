import React, { useState } from 'react'
import { exportElementToPdf } from '../utils/pdfExport.js'

export default function PdfExportButton({ targetId, stockName, stockCode, disabled }) {
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')

  async function onClick() {
    setErr('')
    if (disabled || !stockCode) {
      setErr('먼저 종목 분석을 실행해주세요.')
      return
    }
    const el = document.getElementById(targetId)
    if (!el) {
      setErr('먼저 종목 분석을 실행해주세요.')
      return
    }
    setLoading(true)
    try {
      await exportElementToPdf(el, stockName, stockCode)
    } catch (e) {
      console.error(e)
      setErr('PDF 생성 중 오류가 발생했습니다. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="pdf-export-btn no-print" style={{ margin: '10px 0' }}>
      <button className="btn primary full" onClick={onClick} disabled={loading}>
        {loading ? 'PDF 생성 중…' : '📄 PDF 리포트 저장'}
      </button>
      {err && <div className="error-banner" style={{ marginTop: 8 }}>{err}</div>}
    </div>
  )
}
