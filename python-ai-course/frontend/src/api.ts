const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8765';

export type AttendanceRecord = {
  date: string;
  time: string;
  user_id: string;
  name: string;
  status: string;
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
  } | null;
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
  user_counts: Record<string, number>;
};

async function requestJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.message ?? `API request failed: ${response.status}`);
  }
  return payload as T;
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

export function fetchStats() {
  return requestJson<StatsResponse>("/api/stats");
}

export function fetchUsers() {
  return requestJson<{ users: RegisteredUser[] }>("/api/users");
}
