import { useEffect, useState } from 'react'
import { api } from './api.js'
import AnalysisView from './components/AnalysisView.jsx'
import KnowledgeBase from './components/KnowledgeBase.jsx'
import ReportsView from './components/ReportsView.jsx'
import SystemView from './components/SystemView.jsx'

const TABS = [
  { id: 'analysis', label: 'Analysis Workspace', icon: '🧭' },
  { id: 'knowledge', label: 'Knowledge Base', icon: '📚' },
  { id: 'reports', label: 'Audit Reports', icon: '📊' },
  { id: 'system', label: 'System Telemetry', icon: '⚡' },
]

export default function App() {
  const [tab, setTab] = useState('analysis')
  const [health, setHealth] = useState(null)
  const [healthError, setHealthError] = useState(null)
  const [openReport, setOpenReport] = useState(null)
  const [theme, setTheme] = useState(() => localStorage.getItem('vectra_theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('vectra_theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }

  useEffect(() => {
    let cancelled = false
    const load = () =>
      api.health()
        .then((h) => {
          if (!cancelled) {
            setHealth(h)
            setHealthError(null)
          }
        })
        .catch((e) => {
          if (!cancelled) setHealthError(e.message)
        })
    load()
    const t = setInterval(load, 15000)
    return () => {
      cancelled = true
      clearInterval(t)
    }
  }, [])

  const modeLabel = health
    ? { azure: 'Azure AI Foundry', openai: 'OpenAI / Gemini', offline: 'Offline Rules' }[health.llm_mode] || health.llm_mode
    : null

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand" onClick={() => setTab('analysis')}>
          <div className="logo-badge">V</div>
          <div className="brand-text">
            <span className="brand-name">VectraBank</span>
            <span className="brand-sub">Enterprise Agentic RAG Platform</span>
          </div>
        </div>

        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
            >
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </nav>

        <div className="topbar-right">
          <div className="status-group">
            {healthError && (
              <span className="status-pill error">
                <span className="ping-dot" /> Backend Offline
              </span>
            )}
            {health && (
              <>
                <span className="status-pill online">
                  <span className="ping-dot" /> Live
                </span>
                <span
                  className={`status-pill ${health.llm_mode === 'offline' ? 'warn' : 'online'}`}
                  title={health.llm_model}
                >
                  🤖 {modeLabel}
                </span>
                <span className="status-pill" title="ChromaDB Vector Store">
                  📦 {health.chunks} chunks · {health.documents} docs
                </span>
              </>
            )}
          </div>

          <button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {healthError && (
        <div className="banner banner-bad">
          <span>⚠️</span>
          <div>
            Cannot reach backend API (<code>{healthError}</code>). Run:{' '}
            <code>cd backend &amp;&amp; .\.venv\Scripts\python.exe -m uvicorn api:app --port 8000</code>
          </div>
        </div>
      )}
      {health?.llm_mode === 'offline' && (
        <div className="banner banner-warn">
          <span>ℹ️</span>
          <div>
            Running in deterministic rule-based mode. For full generative reasoning, add your Gemini/OpenAI credentials to{' '}
            <code>backend/.env</code>.
          </div>
        </div>
      )}

      <main className="content">
        {tab === 'analysis' && (
          <AnalysisView
            health={health}
            initialReport={openReport}
            onReportConsumed={() => setOpenReport(null)}
          />
        )}
        {tab === 'knowledge' && <KnowledgeBase />}
        {tab === 'reports' && (
          <ReportsView
            onOpen={(r) => {
              setOpenReport(r)
              setTab('analysis')
            }}
          />
        )}
        {tab === 'system' && <SystemView health={health} />}
      </main>
    </div>
  )
}
