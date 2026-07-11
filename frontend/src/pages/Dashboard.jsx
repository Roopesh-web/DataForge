import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FiBarChart2,
  FiCheckCircle,
  FiClock,
  FiColumns,
  FiDatabase,
  FiFileText,
  FiLayers,
  FiShield,
  FiUploadCloud,
} from 'react-icons/fi'
import ChartCard from '../components/ChartCard'
import EmptyState from '../components/EmptyState'
import StatCard from '../components/StatCard'
import { useDataset } from '../hooks/useDataset'
import {
  datasetDisplayName,
  formatNumber,
  formatTimestamp,
  getHistoryLoads,
} from '../utils/format'

const QUICK_ACTIONS = [
  { to: '/upload', label: 'Upload', icon: FiUploadCloud },
  { to: '/overview', label: 'Overview', icon: FiLayers },
  { to: '/analytics', label: 'Analytics', icon: FiBarChart2 },
  { to: '/quality', label: 'Quality', icon: FiShield },
  { to: '/warehouse', label: 'Warehouse', icon: FiDatabase },
  { to: '/history', label: 'History', icon: FiClock },
]

function Dashboard() {
  const {
    storedFilename,
    dataset,
    profile,
    quality,
    warehouseHistory,
    lastWarehouseLoad,
    fetchWarehouseHistory,
  } = useDataset()
  const [historyReady, setHistoryReady] = useState(Boolean(warehouseHistory))

  useEffect(() => {
    const controller = new AbortController()
    let cancelled = false

    const load = async () => {
      try {
        await fetchWarehouseHistory(50, {
          trackLoading: false,
          signal: controller.signal,
        })
      } catch {
        // History may be empty or API offline; dashboard still shows local context.
      } finally {
        if (!cancelled && !controller.signal.aborted) {
          setHistoryReady(true)
        }
      }
    }

    void load()
    return () => {
      cancelled = true
      controller.abort()
    }
  }, [fetchWarehouseHistory, storedFilename, lastWarehouseLoad])

  const loads = useMemo(
    () => getHistoryLoads(warehouseHistory),
    [warehouseHistory],
  )

  const currentName = datasetDisplayName(dataset, storedFilename)
  const profileMatches = profile?.stored_filename === storedFilename
  const qualityMatches = quality?.stored_filename === storedFilename
  const rows = profileMatches ? profile.row_count : null
  const columns = profileMatches ? profile.column_count : null
  const qualityScore = qualityMatches
    ? quality.validation_summary?.quality_score
    : null

  const recentActivity = useMemo(() => {
    const events = []

    if (dataset?.timestamp) {
      events.push({
        id: `upload-${dataset.stored_filename || storedFilename}`,
        title: 'Dataset uploaded',
        detail: datasetDisplayName(dataset, storedFilename),
        timestamp: dataset.timestamp,
        tone: 'primary',
      })
    }

    for (const item of loads.slice(0, 8)) {
      events.push({
        id: `load-${item.id}`,
        title:
          item.status === 'success'
            ? 'Warehouse load succeeded'
            : 'Warehouse load failed',
        detail: `${item.table_name || item.stored_filename} · ${formatNumber(item.rows_loaded)} rows`,
        timestamp: item.timestamp,
        tone: item.status === 'success' ? 'success' : 'danger',
      })
    }

    return events
      .sort(
        (a, b) =>
          new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime(),
      )
      .slice(0, 8)
  }, [dataset, storedFilename, loads])

  return (
    <div className="page dashboard-page">
      <header className="page__header">
        <span className="page__eyebrow">Overview</span>
        <h2 className="page__heading">Dashboard</h2>
        <p className="page__description">
          Live status for the active dataset, quality score, and recent warehouse
          activity.
        </p>
      </header>

      {!storedFilename ? (
        <EmptyState
          icon={FiUploadCloud}
          title="No dataset loaded"
          text="Upload a CSV, XLSX, or JSON file to populate dashboard metrics."
          actionLabel="Go to Upload"
          actionTo="/upload"
        />
      ) : null}

      <section className="kpi-grid" aria-label="Key metrics">
        <StatCard
          label="Active dataset"
          value={storedFilename ? currentName : '—'}
          hint={storedFilename ? 'Currently selected file' : 'Upload to begin'}
          icon={FiFileText}
          compact
        />
        <StatCard
          label="Rows"
          value={formatNumber(rows)}
          hint={profileMatches ? 'From latest profile' : 'Run Dataset Overview'}
          icon={FiDatabase}
        />
        <StatCard
          label="Columns"
          value={formatNumber(columns)}
          hint={profileMatches ? 'From latest profile' : 'Run Dataset Overview'}
          icon={FiColumns}
        />
        <StatCard
          label="Quality score"
          value={
            qualityScore == null || Number.isNaN(Number(qualityScore))
              ? '—'
              : Number(qualityScore).toFixed(1)
          }
          hint={qualityMatches ? 'From latest quality check' : 'Run Data Quality'}
          icon={FiCheckCircle}
          tone="success"
        />
      </section>

      <section className="dashboard-split" aria-label="Activity and shortcuts">
        <ChartCard
          title="Recent activity"
          subtitle={
            historyReady
              ? 'Uploads and warehouse loads'
              : 'Refreshing warehouse history…'
          }
        >
          {recentActivity.length ? (
            <ul className="activity-list">
              {recentActivity.map((event) => (
                <li
                  key={event.id}
                  className={`activity-list__item activity-list__item--${event.tone}`}
                >
                  <div>
                    <p className="activity-list__title">{event.title}</p>
                    <p className="activity-list__detail">{event.detail}</p>
                  </div>
                  <time className="activity-list__time" dateTime={event.timestamp || undefined}>
                    {formatTimestamp(event.timestamp)}
                  </time>
                </li>
              ))}
            </ul>
          ) : (
            <p className="chart-card__empty">
              {historyReady
                ? 'No recent activity yet. Upload a dataset or load to the warehouse.'
                : 'Loading activity…'}
            </p>
          )}
        </ChartCard>

        <ChartCard title="Quick actions" subtitle="Jump to common workflows">
          <div className="quick-actions">
            {QUICK_ACTIONS.map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to} className="quick-actions__item">
                <Icon aria-hidden="true" />
                <span>{label}</span>
              </Link>
            ))}
          </div>
        </ChartCard>
      </section>
    </div>
  )
}

export default Dashboard
