import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { FiUploadCloud } from 'react-icons/fi'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'
import Loader from '../components/Loader'
import Toast from '../components/Toast'
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
    error,
    clearError,
    loadWarehouse,
    fetchWarehouseHistory,
  } = useDataset()

  const [toast, setToast] = useState(null)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const inFlightRef = useRef(false)

  const showToast = useCallback((type, message) => {
    setToast({ type, message, id: Date.now() })
  }, [])

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      setLoadingHistory(true)
      try {
        await fetchWarehouseHistory(50, { trackLoading: false })
      } catch {
        // Error stored in context.
      } finally {
        if (!cancelled) setLoadingHistory(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [fetchWarehouseHistory])

  const loads = useMemo(
    () => getHistoryLoads(warehouseHistory),
    [warehouseHistory],
  )

  const latestForDataset = useMemo(() => {
    if (!storedFilename) return null
    return loads.find((item) => item.stored_filename === storedFilename) || null
  }, [loads, storedFilename])

  const latestStatus = lastWarehouseLoad || latestForDataset

  const handleLoad = async () => {
    if (!storedFilename || loading || inFlightRef.current) return

    inFlightRef.current = true
    clearError()

    try {
      const result = await loadWarehouse(storedFilename)
      showToast(
        'success',
        `Loaded ${formatNumber(result.rows_loaded)} rows into ${result.table_name}.`,
      )
    } catch (err) {
      showToast('error', err.message || 'Warehouse load failed.')
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

      {error ? (
        <ErrorAlert
          error={error}
          title="Warehouse request failed"
          onDismiss={clearError}
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
          disabled={loading}
        >
          {loading ? 'Loading to warehouse…' : 'Load to Warehouse'}
        </button>

        {loading ? <Loader label="Loading dataset into PostgreSQL…" /> : null}
      </section>

      <section className="warehouse-status-card" aria-live="polite">
        <h3 className="warehouse-status-card__title">Latest load status</h3>
        {loadingHistory && !latestStatus ? (
          <Loader label="Fetching warehouse history…" />
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

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

export default Warehouse
