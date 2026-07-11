import { useCallback, useState } from 'react'
import { parseApiError } from '../services/api'

/**
 * Reusable async action helper with local loading and error state.
 * Use when a call should not touch DatasetContext loading/error.
 */
export function useAsyncAction() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [data, setData] = useState(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const reset = useCallback(() => {
    setLoading(false)
    setError(null)
    setData(null)
  }, [])

  const run = useCallback(async (action) => {
    setLoading(true)
    setError(null)
    try {
      const result = await action()
      setData(result)
      return result
    } catch (err) {
      const parsed =
        err?.message && err?.error
          ? {
              message: err.message,
              error: err.error,
              details: err.details || null,
              requestId: err.requestId || null,
              status: err.status ?? null,
            }
          : parseApiError(err)
      setError(parsed)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    loading,
    error,
    data,
    run,
    clearError,
    reset,
  }
}

export default useAsyncAction
