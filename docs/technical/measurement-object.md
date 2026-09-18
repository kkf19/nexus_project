# NEXUS — Measurement Object (v1)

**Statut** : `ACCEPTED` (D-01, 2026-09-18) — reste `PROPOSED_STANDARD`, révisable.
**Standard** : `PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1`
**Date** : 2026-09-18
**Sources** : Tier 1 (§P provenance, §B IAOOI, §C taxonomie, §D schéma, §Q conflits, §V visuels), Tier 2 (§F 465 indicateurs, §G collecte, §H qualité & lignage), `docs/technical/data-model.md`, `docs/technical/taxonomy.config.json`.
**Rapport à la fiche vision** : la fiche vision nomme le Measurement Object dans sa chaîne de valeur (§6) et le décrit comme « un contenant générique, pas un schéma figé » (§14), en laissant son noyau explicitement ouvert (§17). Ce document le ferme. Là où la fiche vision et Tier 1/Tier 2 divergent, Tier 1/Tier 2 priment (analyses fondées sur la source JCI) — les divergences sont listées en §10, pas résolues en silence.


> **Amendements du 2026-09-18 (soir) — priment sur le texte ci-dessous** (détail : `mvp-scope.md` §1)
> - **D-11** : toute mesure de projet produite par le pipeline porte `period.type = reporting_year` ; `start`/`end` restent renseignés. Les clés d'équivalence des exemples §8–§9 s'écrivent donc `…|reporting_year|project`.
> - **D-13** : `percent` et `ratio` n'entrent jamais dans un total (refus moteur `SEMANTIC_NON_EQUIVALENCE`, motif « unité non additive »).
> - **D-14** : `aggregation.aggregable` d'un objet = son éligibilité individuelle (étapes 1, 2, 5 du §3). Le refus « 45 formées + 12 000 vues » (§9) est un refus **de paire**, produit par le moteur et stocké dans la table des refus ; il ne se porte pas sur l'objet `COMM_AUDIENCE`, qui reste agrégeable avec d'autres vues.
> - **D-03** (rappel) : la déduplication est hors MVP ; le compromis D3 du §10 (refus `UNRESOLVED_DUPLICATE`) est désactivé.
> - **D-15** : `geography.country_iso2` issu du compte de l'OL est en couche `LOCAL_REPORTED_FACT`.

---

## 0. Ce que c'est (définition non négociable)

