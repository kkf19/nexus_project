"""Pipeline IA -- etapes STRUCTURED (extraction, contrat NEXUS-EXTRACTION-v0,
dev-brief.md section 4.1) et STANDARDIZED (mapping taxonomie, section 4.2).

Appels REELS a l'API Anthropic (Claude Haiku 4.5) : pas de simulation, pas de
valeur codee en dur a la place d'un appel LLM (dev-brief.md section 3).

Toutes les listes de codes viennent du contenu de taxonomy_release charge en
base et passe en parametre : jamais recopiees en dur ici (dev-brief.md 2.1).
"""
from __future__ import annotations

import json
from typing import Any

import anthropic

from app.config import settings

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY manquant -- voir .env.example")
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def _codes(node) -> list[str]:
    """Extrait la liste des codes d'un noeud de taxonomy.config.json, quelle
    que soit sa forme (liste de dicts {code,...} ou liste de chaines)."""
    if isinstance(node, dict) and "values" in node:
        return [v["code"] for v in node["values"] if "code" in v]
    if isinstance(node, list):
        if node and isinstance(node[0], dict):
            return [v["code"] for v in node if "code" in v]
        return list(node)
    return []


# ---------------------------------------------------------------------------
# Etape STRUCTURED -- contrat NEXUS-EXTRACTION-v0 (dev-brief.md 4.1)
# ---------------------------------------------------------------------------
EXTRACTION_TOOL_NAME = "emit_extraction"

EXTRACTION_SCHEMA = {
    "type": "object",
    "required": ["language", "project", "candidates", "unparsed_numbers"],
    "properties": {
        "language": {
            "type": "string",
            "description": "Code langue ISO 639-1 detecte dans le texte (ex: fr, en, es).",
        },
        "project": {
            "type": "object",
            "required": ["name", "period"],
            "properties": {
                "name": {
                    "type": "object",
                    "required": ["value", "origin", "quote"],
                    "properties": {
                        "value": {"type": ["string", "null"]},
                        "origin": {"type": "string", "enum": ["inferred", "quoted"]},
                        "quote": {"type": ["string", "null"]},
                    },
                },
                "period": {
                    "type": "object",
                    "required": ["start", "end", "reporting_year", "quote"],
                    "properties": {
                        "start": {"type": ["string", "null"], "description": "date ISO ou null"},
                        "end": {"type": ["string", "null"]},
                        "reporting_year": {"type": ["integer", "null"]},
                        "quote": {"type": ["string", "null"]},
                    },
                },
            },
        },
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "candidate_id", "quote", "span", "metric_label_source", "value",
                    "value_qualifier", "value_range", "unit_raw", "is_rate",
                    "base_population_raw", "definition_text", "confidence",
                ],
                "properties": {
                    "candidate_id": {"type": "string"},
                    "quote": {"type": "string", "description": "Sous-chaine EXACTE du texte source."},
                    "span": {
                        "type": "object",
                        "required": ["start", "end"],
                        "properties": {"start": {"type": "integer"}, "end": {"type": "integer"}},
                    },
                    "metric_label_source": {"type": "string"},
                    "value": {"type": ["number", "null"], "description": "null si illisible/absent, jamais 0"},
                    "value_qualifier": {
                        "type": "string",
                        "enum": ["exact", "approx", "at_least", "at_most", "range"],
                    },
                    "value_range": {"type": ["object", "null"]},
                    "unit_raw": {"type": ["string", "null"]},
                    "is_rate": {"type": "boolean"},
                    "base_population_raw": {"type": ["string", "null"]},
                    "definition_text": {"type": ["string", "null"]},
                    "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                },
            },
        },
        "unparsed_numbers": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["quote", "reason"],
                "properties": {"quote": {"type": "string"}, "reason": {"type": "string"}},
            },
        },
    },
}

