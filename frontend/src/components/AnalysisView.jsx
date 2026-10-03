import { useEffect, useRef, useState } from 'react'
import { api, streamAnalysis } from '../api.js'
import { Markdown, RiskGauge, agentLabel, money, riskClass } from './common.jsx'

const DEFAULT_AGENTS = [
  'Enhanced_Data_Gatherer', 'Enhanced_Fraud_Analyst', 'Enhanced_Loan_Analyst',
  'Enhanced_Support_Specialist', 'Enhanced_Risk_Analyst', 'Enhanced_Synthesis_Coordinator',
]

const QUICK_QUERIES = [
  'I need comprehensive financial planning including investments and retirement options',
  'I want to apply for a home loan and need to understand my eligibility',
  'I noticed some suspicious activity on my account and need help resolving it',
  'Am I eligible for a personal loan and what rate would I get?',
]

export default function AnalysisView({ health, initialReport, onReportConsumed }) {
  const [customers, setCustomers] = useState([])
  const [customerId, setCustomerId] = useState('12345')
  const [query, setQuery] = useState(QUICK_QUERIES[0])
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)
  const [stages, setStages] = useState([])
  const [retrieval, setRetrieval] = useState([])
  const [toolsData, setToolsData] = useState(null)
  const [routingData, setRoutingData] = useState(null)
  const [agentState, setAgentState] = useState({})
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [report, setReport] = useState(null)
  const abortRef = useRef(null)

  const agents = routingData?.agents || health?.agents || DEFAULT_AGENTS

  useEffect(() => {
    api.customers().then(setCustomers).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    if (initialReport) {
      setReport(initialReport)
      setCustomerId(initialReport.customer_id)
      setQuery(initialReport.query)
      const st = {}
      Object.entries(initialReport.agent_contributions || {}).forEach(([k, v]) => {
        st[k] = { status: 'done', content: v, seconds: initialReport.processing_metrics?.agent_timings_seconds?.[k] }
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
    try {
      await streamAnalysis({ customer_id: customerId.trim(), query: query.trim() }, (ev) => {
        if (ev.type === 'stage') setStages((s) => [...s, ev])
        else if (ev.type === 'retrieval') setRetrieval(ev.results)
        else if (ev.type === 'tools_executed') setToolsData(ev.tools)
        else if (ev.type === 'router_decision') setRoutingData(ev)
        else if (ev.type === 'agent_started') {
          setAgentState((s) => ({ ...s, [ev.agent]: { ...(s[ev.agent] || {}), status: 'running', content: s[ev.agent]?.content || '' } }))
          setSelectedAgent(ev.agent)
        }
        else if (ev.type === 'agent_token') {
          setAgentState((s) => ({
            ...s,
            [ev.agent]: {
              ...(s[ev.agent] || {}),
              status: 'running',
              content: (s[ev.agent]?.content || '') + ev.token
            }
          }))
          setSelectedAgent(ev.agent)
        }
        else if (ev.type === 'agent_completed') {
          setAgentState((s) => ({ ...s, [ev.agent]: { status: 'done', content: ev.content, seconds: ev.seconds } }))
          setSelectedAgent(ev.agent)
        } else if (ev.type === 'report') {
          setReport(ev.report)
          setStages((s) => [...s, { stage: 'done', message: `Analysis complete in ${ev.report.processing_metrics.total_processing_time_seconds}s` }])
        }
        else if (ev.type === 'error') setError(ev.message)
      }, controller.signal)
    } catch (e) {
      if (e.name !== 'AbortError') setError(e.message)
    } finally {
      setRunning(false)
    }
  }

  const selected = selectedAgent && agentState[selectedAgent]

  return (
    <div className="analysis-grid">
      {/* ---------------- left: customer + query ---------------- */}
      <section className="panel">
        <h2>Customer</h2>
        <div className="customer-list">
          {customers.map((c) => (
            <button
              key={c.customer_id}
              className={`customer-card ${c.customer_id === customerId ? 'selected' : ''}`}
              onClick={() => { setCustomerId(c.customer_id); if (c.sample_query) setQuery(c.sample_query) }}
            >
              <div className="row between">
                <strong>#{c.customer_id}</strong>
                <span className={`badge ${riskClass(c.computed_risk_tier)}`}>{c.computed_risk_tier}</span>
              </div>
              <div className="muted small">{c.account_type.replace('_', ' ')} · since {c.customer_since}</div>
              <div className="row between small">
                <span>{money(c.income)}</span>
                <span>Credit {c.credit_score}</span>
              </div>
            </button>
          ))}
        </div>
        <label className="field">
          <span>Customer ID</span>
          <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="e.g. 12345" />
        </label>
        {customer && (
          <div className="profile">
            <div className="kv"><span>Products</span><span>{customer.banking_products.join(', ')}</span></div>
            <div className="kv"><span>Last review</span><span>{customer.last_review_date}</span></div>
            <details>
              <summary>Recent transactions ({customer.recent_transactions.length})</summary>
              <table className="table small">
                <tbody>
                  {customer.recent_transactions.map((t, i) => (
                    <tr key={i}><td>{String(t.ts).slice(0, 10)}</td><td>{t.description}</td><td className="num">{money(t.amount)}</td></tr>
                  ))}
                </tbody>
              </table>
            </details>
          </div>
        )}
        {!customer && customerId && customers.length > 0 && (
          <p className="muted small">Unknown customer — analysis will run with an empty profile.</p>
        )}
      </section>

      {/* ---------------- center: query + pipeline + agent output ---------------- */}
      <section className="panel main-panel">
        <h2>Customer Query</h2>
        <textarea rows={3} value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Describe the customer's request…" />
        <div className="chips">
          {QUICK_QUERIES.map((q) => (
            <button key={q} className="chip" onClick={() => setQuery(q)}>{q.length > 48 ? q.slice(0, 48) + '…' : q}</button>
          ))}
        </div>
        <div className="row">
          <button className="primary" onClick={run} disabled={running || !customerId.trim() || query.trim().length < 3}>
            {running ? 'Analyzing…' : 'Run multi-agent analysis'}
          </button>
          {running && <button className="ghost" onClick={() => abortRef.current?.abort()}>Cancel</button>}
          {stages.length > 0 && <span className="muted small">{stages[stages.length - 1].message}</span>}
        </div>
        {error && <div className="banner banner-bad">{error}</div>}

        {routingData && (
          <div className="banner banner-ok router-card">
            <div className="row between">
              <strong>🧭 Supervisor Dynamic Route: {routingData.intent}</strong>
              <span className="badge badge-accent">{routingData.agents?.length} active agents</span>
            </div>
            <div className="small muted" style={{ marginTop: '4px' }}>{routingData.reasoning}</div>
          </div>
        )}

        {toolsData && (
          <div className="tools-panel">
            <div className="tools-header">
              <span className="tools-title">🧮 Verified Financial Calculations</span>
              <span className="muted small">Computed by deterministic banking algorithms</span>
            </div>
            <div className="tools-grid">
              <div className="tool-metric">
                <span className="tool-label">Debt-To-Income</span>
                <span className="tool-val">{toolsData.dti_metrics?.dti_percent}%</span>
                <span className="tool-sub">{toolsData.dti_metrics?.tier?.split(' ')[0]}</span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">Max Borrowing Capacity</span>
                <span className="tool-val">${toolsData.loan_affordability?.max_recommended_borrowing_limit?.toLocaleString()}</span>
                <span className="tool-sub">@ {toolsData.loan_affordability?.assigned_apr}% APR</span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">15-Yr Wealth Projection</span>
                <span className="tool-val">${toolsData.wealth_projection?.projected_portfolio_value?.toLocaleString()}</span>
                <span className="tool-sub">{toolsData.wealth_projection?.multiplier}x deposit multiplier</span>
              </div>
              <div className="tool-metric">
                <span className="tool-label">Fraud Scan</span>
                <span className={`tool-val ${toolsData.fraud_rule_scan?.risk_level === 'LOW' ? 'val-good' : 'val-warn'}`}>
                  {toolsData.fraud_rule_scan?.risk_level}
                </span>
                <span className="tool-sub">{toolsData.fraud_rule_scan?.alerts_count} trigger alerts</span>
              </div>
            </div>
          </div>
        )}

        <h3>Agent Pipeline</h3>
        <ol className="pipeline">
          {agents.map((a, i) => {
            const st = agentState[a]?.status || 'pending'
            return (
              <li key={a} className={`step ${st} ${selectedAgent === a ? 'selected' : ''}`}>
                <button onClick={() => agentState[a]?.content && setSelectedAgent(a)} disabled={!agentState[a]?.content}>
                  <span className="step-num">{st === 'done' ? '✓' : i + 1}</span>
                  <span className="step-name">{agentLabel(a)}</span>
                  <span className="step-meta">
                    {st === 'running' ? <span className="spinner" /> : st === 'done' ? `${agentState[a].seconds ?? ''}s` : ''}
                  </span>
                </button>
              </li>
            )
          })}
        </ol>

        {retrieval.length > 0 && (
          <details className="retrieval">
            <summary>Retrieved policy context ({retrieval.length} chunks)</summary>
            <ul>
              {retrieval.map((r, i) => (
                <li key={i}><code>{r.filename}</code> <span className="muted">· {r.collection} · score {r.score}</span></li>
              ))}
            </ul>
          </details>
        )}

        {selected?.content ? (
          <div className="agent-output">
            <div className="agent-output-title row between">
              <span>{agentLabel(selectedAgent)}</span>
              {selected?.status === 'running' && (
                <span className="streaming-badge"><span className="pulse-dot" /> Streaming live response...</span>
              )}
            </div>
            <Markdown>{selected.content}</Markdown>
          </div>
        ) : (
          !running && !report && <p className="muted empty">Select a customer, enter a query and run the analysis to watch the agents collaborate in real-time.</p>
        )}
      </section>

      {/* ---------------- right: report ---------------- */}
      <section className="panel">
        <h2>Executive Report</h2>
        {!report && <p className="muted">{running ? 'Agents are working…' : 'The synthesized report will appear here.'}</p>}
        {report && (
          <div className="report">
            <RiskGauge score={report.risk_score} tier={report.risk_assessment} />
            <div className="muted small center">{report.report_id} · {new Date(report.generated_at).toLocaleString()}</div>
            <h3>Key findings</h3>
            <ul className="list">{report.key_findings.map((f, i) => <li key={i}>{f}</li>)}</ul>
            <h3>Recommendations</h3>
            <ul className="list check">{report.recommendations.map((f, i) => <li key={i}>{f}</li>)}</ul>
            <h3>Policy references</h3>
            <div className="chips">{report.policy_references.map((p) => <span key={p} className="chip static">{p}</span>)}</div>
            <h3>Actions taken</h3>
            <ul className="list small">{report.actions_taken.map((f, i) => <li key={i}>{f}</li>)}</ul>
            <h3>Metrics</h3>
            <div className="kv"><span>Processing time</span><span>{report.processing_metrics.total_processing_time_seconds}s</span></div>
            <div className="kv"><span>Agents</span><span>{report.processing_metrics.agents_used}</span></div>
            <div className="kv"><span>Search results</span><span>{report.processing_metrics.search_results_analyzed}</span></div>
            <div className="kv"><span>LLM</span><span>{report.processing_metrics.llm_mode} · {report.processing_metrics.llm_model}</span></div>
            <button className="ghost full" onClick={() => downloadJson(report)}>Download report JSON</button>
          </div>
        )}
      </section>
    </div>
  )
}

function downloadJson(report) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${report.report_id}.json`
  a.click()
  URL.revokeObjectURL(url)
}
