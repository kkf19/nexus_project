"""Orchestration de l'agregation branchee sur l'API (dev-brief.md section 3.3
et Annexe A, points d'entree #9 a #12).

Ce module ne decide RIEN sur l'eligibilite ou la compatibilite de deux
mesures : tout cela reste dans aggregation_engine.py, appele tel quel via
engine_service (dev-brief.md section 8 -- "toute divergence... est un bug de
la reimplementation"). Son role, uniquement :

1. Choisir quelles mesures entrent dans un calcul donne, selon la vue
   (OL / nationale / mondiale) et les filtres (annee, 3 axes separement) --
   dev-brief.md section 3.3.
2. Reconstituer ces mesures en MO complets (mo_builder), en excluant les
   agregats deja calcules et les chiffres de reference JCI, comme demande en
   section 8.
3. Appeler aggregate() du moteur.
4. Ecrire le resultat : un agregat par Aggregate produit (ligne `aggregate` +
   MO calcule dans `measurement` + parents dans `measurement_parent`), et une
   ligne `refusal` par refus SANS EXCEPTION (RI-06 / CTL-REFUSAL).
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.services import engine_service, mo_builder, validators_service

logger = logging.getLogger("nexus.aggregation")

VIEWS = ("ol", "national", "global")
GROUP_BY_VALUES = ("subject", "geography", "network")


class AggregationError(Exception):
    """Erreur cote appelant (vue/scope invalide, mesure introuvable...).
    Le routeur la traduit en reponse HTTP (400 ou 404 selon status_code)."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ---------------------------------------------------------------------------
# Selection du perimetre (dev-brief.md section 3.3)
# ---------------------------------------------------------------------------
def _scope_organization_ids(db: Session, view: str, scope_organization_id: str | None) -> list[str] | None:
    """None = pas de restriction (vue mondiale). Sinon la liste exacte des
    organization_id dont les mesures entrent dans le calcul."""
    if view == "ol":
        if not scope_organization_id:
            raise AggregationError("scope_organization_id requis pour la vue 'ol'")
        return [scope_organization_id]
    if view == "national":
        if not scope_organization_id:
            raise AggregationError("scope_organization_id requis pour la vue 'national'")
        children = db.execute(
            select(models.Organization.organization_id)
            .where(models.Organization.parent_organization_id == scope_organization_id)
        ).scalars().all()
        return list(children)
    if view == "global":
        return None
    raise AggregationError(f"vue inconnue : {view!r} (attendu : {', '.join(VIEWS)})")


def _project_ids_matching_axes(db: Session, filters: dict) -> list[str] | None:
    """Croise les 3 axes de classification, chacun applique separement puis
    intersecte (RI-10 : les axes sont independants, on ne les fusionne pas
    en une seule regle). None = aucun filtre d'axe demande."""
    area = filters.get("area_of_opportunity")
    programme = filters.get("programme")
    sdg = filters.get("sdg")
    if not any([area, programme, sdg]):
        return None

    result: set[str] | None = None

    def _intersect(ids: set[str]) -> None:
        nonlocal result
        result = ids if result is None else (result & ids)

    if area:
        _intersect(set(db.execute(
            select(models.ProjectAreaOfOpportunity.project_id)
            .where(models.ProjectAreaOfOpportunity.code == area)
        ).scalars().all()))
    if programme:
        _intersect(set(db.execute(
            select(models.ProjectProgramme.project_id)
            .where(models.ProjectProgramme.code == programme)
        ).scalars().all()))
    if sdg:
        _intersect(set(db.execute(
            select(models.ProjectSdg.project_id)
            .where(models.ProjectSdg.goal == int(sdg))
        ).scalars().all()))

    return sorted(result or set())


def _select_candidate_rows(db: Session, view: str, scope_organization_id: str | None,
                            filters: dict) -> list[models.Measurement]:
    """Mesures candidates : exclut les agregats deja calcules (source =
    'engine') et les chiffres de reference JCI (layer = OFFICIAL_JCI_FACT),
    comme demande dev-brief.md section 8."""
    org_ids = _scope_organization_ids(db, view, scope_organization_id)

    stmt = select(models.Measurement).where(
        models.Measurement.layer != "OFFICIAL_JCI_FACT",
        (models.Measurement.source_origin.is_(None)) | (models.Measurement.source_origin != "engine"),
    )
    if org_ids is not None:
        if not org_ids:
            return []
        stmt = stmt.where(models.Measurement.organization_id.in_(org_ids))

    reporting_year = filters.get("reporting_year")
    if reporting_year is not None:
        stmt = stmt.where(models.Measurement.period_reporting_year == int(reporting_year))

    project_ids_filter = _project_ids_matching_axes(db, filters)
    if project_ids_filter is not None:
        if not project_ids_filter:
            return []
        stmt = stmt.where(models.Measurement.project_id.in_(project_ids_filter))

    return list(db.execute(stmt).scalars().all())


