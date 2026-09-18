from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExtractionCandidate, Submission, TaxonomyRelease
from app.schemas import SubmissionCreate, SubmissionDetail, SubmissionOut
from app.services import ai_pipeline

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _run_pipeline(submission: Submission, db: Session) -> None:
    """Etapes STRUCTURED puis STANDARDIZED (dev-brief.md section 4).
    Synchrone (suffisant pour la demo hackathon). En cas d'echec :
    pipeline_status=failed, raw_text jamais modifie (RI-07, section 3.1)."""
    try:
        extraction = ai_pipeline.extract_structured(submission.raw_text)
    except Exception as exc:  # appel LLM, reseau, format de reponse
        submission.pipeline_status = "failed"
        submission.pipeline_error = f"extraction : {exc}"
        db.commit()
        return

    errors = ai_pipeline.validate_extraction_contract(extraction, submission.raw_text)
    db.add(ExtractionCandidate(
        candidate_id=f"CAND-{uuid.uuid4().hex[:12]}",
        submission_id=submission.submission_id,
        stage="structured",
        payload=extraction,
        model_id="llm_extractor@v0",
        validation_errors=errors or None,
    ))
    submission.language = extraction.get("language")
    if errors:
        submission.pipeline_status = "failed"
        submission.pipeline_error = "extraction invalide : " + " ; ".join(errors)
        db.commit()
        return
    submission.pipeline_status = "extracted"
    db.commit()

    taxonomy_release = db.execute(
        select(TaxonomyRelease).where(TaxonomyRelease.is_active.is_(True))
    ).scalar_one_or_none()
    if not taxonomy_release:
        submission.pipeline_status = "failed"
        submission.pipeline_error = "aucune taxonomie active en base (lancer supabase_init.sql)"
        db.commit()
        return

    try:
        mapping = ai_pipeline.map_standardized(extraction, taxonomy_release.content)
    except Exception as exc:
        submission.pipeline_status = "failed"
        submission.pipeline_error = f"mapping : {exc}"
        db.commit()
        return

    errors2 = ai_pipeline.validate_mapping_contract(mapping, taxonomy_release.content)
    db.add(ExtractionCandidate(
        candidate_id=f"CAND-{uuid.uuid4().hex[:12]}",
        submission_id=submission.submission_id,
        stage="standardized",
        payload=mapping,
        model_id="llm_classifier@v0",
        validation_errors=errors2 or None,
    ))
    if errors2:
        submission.pipeline_status = "failed"
        submission.pipeline_error = "mapping invalide : " + " ; ".join(errors2)
        db.commit()
        return

    submission.pipeline_status = "awaiting_confirmation"
    db.commit()


@router.post("", response_model=SubmissionOut)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    """Annexe A #1. Etape RAW (dev-brief section 3.1) : le texte est conserve
    tel quel, pour toujours (RI-07). Declenche ensuite les etapes 2/3."""
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

    _run_pipeline(submission, db)
    db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=SubmissionDetail)
def get_submission(submission_id: str, db: Session = Depends(get_db)):
    """Annexe A #2."""
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission introuvable")
    return submission


@router.get("/{submission_id}/draft")
def get_submission_draft(submission_id: str, db: Session = Depends(get_db)):
    """Annexe A #4 (version socle) : expose les candidats IA bruts (structured
    + standardized) pour verification. L'ecran de confirmation (Phase 4) en
    fera une fiche lisible avec origine par champ."""
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission introuvable")
    candidates = db.execute(
        select(ExtractionCandidate)
        .where(ExtractionCandidate.submission_id == submission_id)
        .order_by(ExtractionCandidate.created_at)
    ).scalars().all()
    return {
        "submission_id": submission.submission_id,
        "pipeline_status": submission.pipeline_status,
        "pipeline_error": submission.pipeline_error,
        "candidates": [
            {"stage": c.stage, "payload": c.payload, "validation_errors": c.validation_errors}
            for c in candidates
        ],
    }


@router.post("/{submission_id}/retry", response_model=SubmissionOut)
def retry_submission(submission_id: str, db: Session = Depends(get_db)):
    """Annexe A #3. Relance l'analyse sur le MEME texte : on ne redemande
    jamais de ressaisir (dev-brief section 3.1)."""
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission introuvable")
    submission.pipeline_status = "received"
    submission.pipeline_error = None
    db.commit()
    _run_pipeline(submission, db)
    db.refresh(submission)
    return submission
