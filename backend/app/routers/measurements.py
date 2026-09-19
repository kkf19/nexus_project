from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement
from app.schemas import ReviewRequest
from app.services import mo_builder

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/{measurement_id}")
def get_measurement(measurement_id: str, db: Session = Depends(get_db)):
    """Annexe A #7 : MO complet reconstitue (mo_builder), avec derivation[]
    et relations[] — ce que le socle (Phase 1) ne pouvait pas encore rendre."""
    measurement = db.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="measurement introuvable")
    return mo_builder.row_to_measurement_object(db, measurement)


@router.post("/{measurement_id}/review")
def review_measurement(measurement_id: str, payload: ReviewRequest, db: Session = Depends(get_db)):
    """Annexe A #8. Refus si `layer = OFFICIAL_JCI_FACT` (T4/RI-05 : un
    chiffre JCI reste `reported` definitivement) ou si `dq_refs` est present
    (T6 : un conflit documentaire ouvert bloque toute revue)."""
    measurement = db.get(Measurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="measurement introuvable")

    if measurement.layer == "OFFICIAL_JCI_FACT":
        raise HTTPException(
            status_code=409,
            detail="un chiffre JCI officiel reste 'reported' definitivement : aucune revue possible (T4, RI-05)",
        )
    if measurement.dq_refs:
        raise HTTPException(
            status_code=409,
            detail="un conflit documentaire ouvert bloque toute revue tant qu'il n'est pas resolu (T6) : "
                   + ", ".join(measurement.dq_refs),
        )

    now = datetime.now(timezone.utc)
    if payload.action == "validate":
        measurement.verification_status = "validated"
        measurement.validated_by = payload.reviewed_by
        measurement.validated_at = now
    elif payload.action == "flag":
        measurement.verification_status = "flagged"
        measurement.flag = {"reason": payload.reason, "by": payload.reviewed_by, "at": now.isoformat()}
    elif payload.action == "unflag":
        measurement.verification_status = "reported"
        measurement.flag = None
    else:
        raise HTTPException(status_code=400, detail=f"action inconnue : {payload.action!r} (validate|flag|unflag)")

    db.commit()
    db.refresh(measurement)
    return mo_builder.row_to_measurement_object(db, measurement)
