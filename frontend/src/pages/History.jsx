import { useCallback, useEffect, useMemo, useState } from 'react'
import { FiClock } from 'react-icons/fi'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'
import PageSkeleton from '../components/Skeleton'
import { useDataset } from '../hooks/useDataset'
import {
  formatDurationMs,
  formatNumber,
  formatTimestamp,
  getHistoryLoads,
} from '../utils/format'

function StatusPill({ status }) {
  const normalized = String(status || 'unknown').toLowerCase()
  const tone =
    normalized === 'success' ? 'pass' : normalized === 'failed' ? 'fail' : 'info'
  return <span className={`status-badge status-badge--${tone}`}>{normalized}</span>
}

function History() {
  const {
    warehouseHistory,
    error,
    clearError,
    fetchWarehouseHistory,
    loadingAction,
  } = useDataset()

  const [search, setSearch] = useState('')
  const [loadingHistory, setLoadingHistory] = useState(true)

  const visibleError =
    error &&
    error.error !== 'REQUEST_CANCELLED' &&
    error.error !== 'REQUEST_IN_FLIGHT'
      ? error
      : null

  const refreshHistory = useCallback(
    async (signal) => {
      setLoadingHistory(true)
      clearError()
      try {
        await fetchWarehouseHistory(100, { trackLoading: false, signal })
      } catch (err) {
        if (err?.error === 'REQUEST_CANCELLED' || signal?.aborted) return
        // Error stored in context.
      } finally {
        if (!signal?.aborted) setLoadingHistory(false)
      }
    },
    [fetchWarehouseHistory, clearError],
  )

  useEffect(() => {
    const controller = new AbortController()
    const timer = window.setTimeout(() => {
      void refreshHistory(controller.signal)
    }, 0)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [refreshHistory])

  const loads = useMemo(
    () => getHistoryLoads(warehouseHistory),
    [warehouseHistory],
  )

  const rows = useMemo(() => {
    const query = search.trim().toLowerCase()
    const filtered = query
      ? loads.filter((item) => {
          const haystack = [
            item.stored_filename,
            item.table_name,
            item.status,
            item.error_message,
          ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase()
          return haystack.includes(query)
        })
      : loads

    return [...filtered].sort((a, b) => {
      const timeA = new Date(a.timestamp || 0).getTime()
      const timeB = new Date(b.timestamp || 0).getTime()
      return timeB - timeA
    })
  }, [loads, search])

  const columns = [
    {
      key: 'stored_filename',
      label: 'Filename',
      render: (value) => value || '—',
    },
    {
      key: 'table_name',
      label: 'Dataset',
      render: (value) => value || '—',
    },
    {
      key: 'status',
      label: 'Status',
      render: (value) => <StatusPill status={value} />,
    },
    {
      key: 'timestamp',
      label: 'Timestamp',
      render: (value) => formatTimestamp(value),
    },
    {
      key: 'duration_ms',
      label: 'Duration',
      render: (value) => formatDurationMs(value),
    },
    {
      key: 'rows_loaded',
      label: 'Rows',
      render: (value) => formatNumber(value),
    },
  ]

  return (
    <div className="page history-page">
      <header className="page__header">
        <span className="page__eyebrow">Audit</span>
        <h2 className="page__heading">History</h2>
        <p className="page__description">
          Warehouse load history with search and latest-first sorting.
        </p>
      </header>

      {visibleError ? (
        <ErrorAlert
          error={visibleError}
          title="Failed to load history"
          onDismiss={clearError}
          onRetry={() => refreshHistory()}
          retryLabel="Retry history"
          retryDisabled={loadingHistory || loadingAction === 'history'}
        />
      ) : null}

      {loadingHistory ? (
        <PageSkeleton cards={0} label="Loading warehouse history…" />
      ) : !loads.length ? (
        <EmptyState
          icon={FiClock}
          title="No warehouse history yet"
          text="Load a dataset to the warehouse to start building an audit trail."
          actionLabel="Go to Warehouse"
          actionTo="/warehouse"
        />
      ) : (
        <ChartCard
          title="Warehouse loads"
          subtitle={`${rows.length} of ${loads.length} loads shown`}
          actions={
            <label className="history-search">
              <span className="visually-hidden">Search history</span>
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search filename, dataset, status…"
                aria-label="Search warehouse history"
              />
            </label>
          }
        >
          <DataTable
            columns={columns}
            rows={rows}
            emptyMessage="No loads match your search."
          />
        </ChartCard>
      )}
    </div>
  )
}

export default History
