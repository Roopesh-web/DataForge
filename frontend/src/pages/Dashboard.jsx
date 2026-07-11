import { useEffect, useMemo } from 'react'
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

  useEffect(() => {
    const load = async () => {
      try {
        await fetchWarehouseHistory(50, { trackLoading: false })
      } catch {
        // History may be empty or API offline; dashboard still shows local context.
      }
    }
    void load()
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
  }, [dataset, loads, storedFilename])

  return (
    <div className="page dashboard-page">
      <header className="page__header">
        <span className="page__eyebrow">Overview</span>
        <h2 className="page__heading">Welcome to DataForge</h2>
        <p className="page__description">
          Live workspace metrics from your active dataset, quality results, and
          warehouse activity.
        </p>
      </header>

      <section className="kpi-grid" aria-label="Key performance indicators">
        <StatCard
          label="Current Dataset"
          value={storedFilename ? currentName : '—'}
          hint={storedFilename || 'Upload a file to begin'}
          icon={FiFileText}
          tone="primary"
          compact
        />
        <StatCard
          label="Number of Rows"
          value={rows != null ? formatNumber(rows) : '—'}
          hint={rows != null ? 'From latest profile' : 'Run Dataset Overview'}
          icon={FiLayers}
          tone="accent"
        />
        <StatCard
          label="Number of Columns"
          value={columns != null ? formatNumber(columns) : '—'}
          hint={columns != null ? 'From latest profile' : 'Run Dataset Overview'}
          icon={FiColumns}
          tone="success"
        />
        <StatCard
          label="Quality Score"
          value={
            qualityScore != null ? Number(qualityScore).toFixed(1) : '—'
          }
          hint={
            qualityScore != null ? 'From latest quality check' : 'Run Data Quality'
          }
          icon={FiCheckCircle}
          tone="warning"
        />
      </section>

      <section className="kpi-grid kpi-grid--two" aria-label="Warehouse metrics">
        <StatCard
          label="Warehouse Loads"
          value={formatNumber(loads.length)}
          hint={
            lastWarehouseLoad
              ? `Latest: ${lastWarehouseLoad.status} · ${formatNumber(lastWarehouseLoad.rows_loaded)} rows`
              : 'Loads recorded in history'
          }
          icon={FiDatabase}
          tone="primary"
        />
        <StatCard
          label="Last Upload Time"
          value={
            dataset?.timestamp ? formatTimestamp(dataset.timestamp) : '—'
          }
          hint={dataset ? 'From current session upload' : 'No upload in this session'}
          icon={FiClock}
          tone="accent"
          compact
        />
      </section>

      <div className="dashboard-split">
        <ChartCard title="Recent Activity" subtitle="Uploads and warehouse loads">
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
                  <time className="activity-list__time">
                    {formatTimestamp(event.timestamp)}
                  </time>
                </li>
              ))}
            </ul>
          ) : (
            <p className="chart-card__empty">
              No recent activity yet. Upload a dataset or load to the warehouse.
            </p>
          )}
        </ChartCard>

        <ChartCard title="Quick Actions" subtitle="Jump to the next workflow step">
          <div className="quick-actions">
            {QUICK_ACTIONS.map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to} className="quick-actions__item">
                <Icon aria-hidden="true" />
                <span>{label}</span>
              </Link>
            ))}
          </div>
        </ChartCard>
      </div>
    </div>
  )
}

export default Dashboard
