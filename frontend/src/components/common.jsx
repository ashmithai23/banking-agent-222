import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export function Markdown({ children }) {
  return (
    <div className="markdown">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children || ''}</ReactMarkdown>
    </div>
  )
}

export const money = (v) =>
  Number(v || 0).toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

export const agentLabel = (name = '') => name.replace(/^Enhanced_/, '').replace(/_/g, ' ')

export const riskClass = (tier = '') =>
  ({ low: 'risk-low', 'medium-low': 'risk-medlow', medium: 'risk-med', high: 'risk-high', critical: 'risk-crit' }[tier] || '')

export function RiskGauge({ score = 0, tier }) {
  const pct = Math.max(0, Math.min(1, score))
  const angle = -90 + pct * 180
  return (
    <div className="gauge">
      <svg viewBox="0 0 200 115" aria-label={`Risk score ${score}`}>
        <defs>
          <linearGradient id="g" x1="0" x2="1">
            <stop offset="0%" stopColor="#16a34a" />
            <stop offset="50%" stopColor="#eab308" />
            <stop offset="100%" stopColor="#dc2626" />
          </linearGradient>
        </defs>
        <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="url(#g)" strokeWidth="16" strokeLinecap="round" />
        <g transform={`rotate(${angle} 100 100)`}>
          <line x1="100" y1="100" x2="100" y2="32" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
        </g>
        <circle cx="100" cy="100" r="7" fill="currentColor" />
      </svg>
      <div className="gauge-value">{score.toFixed(3)}</div>
      <span className={`badge big ${riskClass(tier)}`}>{tier}</span>
    </div>
  )
}
