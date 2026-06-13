import { appConfig } from '@/config/env';

import { ApiError } from './errors';

export type RequestBody = BodyInit | Record<string, unknown> | Array<Record<string, unknown>> | null;

export type RequestOptions = Omit<RequestInit, 'body' | 'headers' | 'method'> & {
  body?: RequestBody;
  headers?: HeadersInit;
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  timeoutMs?: number;
};

type JsonResponse = Record<string, unknown> | Array<unknown> | string | number | boolean | null;

const isJsonBody = (body: RequestBody): body is Record<string, unknown> | Array<Record<string, unknown>> =>
  body !== null && typeof body === 'object' && !(body instanceof FormData) && !(body instanceof Blob);

export class ApiClient {
  constructor(
    private readonly baseUrl: string,
    private readonly defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  ) {}

  async request<TResponse>(path: string, options: RequestOptions = {}): Promise<TResponse> {
    const requestUrl = new URL(path.replace(/^\//, ''), this.baseUrl.endsWith('/') ? this.baseUrl : `${this.baseUrl}/`);
    const controller = new AbortController();
    const timeoutMs = options.timeoutMs ?? appConfig.requestTimeoutMs;
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

    const headers = new Headers(this.defaultHeaders);
    new Headers(options.headers ?? {}).forEach((value, key) => headers.set(key, value));

    try {
      const response = await fetch(requestUrl, {
        ...options,
        headers,
        signal: options.signal ?? controller.signal,
        body: this.serializeBody(options.body),
        method: options.method ?? 'GET',
      });

      if (!response.ok) {
        throw await this.buildError(response);
      }

      return (await this.parseResponse<TResponse>(response)) as TResponse;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      throw error;
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  private serializeBody(body: RequestBody): BodyInit | undefined {
    if (body === null || body === undefined) {
      return undefined;
    }

    if (typeof body === 'string' || body instanceof FormData || body instanceof Blob || body instanceof URLSearchParams) {
      return body;
    }

    if (isJsonBody(body)) {
      return JSON.stringify(body);
    }

    return undefined;
  }

  private async parseResponse<TResponse>(response: Response): Promise<TResponse> {
    if (response.status === 204) {
      return undefined as TResponse;
    }

    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('application/json')) {
      return (await response.json()) as TResponse;
    }

    return (await response.text()) as TResponse;
  }

  private async buildError(response: Response): Promise<ApiError> {
    const contentType = response.headers.get('content-type') ?? '';
    let details: JsonResponse | string | undefined;

    if (contentType.includes('application/json')) {
      details = (await response.json()) as JsonResponse;
    } else {
      details = await response.text();
    }

    const message = response.status >= 500 ? 'The upstream service failed.' : 'The request could not be completed.';
    return new ApiError(message, {
      kind: response.status >= 500 ? 'upstream' : 'validation',
      status: response.status,
      details,
      retriable: response.status >= 500 || response.status === 429,
    });
  }
}

export function createApiClient(): ApiClient {
  return new ApiClient(appConfig.apiBaseUrl);
}
