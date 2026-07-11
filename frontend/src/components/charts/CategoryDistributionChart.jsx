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

function CategoryDistributionChart({ data = [] }) {
  if (!data.length) {
    return <p className="chart-card__empty">No category frequencies available.</p>
  }

  return (
    <div className="chart-frame">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 48 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis
            dataKey="value"
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            interval={0}
            angle={-20}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fill: CHART_COLORS.muted, fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={chartTooltipStyle}
            formatter={(value) => [formatNumber(value, 0), 'Frequency']}
          />
          <Bar dataKey="frequency" fill={CHART_COLORS.accent} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default CategoryDistributionChart
