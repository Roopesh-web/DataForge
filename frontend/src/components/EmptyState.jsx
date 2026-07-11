import { Link } from 'react-router-dom'
import { FiDatabase } from 'react-icons/fi'

function EmptyState({
  icon: Icon = FiDatabase,
  title = 'No dataset selected',
  text = 'Upload a CSV, XLSX, or JSON file to continue.',
  actionLabel = 'Go to Upload',
  actionTo = '/upload',
}) {
  return (
    <div className="empty-state">
      <div className="empty-state__icon" aria-hidden="true">
        <Icon size={28} />
      </div>
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__text">{text}</p>
      {actionTo ? (
        <Link to={actionTo} className="empty-state__action">
          {actionLabel}
        </Link>
      ) : null}
    </div>
  )
}

export default EmptyState