# ---------------------------------------------------------------------------
# Sujet et periode d'un agregat produit par le moteur
# ---------------------------------------------------------------------------
def _build_subject_and_period(a: Any, mo_by_id: dict[str, dict], *, group_by: str, view: str,
                               scope_organization_id: str | None) -> tuple[dict, dict]:
    """Le moteur (Aggregate.to_measurement_object) attend un subject et une
    period tout faits -- il ne les invente pas (dev-brief.md Annexe A #9).
    Aucune regle d'eligibilite ici : la periode vient d'une des mesures
    d'entree (elles partagent deja la meme reporting_year a l'interieur d'un
    seau -- pair_compatibility() l'exige dans aggregation_engine.py).

    IMPORTANT (E1, validate_measurement_objects.py) : `aggregation.equivalence_key`
    stockee sur l'agregat est CELLE DEJA CALCULEE PAR LE MOTEUR a partir des
    mesures d'entree (Aggregate.equivalence_key, jamais recalculee ici) --
    et cette cle inclut `subject.type` (aggregation_engine.py, equivalence_key()).
    Le validateur la revalide en la recalculant depuis le MO stocke : si le
    `subject.type` qu'on donne ici differe de celui des mesures d'entree, la
    cle stockee et la cle recalculee divergent et l'objet est rejete. Comme
    tous les membres d'un meme seau partagent deja le meme `subject.type`
    (il fait partie de la cle de regroupement), on le reprend TEL QUEL ; seuls
    `id`/`name` (hors cle) decrivent la portee de l'agregat."""
    first_input_mo = mo_by_id[a.inputs[0]]
    period = dict(first_input_mo.get("period") or {"type": "unknown"})
    input_subject_type = (first_input_mo.get("subject") or {}).get("type") or "project"

    if group_by == "subject":
        # a.group == f"{subject.type}:{subject.id}" : tous les membres du
        # seau partagent deja ce sujet (c'est la cle de regroupement).
        subject = dict(first_input_mo.get("subject") or {})
        subject.setdefault("type", input_subject_type)
    elif group_by == "geography":
        _, _, value = a.group.partition(":")
        subject = {"type": input_subject_type, "id": value or "unknown", "name": a.group}
    else:  # "network"
        subject = {
            "type": input_subject_type,
            "id": scope_organization_id or "JCI_GLOBAL",
            "name": {"ol": "Agregat — vue OL", "national": "Agregat — vue nationale",
                     "global": "Agregat — vue mondiale"}.get(view, "Agregat"),
        }
    return subject, period


def _bucket_of_refusal(refusal: Any, mo_by_id: dict[str, dict], group_by: str) -> tuple[str, str] | None:
    """A quel (groupe, cle d'equivalence) appartient un refus de paire, pour
    le relier a l'agregat qu'il concerne. Les refus de paire du moteur ne
    surviennent qu'entre membres d'un MEME seau (aggregation_engine.py,
    aggregate() : pair_compatibility() n'est appele qu'a l'interieur d'un
    seau deja regroupe par cle d'equivalence) -- on relit cette cle, on ne
    la recalcule jamais autrement que via les fonctions du moteur."""
    for mid in refusal.measurement_ids:
        mo = mo_by_id.get(mid)
        if mo:
            return (engine_service.group_label(mo, group_by), engine_service.equivalence_key(mo))
    return None


def _write_refusal(db: Session, refusal: Any, *, aggregate_run_id: str | None) -> dict:
    refusal_id = f"REF-{uuid.uuid4().hex[:12]}"
    db.add(models.Refusal(
        refusal_id=refusal_id,
        aggregate_run_id=aggregate_run_id,
        reason=refusal.reason,
        measurement_ids=refusal.measurement_ids,
        detail=refusal.detail or None,
        explanation_fr=refusal.explain(),
    ))
    return {
        "refusal_id": refusal_id,
        "aggregate_run_id": aggregate_run_id,
        "reason": refusal.reason,
        "measurement_ids": refusal.measurement_ids,
        "detail": refusal.detail or None,
        "explanation_fr": refusal.explain(),
    }