> **Un Measurement Object est l'enregistrement atomique d'UNE grandeur : un nombre (ou l'absence explicite de nombre), portant sur UNE population ou UNE chose dénombrable, exprimé dans UNE unité, sur UNE période, produit d'UNE manière, tel qu'affirmé par UNE source.**

Ce n'est **pas** :
- un projet (le projet est un conteneur qui porte plusieurs measurements) ;
- un indicateur (un indicateur est une *définition* ; un measurement en est une *occurrence*) ;
- une ligne de dashboard (le dashboard est une vue calculée par-dessus des measurements).

**Déclaration de grain (la ligne la plus importante du document)** :

```
1 Measurement Object
  = 1 metric_code
  × 1 subject (projet | organisation | événement | programme | réseau)
  × 1 population qualifiée
  × 1 unité
  × 1 période
  × 1 source
```

Si deux de ces axes varient, ce sont **deux** Measurement Objects, jamais un seul agrégé implicitement.

**Pourquoi un objet unique pour le local ET pour JCI** : le même type d'objet porte aussi bien « 25 jeunes formés » déclaré par JCI Comé qu'« Total Number of Volunteers Engaged: 42,401 » publié par JCI [p. 86]. C'est ce qui permet la règle AGG-5 : comparer un agrégat calculé par le moteur avec un total publié par JCI, sans jamais substituer l'un à l'autre. Les 465 indicateurs de Tier 2 sont, structurellement, des Measurement Objects de `subject.type = network`.

---

## 1. Principe directeur : chaque champ répare une défaillance observée

Aucun champ de cet objet n'existe « parce que c'est propre ». Chacun existe parce que son absence a produit une erreur constatée dans le rapport JCI 2025.

| Champ | Défaillance observée qui le justifie |
|---|---|
| `definition` (avec `unknown` légal) | 462 des 465 indicateurs du rapport n'ont **aucune définition imprimée** (T2-1) |
| `metric_label_source` séparé de `metric_code` | « Measurable outcomes included 244 volunteer hours » — le libellé JCI et le sens réel divergent (S2) |
| `iaooi_class` séparé de `source_wording_class` | Des INPUTS sont étiquetés « outcomes » dans 4 projets [p. 87–90] (S2) |
| `value_qualifier` | « over 100,000 », « more than 100 countries », « environ 150 heures » — la précision déclarée par la source doit survivre (DQC-01, DQC-02) |
| `population.count_type` | 21 148 414 « beneficiaries » sans définition ni méthode de comptage (T2-4, H.3) |
| `population.internal_external` | Membres JCI et communautés externes mélangés dans les agrégats (S6) |
| `population.base_population` | « 75 % placed » sans base [p. 91] (DQC-12) ; « 4 nouveaux membres = 20 % » (DQC-13) |
| `period` obligatoire | 6 périodes de reporting différentes dans un même rapport (DQC-24) |
| `value_status = visual_data_not_extracted` | 9 graphiques illisibles → `null`, jamais 0 (§V, règle P4) |
| `value_status = conflicting` + `dq_refs` | 26 conflits documentaires, tous UNRESOLVED (§Q) |
| `layer` + `derivation[]` | Lignage cassé à 3 niveaux sur 9 sur la métrique la mieux fournie (H.3) |
| `verification_status` | Le rapport ne décrit **aucune** méthode de vérification (H.1) |
| `aggregation.dedup_key` | Un twinning peut être déclaré par chaque partie (R6, cas TC5) |
| `aggregation.equivalence_key` | `trained ≠ reached`, `registered ≠ attendees`, `reach ≠ beneficiaries` (DQC-06, 08, 14, 15) |
| `relations[]` | Entonnoir 200+ / 120 / 60 sur la même population [p. 92] : reliés, non additionnables |

---

## 2. Structure de l'objet

### 2.1 Identité
| Champ | Type | Note |
|---|---|---|
| `measurement_id` | string | SYSTEM-DERIVED, stable |
| `standard` | string | `PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1` |
| `created_at` / `updated_at` | datetime | SYSTEM-DERIVED |

### 2.2 Sémantique — *qu'est-ce qui est mesuré*
| Champ | Type | Couche | Note |
|---|---|---|---|
| `metric_code` | enum (taxonomie L5/L6/L7 + vocabulaire métrique) | attribution = SEMANTIC_INTERPRETATION, code = PROPOSED_STANDARD | jamais OFFICIAL_JCI_FACT (règle P5, contrôle V6) |
| `metric_label_source` | string | OFFICIAL_JCI_FACT ou LOCAL_REPORTED_FACT | le libellé **exact** de la source, jamais reformulé |
| `definition` | object `{text, layer, status}` | — | `status ∈ {specified, unknown}`. `unknown` → `text = "NOT SPECIFIED IN THE SOURCE DOCUMENT"`. **Jamais inventée.** |
| `iaooi_class` | enum `INPUT \| ACTIVITY \| OUTPUT \| OUTCOME \| IMPACT_CLAIM \| CONTEXT \| UNCERTAIN` | SEMANTIC_INTERPRETATION | `+ rule_id + confidence`. Standard `IAOOI-v0`. |
| `source_wording_class` | string \| null | OFFICIAL/LOCAL fact | comment la **source** l'a rangé (ex. `"measurable outcomes"`). Permet la phrase clé du produit : *« le document l'appelle X, NEXUS le classe Y, voici pourquoi »*. |
| `taxonomy_refs` | object | SEMANTIC_INTERPRETATION | `{area_of_opportunity[], program, activity_type[], target_group[], sdgs[]}` — codes issus de `taxonomy.config.json` |

### 2.3 Valeur — *le nombre*
| Champ | Type | Note |
|---|---|---|
| `value` | number \| null | `null` obligatoire si `unknown` / `visual_data_not_extracted`. **Jamais 0 par défaut.** |
| `value_status` | enum | `extracted \| calculated \| estimated \| unknown \| visual_data_not_extracted \| conflicting` |
| `value_qualifier` | enum | `exact \| approx \| at_least \| at_most \| range` — décrit la précision **déclarée par la source**, ne transforme jamais `extracted` en `estimated` |
| `value_range` | `{min, max}` \| null | requis si `value_qualifier = range` |
| `unit` | `{code, dimension, currency_code?}` | `person, hour, item, kg, t, kW, signature, agreement, document, percent, ratio, currency, tree, ...` |
| `unit_normalization` | object \| null | `{original_unit, original_value, rule_id, rate_date}` — SEMANTIC_INTERPRETATION ; obligatoire pour toute conversion (devise, durée) |
| `formula` / `inputs[]` | string / string[] | obligatoires si `calculated` (règle P2) |
| `method` / `assumptions[]` | string / string[] | obligatoires si `estimated` (règle P3) |
| `conflicting_values[]` | array | obligatoire si `conflicting` : **toutes** les valeurs conservées, aucune choisie (règle P8) |

### 2.4 Sujet et population — *sur quoi ça porte*
| Champ | Type | Note |
|---|---|---|
| `subject` | `{type, id, name}` | `type ∈ {project, organization, event, program, network}` |
| `population.target_group[]` | enum familles (taxonomie v0.2.2, D-19) + `OTHER` | SEMANTIC_INTERPRETATION — facultatif, jamais bloquant, **hors clé d'équivalence** ; libellé source conservé |
| `population.internal_external` | enum `internal \| external \| mixed \| unknown` | membres JCI vs communautés externes — **HUMAN-VALIDATED** (règle R7) |
| `population.count_type` | enum `direct \| indirect \| audience \| unique \| cumulative \| unknown` | sans lui, aucun total de « bénéficiaires » n'a de sens |
| `population.dedup_basis` | enum `unique_persons \| attendances \| households \| unknown` | distingue « 100 personnes » de « 100 présences » |
| `population.base_population` | `{value, definition, layer} \| null` | **obligatoire** si `unit = percent \| ratio` (DQC-12/13) |
| `population.attributes` | object \| null | `{gender_share, age_band, rural_urban}` — attributs, pas des groupes |

### 2.5 Temps et géographie
| Champ | Type | Note |
|---|---|---|
| `period` | `{type, start, end, reporting_year}` | `type ∈ {point_in_time, range, reporting_year, unknown}`. Obligatoire (DQC-24). |
| `geography` | `{local_organization, national_organization, country_iso2, geographic_area}` | chaque niveau porte sa propre `{value, layer, rule_id, confidence}`. **Jamais de clé `area` nue** (règle P7). `geographic_area` déduite reste SEMANTIC_INTERPRETATION tant que la table JCI manque (VDX-01). |

### 2.6 Provenance
| Champ | Type | Note |
|---|---|---|
| `layer` | enum | `OFFICIAL_JCI_FACT \| LOCAL_REPORTED_FACT \| SEMANTIC_INTERPRETATION \| PROPOSED_STANDARD` |
| `source` | `{origin, document_id, page, section, quote, span, submitted_at, language}` | `quote` **non vide obligatoire** pour OFFICIAL_JCI_FACT et LOCAL_REPORTED_FACT (règles P1/P9, contrôle V2) |
| `derivation[]` | array ordonnée | chaque étape : `{step, rule_id, agent, input_refs[], confidence, timestamp}`. `agent` = `llm_extractor@v0` / `rules@v0` / `reviewer:<id>`. C'est le lignage `LINEAGE-v0` **porté par l'objet lui-même**, pas reconstruit après coup. |
| `confidence` | enum `H \| M \| L` | obligatoire sur toute SEMANTIC_INTERPRETATION |

### 2.7 Contrôle qualité
| Champ | Type | Note |
|---|---|---|
| `verification_status` | enum `reported \| flagged \| validated \| verified` | voir §4 |
| `evidence_refs[]` | array | **obligatoire** si `verified` (règle T2, contrôle V11) |
| `checks_passed[]` / `checks_failed[]` | string[] | ids des règles AUTO-CHECKED |
| `dq_refs[]` | string[] | liens vers DQC / VDX |
| `flag` | `{raised_by, reason, at} \| null` | rempli si `flagged` |
| `validated_by` / `validated_at` | string / datetime | posés sur l'étape d'interprétation, jamais sur la valeur source (règle P10/T7) |

### 2.8 Contrôle d'agrégation — *le cœur du produit*
| Champ | Type | Note |
|---|---|---|
| `aggregation.equivalence_key` | string | clé déterministe, voir §3 |
| `aggregation.aggregable` | enum `true \| false \| conditional` | calculé par le moteur |
| `aggregation.refusal_reason` | enum \| null | `SEMANTIC_NON_EQUIVALENCE \| UNKNOWN_VALUE \| OPEN_CONFLICT \| MISSING_DEFINITION \| MISSING_COUNT_TYPE \| PERIOD_MISMATCH \| UNRESOLVED_DUPLICATE \| POPULATION_OVERLAP \| MISSING_PERIOD` (D-17) |
| `aggregation.dedup_key` | string \| null | empreinte projet canonique (twinning, multi-déclaration) |
| `aggregation.suspected_duplicate_of[]` | string[] | jamais fusionné automatiquement |
| `aggregation.coverage` | `{contributing_units, total_units, share} \| null` | rempli quand l'objet **est** un agrégat (règle AGG-4) |
| `parent_measurement_ids[]` | string[] | pour un agrégat : les objets sommés |

### 2.9 Relations entre measurements
`relations[]` : `{relation_type, measurement_id, note}` avec
`relation_type ∈ {subset_of, funnel_stage, same_population_different_metric, restatement_of, conflicts_with}`.

C'est ce qui permet d'afficher **« 200 personnes touchées, dont 120 formées, dont 60 diplômées »** [p. 92] au lieu de `380`. Sans ce champ, le système n'a que deux options, toutes deux fausses : additionner, ou perdre l'information.

---

## 3. La clé d'équivalence (mécanisme central)

Deux Measurement Objects ne sont additionnables que si leurs clés d'équivalence sont **identiques** :

```
equivalence_key = hash(
    metric_code,
    unit.code,
    iaooi_class,
    population.count_type,
    population.internal_external,
    population.dedup_basis,
    period.type,
    subject.type
)
```

Règle complémentaire : si les deux objets ont une `definition.status = specified` et que les textes de définition **diffèrent**, l'agrégation est refusée même si les clés coïncident. Deux `unknown` ne valent pas équivalence : ils produisent `conditional` + avertissement.

C'est ce qui rend exécutable la phrase de la fiche vision — *« mieux vaut afficher deux chiffres distincts et corrects qu'un total flatteur mais faux »*. Le refus n'est pas une opinion du moteur, c'est une comparaison de clés.

### Procédure de décision d'agrégation

```
aggregate(m1..mn):
  1. tout value_status ∈ {extracted, calculated}        sinon REFUS: UNKNOWN_VALUE
  2. aucun dq_ref en resolution_status = UNRESOLVED     sinon REFUS: OPEN_CONFLICT
  3. equivalence_key identiques                          sinon REFUS: SEMANTIC_NON_EQUIVALENCE
  4. définitions compatibles                             sinon REFUS: MISSING_DEFINITION (ou conditional)
  5. count_type renseigné (≠ unknown)                    sinon REFUS: MISSING_COUNT_TYPE
  5bis. période connue (type ≠ unknown, année renseignée) sinon REFUS: MISSING_PERIOD   (D-17)
  6. périodes compatibles (même reporting_year)          sinon REFUS: PERIOD_MISMATCH
  7. aucun dedup_key en collision non résolue            sinon REFUS: UNRESOLVED_DUPLICATE
  8. aucune relation subset_of / funnel_stage entre eux  sinon REFUS: POPULATION_OVERLAP

  si OK →  value            = Σ values
           value_status     = calculated   (+ formula, inputs)
           layer            = SEMANTIC_INTERPRETATION   (jamais OFFICIAL_JCI_FACT — règle P2)
           value_qualifier  = approx si au moins une entrée est approx      (AGG-3)
           verification_status = min(entrées)                               (AGG-2)
           coverage         = {contributing_units, total_units, share}      (AGG-4)
           parent_measurement_ids = [ids]

  si REFUS → l'objet refusé est CONSERVÉ et AFFICHÉ avec sa raison.
             Un refus n'est pas une erreur : c'est un résultat.
```

**AGG-5** : un agrégat moteur ne remplace jamais un total publié par JCI. La comparaison affiche les deux et ouvre un objet de conflit si l'écart dépasse le seuil (seuil = décision d'équipe, non fixé).

