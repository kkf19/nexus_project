from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TaxonomyRelease

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("")
def get_active_taxonomy(db: Session = Depends(get_db)):
    """Annexe A #13. Le référentiel actif, chargé tel quel par
    scripts/init_db.py — jamais recopié en dur (dev-brief §2.1)."""
    release = db.execute(
        select(TaxonomyRelease).where(TaxonomyRelease.is_active.is_(True))
    ).scalar_one_or_none()
    if not release:
        raise HTTPException(status_code=404, detail="aucune taxonomie active — lancer scripts/init_db.py")
    return {"version": release.version, "content": release.content}
