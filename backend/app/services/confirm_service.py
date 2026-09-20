"""Construction et validation des Measurement Objects a la confirmation de la
fiche (Annexe A #5, dev-brief.md section 3.2 ; revu par impact-science.md,
D-23 a D-31).

Principe : pour chaque chiffre retenu, on construit un ou plusieurs
Measurement Object complets (forme imbriquee de measurement-object.schema.json),
on les fait passer par les DEUX validateurs reutilises tels quels (section 8),
puis par equivalence_key() et eligibility() du moteur -- CE DERNIER calcule la
cle d'equivalence et l'eligibilite, jamais l'IA (RI-03). Ce n'est qu'apres
coup que le MO est eclate en colonnes pour la table `measurement` (section 2.8).

Un candidat dont la population resultante est "mixed" (interne + externe)
produit DEUX Measurement Objects distincts, jamais un seul chiffre etiquete
"mixed" (D-26, AC-30) : R7 (membres JCI et public externe jamais additionnes)
serait sinon impossible a faire respecter par le moteur en aval.

Les ressources (benevoles JCI, heures de benevolat) ne viennent plus d'un
candidat numerique generique : ce sont desormais des champs dedies et
obligatoires de la fiche de confirmation (D-28, D-30), analogues a
project.name/period. Le nombre de benevoles JCI devient sa propre mesure
(metric_code=VOLUNTEERS, internal_external=internal) ; les heures de
benevolat sont pre-calculees (benevoles x duree) sauf correction du SG.

A5 (impact-science.md D-25 a D-28) : la classification confirmee par le SG
(familles d'activite, Areas + principale, RISE, ODD + justification) est
validee EN BLOC avant toute ecriture -- exactement 1 Area primary, RISE
coherent avec la presence de Community Impact (CI) dans les Areas, au moins
un pilier si RISE=yes, un libelle pour toute famille "Autre", et une
justification non vide pour chaque ODD retenu avec exactement 1 principal.
La regle dure RI-10/D-26 ("public 100% interne => jamais CI") est appliquee
ici sur la population REELLEMENT CONFIRMEE par le SG (pas seulement sur la
proposition de l'IA, deja verifiee de facon best-effort en amont par
ai_pipeline.validate_mapping_contract) : c'est le dernier verrou avant
ecriture.

Si UN SEUL candidat retenu (ou la classification, ou le projet) echoue la
validation, RIEN n'est ecrit (section 3.2, "si la transaction echoue, rien
n'est ecrit") : cette fonction ne fait aucun commit elle-meme, c'est au
routeur de le faire apres coup.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.services import engine_service, mo_builder, validators_service
from app.services.ai_pipeline import _codes

# D-30 / RI-07 : un chiffre confirme a la fiche mais absent du texte source
# soumis (l'IA ne l'y a pas trouve) n'a pas de citation a donner -- on ne
# fabrique JAMAIS de fausse citation (P1/P9 du schema). On le range alors en
# SEMANTIC_INTERPRETATION / value_status=estimated (methode), jamais en
# LOCAL_REPORTED_FACT (qui exige une citation non vide, P1/P9).
RESOURCE_NO_QUOTE_METHOD = (
    "Valeur saisie ou confirmee directement par l'organisation locale a la "
    "confirmation de la fiche ; absente (ou non retrouvee telle quelle) du "
    "texte source soumis."
)

# Bug constate en demo (2026-09-20) : measurement-object.schema.json impose
# confidence in {H, M, L} partout ou ce champ existe (P1). Le schema JSON
# envoye au modele (ai_pipeline.py) declare deja cet enum comme "required",
# mais rien ne garantit qu'un LLM respecte toujours un enum pour un champ qui
# exprime sa PROPRE incertitude -- il peut renvoyer confidence=null au lieu
# de choisir une valeur quand le texte source est ambigu. Sans ce garde-fou,
# cela fait echouer TOUTE la confirmation de la fiche avec une erreur de
# schema illisible pour le SG ("derivation/1/confidence: None is not one of
# [...]"), alors que la valeur elle-meme (avec sa citation source) reste
# parfaitement valide et ne devrait pas etre perdue pour autant.
#
# Decision (a confirmer/documenter au decision log si le projet continue) :
# une confiance absente est traitee comme la plus BASSE (L), jamais H ni M --
# on ne fabrique jamais une certitude que l'IA n'a pas exprimee (section 2
# des instructions produit, "no unsupported inference"). C'est un defaut
# defensif au point d'ecriture, pas une correction de l'IA elle-meme.
_VALID_CONFIDENCE = {"H", "M", "L"}


def _safe_confidence(value: str | None) -> str:
    return value if value in _VALID_CONFIDENCE else "L"


class ConfirmError(Exception):
    """Erreur de validation bloquante : rien ne doit etre ecrit en base."""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("; ".join(e.get("message", "") for e in errors))


def _index_by_candidate_id(items: list[dict]) -> dict[str, dict]:
    return {it.get("candidate_id"): it for it in items if it.get("candidate_id")}


def _effective_internal_external(mapping: dict, user_input) -> str | None:
    """Valeur internal_external REELLEMENT retenue pour un candidat : celle
    saisie/corrigee par le SG si presente, sinon celle proposee par l'IA.
    Utilisee a la fois pour construire les Measurement Objects et pour la
    regle dure RI-10/D-26 (public 100% interne => jamais CI), qui doit juger
    la population CONFIRMEE, pas seulement proposee."""
    ie = mapping.get("internal_external")
    if user_input is not None and user_input.internal_external:
        ie = user_input.internal_external
    return ie


def _validate_classification(
    axes, taxonomy_content: dict, *, effective_internal_externals: list[str | None],
) -> list[str]:
    """impact-science.md section 6 / D-25 a D-27 : structure des 4 dimensions
    de classification confirmees par le SG. Chaque message nomme le champ
    concerne (AC-16) ; rien n'est ecrit si une seule regle echoue.

    - D-25/AC-27 : au moins une famille d'activite ; libelle obligatoire pour
      toute famille "Autre" (code se terminant par _OTHER, ou "OTHER").
    - D-26/AC-26 : au moins une Area, EXACTEMENT une marquee "primary".
    - D-24/AC-25 : RISE coherent avec la presence de Community Impact (CI)
      parmi les Areas confirmees -- "yes"/"no" seulement si CI est present,
      "not_applicable" sinon ; au moins un pilier si "yes", aucun sinon.
    - D-27/AC-28 : au moins un ODD, EXACTEMENT un principal, une justification
      non vide pour CHAQUE ODD retenu.
    - RI-10/D-26/AC-24 : si Community Impact (CI) est confirme, la population
      CONFIRMEE de tous les candidats connus ne peut pas etre 100% interne.
    """
    errors: list[str] = []
    tc_axes = taxonomy_content["classification_axes"]
    allowed_family = set(_codes(tc_axes["activity_family"]))
    allowed_area = set(_codes(tc_axes["area_of_opportunity"]))
    allowed_rise = set(_codes(taxonomy_content["rise_pillars"]))

    # --- Familles d'activite (D-25 / AC-27) ---
    if not axes.activity_families:
        errors.append("axes.activity_families : au moins une famille d'activite est requise (D-25)")
    for fam in axes.activity_families:
        if fam.code not in allowed_family:
            errors.append(f"axes.activity_families : code inconnu du referentiel : {fam.code!r}")
        elif (fam.code.endswith("_OTHER") or fam.code == "OTHER") and not (fam.other_label or "").strip():
            errors.append(
                f"axes.activity_families : libelle obligatoire pour la famille {fam.code!r} (D-25, AC-27)"
            )

    # --- Areas (D-26 / AC-26) ---
    if not axes.area_of_opportunity:
        errors.append("axes.area_of_opportunity : au moins un domaine d'intervention est requis (R2)")
    for area in axes.area_of_opportunity:
        if area.code not in allowed_area:
            errors.append(f"axes.area_of_opportunity : code inconnu du referentiel : {area.code!r}")
        if area.role not in ("primary", "secondary"):
            errors.append(f"axes.area_of_opportunity : role invalide pour {area.code!r} : {area.role!r}")
    area_codes = {a.code for a in axes.area_of_opportunity}
    primary_areas = [a for a in axes.area_of_opportunity if a.role == "primary"]
    if axes.area_of_opportunity and len(primary_areas) != 1:
        errors.append(
            f"axes.area_of_opportunity : exactement une Area 'primary' est requise "
            f"(trouve : {len(primary_areas)}) (D-26, AC-26)"
        )

    # --- RISE (D-24 / AC-25) ---
    ci_present = "CI" in area_codes
    rise_status = axes.rise.status
    if rise_status not in ("yes", "no", "not_applicable"):
        errors.append(f"axes.rise.status : valeur invalide : {rise_status!r}")
    else:
        if ci_present and rise_status not in ("yes", "no"):
            errors.append(
                "axes.rise.status : Community Impact est coche, RISE doit etre confirme "
                "'yes' ou 'no' (ne peut pas rester vide/'not_applicable') (D-24, AC-25)"
            )
        if not ci_present and rise_status != "not_applicable":
            errors.append(
                "axes.rise.status : ne peut valoir 'yes' ou 'no' que si Community Impact "
                "(CI) est coche parmi les Areas (D-24, AC-25)"
            )
    if rise_status == "yes" and not axes.rise.pillars:
        errors.append("axes.rise.pillars : au moins un pilier est requis quand RISE = 'yes' (D-24, AC-25)")
    if rise_status != "yes" and axes.rise.pillars:
        errors.append("axes.rise.pillars : aucun pilier ne doit etre present quand RISE != 'yes'")
    for code in axes.rise.pillars:
        if code not in allowed_rise:
            errors.append(f"axes.rise.pillars : code inconnu du referentiel : {code!r}")

    # --- ODD (D-27 / AC-28) ---
    if not axes.sdgs:
        errors.append("axes.sdgs : au moins un ODD est requis, avec exactement un principal (R5, D-27)")
    for sdg in axes.sdgs:
        if not (1 <= sdg.goal <= 17):
            errors.append(f"axes.sdgs : numero d'ODD hors 1..17 : {sdg.goal}")
        if not (sdg.justification or "").strip():
            errors.append(f"axes.sdgs : justification obligatoire pour l'ODD {sdg.goal} (D-27, AC-28)")
    primary_sdgs = sum(1 for s in axes.sdgs if s.role == "primary")
    if axes.sdgs and primary_sdgs != 1:
        errors.append(f"axes.sdgs : exactement un ODD 'primary' est requis (trouve : {primary_sdgs}) (AC-28)")

    # --- Regle dure RI-10/D-26 : public 100% interne => jamais CI (AC-24) ---
    # Best-effort au niveau IA (A4), verrou definitif ici sur la population
    # REELLEMENT CONFIRMEE. On ne bloque que si au moins une population est
    # CONNUE (jamais d'invention a partir d'une absence d'information).
    known_ie = [ie for ie in effective_internal_externals if ie in ("internal", "external", "mixed")]
    if ci_present and known_ie and all(ie == "internal" for ie in known_ie):
        errors.append(
            "axes.area_of_opportunity : public interne => Community Impact impossible (D-26, AC-24)"
        )

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
    # D-28/D-30 : ces trois champs sont bloquants. Pydantic (schemas.ConfirmProject,
    # champs non-optionnels) refuse deja une valeur absente/nulle avant meme
    # d'arriver ici (422 nommant le champ, AC-16) ; on ne revalide donc que la
    # coherence entre eux, pas leur simple presence.
    if project.jci_volunteers_count is not None and project.jci_volunteers_count < 0:
        errors.append("project.jci_volunteers_count : une valeur negative n'est pas acceptee")
    if project.activity_duration_hours is not None and project.activity_duration_hours < 0:
        errors.append("project.activity_duration_hours : une valeur negative n'est pas acceptee")
    if project.volunteer_hours is not None and project.volunteer_hours < 0:
        errors.append("project.volunteer_hours : une valeur negative n'est pas acceptee")
    return errors


def _base_geography(organization: "models.Organization") -> dict[str, Any]:
    geography: dict[str, Any] = {
        "local_organization": {"value": organization.name, "layer": "LOCAL_REPORTED_FACT"},
    }
    if organization.country_iso2:
        geography["country_iso2"] = {"value": organization.country_iso2, "layer": "LOCAL_REPORTED_FACT"}
        # geographic_area (SEMANTIC_INTERPRETATION, via geo_mapping) : non branche
        # tant que le vrai compte OL (D-18, country/geographic_area) n'existe pas.
    return geography


def _finalize_mo(mo: dict[str, Any], *, project_id: str) -> dict[str, Any]:
    """Calcule aggregation.{aggregable, equivalence_key, refusal_reason,
    dedup_key} via le moteur -- JAMAIS par l'IA ni a la main (RI-03)."""
    eq_key = engine_service.equivalence_key(mo)
    refusal = engine_service.eligibility(mo)
    mo["aggregation"] = {
        "aggregable": refusal is None,
        "equivalence_key": eq_key,
        "refusal_reason": refusal.reason if refusal else None,
        "dedup_key": project_id,
    }
    return mo


