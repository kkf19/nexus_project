from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement
from app.schemas import MeasurementOut

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/{measurement_id}", response_model=MeasurementOut)
def get_measurement(measurement_id: str, db: Session = Depends(get_db)):
    """Annexe A #7 (version minimale du socle — derivation[] et relations[]
    arrivent avec l'agrégation branchée, Phase 3)."""
    measurement = db.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="measurement introuvable")
    return measurement
