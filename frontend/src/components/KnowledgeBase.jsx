import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Markdown } from './common.jsx'

const COLLECTIONS = ['fraud_detection', 'loan_policies', 'customer_support', 'risk_assessment', 'transaction_monitoring', 'compliance']

export default function KnowledgeBase() {
  const [docs, setDocs] = useState([])
  const [active, setActive] = useState(null)
  const [doc, setDoc] = useState(null)
  const [query, setQuery] = useState('large transaction monitoring threshold')
  const [selected, setSelected] = useState(COLLECTIONS)
  const [topK, setTopK] = useState(3)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.documents().then((d) => { setDocs(d); if (d[0]) setActive(d[0].name) }).catch((e) => setError(e.message))
  }, [])

  useEffect(() => {
    if (active) api.document(active).then(setDoc).catch((e) => setError(e.message))
  }, [active])

  const search = async (e) => {
    e?.preventDefault()
    if (!query.trim() || selected.length === 0) return
    setBusy(true)
    setError(null)
    try { setResults(await api.search({ query, collections: selected, top_k: topK })) }
    catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  const toggle = (c) => setSelected((s) => (s.includes(c) ? s.filter((x) => x !== c) : [...s, c]))

  return (
    <div className="kb-grid">
      <section className="panel">
        <h2>Policy Documents</h2>
        <ul className="doc-list">
          {docs.map((d) => (
            <li key={d.name}>
              <button className={active === d.name ? 'selected' : ''} onClick={() => setActive(d.name)}>
                <strong>{d.name}</strong>
                <span className="muted small">{d.department} · v{d.version} · {d.type}</span>
              </button>
            </li>
          ))}
        </ul>
        {doc && (
          <div className="doc-view">
            <div className="muted small">Effective {doc.metadata?.effective_date} · {doc.metadata?.file_size} bytes</div>
            <Markdown>{doc.content}</Markdown>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>Hybrid RAG Search</h2>
        <p className="muted small">Semantic similarity (ChromaDB, cosine) + keyword boosting across banking collections.</p>
        <form onSubmit={search}>
          <div className="row">
            <input className="grow" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search policies…" />
            <select value={topK} onChange={(e) => setTopK(Number(e.target.value))}>
              {[1, 2, 3, 5, 10].map((n) => <option key={n} value={n}>top {n} / collection</option>)}
            </select>
            <button className="primary" disabled={busy}>{busy ? 'Searching…' : 'Search'}</button>
          </div>
          <div className="chips">
            {COLLECTIONS.map((c) => (
              <button type="button" key={c} className={`chip ${selected.includes(c) ? 'on' : ''}`} onClick={() => toggle(c)}>{c}</button>
            ))}
          </div>
        </form>
        {error && <div className="banner banner-bad">{error}</div>}
        {results && results.length === 0 && <p className="muted">No results.</p>}
        {results?.map((r, i) => (
          <div key={i} className="result">
            <div className="row between">
              <strong>{r.filename}</strong>
              <span className="badge">{r.final_score.toFixed(3)}</span>
            </div>
            <div className="muted small">
              {r.collection} · {r.chunk_info} · semantic {r.relevance_score.toFixed(3)} + keyword {r.keyword_boost.toFixed(2)}
            </div>
            <details>
              <summary>Show chunk</summary>
              <Markdown>{r.document}</Markdown>
            </details>
          </div>
        ))}
      </section>
    </div>
  )
}