---

## 4. Cycle de vie du statut de vérification

Réconciliation de la fiche vision §9 (*Déclarée → Validée / Signalée*) et de Tier 2 §H.2 (*reported → validated → verified*). Les deux sont nécessaires et ne mesurent pas la même chose : la fiche vision décrit un **circuit de gouvernance humain**, Tier 2 décrit un **niveau de preuve**. Retenu :

```
reported ──(contrôles auto OK + revue nationale)──> validated ──(pièce justificative)──> verified
    │                                                    │
    └──────────────> flagged <───────────────────────────┘
         (incohérence manifeste signalée par la nationale — état BLOQUANT)
```

| Statut | Signification | Preuve exigée | Entre dans les agrégats ? |
|---|---|---|---|
| `reported` | Déclaré par la source, aucun contrôle | `source.quote` | Oui, en agrégat **provisoire** marqué comme tel |
| `flagged` | Incohérence manifeste signalée | `flag.reason` | **Non** — bloquant |
| `validated` | Contrôles de cohérence passés + revue | `checks_passed[]` + relecteur | Oui |
| `verified` | Confronté à une pièce justificative | `evidence_refs[]` obligatoire | Oui |

Règles de transition (T1–T7 de Tier 2, complétées) :
- **T1** `reported → validated` : toutes les règles AUTO-CHECKED du champ passées **et** aucun DQC ouvert
- **T2** `validated → verified` : `evidence_refs[]` non vide
- **T3** toute modification de valeur repasse à `reported` et crée une version (ancienne valeur conservée)
- **T4** un `OFFICIAL_JCI_FACT` reste `reported` **définitivement** : le moteur ne peut ni valider ni vérifier un chiffre JCI, le rapport ne décrivant aucune vérification (contrôle V11)
- **T5** `calculated` hérite du plus faible statut de ses entrées ; `estimated` ne dépasse jamais `validated`
- **T6** un DQC ouvert bloque le passage à `validated`
- **T7** `validated_by` / `validated_at` se posent sur l'étape d'interprétation, jamais sur la valeur source
- **T8** *(nouveau)* `flagged` est atteignable depuis n'importe quel état et bloque l'agrégation jusqu'à résolution ; la levée d'un flag repasse à `reported`

