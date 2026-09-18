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
