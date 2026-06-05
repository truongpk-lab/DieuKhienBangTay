const DEFAULT_TIMEOUT_MS = 8000

export class ApiError extends Error {
  status?: number
  path: string

  constructor(message: string, path: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.path = path
    this.status = status
  }
}

export type ApiRequestOptions = RequestInit & {
  timeoutMs?: number
}

export type ApiFallbackResult<T> = {
  data: T
  fromFallback: boolean
  error?: ApiError
}

export function getApiBaseUrl() {
  return (import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')
}

export async function requestJson<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...fetchOptions } = options
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  const requestHeaders = new Headers(headers)
  if (fetchOptions.body !== undefined && !requestHeaders.has('Content-Type')) {
    requestHeaders.set('Content-Type', 'application/json')
  }

  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...fetchOptions,
      headers: requestHeaders,
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new ApiError(await getErrorMessage(response), path, response.status)
    }

    return (await response.json()) as T
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError(`Backend request timed out after ${timeoutMs}ms`, path)
    }
    throw new ApiError(error instanceof Error ? error.message : 'Backend request failed', path)
  } finally {
    window.clearTimeout(timeout)
  }
}

export async function withApiFallback<T>(
  request: () => Promise<T>,
  fallback: T,
): Promise<ApiFallbackResult<T>> {
  try {
    return { data: await request(), fromFallback: false }
  } catch (error) {
    return {
      data: fallback,
      fromFallback: true,
      error: error instanceof ApiError ? error : new ApiError('Backend request failed', 'unknown'),
    }
  }
}

async function getErrorMessage(response: Response) {
  const fallback = `Backend request failed: ${response.status}`
  const body = (await response
    .clone()
    .json()
    .catch(() => null)) as { detail?: unknown; message?: unknown } | null

  if (typeof body?.detail === 'string') {
    return body.detail
  }
  if (typeof body?.message === 'string') {
    return body.message
  }
  return fallback
}
