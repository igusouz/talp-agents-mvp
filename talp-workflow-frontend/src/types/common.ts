export type UUID = string;
export type ISODateString = string;
export type JsonObject = Record<string, unknown>;

export type AsyncStatus = 'idle' | 'loading' | 'success' | 'error';

export interface ApiEnvelope<T> {
  data: T;
  requestId?: string;
  correlationId?: string;
}
