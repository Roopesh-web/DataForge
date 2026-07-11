import { useCallback, useMemo, useRef, useState } from 'react'
import {
  analyzeDataset,
  getWarehouseHistory,
  loadToWarehouse,
  profileDataset,
  qualityCheck,
  uploadFile,
} from '../services/api'
import { DatasetContext } from './dataset-context'

const initialState = {
  storedFilename: null,
  dataset: null,
  profile: null,
  analytics: null,
  quality: null,
  warehouseHistory: null,
  lastWarehouseLoad: null,
  loading: false,
  loadingAction: null,
  error: null,
}

/** Page-level reads that should yield when navigating to another view. */
const CANCELABLE_ACTIONS = new Set(['profile', 'analytics', 'quality', 'history'])

function toContextError(err) {
  return {
    message: err.message || 'An unexpected error occurred',
    error: err.error || 'UNKNOWN_ERROR',
    details: err.details || null,
    requestId: err.requestId || null,
    status: err.status ?? null,
  }
}

function isCancelError(err) {
  if (!err) return false
  if (err.error === 'REQUEST_CANCELLED') return true
  if (err.name === 'CanceledError' || err.name === 'AbortError') return true
  if (err.code === 'ERR_CANCELED') return true
  return false
}

export function DatasetProvider({ children }) {
  const [storedFilename, setStoredFilename] = useState(initialState.storedFilename)
  const [dataset, setDataset] = useState(initialState.dataset)
  const [profile, setProfile] = useState(initialState.profile)
  const [analytics, setAnalytics] = useState(initialState.analytics)
  const [quality, setQuality] = useState(initialState.quality)
  const [warehouseHistory, setWarehouseHistory] = useState(
    initialState.warehouseHistory,
  )
  const [lastWarehouseLoad, setLastWarehouseLoad] = useState(
    initialState.lastWarehouseLoad,
  )
  const [loading, setLoading] = useState(initialState.loading)
  const [loadingAction, setLoadingAction] = useState(initialState.loadingAction)
  const [error, setError] = useState(initialState.error)

  /** @type {React.MutableRefObject<Map<string, { promise: Promise<unknown>, controller: AbortController }>>} */
  const inFlightRef = useRef(new Map())
  /** Dedupes silent (trackLoading: false) warehouse history fetches by limit. */
  const silentHistoryRef = useRef(new Map())

  const syncLoadingState = useCallback(() => {
    const entries = [...inFlightRef.current.keys()]
    if (entries.length === 0) {
      setLoading(false)
      setLoadingAction(null)
      return
    }
    setLoading(true)
    setLoadingAction(entries[entries.length - 1])
  }, [])

  const abortAction = useCallback(
    (actionKey) => {
      const entry = inFlightRef.current.get(actionKey)
      if (!entry) return
      entry.controller.abort()
      inFlightRef.current.delete(actionKey)
      syncLoadingState()
    },
    [syncLoadingState],
  )

  const abortCancelableActions = useCallback(
    (exceptKey = null) => {
      for (const [key, entry] of [...inFlightRef.current.entries()]) {
        if (exceptKey && key === exceptKey) continue
        if (!CANCELABLE_ACTIONS.has(key)) continue
        entry.controller.abort()
        inFlightRef.current.delete(key)
      }
      syncLoadingState()
    },
    [syncLoadingState],
  )

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const resetDataset = useCallback(() => {
    for (const entry of inFlightRef.current.values()) {
      entry.controller.abort()
    }
    inFlightRef.current.clear()
    setStoredFilename(initialState.storedFilename)
    setDataset(initialState.dataset)
    setProfile(initialState.profile)
    setAnalytics(initialState.analytics)
    setQuality(initialState.quality)
    setWarehouseHistory(initialState.warehouseHistory)
    setLastWarehouseLoad(initialState.lastWarehouseLoad)
    setLoading(initialState.loading)
    setLoadingAction(initialState.loadingAction)
    setError(initialState.error)
  }, [])

  /**
   * Run a named async action with:
   * - promise dedupe for the same actionKey
   * - AbortController cancellation of prior cancelable reads
   * - silent handling of aborted requests
   */
  const runAction = useCallback(
    async (actionKey, action, options = {}) => {
      const { signal: externalSignal = null, cancelOthers = true } = options

      const existing = inFlightRef.current.get(actionKey)
      if (existing) {
        if (!existing.controller.signal.aborted) {
          return existing.promise
        }
        inFlightRef.current.delete(actionKey)
      }

      if (cancelOthers) {
        abortCancelableActions(actionKey)
      }

      const controller = new AbortController()

      let settle
      const promise = new Promise((resolve, reject) => {
        settle = { resolve, reject }
      })

      const entry = { promise, controller }
      inFlightRef.current.set(actionKey, entry)

      const releaseEntry = () => {
        if (inFlightRef.current.get(actionKey) === entry) {
          inFlightRef.current.delete(actionKey)
        }
        syncLoadingState()
      }

      if (externalSignal) {
        if (externalSignal.aborted) {
          controller.abort()
          releaseEntry()
          throw Object.assign(new Error('Request cancelled'), {
            error: 'REQUEST_CANCELLED',
          })
        } else {
          externalSignal.addEventListener(
            'abort',
            () => {
              controller.abort()
              releaseEntry()
            },
            { once: true },
          )
        }
      }

      setLoading(true)
      setLoadingAction(actionKey)
      setError(null)

      ;(async () => {
        try {
          if (controller.signal.aborted) {
            settle.reject(
              Object.assign(new Error('Request cancelled'), {
                error: 'REQUEST_CANCELLED',
              }),
            )
            return
          }

          const result = await action(controller.signal)
          settle.resolve(result)
        } catch (err) {
          if (isCancelError(err) || controller.signal.aborted) {
            settle.reject(
              Object.assign(new Error('Request cancelled'), {
                error: 'REQUEST_CANCELLED',
              }),
            )
            return
          }
          setError(toContextError(err))
          settle.reject(err)
        } finally {
          releaseEntry()
        }
      })()

      return promise
    },
    [abortCancelableActions, syncLoadingState],
  )

  const uploadDataset = useCallback(
    async (file, options = {}) => {
      return runAction(
        'upload',
        async (signal) => {
          const result = await uploadFile(file, { ...options, signal })
          setDataset(result)
          setStoredFilename(result.stored_filename)
          setProfile(null)
          setAnalytics(null)
          setQuality(null)
          return result
        },
        { cancelOthers: true },
      )
    },
    [runAction],
  )

  const fetchProfile = useCallback(
    async (filename = storedFilename, options = {}) => {
      const target = filename || storedFilename
      if (!target) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction(
        'profile',
        async (signal) => {
          const result = await profileDataset(target, { signal })
          setProfile(result)
          return result
        },
        { signal: options.signal, cancelOthers: options.cancelOthers !== false },
      )
    },
    [runAction, storedFilename],
  )

  const fetchAnalytics = useCallback(
    async (filename = storedFilename, options = {}) => {
      const target = filename || storedFilename
      if (!target) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction(
        'analytics',
        async (signal) => {
          const result = await analyzeDataset(target, { signal })
          setAnalytics(result)
          return result
        },
        { signal: options.signal, cancelOthers: options.cancelOthers !== false },
      )
    },
    [runAction, storedFilename],
  )

  const fetchQuality = useCallback(
    async (filename = storedFilename, options = {}) => {
      const target = filename || storedFilename
      if (!target) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction(
        'quality',
        async (signal) => {
          const result = await qualityCheck(target, { signal })
          setQuality(result)
          return result
        },
        { signal: options.signal, cancelOthers: options.cancelOthers !== false },
      )
    },
    [runAction, storedFilename],
  )

  const loadWarehouse = useCallback(
    async (filename = storedFilename, options = {}) => {
      const target = filename || storedFilename
      if (!target) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction(
        'warehouse',
        async (signal) => {
          const result = await loadToWarehouse(target, { signal })
          setLastWarehouseLoad(result)
          const history = await getWarehouseHistory(50, { signal })
          setWarehouseHistory(history)
          return result
        },
        { signal: options.signal, cancelOthers: true },
      )
    },
    [runAction, storedFilename],
  )

  const fetchWarehouseHistory = useCallback(
    async (limit = 50, options = {}) => {
      const trackLoading = options.trackLoading !== false
      const signal = options.signal

      const action = async (actionSignal) => {
        const result = await getWarehouseHistory(limit, { signal: actionSignal })
        setWarehouseHistory(result)
        return result
      }

      if (!trackLoading) {
        const dedupeKey = String(limit)
        const existing = silentHistoryRef.current.get(dedupeKey)
        if (existing) {
          return existing
        }

        const promise = (async () => {
          try {
            return await action(signal)
          } catch (err) {
            if (isCancelError(err) || signal?.aborted) {
              throw Object.assign(new Error('Request cancelled'), {
                error: 'REQUEST_CANCELLED',
              })
            }
            setError(toContextError(err))
            throw err
          } finally {
            if (silentHistoryRef.current.get(dedupeKey) === promise) {
              silentHistoryRef.current.delete(dedupeKey)
            }
          }
        })()

        silentHistoryRef.current.set(dedupeKey, promise)
        return promise
      }

      return runAction('history', action, {
        signal,
        cancelOthers: options.cancelOthers !== false,
      })
    },
    [runAction],
  )

  const value = useMemo(
    () => ({
      storedFilename,
      dataset,
      profile,
      analytics,
      quality,
      warehouseHistory,
      lastWarehouseLoad,
      loading,
      loadingAction,
      error,
      setStoredFilename,
      setDataset,
      setProfile,
      setAnalytics,
      setQuality,
      setWarehouseHistory,
      setLastWarehouseLoad,
      setLoading,
      setError,
      clearError,
      resetDataset,
      abortAction,
      uploadDataset,
      fetchProfile,
      fetchAnalytics,
      fetchQuality,
      loadWarehouse,
      fetchWarehouseHistory,
    }),
    [
      storedFilename,
      dataset,
      profile,
      analytics,
      quality,
      warehouseHistory,
      lastWarehouseLoad,
      loading,
      loadingAction,
      error,
      clearError,
      resetDataset,
      abortAction,
      uploadDataset,
      fetchProfile,
      fetchAnalytics,
      fetchQuality,
      loadWarehouse,
      fetchWarehouseHistory,
    ],
  )

  return (
    <DatasetContext.Provider value={value}>{children}</DatasetContext.Provider>
  )
}

export default DatasetProvider