# ---------------------------------------------------------------------------
# Annexe A #9 — POST /aggregations/run
# ---------------------------------------------------------------------------
def run_aggregation(db: Session, *, view: str, scope_organization_id: str | None,
                     group_by: str = "network", filters: dict | None = None) -> dict:
    filters = dict(filters or {})
    if group_by not in GROUP_BY_VALUES:
        raise AggregationError(f"group_by inconnu : {group_by!r} (attendu : {', '.join(GROUP_BY_VALUES)})")
    if view not in VIEWS:
        raise AggregationError(f"vue inconnue : {view!r} (attendu : {', '.join(VIEWS)})")
    if view != "global" and scope_organization_id and not db.get(models.Organization, scope_organization_id):
        raise AggregationError(f"organisation introuvable : {scope_organization_id}", status_code=404)

    rows = _select_candidate_rows(db, view, scope_organization_id, filters)
    mo_list = [mo_builder.row_to_measurement_object(db, r) for r in rows]
    # Filet de securite en plus du filtre source_origin ci-dessus (dev-brief.md
    # section 8 : "exclure les MO agregats (parent_measurement_ids non vide)").
    mo_list = [m for m in mo_list if not m.get("parent_measurement_ids")]
    mo_by_id = {m["measurement_id"]: m for m in mo_list}

    result = engine_service.aggregate(mo_list, group_by=group_by, total_units=None)

    now = datetime.now(timezone.utc)
    aggregate_dicts: list[dict] = []
    run_id_by_bucket: dict[tuple[str, str], str] = {}

    for a in result.aggregates:
        run_id = f"RUN-{uuid.uuid4().hex[:12]}"
        new_measurement_id = f"AGG-{uuid.uuid4().hex[:12]}"
        subject, period = _build_subject_and_period(
            a, mo_by_id, group_by=group_by, view=view, scope_organization_id=scope_organization_id,
        )
        mo = a.to_measurement_object(new_measurement_id, subject, period)

        valid, detail = validators_service.is_valid(mo)
        if not valid:
            # L'agregat vient du moteur reutilise tel quel (section 8) : ceci ne
            # devrait jamais arriver. Le calcul lui-meme reste correct ; on ne
            # bloque pas le tableau de bord pour ca, mais on le journalise fort
            # cote serveur pour investigation (jamais annonce "conforme" sans
            # verification reelle).
            logger.error("Agregat %s invalide selon les validateurs reutilises : %s", new_measurement_id, detail)

        row = mo_builder.mo_to_measurement_row(
            mo, submission_id=None, project_id=None,
            organization_id=scope_organization_id, taxonomy_version=None,
        )
        db.add(row)
        db.flush()

        for pos, step in enumerate(mo.get("derivation") or []):
            db.add(models.Derivation(
                measurement_id=new_measurement_id, position=pos,
                step=step.get("step"), rule_id=step.get("rule_id"),
                agent=step.get("agent"), confidence=step.get("confidence"),
            ))
        for pos, parent_id in enumerate(a.inputs):
            db.add(models.MeasurementParent(
                measurement_id=new_measurement_id, parent_measurement_id=parent_id, position=pos,
            ))
        db.add(models.AggregateRun(
            aggregate_run_id=run_id,
            measurement_id=new_measurement_id,
            view=view,
            scope_organization_id=scope_organization_id,
            group_by=group_by,
            group_label=a.group,
            filters=filters or None,
            engine_version=engine_service.ENGINE_VERSION,
            computed_at=now,
        ))

        run_id_by_bucket[(a.group, a.equivalence_key)] = run_id
        mo["_aggregate_run_id"] = run_id
        aggregate_dicts.append(mo)

    refusal_dicts: list[dict] = []
    # Exclusions individuelles (eligibility()) : n'appartiennent a aucun seau.
    for _mid, refusal in result.excluded:
        refusal_dicts.append(_write_refusal(db, refusal, aggregate_run_id=None))
    # Refus de paire (pair_compatibility()) : rattaches a l'agregat de leur seau.
    for refusal in result.refusals:
        bucket = _bucket_of_refusal(refusal, mo_by_id, group_by)
        run_id = run_id_by_bucket.get(bucket) if bucket else None
        refusal_dicts.append(_write_refusal(db, refusal, aggregate_run_id=run_id))

    db.commit()

    return {
        "view": view,
        "scope_organization_id": scope_organization_id,
        "group_by": group_by,
        "filters": filters,
        "computed_at": now.isoformat(),
        "engine_version": engine_service.ENGINE_VERSION,
        "aggregates": aggregate_dicts,
        "refusals": refusal_dicts,
        "stale": False,
    }


