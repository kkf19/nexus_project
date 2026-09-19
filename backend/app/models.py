"""Modèles SQLAlchemy — correspondance directe avec dev-brief.md §2.

Règles transverses appliquées ici :
- Aucune colonne numérique de VALEUR n'a de défaut à 0 : NULL = inconnu (RI-02).
- Les énumérations ne sont JAMAIS des contraintes SQL : elles sont vérifiées
  par code contre measurement-object.schema.json et taxonomy.config.json,
  jamais codées en dur ici (dev-brief.md §2, règles transverses).
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


# ---------------------------------------------------------------------------
# §2.1 — référentiel de taxonomie versionné (chargé tel quel, jamais réécrit)
# ---------------------------------------------------------------------------
class TaxonomyRelease(Base):
    __tablename__ = "taxonomy_release"

    version: Mapped[str] = mapped_column(Text, primary_key=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    checksum: Mapped[str] = mapped_column(Text, nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


# ---------------------------------------------------------------------------
# §2.2 — geo_mapping (référentiel manuel pays/NO -> geographic_area, VDX-01)
# ---------------------------------------------------------------------------
class GeoMapping(Base):
    __tablename__ = "geo_mapping"

    country_iso2: Mapped[str] = mapped_column(Text, primary_key=True)
    mapping_version: Mapped[str] = mapped_column(Text, primary_key=True)
    geographic_area: Mapped[str] = mapped_column(Text, nullable=False)  # AFME|AMERICA|ASPAC|EUROPE
    confidence: Mapped[str] = mapped_column(Text, nullable=False)  # H|M|L
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# §2.3 — organization (OL et NO)
# ---------------------------------------------------------------------------
class Organization(Base):
    __tablename__ = "organization"

    organization_id: Mapped[str] = mapped_column(Text, primary_key=True)
    org_type: Mapped[str] = mapped_column(Text, nullable=False)  # local|national (proposé)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_organization_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("organization.organization_id"), nullable=True
    )
    country_iso2: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# §2.4 — app_user (3 rôles actés)
# ---------------------------------------------------------------------------
class AppUser(Base):
    __tablename__ = "app_user"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("organization.organization_id"), nullable=True
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)  # admin_ol|admin_national|board_global


# ---------------------------------------------------------------------------
# §2.5 — submission : la pièce source (RAW), conservée pour toujours (RI-07)
# ---------------------------------------------------------------------------
class Submission(Base):
    __tablename__ = "submission"

    submission_id: Mapped[str] = mapped_column(Text, primary_key=True)
    organization_id: Mapped[str] = mapped_column(Text, ForeignKey("organization.organization_id"), nullable=False)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("app_user.user_id"), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)  # NOT NULL, jamais modifié
    raw_text_sha256: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    pipeline_status: Mapped[str] = mapped_column(Text, nullable=False, default="received")
    pipeline_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Aucune route de mise à jour n'est exposée sur raw_text (RI-07 / CTL-RAW).


# ---------------------------------------------------------------------------
# §2.6 — extraction_candidate : sorties IA non encore confirmées
# ---------------------------------------------------------------------------
class ExtractionCandidate(Base):
    __tablename__ = "extraction_candidate"

    candidate_id: Mapped[str] = mapped_column(Text, primary_key=True)
    submission_id: Mapped[str] = mapped_column(Text, ForeignKey("submission.submission_id"), nullable=False)
    stage: Mapped[str] = mapped_column(Text, nullable=False)  # structured|standardized
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    validation_errors: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# §2.7 — project et ses tables de classification.
# D-07 (3 axes independants) est amende par D-23/D-24/D-25 (2026-09-19) :
#   - activity_family (nouvel axe, 1ere dimension, voir taxonomy.config.json) n'a PAS
#     de table dediee ici -- voir ProjectActivityFamily plus bas.
#   - ProjectProgramme est DEPRECATED (programme = activite, pas un axe).
#   - RISE (ProjectRisePillar) est desormais DEPENDANT de Community Impact,
#     pilote par Project.rise_status (yes/no/not_applicable).
# ---------------------------------------------------------------------------
class Project(Base):
    __tablename__ = "project"

    project_id: Mapped[str] = mapped_column(Text, primary_key=True)
    submission_id: Mapped[str] = mapped_column(Text, ForeignKey("submission.submission_id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(Text, ForeignKey("organization.organization_id"), nullable=False)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)  # #1 — IA puis corrigeable U
    reporting_year: Mapped[int] = mapped_column(Integer, nullable=False)  # #3 — sinon PERIOD_MISMATCH
    period_start: Mapped[str | None] = mapped_column(Text, nullable=True)  # date ISO
    period_end: Mapped[str | None] = mapped_column(Text, nullable=True)

    outcome_status: Mapped[str] = mapped_column(Text, nullable=False)  # measured|pending_follow_up|none (#12, D-20)
    expected_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    rise_status: Mapped[str | None] = mapped_column(Text, nullable=True)  # yes|no|not_applicable (D-24) -- yes seulement si CI dans les Areas
    activity_duration_hours: Mapped[float | None] = mapped_column(Numeric, nullable=True)  # heures (D-30), sert au calcul de VOLUNTEER_HOURS

    programme_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    taxonomy_version: Mapped[str] = mapped_column(Text, ForeignKey("taxonomy_release.version"), nullable=False)
    confirmed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # activity.description (champ #4) = submission.raw_text : pas de colonne dupliquée.


class ProjectAreaOfOpportunity(Base):
    """Axe A. Cardinalité 1..n (R2)."""
    __tablename__ = "project_area_of_opportunity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(Text, ForeignKey("project.project_id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)  # BE|ID|IC|CI
    role: Mapped[str | None] = mapped_column(Text, nullable=True)  # primary|secondary (D-26) -- exactement 1 primary par projet, verifie en code
    layer: Mapped[str] = mapped_column(Text, nullable=False, default="SEMANTIC_INTERPRETATION")
    rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_by: Mapped[str | None] = mapped_column(Text, nullable=True, default="llm_classifier@v0")
    confirmed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProjectProgramme(Base):
    """DEPRECATED (D-23, 2026-09-19) : le programme n'est plus un axe de classification.
    Table conservee pour compatibilite historique, mais plus alimentee par le pipeline IA
    ni par la confirmation a partir de v0.3.0 -- voir classification_axes.activity_family
    (jci_programme_examples) dans taxonomy.config.json. Cardinalite 0..n (R9)."""
    __tablename__ = "project_programme"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(Text, ForeignKey("project.project_id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)  # référentiel programme.values[].code
    layer: Mapped[str] = mapped_column(Text, nullable=False, default="SEMANTIC_INTERPRETATION")
    rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_by: Mapped[str | None] = mapped_column(Text, nullable=True, default="llm_classifier@v0")
    confirmed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProjectRisePillar(Base):
    """Axe B (composante). 1..n si RISE est dans les programmes, sinon 0 (R4)."""
    __tablename__ = "project_rise_pillar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(Text, ForeignKey("project.project_id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)  # REBUILD_ECONOMIES|WORKFORCE|MENTAL_HEALTH
    layer: Mapped[str] = mapped_column(Text, nullable=False, default="SEMANTIC_INTERPRETATION")
    rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_by: Mapped[str | None] = mapped_column(Text, nullable=True, default="llm_classifier@v0")
    confirmed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProjectActivityFamily(Base):
    """Nouvel axe (D-25, 2026-09-19) -- 1ere dimension de classification : QUOI a ete
    fait (former, debattre, planter, jumeler...). Cardinalite 1..n par projet.
    Codes dans classification_axes.activity_family de taxonomy.config.json.
    other_label est obligatoire quand code se termine par _OTHER ou vaut OTHER."""
    __tablename__ = "project_activity_family"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(Text, ForeignKey("project.project_id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    other_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProjectSdg(Base):
    """Axe C. 1..n, exactement 1 `primary` (R5)."""
    __tablename__ = "project_sdg"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(Text, ForeignKey("project.project_id"), nullable=False)
    goal: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..17
    role: Mapped[str] = mapped_column(Text, nullable=False)  # primary|secondary|unknown
    layer: Mapped[str] = mapped_column(Text, nullable=False, default="SEMANTIC_INTERPRETATION")
    rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_by: Mapped[str | None] = mapped_column(Text, nullable=True, default="llm_classifier@v0")
    confirmed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# §2.8 — measurement : table centrale, une ligne = un Measurement Object
# ---------------------------------------------------------------------------
class Measurement(Base):
    __tablename__ = "measurement"

    measurement_id: Mapped[str] = mapped_column(Text, primary_key=True)
    standard: Mapped[str] = mapped_column(Text, nullable=False, default="PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # FK de service : NULL pour les chiffres JCI de référence et les agrégats
    submission_id: Mapped[str | None] = mapped_column(Text, ForeignKey("submission.submission_id"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(Text, ForeignKey("project.project_id"), nullable=True)
    organization_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("organization.organization_id"), nullable=True
    )
    taxonomy_version: Mapped[str | None] = mapped_column(Text, ForeignKey("taxonomy_release.version"), nullable=True)

    metric_code: Mapped[str] = mapped_column(Text, nullable=False)
    metric_label_source: Mapped[str] = mapped_column(Text, nullable=False)  # mots exacts de la source

    definition_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    definition_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    definition_layer: Mapped[str | None] = mapped_column(Text, nullable=True)
    definition_source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)

    iaooi_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    iaooi_layer: Mapped[str | None] = mapped_column(Text, nullable=True)
    iaooi_standard: Mapped[str | None] = mapped_column(Text, nullable=True)
    iaooi_rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    iaooi_confidence: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_wording_class: Mapped[str | None] = mapped_column(Text, nullable=True)
    taxonomy_refs: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    value: Mapped[float | None] = mapped_column(Numeric, nullable=True)  # NULL autorisé, AUCUN défaut (RI-02)
    value_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_qualifier: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_range: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    unit_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_dimension: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_currency_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_sub_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    unit_normalization: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    inputs: Mapped[list | None] = mapped_column(JSON, nullable=True)
    method: Mapped[str | None] = mapped_column(Text, nullable=True)
    assumptions: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflicting_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    subject_type: Mapped[str | None] = mapped_column(Text, nullable=True)  # project|organization|event|program|network
    subject_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    pop_internal_external: Mapped[str | None] = mapped_column(Text, nullable=True)  # IA -> U
    pop_count_type: Mapped[str | None] = mapped_column(Text, nullable=True)  # IA -> U
    pop_dedup_basis: Mapped[str | None] = mapped_column(Text, nullable=True)
    pop_target_group: Mapped[list | None] = mapped_column(JSON, nullable=True)
    pop_base_population: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # requis si percent|ratio
    pop_attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    period_type: Mapped[str | None] = mapped_column(Text, nullable=True)  # reporting_year pour toute mesure de projet
    period_start: Mapped[str | None] = mapped_column(Text, nullable=True)
    period_end: Mapped[str | None] = mapped_column(Text, nullable=True)
    period_reporting_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    geography: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 4 niveaux {value, layer, rule_id, confidence}

    layer: Mapped[str] = mapped_column(Text, nullable=False)

    source_origin: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_document_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_page: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_section: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_quote: Mapped[str | None] = mapped_column(Text, nullable=True)  # sous-chaîne exacte de raw_text
    source_submitted_at: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_language: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_span: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {start, end}

    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)  # H|M|L
    verification_status: Mapped[str] = mapped_column(Text, nullable=False, default="reported")

    evidence_refs: Mapped[list | None] = mapped_column(JSON, nullable=True)
    checks_passed: Mapped[list | None] = mapped_column(JSON, nullable=True)
    checks_failed: Mapped[list | None] = mapped_column(JSON, nullable=True)
    dq_refs: Mapped[list | None] = mapped_column(JSON, nullable=True)
    flag: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    validated_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Calculée par equivalence_key() du moteur — JAMAIS par l'IA (RI-03)
    agg_equivalence_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Résultat de eligibility() du moteur (D-14). Stockée en TEXT ; resérialisée
    # en booléen JSON à l'export (AC-15). Les refus ENTRE deux mesures vont
    # dans `refusal`, pas ici.
    agg_aggregable: Mapped[str | None] = mapped_column(Text, nullable=True)
    agg_refusal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    agg_dedup_key: Mapped[str | None] = mapped_column(Text, nullable=True)  # stocké, JAMAIS lu (D-03)
    agg_suspected_duplicate_of: Mapped[list | None] = mapped_column(JSON, nullable=True)
    agg_coverage: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_measurement_org_year", "organization_id", "period_reporting_year"),
        Index("ix_measurement_equivalence_key", "agg_equivalence_key"),
        Index("ix_measurement_metric_code", "metric_code"),
        Index("ix_measurement_project_id", "project_id"),
        Index("ix_measurement_verification_status", "verification_status"),
    )


# ---------------------------------------------------------------------------
# §2.9 — tables filles de measurement
# ---------------------------------------------------------------------------
class Derivation(Base):
    """Lignage, étape par étape, porté par l'objet."""
    __tablename__ = "derivation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[str] = mapped_column(Text, ForeignKey("measurement.measurement_id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # ordre
    step: Mapped[str] = mapped_column(Text, nullable=False)
    rule_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_refs: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MeasurementRelation(Base):
    """Liens entre chiffres non additionnables (entonnoir, sous-ensemble, etc.)."""
    __tablename__ = "measurement_relation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[str] = mapped_column(Text, ForeignKey("measurement.measurement_id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(Text, nullable=False)
    # subset_of|funnel_stage|same_population_different_metric|restatement_of|conflicts_with
    target_measurement_id: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)


