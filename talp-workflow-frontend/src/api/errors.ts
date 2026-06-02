export type ApiErrorKind = 'validation' | 'network' | 'timeout' | 'upstream' | 'unexpected';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly code?: string;
  readonly details?: unknown;
  readonly retriable: boolean;

  constructor(
    message: string,
    options: {
      kind: ApiErrorKind;
      status?: number;
      code?: string;
      details?: unknown;
      retriable?: boolean;
    },
  ) {
    super(message);
    this.name = 'ApiError';
    this.kind = options.kind;
    this.status = options.status;
    this.code = options.code;
    this.details = options.details;
    this.retriable = options.retriable ?? false;
  }
}

export const normalizeApiError = (error: unknown): ApiError => {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof DOMException && error.name === 'AbortError') {
    return new ApiError('The request timed out.', {
      kind: 'timeout',
      retriable: true,
    });
  }

  if (error instanceof TypeError) {
    return new ApiError(error.message || 'Network request failed.', {
      kind: 'network',
      retriable: true,
    });
  }

  if (error instanceof Error) {
    return new ApiError(error.message, { kind: 'unexpected' });
  }

  return new ApiError('An unknown error occurred.', { kind: 'unexpected' });
};
