import { useEffect, useRef, useState } from 'react'
import { api, streamAnalysis } from '../api.js'
import {
  Markdown,
  RiskGauge,
  agentIcon,
  agentLabel,
  agentRoleDesc,
  money,
  riskClass,
} from './common.jsx'

const DEFAULT_AGENTS = [
  'Enhanced_Data_Gatherer',
  'Enhanced_Fraud_Analyst',
  'Enhanced_Loan_Analyst',
  'Enhanced_Support_Specialist',
  'Enhanced_Risk_Analyst',
  'Enhanced_Synthesis_Coordinator',
]

const QUICK_QUERIES = [
  {
    category: '🏠 Lending',
    label: 'Home Loan & DTI Eligibility',
    text: 'I want to apply for a 30-year fixed home loan and need to understand my borrowing limit, DTI eligibility, and required down payment.',
  },
  {
    category: '📈 Wealth',
    label: '15-Year Wealth & Retirement Plan',
    text: 'I need comprehensive financial planning including index fund compounding, monthly contributions, and retirement wealth projections.',
  },
  {
    category: '🛡️ Compliance',
    label: 'Suspicious Activity & Wire Check',
    text: 'I noticed unusual international wire activity and potential structuring on my business account. Please review transaction compliance.',
  },
  {
    category: '💳 Accounts',
    label: 'Personal Loan & Fee Schedule',
    text: 'Am I eligible for a personal line of credit, what interest rate would I receive, and what are the overdraft terms?',
  },
]

