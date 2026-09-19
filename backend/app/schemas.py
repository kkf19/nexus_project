"""Schémas Pydantic pour les entrées/sorties de l'API.

À ne pas confondre avec measurement-object.schema.json, qui reste LA seule
source de vérité pour la forme d'un Measurement Object (dev-brief.md §8).
"""
from __future__ import annotations

from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    raw_text: str
    # Provisoire : il n'y a pas encore de compte OL connecté (Phase 1).
    # Sera remplacé par l'identité du compte authentifié.
    organization_id: str = "DEMO-OL"
    user_id: str = "DEMO-USER"


class SubmissionOut(BaseModel):
    submission_id: str
    pipeline_status: str

    class Config:
        from_attributes = True


class SubmissionDetail(BaseModel):
    submission_id: str
    pipeline_status: str
    pipeline_error: str | None
    raw_text: str

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    project_id: str
    name: str | None
    reporting_year: int
    outcome_status: str

    class Config:
        from_attributes = True


class MeasurementOut(BaseModel):
    measurement_id: str
    metric_code: str
    value: float | None
    value_status: str | None
    layer: str
    verification_status: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Annexe A #5 — POST /submissions/{id}/confirm (dev-brief.md section 3.2,
# revu par impact-science.md D-23 a D-31)
#
# A5 : la fiche de confirmation suit desormais les 4 dimensions de
# impact-science.md section 6, chacune confirmee explicitement par le SG (le
# "role" primary/secondary d'une Area, le libelle "Autre" d'une famille, le
# statut RISE, la justification de chaque ODD ne sont plus deductibles d'une
# simple liste de codes -- ils doivent etre soumis tels quels, D-28). Ceci
# remplace la forme Phase 3 (liste de codes bruts + 4 cases a cocher C1-C4) :
# rupture de contrat assumee, le frontend A6 doit envoyer cette nouvelle forme.
# ---------------------------------------------------------------------------
class ConfirmActivityFamily(BaseModel):
    code: str
    other_label: str | None = None  # obligatoire si code = *_OTHER ou OTHER (D-25, AC-27)


class ConfirmArea(BaseModel):
    code: str
    role: str  # primary|secondary -- exactement 1 "primary" par projet (D-26, AC-26)


class ConfirmRise(BaseModel):
    # yes|no|not_applicable -- "yes"/"no" seulement si Community Impact (CI)
    # est parmi les Areas confirmees, "not_applicable" sinon (D-24, AC-25).
    status: str = "not_applicable"
    pillars: list[str] = []  # >=1 requis si status == "yes"


class ConfirmSdg(BaseModel):
    goal: int
    role: str  # primary|secondary|unknown -- exactement 1 "primary" (R5, D-27)
    justification: str  # phrase justificative -- obligatoire pour tout ODD retenu (D-27, AC-28)


class ConfirmAxes(BaseModel):
    activity_families: list[ConfirmActivityFamily] = []  # >=1 requis (D-25)
    area_of_opportunity: list[ConfirmArea] = []           # >=1 requis, 1 seule "primary" (D-26)
    programme: list[str] = []             # DEPRECATED (D-23) -- conserve pour compatibilite
                                           # historique de lecture, plus jamais alimente ni exploite.
    rise: ConfirmRise = ConfirmRise()     # D-24
    sdgs: list[ConfirmSdg] = []           # >=1, exactement 1 "primary", justifies (D-27)


class ConfirmProject(BaseModel):
    name: str | None = None
    reporting_year: int
    period_start: str | None = None
    period_end: str | None = None
    outcome_status: str  # measured|pending_follow_up|none (D-20)
    expected_outcome: str | None = None   # requis si pending_follow_up
    follow_up_date: str | None = None     # requis si pending_follow_up (date ISO)

    # Ressources (D-25/D-28/D-30) : champs dedies et obligatoires, plus
    # dependants d'un candidat numerique generique. "0" est une valeur
    # explicite acceptee ; seule l'ABSENCE de valeur est refusee (AC-16) --
    # d'ou des champs non optionnels ici (pas de valeur par defaut).
    jci_volunteers_count: float           # bénévoles JCI (internes)
    activity_duration_hours: float        # durée de l'activité, en heures
    volunteer_hours: float                # heures de bénévolat -- préremplies au calcul
                                           # bénévoles x durée, corrigeables par le SG
    volunteer_hours_corrected: bool = False  # True si le SG a modifié la valeur pré-calculée (D-30)


class ConfirmCandidateInput(BaseModel):
    candidate_id: str
    include: bool = True          # false = l'utilisateur retire ce chiffre
    value: float | None = None    # correction de valeur (sinon celle de l'IA) -- ignore si
                                   # la population résultante est "mixed" (voir value_internal/external)
    value_internal: float | None = None  # requis si internal_external résultant == "mixed" (D-26/AC-30)
    value_external: float | None = None  # requis si internal_external résultant == "mixed" (D-26/AC-30)
    count_type: str | None = None       # reponse "type de comptage" (direct/indirect/audience)
    internal_external: str | None = None  # reponse "pour qui" (interne/externe/mixte)
    corrected: bool = False       # trace derivation "human_validation"


class ConfirmRequest(BaseModel):
    # NOTE (A5) : ConfirmConfirmations (C1-C4) est retiree -- D-28 remplace ce
    # mecanisme de cases a cocher generiques par l'obligation, verifiee champ
    # par champ, que chaque donnee necessaire au dashboard soit realement
    # renseignee (voir _validate_classification/_validate_project cote
    # confirm_service.py). Une fiche ne peut donc plus etre confirmee "a
    # blanc" par 4 cases cochees sans rapport avec les valeurs saisies.
    project: ConfirmProject
    axes: ConfirmAxes
    candidates: list[ConfirmCandidateInput] = []
    confirmed_by: str = "DEMO-USER"


class ConfirmResult(BaseModel):
    project_id: str
    measurement_ids: list[str]


# ---------------------------------------------------------------------------
# Annexe A #8 — POST /measurements/{id}/review
# ---------------------------------------------------------------------------
class ReviewRequest(BaseModel):
    action: str  # validate|flag|unflag
    reason: str | None = None
    reviewed_by: str = "DEMO-USER"


# ---------------------------------------------------------------------------
# Annexe A #9 — POST /aggregations/run (et #10 GET /dashboards/{view})
# ---------------------------------------------------------------------------
class AggregationFilters(BaseModel):
    reporting_year: int | None = None
    area_of_opportunity: str | None = None   # axe A
    programme: str | None = None              # axe B (DEPRECATED, D-23)
    sdg: int | None = None                    # axe C (numero d'ODD, 1..17)


class AggregationRunRequest(BaseModel):
    view: str  # ol|national|global
    scope_organization_id: str | None = None  # requis pour ol/national, absent pour global
    group_by: str = "network"                 # subject|geography|network
    filters: AggregationFilters = AggregationFilters()


# ---------------------------------------------------------------------------
# Annexe A #12 — POST /aggregations/check-pair
# ---------------------------------------------------------------------------
class CheckPairRequest(BaseModel):
    measurement_id_a: str
    measurement_id_b: str
