import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { CHART_COLORS, chartTooltipStyle, formatNumber } from './chartTheme'

/**
 * Backend analytics returns summary stats, not raw samples.
 * Render a distribution summary (min / median / mean / max).
 */
function NumericDistributionChart({ stats }) {
  if (!stats) {
    return <p className="chart-card__empty">No numeric statistics for this column.</p>
  }

  const data = [
    { metric: 'Min', value: stats.min },
    { metric: 'Median', value: stats.median },
    { metric: 'Mean', value: stats.mean },
    { metric: 'Max', value: stats.max },
  ].filter((item) => item.value != null && !Number.isNaN(Number(item.value)))

  if (!data.length) {
    return <p className="chart-card__empty">No plottable numeric summary values.</p>
  }

  return (
    <div className="chart-frame">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="metric" tick={{ fill: CHART_COLORS.muted, fontSize: 11 }} />
          <YAxis tick={{ fill: CHART_COLORS.muted, fontSize: 11 }} />
          <Tooltip
            contentStyle={chartTooltipStyle}
            formatter={(value) => [formatNumber(value), 'Value']}
          />
          <Bar dataKey="value" fill={CHART_COLORS.primary} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default NumericDistributionChart
