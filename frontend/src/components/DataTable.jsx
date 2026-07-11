function DataTable({ columns = [], rows = [], emptyMessage = 'No data available.' }) {
  if (!rows.length) {
    return (
      <div className="data-table-empty" role="status">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} scope="col" style={column.width ? { width: column.width } : undefined}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => {
            const rowKey = row.id ?? row.rule_id ?? row.name ?? row.column ?? rowIndex
            return (
              <tr key={rowKey}>
                {columns.map((column) => {
                  const raw = row[column.key]
                  const content = column.render ? column.render(raw, row) : raw
                  return <td key={column.key}>{content ?? '—'}</td>
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable
