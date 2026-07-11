import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { CHART_COLORS, chartTooltipStyle, formatNumber } from './chartTheme'

function MissingValuesChart({ count = 0, percentage = 0, totalCells = null }) {
  const present = Math.max((totalCells ?? 100) - count, 0)
  const data =
    totalCells != null
      ? [
          { label: 'Present', value: present },
          { label: 'Missing', value: count },
        ]
      : [
          { label: 'Present %', value: Math.max(100 - percentage, 0) },
          { label: 'Missing %', value: percentage },
        ]

  return (
    <div className="chart-frame">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid stroke={CHART_COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="label" tick={{ fill: CHART_COLORS.muted, fontSize: 11 }} />
          <YAxis tick={{ fill: CHART_COLORS.muted, fontSize: 11 }} />
          <Tooltip
            contentStyle={chartTooltipStyle}
            formatter={(value) => [
              formatNumber(value, totalCells != null ? 0 : 2),
              totalCells != null ? 'Cells' : 'Percent',
            ]}
          />
          <Bar dataKey="value" radius={[6, 6, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.label}
                fill={entry.label.startsWith('Missing') ? CHART_COLORS.danger : CHART_COLORS.success}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default MissingValuesChart
