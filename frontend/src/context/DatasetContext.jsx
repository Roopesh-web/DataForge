import { useCallback, useMemo, useState } from 'react'
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
  loading: false,
  error: null,
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
  const [loading, setLoading] = useState(initialState.loading)
  const [error, setError] = useState(initialState.error)

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
    setLoading(initialState.loading)
    setError(initialState.error)
  }, [])

  const runAction = useCallback(async (action) => {
    setLoading(true)
    setError(null)
    try {
      return await action()
    } catch (err) {
      setError({
        message: err.message || 'An unexpected error occurred',
        error: err.error || 'UNKNOWN_ERROR',
        details: err.details || null,
        requestId: err.requestId || null,
        status: err.status ?? null,
      })
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const uploadDataset = useCallback(
    async (file) => {
      return runAction(async () => {
        const result = await uploadFile(file)
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
        throw new Error('No dataset selected. Upload a file first.')
      }
      return runAction(async () => {
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
        throw new Error('No dataset selected. Upload a file first.')
      }
      return runAction(async () => {
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
        throw new Error('No dataset selected. Upload a file first.')
      }
      return runAction(async () => {
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
        throw new Error('No dataset selected. Upload a file first.')
      }
      return runAction(async () => {
        const result = await loadToWarehouse(filename)
        return result
      })
    },
    [runAction, storedFilename],
  )

  const fetchWarehouseHistory = useCallback(
    async (limit = 50) => {
      return runAction(async () => {
        const result = await getWarehouseHistory(limit)
        setWarehouseHistory(result)
        return result
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
      loading,
      error,
      setStoredFilename,
      setDataset,
      setProfile,
      setAnalytics,
      setQuality,
      setWarehouseHistory,
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
      loading,
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
