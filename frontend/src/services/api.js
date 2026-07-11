import axios from 'axios'

/**
 * Resolve the API base URL.
 * - If VITE_API_URL is set (non-empty), use it.
 * - In Vite dev with no override, use same-origin ("") so requests go through
 *   the Vite proxy and avoid CORS failures against localhost:8000.
 * - Otherwise fall back to http://localhost:8000.
 */
export function resolveApiBaseUrl() {
  const configured = import.meta.env.VITE_API_URL
  if (typeof configured === 'string' && configured.trim() !== '') {
    return configured.trim().replace(/\/$/, '')
  }
  if (import.meta.env.DEV) {
    return ''
  }
  return 'http://localhost:8000'
}

export const API_BASE_URL = resolveApiBaseUrl()

export const REQUEST_TIMEOUT_MS = 120_000
export const HEALTH_TIMEOUT_MS = 8_000

/**
 * Normalize FastAPI ErrorResponse and network failures into a consistent shape.
 * Backend format: { error, message, details?, request_id? }
 */
export function parseApiError(error) {
  if (!error) {
    return {
      message: 'An unexpected error occurred',
      error: 'UNKNOWN_ERROR',
      details: null,
      requestId: null,
      status: null,
    }
  }

  if (error.response) {
    const payload = error.response.data
    const status = error.response.status

    if (payload && typeof payload === 'object') {
      return {
        message:
          payload.message ||
          payload.detail ||
          payload.error ||
          `Request failed with status ${status}`,
        error: payload.error || 'HTTP_ERROR',
        details: Array.isArray(payload.details) ? payload.details : null,
        requestId:
          payload.request_id ||
          error.response.headers?.['x-request-id'] ||
          null,
        status,
      }
    }

    return {
      message:
        typeof payload === 'string' && payload.trim()
          ? payload
          : `Request failed with status ${status}`,
      error: 'HTTP_ERROR',
      details: null,
      requestId: error.response.headers?.['x-request-id'] || null,
      status,
    }
  }

  if (error.request) {
    return {
      message: 'Unable to reach the DataForge API. Check that the backend is running.',
      error: 'NETWORK_ERROR',
      details: null,
      requestId: null,
      status: null,
    }
  }

  return {
    message: error.message || 'An unexpected error occurred',
    error: 'CLIENT_ERROR',
    details: null,
    requestId: null,
    status: null,
  }
}

export class ApiError extends Error {
  constructor(parsed) {
    super(parsed.message)
    this.name = 'ApiError'
    this.error = parsed.error
    this.details = parsed.details
    this.requestId = parsed.requestId
    this.status = parsed.status
  }
}

function toApiError(error) {
  if (error instanceof ApiError) return error
  return new ApiError(parseApiError(error))
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(toApiError(error)),
)

export async function checkHealth() {
  const response = await apiClient.get('/health', {
    timeout: HEALTH_TIMEOUT_MS,
  })

  // Axios already treats non-2xx as errors. Also require the known payload.
  const data = response.data
  if (!data || typeof data !== 'object' || data.status !== 'healthy') {
    throw new ApiError({
      message: 'Health check returned an unexpected payload',
      error: 'HEALTHCHECK_FAILED',
      details: null,
      requestId: response.headers?.['x-request-id'] || null,
      status: response.status,
    })
  }

  return data
}

export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function profileDataset(storedFilename) {
  const response = await apiClient.post('/profile', {
    stored_filename: storedFilename,
  })
  return response.data
}

export async function analyzeDataset(storedFilename) {
  const response = await apiClient.post('/analytics', {
    stored_filename: storedFilename,
  })
  return response.data
}

export async function qualityCheck(storedFilename) {
  const response = await apiClient.post('/quality-check', {
    stored_filename: storedFilename,
  })
  return response.data
}

export async function loadToWarehouse(storedFilename) {
  const response = await apiClient.post('/warehouse/load', {
    stored_filename: storedFilename,
  })
  return response.data
}

export async function getWarehouseHistory(limit = 50) {
  const response = await apiClient.get('/warehouse/history', {
    params: { limit },
  })
  return response.data
}

export default apiClient
