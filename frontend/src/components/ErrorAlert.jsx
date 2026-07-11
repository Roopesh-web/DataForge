import { FiAlertCircle, FiX } from 'react-icons/fi'

/**
 * Displays normalized backend errors:
 * { error, message, details?, requestId?, status? }
 */
function ErrorAlert({ error, onDismiss, title = 'Something went wrong' }) {
  if (!error) return null

  const message =
    typeof error === 'string' ? error : error.message || 'An unexpected error occurred'
  const code = typeof error === 'object' ? error.error : null
  const requestId = typeof error === 'object' ? error.requestId : null
  const details = typeof error === 'object' && Array.isArray(error.details)
    ? error.details
    : null

  return (
    <div className="error-alert" role="alert">
      <div className="error-alert__icon" aria-hidden="true">
        <FiAlertCircle size={20} />
      </div>

      <div className="error-alert__body">
        <div className="error-alert__header">
          <h3 className="error-alert__title">{title}</h3>
          {onDismiss ? (
            <button
              type="button"
              className="error-alert__dismiss"
              onClick={onDismiss}
              aria-label="Dismiss error"
            >
              <FiX size={16} aria-hidden="true" />
            </button>
          ) : null}
        </div>

        <p className="error-alert__message">{message}</p>

        {code || requestId ? (
          <p className="error-alert__meta">
            {code ? <span>{code}</span> : null}
            {code && requestId ? <span aria-hidden="true"> · </span> : null}
            {requestId ? <span>Request ID: {requestId}</span> : null}
          </p>
        ) : null}

        {details?.length ? (
          <ul className="error-alert__details">
            {details.map((detail, index) => (
              <li key={`${detail.field || 'detail'}-${index}`}>
                {detail.field ? <strong>{detail.field}: </strong> : null}
                {detail.message}
                {detail.code ? ` (${detail.code})` : null}
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </div>
  )
}

export default ErrorAlert
