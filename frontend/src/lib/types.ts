// Types partagés, alignés sur measurement-object.schema.json et les schémas
// Pydantic du backend (backend/app/schemas.py). Volontairement permissifs
// sur les champs profonds qu'on ne fait que ré-afficher tels quels.
//
// A6 (impact-science.md) : ces types suivent la nouvelle forme du pipeline
// (A4) et de la confirmation (A5) -- famille d'activité en 1ère dimension,
// Areas avec un rôle primary/secondary, RISE en objet {status, pillars},
// ODD avec justification obligatoire. L'axe "programme" est retiré des
// échanges frontend/backend (deprecated, D-23).

export type Confidence = "H" | "M" | "L" | string;

export interface TaxonomyValue {
  code: string;
  label: string;
  [key: string]: unknown;
}

export interface TaxonomyContent {
  meta: { version: string; [key: string]: unknown };
  classification_axes: {
    activity_family: { values: TaxonomyValue[]; [key: string]: unknown };
    area_of_opportunity: { values: TaxonomyValue[]; [key: string]: unknown };
    programme: { values: TaxonomyValue[]; status?: string; [key: string]: unknown };
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

// {value, origin, quote} -- forme partagée par project.name, .jci_volunteers_count
// et .activity_duration_hours (ai_pipeline.py, A4).
export interface ValueOriginQuote<T> {
  value: T | null;
  origin: "inferred" | "quoted";
  quote: string | null;
}

export interface ExtractionPayload {
  language: string;
  project: {
    name: ValueOriginQuote<string>;
    period: {
      start: string | null;
      end: string | null;
      reporting_year: number | null;
      quote: string | null;
    };
    jci_volunteers_count: ValueOriginQuote<number>;
    activity_duration_hours: ValueOriginQuote<number>;
  };
  candidates: ExtractionCandidate[];
}

export interface CandidateMapping {
  candidate_id: string;
  metric_code: string | null;
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

// project_classification (A4, impact-science.md) : famille -> Areas (1
// principale) -> RISE (si CI) -> ODD, chaque valeur justifiée par une phrase
// tirée du texte.
export interface MappingActivityFamily {
  code: string;
  other_label: string | null;
  confidence: Confidence;
  justification: string;
}

export interface MappingArea {
  code: string;
  role: "primary" | "secondary";
  confidence: Confidence;
  justification: string;
}

export interface MappingRisePillar {
  code: string;
  confidence: Confidence;
  justification: string;
}

export interface MappingRise {
  status: "yes" | "no" | "not_applicable";
  pillars: MappingRisePillar[];
}

export interface MappingSdg {
  goal: number;
  role: "primary" | "secondary";
  confidence: Confidence;
  justification: string;
}

export interface MappingPayload {
  project_classification: {
    activity_families: MappingActivityFamily[];
    area_of_opportunity: MappingArea[];
    rise: MappingRise;
    sdgs: MappingSdg[];
    activity_type: string[]; // alias dérivé (compatibilité), pas ressaisi par l'IA
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

// --- Corps envoyé à POST /submissions/{id}/confirm (A5) ---

export interface ConfirmActivityFamilyInput {
  code: string;
  other_label: string | null;
}

export interface ConfirmAreaInput {
  code: string;
  role: "primary" | "secondary";
}

export interface ConfirmRiseInput {
  status: "yes" | "no" | "not_applicable";
  pillars: string[];
}

export interface ConfirmSdgInput {
  goal: number;
  role: "primary" | "secondary";
  justification: string;
}

export interface ConfirmAxesInput {
  activity_families: ConfirmActivityFamilyInput[];
  area_of_opportunity: ConfirmAreaInput[];
  rise: ConfirmRiseInput;
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
  jci_volunteers_count: number;
  activity_duration_hours: number;
  volunteer_hours: number;
  volunteer_hours_corrected: boolean;
}

export interface ConfirmCandidateInput {
  candidate_id: string;
  include: boolean;
  value?: number | null;
  value_internal?: number | null;
  value_external?: number | null;
  count_type?: string | null;
  internal_external?: string | null;
  corrected?: boolean;
}

export interface ConfirmRequestBody {
  project: ConfirmProjectInput;
  axes: ConfirmAxesInput;
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

// A7 -- GET /dashboards/{view}/overview (impact-science.md §7, D-29).
// Complémentaire à DashboardResponse ci-dessus : les nombres de ressources/
// impact/portée restent des Aggregate[] (mêmes objets, reclassables avec
// classify.ts comme aujourd'hui) ; ce qui s'y ajoute est un pur comptage de
// projets distincts, que le moteur ne produit pas lui-même.
export interface DashboardOverview {
  total_projects: number;
  projects_measured: number;
  rise_projects: number;
  rise_pct_of_ci: number | null;
  rise_pct_of_all: number | null;
  countries_active: number;
  ols_active: number;
  aggregates: Aggregate[];
  refusals: Refusal[];
}

export interface AreaFamilyCount {
  code: string;
  label: string;
  project_count: number;
}

export interface AreaRiseBreakdown {
  yes: number;
  no: number;
  pillars: { code: string; project_count: number }[];
}

export interface AreaTopSdg {
  goal: number;
  project_count: number;
}

// Écran 2 (impact-science.md §7) : un bloc par Area. `total_projects` d'un
// bloc n'est jamais comparable ni sommable avec les autres blocs (D-29) --
// le total unique de projets vient de DashboardOverview.total_projects.
export interface AreaBlock {
  code: string;
  label: string;
  total_projects: number;
  secondary_only_count: number;
  projects_measured: number;
  families: AreaFamilyCount[];
  rise: AreaRiseBreakdown | null;
  top_sdgs: AreaTopSdg[];
  aggregates: Aggregate[];
  refusals: Refusal[];
}

// Écran 3 : un bloc par ODD, seuls les ODD avec au moins un projet.
export interface SdgBlock {
  goal: number;
  primary_count: number;
  secondary_count: number;
  projects_measured: number;
  aggregates: Aggregate[];
}

export interface DashboardOverviewResponse {
  view: string;
  scope_organization_id: string | null;
  filters: Record<string, unknown>;
  computed_at: string;
  overview: DashboardOverview;
  areas: AreaBlock[];
  sdgs: SdgBlock[];
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

// Drill-down "Area / ODD -> projets" (revue Product Owner 2026-09-20) :
// GET /projects (liste, un item par projet du périmètre) et GET
// /projects/{id} (détail + mesures, pour l'écran de preuve/traçabilité).
export interface ProjectListItem {
  project_id: string;
  name: string;
  organization_id: string;
  organization_name: string;
  country_iso2: string | null;
  reporting_year: number;
  outcome_status: string;
}

export interface ProjectListResponse {
  projects: ProjectListItem[];
}

export interface ProjectDetail {
  project_id: string;
  name: string | null;
  organization_id: string;
  organization_name: string | null;
  country_iso2: string | null;
  reporting_year: number;
  period_start: string | null;
  period_end: string | null;
  outcome_status: string;
  expected_outcome: string | null;
  follow_up_date: string | null;
  taxonomy_version: string;
  confirmed_by: string | null;
  confirmed_at: string | null;
  axes: {
    area_of_opportunity: string[];
    programme: string[];
    rise_pillars: string[];
    sdgs: { goal: number; role: string }[];
  };
  measurements: MeasurementObject[];
}

export interface CheckPairResult {
  compatible: boolean;
  refusal?: Refusal;
}

export interface ApiErrorBody {
  detail?: string | { errors?: ConfirmErrorItem[]; [key: string]: unknown } | unknown;
}
