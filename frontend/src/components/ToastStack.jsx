import { useEffect } from 'react'
import { FiAlertCircle, FiCheckCircle, FiX } from 'react-icons/fi'

function ToastItem({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return undefined
    const timer = window.setTimeout(() => {
      onClose?.(toast.id)
    }, toast.duration ?? 3500)
    return () => window.clearTimeout(timer)
  }, [toast, onClose])

  const isSuccess = toast.type === 'success'

  return (
    <div
      className={`toast toast--${isSuccess ? 'success' : 'error'}`}
      role={isSuccess ? 'status' : 'alert'}
      aria-live={isSuccess ? 'polite' : 'assertive'}
    >
      <span className="toast__icon" aria-hidden="true">
        {isSuccess ? <FiCheckCircle size={18} /> : <FiAlertCircle size={18} />}
      </span>
      <p className="toast__message">{toast.message}</p>
      <button
        type="button"
        className="toast__close"
        onClick={() => onClose?.(toast.id)}
        aria-label="Dismiss notification"
      >
        <FiX size={16} aria-hidden="true" />
      </button>
    </div>
  )
}

function ToastStack({ toasts = [], onDismiss }) {
  if (!toasts.length) return null

  return (
    <div className="toast-stack" aria-label="Notifications">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={onDismiss} />
      ))}
    </div>
  )
}

export default ToastStack
