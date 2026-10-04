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
  Number(v || 0).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  })

export const agentLabel = (name = '') =>
  name.replace(/^Enhanced_/, '').replace(/_/g, ' ')

export const agentIcon = (name = '') => {
  const clean = name.toLowerCase()
  if (clean.includes('gatherer') || clean.includes('data')) return '🔍'
  if (clean.includes('fraud')) return '🛡️'
  if (clean.includes('loan')) return '🏠'
  if (clean.includes('support')) return '💬'
  if (clean.includes('risk')) return '⚖️'
  if (clean.includes('synthesis') || clean.includes('coordinator')) return '🧠'
  return '🤖'
}

export const agentRoleDesc = (name = '') => {
  const clean = name.toLowerCase()
  if (clean.includes('gatherer')) return 'Aggregates banking profiles & transaction history'
  if (clean.includes('fraud')) return 'Evaluates velocity, AML thresholds & flags anomalies'
  if (clean.includes('loan')) return 'Assesses DTI, collateral & mortgage eligibility'
  if (clean.includes('support')) return 'Cross-references customer communication & dispute logs'
  if (clean.includes('risk')) return 'Calibrates composite exposure & regulatory guardrails'
  if (clean.includes('synthesis')) return 'Synthesizes multi-agent consensus into final executive report'
  return 'Specialist banking AI assistant'
}

export const riskClass = (tier = '') => {
  const t = String(tier || '').toLowerCase()
  return (
    {
      low: 'risk-low',
      'medium-low': 'risk-medlow',
      medium: 'risk-med',
      high: 'risk-high',
      critical: 'risk-crit',
    }[t] || 'risk-low'
  )
}

export function RiskGauge({ score = 0, tier = 'low' }) {
  const clampedScore = Math.max(0, Math.min(1, score))
  const angle = -90 + clampedScore * 180

  return (
    <div className="gauge">
      <svg viewBox="0 0 200 120" aria-label={`Risk score ${clampedScore}`}>
        <defs>
          <linearGradient id="riskGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="35%" stopColor="#84cc16" />
            <stop offset="65%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
          <filter id="gaugeGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Background Track */}
        <path
          d="M 25 105 A 75 75 0 0 1 175 105"
          fill="none"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth="16"
          strokeLinecap="round"
        />

        {/* Gradient Active Arc */}
        <path
          d="M 25 105 A 75 75 0 0 1 175 105"
          fill="none"
          stroke="url(#riskGrad)"
          strokeWidth="14"
          strokeLinecap="round"
          filter="url(#gaugeGlow)"
        />

        {/* Needle Indicator */}
        <g transform={`rotate(${angle} 100 105)`} style={{ transition: 'transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)' }}>
          <line
            x1="100"
            y1="105"
            x2="100"
            y2="36"
            stroke="var(--text-primary)"
            strokeWidth="3.5"
            strokeLinecap="round"
          />
          <circle cx="100" cy="38" r="4" fill="var(--brand-cyan)" />
        </g>

        {/* Center Hub */}
        <circle cx="100" cy="105" r="9" fill="var(--panel)" stroke="var(--brand-blue)" strokeWidth="3" />
        <circle cx="100" cy="105" r="4" fill="var(--brand-blue)" />
      </svg>

      <div className="gauge-value">{clampedScore.toFixed(3)}</div>
      <span className={`badge big ${riskClass(tier)}`}>
        {tier} exposure
      </span>
    </div>
  )
}
