"""Schémas Pydantic pour les entrées/sorties de l'API.

À ne pas confondre avec measurement-object.schema.json, qui reste LA seule
source de vérité pour la forme d'un Measurement Object (dev-brief.md §8).
"""
from __future__ import annotations

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    raw_text: str
    # Provisoire : il n'y a pas encore de compte OL connecté (Phase 1).
    # Sera remplacé par l'identité du compte authentifié.
    organization_id: str = "DEMO-OL"
    user_id: str = "DEMO-USER"


class SubmissionOut(BaseModel):
    submission_id: str
    pipeline_status: str

    class Config:
        from_attributes = True


class SubmissionDetail(BaseModel):
    submission_id: str
    pipeline_status: str
    pipeline_error: str | None
    raw_text: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    project_id: str
    name: str | None
    reporting_year: int
    outcome_status: str

    class Config:
        from_attributes = True


class MeasurementOut(BaseModel):
    measurement_id: str
    metric_code: str
    value: float | None
    value_status: str | None
    layer: str
    verification_status: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Annexe A #5 — POST /submissions/{id}/confirm (dev-brief.md section 3.2,
# revu par impact-science.md D-23 a D-31)
# ---------------------------------------------------------------------------
class ConfirmSdg(BaseModel):
    goal: int
    role: str  # primary|secondary|unknown


class ConfirmAxes(BaseModel):
    # NOTE (A3) : forme Phase 3 conservee telle quelle ici. Les changements
    # d'impact-science.md sur cet axe (role primary/secondary par Area,
    # activity_families comme 1ere dimension, rise_status conditionne a CI,
    # ODD sans plafond mais justifies) sont apportes en A4/A5, en meme temps
    # que le pipeline IA et la validation qui les exploitent -- pour ne pas
    # ajouter des champs de schema qu'aucun code ne consomme encore.
    area_of_opportunity: list[str] = []   # >=1 requis (R2)
    programme: list[str] = []             # 0..n, DEPRECATED (D-23) -- conserve pour compatibilite,
                                           # plus alimente a partir de v0.3.0
    rise_pillars: list[str] = []          # >=1 requis si "RISE" dans programme (R4, forme Phase 3)
    sdgs: list[ConfirmSdg] = []           # >=1, exactement 1 "primary" (R5)


class ConfirmProject(BaseModel):
    name: str | None = None
    reporting_year: int
    period_start: str | None = None
    period_end: str | None = None
    outcome_status: str  # measured|pending_follow_up|none (D-20)
    expected_outcome: str | None = None   # requis si pending_follow_up
    follow_up_date: str | None = None     # requis si pending_follow_up (date ISO)

    # Ressources (D-25/D-28/D-30) : champs dedies et obligatoires, plus
    # dependants d'un candidat numerique generique. "0" est une valeur
    # explicite acceptee ; seule l'ABSENCE de valeur est refusee (AC-16) --
    # d'ou des champs non optionnels ici (pas de valeur par defaut).
    jci_volunteers_count: float           # bénévoles JCI (internes)
    activity_duration_hours: float        # durée de l'activité, en heures
    volunteer_hours: float                # heures de bénévolat -- préremplies au calcul
                                           # bénévoles x durée, corrigeables par le SG
    volunteer_hours_corrected: bool = False  # True si le SG a modifié la valeur pré-calculée (D-30)


class ConfirmCandidateInput(BaseModel):
    candidate_id: str
    include: bool = True          # false = l'utilisateur retire ce chiffre
    value: float | None = None    # correction de valeur (sinon celle de l'IA) -- ignore si
                                   # la population résultante est "mixed" (voir value_internal/external)
    value_internal: float | None = None  # requis si internal_external résultant == "mixed" (D-26/AC-30)
    value_external: float | None = None  # requis si internal_external résultant == "mixed" (D-26/AC-30)
    count_type: str | None = None       # reponse C1 (beneficiaires uniquement)
    internal_external: str | None = None  # reponse C2 (beneficiaires uniquement)
    corrected: bool = False       # trace derivation "human_validation"


class ConfirmConfirmations(BaseModel):
    C1: bool = False
    C2: bool = False
    C3: bool = False
    C4: bool = False


class ConfirmRequest(BaseModel):
    project: ConfirmProject
    axes: ConfirmAxes
    confirmations: ConfirmConfirmations
    candidates: list[ConfirmCandidateInput] = []
    confirmed_by: str = "DEMO-USER"


class ConfirmResult(BaseModel):
    project_id: str
    measurement_ids: list[str]


# ---------------------------------------------------------------------------
# Annexe A #8 — POST /measurements/{id}/review
# ---------------------------------------------------------------------------
class ReviewRequest(BaseModel):
    action: str  # validate|flag|unflag
    reason: str | None = None
    reviewed_by: str = "DEMO-USER"


# ---------------------------------------------------------------------------
# Annexe A #9 — POST /aggregations/run (et #10 GET /dashboards/{view})
# ---------------------------------------------------------------------------
class AggregationFilters(BaseModel):
    reporting_year: int | None = None
    area_of_opportunity: str | None = None   # axe A
    programme: str | None = None              # axe B (DEPRECATED, D-23)
    sdg: int | None = None                    # axe C (numero d'ODD, 1..17)


class AggregationRunRequest(BaseModel):
    view: str  # ol|national|global
    scope_organization_id: str | None = None  # requis pour ol/national, absent pour global
    group_by: str = "network"                 # subject|geography|network
    filters: AggregationFilters = AggregationFilters()


# ---------------------------------------------------------------------------
# Annexe A #12 — POST /aggregations/check-pair
# ---------------------------------------------------------------------------
class CheckPairRequest(BaseModel):
    measurement_id_a: str
    measurement_id_b: str
