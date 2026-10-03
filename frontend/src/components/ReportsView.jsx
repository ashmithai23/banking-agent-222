import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { riskClass } from './common.jsx'

export default function ReportsView({ onOpen }) {
  const [reports, setReports] = useState(null)
  const [error, setError] = useState(null)

  const load = () => api.reports().then(setReports).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  const open = async (id) => {
    try { onOpen(await api.report(id)) } catch (e) { setError(e.message) }
  }

  return (
    <section className="panel">
      <div className="row between">
        <h2>Generated Reports</h2>
        <button className="ghost" onClick={load}>Refresh</button>
      </div>
      {error && <div className="banner banner-bad">{error}</div>}
      {reports && reports.length === 0 && <p className="muted">No reports yet — run an analysis first.</p>}
      {reports && reports.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr><th>Report</th><th>Customer</th><th>Query</th><th>Risk</th><th>Time</th><th>Generated</th><th /></tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.report_id}>
                  <td><code>{r.report_id}</code></td>
                  <td>#{r.customer_id}</td>
                  <td className="truncate" title={r.query}>{r.query}</td>
                  <td><span className={`badge ${riskClass(r.risk_assessment)}`}>{r.risk_assessment} · {r.risk_score.toFixed(2)}</span></td>
                  <td>{r.processing_time}s</td>
                  <td>{new Date(r.generated_at).toLocaleString()}</td>
                  <td><button className="ghost" onClick={() => open(r.report_id)}>Open</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
