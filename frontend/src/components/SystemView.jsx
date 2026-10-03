import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { agentLabel } from './common.jsx'

export default function SystemView({ health }) {
  const [metrics, setMetrics] = useState(null)
  const [error, setError] = useState(null)

  const load = () => api.metrics().then(setMetrics).catch((e) => setError(e.message))
  useEffect(() => { load() }, [])

  return (
    <div className="kb-grid">
      <section className="panel">
        <div className="row between">
          <h2>System Status</h2>
          <button className="ghost" onClick={load}>Refresh</button>
        </div>
        {error && <div className="banner banner-bad">{error}</div>}
        {health && (
          <>
            <div className="kv"><span>LLM provider</span><span>{health.llm_mode}</span></div>
            <div className="kv"><span>Model / deployment</span><span>{health.llm_model}</span></div>
            <div className="kv"><span>Azure SQL</span><span>{health.sql_connected ? 'connected' : 'sample-data fallback'}</span></div>
            <div className="kv"><span>Policy documents</span><span>{health.documents}</span></div>
            <div className="kv"><span>Vector chunks</span><span>{health.chunks}</span></div>
            <h3>Agents (sequential)</h3>
            <ol className="list">{health.agents.map((a) => <li key={a}>{agentLabel(a)}</li>)}</ol>
          </>
        )}
        {metrics && (
          <>
            <h3>Runtime metrics</h3>
            <div className="kv"><span>Total requests</span><span>{metrics.performance.total_requests}</span></div>
            <div className="kv"><span>Successful analyses</span><span>{metrics.performance.successful_analyses}</span></div>
            <div className="kv"><span>Failed</span><span>{metrics.system.failed_processing}</span></div>
            <div className="kv"><span>Reports stored</span><span>{metrics.reports_stored}</span></div>
            <div className="kv"><span>Started</span><span>{new Date(metrics.system.start_time).toLocaleString()}</span></div>
          </>
        )}
      </section>
      <section className="panel">
        <h2>ChromaDB Collections</h2>
        {metrics && (
          <table className="table">
            <thead><tr><th>Collection</th><th>Chunks</th><th>Status</th></tr></thead>
            <tbody>
              {Object.entries(metrics.collections).map(([k, v]) => (
                <tr key={k}><td>{k}</td><td>{v.document_count}</td><td>{v.status}</td></tr>
              ))}
            </tbody>
          </table>
        )}
        <h3>Architecture</h3>
        <p className="muted small">
          React UI → FastAPI (SSE streaming) → Semantic Kernel SequentialOrchestration of six agents, grounded by hybrid
          RAG over ChromaDB and customer data from Azure SQL (with sample-data fallback).
        </p>
      </section>
    </div>
  )
}