def _build_measurement_object(
    *,
    measurement_id: str,
    extraction_cand: dict,
    mapping: dict,
    value: float | None,
    internal_external: str | None,
    count_type: str | None,
    corrected: bool,
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
    """Construit UN Measurement Object pour une valeur numerique donnee.

    A3 (impact-science.md) : value/internal_external/count_type sont
    desormais des parametres explicites (plus derives en interne d'un seul
    `user_input`) pour permettre a l'appelant de construire deux MO distincts
    a partir d'un meme candidat quand la population resultante est mixte
    (D-26/AC-30) -- jamais un seul chiffre etiquete "mixed".
    """
    value_qualifier = extraction_cand.get("value_qualifier")
    definition_text = extraction_cand.get("definition_text")

    geography = _base_geography(organization)

    derivation = [
        {"step": "extract_number", "rule_id": "EXTRACT-NUM", "agent": "llm_extractor@v0",
         "confidence": _safe_confidence(extraction_cand.get("confidence"))},
        {"step": "classify", "rule_id": "MAP-METRIC", "agent": "llm_classifier@v0",
         "confidence": _safe_confidence(mapping.get("confidence"))},
    ]
    if corrected:
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
            "confidence": _safe_confidence(mapping.get("confidence")),
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
        # measurement-object.schema.json : subject.name doit etre une string si
        # present (pas de null explicite) -- un projet sans nom (name=None,
        # champ facultatif de ConfirmProject) omet donc la cle plutot que
        # d'envoyer null, sinon le validateur rejette (trouve en testant la
        # Phase 3 : un projet sans nom faisait echouer TOUTE confirmation).
        "subject": {"type": "project", "id": project_id, **({"name": project_name} if project_name else {})},
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
        "confidence": _safe_confidence(extraction_cand.get("confidence")),
        "verification_status": "reported",
    }
    if relations:
        mo["relations"] = relations

    return _finalize_mo(mo, project_id=project_id)