EXTRACTION_SYSTEM_PROMPT = """Tu es le module d'extraction NEXUS (contrat NEXUS-EXTRACTION-v0).

Tu lis un texte libre ecrit par une organisation locale JCI decrivant un projet, et tu en extrais UNIQUEMENT ce qui est explicitement ecrit -- tu n'inventes rien, tu ne deduis pas de chiffre absent.

Regles obligatoires :
1. `quote` doit etre une sous-chaine EXACTE du texte source (memes caracteres, aucune reformulation).
2. TOUT nombre present dans le texte doit apparaitre soit dans `candidates`, soit dans `unparsed_numbers` avec une raison (ex: "date, pas une mesure"). Aucun chiffre n'est ignore en silence.
3. `value` = null si le nombre est illisible ou absent. JAMAIS 0 a la place d'une valeur inconnue.
4. Les mots "environ", "plus de", "au moins", "jusqu'a" deviennent value_qualifier = approx / at_least / at_most / range (avec value_range rempli si "range"). Le qualificatif n'invente pas de valeur.
5. `definition_text` = null si le texte ne definit pas ce qui est compte.
6. `project.name` : si le texte ne donne pas de nom explicite, deduis un nom court factuel (origin="inferred", quote=null) ; sinon origin="quoted" avec la citation exacte.
7. `project.period` : extrais les dates si elles sont ecrites, calcule `reporting_year` a partir d'elles ; si aucune date n'est donnee, mets tout a null.
8. Detecte la langue du texte pour `language`.

Reponds UNIQUEMENT en appelant l'outil fourni, avec les positions `span` en nombre de caracteres depuis le debut du texte source."""


def _normalize_span(span) -> dict[str, int | None]:
    """Le modele repond parfois par un tableau [start, end] au lieu de
    l'objet {start, end} demande dans le schema (tolerance constatee sur
    l'API de tool-use, cf. auto-test). On normalise ici plutot que de
    rejeter une extraction par ailleurs correcte."""
    if isinstance(span, dict):
        return {"start": span.get("start"), "end": span.get("end")}
    if isinstance(span, (list, tuple)) and len(span) == 2:
        return {"start": span[0], "end": span[1]}
    return {"start": None, "end": None}


def extract_structured(raw_text: str) -> dict[str, Any]:
    """Etape STRUCTURED (dev-brief.md 4.1). Appel reel a Claude Haiku 4.5."""
    client = _get_client()
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        system=EXTRACTION_SYSTEM_PROMPT,
        tools=[{
            "name": EXTRACTION_TOOL_NAME,
            "description": "Enregistre le resultat de l'extraction NEXUS-EXTRACTION-v0.",
            "input_schema": EXTRACTION_SCHEMA,
        }],
        tool_choice={"type": "tool", "name": EXTRACTION_TOOL_NAME},
        messages=[{"role": "user", "content": raw_text}],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = dict(tool_use.input)
    result["contract"] = "NEXUS-EXTRACTION-v0"
    for c in result.get("candidates", []):
        c["span"] = _normalize_span(c.get("span"))
    return result


def validate_extraction_contract(extraction: dict, raw_text: str) -> list[str]:
    """CTL-QUOTE et verifications structurelles minimales sur la sortie IA."""
    errors: list[str] = []
    proj = extraction.get("project") or {}
    name_quote = (proj.get("name") or {}).get("quote")
    if name_quote and name_quote not in raw_text:
        errors.append(f"CTL-QUOTE: project.name.quote absente du texte source : {name_quote!r}")
    period_quote = (proj.get("period") or {}).get("quote")
    if period_quote and period_quote not in raw_text:
        errors.append(f"CTL-QUOTE: project.period.quote absente du texte source : {period_quote!r}")

    for c in extraction.get("candidates", []):
        quote = c.get("quote")
        if not quote or quote not in raw_text:
            errors.append(f"CTL-QUOTE: candidate {c.get('candidate_id')} quote absente du texte source : {quote!r}")
        if c.get("value") == 0:
            errors.append(f"RI-02: candidate {c.get('candidate_id')} a value=0 (interdit, doit etre null si inconnu)")
    return errors


# ---------------------------------------------------------------------------
# Etape STANDARDIZED -- mapping taxonomie (dev-brief.md 4.2)
# ---------------------------------------------------------------------------
MAPPING_TOOL_NAME = "emit_mapping"