# ---------------------------------------------------------------------------
# Annexe A #10 — GET /dashboards/{view}
# ---------------------------------------------------------------------------
def _last_successful_run(db: Session, *, view: str, scope_organization_id: str | None,
                          group_by: str) -> dict | None:
    """dev-brief.md section 3.3 : "en cas d'echec du moteur, l'ecran affiche
    la derniere execution reussie avec sa date". Best-effort : ne retrouve que
    les refus rattaches a un agregat de ce lot (les exclusions individuelles,
    non rattachees, ne sont pas rejouables apres coup par construction)."""
    stmt = select(models.AggregateRun).where(
        models.AggregateRun.view == view, models.AggregateRun.group_by == group_by,
    )
    stmt = stmt.where(models.AggregateRun.scope_organization_id == scope_organization_id) \
        if scope_organization_id is not None else stmt.where(models.AggregateRun.scope_organization_id.is_(None))

    latest = db.execute(stmt.order_by(models.AggregateRun.computed_at.desc())).scalars().first()
    if latest is None:
        return None

    same_batch = [r for r in db.execute(
        stmt.where(models.AggregateRun.computed_at == latest.computed_at)
    ).scalars().all()]

    aggregate_dicts: list[dict] = []
    refusal_dicts: list[dict] = []
    for run in same_batch:
        row = db.get(models.Measurement, run.measurement_id)
        if row:
            mo = mo_builder.row_to_measurement_object(db, row)
            mo["_aggregate_run_id"] = run.aggregate_run_id
            aggregate_dicts.append(mo)
        refusals = db.execute(
            select(models.Refusal).where(models.Refusal.aggregate_run_id == run.aggregate_run_id)
        ).scalars().all()
        for r in refusals:
            refusal_dicts.append({
                "refusal_id": r.refusal_id, "aggregate_run_id": r.aggregate_run_id,
                "reason": r.reason, "measurement_ids": r.measurement_ids,
                "detail": r.detail, "explanation_fr": r.explanation_fr,
            })

    return {
        "view": view, "scope_organization_id": scope_organization_id, "group_by": group_by,
        "filters": same_batch[0].filters if same_batch else None,
        "computed_at": latest.computed_at.isoformat(),
        "engine_version": latest.engine_version,
        "aggregates": aggregate_dicts,
        "refusals": refusal_dicts,
        "stale": True,
    }


def _official_jci_facts(db: Session) -> list[dict]:
    rows = db.execute(select(models.Measurement).where(models.Measurement.layer == "OFFICIAL_JCI_FACT")).scalars().all()
    return [mo_builder.row_to_measurement_object(db, r) for r in rows]


def _displayed_quality_issues(db: Session) -> list[dict]:
    rows = db.execute(select(models.QualityIssue).where(models.QualityIssue.displayed.is_(True))).scalars().all()
    return [
        {"issue_id": r.issue_id, "kind": r.kind, "subject": r.subject,
         "values": r.values, "resolution_status": r.resolution_status}
        for r in rows
    ]


def get_dashboard(db: Session, *, view: str, scope_organization_id: str | None,
                   group_by: str = "network", filters: dict | None = None) -> dict:
    try:
        result = run_aggregation(db, view=view, scope_organization_id=scope_organization_id,
                                  group_by=group_by, filters=filters)
    except AggregationError:
        raise
    except Exception:
        db.rollback()
        logger.exception(
            "Echec du moteur pendant le calcul du tableau de bord (vue=%s, scope=%s, group_by=%s) "
            "-- affichage de la derniere execution reussie.", view, scope_organization_id, group_by,
        )
        result = _last_successful_run(db, view=view, scope_organization_id=scope_organization_id, group_by=group_by)
        if result is None:
            raise

    if view == "global":
        result["official_jci_facts"] = _official_jci_facts(db)
        result["quality_issues"] = _displayed_quality_issues(db)

    return result


