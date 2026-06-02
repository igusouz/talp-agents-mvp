export class ApiError extends Error {
  readonly name = 'ApiError'

  constructor(
    message: string,
    public readonly status?: number,
    public readonly details?: unknown,
  ) {
    super(message)
  }
}

export class ApiTimeoutError extends ApiError {
  readonly name = 'ApiTimeoutError'

  constructor(message = 'The request timed out', details?: unknown) {
    super(message, undefined, details)
  }
}

export class ApiNetworkError extends ApiError {
  readonly name = 'ApiNetworkError'

  constructor(message = 'A network error occurred', details?: unknown) {
    super(message, undefined, details)
  }
}

export class ApiAbortError extends ApiError {
  readonly name = 'ApiAbortError'

  constructor(message = 'The request was aborted', details?: unknown) {
    super(message, undefined, details)
  }
}

export class ApiResponseError extends ApiError {
  readonly name = 'ApiResponseError'

  constructor(message: string, status: number, details?: unknown) {
    super(message, status, details)
  }
}
