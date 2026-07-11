import { useEffect, useState } from 'react'
import { version as reactVersion } from 'react'
import {
  FiActivity,
  FiCpu,
  FiDatabase,
  FiGlobe,
  FiInfo,
  FiLayers,
  FiMonitor,
  FiServer,
} from 'react-icons/fi'
import { useHealth } from '../hooks/useHealth'
import { API_BASE_URL, fetchOpenApiInfo } from '../services/api'
import {
  APP_NAME,
  APP_STACK,
  APP_TAGLINE,
  APP_VERSION,
  DEVELOPER_NAME,
  FRONTEND_VERSION,
  PROJECT_DESCRIPTION,
  THEME_MODE,
  THEME_NAME,
} from '../config/appInfo'

function displayBackendUrl() {
  if (API_BASE_URL) return API_BASE_URL
  if (import.meta.env.DEV) {
    return 'http://localhost:8000 (Vite proxy)'
  }
  return 'http://localhost:8000'
}

function formatCheckedAt(date) {
  if (!date) return '—'
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

function SettingsRow({ label, value, mono = false }) {
  return (
    <div className="settings-row">
      <dt className="settings-row__label">{label}</dt>
      <dd className={`settings-row__value${mono ? ' settings-row__value--mono' : ''}`}>
        {value ?? '—'}
      </dd>
    </div>
  )
}

function SettingsCard({ icon: Icon, title, children, footer = null }) {
  return (
    <section className="settings-card">
      <header className="settings-card__header">
        <span className="settings-card__icon" aria-hidden="true">
          <Icon size={18} />
        </span>
        <h3 className="settings-card__title">{title}</h3>
      </header>
      <dl className="settings-card__body">{children}</dl>
      {footer}
    </section>
  )
}

function Settings() {
  const { status, lastCheckedAt, error, refresh, isChecking } = useHealth()
  const [backendInfo, setBackendInfo] = useState({
    title: null,
    version: null,
    loading: true,
  })

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        const info = await fetchOpenApiInfo()
        if (cancelled) return
        setBackendInfo({
          title: info.title,
          version: info.version,
          loading: false,
        })
      } catch {
        if (cancelled) return
        setBackendInfo({
          title: null,
          version: null,
          loading: false,
        })
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [])

  const handleRefresh = async () => {
    await refresh()
    try {
      const info = await fetchOpenApiInfo()
      setBackendInfo({
        title: info.title,
        version: info.version,
        loading: false,
      })
    } catch {
      setBackendInfo((prev) => ({ ...prev, loading: false }))
    }
  }

  const apiStatusLabel =
    status === 'online' ? 'Online' : status === 'offline' ? 'Offline' : 'Checking…'

  const apiStatusClass =
    status === 'online'
      ? 'settings-status settings-status--online'
      : status === 'offline'
        ? 'settings-status settings-status--offline'
        : 'settings-status settings-status--checking'

  const environment = import.meta.env.PROD ? 'Production' : 'Development'
  const postgresValue =
    status === 'online'
      ? 'Available via DataForge warehouse API'
      : status === 'offline'
        ? 'Unavailable while API is offline'
        : 'Checking…'

  const backendVersionValue = backendInfo.loading
    ? 'Loading…'
    : backendInfo.version || (status === 'online' ? APP_VERSION : 'Unavailable')

  const fastapiValue = backendInfo.title
    ? `${backendInfo.title} (FastAPI)`
    : 'FastAPI REST API'

  return (
    <div className="page settings-page">
      <header className="page__header">
        <span className="page__eyebrow">Configuration</span>
        <h2 className="page__heading">Settings</h2>
        <p className="page__description">
          Read-only platform information for {APP_NAME}. Connection details and runtime
          metadata are shown for reference — nothing here is editable.
        </p>
      </header>

      <div className="settings-grid">
        <SettingsCard
          icon={FiGlobe}
          title="Connection"
          footer={
            <div className="settings-card__footer">
              <button
                type="button"
                className="settings-refresh-btn"
                onClick={handleRefresh}
                disabled={isChecking}
              >
                {isChecking ? 'Checking…' : 'Refresh status'}
              </button>
            </div>
          }
        >
          <SettingsRow label="Backend URL" value={displayBackendUrl()} mono />
          <SettingsRow
            label="API Status"
            value={
              <span className={apiStatusClass}>
                <span className="settings-status__dot" aria-hidden="true" />
                {apiStatusLabel}
              </span>
            }
          />
          <SettingsRow label="Last checked" value={formatCheckedAt(lastCheckedAt)} />
          {error ? <SettingsRow label="Last error" value={error} /> : null}
        </SettingsCard>

        <SettingsCard icon={FiServer} title="Backend">
          <SettingsRow label="Backend version" value={backendVersionValue} mono />
          <SettingsRow label="FastAPI" value={fastapiValue} />
          <SettingsRow label="API docs" value="/docs" mono />
          <SettingsRow label="Health endpoint" value="/health" mono />
        </SettingsCard>

        <SettingsCard icon={FiMonitor} title="Frontend">
          <SettingsRow label="Frontend version" value={FRONTEND_VERSION} mono />
          <SettingsRow label="Application version" value={APP_VERSION} mono />
          <SettingsRow label="React version" value={reactVersion} mono />
          <SettingsRow label="Build mode" value={environment} />
        </SettingsCard>

        <SettingsCard icon={FiDatabase} title="Data layer">
          <SettingsRow label="PostgreSQL" value={postgresValue} />
          <SettingsRow label="Warehouse" value="PostgreSQL metadata + dynamic tables" />
          <SettingsRow label="Analytics engine" value="Polars (via FastAPI)" />
        </SettingsCard>

        <SettingsCard icon={FiLayers} title="Theme">
          <SettingsRow label="Theme" value={THEME_NAME} />
          <SettingsRow label="Mode" value={THEME_MODE} />
          <SettingsRow label="Typography" value="Sora · IBM Plex Sans" />
          <SettingsRow label="Accent" value="Blue / Cyan" />
        </SettingsCard>

        <SettingsCard icon={FiCpu} title="Environment">
          <SettingsRow label="Current environment" value={environment} />
          <SettingsRow
            label="Vite mode"
            value={import.meta.env.MODE}
            mono
          />
          <SettingsRow
            label="Dev tools"
            value={import.meta.env.DEV ? 'Enabled' : 'Disabled'}
          />
        </SettingsCard>

        <SettingsCard icon={FiInfo} title="Project">
          <SettingsRow label="Product" value={APP_NAME} />
          <SettingsRow label="Tagline" value={APP_TAGLINE} />
          <SettingsRow label="Stack" value={APP_STACK} />
          <SettingsRow label="About" value={PROJECT_DESCRIPTION} />
        </SettingsCard>

        <SettingsCard icon={FiActivity} title="Developer">
          <SettingsRow label="Maintainer" value={DEVELOPER_NAME} />
          <SettingsRow label="UI" value="React + Vite" />
          <SettingsRow label="API" value="FastAPI" />
          <SettingsRow label="License display" value="Internal / project use" />
        </SettingsCard>
      </div>
    </div>
  )
}

export default Settings