def _build_measurement_objects_for_candidate(
    *,
    extraction_cand: dict,
    mapping: dict,
    user_input,
    measurement_ids: dict[str, str],
    project_id: str,
    project_name: str | None,
    reporting_year: int,
    period_start: str | None,
    period_end: str | None,
    taxonomy_refs_snapshot: dict,
    organization: "models.Organization",
    submission: "models.Submission",
    relations: list[dict],
) -> tuple[list[dict], list[str]]:
    """Construit 1 ou 2 MO pour un candidat retenu. Retourne (mos, erreurs) --
    ne leve jamais : les erreurs sont collectees comme partout ailleurs dans
    ce module, pour que confirm_submission puisse toutes les rassembler avant
    de decider si la transaction entiere echoue.

    2 MO quand la population resultante est "mixed" (D-26/AC-30) : deux
    mesures distinctes (internal / external), jamais un seul chiffre.
    """
    candidate_id = extraction_cand.get("candidate_id")
    count_type = mapping.get("count_type")
    internal_external = _effective_internal_external(mapping, user_input)
    corrected = bool(user_input and user_input.corrected)
    if user_input is not None:
        count_type = user_input.count_type or count_type

    if internal_external == "mixed":
        if user_input is None or user_input.value_internal is None or user_input.value_external is None:
            return [], [
                f"candidat {candidate_id} : population mixte (interne + externe) -- "
                "value_internal ET value_external sont tous deux requis (D-26, AC-30). "
                "Un seul chiffre etiquete 'mixed' n'est jamais accepte."
            ]
        mos = [
            _build_measurement_object(
                measurement_id=measurement_ids["INT"], extraction_cand=extraction_cand, mapping=mapping,
                value=user_input.value_internal, internal_external="internal", count_type=count_type,
                corrected=corrected, project_id=project_id, project_name=project_name,
                reporting_year=reporting_year, period_start=period_start, period_end=period_end,
                taxonomy_refs_snapshot=taxonomy_refs_snapshot, organization=organization,
                submission=submission, relations=relations,
            ),
            _build_measurement_object(
                measurement_id=measurement_ids["EXT"], extraction_cand=extraction_cand, mapping=mapping,
                value=user_input.value_external, internal_external="external", count_type=count_type,
                corrected=corrected, project_id=project_id, project_name=project_name,
                reporting_year=reporting_year, period_start=period_start, period_end=period_end,
                taxonomy_refs_snapshot=taxonomy_refs_snapshot, organization=organization,
                submission=submission, relations=relations,
            ),
        ]
        return mos, []

    value = extraction_cand.get("value")
    if user_input is not None and user_input.value is not None:
        value = user_input.value
    mo = _build_measurement_object(
        measurement_id=measurement_ids["SINGLE"], extraction_cand=extraction_cand, mapping=mapping,
        value=value, internal_external=internal_external, count_type=count_type,
        corrected=corrected, project_id=project_id, project_name=project_name,
        reporting_year=reporting_year, period_start=period_start, period_end=period_end,
        taxonomy_refs_snapshot=taxonomy_refs_snapshot, organization=organization,
        submission=submission, relations=relations,
    )
    return [mo], []


