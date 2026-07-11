import axios from 'axios'

/**
 * Resolve the API base URL.
 *
 * Priority:
 * 1. `VITE_API_URL` when set (required for typical production deploys to a separate API host)
 * 2. Empty string (same-origin) — Vite proxy in development, or reverse-proxy in production
 *
 * Never hardcode a production API host. Set `VITE_API_URL` at build time for deployed backends.
 */
export function resolveApiBaseUrl() {
  const configured = import.meta.env.VITE_API_URL
  if (typeof configured === 'string' && configured.trim() !== '') {
    return configured.trim().replace(/\/$/, '')
  }
  return ''
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

  if (
    axios.isCancel?.(error) ||
    error.code === 'ERR_CANCELED' ||
    error.name === 'CanceledError' ||
    error.name === 'AbortError'
  ) {
    return {
      message: 'Request cancelled',
      error: 'REQUEST_CANCELLED',
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
    const isTimeout =
      error.code === 'ECONNABORTED' ||
      error.code === 'ETIMEDOUT' ||
      /timeout/i.test(error.message || '')

    if (isTimeout) {
      return {
        message:
          'The request timed out. The API may be busy or the dataset is large — please retry.',
        error: 'TIMEOUT_ERROR',
        details: null,
        requestId: null,
        status: null,
      }
    }

    return {
      message: 'Unable to reach the DataForge API. Check that the backend is running.',
      error: 'NETWORK_ERROR',
      details: null,
      requestId: null,
      status: null,
    }
  }

  if (
    error.code === 'ECONNABORTED' ||
    error.code === 'ETIMEDOUT' ||
    /timeout/i.test(error.message || '')
  ) {
    return {
      message:
        'The request timed out. The API may be busy or the dataset is large — please retry.',
      error: 'TIMEOUT_ERROR',
      details: null,
      requestId: null,
      status: null,
    }
  }

  return {
    message: error.message || 'An unexpected error occurred',
    error: error.error || 'CLIENT_ERROR',
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

/**
 * Reads title/version from the existing FastAPI OpenAPI document.
 * Used only for read-only Settings display — does not change API behavior.
 */
export async function fetchOpenApiInfo() {
  const response = await apiClient.get('/openapi.json', {
    timeout: HEALTH_TIMEOUT_MS,
  })
  const info = response.data?.info
  if (!info || typeof info !== 'object') {
    return { title: null, version: null, description: null }
  }
  return {
    title: typeof info.title === 'string' ? info.title : null,
    version: typeof info.version === 'string' ? info.version : null,
    description: typeof info.description === 'string' ? info.description : null,
  }
}

export async function uploadFile(file, { onUploadProgress, signal } = {}) {
  const formData = new FormData()
  formData.append('file', file)

  // Let the browser set multipart Content-Type with boundary.
  const response = await apiClient.post('/upload', formData, {
    onUploadProgress,
    signal,
  })
  return response.data
}

export async function profileDataset(storedFilename, { signal } = {}) {
  const response = await apiClient.post(
    '/profile',
    {
      stored_filename: storedFilename,
    },
    { signal },
  )
  return response.data
}

export async function analyzeDataset(storedFilename, { signal } = {}) {
  const response = await apiClient.post(
    '/analytics',
    {
      stored_filename: storedFilename,
    },
    { signal },
  )
  return response.data
}

export async function qualityCheck(storedFilename, { signal } = {}) {
  const response = await apiClient.post(
    '/quality-check',
    {
      stored_filename: storedFilename,
    },
    { signal },
  )
  return response.data
}

export async function loadToWarehouse(storedFilename, { signal } = {}) {
  const response = await apiClient.post(
    '/warehouse/load',
    {
      stored_filename: storedFilename,
    },
    { signal },
  )
  return response.data
}

export async function getWarehouseHistory(limit = 50, { signal } = {}) {
  const response = await apiClient.get('/warehouse/history', {
    params: { limit },
    signal,
  })
  return response.data
}

export default apiClient
