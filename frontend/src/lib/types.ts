// Types partagés, alignés sur measurement-object.schema.json et les schémas
// Pydantic du backend (backend/app/schemas.py). Volontairement permissifs
// sur les champs profonds qu'on ne fait que ré-afficher tels quels.

export type Confidence = "H" | "M" | "L" | string;

export interface TaxonomyValue {
  code: string;
  label: string;
  [key: string]: unknown;
}

export interface TaxonomyContent {
  meta: { version: string; [key: string]: unknown };
  classification_axes: {
    area_of_opportunity: { values: TaxonomyValue[]; [key: string]: unknown };
    programme: { values: TaxonomyValue[]; [key: string]: unknown };
    sdg: { [key: string]: unknown };
  };
  rise_pillars: { values: TaxonomyValue[]; [key: string]: unknown };
  measurement_layer: {
    target_group?: { values: TaxonomyValue[] };
    [key: string]: unknown;
  };
  [key: string]: unknown;
}

// Réponse réelle de POST /submissions, /retry (response_model=SubmissionOut,
// backend/app/schemas.py) : volontairement minimale, deux champs seulement.
export interface SubmissionOut {
  submission_id: string;
  pipeline_status:
    | "received"
    | "extracted"
    | "awaiting_confirmation"
    | "confirmed"
    | "failed";
}

// Réponse de GET /submissions/{id} (response_model=SubmissionDetail).
export interface SubmissionDetail {
  submission_id: string;
  pipeline_status: SubmissionOut["pipeline_status"];
  pipeline_error: string | null;
  raw_text: string;
}

export interface ExtractionCandidate {
  candidate_id: string;
  quote: string;
  span: { start: number; end: number };
  metric_label_source: string;
  value: number | null;
  value_qualifier: string | null;
  definition_text: string | null;
  confidence: Confidence;
}

export interface ExtractionPayload {
  language: string;
  project: {
    name: { value: string | null; origin: string; quote: string | null };
    period: {
      start: string | null;
      end: string | null;
      reporting_year: number | null;
      quote: string | null;
    };
  };
  candidates: ExtractionCandidate[];
}

export interface CandidateMapping {
  candidate_id: string;
  metric_code: string;
  iaooi_value: "INPUT" | "ACTIVITY" | "OUTPUT" | "OUTCOME" | "IMPACT_CLAIM" | "CONTEXT" | "UNCERTAIN" | string;
  confidence: Confidence;
  unit_code: string;
  unit_dimension: string;
  count_type: string;
  internal_external: string;
  dedup_basis: string;
  target_group: string[];
  source_wording_class: string;
}

export interface MappingRelation {
  relation_type: string;
  candidate_id_a: string;
  candidate_id_b: string;
}

export interface MappingPayload {
  project_classification: {
    area_of_opportunity: { code: string; confidence: Confidence }[];
    programme: { code: string; confidence: Confidence }[];
    rise_pillars: (string | { code: string; confidence: Confidence })[];
    sdgs: { goal: number; role: "primary" | "secondary"; confidence: Confidence }[];
    activity_type: string[];
  };
  candidate_mappings: CandidateMapping[];
  relations: MappingRelation[];
}

export interface SubmissionDraft {
  submission_id: string;
  pipeline_status: SubmissionOut["pipeline_status"];
  pipeline_error: string | null;
  candidates: {
    stage: "structured" | "standardized";
    payload: ExtractionPayload | MappingPayload;
    validation_errors: string[] | null;
  }[];
}

export interface ConfirmSdgInput {
  goal: number;
  role: "primary" | "secondary";
}

export interface ConfirmAxesInput {
  area_of_opportunity: string[];
  programme: string[];
  rise_pillars: string[];
  sdgs: ConfirmSdgInput[];
}

export interface ConfirmProjectInput {
  name: string | null;
  reporting_year: number;
  period_start: string | null;
  period_end: string | null;
  outcome_status: "measured" | "pending_follow_up" | "none";
  expected_outcome?: string | null;
  follow_up_date?: string | null;
}

