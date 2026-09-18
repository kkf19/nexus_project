from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Submission
from app.schemas import SubmissionCreate, SubmissionDetail, SubmissionOut

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionOut)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    """Annexe A #1. Étape RAW (dev-brief §3.1) : le texte est conservé tel
    quel, pour toujours (RI-07). Les étapes 2/3 (extraction et classement IA)
    seront déclenchées ici à partir de la Phase 2 — non câblées pour l'instant."""
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text vide")

    submission = Submission(
        submission_id=f"SUB-{uuid.uuid4().hex[:12]}",
        organization_id=payload.organization_id,
        user_id=payload.user_id,
        raw_text=payload.raw_text,
        raw_text_sha256=hashlib.sha256(payload.raw_text.encode("utf-8")).hexdigest(),
        pipeline_status="received",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=SubmissionDetail)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    """Annexe A #2."""
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission introuvable")
    return submission


@router.post("/{submission_id}/retry", response_model=SubmissionOut)
def retry_submission(submission_id: str, db: Session = Depends(get_db)):
    """Annexe A #3. Relance l'analyse sur le MÊME texte : on ne redemande
    jamais de ressaisir (dev-brief §3.1)."""
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission introuvable")
    submission.pipeline_status = "received"
    submission.pipeline_error = None
    db.commit()
    db.refresh(submission)
    return submission
