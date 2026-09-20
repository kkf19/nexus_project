from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Measurement,
    Organization,
    Project,
    ProjectAreaOfOpportunity,
    ProjectProgramme,
    ProjectRisePillar,
    ProjectSdg,
)
from app.services import aggregation_service, mo_builder

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def get_projects_list(
    view: str,
    scope_organization_id: str | None = None,
    area_of_opportunity: str | None = None,
    sdg: int | None = None,
    reporting_year: int | None = None,
    db: Session = Depends(get_db),
):
    """Drill-down du tableau de bord (revue Product Owner 2026-09-20) : liste
    les projets d'un perimetre (vue + organisation + annee), optionnellement
    restreinte a une Area ou un ODD -- memes filtres que get_area_breakdown /
    get_sdg_breakdown (aggregation_service.py), aucune nouvelle regle."""
    try:
        return aggregation_service.list_projects(
            db, view=view, scope_organization_id=scope_organization_id,
            area_of_opportunity=area_of_opportunity, sdg=sdg, reporting_year=reporting_year,
        )
    except aggregation_service.AggregationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Annexe A #6 : le projet, ses 4 tables de classification (axes A, B,
    piliers RISE, C — indépendants, RI-10), et les MO rattachés (reconstitués
    en entier, mo_builder)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project introuvable")

    organization = db.get(Organization, project.organization_id)

    areas = db.execute(
        select(ProjectAreaOfOpportunity).where(ProjectAreaOfOpportunity.project_id == project_id)
    ).scalars().all()
    programmes = db.execute(
        select(ProjectProgramme).where(ProjectProgramme.project_id == project_id)
    ).scalars().all()
    pillars = db.execute(
        select(ProjectRisePillar).where(ProjectRisePillar.project_id == project_id)
    ).scalars().all()
    sdgs = db.execute(
        select(ProjectSdg).where(ProjectSdg.project_id == project_id)
    ).scalars().all()
    measurements = db.execute(
        select(Measurement).where(Measurement.project_id == project_id)
    ).scalars().all()

    return {
        "project_id": project.project_id,
        "name": project.name,
        "organization_id": project.organization_id,
        "organization_name": organization.name if organization else None,
        "country_iso2": organization.country_iso2 if organization else None,
        "reporting_year": project.reporting_year,
        "period_start": project.period_start,
        "period_end": project.period_end,
        "outcome_status": project.outcome_status,
        "expected_outcome": project.expected_outcome,
        "follow_up_date": project.follow_up_date.isoformat() if project.follow_up_date else None,
        "taxonomy_version": project.taxonomy_version,
        "confirmed_by": project.confirmed_by,
        "confirmed_at": project.confirmed_at.isoformat() if project.confirmed_at else None,
        "axes": {
            "area_of_opportunity": [a.code for a in areas],
            "programme": [p.code for p in programmes],
            "rise_pillars": [p.code for p in pillars],
            "sdgs": [{"goal": s.goal, "role": s.role} for s in sdgs],
        },
        "measurements": mo_builder.rows_to_measurement_objects(db, measurements),
    }
