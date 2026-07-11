import { useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  FiAlertTriangle,
  FiColumns,
  FiDatabase,
  FiFileText,
  FiGrid,
  FiLayers,
} from 'react-icons/fi'
import DataTable from '../components/DataTable'
import ErrorAlert from '../components/ErrorAlert'
import Loader from '../components/Loader'
import StatCard from '../components/StatCard'
import { useDataset } from '../hooks/useDataset'

function formatNumber(value) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return Number(value).toLocaleString()
}

function formatPercent(value) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return `${Number(value).toFixed(2)}%`
}

function datasetDisplayName(dataset, storedFilename) {
  return dataset?.original_filename || storedFilename || 'Untitled dataset'
}

function TypeBadge({ type }) {
  const normalized = String(type || 'unknown').toLowerCase().replace(/\s+/g, '-')
  return <span className={`type-badge type-badge--${normalized}`}>{type || 'unknown'}</span>
}

function Profile() {
  const {
    storedFilename,
    dataset,
    profile,
    loading,
    error,
    clearError,
    fetchProfile,
  } = useDataset()

  useEffect(() => {
    if (!storedFilename) return undefined

    const load = async () => {
      try {
        await fetchProfile(storedFilename)
      } catch {
        // Error is stored in DatasetContext.
      }
    }

    void load()
    return undefined
  }, [storedFilename, fetchProfile])

  const profileMatches = profile?.stored_filename === storedFilename

  const missingValues = useMemo(() => {
    if (!profileMatches || !profile?.columns?.length) return 0
    return profile.columns.reduce((sum, column) => sum + (column.null_count || 0), 0)
  }, [profile, profileMatches])

  const typeSummary = useMemo(() => {
    if (!profileMatches || !profile) return '—'
    const parts = []
    if (profile.numeric_columns?.length) {
      parts.push(`${profile.numeric_columns.length} numeric`)
    }
    if (profile.categorical_columns?.length) {
      parts.push(`${profile.categorical_columns.length} categorical`)
    }
    if (profile.datetime_columns?.length) {
      parts.push(`${profile.datetime_columns.length} datetime`)
    }
    const typed = new Set([
      ...(profile.numeric_columns || []),
      ...(profile.categorical_columns || []),
      ...(profile.datetime_columns || []),
    ])
    const other = Math.max((profile.column_count || 0) - typed.size, 0)
    if (other > 0) parts.push(`${other} other`)
    return parts.length ? parts.join(' · ') : 'No typed columns'
  }, [profile, profileMatches])

  const columnRows = useMemo(() => {
    if (!profileMatches || !profile?.columns?.length) return []
    return profile.columns.map((column) => ({
      name: column.name,
      datatype: column.datatype,
      raw_dtype: column.raw_dtype,
      null_count: column.null_count,
      null_percentage: column.null_percentage,
      unique_values: column.unique_values,
      min: column.statistics?.min,
      max: column.statistics?.max,
      mean: column.statistics?.mean,
    }))
  }, [profile, profileMatches])

  const tableColumns = [
    { key: 'name', label: 'Column' },
    {
      key: 'datatype',
      label: 'Type',
      render: (value) => <TypeBadge type={value} />,
    },
    { key: 'raw_dtype', label: 'Raw dtype' },
    {
      key: 'null_count',
      label: 'Missing',
      render: (value) => formatNumber(value),
    },
    {
      key: 'null_percentage',
      label: 'Missing %',
      render: (value) => formatPercent(value),
    },
    {
      key: 'unique_values',
      label: 'Unique',
      render: (value) => formatNumber(value),
    },
    {
      key: 'min',
      label: 'Min',
      render: (value) => (value == null ? '—' : formatNumber(value)),
    },
    {
      key: 'max',
      label: 'Max',
      render: (value) => (value == null ? '—' : formatNumber(value)),
    },
    {
      key: 'mean',
      label: 'Mean',
      render: (value) => (value == null ? '—' : Number(value).toFixed(2)),
    },
  ]

  if (!storedFilename) {
    return (
      <div className="page overview-page">
        <header className="page__header">
          <span className="page__eyebrow">Profiling</span>
          <h2 className="page__heading">Dataset Overview</h2>
          <p className="page__description">
            Explore schema inference, missing values, and column-level profiles.
          </p>
        </header>

        <div className="empty-state">
          <div className="empty-state__icon" aria-hidden="true">
            <FiDatabase size={28} />
          </div>
          <h3 className="empty-state__title">No dataset selected</h3>
          <p className="empty-state__text">
            Upload a CSV, XLSX, or JSON file to generate a profile overview.
          </p>
          <Link to="/upload" className="empty-state__action">
            Go to Upload
          </Link>
        </div>
      </div>
    )
  }

  const name = datasetDisplayName(dataset, storedFilename)
  const showLoader = loading && !profileMatches

  return (
    <div className="page overview-page">
      <header className="page__header">
        <span className="page__eyebrow">Profiling</span>
        <h2 className="page__heading">Dataset Overview</h2>
        <p className="page__description">
          Schema inference and column profiles for{' '}
          <strong className="overview-page__filename">{name}</strong>
          {profileMatches && profile?.file_format
            ? ` · ${profile.file_format.toUpperCase()}`
            : ''}
          .
        </p>
      </header>

      {error ? (
        <ErrorAlert
          error={error}
          title="Failed to load profile"
          onDismiss={clearError}
        />
      ) : null}

      {showLoader ? (
        <Loader fullPage label="Profiling dataset…" />
      ) : profileMatches ? (
        <>
          <section className="kpi-grid" aria-label="Dataset summary">
            <StatCard
              label="Dataset Name"
              value={name}
              hint={storedFilename}
              icon={FiFileText}
              tone="primary"
              compact
            />
            <StatCard
              label="Rows"
              value={formatNumber(profile.row_count)}
              hint="Total records"
              icon={FiLayers}
              tone="accent"
            />
            <StatCard
              label="Columns"
              value={formatNumber(profile.column_count)}
              hint="Fields in schema"
              icon={FiColumns}
              tone="success"
            />
            <StatCard
              label="Missing Values"
              value={formatNumber(missingValues)}
              hint={
                profile.duplicate_rows
                  ? `${formatNumber(profile.duplicate_rows)} duplicate rows`
                  : 'Across all columns'
              }
              icon={FiAlertTriangle}
              tone="warning"
            />
          </section>

          <section className="overview-panel">
            <div className="overview-panel__header">
              <h3 className="overview-panel__title">
                <FiGrid aria-hidden="true" /> Column Types
              </h3>
              <p className="overview-panel__subtitle">{typeSummary}</p>
            </div>
            <div className="type-chip-row">
              {(profile.numeric_columns || []).map((column) => (
                <span key={`num-${column}`} className="type-chip type-chip--numeric">
                  {column}
                </span>
              ))}
              {(profile.categorical_columns || []).map((column) => (
                <span key={`cat-${column}`} className="type-chip type-chip--categorical">
                  {column}
                </span>
              ))}
              {(profile.datetime_columns || []).map((column) => (
                <span key={`dt-${column}`} className="type-chip type-chip--datetime">
                  {column}
                </span>
              ))}
              {!profile.numeric_columns?.length &&
              !profile.categorical_columns?.length &&
              !profile.datetime_columns?.length ? (
                <span className="overview-panel__subtitle">No typed columns available.</span>
              ) : null}
            </div>
          </section>

          <section className="overview-panel overview-panel--table">
            <div className="overview-panel__header">
              <h3 className="overview-panel__title">Column Table</h3>
              <p className="overview-panel__subtitle">
                Null counts, uniqueness, and numeric stats per column.
              </p>
            </div>
            <DataTable
              columns={tableColumns}
              rows={columnRows}
              emptyMessage="No column profiles returned for this dataset."
            />
          </section>
        </>
      ) : !loading ? (
        <div className="empty-state">
          <div className="empty-state__icon" aria-hidden="true">
            <FiAlertTriangle size={28} />
          </div>
          <h3 className="empty-state__title">Profile unavailable</h3>
          <p className="empty-state__text">
            Profiling did not return data for this file. Try uploading again.
          </p>
          <Link to="/upload" className="empty-state__action">
            Back to Upload
          </Link>
        </div>
      ) : null}
    </div>
  )
}

export default Profile