# ---------------------------------------------------------------------------
# Annexe A #12 — POST /aggregations/check-pair
# ---------------------------------------------------------------------------
def check_pair(db: Session, measurement_id_a: str, measurement_id_b: str) -> dict:
    row_a = db.get(models.Measurement, measurement_id_a)
    row_b = db.get(models.Measurement, measurement_id_b)
    if not row_a or not row_b:
        missing = measurement_id_a if not row_a else measurement_id_b
        raise AggregationError(f"mesure introuvable : {missing}", status_code=404)

    mo_a = mo_builder.row_to_measurement_object(db, row_a)
    mo_b = mo_builder.row_to_measurement_object(db, row_b)
    refusal = engine_service.pair_compatibility(mo_a, mo_b)
    return {
        "compatible": refusal is None,
        "refusal": None if refusal is None else {
            "reason": refusal.reason, "measurement_ids": refusal.measurement_ids,
            "detail": refusal.detail, "explanation_fr": refusal.explain(),
        },
    }


# ---------------------------------------------------------------------------
# Annexe A #11 — GET /trace/{measurement_id}
# ---------------------------------------------------------------------------
def trace_measurement(db: Session, measurement_id: str) -> dict:
    root = db.get(models.Measurement, measurement_id)
    if not root:
        raise AggregationError(f"mesure introuvable : {measurement_id}", status_code=404)

    visited: set[str] = set()
    entries: list[dict] = []
    chain_state = {"complete": True}

    def _resolve(mid: str) -> None:
        if mid in visited:
            return
        visited.add(mid)
        m = db.get(models.Measurement, mid)
        if not m:
            chain_state["complete"] = False
            entries.append({
                "measurement_id": mid, "resolved": False,
                "note": "chaine incomplete : mesure introuvable (CTL-TRACE, dev-brief.md Annexe B)",
            })
            return

        parents = db.execute(
            select(models.MeasurementParent)
            .where(models.MeasurementParent.measurement_id == mid)
            .order_by(models.MeasurementParent.position)
        ).scalars().all()

        if parents:
            for p in parents:
                _resolve(p.parent_measurement_id)
            entries.append({
                "measurement_id": mid, "resolved": True, "kind": "aggregate",
                "measurement": mo_builder.row_to_measurement_object(db, m),
                "parent_measurement_ids": [p.parent_measurement_id for p in parents],
            })
            return

        leaf_entry: dict[str, Any] = {
            "measurement_id": mid, "resolved": True, "kind": "leaf",
            "measurement": mo_builder.row_to_measurement_object(db, m),
        }
        if m.layer == "OFFICIAL_JCI_FACT" or not m.submission_id:
            leaf_entry["submission"] = None
            leaf_entry["ctl_raw_ok"] = None
            entries.append(leaf_entry)
            return

        submission = db.get(models.Submission, m.submission_id)
        if not submission:
            chain_state["complete"] = False
            leaf_entry["submission"] = None
            leaf_entry["note"] = "chaine incomplete : submission introuvable (CTL-TRACE)"
            entries.append(leaf_entry)
            return

        # CTL-RAW (RI-07, dev-brief.md section 5) : le texte n'a jamais ete modifie.
        ctl_raw_ok = hashlib.sha256(submission.raw_text.encode("utf-8")).hexdigest() == submission.raw_text_sha256
        quote = m.source_quote
        quote_found = bool(quote) and quote in submission.raw_text
        span = m.source_span if isinstance(m.source_span, dict) else {}
        start, end = span.get("start"), span.get("end")
        if (start is None or end is None) and quote_found:
            start = submission.raw_text.index(quote)
            end = start + len(quote)

        leaf_entry["submission"] = {
            "submission_id": submission.submission_id,
            "raw_text": submission.raw_text,
            "quote": quote,
            "quote_found_in_raw_text": quote_found,
            "highlight_span": {"start": start, "end": end} if start is not None and end is not None else None,
        }
        leaf_entry["ctl_raw_ok"] = ctl_raw_ok
        if not ctl_raw_ok:
            chain_state["complete"] = False
        entries.append(leaf_entry)

    _resolve(measurement_id)

    return {
        "measurement_id": measurement_id,
        "chain_complete": chain_state["complete"],
        "entries": entries,
    }