export interface ConfirmCandidateInput {
  candidate_id: string;
  include: boolean;
  value?: number | null;
  count_type?: string | null;
  internal_external?: string | null;
  corrected?: boolean;
}

export interface ConfirmRequestBody {
  project: ConfirmProjectInput;
  axes: ConfirmAxesInput;
  confirmations: { C1: boolean; C2: boolean; C3: boolean; C4: boolean };
  candidates: ConfirmCandidateInput[];
  confirmed_by: string;
}

export interface ConfirmResult {
  project_id: string;
  measurement_ids: string[];
}

export interface ConfirmErrorItem {
  candidate_id?: string;
  message: string;
}

export interface MeasurementObject {
  measurement_id: string;
  metric_code: string;
  metric_label_source: string;
  definition: { status: string; text: string; layer?: string };
  iaooi_class: { value: string; confidence?: Confidence };
  value: number | null;
  value_status: string;
  value_qualifier: string | null;
  unit: { code: string; dimension?: string };
  subject: { type: string; id: string; name?: string };
  population: {
    internal_external: string;
    count_type: string;
    dedup_basis: string;
    target_group: string[];
  };
  period: { type: string; start: string | null; end: string | null; reporting_year: number | null };
  layer: string;
  source?: {
    origin: string;
    document_id?: string;
    quote?: string;
    span?: { start: number; end: number };
    submitted_at?: string;
    language?: string;
  };
  verification_status: string;
  aggregation: {
    aggregable: boolean;
    equivalence_key: string | null;
    refusal_reason: string | null;
    dedup_key?: string | null;
  };
  derivation?: { step: string; rule_id?: string; agent?: string; confidence?: Confidence }[];
  flag?: { reason: string; by: string; at: string } | null;
  [key: string]: unknown;
}

export interface Refusal {
  refusal_id?: string;
  aggregate_run_id?: string;
  reason: string;
  measurement_ids: string[];
  detail?: string;
  explanation_fr: string;
}

export interface Aggregate {
  measurement_id: string;
  metric_code: string;
  metric_label_source?: string;
  value: number | null;
  value_status: string;
  value_qualifier?: string | null;
  formula?: string;
  inputs: string[];
  unit: { code: string };
  subject: { type: string; id: string; name?: string };
  population?: { internal_external?: string; count_type?: string; dedup_basis?: string };
  iaooi_class?: { value: string };
  [key: string]: unknown;
}

export interface DashboardResponse {
  view: string;
  scope_organization_id: string | null;
  group_by: string;
  filters: Record<string, unknown>;
  computed_at: string;
  engine_version: string;
  aggregates: Aggregate[];
  refusals: Refusal[];
  stale: boolean;
  official_jci_facts?: unknown[];
  quality_issues?: QualityIssue[];
}

export interface QualityIssue {
  issue_id: string;
  kind: string;
  subject: string;
  values: {
    label: string;
    value: number;
    value_qualifier?: string;
    unit?: string;
    layer: string;
    formula?: string;
    source?: { document?: string; page?: string; section?: string; quote?: string };
  }[];
  resolution_status: string;
}

export interface TraceResponse {
  measurement_id: string;
  chain_complete: boolean;
  entries: TraceEntry[];
}

export interface TraceEntry {
  measurement_id: string;
  resolved: boolean;
  kind?: "aggregate" | "leaf";
  measurement?: MeasurementObject;
  parent_measurement_ids?: string[];
  submission?: {
    submission_id: string;
    raw_text: string;
    quote: string | null;
    quote_found_in_raw_text: boolean;
    highlight_span: { start: number; end: number } | null;
  } | null;
  ctl_raw_ok?: boolean | null;
  note?: string;
}

export interface CheckPairResult {
  compatible: boolean;
  refusal?: Refusal;
}

export interface ApiErrorBody {
  detail?: string | { errors?: ConfirmErrorItem[]; [key: string]: unknown } | unknown;
}
