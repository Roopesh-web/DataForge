import { FiAlertCircle, FiRefreshCw, FiX } from 'react-icons/fi'

/**
 * Displays normalized backend errors:
 * { error, message, details?, requestId?, status? }
 */
function ErrorAlert({
  error,
  onDismiss,
  onRetry,
  retryLabel = 'Retry',
  retryDisabled = false,
  title = 'Something went wrong',
}) {
  if (!error) return null

  const message =
    typeof error === 'string' ? error : error.message || 'An unexpected error occurred'
  const code = typeof error === 'object' ? error.error : null
  const requestId = typeof error === 'object' ? error.requestId : null
  const details = typeof error === 'object' && Array.isArray(error.details)
    ? error.details
    : null
  const isTimeout = code === 'TIMEOUT_ERROR'
  const isNetwork = code === 'NETWORK_ERROR'

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

        {isTimeout || isNetwork ? (
          <p className="error-alert__meta">
            {isTimeout
              ? 'The request timed out. Check the API and try again.'
              : 'A network problem prevented the request from completing.'}
          </p>
        ) : null}

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

        {onRetry ? (
          <div className="error-alert__actions">
            <button
              type="button"
              className="error-alert__retry"
              onClick={onRetry}
              disabled={retryDisabled}
            >
              <FiRefreshCw size={14} aria-hidden="true" />
              {retryLabel}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default ErrorAlert
