import { correlationColor, formatNumber } from './chartTheme'

function CorrelationHeatmap({ columns = [], values = [] }) {
  if (!columns.length || !values.length) {
    return <p className="chart-card__empty">Not enough numeric columns for correlation.</p>
  }

  return (
    <div className="corr-heatmap-wrap">
      <table className="corr-heatmap">
        <thead>
          <tr>
            <th aria-hidden="true" />
            {columns.map((column) => (
              <th key={column} title={column}>
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {columns.map((rowName, rowIndex) => (
            <tr key={rowName}>
              <th scope="row" title={rowName}>
                {rowName}
              </th>
              {(values[rowIndex] || []).map((cell, colIndex) => (
                <td
                  key={`${rowName}-${columns[colIndex]}`}
                  style={{ background: correlationColor(cell) }}
                  title={`${rowName} × ${columns[colIndex]}: ${formatNumber(cell, 3)}`}
                >
                  {cell == null ? '—' : Number(cell).toFixed(2)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default CorrelationHeatmap
