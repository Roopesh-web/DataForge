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

function OutlierBarChart({ data = [] }) {
  if (!data.length) {
    return <p className="chart-card__empty">No outlier results available.</p>
  }

  return (
    <div className="chart-frame">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 48 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis
            dataKey="column"
            tick={{ fill: CHART_COLORS.muted, fontSize: 11 }}
            interval={0}
            angle={-25}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fill: CHART_COLORS.muted, fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={chartTooltipStyle}
            formatter={(value) => [formatNumber(value, 0), 'Outliers']}
          />
          <Bar dataKey="outlier_count" fill={CHART_COLORS.warning} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default OutlierBarChart
