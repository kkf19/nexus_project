from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project
from app.schemas import ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Annexe A #6 (version minimale du socle — les 4 tables de
    classification et les MO rattachés arrivent avec l'agrégation branchée,
    Phase 3)."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project introuvable")
    return project
