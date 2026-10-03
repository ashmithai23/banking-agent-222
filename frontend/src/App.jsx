import { useEffect, useState } from 'react'
import { api } from './api.js'
import AnalysisView from './components/AnalysisView.jsx'
import KnowledgeBase from './components/KnowledgeBase.jsx'
import ReportsView from './components/ReportsView.jsx'
import SystemView from './components/SystemView.jsx'

const TABS = [
  { id: 'analysis', label: 'Analysis' },
  { id: 'knowledge', label: 'Knowledge Base' },
  { id: 'reports', label: 'Reports' },
  { id: 'system', label: 'System' },
]

export default function App() {
  const [tab, setTab] = useState('analysis')
  const [health, setHealth] = useState(null)
  const [healthError, setHealthError] = useState(null)
  const [openReport, setOpenReport] = useState(null)

  useEffect(() => {
    let cancelled = false
    const load = () =>
      api.health()
        .then((h) => { if (!cancelled) { setHealth(h); setHealthError(null) } })
        .catch((e) => { if (!cancelled) setHealthError(e.message) })
    load()
    const t = setInterval(load, 15000)
    return () => { cancelled = true; clearInterval(t) }
  }, [])

  const modeLabel = health
    ? { azure: 'Azure AI Foundry', openai: 'OpenAI', offline: 'Offline rule-based' }[health.llm_mode] || health.llm_mode
    : null

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="logo">V</span>
          <div>
            <div className="brand-name">VectraBank</div>
            <div className="brand-sub">Agentic RAG for Banking</div>
          </div>
        </div>
        <nav className="tabs">
          {TABS.map((t) => (
            <button key={t.id} className={`tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
              {t.label}
            </button>
          ))}
        </nav>
        <div className="status">
          {healthError && <span className="pill pill-bad">Backend offline</span>}
          {health && (
            <>
              <span className="pill pill-ok">● API online</span>
              <span className={`pill ${health.llm_mode === 'offline' ? 'pill-warn' : 'pill-ok'}`} title={health.llm_model}>
                LLM: {modeLabel}
              </span>
              <span className="pill">{health.chunks} chunks · {health.documents} docs</span>
            </>
          )}
        </div>
      </header>

      {healthError && (
        <div className="banner banner-bad">
          Cannot reach the backend API ({healthError}). Start it with <code>cd backend &amp;&amp; uvicorn api:app --port 8000</code>.
        </div>
      )}
      {health?.llm_mode === 'offline' && (
        <div className="banner banner-warn">
          Running without LLM credentials — agents use deterministic, policy-grounded rules. Add Azure AI Foundry or
          OpenAI keys to <code>backend/.env</code> for GPT-powered agents.
        </div>
      )}

      <main className="content">
        {tab === 'analysis' && <AnalysisView health={health} initialReport={openReport} onReportConsumed={() => setOpenReport(null)} />}
        {tab === 'knowledge' && <KnowledgeBase />}
        {tab === 'reports' && <ReportsView onOpen={(r) => { setOpenReport(r); setTab('analysis') }} />}
        {tab === 'system' && <SystemView health={health} />}
      </main>
    </div>
  )
}