def _build_resource_measurements(
    *,
    project_id: str,
    project_name: str | None,
    reporting_year: int,
    period_start: str | None,
    period_end: str | None,
    organization: "models.Organization",
    submission: "models.Submission",
    jci_volunteers_count: float,
    activity_duration_hours: float,
    volunteer_hours: float,
    volunteer_hours_corrected: bool,
    volunteers_extraction: dict | None,
    duration_extraction: dict | None,
) -> list[dict]:
    """D-25/D-28/D-30 -- construit les mesures de RESSOURCES a partir des
    champs dedies de la fiche de confirmation (plus des candidats numeriques
    generiques) :

    - VOLUNTEERS (internal) : le nombre de benevoles JCI confirme.
    - VOLUNTEER_HOURS : benevoles JCI x duree, value_status=calculated avec
      sa formule et sa derivation (AC-29), SAUF si le SG a corrige la valeur
      calculee : dans ce cas la valeur corrigee est stockee telle quelle et
      la derivation de calcul n'est plus appliquee (AC-29).

    volunteers_extraction / duration_extraction : dict optionnel
    {"origin": "quoted"|"inferred", "quote": str|None} tel que produit par le
    pipeline IA (A4) pour project.jci_volunteers_count / activity_duration_hours.
    """
    geography = _base_geography(organization)
    subject = {"type": "project", "id": project_id, **({"name": project_name} if project_name else {})}
    period = {"type": "reporting_year", "start": period_start, "end": period_end, "reporting_year": reporting_year}

    def _quote_of(extraction: dict | None) -> str | None:
        if not extraction:
            return None
        if extraction.get("origin") == "quoted" and extraction.get("quote"):
            return extraction["quote"]
        return None

    volunteers_quote = _quote_of(volunteers_extraction)
    volunteers_id = f"MEAS-{uuid.uuid4().hex[:12]}"

    if volunteers_quote:
        volunteers_mo: dict[str, Any] = {
            "measurement_id": volunteers_id,
            "standard": engine_service.STANDARD,
            "metric_code": "VOLUNTEERS",
            "metric_label_source": "benevoles JCI",
            "definition": {"status": "unknown", "text": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
                            "layer": "LOCAL_REPORTED_FACT"},
            "iaooi_class": {"value": "INPUT", "layer": "SEMANTIC_INTERPRETATION",
                             "standard": "PROPOSED_STANDARD:IAOOI-v0", "rule_id": "INPUT-VOLUNTEERS-JCI",
                             "confidence": "H"},
            "value": jci_volunteers_count,
            "value_status": "extracted",
            "unit": {"code": "person", "dimension": "count"},
            "subject": subject,
            "population": {"target_group": ["JCI_MEMBERS"], "internal_external": "internal",
                            "count_type": "direct", "dedup_basis": "unique_persons"},
            "period": period,
            "geography": geography,
            "layer": "LOCAL_REPORTED_FACT",
            "source": {"origin": "submission", "document_id": submission.submission_id,
                       "quote": volunteers_quote, "submitted_at": submission.submitted_at.isoformat()
                       if submission.submitted_at else None, "language": submission.language},
            "derivation": [{"step": "extract_number", "rule_id": "EXTRACT-NUM", "agent": "llm_extractor@v0",
                             "confidence": "H"}],
            "confidence": "H",
            "verification_status": "reported",
        }
    else:
        volunteers_mo = {
            "measurement_id": volunteers_id,
            "standard": engine_service.STANDARD,
            "metric_code": "VOLUNTEERS",
            "metric_label_source": "benevoles JCI",
            "definition": {"status": "unknown", "text": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
                            "layer": "LOCAL_REPORTED_FACT"},
            "iaooi_class": {"value": "INPUT", "layer": "SEMANTIC_INTERPRETATION",
                             "standard": "PROPOSED_STANDARD:IAOOI-v0", "rule_id": "INPUT-VOLUNTEERS-JCI",
                             "confidence": "M"},
            "value": jci_volunteers_count,
            "value_status": "estimated",
            "method": RESOURCE_NO_QUOTE_METHOD,
            "unit": {"code": "person", "dimension": "count"},
            "subject": subject,
            "population": {"target_group": ["JCI_MEMBERS"], "internal_external": "internal",
                            "count_type": "direct", "dedup_basis": "unique_persons"},
            "period": period,
            "geography": geography,
            "layer": "SEMANTIC_INTERPRETATION",
            "source": {"origin": "submission", "document_id": submission.submission_id,
                       "submitted_at": submission.submitted_at.isoformat()
                       if submission.submitted_at else None, "language": submission.language},
            "derivation": [{"step": "human_validation", "rule_id": "HUMAN-FORM-ENTRY", "agent": "human@ol",
                             "confidence": "M"}],
            "confidence": "M",
            "verification_status": "reported",
        }
    volunteers_mo = _finalize_mo(volunteers_mo, project_id=project_id)

    expected_hours = jci_volunteers_count * activity_duration_hours
    hours_matches_formula = (not volunteer_hours_corrected) and abs(volunteer_hours - expected_hours) < 1e-9
    hours_id = f"MEAS-{uuid.uuid4().hex[:12]}"

    if hours_matches_formula:
        # AC-29 : heures pre-calculees, value_status=calculated, formule +
        # derivation qui la porte (P2/V4 du schema : calculated impose
        # SEMANTIC_INTERPRETATION + formula + inputs).
        hours_mo: dict[str, Any] = {
            "measurement_id": hours_id,
            "standard": engine_service.STANDARD,
            "metric_code": "VOLUNTEER_HOURS",
            "metric_label_source": "heures de benevolat (calcule)",
            "definition": {"status": "specified",
                           "text": "Benevoles JCI x duree de l'activite en heures",
                           "layer": "SEMANTIC_INTERPRETATION"},
            "iaooi_class": {"value": "INPUT", "layer": "SEMANTIC_INTERPRETATION",
                             "standard": "PROPOSED_STANDARD:IAOOI-v0", "rule_id": "CALC-VOLUNTEER-HOURS",
                             "confidence": "H"},
            "value": expected_hours,
            "value_status": "calculated",
            "formula": "VOLUNTEERS(internal) x activity_duration_hours",
            "inputs": [volunteers_id],
            "unit": {"code": "hour", "dimension": "duration"},
            "subject": subject,
            "population": {"target_group": ["JCI_MEMBERS"], "internal_external": "internal",
                            "count_type": "direct", "dedup_basis": "unique_persons"},
            "period": period,
            "geography": geography,
            "layer": "SEMANTIC_INTERPRETATION",
            # (A7) origin="submission", PAS "engine" : cette mesure est calculee
            # UNE FOIS a la confirmation de la fiche (benevoles x duree, D-30),
            # ce n'est PAS un agregat produit par aggregation_engine.aggregate()
            # (celui-la seul justifie l'exclusion "source_origin == 'engine'"
            # d'aggregation_service._select_candidate_rows, qui sert a ne
            # jamais reinjecter un agregat deja calcule comme mesure d'entree).
            # Bug latent corrige ici (A7) : avec "engine", VOLUNTEER_HOURS
            # etait exclu de TOUTE agregation, pour TOUS les projets, depuis
            # A3 -- jamais detecte faute de test bout-en-bout sur le tableau
            # de bord avant test_a7.py.
            "source": {"origin": "submission", "document_id": submission.submission_id,
                       "submitted_at": submission.submitted_at.isoformat()
                       if submission.submitted_at else None},
            "derivation": [{
                "step": "calculate", "rule_id": "CALC-VOLUNTEER-HOURS", "agent": "rules@v0",
                "input_refs": [volunteers_id], "confidence": "H",
            }],
            "confidence": "H",
            "verification_status": "reported",
        }
    else:
        # D-30 : le SG a corrige la valeur calculee -- la valeur corrigee est
        # stockee telle quelle, la derivation de calcul n'est plus appliquee
        # (AC-29). Meme regle "jamais de fausse citation" que pour VOLUNTEERS
        # sans citation : SEMANTIC_INTERPRETATION / estimated / methode.
        hours_mo = {
            "measurement_id": hours_id,
            "standard": engine_service.STANDARD,
            "metric_code": "VOLUNTEER_HOURS",
            "metric_label_source": "heures de benevolat (corrige par l'OL)",
            "definition": {"status": "unknown", "text": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
                           "layer": "LOCAL_REPORTED_FACT"},
            "iaooi_class": {"value": "INPUT", "layer": "SEMANTIC_INTERPRETATION",
                             "standard": "PROPOSED_STANDARD:IAOOI-v0", "rule_id": "INPUT-VOLUNTEER-HOURS",
                             "confidence": "M"},
            "value": volunteer_hours,
            "value_status": "estimated",
            "method": RESOURCE_NO_QUOTE_METHOD + " Remplace la valeur calculee (benevoles x duree).",
            "unit": {"code": "hour", "dimension": "duration"},
            "subject": subject,
            "population": {"target_group": ["JCI_MEMBERS"], "internal_external": "internal",
                            "count_type": "direct", "dedup_basis": "unique_persons"},
            "period": period,
            "geography": geography,
            "layer": "SEMANTIC_INTERPRETATION",
            "source": {"origin": "submission", "document_id": submission.submission_id,
                       "submitted_at": submission.submitted_at.isoformat()
                       if submission.submitted_at else None, "language": submission.language},
            "derivation": [{"step": "human_validation", "rule_id": "HUMAN-CONFIRM", "agent": "human@ol",
                             "confidence": "H"}],
            "confidence": "H",
            "verification_status": "reported",
        }
    hours_mo = _finalize_mo(hours_mo, project_id=project_id)

    return [volunteers_mo, hours_mo]


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
    # NOTE (A5) : pas de rejet ici si included_ids est vide -- un projet sans
    # aucun chiffre generique extrait (texte purement qualitatif) reste
    # confirmable des lors que les mesures de RESSOURCES (benevoles JCI,
    # heures, toujours construites plus bas, D-28) sont valides. Le vrai
    # garde-fou "rien a ecrire du tout" est le controle sur `all_mos` a la
    # fin de cette fonction, apres l'ajout des mesures de ressources.

    # A5 : la population REELLEMENT confirmee (IA + eventuelle correction SG)
    # de chaque candidat retenu, calculee AVANT toute validation, pour que la
    # regle dure RI-10/D-26 (AC-24) juge les donnees confirmees, pas la seule
    # proposition de l'IA.
    effective_ies = [
        _effective_internal_external(mapping_by_id[cid], user_by_id.get(cid))
        for cid in included_ids
    ]

    errors: list[dict] = []
    errors += [{"message": m} for m in _validate_classification(
        payload.axes, taxonomy_content, effective_internal_externals=effective_ies,
    )]
    errors += [{"message": m} for m in _validate_project(payload.project)]
    if errors:
        raise ConfirmError(errors)

    # Identifiants generes a l'avance (SINGLE, INT, EXT) : un candidat non
    # mixte n'utilise que SINGLE, un candidat mixte que INT+EXT. Les ids non
    # utilises sont simplement ignores (cf. _build_measurement_objects_for_candidate).
    ids_by_candidate: dict[str, dict[str, str]] = {
        cid: {"SINGLE": f"MEAS-{uuid.uuid4().hex[:12]}",
              "INT": f"MEAS-{uuid.uuid4().hex[:12]}",
              "EXT": f"MEAS-{uuid.uuid4().hex[:12]}"}
        for cid in included_ids
    }

    def _primary_measurement_id(cid: str) -> str:
        """Identifiant utilise comme cible d'une relation vers ce candidat.
        Choix simplificateur documente : pour un candidat mixte (rare en
        relation avec un autre candidat), on pointe vers sa part interne --
        cas non couvert par les criteres d'acceptation A3."""
        return ids_by_candidate[cid]["INT"] if (
            (user_by_id.get(cid) and user_by_id[cid].internal_external == "mixed")
            or mapping_by_id.get(cid, {}).get("internal_external") == "mixed"
        ) else ids_by_candidate[cid]["SINGLE"]

    project_id = f"PRJ-{uuid.uuid4().hex[:12]}"
    # taxonomy_refs (snapshot pose sur CHAQUE mesure, a titre informatif) est
    # une forme FIGEE par measurement-object.schema.json (additionalProperties
    # false : seules area_of_opportunity/programme/rise_pillars/activity_type/
    # target_group/sdgs/layer sont autorisees). Le role primary/secondary par
    # Area, le libelle "Autre" par famille et la justification par ODD --
    # toutes nouvelles avec impact-science.md -- sont donc stockes dans les
    # tables project_* dediees (ecrites plus bas), jamais dans ce schema
    # immuable : on ne le modifie pas (regle de reutilisation, Etape 0).
    taxonomy_refs_snapshot = {
        "area_of_opportunity": [a.code for a in payload.axes.area_of_opportunity],
        "programme": [],  # DEPRECATED (D-23) -- toujours vide desormais
        "rise_pillars": list(payload.axes.rise.pillars),
        "sdgs": [{"goal": s.goal, "role": s.role} for s in payload.axes.sdgs],
        "activity_type": [f.code for f in payload.axes.activity_families],  # alias derive (compat)
    }

    all_mos: dict[str, dict] = {}
    validation_errors: list[dict] = []
    for cid in included_ids:
        relations_for_candidate = []
        for rel in relations_raw:
            other = None
            if rel.get("candidate_id_a") == cid:
                other = rel.get("candidate_id_b")
            elif rel.get("candidate_id_b") == cid:
                other = rel.get("candidate_id_a")
            if other and other in ids_by_candidate:
                relations_for_candidate.append({
                    "relation_type": rel.get("relation_type"),
                    "measurement_id": _primary_measurement_id(other),
                })

        mos, cand_errors = _build_measurement_objects_for_candidate(
            extraction_cand=extraction_by_id[cid],
            mapping=mapping_by_id[cid],
            user_input=user_by_id.get(cid),
            measurement_ids=ids_by_candidate[cid],
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
        if cand_errors:
            validation_errors += [{"candidate_id": cid, "message": m} for m in cand_errors]
            continue
        for mo in mos:
            ok, detail = validators_service.is_valid(mo)
            if not ok:
                # validate_measurement_object() renvoie des paires (code, message) ;
                # validate_provenance() renvoie des triplets (code, path, message).
                # Les deux formes sont normalisees ici (cf. docs/technical/
                # validate_measurement_objects.py:validate_one et Tier 2/validate_provenance.py).
                for code, msg in detail["schema_errors"]:
                    validation_errors.append({"candidate_id": cid, "message": f"{code}: {msg}"})
                for code, path, msg in detail["provenance_blocking"]:
                    validation_errors.append({"candidate_id": cid, "message": f"{code} {path}: {msg}"})
            else:
                all_mos[mo["measurement_id"]] = mo

    # --- Ressources (D-25/D-28/D-30) : benevoles JCI + heures, champs dedies
    # de la fiche, plus des candidats numeriques generiques. ---
    volunteers_extraction = (structured.payload.get("project") or {}).get("jci_volunteers_count")
    duration_extraction = (structured.payload.get("project") or {}).get("activity_duration_hours")
    resource_mos = _build_resource_measurements(
        project_id=project_id,
        project_name=payload.project.name,
        reporting_year=payload.project.reporting_year,
        period_start=payload.project.period_start,
        period_end=payload.project.period_end,
        organization=organization,
        submission=submission,
        jci_volunteers_count=payload.project.jci_volunteers_count,
        activity_duration_hours=payload.project.activity_duration_hours,
        volunteer_hours=payload.project.volunteer_hours,
        volunteer_hours_corrected=payload.project.volunteer_hours_corrected,
        volunteers_extraction=volunteers_extraction,
        duration_extraction=duration_extraction,
    )
    for mo in resource_mos:
        ok, detail = validators_service.is_valid(mo)
        if not ok:
            for code, msg in detail["schema_errors"]:
                validation_errors.append({"candidate_id": "RESOURCES", "message": f"{code}: {msg}"})
            for code, path, msg in detail["provenance_blocking"]:
                validation_errors.append({"candidate_id": "RESOURCES", "message": f"{code} {path}: {msg}"})
        else:
            all_mos[mo["measurement_id"]] = mo

    if validation_errors:
        raise ConfirmError(validation_errors)
    if not all_mos:
        raise ConfirmError([{"message": "aucune mesure valide a ecrire : rien a confirmer"}])

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
        activity_duration_hours=payload.project.activity_duration_hours,
        rise_status=payload.axes.rise.status,  # D-24 -- deja valide coherent avec CI ci-dessus
        programme_confirmed=True,
        taxonomy_version=taxonomy_release.version,
        confirmed_by=payload.confirmed_by,
        confirmed_at=now,
    )
    db.add(project)

    for area in payload.axes.area_of_opportunity:
        db.add(models.ProjectAreaOfOpportunity(project_id=project_id, code=area.code, role=area.role,
                                                confirmed_by=payload.confirmed_by, confirmed_at=now))
    for fam in payload.axes.activity_families:
        db.add(models.ProjectActivityFamily(project_id=project_id, code=fam.code, other_label=fam.other_label,
                                             confirmed_by=payload.confirmed_by, confirmed_at=now))
    for code in payload.axes.rise.pillars:
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
    for measurement_id, mo in all_mos.items():
        row = mo_builder.mo_to_measurement_row(
            mo,
            submission_id=submission.submission_id,
            project_id=project_id,
            organization_id=submission.organization_id,
            taxonomy_version=taxonomy_release.version,
        )
        db.add(row)
        measurement_rows[measurement_id] = row
    db.flush()

    for measurement_id, mo in all_mos.items():
        row = measurement_rows[measurement_id]
        for pos, step in enumerate(mo["derivation"]):
            db.add(models.Derivation(
                measurement_id=row.measurement_id, position=pos,
                step=step.get("step"), rule_id=step.get("rule_id"),
                agent=step.get("agent"), input_refs=step.get("input_refs"),
                confidence=step.get("confidence"),
            ))
        for rel in mo.get("relations", []):
            db.add(models.MeasurementRelation(
                measurement_id=row.measurement_id,
                relation_type=rel["relation_type"],
                target_measurement_id=rel["measurement_id"],
            ))

    submission.pipeline_status = "confirmed"
    return project_id, list(all_mos.keys())
