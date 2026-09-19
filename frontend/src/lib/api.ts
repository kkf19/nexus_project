import { API_BASE_URL } from "./config";
import type {
  ApiErrorBody,
  CheckPairResult,
  ConfirmRequestBody,
  ConfirmResult,
  DashboardResponse,
  SubmissionDetail,
  SubmissionDraft,
  SubmissionOut,
  TaxonomyContent,
  TraceResponse,
} from "./types";

export class ApiError extends Error {
  status: number;
  body: ApiErrorBody | null;

  constructor(status: number, body: ApiErrorBody | null, message: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

/** Message générique à afficher à l'écran ; jamais le détail technique. */
export function friendlyErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (typeof err.body?.detail === "string") return err.body.detail;
    return "Une erreur est survenue. Merci de réessayer dans un instant.";
  }
  return "Impossible de joindre le serveur. Vérifiez votre connexion et réessayez.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
    });
  } catch {
    throw new ApiError(0, null, "network error");
  }

  if (!res.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = await res.json();
    } catch {
      // corps non-JSON : on garde body = null
    }
    throw new ApiError(res.status, body, `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export function createSubmission(params: {
  organization_id: string;
  user_id: string;
  raw_text: string;
}): Promise<SubmissionOut> {
  return request<SubmissionOut>("/submissions", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function getSubmission(id: string): Promise<SubmissionDetail> {
  return request<SubmissionDetail>(`/submissions/${id}`);
}

export function getSubmissionDraft(id: string): Promise<SubmissionDraft> {
  return request<SubmissionDraft>(`/submissions/${id}/draft`);
}

export function retrySubmission(id: string): Promise<SubmissionOut> {
  return request<SubmissionOut>(`/submissions/${id}/retry`, { method: "POST" });
}

export function confirmSubmission(id: string, body: ConfirmRequestBody): Promise<ConfirmResult> {
  return request<ConfirmResult>(`/submissions/${id}/confirm`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function getTaxonomy(): Promise<{ version: string; content: TaxonomyContent }> {
  return request(`/taxonomy`);
}

export function getDashboard(
  view: "ol" | "national" | "global",
  params: {
    scope_organization_id?: string;
    group_by?: string;
    reporting_year?: number;
    area_of_opportunity?: string;
    programme?: string;
    sdg?: number;
  } = {}
): Promise<DashboardResponse> {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
  });
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  return request<DashboardResponse>(`/dashboards/${view}${suffix}`);
}

export function getTrace(measurementId: string): Promise<TraceResponse> {
  return request<TraceResponse>(`/trace/${measurementId}`);
}

export function checkPair(a: string, b: string): Promise<CheckPairResult> {
  return request<CheckPairResult>(`/aggregations/check-pair`, {
    method: "POST",
    body: JSON.stringify({ measurement_id_a: a, measurement_id_b: b }),
  });
}

export function reviewMeasurement(
  id: string,
  action: "validate" | "flag" | "unflag",
  reason: string | undefined,
  reviewedBy: string
) {
  return request(`/measurements/${id}/review`, {
    method: "POST",
    body: JSON.stringify({ action, reason, reviewed_by: reviewedBy }),
  });
}

export function getMeasurement(id: string) {
  return request(`/measurements/${id}`);
}

export function getProject(id: string) {
  return request(`/projects/${id}`);
}
