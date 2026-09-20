"""Conversion Measurement Object <-> colonnes de la table `measurement`, dans
les deux sens.

Ce module est le point unique qui sait comment un MO (forme imbriquee de
measurement-object.schema.json) se range dans le schema plat de la base
(dev-brief.md section 2.8 et Annexe B). Il est utilise :

- a l'ecriture, par confirm_service.py (fiche confirmee -> mesures locales)
  et aggregation_service.py (agregats du moteur -> mesures calculees) ;
- a la lecture, par les points d'entree qui doivent rendre un MO complet :
  GET /measurements/{id}, GET /projects/{id}, GET /trace/{id},
  POST /aggregations/check-pair, et aggregation_service.py qui doit
  reconstituer les MO candidats avant de les passer au moteur.

Aucune regle metier n'est decidee ici : ce module range des donnees deja
produites (par l'IA, l'utilisateur, ou le moteur) dans des colonnes, et les
en ressort. Toute regle d'eligibilite ou d'agregation reste dans
aggregation_engine.py, appele via engine_service.py.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def _omit_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


# ---------------------------------------------------------------------------
# MO (dict) -> ligne `measurement` (et ses tables filles, ecrites a part)
# ---------------------------------------------------------------------------
def mo_to_measurement_row(
    mo: dict,
    *,
    submission_id: str | None,
    project_id: str | None,
    organization_id: str | None,
    taxonomy_version: str | None,
) -> models.Measurement:
    """Construit la ligne `measurement` a partir d'un MO complet et valide.

    N'ecrit PAS les tables filles (derivation, measurement_relation,
    measurement_parent) : l'appelant les ajoute apres avoir flush() cette
    ligne, pour satisfaire les FK (voir confirm_service.py et
    aggregation_service.py pour l'ordre exact).
    """
    definition = mo.get("definition") or {}
    iaooi = mo.get("iaooi_class") or {}
    unit = mo.get("unit") or {}
    subject = mo.get("subject") or {}
    population = mo.get("population") or {}
    period = mo.get("period") or {}
    source = mo.get("source") or {}
    aggregation = mo.get("aggregation") or {}

    aggregable = aggregation.get("aggregable")
    agg_aggregable_text = "true" if aggregable is True else ("false" if aggregable is False else None)

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
        definition_source_ref=definition.get("source_ref"),
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
        unit_currency_code=unit.get("currency_code"),
        unit_sub_code=unit.get("sub_code"),
        unit_normalization=mo.get("unit_normalization"),
        formula=mo.get("formula"),
        inputs=mo.get("inputs"),
        method=mo.get("method"),
        assumptions=mo.get("assumptions"),
        conflicting_values=mo.get("conflicting_values"),
        subject_type=subject.get("type"),
        subject_id=subject.get("id"),
        subject_name=subject.get("name"),
        pop_internal_external=population.get("internal_external"),
        pop_count_type=population.get("count_type"),
        pop_dedup_basis=population.get("dedup_basis"),
        pop_target_group=population.get("target_group"),
        pop_base_population=population.get("base_population"),
        pop_attributes=population.get("attributes"),
        period_type=period.get("type"),
        period_start=period.get("start"),
        period_end=period.get("end"),
        period_reporting_year=period.get("reporting_year"),
        geography=mo.get("geography"),
        layer=mo["layer"],
        source_origin=source.get("origin"),
        source_document_id=source.get("document_id"),
        source_page=source.get("page"),
        source_section=source.get("section"),
        source_quote=source.get("quote"),
        source_span=source.get("span"),
        source_submitted_at=source.get("submitted_at"),
        source_language=source.get("language"),
        confidence=mo.get("confidence"),
        verification_status=mo["verification_status"],
        evidence_refs=mo.get("evidence_refs"),
        checks_passed=mo.get("checks_passed"),
        checks_failed=mo.get("checks_failed"),
        dq_refs=mo.get("dq_refs"),
        flag=mo.get("flag"),
        validated_by=mo.get("validated_by"),
        validated_at=mo.get("validated_at"),
        agg_equivalence_key=aggregation.get("equivalence_key"),
        agg_aggregable=agg_aggregable_text,
        agg_refusal_reason=aggregation.get("refusal_reason"),
        agg_dedup_key=aggregation.get("dedup_key"),
        agg_suspected_duplicate_of=aggregation.get("suspected_duplicate_of"),
        agg_coverage=aggregation.get("coverage"),
    )


# ---------------------------------------------------------------------------
# ligne `measurement` (+ tables filles) -> MO (dict)
# ---------------------------------------------------------------------------
def _base_measurement_object(row: models.Measurement) -> dict:
    """Partie du MO qui ne depend que de la ligne `measurement` elle-meme
    (aucune requete DB). Partagee par row_to_measurement_object() et son
    pendant par lot rows_to_measurement_objects() ci-dessous (correctif perf
    2026-09-20, D-37) -- une seule construction, jamais deux implementations
    qui pourraient diverger."""
    mo: dict[str, Any] = {
        "measurement_id": row.measurement_id,
        "standard": row.standard,
        "metric_code": row.metric_code,
        "metric_label_source": row.metric_label_source,
        "definition": _omit_none({
            "status": row.definition_status,
            "text": row.definition_text,
            "layer": row.definition_layer,
            "source_ref": row.definition_source_ref,
        }),
        "iaooi_class": _omit_none({
            "value": row.iaooi_value,
            "layer": row.iaooi_layer,
            "standard": row.iaooi_standard,
            "rule_id": row.iaooi_rule_id,
            "confidence": row.iaooi_confidence,
        }),
        "value": row.value if row.value is None else float(row.value),
        "value_status": row.value_status,
        "unit": _omit_none({
            "code": row.unit_code,
            "dimension": row.unit_dimension,
            "currency_code": row.unit_currency_code,
            "sub_code": row.unit_sub_code,
        }),
        "subject": _omit_none({
            "type": row.subject_type,
            "id": row.subject_id,
            "name": row.subject_name,
        }),
        "population": _omit_none({
            "internal_external": row.pop_internal_external,
            "count_type": row.pop_count_type,
            "dedup_basis": row.pop_dedup_basis,
            "target_group": row.pop_target_group,
            "base_population": row.pop_base_population,
            "attributes": row.pop_attributes,
        }),
        "period": {
            "type": row.period_type,
            "start": row.period_start,
            "end": row.period_end,
            "reporting_year": row.period_reporting_year,
        },
        "layer": row.layer,
        "source": _omit_none({
            "origin": row.source_origin,
            "document_id": row.source_document_id,
            "page": row.source_page,
            "section": row.source_section,
            "quote": row.source_quote,
            "span": row.source_span,
            "submitted_at": row.source_submitted_at,
            "language": row.source_language,
        }),
        "verification_status": row.verification_status,
        "aggregation": {
            "aggregable": {"true": True, "false": False}.get(row.agg_aggregable),
            "equivalence_key": row.agg_equivalence_key,
            "refusal_reason": row.agg_refusal_reason,
            **_omit_none({
                "dedup_key": row.agg_dedup_key,
                "suspected_duplicate_of": row.agg_suspected_duplicate_of,
                "coverage": row.agg_coverage,
            }),
        },
    }

    if row.value_qualifier is not None:
        mo["value_qualifier"] = row.value_qualifier
    if row.value_range is not None:
        mo["value_range"] = row.value_range
    if row.source_wording_class is not None:
        mo["source_wording_class"] = row.source_wording_class
    if row.taxonomy_refs is not None:
        mo["taxonomy_refs"] = row.taxonomy_refs
    if row.unit_normalization is not None:
        mo["unit_normalization"] = row.unit_normalization
    if row.formula is not None:
        mo["formula"] = row.formula
    if row.inputs is not None:
        mo["inputs"] = row.inputs
    if row.method is not None:
        mo["method"] = row.method
    if row.assumptions is not None:
        mo["assumptions"] = row.assumptions
    if row.conflicting_values is not None:
        mo["conflicting_values"] = row.conflicting_values
    if row.geography is not None:
        mo["geography"] = row.geography
    if row.confidence is not None:
        mo["confidence"] = row.confidence
    if row.evidence_refs is not None:
        mo["evidence_refs"] = row.evidence_refs
    if row.checks_passed is not None:
        mo["checks_passed"] = row.checks_passed
    if row.checks_failed is not None:
        mo["checks_failed"] = row.checks_failed
    if row.dq_refs is not None:
        mo["dq_refs"] = row.dq_refs
    if row.flag is not None:
        mo["flag"] = row.flag
    if row.validated_by is not None:
        mo["validated_by"] = row.validated_by
    if row.validated_at is not None:
        mo["validated_at"] = row.validated_at.isoformat()

    return mo


def _attach_children(
    mo: dict,
    derivations: list[models.Derivation],
    relations: list[models.MeasurementRelation],
    parents: list[models.MeasurementParent],
) -> dict:
    """Ajoute derivation[]/relations[]/parent_measurement_ids a un MO deja
    construit par _base_measurement_object(), a partir de listes DEJA
    chargees (une fois par mesure dans row_to_measurement_object(), ou en un
    lot pour plusieurs mesures dans rows_to_measurement_objects())."""
    if derivations:
        mo["derivation"] = [
            _omit_none({
                "step": d.step,
                "rule_id": d.rule_id,
                "agent": d.agent,
                "input_refs": d.input_refs,
                "confidence": d.confidence,
            })
            for d in derivations
        ]
    if relations:
        mo["relations"] = [
            _omit_none({
                "relation_type": r.relation_type,
                "measurement_id": r.target_measurement_id,
                "note": r.note,
            })
            for r in relations
        ]
    if parents:
        mo["parent_measurement_ids"] = [p.parent_measurement_id for p in parents]
    return mo


def row_to_measurement_object(db: Session, row: models.Measurement) -> dict:
    """Reconstitue un MO complet a partir d'une ligne `measurement`.

    Inclut `derivation[]`, `relations[]` (measurement_relation) et
    `parent_measurement_ids` (measurement_parent) quand ils existent.
    Ne fait AUCUN calcul metier : les valeurs viennent telles qu'elles ont
    ete stockees (par confirm_service ou aggregation_service), qui sont
    elles-memes le resultat du moteur ou de l'IA+humain.

    Une mesure a la fois -> 3 requetes (derivation/relations/parents). Pour
    plusieurs mesures d'un coup, preferer rows_to_measurement_objects()
    ci-dessous : 3 requetes AU TOTAL (via IN (...)), pas 3 par mesure
    (correctif perf 2026-09-20, D-37 -- ce N+1, repete dans chacun des ~14
    recalculs de "Vue d'ensemble" par aggregation_service.py, etait la cause
    confirmee des 30-50s de chargement releves en direct par KKF)."""
    mo = _base_measurement_object(row)

    derivations = db.execute(
        select(models.Derivation)
        .where(models.Derivation.measurement_id == row.measurement_id)
        .order_by(models.Derivation.position)
    ).scalars().all()
    relations = db.execute(
        select(models.MeasurementRelation).where(models.MeasurementRelation.measurement_id == row.measurement_id)
    ).scalars().all()
    parents = db.execute(
        select(models.MeasurementParent)
        .where(models.MeasurementParent.measurement_id == row.measurement_id)
        .order_by(models.MeasurementParent.position)
    ).scalars().all()

    return _attach_children(mo, derivations, relations, parents)


def rows_to_measurement_objects(db: Session, rows: list[models.Measurement]) -> list[dict]:
    """Version par lot de row_to_measurement_object() : EXACTEMENT le meme
    resultat, mesure par mesure (meme ordre que `rows`), mais 3 requetes SQL
    au total au lieu de 3 par mesure. Ajoutee le 2026-09-20 (D-37) pour
    aggregation_service.py, qui reconstruit tous ses MO candidats a chacun
    des ~14 recalculs d'un chargement de "Vue d'ensemble" -- avec N mesures
    candidates, l'ancien code faisait 3xN requetes x14, celui-ci en fait
    3x14. Ne change aucune regle metier ni aucun champ du MO, seulement la
    facon dont les tables filles sont relues depuis la base."""
    if not rows:
        return []
    ids = [r.measurement_id for r in rows]

    derivations_by_mid: dict[str, list[models.Derivation]] = {}
    for d in db.execute(
        select(models.Derivation)
        .where(models.Derivation.measurement_id.in_(ids))
        .order_by(models.Derivation.measurement_id, models.Derivation.position)
    ).scalars().all():
        derivations_by_mid.setdefault(d.measurement_id, []).append(d)

    relations_by_mid: dict[str, list[models.MeasurementRelation]] = {}
    for r in db.execute(
        select(models.MeasurementRelation).where(models.MeasurementRelation.measurement_id.in_(ids))
    ).scalars().all():
        relations_by_mid.setdefault(r.measurement_id, []).append(r)

    parents_by_mid: dict[str, list[models.MeasurementParent]] = {}
    for p in db.execute(
        select(models.MeasurementParent)
        .where(models.MeasurementParent.measurement_id.in_(ids))
        .order_by(models.MeasurementParent.measurement_id, models.MeasurementParent.position)
    ).scalars().all():
        parents_by_mid.setdefault(p.measurement_id, []).append(p)

    return [
        _attach_children(
            _base_measurement_object(row),
            derivations_by_mid.get(row.measurement_id, []),
            relations_by_mid.get(row.measurement_id, []),
            parents_by_mid.get(row.measurement_id, []),
        )
        for row in rows
    ]
