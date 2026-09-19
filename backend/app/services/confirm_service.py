"""Construction et validation des Measurement Objects a la confirmation de la
fiche (Annexe A #5, dev-brief.md section 3.2).

Principe : pour chaque chiffre retenu, on construit un Measurement Object
complet (forme imbriquee de measurement-object.schema.json), on le fait
passer par les DEUX validateurs reutilises tels quels (section 8), puis par
equivalence_key() et eligibility() du moteur -- CE DERNIER calcule la cle
d'equivalence et l'eligibilite, jamais l'IA (RI-03). Ce n'est qu'apres coup
que le MO est eclate en colonnes pour la table `measurement` (section 2.8).

Si UN SEUL candidat retenu echoue la validation, RIEN n'est ecrit (section
3.2, "si la transaction echoue, rien n'est ecrit") : cette fonction ne fait
aucun commit elle-meme, c'est au routeur de le faire apres coup.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.services import engine_service, validators_service
from app.services.ai_pipeline import _codes

RISE_PROGRAMME_CODE = "RISE"


class ConfirmError(Exception):
    """Erreur de validation bloquante : rien ne doit etre ecrit en base."""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("; ".join(e.get("message", "") for e in errors))


def _index_by_candidate_id(items: list[dict]) -> dict[str, dict]:
    return {it.get("candidate_id"): it for it in items if it.get("candidate_id")}


def _validate_axes(axes, taxonomy_content: dict) -> list[str]:
    """R2 (>=1 domaine), R5 (exactement 1 SDG primary), R4 (piliers RISE
    requis si RISE coche), et codes de taxonomie inconnus rejetes (jamais
    enregistres)."""
    errors: list[str] = []
    tc_axes = taxonomy_content["classification_axes"]
    allowed_area = set(_codes(tc_axes["area_of_opportunity"]))
    allowed_programme = set(_codes(tc_axes["programme"]))
    allowed_rise = set(_codes(taxonomy_content["rise_pillars"]))

    if not axes.area_of_opportunity:
        errors.append("axes.area_of_opportunity : au moins un domaine d'intervention est requis (R2)")
    for code in axes.area_of_opportunity:
        if code not in allowed_area:
            errors.append(f"axes.area_of_opportunity : code inconnu du referentiel : {code!r}")
    for code in axes.programme:
        if code not in allowed_programme:
            errors.append(f"axes.programme : code inconnu du referentiel : {code!r}")
    for code in axes.rise_pillars:
        if code not in allowed_rise:
            errors.append(f"axes.rise_pillars : code inconnu du referentiel : {code!r}")

    if RISE_PROGRAMME_CODE in axes.programme and not axes.rise_pillars:
        errors.append("axes.rise_pillars : au moins un pilier RISE est requis quand RISE est coche (R4)")

    primary_count = sum(1 for s in axes.sdgs if s.role == "primary")
    if not axes.sdgs:
        errors.append("axes.sdgs : au moins un ODD est requis, avec exactement un principal (R5)")
    elif primary_count != 1:
        errors.append(f"axes.sdgs : exactement un ODD 'primary' est requis (trouve : {primary_count})")

    return errors


def _validate_confirmations(confirmations) -> list[str]:
    errors = []
    for code in ("C1", "C2", "C3", "C4"):
        if not getattr(confirmations, code):
            errors.append(f"confirmation {code} manquante : la fiche ne peut pas etre confirmee (AC-16)")
    return errors


def _validate_project(project) -> list[str]:
    errors = []
    if project.outcome_status not in ("measured", "pending_follow_up", "none"):
        errors.append(f"project.outcome_status invalide : {project.outcome_status!r}")
    if project.outcome_status == "pending_follow_up":
        if not project.expected_outcome:
            errors.append("project.expected_outcome requis quand outcome_status = pending_follow_up")
        if not project.follow_up_date:
            errors.append("project.follow_up_date requis quand outcome_status = pending_follow_up")
    return errors


def _build_measurement_object(
    *,
    measurement_id: str,
    extraction_cand: dict,
    mapping: dict,
    user_input,
    project_id: str,
    project_name: str | None,
    reporting_year: int,
    period_start: str | None,
    period_end: str | None,
    taxonomy_refs_snapshot: dict,
    organization: "models.Organization",
    submission: "models.Submission",
    relations: list[dict],
) -> dict[str, Any]:
    value = extraction_cand.get("value")
    if user_input is not None and user_input.value is not None:
        value = user_input.value
    value_qualifier = extraction_cand.get("value_qualifier")
    definition_text = extraction_cand.get("definition_text")

    count_type = mapping.get("count_type")
    internal_external = mapping.get("internal_external")
    if user_input is not None:
        count_type = user_input.count_type or count_type
        internal_external = user_input.internal_external or internal_external

    geography: dict[str, Any] = {
        "local_organization": {"value": organization.name, "layer": "LOCAL_REPORTED_FACT"},
    }
    if organization.country_iso2:
        geography["country_iso2"] = {"value": organization.country_iso2, "layer": "LOCAL_REPORTED_FACT"}
        # geographic_area (SEMANTIC_INTERPRETATION, via geo_mapping) : non branche
        # tant que le vrai compte OL (D-18, country/geographic_area) n'existe pas.

    derivation = [
        {"step": "extract_number", "rule_id": "EXTRACT-NUM", "agent": "llm_extractor@v0",
         "confidence": extraction_cand.get("confidence")},
        {"step": "classify", "rule_id": "MAP-METRIC", "agent": "llm_classifier@v0",
         "confidence": mapping.get("confidence")},
    ]
    if user_input is not None and user_input.corrected:
        derivation.append({"step": "human_validation", "rule_id": "HUMAN-CONFIRM", "agent": "human@ol",
                            "confidence": "H"})

    mo: dict[str, Any] = {
        "measurement_id": measurement_id,
        "standard": engine_service.STANDARD,
        "metric_code": mapping.get("metric_code"),
        "metric_label_source": extraction_cand.get("metric_label_source"),
        "definition": {
            "status": "specified" if definition_text else "unknown",
            "text": definition_text or "NOT SPECIFIED IN THE SOURCE DOCUMENT",
            "layer": "LOCAL_REPORTED_FACT",
        },
        "iaooi_class": {
            "value": mapping.get("iaooi_value"),
            "layer": "SEMANTIC_INTERPRETATION",
            "standard": "PROPOSED_STANDARD:IAOOI-v0",
            "rule_id": "MAP-METRIC",
            "confidence": mapping.get("confidence"),
        },
        "source_wording_class": mapping.get("source_wording_class"),
        "taxonomy_refs": {
            **taxonomy_refs_snapshot,
            "target_group": mapping.get("target_group") or [],
            "layer": "SEMANTIC_INTERPRETATION",
        },
        "value": value,
        "value_status": "unknown" if value is None else "extracted",
        "value_qualifier": value_qualifier,
        "unit": {
            "code": mapping.get("unit_code"),
            "dimension": mapping.get("unit_dimension"),
        },
        "subject": {
            "type": "project",
            "id": project_id,
            "name": project_name,
        },
        "population": {
            "target_group": mapping.get("target_group") or [],
            "internal_external": internal_external or "unknown",
            "count_type": count_type or "unknown",
            "dedup_basis": mapping.get("dedup_basis") or "unknown",
        },
        "period": {
            "type": "reporting_year",
            "start": period_start,
            "end": period_end,
            "reporting_year": reporting_year,
        },
        "geography": geography,
        "layer": "LOCAL_REPORTED_FACT",
        "source": {
            "origin": "submission",
            "document_id": submission.submission_id,
            "quote": extraction_cand.get("quote"),
            "span": extraction_cand.get("span"),
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "language": submission.language,
        },
        "derivation": derivation,
        "confidence": extraction_cand.get("confidence"),
        "verification_status": "reported",
    }
    if relations:
        mo["relations"] = relations

    # equivalence_key / eligibility : calcules par le moteur, JAMAIS par l'IA (RI-03)
    eq_key = engine_service.equivalence_key(mo)
    refusal = engine_service.eligibility(mo)
    mo["aggregation"] = {
        "aggregable": refusal is None,
        "equivalence_key": eq_key,
        "refusal_reason": refusal.reason if refusal else None,
        "dedup_key": project_id,
    }
    return mo


def _mo_to_measurement_row(mo: dict, *, submission_id: str, project_id: str, organization_id: str,
                            taxonomy_version: str) -> models.Measurement:
    definition = mo.get("definition") or {}
    iaooi = mo.get("iaooi_class") or {}
    unit = mo.get("unit") or {}
    subject = mo.get("subject") or {}
    population = mo.get("population") or {}
    period = mo.get("period") or {}
    source = mo.get("source") or {}
    aggregation = mo.get("aggregation") or {}

    return models.Measurement(
        measurement_id=mo["measurement_id"],
        standard=mo["standard"],
        submission_id=submission_id,
        project_id=project_id,
        organization_id=organization_id,
        taxonomy_version=taxonomy_version,
        metric_code=mo["metric_code"],
        metric_label_source=mo["metric_label_source"],
        definition_status=definition.get("status"),
        definition_text=definition.get("text"),
        definition_layer=definition.get("layer"),
        iaooi_value=iaooi.get("value"),
        iaooi_layer=iaooi.get("layer"),
        iaooi_standard=iaooi.get("standard"),
        iaooi_rule_id=iaooi.get("rule_id"),
        iaooi_confidence=iaooi.get("confidence"),
        source_wording_class=mo.get("source_wording_class"),
        taxonomy_refs=mo.get("taxonomy_refs"),
        value=mo.get("value"),
        value_status=mo.get("value_status"),
        value_qualifier=mo.get("value_qualifier"),
        value_range=mo.get("value_range"),
        unit_code=unit.get("code"),
        unit_dimension=unit.get("dimension"),
        subject_type=subject.get("type"),
        subject_id=subject.get("id"),
        subject_name=subject.get("name"),
        pop_internal_external=population.get("internal_external"),
        pop_count_type=population.get("count_type"),
        pop_dedup_basis=population.get("dedup_basis"),
        pop_target_group=population.get("target_group"),
        period_type=period.get("type"),
        period_start=period.get("start"),
        period_end=period.get("end"),
        period_reporting_year=period.get("reporting_year"),
        geography=mo.get("geography"),
        layer=mo["layer"],
        source_origin=source.get("origin"),
        source_document_id=source.get("document_id"),
        source_quote=source.get("quote"),
        source_span=source.get("span"),
        source_submitted_at=source.get("submitted_at"),
        source_language=source.get("language"),
        confidence=mo.get("confidence"),
        verification_status=mo["verification_status"],
        agg_equivalence_key=aggregation.get("equivalence_key"),
        agg_aggregable="true" if aggregation.get("aggregable") else "false",
        agg_refusal_reason=aggregation.get("refusal_reason"),
        agg_dedup_key=aggregation.get("dedup_key"),
    )


def confirm_submission(db: Session, submission: models.Submission, payload) -> tuple[str, list[str]]:
    """Orchestration complete de la confirmation. Ne commit jamais elle-meme :
    en cas de succes le routeur committera, en cas de ConfirmError rien n'a
    ete flush de facon durable (le routeur fait rollback)."""
    from sqlalchemy import select
    taxonomy_release = db.execute(
        select(models.TaxonomyRelease).where(models.TaxonomyRelease.is_active.is_(True))
    ).scalar_one_or_none()
    if not taxonomy_release:
        raise ConfirmError([{"message": "aucune taxonomie active en base"}])
    taxonomy_content = taxonomy_release.content

    organization = db.get(models.Organization, submission.organization_id)
    if not organization:
        raise ConfirmError([{"message": f"organisation introuvable : {submission.organization_id}"}])

    errors: list[dict] = []
    errors += [{"message": m} for m in _validate_confirmations(payload.confirmations)]
    errors += [{"message": m} for m in _validate_axes(payload.axes, taxonomy_content)]
    errors += [{"message": m} for m in _validate_project(payload.project)]
    if errors:
        raise ConfirmError(errors)

    candidates_rows = db.execute(
        select(models.ExtractionCandidate)
        .where(models.ExtractionCandidate.submission_id == submission.submission_id)
        .order_by(models.ExtractionCandidate.created_at)
    ).scalars().all()
    structured = next((c for c in candidates_rows if c.stage == "structured"), None)
    standardized = next((c for c in candidates_rows if c.stage == "standardized"), None)
    if not structured or not standardized:
        raise ConfirmError([{"message": "le pipeline IA n'a pas produit de candidats structured+standardized"}])

    extraction_by_id = _index_by_candidate_id(structured.payload.get("candidates", []))
    mapping_by_id = _index_by_candidate_id(standardized.payload.get("candidate_mappings", []))
    user_by_id = {c.candidate_id: c for c in payload.candidates}
    relations_raw = standardized.payload.get("relations", [])

    included_ids = [
        cid for cid in extraction_by_id
        if cid in mapping_by_id and (cid not in user_by_id or user_by_id[cid].include)
    ]
    if not included_ids:
        raise ConfirmError([{"message": "aucun chiffre retenu : rien a confirmer"}])

    measurement_id_by_candidate = {cid: f"MEAS-{uuid.uuid4().hex[:12]}" for cid in included_ids}

    project_id = f"PRJ-{uuid.uuid4().hex[:12]}"
    taxonomy_refs_snapshot = {
        "area_of_opportunity": list(payload.axes.area_of_opportunity),
        "programme": list(payload.axes.programme),
        "sdgs": [s.model_dump() for s in payload.axes.sdgs],
        "activity_type": (standardized.payload.get("project_classification") or {}).get("activity_type", []),
    }

    mo_by_candidate: dict[str, dict] = {}
    validation_errors: list[dict] = []
    for cid in included_ids:
        relations_for_candidate = []
        for rel in relations_raw:
            other = None
            if rel.get("candidate_id_a") == cid:
                other = rel.get("candidate_id_b")
            elif rel.get("candidate_id_b") == cid:
                other = rel.get("candidate_id_a")
            if other and other in measurement_id_by_candidate:
                relations_for_candidate.append({
                    "relation_type": rel.get("relation_type"),
                    "measurement_id": measurement_id_by_candidate[other],
                })

        mo = _build_measurement_object(
            measurement_id=measurement_id_by_candidate[cid],
            extraction_cand=extraction_by_id[cid],
            mapping=mapping_by_id[cid],
            user_input=user_by_id.get(cid),
            project_id=project_id,
            project_name=payload.project.name,
            reporting_year=payload.project.reporting_year,
            period_start=payload.project.period_start,
            period_end=payload.project.period_end,
            taxonomy_refs_snapshot=taxonomy_refs_snapshot,
            organization=organization,
            submission=submission,
            relations=relations_for_candidate,
        )
        ok, detail = validators_service.is_valid(mo)
        if not ok:
            for code, path, msg in detail["schema_errors"]:
                validation_errors.append({"candidate_id": cid, "message": f"{code} {path}: {msg}"})
            for code, path, msg in detail["provenance_blocking"]:
                validation_errors.append({"candidate_id": cid, "message": f"{code} {path}: {msg}"})
        else:
            mo_by_candidate[cid] = mo

    if validation_errors:
        raise ConfirmError(validation_errors)

    # --- Rien n'a echoue : ecriture reelle (une seule transaction, non commitee ici) ---
    now = datetime.now(timezone.utc)
    project = models.Project(
        project_id=project_id,
        submission_id=submission.submission_id,
        organization_id=submission.organization_id,
        name=payload.project.name,
        reporting_year=payload.project.reporting_year,
        period_start=payload.project.period_start,
        period_end=payload.project.period_end,
        outcome_status=payload.project.outcome_status,
        expected_outcome=payload.project.expected_outcome,
        follow_up_date=(
            datetime.strptime(payload.project.follow_up_date, "%Y-%m-%d").date()
            if payload.project.follow_up_date else None
        ),
        programme_confirmed=True,
        taxonomy_version=taxonomy_release.version,
        confirmed_by=payload.confirmed_by,
        confirmed_at=now,
    )
    db.add(project)

    for code in payload.axes.area_of_opportunity:
        db.add(models.ProjectAreaOfOpportunity(project_id=project_id, code=code,
                                                confirmed_by=payload.confirmed_by, confirmed_at=now))
    for code in payload.axes.programme:
        db.add(models.ProjectProgramme(project_id=project_id, code=code,
                                        confirmed_by=payload.confirmed_by, confirmed_at=now))
    for code in payload.axes.rise_pillars:
        db.add(models.ProjectRisePillar(project_id=project_id, code=code,
                                         confirmed_by=payload.confirmed_by, confirmed_at=now))
    for sdg in payload.axes.sdgs:
        db.add(models.ProjectSdg(project_id=project_id, goal=sdg.goal, role=sdg.role,
                                  confirmed_by=payload.confirmed_by, confirmed_at=now))
    db.flush()  # le projet et ses axes existent avant toute mesure qui les reference

    # Ecriture en deux passes : toutes les mesures d'abord, puis leurs tables
    # filles (derivation, measurement_relation). Un flush() intermediaire
    # garantit que les FK sont satisfaites cote Postgres -- l'ordre de tri
    # topologique implicite de SQLAlchemy s'est avere insuffisant ici avec
    # plusieurs mesures + leurs enfants ajoutees de facon entrelacee (constate
    # en production : ForeignKeyViolation sur derivation.measurement_id).
    measurement_rows: dict[str, models.Measurement] = {}
    for cid, mo in mo_by_candidate.items():
        row = _mo_to_measurement_row(
            mo,
            submission_id=submission.submission_id,
            project_id=project_id,
            organization_id=submission.organization_id,
            taxonomy_version=taxonomy_release.version,
        )
        db.add(row)
        measurement_rows[cid] = row
    db.flush()

    for cid, mo in mo_by_candidate.items():
        row = measurement_rows[cid]
        for pos, step in enumerate(mo["derivation"]):
            db.add(models.Derivation(
                measurement_id=row.measurement_id, position=pos,
                step=step.get("step"), rule_id=step.get("rule_id"),
                agent=step.get("agent"), confidence=step.get("confidence"),
            ))
        for rel in mo.get("relations", []):
            db.add(models.MeasurementRelation(
                measurement_id=row.measurement_id,
                relation_type=rel["relation_type"],
                target_measurement_id=rel["measurement_id"],
            ))

    submission.pipeline_status = "confirmed"
    return project_id, [measurement_id_by_candidate[cid] for cid in mo_by_candidate]
