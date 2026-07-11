export const CHART_COLORS = {
  primary: '#3b82f6',
  accent: '#22d3ee',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  muted: '#94a3b8',
  grid: '#1e293b',
  tooltipBg: '#111827',
  tooltipBorder: '#334155',
}

export const chartTooltipStyle = {
  backgroundColor: CHART_COLORS.tooltipBg,
  border: `1px solid ${CHART_COLORS.tooltipBorder}`,
  borderRadius: 10,
  color: '#f8fafc',
  fontSize: 12,
  boxShadow: '0 8px 24px rgba(2, 6, 23, 0.45)',
}

export function formatNumber(value, digits = 2) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  const num = Number(value)
  if (Number.isInteger(num)) return num.toLocaleString()
  return num.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  })
}

export function correlationColor(value) {
  if (value == null || Number.isNaN(Number(value))) return 'rgba(51, 65, 85, 0.55)'
  const t = Math.max(-1, Math.min(1, Number(value)))
  if (t >= 0) {
    return `rgba(59, 130, 246, ${0.15 + t * 0.7})`
  }
  return `rgba(239, 68, 68, ${0.15 + Math.abs(t) * 0.7})`
}
