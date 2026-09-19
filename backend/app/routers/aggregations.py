"""Annexe A #9 à #12 (dev-brief.md) — agrégation branchée sur le moteur,
tableaux de bord, traçabilité, et vérification de compatibilité à la demande.

Aucune règle d'éligibilité/agrégation ici : tout passe par
app.services.aggregation_service, qui lui-même n'appelle que
aggregation_engine.py (moteur réutilisé tel quel, dev-brief.md §8).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AggregationRunRequest, CheckPairRequest
from app.services import aggregation_service

router = APIRouter(tags=["aggregations"])


@router.post("/aggregations/run")
def post_aggregations_run(payload: AggregationRunRequest, db: Session = Depends(get_db)):
    """Annexe A #9 : `{view, scope_organization_id, group_by, filters}` ->
    `{aggregates[], refusals[]}` (chaque agrégat/refus porte son propre
    `aggregate_run_id` — voir aggregation_service.py pour pourquoi il n'y a
    pas un identifiant unique pour tout l'appel : `aggregate.aggregate_run_id`
    est la clé primaire de cette table, dev-brief.md §2.10)."""
    filters = payload.filters.model_dump(exclude_none=True) if payload.filters else {}
    try:
        return aggregation_service.run_aggregation(
            db, view=payload.view, scope_organization_id=payload.scope_organization_id,
            group_by=payload.group_by, filters=filters,
        )
    except aggregation_service.AggregationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/dashboards/{view}")
def get_dashboards_view(
    view: str,
    scope_organization_id: str | None = Query(default=None),
    group_by: str = Query(default="network"),
    reporting_year: int | None = Query(default=None),
    area_of_opportunity: str | None = Query(default=None),
    programme: str | None = Query(default=None),
    sdg: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Annexe A #10. Recalcule à chaque appel (dev-brief.md §3.3 : "le même
    appel aggregate() sert aux trois vues") et persiste le résultat. Si le
    moteur échoue, retombe sur la dernière exécution réussie et marque
    `stale: true` ("on n'affiche jamais un total partiel calculé hors
    moteur"). Vue mondiale uniquement : `official_jci_facts` et
    `quality_issues` (les 4 conflits affichés, dev-brief.md §2.11)."""
    filters = {
        "reporting_year": reporting_year,
        "area_of_opportunity": area_of_opportunity,
        "programme": programme,
        "sdg": sdg,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    try:
        return aggregation_service.get_dashboard(
            db, view=view, scope_organization_id=scope_organization_id, group_by=group_by, filters=filters,
        )
    except aggregation_service.AggregationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/trace/{measurement_id}")
def get_trace(measurement_id: str, db: Session = Depends(get_db)):
    """Annexe A #11 : chaîne complète jusqu'à `raw_text`, citation surlignée,
    résultats de CTL-RAW (empreinte inchangée) et CTL-TRACE (chaque parent se
    résout, sinon "chaîne incomplète" — jamais une erreur serveur)."""
    try:
        return aggregation_service.trace_measurement(db, measurement_id)
    except aggregation_service.AggregationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/aggregations/check-pair")
def post_aggregations_check_pair(payload: CheckPairRequest, db: Session = Depends(get_db)):
    """Annexe A #12 : `{compatible, refusal?}` via `pair_compatibility()`."""
    try:
        return aggregation_service.check_pair(db, payload.measurement_id_a, payload.measurement_id_b)
    except aggregation_service.AggregationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
