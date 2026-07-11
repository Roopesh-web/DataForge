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

function toContextError(err) {
  return {
    message: err.message || 'An unexpected error occurred',
    error: err.error || 'UNKNOWN_ERROR',
    details: err.details || null,
    requestId: err.requestId || null,
    status: err.status ?? null,
  }
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
  const inFlightRef = useRef(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const resetDataset = useCallback(() => {
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
    inFlightRef.current = null
  }, [])

  const runAction = useCallback(async (actionKey, action) => {
    if (inFlightRef.current) {
      const busyError = Object.assign(
        new Error('Another request is already in progress. Please wait.'),
        {
          error: 'REQUEST_IN_FLIGHT',
          details: null,
          requestId: null,
          status: null,
        },
      )
      setError(toContextError(busyError))
      throw busyError
    }

    inFlightRef.current = actionKey
    setLoading(true)
    setLoadingAction(actionKey)
    setError(null)

    try {
      return await action()
    } catch (err) {
      setError(toContextError(err))
      throw err
    } finally {
      inFlightRef.current = null
      setLoading(false)
      setLoadingAction(null)
    }
  }, [])

  const uploadDataset = useCallback(
    async (file, options = {}) => {
      return runAction('upload', async () => {
        const result = await uploadFile(file, options)
        setDataset(result)
        setStoredFilename(result.stored_filename)
        setProfile(null)
        setAnalytics(null)
        setQuality(null)
        return result
      })
    },
    [runAction],
  )

  const fetchProfile = useCallback(
    async (filename = storedFilename) => {
      if (!filename) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction('profile', async () => {
        const result = await profileDataset(filename)
        setProfile(result)
        return result
      })
    },
    [runAction, storedFilename],
  )

  const fetchAnalytics = useCallback(
    async (filename = storedFilename) => {
      if (!filename) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction('analytics', async () => {
        const result = await analyzeDataset(filename)
        setAnalytics(result)
        return result
      })
    },
    [runAction, storedFilename],
  )

  const fetchQuality = useCallback(
    async (filename = storedFilename) => {
      if (!filename) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction('quality', async () => {
        const result = await qualityCheck(filename)
        setQuality(result)
        return result
      })
    },
    [runAction, storedFilename],
  )

  const loadWarehouse = useCallback(
    async (filename = storedFilename) => {
      if (!filename) {
        throw Object.assign(new Error('No dataset selected. Upload a file first.'), {
          error: 'NO_DATASET',
        })
      }
      return runAction('warehouse', async () => {
        const result = await loadToWarehouse(filename)
        setLastWarehouseLoad(result)
        const history = await getWarehouseHistory(50)
        setWarehouseHistory(history)
        return result
      })
    },
    [runAction, storedFilename],
  )

  const fetchWarehouseHistory = useCallback(
    async (limit = 50, options = {}) => {
      const trackLoading = options.trackLoading !== false

      const action = async () => {
        const result = await getWarehouseHistory(limit)
        setWarehouseHistory(result)
        return result
      }

      if (!trackLoading) {
        try {
          return await action()
        } catch (err) {
          setError(toContextError(err))
          throw err
        }
      }

      return runAction('history', action)
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
