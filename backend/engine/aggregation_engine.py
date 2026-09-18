#!/usr/bin/env python3
"""
NEXUS — moteur d'agrégation sûre.

Le cœur de la proposition de valeur : le système sait dire NON, et sait dire
POURQUOI. Deux Measurement Objects ne s'additionnent que si leurs clés
d'équivalence coïncident et que huit conditions sont réunies.

Un refus n'est pas une erreur. C'est un résultat, conservé et affiché.

Référence : docs/technical/measurement-object.md §3
Standard   : PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1

Usage:
    python3 aggregation_engine.py <measurements.json> [--group-by subject|geography|network]
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable

STANDARD = "PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1"

# ---------------------------------------------------------------------------
# Raisons de refus (énumération fermée — cf. measurement-object.schema.json)
# ---------------------------------------------------------------------------
SEMANTIC_NON_EQUIVALENCE = "SEMANTIC_NON_EQUIVALENCE"
UNKNOWN_VALUE = "UNKNOWN_VALUE"
OPEN_CONFLICT = "OPEN_CONFLICT"
MISSING_DEFINITION = "MISSING_DEFINITION"
MISSING_COUNT_TYPE = "MISSING_COUNT_TYPE"
PERIOD_MISMATCH = "PERIOD_MISMATCH"
UNRESOLVED_DUPLICATE = "UNRESOLVED_DUPLICATE"
POPULATION_OVERLAP = "POPULATION_OVERLAP"
MISSING_PERIOD = "MISSING_PERIOD"  # D-17

REASON_FR = {
    SEMANTIC_NON_EQUIVALENCE: "les mesures ne désignent pas la même chose",
    UNKNOWN_VALUE: "valeur inconnue ou non extraite (jamais remplacée par 0)",
    OPEN_CONFLICT: "un conflit documentaire non résolu porte sur cette valeur",
    MISSING_DEFINITION: "définitions incompatibles ou absentes",
    MISSING_COUNT_TYPE: "type de comptage non renseigné : le total n'aurait pas de sens",
    PERIOD_MISMATCH: "périodes de reporting non comparables",
    UNRESOLVED_DUPLICATE: "doublon suspecté non résolu (risque de double comptage)",
    POPULATION_OVERLAP: "les populations se recouvrent (sous-ensemble ou étape d'entonnoir)",
    MISSING_PERIOD: "période inconnue : une mesure non datée n'entre dans aucun total (D-17)",
}

VALUE_STATUS_AGGREGABLE = {"extracted", "calculated"}
BLOCKING_VERIFICATION = {"flagged"}

EXCLUSIVE_RELATIONS = {"subset_of", "funnel_stage", "same_population_different_metric"}

# Décision produit D-13 (2026-09-18) : un pourcentage ou un ratio n'entre jamais
# dans un total (20 % + 30 % ne font pas 50 %). Refusé ici, affiché par projet.
NON_ADDITIVE_UNITS = {"percent", "ratio"}

# Décision produit D-03 (2026-09-18) : la déduplication est hors périmètre MVP.
# Un même projet déclaré par deux organisations est compté deux fois, sans refus
# ni signalement. Le code correspondant est conservé et réactivable ici.
DEDUP_ENABLED = False


# ---------------------------------------------------------------------------
# Clé d'équivalence
# ---------------------------------------------------------------------------
def equivalence_key(m: dict) -> str:
    """Deux mesures ne sont additionnables que si cette clé est identique.

    L'ordre des composants est figé : il fait partie du standard.
    """
    return "|".join([
        str(m.get("metric_code")),
        str((m.get("unit") or {}).get("code")),
        str((m.get("iaooi_class") or {}).get("value")),
        str((m.get("population") or {}).get("count_type")),
        str((m.get("population") or {}).get("internal_external")),
        str((m.get("population") or {}).get("dedup_basis")),
        str((m.get("period") or {}).get("type")),
        str((m.get("subject") or {}).get("type")),
    ])


# ---------------------------------------------------------------------------
# Résultats
# ---------------------------------------------------------------------------
@dataclass
class Refusal:
    reason: str
    measurement_ids: list[str]
    detail: str = ""

    def explain(self) -> str:
        return f"{self.reason} — {REASON_FR.get(self.reason, '')}" + (f" ({self.detail})" if self.detail else "")


@dataclass
class Aggregate:
    metric_code: str
    equivalence_key: str
    value: float
    unit: str
    value_qualifier: str
    verification_status: str
    inputs: list[str]
    coverage: dict
    group: str

    def to_measurement_object(self, measurement_id: str, subject: dict, period: dict) -> dict:
        """Un agrégat est lui-même un Measurement Object (règle P2 : calculated
        ⇒ SEMANTIC_INTERPRETATION, jamais OFFICIAL_JCI_FACT)."""
        return {
            "measurement_id": measurement_id,
            "standard": STANDARD,
            "metric_code": self.metric_code,
            "metric_label_source": f"agrégat moteur — {self.metric_code} — {self.group}",
            "definition": {"status": "specified",
                           "text": "somme des mesures de clé d'équivalence identique"},
            "iaooi_class": {"value": self.equivalence_key.split("|")[2],
                            "layer": "SEMANTIC_INTERPRETATION",
                            "rule_id": "AGG-1", "confidence": "H"},
            "value": self.value,
            "value_status": "calculated",
            "value_qualifier": self.value_qualifier,
            "formula": "sum(inputs)",
            "inputs": self.inputs,
            "unit": {"code": self.unit},
            "subject": subject,
            "population": {
                "internal_external": self.equivalence_key.split("|")[4],
                "count_type": self.equivalence_key.split("|")[3],
                "dedup_basis": self.equivalence_key.split("|")[5],
            },
            "period": period,
            "layer": "SEMANTIC_INTERPRETATION",
            "source": {"origin": "engine"},
            "derivation": [{"step": "aggregate", "rule_id": "AGG-1",
                            "agent": "rules@v0", "input_refs": self.inputs,
                            "confidence": "H"}],
            "confidence": "H",
            "verification_status": self.verification_status,
            "parent_measurement_ids": self.inputs,
            "aggregation": {
                "aggregable": True,
                "equivalence_key": self.equivalence_key,
                "coverage": self.coverage,
            },
        }


@dataclass
class EngineResult:
    aggregates: list[Aggregate] = field(default_factory=list)
    refusals: list[Refusal] = field(default_factory=list)
    excluded: list[tuple[str, Refusal]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Éligibilité individuelle (étapes 1, 2, 5 de la procédure)
# ---------------------------------------------------------------------------
def eligibility(m: dict) -> Refusal | None:
    mid = m.get("measurement_id", "?")

    # 1 — la valeur doit exister et être exploitable. UNKNOWN n'est jamais ZERO.
    if m.get("value_status") not in VALUE_STATUS_AGGREGABLE or m.get("value") is None:
        return Refusal(UNKNOWN_VALUE, [mid], f"value_status={m.get('value_status')}")

    # 2 — un conflit documentaire ouvert bloque (règles P8 / T6)
    if m.get("dq_refs"):
        return Refusal(OPEN_CONFLICT, [mid], f"objets qualité : {', '.join(m['dq_refs'])}")

    # 2bis — un signalement bloque (règle T8)
    if m.get("verification_status") in BLOCKING_VERIFICATION:
        reason = ((m.get("flag") or {}).get("reason")) or "signalé"
        return Refusal(OPEN_CONFLICT, [mid], f"signalé : {reason}")

    # 4bis — une unité non additive ne se somme jamais (D-13)
    unit_code = (m.get("unit") or {}).get("code")
    if unit_code in NON_ADDITIVE_UNITS:
        return Refusal(SEMANTIC_NON_EQUIVALENCE, [mid], f"unité non additive : {unit_code} (D-13)")

    # 5 — sans type de comptage, un total de personnes ne veut rien dire
    if (m.get("population") or {}).get("count_type") in (None, "unknown"):
        return Refusal(MISSING_COUNT_TYPE, [mid])

    # 6bis — une mesure non datée n'entre dans aucun total (D-17, DQC-24).
    # Filet de sécurité : pour une saisie OL, la complétion guidée rend la
    # période obligatoire en amont ; ce refus couvre les sources qu'on ne peut
    # pas interroger (documents JCI, imports).
    period = m.get("period") or {}
    if period.get("type") in (None, "unknown") or period.get("reporting_year") is None:
        return Refusal(MISSING_PERIOD, [mid], f"period.type={period.get('type')}")

    return None


# ---------------------------------------------------------------------------
# Compatibilité par paire (étapes 4, 6, 7, 8)
# ---------------------------------------------------------------------------
def _definitions_compatible(a: dict, b: dict) -> bool:
    da, db = a.get("definition") or {}, b.get("definition") or {}
    if da.get("status") == "specified" and db.get("status") == "specified":
        return da.get("text", "").strip().lower() == db.get("text", "").strip().lower()
    # deux `unknown` ne valent pas équivalence : traités en `conditional` ailleurs
    return True


def _periods_compatible(a: dict, b: dict) -> bool:
    pa, pb = a.get("period") or {}, b.get("period") or {}
    ya, yb = pa.get("reporting_year"), pb.get("reporting_year")
    if ya is None or yb is None:
        return False
    return ya == yb


def _duplicate_collision(a: dict, b: dict) -> bool:
    # Décision D-03 : hors périmètre MVP. Second point d'entrée de la règle,
    # à garder synchronisé avec _resolve_duplicates.
    if not DEDUP_ENABLED:
        return False

    agga, aggb = a.get("aggregation") or {}, b.get("aggregation") or {}
    ida, idb = a.get("measurement_id"), b.get("measurement_id")

    # doublon explicitement suspecté, dans un sens ou dans l'autre
    if idb in (agga.get("suspected_duplicate_of") or []):
        return True
    if ida in (aggb.get("suspected_duplicate_of") or []):
        return True

    # même projet canonique déclaré deux fois (twinning, cas TC5) → double comptage
    ka, kb = agga.get("dedup_key"), aggb.get("dedup_key")
    return bool(ka and kb and ka == kb and ida != idb)


def _population_overlap(a: dict, b: dict) -> bool:
    for rel in (a.get("relations") or []):
        if rel.get("relation_type") in EXCLUSIVE_RELATIONS and rel.get("measurement_id") == b.get("measurement_id"):
            return True
    for rel in (b.get("relations") or []):
        if rel.get("relation_type") in EXCLUSIVE_RELATIONS and rel.get("measurement_id") == a.get("measurement_id"):
            return True
    return False


def pair_compatibility(a: dict, b: dict) -> Refusal | None:
    ids = [a.get("measurement_id", "?"), b.get("measurement_id", "?")]
    if equivalence_key(a) != equivalence_key(b):
        return Refusal(SEMANTIC_NON_EQUIVALENCE, ids,
                       f"{equivalence_key(a)}  ≠  {equivalence_key(b)}")
    if not _definitions_compatible(a, b):
        return Refusal(MISSING_DEFINITION, ids, "définitions déclarées divergentes")
    if not _periods_compatible(a, b):
        return Refusal(PERIOD_MISMATCH, ids)
    if _duplicate_collision(a, b):
        return Refusal(UNRESOLVED_DUPLICATE, ids, "même dedup_key — projet probablement déclaré deux fois")
    if _population_overlap(a, b):
        return Refusal(POPULATION_OVERLAP, ids)
    return None


# ---------------------------------------------------------------------------
# Moteur
# ---------------------------------------------------------------------------
VERIFICATION_RANK = {"flagged": -1, "reported": 0, "validated": 1, "verified": 2}
RANK_VERIFICATION = {v: k for k, v in VERIFICATION_RANK.items()}


def _dedup_group_key(m: dict) -> str | None:
    """Empreinte du projet canonique, si elle existe."""
    agg = m.get("aggregation") or {}
    if agg.get("dedup_key"):
        return agg["dedup_key"]
    return None


def _resolve_duplicates(members: list[dict], result: EngineResult,
                        enabled: bool = DEDUP_ENABLED) -> tuple[list[dict], list[str]]:
    """Traite les déclarations multiples d'un même projet canonique.

    DÉSACTIVÉ PAR DÉFAUT — décision produit D-03 (2026-09-18) : la déduplication
    est hors périmètre MVP. Un projet déclaré deux fois est compté deux fois.
    Le code reste en place, prêt à être réactivé par DEDUP_ENABLED = True.

    Quand la règle est active :
    - valeurs identiques  -> une seule entre dans la somme, la duplication est tracée
    - valeurs divergentes -> aucune n'entre : c'est un conflit, pas un doublon,
                             et sa résolution appartient aux humains
    Le moteur ne choisit jamais entre deux déclarations divergentes.
    """
    if not enabled:
        return list(members), []

    by_key: dict[str, list[dict]] = {}
    singles: list[dict] = []
    for m in members:
        key = _dedup_group_key(m)
        if key:
            by_key.setdefault(key, []).append(m)
        else:
            singles.append(m)

    kept = list(singles)
    notes: list[str] = []

    for key, group in by_key.items():
        if len(group) == 1:
            kept.append(group[0])
            continue

        ids = [g.get("measurement_id", "?") for g in group]
        values = {g.get("value") for g in group}

        if len(values) == 1:
            # même projet, même chiffre : compté UNE fois
            kept.append(group[0])
            notes.append(f"{key}: {len(group)} déclarations identiques ({', '.join(ids)}) — comptées une seule fois")
            result.refusals.append(Refusal(
                UNRESOLVED_DUPLICATE, ids,
                f"même projet canonique « {key} » déclaré {len(group)} fois avec la même valeur "
                f"({group[0].get('value')}) — compté une seule fois, non additionné"))
        else:
            # même projet, chiffres différents : personne ne tranche
            result.refusals.append(Refusal(
                UNRESOLVED_DUPLICATE, ids,
                f"même projet canonique « {key} » déclaré avec des valeurs divergentes "
                f"({', '.join(str(v) for v in sorted(values, key=lambda x: (x is None, x)))}) — "
                f"aucune retenue, arbitrage humain requis"))

    return kept, notes


def group_label(m: dict, group_by: str) -> str:
    if group_by == "subject":
        return f"{(m.get('subject') or {}).get('type')}:{(m.get('subject') or {}).get('id')}"
    if group_by == "geography":
        geo = m.get("geography") or {}
        for level in ("geographic_area", "country_iso2", "national_organization", "local_organization"):
            node = geo.get(level)
            value = node.get("value") if isinstance(node, dict) else node
            if value:
                return f"{level}:{value}"
        return "geography:unknown"
    return "network:all"


def aggregate(measurements: Iterable[dict], group_by: str = "subject",
              total_units: int | None = None) -> EngineResult:
    result = EngineResult()
    eligible: list[dict] = []

    # Étapes 1, 2, 5 — éligibilité individuelle
    for m in measurements:
        refusal = eligibility(m)
        if refusal:
            result.excluded.append((m.get("measurement_id", "?"), refusal))
        else:
            eligible.append(m)

    # Regroupement par (groupe, clé d'équivalence)
    buckets: dict[tuple[str, str], list[dict]] = {}
    for m in eligible:
        buckets.setdefault((group_label(m, group_by), equivalence_key(m)), []).append(m)

    # Étapes 3, 4, 6, 7, 8 — compatibilité intra-groupe
    for (group, key), members in sorted(buckets.items()):
        # Étape 7 (pré-passe) — déduplication.
        # Garder arbitrairement l'une de deux déclarations du même projet serait
        # une résolution silencieuse de conflit. Deux cas seulement :
        #   valeurs identiques -> compté une fois, la duplication est tracée
        #   valeurs divergentes -> personne ne tranche, tout le groupe est refusé
        members, dedup_notes = _resolve_duplicates(members, result)

        kept: list[dict] = []
        for candidate in members:
            refusal = None
            for already in kept:
                refusal = pair_compatibility(already, candidate)
                if refusal:
                    break
            if refusal:
                result.refusals.append(refusal)
            else:
                kept.append(candidate)

        if not kept:
            continue

        qualifiers = {m.get("value_qualifier", "exact") for m in kept}
        ranks = [VERIFICATION_RANK.get(m.get("verification_status", "reported"), 0) for m in kept]
        contributing = len({(m.get("subject") or {}).get("id") for m in kept})

        result.aggregates.append(Aggregate(
            metric_code=kept[0]["metric_code"],
            equivalence_key=key,
            value=sum(m["value"] for m in kept),
            unit=(kept[0].get("unit") or {}).get("code", "?"),
            # AGG-3 : une entrée approximative rend l'agrégat approximatif
            value_qualifier="approx" if qualifiers & {"approx", "at_least", "at_most", "range"} else "exact",
            # AGG-2 : le statut de l'agrégat est le plus faible de ses entrées
            verification_status=RANK_VERIFICATION[min(ranks)],
            inputs=[m["measurement_id"] for m in kept],
            # AGG-4 : un agrégat déclare sa couverture
            coverage={"contributing_units": contributing,
                      "total_units": total_units if total_units is not None else contributing,
                      "share": round(contributing / total_units, 3) if total_units else 1.0},
            group=group,
        ))

    return result


# ---------------------------------------------------------------------------
# Rapport lisible — ce que le board voit
# ---------------------------------------------------------------------------
def report(result: EngineResult) -> str:
    out: list[str] = []
    out.append("=" * 72)
    out.append("NEXUS — RÉSULTAT D'AGRÉGATION")
    out.append("=" * 72)

    out.append(f"\n  AGRÉGATS PRODUITS ({len(result.aggregates)})")
    if not result.aggregates:
        out.append("    (aucun)")
    for a in result.aggregates:
        approx = "≈ " if a.value_qualifier == "approx" else ""
        out.append(f"\n    [{a.group}]  {a.metric_code}")
        out.append(f"      {approx}{a.value:,.0f} {a.unit}".replace(",", " "))
        out.append(f"      statut de vérification : {a.verification_status}  (le plus faible des entrées — AGG-2)")
        out.append(f"      couverture : {a.coverage['contributing_units']}/{a.coverage['total_units']} "
                   f"unités contributrices ({a.coverage['share']:.0%}) — AGG-4")
        out.append(f"      composé de : {', '.join(a.inputs)}")
        out.append(f"      clé : {a.equivalence_key}")

    total_refus = len(result.excluded) + len(result.refusals)
    out.append(f"\n  REFUS D'AGRÉGATION ({total_refus}) — conservés et affichés, pas masqués")
    for mid, refusal in result.excluded:
        out.append(f"\n    ✗ {mid}")
        out.append(f"      {refusal.explain()}")
    for refusal in result.refusals:
        out.append(f"\n    ✗ {' + '.join(refusal.measurement_ids)}")
        out.append(f"      {refusal.explain()}")

    out.append("\n" + "=" * 72)
    out.append("  Un refus n'est pas une panne du système : c'est sa fonction.")
    out.append("=" * 72)
    return "\n".join(out)


# ---------------------------------------------------------------------------
def load_measurements(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "valid" in data:
        objs = data["valid"]
    elif isinstance(data, dict) and "measurements" in data:
        objs = data["measurements"]
    elif isinstance(data, list):
        objs = data
    else:
        objs = [data]
    return [{k: v for k, v in o.items() if not k.startswith("_")} for o in objs]


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    path = argv[0]
    group_by = "subject"
    if "--group-by" in argv:
        group_by = argv[argv.index("--group-by") + 1]
    measurements = load_measurements(path)
    # on écarte les agrégats déjà calculés : on ne somme pas un total et ses parties
    measurements = [m for m in measurements if not m.get("parent_measurement_ids")]
    print(report(aggregate(measurements, group_by=group_by)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
