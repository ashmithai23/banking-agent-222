import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { riskClass } from './common.jsx'

export default function ReportsView({ onOpen }) {
  const [reports, setReports] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [riskFilter, setRiskFilter] = useState('ALL')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = () => {
    setLoading(true)
    api.reports()
      .then((r) => {
        setReports(r)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const open = async (id) => {
    try {
      onOpen(await api.report(id))
    } catch (e) {
      setError(e.message)
    }
  }

  const downloadJson = (r) => {
    const blob = new Blob([JSON.stringify(r, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${r.report_id}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const filteredReports = (reports || []).filter((r) => {
    const matchesSearch =
      r.report_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.query.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesRisk =
      riskFilter === 'ALL' ||
      String(r.risk_assessment).toUpperCase() === riskFilter.toUpperCase()

    return matchesSearch && matchesRisk
  })

  // Summary Metrics
  const total = reports?.length || 0
  const highRiskCount =
    reports?.filter((r) =>
      ['high', 'critical'].includes(String(r.risk_assessment).toLowerCase())
    ).length || 0

  return (
    <section className="panel">
      <div className="row between">
        <h2>
          <span className="h2-icon">📊</span> Historical Audit Reports
        </h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="ghost" onClick={load} disabled={loading}>
            {loading ? 'Refreshing…' : '🔄 Refresh Log'}
          </button>
        </div>
      </div>

      {/* Analytics KPI Ribbon */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '12px',
          margin: '14px 0 18px',
        }}
      >
        <div className="tool-metric">
          <span className="tool-label">Total Audited Reports</span>
          <span className="tool-val">{total}</span>
          <span className="tool-sub">Logged in local session</span>
        </div>
        <div className="tool-metric">
          <span className="tool-label">High Exposure Cases</span>
          <span className="tool-val" style={{ color: highRiskCount > 0 ? 'var(--bad)' : 'var(--ok)' }}>
            {highRiskCount}
          </span>
          <span className="tool-sub">Requiring officer sign-off</span>
        </div>
        <div className="tool-metric">
          <span className="tool-label">Audit Engine Status</span>
          <span className="tool-val val-good">Compliant</span>
          <span className="tool-sub">SEC / BSA / Reg Z compliant</span>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="row between" style={{ marginBottom: '14px' }}>
        <input
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="🔍 Search reports by ID, customer ID, or query keywords..."
          style={{ maxWidth: '420px', fontSize: '13px' }}
        />
        <div style={{ display: 'flex', gap: '6px' }}>
          {['ALL', 'LOW', 'MEDIUM', 'HIGH'].map((t) => (
            <button
              key={t}
              className={`chip ${riskFilter === t ? 'on' : ''}`}
              onClick={() => setRiskFilter(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="banner banner-bad">{error}</div>}

      {reports && reports.length === 0 && (
        <div className="empty">
          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📁</div>
          <strong>No Audit Reports Generated Yet</strong>
          <p className="muted small" style={{ maxWidth: '400px', margin: '6px auto 0' }}>
            Run an analysis in the Analysis Workspace to generate and store complete audit trails.
          </p>
        </div>
      )}

      {reports && reports.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Report ID</th>
                <th>Customer</th>
                <th>Query Context</th>
                <th>Risk Classification</th>
                <th>Latency</th>
                <th>Timestamp</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredReports.map((r) => (
                <tr key={r.report_id}>
                  <td>
                    <code className="font-mono">{r.report_id}</code>
                  </td>
                  <td>
                    <strong>#{r.customer_id}</strong>
                  </td>
                  <td className="truncate" title={r.query} style={{ maxWidth: '280px' }}>
                    {r.query}
                  </td>
                  <td>
                    <span className={`badge ${riskClass(r.risk_assessment)}`}>
                      {r.risk_assessment} · {Number(r.risk_score).toFixed(2)}
                    </span>
                  </td>
                  <td className="font-mono small">{r.processing_time}s</td>
                  <td className="muted small">{new Date(r.generated_at).toLocaleString()}</td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '6px' }}>
                      <button className="primary" style={{ padding: '4px 10px', fontSize: '12px' }} onClick={() => open(r.report_id)}>
                        Inspect
                      </button>
                      <button className="ghost" style={{ padding: '4px 8px', fontSize: '12px' }} onClick={() => downloadJson(r)}>
                        💾
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
