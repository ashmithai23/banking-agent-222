const BASE = import.meta.env.VITE_API_BASE || ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = res.statusText
    try { detail = (await res.json()).detail || detail } catch { /* ignore */ }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return res.json()
}

export const api = {
  health: () => request('/api/health'),
  metrics: () => request('/api/metrics'),
  customers: () => request('/api/customers'),
  documents: () => request('/api/documents'),
  document: (name) => request(`/api/documents/${encodeURIComponent(name)}`),
  search: (body) => request('/api/search', { method: 'POST', body: JSON.stringify(body) }),
  reports: () => request('/api/reports'),
  report: (id) => request(`/api/reports/${encodeURIComponent(id)}`),
}

/** Stream analysis progress via SSE over fetch (POST). Calls onEvent for each event. */
export async function streamAnalysis(body, onEvent, signal) {
  const res = await fetch(`${BASE}/api/analyze/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })
  if (!res.ok || !res.body) {
    let detail = res.statusText
    try { detail = (await res.json()).detail || detail } catch { /* ignore */ }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const chunk = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      const line = chunk.split('\n').find((l) => l.startsWith('data: '))
      if (line) onEvent(JSON.parse(line.slice(6)))
    }
  }
}
