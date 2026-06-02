import { ApiAbortError, ApiNetworkError, ApiResponseError, ApiTimeoutError } from '@/shared/api/errors'

export interface HttpClientOptions {
  baseUrl: string
  timeoutMs: number
  defaultHeaders?: HeadersInit
}

export interface RequestOptions extends Omit<RequestInit, 'body' | 'headers'> {
  headers?: HeadersInit
  body?: unknown
  timeoutMs?: number
}

function mergeHeaders(...headersList: Array<HeadersInit | undefined>): Headers {
  const headers = new Headers()
  for (const headersInit of headersList) {
    if (!headersInit) {
      continue
    }

    new Headers(headersInit).forEach((value, key) => {
      headers.set(key, value)
    })
  }
  return headers
}

function buildAbortController(timeoutMs: number, externalSignal?: AbortSignal) {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs)

  if (externalSignal) {
    if (externalSignal.aborted) {
      controller.abort(externalSignal.reason)
    } else {
      const abortHandler = () => controller.abort(externalSignal.reason)
      externalSignal.addEventListener('abort', abortHandler, { once: true })
      controller.signal.addEventListener(
        'abort',
        () => externalSignal.removeEventListener('abort', abortHandler),
        { once: true },
      )
    }
  }

  return {
    controller,
    timeoutId,
  }
}

export class HttpClient {
  private readonly baseUrl: string
  private readonly timeoutMs: number
  private readonly defaultHeaders?: HeadersInit

  constructor(options: HttpClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, '')
    this.timeoutMs = options.timeoutMs
    this.defaultHeaders = options.defaultHeaders
  }

  async request<TResponse>(path: string, options: RequestOptions = {}): Promise<TResponse> {
    const url = new URL(path.replace(/^\//, ''), `${this.baseUrl}/`)
    const timeoutMs = options.timeoutMs ?? this.timeoutMs
    const { controller, timeoutId } = buildAbortController(timeoutMs, options.signal)

    try {
      const headers = mergeHeaders(this.defaultHeaders, options.headers)
      if (options.body !== undefined && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json')
      }
      if (!headers.has('Accept')) {
        headers.set('Accept', 'application/json')
      }

      const response = await fetch(url, {
        ...options,
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: controller.signal,
      })

      const contentType = response.headers.get('content-type') ?? ''
      const hasJson = contentType.includes('application/json')
      const parsedBody = hasJson ? await response.json().catch(() => undefined) : await response.text()

      if (!response.ok) {
        throw new ApiResponseError(
          `Request failed with status ${response.status}`,
          response.status,
          parsedBody,
        )
      }

      return parsedBody as TResponse
    } catch (error) {
      if (error instanceof ApiAbortError || error instanceof ApiTimeoutError || error instanceof ApiNetworkError) {
        throw error
      }

      if (error instanceof DOMException && error.name === 'AbortError') {
        if (controller.signal.reason != null) {
          throw new ApiAbortError('The request was aborted', controller.signal.reason)
        }

        throw new ApiTimeoutError(`The request timed out after ${timeoutMs}ms`)
      }

      if (error instanceof TypeError) {
        throw new ApiNetworkError('Unable to reach the orchestrator API', error)
      }

      throw error
    } finally {
      window.clearTimeout(timeoutId)
    }
  }

  get<TResponse>(path: string, options: Omit<RequestOptions, 'body' | 'method'> = {}) {
    return this.request<TResponse>(path, { ...options, method: 'GET' })
  }

  post<TResponse>(path: string, body?: unknown, options: Omit<RequestOptions, 'body'> = {}) {
    return this.request<TResponse>(path, { ...options, body, method: 'POST' })
  }
}