Aucune transition ne change jamais la `layer` (règle P10).

---

## 5. Remplissage par étape du pipeline

| Étape | Champs renseignés | Couche produite |
|---|---|---|
| **RAW** | `source.quote`, `source.submitted_at`, `source.language`, `subject` | LOCAL_REPORTED_FACT |
| **STRUCTURED** (extraction LLM) | `value`, `value_qualifier`, `metric_label_source`, `period` brut, `unit` brut | + `derivation[0]` SEMANTIC_INTERPRETATION |
| **STANDARDIZED** (mapping taxonomie LLM) | `metric_code`, `iaooi_class`, `taxonomy_refs`, `unit_normalization`, `population.*` | SEMANTIC_INTERPRETATION + PROPOSED_STANDARD |
| **VALIDATED** | `checks_passed/failed`, `verification_status`, `dq_refs`, `confidence` | statut, couche inchangée |
| **AGGREGATED** | `aggregation.*`, `parent_measurement_ids`, `coverage` | SEMANTIC_INTERPRETATION · calculated |

Un objet ne saute jamais d'étape. Un objet incomplet reste stocké **tel quel**, avec ses trous explicites — il n'est pas rejeté, il est non agrégeable.

---

## 6. Sous-ensemble MVP (48h)

Champs **obligatoires** pour la démo hackathon — le reste du schéma existe mais peut rester `null` :