MAPPING_SYSTEM_PROMPT = """Tu es le module de classement NEXUS (mapping taxonomie, dev-brief.md 4.2).

Tu recois le resultat d'une extraction (candidats chiffres + nom du projet) et tu dois :

1. Classer le PROJET sur trois axes INDEPENDANTS (aucun ne se deduit d'un autre) :
   - area_of_opportunity (Axe A, domaine d'intervention) : 1 a n valeurs
   - programme (Axe B) : 0 a n valeurs. "Aucun programme" (liste vide) est une reponse legitime ; ne force jamais RISE ou un autre programme si le texte ne l'evoque pas clairement.
   - sdgs (Axe C, Objectifs de Developpement Durable) : 1 a n valeurs, dont EXACTEMENT une avec role="primary". Ne sur-etiquette pas : ne propose que les ODD clairement lies au texte.
   - rise_pillars : uniquement si "RISE" figure dans programme ci-dessus, sinon liste vide.
   - activity_type : deduit du texte, jamais une question posee a l'utilisateur (D-08).

2. Pour CHAQUE candidat chiffre recu, proposer :
   - metric_code (dans le referentiel fourni, ou null si aucun ne convient -- ne jamais inventer un code hors liste)
   - iaooi_value : INPUT (ressource mobilisee, ex. benevoles/heures), ACTIVITY (ce qui a ete fait), OUTPUT (ce qui a ete produit), OUTCOME (changement reel constate), IMPACT_CLAIM (revendication d'impact non mesuree), CONTEXT, ou UNCERTAIN si ambigu
   - unit_code/unit_dimension (ex: person/count, hour/duration, view/count, percent/ratio)
   - count_type : direct (participation reelle), indirect, audience (touche mais pas participe), unique ou cumulative, unknown si non precise
   - internal_external : membres JCI (internal), public externe (external), les deux (mixed), ou unknown
   - dedup_basis, target_group[], source_wording_class (les mots employes par la source), definition (status specified/unknown + texte si donne)

3. Proposer des relations[] entre candidats quand deux chiffres decrivent des etapes d'un meme entonnoir (funnel_stage), un sous-ensemble (subset_of), ou la meme population sous un angle different (same_population_different_metric).

Regles :
- Chaque code que tu utilises DOIT venir de la liste autorisee fournie dans le schema. N'invente jamais un code.
- Un chiffre de communication (vues, followers, portee) n'est jamais compte comme des beneficiaires : count_type="audience", jamais confondu avec un metric_code de personnes formees.
- Si le texte ne permet pas de trancher un champ, utilise "unknown" (jamais une valeur inventee par defaut).
- Justifie chaque choix d'axe projet brievement (justification).

Reponds UNIQUEMENT en appelant l'outil fourni."""


def build_mapping_schema(taxonomy_content: dict) -> dict:
    """Construit dynamiquement les enums de codes depuis taxonomy_content
    (jamais recopies en dur ici -- dev-brief.md 2.1)."""
    axes = taxonomy_content["classification_axes"]
    ml = taxonomy_content["measurement_layer"]

    area_codes = _codes(axes["area_of_opportunity"])
    programme_codes = _codes(axes["programme"])
    rise_pillar_codes = _codes(taxonomy_content["rise_pillars"])
    metric_codes = _codes(ml["input_type"]) + _codes(ml["output_type"]) + _codes(ml["outcome_type"])
    target_group_codes = _codes(ml["target_group"])
    activity_type_codes = _codes(ml["activity_type"])

    return {
        "type": "object",
        "required": ["project_classification", "candidate_mappings", "relations"],
        "properties": {
            "project_classification": {
                "type": "object",
                "required": ["area_of_opportunity", "programme", "rise_pillars", "sdgs", "activity_type"],
                "properties": {
                    "area_of_opportunity": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["code", "confidence", "justification"],
                            "properties": {
                                "code": {"type": "string", "enum": area_codes},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
                    },
                    "programme": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["code", "confidence", "justification"],
                            "properties": {
                                "code": {"type": "string", "enum": programme_codes},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
                    },
                    "rise_pillars": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["code", "confidence", "justification"],
                            "properties": {
                                "code": {"type": "string", "enum": rise_pillar_codes},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
                    },
                    "sdgs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["goal", "role", "confidence", "justification"],
                            "properties": {
                                "goal": {"type": "integer", "minimum": 1, "maximum": 17},
                                "role": {"type": "string", "enum": ["primary", "secondary", "unknown"]},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
                    },
                    "activity_type": {
                        "type": "array",
                        "items": {"type": "string", "enum": activity_type_codes},
                    },
                },
            },
            "candidate_mappings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "candidate_id", "metric_code", "iaooi_value", "confidence",
                        "unit_code", "unit_dimension", "count_type", "internal_external",
                        "dedup_basis", "target_group", "source_wording_class",
                        "definition_status", "definition_text",
                    ],
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "metric_code": {"type": ["string", "null"], "enum": metric_codes + [None]},
                        "iaooi_value": {
                            "type": "string",
                            "enum": ["INPUT", "ACTIVITY", "OUTPUT", "OUTCOME", "IMPACT_CLAIM", "CONTEXT", "UNCERTAIN"],
                        },
                        "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                        "unit_code": {"type": ["string", "null"]},
                        "unit_dimension": {"type": ["string", "null"]},
                        "count_type": {
                            "type": "string",
                            "enum": ["direct", "indirect", "audience", "unique", "cumulative", "unknown"],
                        },
                        "internal_external": {"type": "string", "enum": ["internal", "external", "mixed", "unknown"]},
                        "dedup_basis": {
                            "type": "string",
                            "enum": ["unique_persons", "attendances", "households", "unknown"],
                        },
                        "target_group": {"type": "array", "items": {"type": "string", "enum": target_group_codes}},
                        "source_wording_class": {"type": ["string", "null"]},
                        "definition_status": {"type": "string", "enum": ["specified", "unknown"]},
                        "definition_text": {"type": ["string", "null"]},
                    },
                },
            },
            "relations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["relation_type", "candidate_id_a", "candidate_id_b"],
                    "properties": {
                        "relation_type": {
                            "type": "string",
                            "enum": ["subset_of", "funnel_stage", "same_population_different_metric"],
                        },
                        "candidate_id_a": {"type": "string"},
                        "candidate_id_b": {"type": "string"},
                    },
                },
            },
        },
    }


