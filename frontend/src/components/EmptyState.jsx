import { Link } from 'react-router-dom'
import { FiDatabase } from 'react-icons/fi'

function EmptyState({
  icon: Icon = FiDatabase,
  title = 'No dataset selected',
  text = 'Upload a CSV, XLSX, or JSON file to continue.',
  actionLabel = 'Go to Upload',
  actionTo = '/upload',
  onAction,
  actionDisabled = false,
}) {
  return (
    <div className="empty-state" role="status">
      <div className="empty-state__icon" aria-hidden="true">
        <Icon size={28} />
      </div>
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__text">{text}</p>
      {onAction ? (
        <button
          type="button"
          className="empty-state__action"
          onClick={onAction}
          disabled={actionDisabled}
        >
          {actionLabel}
        </button>
      ) : actionTo ? (
        <Link to={actionTo} className="empty-state__action">
          {actionLabel}
        </Link>
      ) : null}
    </div>
  )
}

export default EmptyState