export default function AnalysisView({ health, initialReport, onReportConsumed }) {
  const [customers, setCustomers] = useState([])
  const [customerSearch, setCustomerSearch] = useState('')
  const [customerId, setCustomerId] = useState('12345')
  const [query, setQuery] = useState(QUICK_QUERIES[0].text)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)
  const [stages, setStages] = useState([])
  const [retrieval, setRetrieval] = useState([])
  const [toolsData, setToolsData] = useState(null)
  const [routingData, setRoutingData] = useState(null)
  const [agentState, setAgentState] = useState({})
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [report, setReport] = useState(null)
  const [toastMessage, setToastMessage] = useState(null)
  const [checkedRecommendations, setCheckedRecommendations] = useState({})
  const abortRef = useRef(null)

  const showToast = (msg) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 3500)
  }

  const agents = routingData?.agents || health?.agents || DEFAULT_AGENTS

  useEffect(() => {
    api.customers()
      .then(setCustomers)
      .catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    if (initialReport) {
      setReport(initialReport)
      setCustomerId(initialReport.customer_id)
      setQuery(initialReport.query)
      const st = {}
      Object.entries(initialReport.agent_contributions || {}).forEach(([k, v]) => {
        st[k] = {
          status: 'done',
          content: v,
          seconds: initialReport.processing_metrics?.agent_timings_seconds?.[k],
        }
      })
      setAgentState(st)
      setStages([])
      setRetrieval([])
      setToolsData(null)
      setRoutingData(null)
      setSelectedAgent(Object.keys(st).pop() || 'Enhanced_Synthesis_Coordinator')
      onReportConsumed?.()
    }
  }, [initialReport, onReportConsumed])

  const customer = customers.find((c) => c.customer_id === customerId)

  const filteredCustomers = customers.filter(
    (c) =>
      c.customer_id.toLowerCase().includes(customerSearch.toLowerCase()) ||
      c.account_type.toLowerCase().includes(customerSearch.toLowerCase())
  )

  const run = async () => {
    if (!customerId.trim() || query.trim().length < 3) return
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setRunning(true)
    setError(null)
    setStages([])
    setRetrieval([])
    setToolsData(null)
    setRoutingData(null)
    setAgentState({})
    setReport(null)
    setSelectedAgent(null)
    setCheckedRecommendations({})

    try {
      await streamAnalysis(
        { customer_id: customerId.trim(), query: query.trim() },
        (ev) => {
          if (ev.type === 'stage') setStages((s) => [...s, ev])
          else if (ev.type === 'retrieval') setRetrieval(ev.results)
          else if (ev.type === 'tools_executed') setToolsData(ev.tools)
          else if (ev.type === 'router_decision') setRoutingData(ev)
          else if (ev.type === 'agent_started') {
            setAgentState((s) => ({
              ...s,
              [ev.agent]: {
                ...(s[ev.agent] || {}),
                status: 'running',
                content: s[ev.agent]?.content || '',
              },
            }))
            setSelectedAgent(ev.agent)
          } else if (ev.type === 'agent_token') {
            setAgentState((s) => ({
              ...s,
              [ev.agent]: {
                ...(s[ev.agent] || {}),
                status: 'running',
                content: (s[ev.agent]?.content || '') + ev.token,
              },
            }))
            setSelectedAgent(ev.agent)
          } else if (ev.type === 'agent_completed') {
            setAgentState((s) => ({
              ...s,
              [ev.agent]: { status: 'done', content: ev.content, seconds: ev.seconds },
            }))
            setSelectedAgent(ev.agent)
          } else if (ev.type === 'report') {
            setReport(ev.report)
            setStages((s) => [
              ...s,
              {
                stage: 'done',
                message: `Synthesized report ready (${ev.report.processing_metrics.total_processing_time_seconds}s)`,
              },
            ])
            showToast('✅ Multi-agent analysis completed successfully!')
          } else if (ev.type === 'error') {
            setError(ev.message)
          }
        },
        controller.signal
      )
    } catch (e) {
      if (e.name !== 'AbortError') setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const selected = selectedAgent && agentState[selectedAgent]

  const copySummary = () => {
    if (!report) return
    const text = `VectraBank Executive Report (#${report.report_id})
Customer: #${report.customer_id}
Risk Tier: ${report.risk_assessment} (${report.risk_score.toFixed(3)})
Key Findings:
${report.key_findings.map((f) => `- ${f}`).join('\n')}
Recommendations:
${report.recommendations.map((r) => `[ ] ${r}`).join('\n')}`

    navigator.clipboard.writeText(text).then(() => {
      showToast('📋 Executive summary copied to clipboard!')
    })
  }

  return (
    <div className="analysis-grid">
      {/* ---------------- Toast Notification ---------------- */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            background: 'var(--panel)',
            border: '1px solid var(--border-focus)',
            color: 'var(--text-primary)',
            padding: '12px 18px',
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-lg)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            animation: 'slideDown 0.25s ease',
          }}
        >
          <span>{toastMessage}</span>
        </div>
      )}

      {/* ---------------- LEFT COLUMN: Customer Intelligence Hub ---------------- */}
      <section className="panel">
        <div className="row between" style={{ margin: '0 0 10px' }}>
          <h2>
            <span className="h2-icon">👤</span> Customer Intelligence
          </h2>
          <span className="badge" style={{ background: 'var(--accent-soft)', color: 'var(--brand-blue)' }}>
            {customers.length} Profiles
          </span>
        </div>

        <div className="customer-search-box">
          <input
            value={customerSearch}
            onChange={(e) => setCustomerSearch(e.target.value)}
            placeholder="🔍 Filter by ID, type (e.g. wealth, standard)..."
            style={{ fontSize: '12.5px', padding: '7px 10px' }}
          />
        </div>

        <div className="chips" style={{ margin: '4px 0 10px', gap: '5px' }}>
          {['ALL', 'LOW', 'MEDIUM', 'HIGH'].map((t) => (
            <button
              key={t}
              className={`chip ${
                (customerSearch === '' && t === 'ALL') || customerSearch.toUpperCase() === t
                  ? 'on'
                  : ''
              }`}
              onClick={() => setCustomerSearch(t === 'ALL' ? '' : t.toLowerCase())}
              style={{ padding: '3px 8px', fontSize: '11px' }}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="muted small" style={{ marginBottom: '8px', fontSize: '11px' }}>
          Showing {filteredCustomers.length} of {customers.length} customer records
        </div>

        <div className="customer-list">
          {filteredCustomers.map((c) => (
            <button
              key={c.customer_id}
              className={`customer-card ${c.customer_id === customerId ? 'selected' : ''}`}
              onClick={() => {
                setCustomerId(c.customer_id)
                if (c.sample_query) setQuery(c.sample_query)
              }}
            >
              <div className="customer-card-header">
                <span className="customer-id-tag">#{c.customer_id}</span>
                <span className={`badge ${riskClass(c.computed_risk_tier)}`}>
                  {c.computed_risk_tier}
                </span>
              </div>
              <div className="customer-meta">
                {c.account_type.replace('_', ' ')} · member since {c.customer_since}
              </div>
              <div className="customer-stats">
                <span style={{ color: 'var(--ok)' }}>{money(c.income)}/yr</span>
                <span className="credit-score-pill">FICO {c.credit_score}</span>
              </div>
            </button>
          ))}
        </div>

        <label className="field">
          <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Selected Customer ID</span>
          <input
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            placeholder="Enter ID (e.g. 12345)"
            className="font-mono"
          />
        </label>

        {customer && (
          <div className="profile-card">
            <div className="profile-title">Account Blueprint</div>
            <div className="kv">
              <span>Holdings</span>
              <span>{customer.banking_products.join(', ')}</span>
            </div>
            <div className="kv">
              <span>Last Review</span>
              <span>{customer.last_review_date}</span>
            </div>
            <details style={{ marginTop: '10px' }}>
              <summary style={{ fontSize: '12.5px', fontWeight: 600 }}>
                Transaction Ledger ({customer.recent_transactions.length})
              </summary>
              <table className="table" style={{ marginTop: '6px', fontSize: '11.5px' }}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Detail</th>
                    <th style={{ textAlign: 'right' }}>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {customer.recent_transactions.map((t, i) => (
                    <tr key={i}>
                      <td className="font-mono">{String(t.ts).slice(0, 10)}</td>
                      <td>{t.description}</td>
                      <td
                        className="num font-mono"
                        style={{
                          color: Number(t.amount) < 0 ? 'var(--bad)' : 'var(--text-primary)',
                        }}
                      >
                        {money(t.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </details>
          </div>
        )}

        {!customer && customerId && customers.length > 0 && (
          <p className="muted small" style={{ marginTop: '12px' }}>
            Unmapped customer profile — fallback mock data will be initialized for this session.
          </p>
        )}
      </section>

      {/* ---------------- CENTER COLUMN: Query, Pipeline & Live Output ---------------- */}
      <section className="panel">
        <h2>
          <span className="h2-icon">🧭</span> Multi-Agent Analysis Workspace
        </h2>

        <div style={{ position: 'relative' }}>
          <textarea
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe the banking scenario, customer request, or loan inquiry..."
            style={{ fontSize: '14px', padding: '12px' }}
          />
        </div>

        {/* Quick Query Shortcuts */}
        <div className="chips">
          {QUICK_QUERIES.map((q, idx) => (
            <button
              key={idx}
              className="chip"
              onClick={() => setQuery(q.text)}
              title={q.text}
            >
              <span>{q.category}</span> {q.label}
            </button>
          ))}
        </div>

        {/* Action Bar */}
        <div className="row between" style={{ marginTop: '12px' }}>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button
              className="primary"
              onClick={run}
              disabled={running || !customerId.trim() || query.trim().length < 3}
            >
              {running ? (
                <>
                  <span className="spinner" /> Orchestrating Multi-Agent Pipeline…
                </>
              ) : (
                <>🚀 Launch Agentic Analysis</>
              )}
            </button>
            {running && (
              <button className="ghost" onClick={() => abortRef.current?.abort()}>
                ⏹️ Terminate
              </button>
            )}
          </div>
          {stages.length > 0 && (
            <span className="muted small font-mono">
              {stages[stages.length - 1].message}
            </span>
          )}
        </div>

        {error && (
          <div className="banner banner-bad" style={{ marginTop: '14px' }}>
            <span>⚠️</span> <div>{error}</div>
          </div>
        )}

        {/* Supervisor Dynamic Route Card */}
        {routingData && (
          <div className="router-card">
            <div className="row between">
              <strong style={{ color: 'var(--brand-cyan)' }}>
                🧭 Supervisor Intent Routing: {routingData.intent}
              </strong>
              <span className="badge" style={{ background: 'var(--brand-blue)', color: '#fff' }}>
                {routingData.agents?.length} Specialist Agents Dispatched
              </span>
            </div>
            <div className="small muted" style={{ marginTop: '6px', lineHeight: 1.5 }}>
              {routingData.reasoning}
            </div>
          </div>
        )}

        {/* Verified Deterministic Banking Tools Panel */}
        {toolsData && (
          <div className="tools-panel">
            <div className="tools-header">
              <span className="tools-title">
                🧮 Deterministic Financial Calculations
              </span>
              <span className="badge risk-low">Audited Engine</span>
            </div>
            <div className="tools-grid">
              <div className="tool-metric">
                <span className="tool-label">Debt-To-Income (DTI)</span>
                <span className="tool-val">{toolsData.dti_metrics?.dti_percent}%</span>
                <span className="tool-sub">
                  Status: {toolsData.dti_metrics?.tier?.split(' ')[0]}
                </span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">Max Borrowing Power</span>
                <span className="tool-val">
                  ${toolsData.loan_affordability?.max_recommended_borrowing_limit?.toLocaleString()}
                </span>
                <span className="tool-sub">
                  @ {toolsData.loan_affordability?.assigned_apr}% APR
                </span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">15-Yr Wealth Projection</span>
                <span className="tool-val">
                  ${toolsData.wealth_projection?.projected_portfolio_value?.toLocaleString()}
                </span>
                <span className="tool-sub">
                  {toolsData.wealth_projection?.multiplier}x Principal Multiplier
                </span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">AML / Fraud Heuristics</span>
                <span
                  className={`tool-val ${
                    toolsData.fraud_rule_scan?.risk_level === 'LOW' ? 'val-good' : 'val-warn'
                  }`}
                >
                  {toolsData.fraud_rule_scan?.risk_level}
                </span>
                <span className="tool-sub">
                  {toolsData.fraud_rule_scan?.alerts_count} Flagged Indicators
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Multi-Agent Collaboration Pipeline */}
        <h3>Specialist Agent Workflow</h3>
        <ol className="pipeline">
          {agents.map((a, i) => {
            const st = agentState[a]?.status || 'pending'
            return (
              <li
                key={a}
                className={`step ${st} ${selectedAgent === a ? 'selected' : ''}`}
                title={agentRoleDesc(a)}
              >
                <button
                  onClick={() => agentState[a]?.content && setSelectedAgent(a)}
                  disabled={!agentState[a]?.content}
                >
                  <span className="step-num">
                    {st === 'done' ? '✓' : st === 'running' ? '●' : i + 1}
                  </span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="step-name">
                      {agentIcon(a)} {agentLabel(a)}
                    </div>
                    <div className="muted" style={{ fontSize: '10.5px' }}>
                      {st === 'running' ? 'Generating reasoning...' : st === 'done' ? 'Completed' : 'Queued'}
                    </div>
                  </div>
                  <span className="step-meta">
                    {st === 'running' ? (
                      <span className="spinner" />
                    ) : st === 'done' ? (
                      `${agentState[a].seconds ?? ''}s`
                    ) : (
                      ''
                    )}
                  </span>
                </button>
              </li>
            )
          })}
        </ol>

        {/* Vector Grounding Context */}
        {retrieval.length > 0 && (
          <details
            style={{
              marginTop: '14px',
              background: 'var(--card-bg)',
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <summary style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--brand-cyan)' }}>
              📚 ChromaDB Vector Grounding ({retrieval.length} Policy Clauses Retreived)
            </summary>
            <ul style={{ paddingLeft: '20px', marginTop: '8px', fontSize: '12.5px' }}>
              {retrieval.map((r, i) => (
                <li key={i} style={{ margin: '4px 0' }}>
                  <code>{r.filename}</code> ·{' '}
                  <span className="muted">
                    Collection: <strong>{r.collection}</strong> · Similarity Score:{' '}
                    <strong>{Number(r.score).toFixed(3)}</strong>
                  </span>
                </li>
              ))}
            </ul>
          </details>
        )}

        {/* Active Agent Output Inspector */}
        {selected?.content ? (
          <div className="agent-output">
            <div className="agent-output-title">
              <span>
                {agentIcon(selectedAgent)} {agentLabel(selectedAgent)} Inspector
              </span>
              {selected?.status === 'running' && (
                <span className="streaming-badge">
                  <span className="pulse-dot" /> Streaming real-time tokens...
                </span>
              )}
            </div>
            <Markdown>{selected.content}</Markdown>
          </div>
        ) : (
          !running &&
          !report && (
            <div className="empty">
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🏦</div>
              <strong style={{ fontSize: '15px' }}>Ready for Multi-Agent Orchestration</strong>
              <p className="muted small" style={{ maxWidth: '420px', margin: '8px auto 0' }}>
                Select a customer profile, customize the inquiry or choose a quick scenario, and run the analysis to view live streaming multi-agent collaboration.
              </p>
            </div>
          )
        )}
      </section>

      {/* ---------------- RIGHT COLUMN: Executive Report & Risk Meter ---------------- */}
      <section className="panel">
        <h2>
          <span className="h2-icon">📊</span> Executive Synthesis
        </h2>

        {!report && (
          <div className="empty">
            <p className="muted">
              {running
                ? 'Synthesizing specialist inputs and computing risk scores…'
                : 'The comprehensive risk audit and synthesis report will appear here.'}
            </p>
          </div>
        )}

        {report && (
          <div className="report">
            {/* Speedometer Risk Gauge */}
            <RiskGauge score={report.risk_score} tier={report.risk_assessment} />

            <div className="center muted small font-mono" style={{ margin: '4px 0 10px' }}>
              Report ID: {report.report_id}
              <br />
              Generated: {new Date(report.generated_at).toLocaleString()}
            </div>

            {/* Key Findings */}
            <h3>Key Findings</h3>
            <ul className="list">
              {report.key_findings.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>

            {/* Interactive Recommendations */}
            <h3>Actionable Directives</h3>
            <ul className="list check">
              {report.recommendations.map((rec, i) => (
                <li
                  key={i}
                  onClick={() =>
                    setCheckedRecommendations((prev) => ({
                      ...prev,
                      [i]: !prev[i],
                    }))
                  }
                  style={{
                    cursor: 'pointer',
                    textDecoration: checkedRecommendations[i] ? 'line-through' : 'none',
                    opacity: checkedRecommendations[i] ? 0.6 : 1,
                  }}
                >
                  {rec}
                </li>
              ))}
            </ul>

            {/* Policy Grounding References */}
            <h3>Regulatory & Policy Citations</h3>
            <div className="chips">
              {report.policy_references.map((p) => (
                <span key={p} className="chip static">
                  📄 {p}
                </span>
              ))}
            </div>

            {/* Performance Telemetry */}
            <h3>Audit Telemetry</h3>
            <div className="kv">
              <span>Total Latency</span>
              <span className="font-mono">
                {report.processing_metrics.total_processing_time_seconds}s
              </span>
            </div>
            <div className="kv">
              <span>Agents Engaged</span>
              <span className="font-mono">{report.processing_metrics.agents_used}</span>
            </div>
            <div className="kv">
              <span>Model Provider</span>
              <span className="font-mono">
                {report.processing_metrics.llm_mode} ({report.processing_metrics.llm_model})
              </span>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '14px' }}>
              <button className="ghost" onClick={copySummary}>
                📋 Copy Summary
              </button>
              <button className="primary" onClick={() => downloadJson(report)}>
                💾 Export JSON
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}

function downloadJson(report) {
  const blob = new Blob([JSON.stringify(report, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${report.report_id}.json`
  a.click()
  URL.revokeObjectURL(url)
}
