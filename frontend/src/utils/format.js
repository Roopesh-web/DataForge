export function formatNumber(value, digits = 0) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  const num = Number(value)
  if (digits === 0 && Number.isInteger(num)) return num.toLocaleString()
  return num.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  })
}

export function formatDurationMs(durationMs) {
  if (durationMs == null || Number.isNaN(Number(durationMs))) return '—'
  const ms = Number(durationMs)
  if (ms < 1000) return `${ms} ms`
  return `${(ms / 1000).toFixed(2)} s`
}

export function formatTimestamp(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString()
}

export function datasetDisplayName(dataset, storedFilename) {
  return dataset?.original_filename || storedFilename || 'Untitled dataset'
}

export function getHistoryLoads(warehouseHistory) {
  if (!warehouseHistory) return []
  if (Array.isArray(warehouseHistory)) return warehouseHistory
  return warehouseHistory.loads || []
}
