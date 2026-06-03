const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8765';

type JsonObject = Record<string, unknown>;

function isJsonObject(value: unknown): value is JsonObject {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function toNumber(value: unknown, fallback = 0) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : fallback;
}

function toStringValue(value: unknown) {
  return value === undefined || value === null ? '' : String(value);
}

function numberMap(value: unknown): Record<string, number> {
  if (!isJsonObject(value)) return {};

  return Object.fromEntries(
    Object.entries(value)
      .map(([key, rawValue]) => [key, toNumber(rawValue)] as const)
      .filter(([, numberValue]) => Number.isFinite(numberValue)),
  );
}

export class ApiError extends Error {
  readonly statusCode: number;
  readonly apiStatus?: string;

  constructor(
    message: string,
    statusCode: number,
    apiStatus?: string,
  ) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.apiStatus = apiStatus;
  }
}

function isNotFoundApiError(error: unknown) {
  return error instanceof ApiError && (error.statusCode === 404 || error.apiStatus === 'not_found');
}

export type AttendanceRecord = {
  date: string;
  time: string;
  user_id: string;
  name: string;
  status: string;
  confidence?: string;
  event_id?: string;
};

export type RecognitionEvent = {
  event_id: string;
  timestamp: string;
  event_type: string;
  user_id: string;
  name: string;
  confidence: string;
  face_count: string;
  message: string;
};

export type RegisteredUser = {
  label: number;
  user_id: string;
  name: string;
  sample_exists: boolean;
};

export type RecognitionResponse = {
  status: 'success' | 'duplicate' | 'recognized' | 'no_face' | 'no_model' | 'unknown' | 'error';
  face_count: number;
  primary_match: {
    matched: boolean;
    name: string;
    user_id: string;
    confidence?: number;
    attendance?: AttendanceRecord;
    event?: RecognitionEvent;
  } | null;
  event?: RecognitionEvent | null;
  matches: Array<{
    matched: boolean;
    name: string;
    user_id: string;
    confidence?: number;
    attendance?: AttendanceRecord;
  }>;
};

export type StatsResponse = {
  total_records: number;
  status_counts: Record<string, number>;
  valid_status_counts: Record<string, number>;
  event_total: number;
  event_counts: Record<string, number>;
  user_counts: Record<string, number>;
  registered_user_count: number;
  attendance_rate: number;
  recognition_success_rate: number;
};

async function requestJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
  });

  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message = isJsonObject(payload) && typeof payload.message === 'string'
      ? payload.message
      : `API request failed: ${response.status}`;
    const apiStatus = isJsonObject(payload) && typeof payload.status === 'string' ? payload.status : undefined;
    throw new ApiError(message, response.status, apiStatus);
  }
  return payload as T;
}

function normalizeRecognitionEvent(value: unknown, index: number): RecognitionEvent {
  const event = isJsonObject(value) ? value : {};
  const timestamp = toStringValue(event.timestamp);

  return {
    event_id: toStringValue(event.event_id) || `legacy-event-${index}`,
    timestamp,
    event_type: toStringValue(event.event_type),
    user_id: toStringValue(event.user_id),
    name: toStringValue(event.name),
    confidence: toStringValue(event.confidence),
    face_count: toStringValue(event.face_count),
    message: toStringValue(event.message),
  };
}

function normalizeStats(payload: Partial<StatsResponse> | null | undefined): StatsResponse {
  return {
    total_records: toNumber(payload?.total_records),
    status_counts: numberMap(payload?.status_counts),
    valid_status_counts: numberMap(payload?.valid_status_counts),
    event_total: toNumber(payload?.event_total),
    event_counts: numberMap(payload?.event_counts),
    user_counts: numberMap(payload?.user_counts),
    registered_user_count: toNumber(payload?.registered_user_count),
    attendance_rate: toNumber(payload?.attendance_rate),
    recognition_success_rate: toNumber(payload?.recognition_success_rate),
  };
}

export function registerFace(userId: string, name: string, imageData: string) {
  return requestJson<{ status: string; message: string }>("/api/register", {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, name, image_data: imageData }),
  });
}

export function recognizeFrame(imageData: string, markAttendance = true) {
  return requestJson<RecognitionResponse>("/api/recognize", {
    method: 'POST',
    body: JSON.stringify({ image_data: imageData, mark_attendance: markAttendance }),
  });
}

export function fetchRecords() {
  return requestJson<{ records: AttendanceRecord[] }>("/api/records");
}

export async function fetchEvents() {
  try {
    const response = await requestJson<{ events?: unknown[] }>("/api/events");
    const events = Array.isArray(response.events)
      ? response.events.map((event, index) => normalizeRecognitionEvent(event, index))
      : [];
    return { events, unavailable: false };
  } catch (error) {
    if (isNotFoundApiError(error)) {
      return { events: [], unavailable: true };
    }
    throw error;
  }
}

export async function fetchStats() {
  const response = await requestJson<Partial<StatsResponse>>("/api/stats");
  return normalizeStats(response);
}

export function fetchUsers() {
  return requestJson<{ users: RegisteredUser[] }>("/api/users");
}
