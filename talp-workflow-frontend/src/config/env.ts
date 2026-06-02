const readString = (value: string | undefined, fallback: string): string => {
  const trimmed = value?.trim();
  return trimmed && trimmed.length > 0 ? trimmed : fallback;
};

const readNumber = (value: string | undefined, fallback: number): number => {
  if (value === undefined || value.trim() === '') {
    return fallback;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
};

const readBoolean = (value: string | undefined, fallback: boolean): boolean => {
  if (value === undefined) {
    return fallback;
  }

  return ['1', 'true', 'yes', 'on'].includes(value.trim().toLowerCase());
};

export const appConfig = {
  appName: readString(import.meta.env.VITE_APP_NAME, 'TALP Workflow Frontend'),
  appVersion: readString(import.meta.env.VITE_APP_VERSION, '0.1.0'),
  apiBaseUrl: readString(
    import.meta.env.VITE_ORCHESTRATOR_API_BASE_URL,
    'http://localhost:8000/api/v1',
  ),
  requestTimeoutMs: readNumber(import.meta.env.VITE_REQUEST_TIMEOUT_MS, 30000),
  enableMocks: readBoolean(import.meta.env.VITE_ENABLE_MOCKS, false),
} as const;