`measurement_id`, `metric_code`, `metric_label_source`, `definition.status`, `iaooi_class` (+ `rule_id`, `confidence`), `value`, `value_status`, `value_qualifier`, `unit.code`, `subject`, `population.count_type`, `population.internal_external`, `period.reporting_year`, `geography.local_organization`, `layer`, `source.quote`, `derivation[]`, `verification_status`, `aggregation.equivalence_key`, `aggregation.aggregable`, `aggregation.refusal_reason`.

Reportés hors chemin critique (schéma prévu, remplissage partiel) : `unit_normalization` des devises, `population.attributes`, `evidence_refs`, `coverage`, résolution automatique des `dedup_key` (le MVP **signale** les doublons suspects sans les fusionner — cf. §10, divergence D3).

---

## 7. Exemple 1 — fait JCI officiel (`subject.type = network`)

```json
{
  "metric_code": "VOLUNTEERS",
  "metric_label_source": "Total Number of Volunteers Engaged",
  "definition": { "status": "unknown", "text": "NOT SPECIFIED IN THE SOURCE DOCUMENT" },
  "iaooi_class": { "value": "INPUT", "layer": "SEMANTIC_INTERPRETATION",
                   "rule_id": "MAP-METRIC", "confidence": "H" },
  "source_wording_class": "Measurable outcomes",
  "value": 42401, "value_status": "extracted", "value_qualifier": "exact",
  "unit": { "code": "person", "dimension": "count" },
  "subject": { "type": "network", "id": "JCI_GLOBAL", "name": "JCI" },
  "population": { "internal_external": "mixed", "count_type": "unknown",
                  "dedup_basis": "unknown" },
  "period": { "type": "reporting_year", "reporting_year": 2025 },
  "layer": "OFFICIAL_JCI_FACT",
  "source": { "origin": "jci_report_2025", "page": "86",
              "section": "Community Impact",
              "quote": "42,401 Total Number of Volunteers Engaged" },
  "verification_status": "reported",
  "dq_refs": ["DQC-05"],
  "aggregation": { "aggregable": false, "refusal_reason": "OPEN_CONFLICT" }
}
```

