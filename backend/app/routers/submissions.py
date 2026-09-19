from __future__ import annotations

import hashlib
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExtractionCandidate, Submission, TaxonomyRelease
from app.schemas import ConfirmRequest, ConfirmResult, SubmissionCreate, SubmissionDetail, SubmissionOut
from app.services import ai_pipeline, confirm_service

logger = logging.getLogger("nexus.submissions")
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
    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)
    except Exception as exc:
        db.rollback()
        # Le detail complet part dans les logs serveur (visibles sur Render,
        # onglet Logs) ; l'appelant ne recoit qu'un message generique, pour
        # ne jamais exposer de details internes (SQL, schema) via l'API.
        logger.exception("Echec de creation de submission (organization_id=%s, user_id=%s)",
                          payload.organization_id, payload.user_id)
        raise HTTPException(status_code=500, detail="Impossible d'enregistrer le temoignage pour le moment.") from exc

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


@router.post("/{submission_id}/confirm")
def confirm_submission(submission_id: str, payload: ConfirmRequest, db: Session = Depends(get_db)):
    """Annexe A #5. Ecrit project + measurements en une seule transaction
    (dev-brief section 3.2). Si un seul MO echoue la validation, RIEN n'est
    ecrit (422 avec le detail des erreurs).

    Diagnostic temporaire (deploiement) : toute la fonction est entouree
    d'un unique try/except qui renvoie une JSONResponse construite a la
    main (jamais via HTTPException/response_model), pour ecarter tout
    probleme de serialisation cote framework le temps de stabiliser ce
    tout nouvel endpoint en production."""
    import traceback

    from fastapi.responses import JSONResponse

    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return JSONResponse(status_code=404, content={"detail": "submission introuvable"})
        if submission.pipeline_status != "awaiting_confirmation":
            return JSONResponse(status_code=409, content={
                "detail": f"submission non prete pour confirmation (statut actuel : {submission.pipeline_status})",
            })
        try:
            project_id, measurement_ids = confirm_service.confirm_submission(db, submission, payload)
        except confirm_service.ConfirmError as exc:
            db.rollback()
            return JSONResponse(status_code=422, content={"errors": exc.errors})
        db.commit()
        return {"project_id": project_id, "measurement_ids": measurement_ids}
    except Exception as exc:
        db.rollback()
        logger.exception("Echec inattendu de confirmation (submission_id=%s)", submission_id)
        return JSONResponse(status_code=500, content={
            "message": str(exc),
            "traceback": traceback.format_exc(),
        })