def map_standardized(extraction: dict, taxonomy_content: dict) -> dict[str, Any]:
    """Etape STANDARDIZED (dev-brief.md 4.2). Appel reel a Claude Haiku 4.5."""
    client = _get_client()
    schema = build_mapping_schema(taxonomy_content)
    user_payload = {
        "project_name": (extraction.get("project") or {}).get("name"),
        "candidates": extraction.get("candidates", []),
    }
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        system=MAPPING_SYSTEM_PROMPT,
        tools=[{
            "name": MAPPING_TOOL_NAME,
            "description": "Enregistre le resultat du mapping taxonomie NEXUS.",
            "input_schema": schema,
        }],
        tool_choice={"type": "tool", "name": MAPPING_TOOL_NAME},
        messages=[{"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)}],
    )
    tool_use = next(b for b in response.content if b.type == "tool_use")
    return dict(tool_use.input)


def validate_mapping_contract(mapping: dict, taxonomy_content: dict) -> list[str]:
    """CTL-TAXO (chaque code existe dans le referentiel), R5 (1 seul SDG
    primary), CTL-AXES (partiel : rise_pillars implique RISE dans programme)."""
    errors: list[str] = []
    axes = taxonomy_content["classification_axes"]
    ml = taxonomy_content["measurement_layer"]

    allowed = {
        "area_of_opportunity": set(_codes(axes["area_of_opportunity"])),
        "programme": set(_codes(axes["programme"])),
        "rise_pillars": set(_codes(taxonomy_content["rise_pillars"])),
        "metric_code": set(_codes(ml["input_type"]) + _codes(ml["output_type"]) + _codes(ml["outcome_type"])),
        "target_group": set(_codes(ml["target_group"])),
        "activity_type": set(_codes(ml["activity_type"])),
    }

    pc = mapping.get("project_classification") or {}
    for item in pc.get("area_of_opportunity", []):
        if item.get("code") not in allowed["area_of_opportunity"]:
            errors.append(f"CTL-TAXO: area_of_opportunity code inconnu : {item.get('code')!r}")
    for item in pc.get("programme", []):
        if item.get("code") not in allowed["programme"]:
            errors.append(f"CTL-TAXO: programme code inconnu : {item.get('code')!r}")
    for item in pc.get("rise_pillars", []):
        if item.get("code") not in allowed["rise_pillars"]:
            errors.append(f"CTL-TAXO: rise_pillars code inconnu : {item.get('code')!r}")
    for item in pc.get("sdgs", []):
        goal = item.get("goal")
        if not isinstance(goal, int) or not (1 <= goal <= 17):
            errors.append(f"CTL-TAXO: sdg goal hors 1..17 : {goal!r}")
    primary_count = sum(1 for s in pc.get("sdgs", []) if s.get("role") == "primary")
    if primary_count != 1:
        errors.append(f"R5: exactement 1 SDG primary attendu, {primary_count} trouve(s)")
    for code in pc.get("activity_type", []):
        if code not in allowed["activity_type"]:
            errors.append(f"CTL-TAXO: activity_type code inconnu : {code!r}")

    for cm in mapping.get("candidate_mappings", []):
        mc = cm.get("metric_code")
        if mc is not None and mc not in allowed["metric_code"]:
            errors.append(f"CTL-TAXO: metric_code inconnu pour {cm.get('candidate_id')} : {mc!r}")
        for tg in cm.get("target_group", []):
            if tg not in allowed["target_group"]:
                errors.append(f"CTL-TAXO: target_group inconnu pour {cm.get('candidate_id')} : {tg!r}")

    programme_codes_chosen = {p.get("code") for p in pc.get("programme", [])}
    if pc.get("rise_pillars") and "RISE" not in programme_codes_chosen:
        errors.append("CTL-AXES: rise_pillars renseigne sans RISE dans programme")

    return errors