Lecture : chiffre officiel JCI, mais **non agrégeable** — conflit DQC-05 ouvert (40 000+ p. v/84 vs 42 401 p. 86), `count_type` inconnu, définition absente. Le système le stocke, l'affiche, et dit pourquoi il ne s'en sert pas.

## 8. Exemple 2 — déclaration locale

```json
{
  "metric_code": "PEOPLE_TRAINED",
  "metric_label_source": "jeunes formés à l'entrepreneuriat",
  "definition": { "status": "specified",
                  "text": "personnes ayant suivi les 3 jours complets" },
  "iaooi_class": { "value": "OUTPUT", "layer": "SEMANTIC_INTERPRETATION",
                   "rule_id": "MAP-METRIC", "confidence": "H" },
  "value": 45, "value_status": "extracted", "value_qualifier": "exact",
  "unit": { "code": "person", "dimension": "count" },
  "subject": { "type": "project", "id": "PRJ-TC1", "name": "Boost PME 2025" },
  "population": { "target_group": ["ENTREPRENEURS_BUSINESSES"], "internal_external": "external",
                  "count_type": "direct", "dedup_basis": "unique_persons" },
  "period": { "type": "range", "start": "2025-09-03", "end": "2025-09-05",
              "reporting_year": 2025 },
  "geography": { "local_organization": "JCI Bouaké Lumière",
                 "country_iso2": { "value": "CI", "layer": "SEMANTIC_INTERPRETATION",
                                   "rule_id": "GEO-FROM-CITY", "confidence": "H" },
                 "geographic_area": { "value": "AFME", "layer": "SEMANTIC_INTERPRETATION",
                                      "rule_id": "GEO-FROM-COUNTRY", "confidence": "M" } },
  "layer": "LOCAL_REPORTED_FACT",
  "source": { "origin": "submission", "document_id": "SUB-TC1",
              "quote": "45 jeunes ont suivi le bootcamp de 3 jours",
              "language": "fr" },
  "verification_status": "validated",
  "checks_passed": ["CHK-UNIT", "CHK-PLAUSIBILITY"],
  "aggregation": { "aggregable": true,
                   "equivalence_key": "PEOPLE_TRAINED|person|OUTPUT|direct|external|unique_persons|range|project" }
}
```

