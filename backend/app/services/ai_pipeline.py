"""Pipeline IA -- etapes STRUCTURED (extraction, contrat NEXUS-EXTRACTION-v0,
dev-brief.md section 4.1) et STANDARDIZED (mapping taxonomie, section 4.2),
revu par impact-science.md (D-23 a D-31).

Appels REELS a l'API Anthropic (Claude Haiku 4.5) : pas de simulation, pas de
valeur codee en dur a la place d'un appel LLM (dev-brief.md section 3).

Toutes les listes de codes viennent du contenu de taxonomy_release charge en
base et passe en parametre : jamais recopiees en dur ici (dev-brief.md 2.1).

Ordre de classement impose par impact-science.md section 0 :
    famille d'activite -> Areas (1 principale) -> RISE (seulement si CI
    figure parmi les Areas) -> ODD (sans plafond, 1 principal, une
    justification par valeur).
Le programme (axe B de D-07) est DEPRECATED depuis v0.3.0 (D-23) : ce
pipeline ne le demande plus a l'IA. Il n'existe pas de champ "programme
officiel JCI" sur le projet (decision explicite du PO, 2026-09-19) --
`activity_family.jci_programme_examples` dans taxonomy.config.json reste une
metadonnee informative du referentiel, jamais une question posee au SG.
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
# Etendu par impact-science.md D-25/D-28/D-30 : deux nouveaux champs projet
# dedies (benevoles JCI, duree de l'activite), sur le meme modele que
# project.name/period ({value, origin, quote}) -- jamais un candidat
# numerique generique de plus (A3 : ils alimentent des mesures a part).
# ---------------------------------------------------------------------------
EXTRACTION_TOOL_NAME = "emit_extraction"

_VALUE_ORIGIN_BLOCK = {
    "type": "object",
    "required": ["value", "origin", "quote"],
    "properties": {
        "value": {"type": ["number", "null"]},
        "origin": {"type": "string", "enum": ["inferred", "quoted"]},
        "quote": {"type": ["string", "null"]},
    },
}

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
            "required": [
                "name", "period", "jci_volunteers_count", "activity_duration_hours",
            ],
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
                "jci_volunteers_count": {
                    **_VALUE_ORIGIN_BLOCK,
                    "description": (
                        "Nombre de benevoles/membres JCI ayant organise ou realise le "
                        "projet -- JAMAIS le public beneficiaire. null si non precise."
                    ),
                },
                "activity_duration_hours": {
                    **_VALUE_ORIGIN_BLOCK,
                    "description": (
                        "Duree de l'activite elle-meme, en heures. Convertir une duree "
                        "donnee en jours (ex: '2 jours') en heures si le texte le permet "
                        "raisonnablement ; null si aucune duree n'est donnee ou si elle "
                        "est trop ambigue pour etre convertie."
                    ),
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
2. TOUT nombre present dans le texte doit apparaitre soit dans `candidates`, soit dans `unparsed_numbers` avec une raison (ex: "date, pas une mesure"). Aucun chiffre n'est ignore en silence. EXCEPTION : le nombre de benevoles JCI et la duree de l'activite ne vont PAS dans `candidates` (ils ont leurs propres champs dedies ci-dessous) -- mets alors leur raison ("benevoles JCI, champ dedie" / "duree de l'activite, champ dedie") dans `unparsed_numbers` si tu veux tracer que ce nombre a bien ete vu.
3. `value` = null si le nombre est illisible ou absent. JAMAIS 0 a la place d'une valeur inconnue.
4. Les mots "environ", "plus de", "au moins", "jusqu'a" deviennent value_qualifier = approx / at_least / at_most / range (avec value_range rempli si "range"). Le qualificatif n'invente pas de valeur.
5. `definition_text` = null si le texte ne definit pas ce qui est compte.
6. `project.name` : si le texte ne donne pas de nom explicite, deduis un nom court factuel (origin="inferred", quote=null) ; sinon origin="quoted" avec la citation exacte.
7. `project.period` : extrais les dates si elles sont ecrites, calcule `reporting_year` a partir d'elles ; si aucune date n'est donnee, mets tout a null.
8. Detecte la langue du texte pour `language`.
9. `project.jci_volunteers_count` : le nombre de benevoles ou membres JCI qui ont organise/realise le projet (jamais le public beneficiaire, jamais un total qui melangerait les deux). null si non precise, avec quote=null dans ce cas.
10. `project.activity_duration_hours` : la duree de l'ACTIVITE elle-meme (pas la duree de la campagne de communication, pas la periode de collecte de fonds), en heures. Si le texte donne une duree en jours ou en creneau horaire ("de 14h a 18h"), convertis-la en heures et garde la citation d'origine dans `quote`. null si aucune duree exploitable n'est donnee.

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
    volunteers_quote = (proj.get("jci_volunteers_count") or {}).get("quote")
    if volunteers_quote and volunteers_quote not in raw_text:
        errors.append(
            f"CTL-QUOTE: project.jci_volunteers_count.quote absente du texte source : {volunteers_quote!r}"
        )
    duration_quote = (proj.get("activity_duration_hours") or {}).get("quote")
    if duration_quote and duration_quote not in raw_text:
        errors.append(
            f"CTL-QUOTE: project.activity_duration_hours.quote absente du texte source : {duration_quote!r}"
        )

    for c in extraction.get("candidates", []):
        quote = c.get("quote")
        if not quote or quote not in raw_text:
            errors.append(f"CTL-QUOTE: candidate {c.get('candidate_id')} quote absente du texte source : {quote!r}")
        if c.get("value") == 0:
            errors.append(f"RI-02: candidate {c.get('candidate_id')} a value=0 (interdit, doit etre null si inconnu)")
    return errors


# ---------------------------------------------------------------------------
# Etape STANDARDIZED -- mapping taxonomie (dev-brief.md 4.2), revu par
# impact-science.md : famille -> Areas (1 principale) -> RISE (si CI) -> ODD.
# ---------------------------------------------------------------------------
MAPPING_TOOL_NAME = "emit_mapping"

# D-30/A3 : les heures de benevolat sont TOUJOURS synthetisees par le backend
# (benevoles JCI x duree, cf confirm_service._build_resource_measurements),
# jamais proposees comme un candidat numerique -- exclu de l'enum ci-dessous
# pour que l'IA ne puisse plus jamais l'utiliser comme metric_code.
_METRIC_CODE_EXCLUDED = {"VOLUNTEER_HOURS"}

MAPPING_SYSTEM_PROMPT = """Tu es le module de classement NEXUS (mapping taxonomie, impact-science.md).

