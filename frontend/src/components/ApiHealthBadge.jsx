import { useHealth } from '../hooks/useHealth'

function ApiHealthBadge() {
  const { status, error, refresh } = useHealth()

  const label =
    status === 'online'
      ? 'API Online'
      : status === 'offline'
        ? 'API Offline'
        : 'Checking API…'

  const className =
    status === 'online'
      ? 'navbar__badge navbar__badge--online'
      : status === 'offline'
        ? 'navbar__badge navbar__badge--offline'
        : 'navbar__badge navbar__badge--checking'

  return (
    <button
      type="button"
      className={className}
      onClick={refresh}
      title={error || 'Click to refresh API status'}
      aria-label={`${label}. Click to refresh.`}
    >
      <span className="navbar__badge-dot" aria-hidden="true" />
      <span aria-live="polite">{label}</span>
    </button>
  )
}

export default ApiHealthBadge
