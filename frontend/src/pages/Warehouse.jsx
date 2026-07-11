import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { FiUploadCloud } from 'react-icons/fi'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'
import PageSkeleton from '../components/Skeleton'
import { useToast } from '../hooks/useToast'
import { useDataset } from '../hooks/useDataset'
import {
  datasetDisplayName,
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

function Warehouse() {
  const {
    storedFilename,
    dataset,
    warehouseHistory,
    lastWarehouseLoad,
    loading,
    loadingAction,
    error,
    clearError,
    loadWarehouse,
    fetchWarehouseHistory,
  } = useDataset()
  const toast = useToast()

  const [loadingHistory, setLoadingHistory] = useState(false)
  const inFlightRef = useRef(false)

  const visibleError =
    error &&
    error.error !== 'REQUEST_CANCELLED' &&
    error.error !== 'REQUEST_IN_FLIGHT'
      ? error
      : null

  useEffect(() => {
    const controller = new AbortController()
    const timer = window.setTimeout(() => {
      void (async () => {
        setLoadingHistory(true)
        clearError()
        try {
          await fetchWarehouseHistory(50, {
            trackLoading: false,
            signal: controller.signal,
          })
        } catch (err) {
          if (err?.error === 'REQUEST_CANCELLED' || controller.signal.aborted) return
        } finally {
          if (!controller.signal.aborted) setLoadingHistory(false)
        }
      })()
    }, 0)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [fetchWarehouseHistory, clearError])

  const loads = useMemo(
    () => getHistoryLoads(warehouseHistory),
    [warehouseHistory],
  )

  const latestForDataset = useMemo(() => {
    if (!storedFilename) return null
    return loads.find((item) => item.stored_filename === storedFilename) || null
  }, [loads, storedFilename])

  const latestStatus = lastWarehouseLoad || latestForDataset
  const warehouseBusy = loadingAction === 'warehouse' || loading

  const handleLoad = async () => {
    if (!storedFilename || warehouseBusy || inFlightRef.current) return

    inFlightRef.current = true
    clearError()

    try {
      const result = await loadWarehouse(storedFilename)
      toast.success(
        `Loaded ${formatNumber(result.rows_loaded)} rows into ${result.table_name}.`,
      )
    } catch (err) {
      if (err?.error === 'REQUEST_CANCELLED') return
      toast.error(err.message || 'Warehouse load failed.')
    } finally {
      inFlightRef.current = false
    }
  }

  if (!storedFilename) {
    return (
      <div className="page warehouse-page">
        <header className="page__header">
          <span className="page__eyebrow">PostgreSQL</span>
          <h2 className="page__heading">Warehouse</h2>
          <p className="page__description">
            Load the active dataset into a PostgreSQL warehouse table.
          </p>
        </header>
        <EmptyState
          icon={FiUploadCloud}
          title="No dataset selected"
          text="Upload a dataset first, then load it into the warehouse."
        />
      </div>
    )
  }

  const name = datasetDisplayName(dataset, storedFilename)

  return (
    <div className="page warehouse-page">
      <header className="page__header">
        <span className="page__eyebrow">PostgreSQL</span>
        <h2 className="page__heading">Warehouse</h2>
        <p className="page__description">
          Persist <strong className="overview-page__filename">{name}</strong> into
          DataForge warehouse storage.
        </p>
      </header>

      {visibleError ? (
        <ErrorAlert
          error={visibleError}
          title="Warehouse request failed"
          onDismiss={clearError}
          onRetry={handleLoad}
          retryLabel="Retry warehouse load"
          retryDisabled={warehouseBusy || loadingHistory}
        />
      ) : null}

      <section className="warehouse-panel">
        <div className="warehouse-panel__copy">
          <h3>Load to Warehouse</h3>
          <p>
            Creates or refreshes a warehouse table for the current file, then records
            the load in history.
          </p>
        </div>

        <button
          type="button"
          className="upload-submit-btn"
          onClick={handleLoad}
          disabled={warehouseBusy}
          aria-busy={warehouseBusy}
        >
          {warehouseBusy ? 'Loading to warehouse…' : 'Load to Warehouse'}
        </button>
      </section>

      {loadingAction === 'warehouse' ? (
        <PageSkeleton cards={2} showPanel={false} label="Loading dataset into PostgreSQL…" />
      ) : null}

      <section className="warehouse-status-card" aria-live="polite">
        <h3 className="warehouse-status-card__title">Latest load status</h3>
        {loadingHistory && !latestStatus ? (
          <PageSkeleton cards={0} showPanel label="Fetching warehouse history…" />
        ) : latestStatus ? (
          <dl className="warehouse-status-grid">
            <div>
              <dt>Status</dt>
              <dd>
                <StatusPill status={latestStatus.status} />
              </dd>
            </div>
            <div>
              <dt>Rows loaded</dt>
              <dd>{formatNumber(latestStatus.rows_loaded)}</dd>
            </div>
            <div>
              <dt>Table</dt>
              <dd>{latestStatus.table_name || '—'}</dd>
            </div>
            <div>
              <dt>Duration</dt>
              <dd>{formatDurationMs(latestStatus.duration_ms)}</dd>
            </div>
            {latestStatus.timestamp ? (
              <div>
                <dt>Timestamp</dt>
                <dd>{formatTimestamp(latestStatus.timestamp)}</dd>
              </div>
            ) : null}
            {latestStatus.error_message ? (
              <div className="warehouse-status-grid__span">
                <dt>Error</dt>
                <dd className="warehouse-status-card__error">
                  {latestStatus.error_message}
                </dd>
              </div>
            ) : null}
          </dl>
        ) : (
          <p className="dashboard-panel__text">
            No warehouse load recorded for this dataset yet.
          </p>
        )}
      </section>

      <p className="warehouse-history-link">
        View full load history on the <Link to="/history">History</Link> page.
      </p>
    </div>
  )
}

export default Warehouse
