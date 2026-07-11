import { useEffect } from 'react'
import { FiAlertCircle, FiCheckCircle, FiX } from 'react-icons/fi'

function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return undefined
    const timer = window.setTimeout(() => {
      onClose?.()
    }, toast.duration ?? 3500)
    return () => window.clearTimeout(timer)
  }, [toast, onClose])

  if (!toast) return null

  const isSuccess = toast.type === 'success'

  return (
    <div
      className={`toast toast--${isSuccess ? 'success' : 'error'}`}
      role="status"
      aria-live="polite"
    >
      <span className="toast__icon" aria-hidden="true">
        {isSuccess ? <FiCheckCircle size={18} /> : <FiAlertCircle size={18} />}
      </span>
      <p className="toast__message">{toast.message}</p>
      <button
        type="button"
        className="toast__close"
        onClick={onClose}
        aria-label="Dismiss notification"
      >
        <FiX size={16} aria-hidden="true" />
      </button>
    </div>
  )
}

export default Toast
