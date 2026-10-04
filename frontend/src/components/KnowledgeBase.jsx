import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Markdown } from './common.jsx'

const COLLECTIONS = [
  'fraud_detection',
  'loan_policies',
  'customer_support',
  'risk_assessment',
  'transaction_monitoring',
  'compliance',
]

export default function KnowledgeBase() {
  const [docs, setDocs] = useState([])
  const [docFilter, setDocFilter] = useState('')
  const [active, setActive] = useState(null)
  const [doc, setDoc] = useState(null)
  const [query, setQuery] = useState('large cash transaction CTR threshold BSA')
  const [selected, setSelected] = useState(COLLECTIONS)
  const [topK, setTopK] = useState(3)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadMsg, setUploadMsg] = useState(null)

  const reloadDocs = () => {
    api.documents()
      .then((d) => {
        setDocs(d)
        if (!active && d[0]) setActive(d[0].name)
      })
      .catch((e) => setError(e.message))
  }

  useEffect(() => {
    reloadDocs()
  }, [])

  useEffect(() => {
    if (active) {
      api.document(active)
        .then(setDoc)
        .catch((e) => setError(e.message))
    }
  }, [active])

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError(null)
    setUploadMsg(null)
    try {
      const res = await api.uploadDocument(file)
      setUploadMsg(
        `✅ Successfully indexed ${res.chunks} chunks from "${res.filename}" into collection "${res.collection}".`
      )
      reloadDocs()
      setActive(res.filename)
    } catch (err) {
      setError(`Upload failed: ${err.message}`)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const search = async (e) => {
    e?.preventDefault()
    if (!query.trim() || selected.length === 0) return
    setBusy(true)
    setError(null)
    try {
      setResults(await api.search({ query, collections: selected, top_k: topK }))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const toggle = (c) =>
    setSelected((s) => (s.includes(c) ? s.filter((x) => x !== c) : [...s, c]))

  const selectAll = () => setSelected(COLLECTIONS)
  const clearAll = () => setSelected([])

  const filteredDocs = docs.filter(
    (d) =>
      d.name.toLowerCase().includes(docFilter.toLowerCase()) ||
      d.department.toLowerCase().includes(docFilter.toLowerCase())
  )

  const getDocIcon = (name = '') => {
    if (name.endsWith('.pdf')) return '📕'
    if (name.endsWith('.md')) return '📘'
    return '📄'
  }

  return (
    <div className="kb-grid">
      {/* ---------------- LEFT: Document Vault & Ingestion ---------------- */}
      <section className="panel">
        <div className="row between">
          <h2>
            <span className="h2-icon">📚</span> Policy Vault
          </h2>
          <label className="primary" style={{ padding: '6px 14px', fontSize: '12.5px', cursor: 'pointer' }}>
            {uploading ? '⏳ Indexing…' : '⬆️ Upload Policy'}
            <input
              type="file"
              accept=".pdf,.md,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
          </label>
        </div>

        {uploadMsg && <div className="banner banner-ok small">{uploadMsg}</div>}
        {error && <div className="banner banner-bad small">{error}</div>}

        {/* Drag & Drop Upload Zone */}
        <div className="upload-dropzone">
          <label className="dropzone-label">
            <span style={{ fontSize: '24px' }}>📥</span>
            <span>Drag &amp; drop or click to ingest banking documents</span>
            <span className="sub">Supports PDF (.pdf), Markdown (.md), and Text (.txt)</span>
            <input
              type="file"
              accept=".pdf,.md,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
          </label>
        </div>

        {/* Document Search Filter */}
        <div style={{ marginBottom: '10px' }}>
          <input
            value={docFilter}
            onChange={(e) => setDocFilter(e.target.value)}
            placeholder="🔍 Search documents by name or department..."
            style={{ fontSize: '12.5px', padding: '7px 10px' }}
          />
        </div>

        {/* Document List */}
        <ul className="doc-list">
          {filteredDocs.map((d) => (
            <li key={d.name}>
              <button
                className={active === d.name ? 'selected' : ''}
                onClick={() => setActive(d.name)}
              >
                <div className="row between" style={{ width: '100%', margin: 0 }}>
                  <strong style={{ fontSize: '13px' }}>
                    {getDocIcon(d.name)} {d.name}
                  </strong>
                  <span className="badge" style={{ fontSize: '10px' }}>
                    v{d.version}
                  </span>
                </div>
                <div className="muted small">
                  Dept: {d.department} · Format: {d.type.toUpperCase()}
                </div>
              </button>
            </li>
          ))}
        </ul>

        {/* Document Content Viewer */}
        {doc && (
          <div className="doc-view">
            <div className="row between" style={{ marginBottom: '8px' }}>
              <strong style={{ color: 'var(--brand-cyan)' }}>📖 Document Reader</strong>
              <span className="muted small font-mono">
                Effective: {doc.metadata?.effective_date || 'N/A'} · {(doc.metadata?.file_size / 1024).toFixed(1)} KB
              </span>
            </div>
            <Markdown>{doc.content}</Markdown>
          </div>
        )}
      </section>

      {/* ---------------- RIGHT: Hybrid Vector Search Inspector ---------------- */}
      <section className="panel">
        <h2>
          <span className="h2-icon">🔍</span> Hybrid Vector Search Lab
        </h2>
        <p className="muted small" style={{ marginBottom: '14px' }}>
          Evaluate semantic cosine similarity (ChromaDB) paired with exact keyword BM25 boost across policy collections.
        </p>

        <form onSubmit={search}>
          <div className="row">
            <input
              className="grow"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search phrase or compliance requirement..."
            />
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              style={{ width: 'auto' }}
            >
              {[1, 2, 3, 5, 10].map((n) => (
                <option key={n} value={n}>
                  Top {n} Chunks
                </option>
              ))}
            </select>
            <button className="primary" disabled={busy || selected.length === 0}>
              {busy ? 'Searching…' : 'Query Vectors'}
            </button>
          </div>

          <div className="row between" style={{ marginTop: '12px' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Target Collections ({selected.length}/{COLLECTIONS.length}):
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                className="ghost"
                onClick={selectAll}
                style={{ padding: '3px 8px', fontSize: '11px' }}
              >
                Select All
              </button>
              <button
                type="button"
                className="ghost"
                onClick={clearAll}
                style={{ padding: '3px 8px', fontSize: '11px' }}
              >
                Clear
              </button>
            </div>
          </div>

          <div className="chips">
            {COLLECTIONS.map((c) => (
              <button
                type="button"
                key={c}
                className={`chip ${selected.includes(c) ? 'on' : ''}`}
                onClick={() => toggle(c)}
              >
                {selected.includes(c) ? '✓ ' : '+ '}
                {c.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </form>

        {results && results.length === 0 && (
          <div className="empty">
            <p className="muted">No matching vector chunks met the relevance threshold.</p>
          </div>
        )}

        {results?.map((r, i) => (
          <div key={i} className="result">
            <div className="row between">
              <strong>
                {getDocIcon(r.filename)} {r.filename}
              </strong>
              <span className="badge risk-low font-mono" style={{ fontSize: '12px' }}>
                Score: {r.final_score.toFixed(3)}
              </span>
            </div>
            <div className="muted small" style={{ margin: '4px 0 8px' }}>
              Collection: <span style={{ color: 'var(--brand-cyan)' }}>{r.collection}</span> · {r.chunk_info}
            </div>

            {/* Score Breakdown Bar */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '8px',
                fontSize: '11px',
                margin: '6px 0 10px',
                background: 'rgba(0, 0, 0, 0.2)',
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <div>
                <span className="muted">Semantic Cosine: </span>
                <strong className="font-mono">{r.relevance_score.toFixed(3)}</strong>
              </div>
              <div>
                <span className="muted">Keyword Boost: </span>
                <strong className="font-mono">+{r.keyword_boost.toFixed(2)}</strong>
              </div>
            </div>

            <details>
              <summary style={{ cursor: 'pointer', color: 'var(--brand-blue)', fontSize: '12.5px', fontWeight: 600 }}>
                Inspect Grounded Chunk Content
              </summary>
              <div style={{ marginTop: '8px', padding: '8px', background: 'var(--bg-app)', borderRadius: 'var(--radius-sm)' }}>
                <Markdown>{r.document}</Markdown>
              </div>
            </details>
          </div>
        ))}
      </section>
    </div>
  )
}