Tu recois le resultat d'une extraction (candidats chiffres + nom du projet) et tu dois classer le PROJET dans cet ordre EXACT (impact-science.md section 0) :

1. FAMILLE(S) D'ACTIVITE (`activity_families`, 1..n) : decrit LA FORME de l'action (former, debattre, planter, jumeler, sensibiliser...), jamais le theme (les ODD portent le theme). Choisis un ou plusieurs codes du referentiel fourni. Si aucun code ne convient, choisis le code *_OTHER (ou OTHER) de l'Area la plus proche et remplis `other_label` avec un libelle court et factuel -- jamais vide dans ce cas.

2. AREA(S) DE JCI (`area_of_opportunity`, 1..n, EXACTEMENT UNE avec role="primary") : utilise les signaux d'inclusion/exclusion fournis dans le referentiel pour chaque Area (champ inclusion_signals/exclusion_signals/hard_rule). REGLE DURE, non negociable : si TOUS les candidats chiffres de type "beneficiaires/participants" sont internal_external="internal" (public exclusivement compose de membres JCI) ET qu'aucun n'est "external" ou "mixed", alors Community Impact (CI) NE DOIT JAMAIS etre propose, ni en principal ni en secondaire -- meme si l'activite ressemble a un projet communautaire. A l'inverse, des qu'un public externe ou mixte est implique dans une activite qui repond a un besoin de la communaute, CI doit etre propose (au moins en secondaire).

3. RISE (`rise`) : NE REPONDS "yes" QUE SI Community Impact (CI) figure parmi les Areas retenues a l'etape 2 (principale ou secondaire). Si CI n'est pas retenu, `rise.status` DOIT etre "not_applicable" et `rise.pillars` une liste vide -- jamais "yes" sans CI. Si CI est retenu, decide "yes" seulement si le projet remplit reellement le critere d'au moins un pilier (utilise les inclusion_rule/exclusion_rule fournis pour chaque pilier) ; la simple presence du mot "RISE" dans le texte ne suffit PAS a elle seule. Si "yes", choisis 1 a 3 piliers, chacun justifie.

4. ODD (`sdgs`, 1..n, SANS PLAFOND, EXACTEMENT UN avec role="primary") : ne propose QUE les ODD que tu peux justifier par une phrase concrete du texte. Un ODD que tu ne peux pas justifier n'est pas propose, quel que soit le nombre d'ODD deja retenus -- il n'y a pas de limite haute, seulement l'exigence de justification.

Pour CHAQUE valeur des etapes 1, 2, 3 et 4 (chaque famille, chaque Area, chaque pilier RISE, chaque ODD), `justification` doit etre une phrase COURTE qui s'appuie sur le texte source (paraphrase ou courte citation) -- jamais une justification generique ou vide.

