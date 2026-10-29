const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> | undefined),
  };
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, typeof detail === "string" ? detail : "Request failed");
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return (await res.text()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
};

export type User = {
  id: number;
  username: string;
  full_name: string;
  role: "admin" | "staff";
  is_active: boolean;
};

export type Patient = {
  id: number;
  patient_code: string;
  full_name: string;
  date_of_birth: string | null;
  age_years: number | null;
  sex: string;
  phone: string;
  address: string;
  external_id: string;
};

export type Doctor = {
  id: number;
  full_name: string;
  specialty: string;
  phone: string;
  email: string;
  is_active: boolean;
};

export type TestParameter = {
  id: number;
  code: string;
  name: string;
  unit: string;
  reference_text: string;
  reference_min: number | null;
  reference_max: number | null;
  sort_order: number;
};

export type TestDefinition = {
  id: number;
  code: string;
  name: string;
  sample_type: string;
  description: string;
  price: number | null;
  is_active: boolean;
  parameters: TestParameter[];
};

export type ResultValue = {
  id: number;
  test_parameter_id: number;
  value_text: string;
  value_numeric: number | null;
  flag: string;
  parameter?: TestParameter;
};

export type OrderTest = {
  id: number;
  test_definition_id: number;
  test_definition?: TestDefinition;
  results: ResultValue[];
};

export type Order = {
  id: number;
  order_number: string;
  patient_id: number;
  doctor_id: number | null;
  status: "registered" | "in_progress" | "completed";
  notes: string;
  ordered_at: string;
  completed_at: string | null;
  patient?: Patient;
  doctor?: Doctor | null;
  order_tests: OrderTest[];
};

export type ClinicSettings = {
  clinic_name: string;
  address: string;
  phone: string;
  footer: string;
  logo_url: string;
};
