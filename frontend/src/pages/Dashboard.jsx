import { FiCheckCircle, FiDatabase, FiLayers, FiUploadCloud } from 'react-icons/fi'
import StatCard from '../components/StatCard'

const PLACEHOLDER_KPIS = [
  {
    label: 'Datasets',
    value: '—',
    hint: 'Upload a file to begin',
    icon: FiUploadCloud,
    tone: 'primary',
  },
  {
    label: 'Rows processed',
    value: '—',
    hint: 'Awaiting ingestion',
    icon: FiLayers,
    tone: 'accent',
  },
  {
    label: 'Avg quality score',
    value: '—',
    hint: 'Run quality checks later',
    icon: FiCheckCircle,
    tone: 'success',
  },
  {
    label: 'Warehouse tables',
    value: '—',
    hint: 'No loads yet',
    icon: FiDatabase,
    tone: 'warning',
  },
]

function Dashboard() {
  return (
    <div className="page">
      <header className="page__header">
        <span className="page__eyebrow">Overview</span>
        <h2 className="page__heading">Welcome to DataForge</h2>
        <p className="page__description">
          Ingest, profile, analyze, and warehouse your datasets from one workspace.
          Metrics will populate once uploads and pipeline actions are connected.
        </p>
      </header>

      <section className="kpi-grid" aria-label="Key performance indicators">
        {PLACEHOLDER_KPIS.map((kpi) => (
          <StatCard key={kpi.label} {...kpi} />
        ))}
      </section>

      <section className="dashboard-panel">
        <h3 className="dashboard-panel__title">Getting started</h3>
        <p className="dashboard-panel__text">
          Use the sidebar to navigate. Upload, profiling, analytics, and quality
          workflows will be implemented in later phases. This home view is navigation
          and layout only.
        </p>
      </section>
    </div>
  )
}

export default Dashboard