## 9. Exemple 3 — le refus qui vend le produit

Deux objets du même projet : `PEOPLE_TRAINED = 45` (ci-dessus) et `COMM_AUDIENCE = 12 000` (portée Facebook du post de l'événement).

```
equivalence_key A : PEOPLE_TRAINED|person|OUTPUT|direct|external|unique_persons|range|project
equivalence_key B : COMM_AUDIENCE|view|OUTPUT|audience|external|unknown|range|project
→ aggregable = false
→ refusal_reason = SEMANTIC_NON_EQUIVALENCE
→ affichage : « 45 personnes formées » ET « 12 000 vues » — jamais « 12 045 personnes touchées »
```

C'est exactement le piège DQC-08 du rapport réel (impressions présentées à côté de reach). Le moteur ne l'évite pas par prudence : il l'évite par comparaison de clés, et il peut **expliquer** son refus au board.

---

## 10. Divergences avec la fiche vision (conservées, non résolues en silence)

| # | Fiche vision | Tier 1 / Tier 2 / ce document | Traitement retenu |
|---|---|---|---|
| **D1** | §9 statuts : Déclarée / Validée / Signalée | H.2 : reported / validated / verified | **Fusion explicite en 4 états** (§4) : les deux axes sont conservés, `flagged` ajouté comme état bloquant. La fiche vision n'avait pas `verified` (preuve justificative) ; Tier 2 n'avait pas `flagged` (gouvernance humaine). |
| **D2** | §11 « Provenance : réelle mais simple — lien vers le rapport source » | P0/P1 : citation exacte + page + section obligatoires, lignage par étape | Version Tier 1 retenue. Le « lien vers la source » seul ne suffit pas à répondre à « d'où vient ce chiffre ». Coût marginal faible, valeur démo élevée. |
| **D3** | §11 « Déduplication : simplifiée / mock, non prioritaire » | R6 + cas de test TC5 (twinning Bénin–Canada) : double comptage réel | **Compromis** : pas de résolution automatique (trop coûteux en 48h), mais `dedup_key` + `suspected_duplicate_of[]` + refus d'agrégation `UNRESOLVED_DUPLICATE`. Le système **détecte et refuse** sans prétendre résoudre. Cela suffit à passer TC5. |
| **D4** | §3.2 exemples génériques (bootcamp, workshop) | 5 fixtures Tier 1 avec provenance par champ, validées | Les fixtures Tier 1 remplacent les exemples de la fiche vision comme scénario de démo. |
| **D5** | §14 « le Measurement Object est un contenant générique, pas un schéma figé » | Ce document fixe un schéma | Pas de contradiction réelle : le schéma est fixe, **les valeurs de taxonomie sont externes et remplaçables** (`taxonomy.config.json`). C'est le contenant qui est stable, pas le contenu. |
| **D6** | §17 stack proposée : Node/Express + SQLite, React + Leaflet + Recharts | — | Aucune contradiction ; décision technique encore ouverte, à trancher avant Phase 1. |

**La fiche vision reste la référence pour le *pourquoi* (problème, North Star, rôles, modalités de saisie, stratégie de robustesse). Elle n'est pas la référence pour le *comment data*.** Elle mérite une mise à jour post-hackathon, pas une réécriture maintenant.

---

## 11. Décision requise

1. Adopter `MEASUREMENT-OBJECT-v1` comme schéma atomique du système (statut `PROPOSED → ACCEPTED`).
2. Valider la réconciliation D1 (4 états de vérification, `flagged` bloquant).
3. Valider le compromis D3 (déduplication = détection + refus, pas de résolution automatique).
4. Le schéma JSON exécutable est `measurement-object.schema.json` ; il doit être branché dans le backend **avant** tout stockage, au même titre que `validate_provenance.py`.
