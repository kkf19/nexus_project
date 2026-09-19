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
# Annexe A #5 — POST /submissions/{id}/confirm (dev-brief.md section 3.2)
# ---------------------------------------------------------------------------
class ConfirmSdg(BaseModel):
    goal: int
    role: str  # primary|secondary|unknown


class ConfirmAxes(BaseModel):
    area_of_opportunity: list[str] = []   # >=1 requis (R2)
    programme: list[str] = []             # 0..n, "aucun programme" = liste vide (R9)
    rise_pillars: list[str] = []          # >=1 requis si "RISE" dans programme (R4)
    sdgs: list[ConfirmSdg] = []           # >=1, exactement 1 "primary" (R5)


class ConfirmProject(BaseModel):
    name: str | None = None
    reporting_year: int
    period_start: str | None = None
    period_end: str | None = None
    outcome_status: str  # measured|pending_follow_up|none (D-20)
    expected_outcome: str | None = None   # requis si pending_follow_up
    follow_up_date: str | None = None     # requis si pending_follow_up (date ISO)


class ConfirmCandidateInput(BaseModel):
    candidate_id: str
    include: bool = True          # false = l'utilisateur retire ce chiffre
    value: float | None = None    # correction de valeur (sinon celle de l'IA)
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