class MeasurementParent(Base):
    """Entrées d'un agrégat (parent_measurement_ids).

    Pas de FK bloquante : l'intégrité est contrôlée par CTL-TRACE, pas par la
    base (dev-brief.md Annexe B — un agrégat de démo peut citer un MO absent
    et doit alors s'afficher "chaîne incomplète", pas planter une contrainte).
    """
    __tablename__ = "measurement_parent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[str] = mapped_column(Text, nullable=False)  # l'agrégat
    parent_measurement_id: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class MeasurementVersion(Base):
    """Règle T3 : toute modification de valeur conserve l'ancienne version."""
    __tablename__ = "measurement_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[str] = mapped_column(Text, ForeignKey("measurement.measurement_id"), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)  # Measurement Object complet
    changed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# §2.10 — aggregate et refusal : résultats du moteur
# ---------------------------------------------------------------------------
class AggregateRun(Base):
    """Décrit l'exécution du moteur qui a produit un agrégat. L'agrégat
    lui-même est un Measurement Object, écrit dans `measurement`."""
    __tablename__ = "aggregate"

    aggregate_run_id: Mapped[str] = mapped_column(Text, primary_key=True)
    measurement_id: Mapped[str] = mapped_column(Text, ForeignKey("measurement.measurement_id"), nullable=False)
    view: Mapped[str] = mapped_column(Text, nullable=False)  # ol|national|global
    scope_organization_id: Mapped[str | None] = mapped_column(Text, nullable=True)  # NULL pour global
    group_by: Mapped[str] = mapped_column(Text, nullable=False)  # subject|geography|network
    group_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    engine_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Refusal(Base):
    """Une ligne par refus du moteur, SANS exception (RI-06). Jamais masqué,
    jamais replié par défaut dans l'interface."""
    __tablename__ = "refusal"

    refusal_id: Mapped[str] = mapped_column(Text, primary_key=True)
    aggregate_run_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("aggregate.aggregate_run_id"), nullable=True
    )  # NULL pour un contrôle de paire à la demande (pair_compatibility)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    measurement_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# §2.11 — quality_issue : registre des 26 conflits documentaires JCI
# ---------------------------------------------------------------------------
class QualityIssue(Base):
    """Charge jci_data_quality_registry_v2.json. displayed=true UNIQUEMENT
    pour DQC-01, DQC-03, DQC-13 et DQC-24 (dev-brief.md §2.11)."""
    __tablename__ = "quality_issue"

    issue_id: Mapped[str] = mapped_column(Text, primary_key=True)
    kind: Mapped[str] = mapped_column(Text, nullable=False)  # conflict|visual
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    values: Mapped[list] = mapped_column(JSON, nullable=False)  # toutes les valeurs, aucune choisie
    resolution_status: Mapped[str] = mapped_column(Text, nullable=False, default="UNRESOLVED")
    displayed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
