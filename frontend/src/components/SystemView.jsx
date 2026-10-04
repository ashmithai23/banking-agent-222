import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { agentIcon, agentLabel, agentRoleDesc } from './common.jsx'

export default function SystemView({ health }) {
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = () => {
    setLoading(true)
    api.metrics()
      .then((m) => {
        setMetrics(m)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const successRate = metrics?.performance
    ? (
        (metrics.performance.successful_analyses /
          Math.max(1, metrics.performance.total_requests)) *
        100
      ).toFixed(1)
    : 100

  return (
    <div className="kb-grid">
      {/* ---------------- LEFT: Core System Telemetry ---------------- */}
      <section className="panel">
        <div className="row between">
          <h2>
            <span className="h2-icon">⚡</span> System Telemetry &amp; Health
          </h2>
          <button className="ghost" onClick={load} disabled={loading}>
            {loading ? 'Refreshing…' : '🔄 Refresh Metrics'}
          </button>
        </div>

        {error && <div className="banner banner-bad">{error}</div>}

        {health && (
          <div className="profile-card" style={{ marginTop: '10px' }}>
            <div className="profile-title">Active Foundation Stack</div>
            <div className="kv">
              <span>LLM Engine Provider</span>
              <strong style={{ color: 'var(--brand-cyan)' }}>
                {health.llm_mode.toUpperCase()}
              </strong>
            </div>
            <div className="kv">
              <span>Deployment Model</span>
              <code className="font-mono">{health.llm_model}</code>
            </div>
            <div className="kv">
              <span>Core Vector Database</span>
              <span>ChromaDB Persistent (Local)</span>
            </div>
            <div className="kv">
              <span>Customer Data Store</span>
              <span>{health.sql_connected ? 'Azure SQL Database' : 'Mock Enterprise Core Banking Fallback'}</span>
            </div>
            <div className="kv">
              <span>Ingested Policy Documents</span>
              <span className="font-mono">{health.documents} documents</span>
            </div>
            <div className="kv">
              <span>Indexed Vector Chunks</span>
              <span className="font-mono">{health.chunks} chunks</span>
            </div>
          </div>
        )}

        {/* Runtime Performance Telemetry */}
        {metrics && (
          <>
            <h3>Runtime Reliability Metrics</h3>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '8px',
                marginTop: '8px',
              }}
            >
              <div className="tool-metric">
                <span className="tool-label">Total Requests</span>
                <span className="tool-val">{metrics.performance.total_requests}</span>
                <span className="tool-sub">Invocations</span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">Success Rate</span>
                <span className="tool-val val-good">{successRate}%</span>
                <span className="tool-sub">{metrics.performance.successful_analyses} completed</span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">Stored Audits</span>
                <span className="tool-val">{metrics.reports_stored}</span>
                <span className="tool-sub">Full JSON logs</span>
              </div>
            </div>

            <div className="kv" style={{ marginTop: '12px' }}>
              <span>Server Started</span>
              <span className="font-mono small">
                {new Date(metrics.system.start_time).toLocaleString()}
              </span>
            </div>
          </>
        )}

        {/* Registered Specialist Agents */}
        {health?.agents && (
          <>
            <h3>Autonomous Specialist Agents ({health.agents.length})</h3>
            <div style={{ display: 'grid', gap: '8px', marginTop: '8px' }}>
              {health.agents.map((a) => (
                <div
                  key={a}
                  style={{
                    background: 'var(--card-bg)',
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                  }}
                >
                  <span style={{ fontSize: '18px' }}>{agentIcon(a)}</span>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: '12.5px', color: 'var(--text-primary)' }}>
                      {agentLabel(a)}
                    </strong>
                    <div className="muted small">{agentRoleDesc(a)}</div>
                  </div>
                  <span className="badge risk-low" style={{ fontSize: '10px' }}>
                    READY
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </section>

      {/* ---------------- RIGHT: ChromaDB Collections & Architecture ---------------- */}
      <section className="panel">
        <h2>
          <span className="h2-icon">📦</span> Vector Collections &amp; Architecture
        </h2>

        {metrics?.collections && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Collection Name</th>
                  <th>Indexed Chunks</th>
                  <th>Operational Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(metrics.collections).map(([k, v]) => (
                  <tr key={k}>
                    <td>
                      <code>{k}</code>
                    </td>
                    <td className="font-mono num">{v.document_count}</td>
                    <td>
                      <span className="badge risk-low">ACTIVE</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <h3>Enterprise Multi-Agent RAG Blueprint</h3>
        <div
          style={{
            background: 'var(--card-bg)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '16px',
            fontSize: '12.5px',
            lineHeight: 1.6,
            color: 'var(--text-secondary)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '18px' }}>🌐</span>
            <strong style={{ color: 'var(--text-primary)' }}>
              End-to-End Orchestration Topology
            </strong>
          </div>
          <p>
            1. <strong>Client Interface</strong>: React 19 SPA running with real-time SSE token streaming and modern fintech design system.
            <br />
            2. <strong>Supervisor Triage</strong>: Dynamic classification routing customer inquiries to specialized agent subsets.
            <br />
            3. <strong>Deterministic Math Engine</strong>: Audited Python calculation routines for DTI, mortgage formulas, and BSA AML limits.
            <br />
            4. <strong>ChromaDB Vector Retrieval</strong>: Hybrid semantic cosine similarity + BM25 keyword boosting across 6 banking policy collections.
            <br />
            5. <strong>Synthesis &amp; Audit Trail</strong>: Multi-agent consensus synthesis into validated executive reports with full audit logs.
          </p>
        </div>
      </section>
    </div>
  )
}
