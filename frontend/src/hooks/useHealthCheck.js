import { useCallback, useEffect, useState } from 'react'
import { checkHealth } from '../services/api'

const DEFAULT_INTERVAL_MS = 30_000

/**
 * Polls GET /health and exposes online/offline status for the navbar.
 */
export function useHealthCheck({
  intervalMs = DEFAULT_INTERVAL_MS,
  enabled = true,
} = {}) {
  const [status, setStatus] = useState('checking')
  const [lastCheckedAt, setLastCheckedAt] = useState(null)
  const [error, setError] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const data = await checkHealth()
      // Explicit success path: HTTP 200 + { status: "healthy" }
      if (data?.status === 'healthy') {
        setStatus('online')
        setError(null)
        setLastCheckedAt(new Date())
        return
      }
      setStatus('offline')
      setError('Health check returned an unexpected payload')
      setLastCheckedAt(new Date())
    } catch (err) {
      setStatus('offline')
      setError(err.message || 'API unreachable')
      setLastCheckedAt(new Date())
    }
  }, [])

  useEffect(() => {
    if (!enabled) return undefined

    let cancelled = false

    const run = async () => {
      try {
        const data = await checkHealth()
        if (cancelled) return
        if (data?.status === 'healthy') {
          setStatus('online')
          setError(null)
        } else {
          setStatus('offline')
          setError('Health check returned an unexpected payload')
        }
        setLastCheckedAt(new Date())
      } catch (err) {
        if (cancelled) return
        setStatus('offline')
        setError(err.message || 'API unreachable')
        setLastCheckedAt(new Date())
      }
    }

    void run()
    const intervalTimer = window.setInterval(() => {
      void run()
    }, intervalMs)

    return () => {
      cancelled = true
      window.clearInterval(intervalTimer)
    }
  }, [enabled, intervalMs])

  return {
    status,
    isOnline: status === 'online',
    isOffline: status === 'offline',
    isChecking: status === 'checking',
    lastCheckedAt,
    error,
    refresh,
  }
}

export default useHealthCheck