5. Pour CHAQUE candidat chiffre recu (hors benevoles JCI et duree, qui ont deja leurs propres champs et ne sont pas des candidats), proposer :
   - metric_code (dans le referentiel fourni, ou null si aucun ne convient -- ne jamais inventer un code hors liste). N'utilise JAMAIS VOLUNTEERS pour des benevoles/membres JCI (ce nombre est capture ailleurs) : VOLUNTEERS ne sert plus qu'a des benevoles EXTERNES (non-membres) eventuels, si le texte en mentionne explicitement.
   - iaooi_value : INPUT (ressource mobilisee), ACTIVITY (ce qui a ete fait), OUTPUT (ce qui a ete produit), OUTCOME (changement reel constate), IMPACT_CLAIM (revendication d'impact non mesuree), CONTEXT, ou UNCERTAIN si ambigu
   - unit_code/unit_dimension (ex: person/count, hour/duration, view/count, percent/ratio)
   - count_type : direct (participation reelle), indirect, audience (touche mais pas participe), unique ou cumulative, unknown si non precise
   - internal_external : membres JCI (internal), public externe (external), les deux (mixed), ou unknown
   - dedup_basis, target_group[], source_wording_class (les mots employes par la source), definition (status specified/unknown + texte si donne)

6. Proposer des relations[] entre candidats quand deux chiffres decrivent des etapes d'un meme entonnoir (funnel_stage), un sous-ensemble (subset_of), ou la meme population sous un angle different (same_population_different_metric).

Regles :
- Chaque code que tu utilises DOIT venir de la liste autorisee fournie dans le schema. N'invente jamais un code.
- Un chiffre de communication (vues, followers, portee) n'est jamais compte comme des beneficiaires : count_type="audience", jamais confondu avec un metric_code de personnes formees.
- Si le texte ne permet pas de trancher un champ, utilise "unknown" (jamais une valeur inventee par defaut).

Reponds UNIQUEMENT en appelant l'outil fourni."""


def build_mapping_schema(taxonomy_content: dict) -> dict:
    """Construit dynamiquement les enums de codes depuis taxonomy_content
    (jamais recopies en dur ici -- dev-brief.md 2.1)."""
    axes = taxonomy_content["classification_axes"]
    ml = taxonomy_content["measurement_layer"]

    family_codes = _codes(axes["activity_family"])
    area_codes = _codes(axes["area_of_opportunity"])
    rise_pillar_codes = _codes(taxonomy_content["rise_pillars"])
    metric_codes = [
        c for c in (_codes(ml["input_type"]) + _codes(ml["output_type"]) + _codes(ml["outcome_type"]))
        if c not in _METRIC_CODE_EXCLUDED
    ]
    target_group_codes = _codes(ml["target_group"])

    return {
        "type": "object",
        "required": ["project_classification", "candidate_mappings", "relations"],
        "properties": {
            "project_classification": {
                "type": "object",
                "required": ["activity_families", "area_of_opportunity", "rise", "sdgs"],
                "properties": {
                    "activity_families": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["code", "confidence", "justification"],
                            "properties": {
                                "code": {"type": "string", "enum": family_codes},
                                "other_label": {"type": ["string", "null"]},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
                    },
                    "area_of_opportunity": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["code", "role", "confidence", "justification"],
                            "properties": {
                                "code": {"type": "string", "enum": area_codes},
                                "role": {"type": "string", "enum": ["primary", "secondary"]},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
                    },
                    "rise": {
                        "type": "object",
                        "required": ["status", "pillars"],
                        "properties": {
                            "status": {"type": "string", "enum": ["yes", "no", "not_applicable"]},
                            "pillars": {
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
                        },
                    },
                    "sdgs": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["goal", "role", "confidence", "justification"],
                            "properties": {
                                "goal": {"type": "integer", "minimum": 1, "maximum": 17},
                                "role": {"type": "string", "enum": ["primary", "secondary"]},
                                "confidence": {"type": "string", "enum": ["H", "M", "L"]},
                                "justification": {"type": "string"},
                            },
                        },
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
    """Etape STANDARDIZED (dev-brief.md 4.2, impact-science.md). Appel reel a
    Claude Haiku 4.5. Ajoute apres coup `activity_type` comme alias derive de
    `activity_families` (compatibilite avec le code existant qui lirait
    encore l'ancien champ, measurement_layer.activity_type -- jamais demande
    deux fois au modele)."""
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
    result = dict(tool_use.input)
    pc = result.get("project_classification") or {}
    pc["activity_type"] = [af.get("code") for af in pc.get("activity_families", []) if af.get("code")]
    return result


def validate_mapping_contract(mapping: dict, taxonomy_content: dict) -> list[str]:
    """CTL-TAXO (chaque code existe dans le referentiel), R5/D-27 (1 seul SDG
    primary), R2/D-26 (1 seule Area primary), D-24 (RISE seulement si CI),
    D-25 (AUTRE => libelle), et un garde-fou best-effort sur la regle dure
    "public 100% interne => jamais CI" (l'enforcement definitif, sur la
    population CONFIRMEE par le SG, est fait a la confirmation -- A5)."""
    errors: list[str] = []
    axes = taxonomy_content["classification_axes"]
    ml = taxonomy_content["measurement_layer"]

    allowed = {
        "activity_family": set(_codes(axes["activity_family"])),
        "area_of_opportunity": set(_codes(axes["area_of_opportunity"])),
        "rise_pillars": set(_codes(taxonomy_content["rise_pillars"])),
        "metric_code": set(
            c for c in (_codes(ml["input_type"]) + _codes(ml["output_type"]) + _codes(ml["outcome_type"]))
            if c not in _METRIC_CODE_EXCLUDED
        ),
        "target_group": set(_codes(ml["target_group"])),
    }

    pc = mapping.get("project_classification") or {}

    families = pc.get("activity_families", [])
    if not families:
        errors.append("R-A4: activity_families : au moins une famille d'activite est requise (D-25)")
    for item in families:
        code = item.get("code")
        if code not in allowed["activity_family"]:
            errors.append(f"CTL-TAXO: activity_families code inconnu : {code!r}")
        elif (code.endswith("_OTHER") or code == "OTHER") and not (item.get("other_label") or "").strip():
            errors.append(f"D-25: activity_families {code!r} choisi sans other_label (libelle obligatoire)")

    areas = pc.get("area_of_opportunity", [])
    if not areas:
        errors.append("R2: area_of_opportunity : au moins un domaine d'intervention est requis")
    for item in areas:
        if item.get("code") not in allowed["area_of_opportunity"]:
            errors.append(f"CTL-TAXO: area_of_opportunity code inconnu : {item.get('code')!r}")
    primary_areas = [a for a in areas if a.get("role") == "primary"]
    if areas and len(primary_areas) != 1:
        errors.append(f"D-26: exactement 1 Area 'primary' attendue, {len(primary_areas)} trouvee(s)")

    area_codes_chosen = {a.get("code") for a in areas}
    rise = pc.get("rise") or {}
    rise_status = rise.get("status")
    rise_pillars = rise.get("pillars", [])
    if rise_status not in ("yes", "no", "not_applicable"):
        errors.append(f"D-24: rise.status invalide : {rise_status!r}")
    if rise_status == "yes" and "CI" not in area_codes_chosen:
        errors.append("D-24: rise.status='yes' propose sans Community Impact (CI) parmi les Areas")
    if rise_status == "yes" and not rise_pillars:
        errors.append("D-24: rise.status='yes' requiert au moins un pilier")
    if rise_status != "yes" and rise_pillars:
        errors.append("D-24: des piliers RISE sont proposes alors que rise.status != 'yes'")
    for item in rise_pillars:
        if item.get("code") not in allowed["rise_pillars"]:
            errors.append(f"CTL-TAXO: rise pillar code inconnu : {item.get('code')!r}")

    sdgs = pc.get("sdgs", [])
    if not sdgs:
        errors.append("R5/D-27: sdgs : au moins un ODD est requis")
    for item in sdgs:
        goal = item.get("goal")
        if not isinstance(goal, int) or not (1 <= goal <= 17):
            errors.append(f"CTL-TAXO: sdg goal hors 1..17 : {goal!r}")
        if not (item.get("justification") or "").strip():
            errors.append(f"D-27: sdg {goal!r} sans justification (obligatoire pour tout ODD retenu)")
    primary_count = sum(1 for s in sdgs if s.get("role") == "primary")
    if sdgs and primary_count != 1:
        errors.append(f"D-27: exactement 1 SDG primary attendu, {primary_count} trouve(s)")

    # Garde-fou best-effort (RI-10) : si TOUS les candidats "population" connus
    # sont internes et qu'aucun n'est externe/mixte, CI ne doit pas etre
    # propose. Ne bloque pas si aucun candidat n'a de internal_external connu
    # (signal insuffisant pour trancher au niveau du pipeline).
    ies = [cm.get("internal_external") for cm in mapping.get("candidate_mappings", [])]
    known_ies = [ie for ie in ies if ie in ("internal", "external", "mixed")]
    if known_ies and all(ie == "internal" for ie in known_ies) and "CI" in area_codes_chosen:
        errors.append(
            "D-26: Community Impact propose alors que tous les candidats connus sont "
            "internal_external='internal' (public 100% membres JCI => jamais CI)"
        )

    for cm in mapping.get("candidate_mappings", []):
        mc = cm.get("metric_code")
        if mc is not None and mc not in allowed["metric_code"]:
            errors.append(f"CTL-TAXO: metric_code inconnu pour {cm.get('candidate_id')} : {mc!r}")
        for tg in cm.get("target_group", []):
            if tg not in allowed["target_group"]:
                errors.append(f"CTL-TAXO: target_group inconnu pour {cm.get('candidate_id')} : {tg!r}")

    return errors
