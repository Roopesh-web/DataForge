import { useCallback, useMemo, useState } from 'react'
import ToastStack from '../components/ToastStack'
import { ToastContext } from './toast-context'

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismissToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const pushToast = useCallback((type, message, options = {}) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    setToasts((current) => [
      ...current.slice(-4),
      {
        id,
        type,
        message,
        duration: options.duration ?? (type === 'error' ? 5000 : 3500),
      },
    ])
    return id
  }, [])

  const value = useMemo(
    () => ({
      pushToast,
      dismissToast,
      success: (message, options) => pushToast('success', message, options),
      error: (message, options) => pushToast('error', message, options),
    }),
    [pushToast, dismissToast],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  )
}

export default ToastProvider
