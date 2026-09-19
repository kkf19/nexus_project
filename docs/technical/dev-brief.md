# NEXUS — Brief de développement du MVP

> **Mise à jour 2026-09-19 (soir)** : la classification et la page de validation suivent désormais `impact-science.md` (décisions D-23 à D-31 de `mvp-scope.md`). En cas de contradiction avec une section de ce brief, **`impact-science.md` prévaut**. Critères d'acceptation : **AC-01 à AC-31** (AC-16, AC-17 et RI-10 réécrits ; AC-23 à AC-31 ajoutés).

**Statut** : référence de construction pour l'équipe de développement · 2026-09-18
**Remplace, pour l'équipe de dev** : la lecture de Tier 1, de Tier 2, de `data-model.md` et de `measurement-object.md`. Ce document se suffit à lui-même ; les fichiers cités en §8 sont à **brancher**, pas à relire.
**Décisions appliquées** : D-01 à D-16, toutes consignées dans `mvp-scope.md` §1 et repérées `[D-xx]` dans le texte. D-10 à D-16 sont les arbitrages du Product Owner du 18/09 au soir (Annexe C).
**Consignes officielles du hackathon** : au 18/09, aucune exigence technique publiée (constitution de l'équipe et appel à mi-parcours seulement). Une consigne ultérieure pourrait invalider : le choix de stack, le format de démonstration (vidéo, URL déployée) et la langue de l'interface.

Conventions : les identifiants (tables, colonnes, codes, énumérations) sont en anglais, **à l'identique des fichiers sources**. Un identifiant marqué *(proposé)* n'existe dans aucune source : il est introduit par ce brief et reste modifiable. `UNKNOWN` signale une information absente des sources.

---

## 1. Le produit en une page

**Ce que fait NEXUS.** Des organisations locales (OL) de JCI décrivent leurs projets en texte libre, dans leur langue. NEXUS transforme ce texte en **chiffres normalisés**. Chaque chiffre est relié à la phrase exacte dont il provient, puis agrégé aux niveaux local, national et mondial, **uniquement lorsque l'addition a un sens**.

**La chaîne complète** :

```
texte libre saisi (RAW, immuable)
  → extraction IA des chiffres et de leur phrase source (STRUCTURED)
  → classement IA sur la taxonomie externe (STANDARDIZED)
  → contrôles automatiques + confirmation humaine (VALIDATED)
  → agrégation par le moteur, avec refus motivés (AGGREGATED)
  → tableaux de bord OL / national / mondial, avec remontée jusqu'à la phrase source
```

**L'unité de donnée** : le *Measurement Object* (MO) `[D-01]`. Un MO = **un** chiffre (ou l'absence explicite de chiffre), sur **une** population, dans **une** unité, sur **une** période, tiré d'**une** source. Un projet porte plusieurs MO. En base, une ligne de `measurement` = un MO.

**La proposition centrale : le système sait refuser d'additionner, et dit pourquoi.** Chaque MO porte une **clé d'équivalence** (`equivalence_key`) composée de huit éléments : code de métrique, unité, classe (input/output/outcome…), type de comptage, public interne ou externe, base de dédoublonnage, type de période et type de sujet. Deux MO ne s'additionnent que si leurs clés sont identiques et si les contrôles du moteur passent. Sinon le moteur produit un **refus** motivé (`SEMANTIC_NON_EQUIVALENCE`, `UNKNOWN_VALUE`, `OPEN_CONFLICT`, etc.), qui est **stocké et affiché** au même titre qu'un total. Exemple : « 45 personnes formées » et « 12 000 vues Facebook » ne deviennent jamais « 12 045 personnes touchées ».

**Le vocabulaire JCI minimal à connaître** :

| Terme | Sens pour le développeur |
|---|---|
| OL / Local Organization | Le club local qui déclare. Son compte est connecté à la saisie. |
| NO / National Organization | Le niveau national, parent des OL. |
| `area_of_opportunity` | **Axe A**. Domaine d'intervention officiel JCI : `BE`, `ID`, `IC`, `CI`. De 1 à n par projet. |
| `programme` | **Axe B**. Programme JCI, par exemple `RISE`. De 0 à n par projet ; « aucun » est une valeur légitime. |
| `sdgs` | **Axe C**. ODD de l'ONU, de 1 à 17. De 1 à n par projet, dont exactement 1 `primary`. |
| `geographic_area` | Zone géographique JCI : `AFME`, `AMERICA`, `ASPAC`, `EUROPE`. **N'a aucun rapport** avec `area_of_opportunity`. |

Les trois axes A, B et C sont **indépendants** `[D-07]` : aucun ne se déduit d'un autre.

**Quatre couches de provenance** (`layer`), jamais confondues :

| Couche | Signification |
|---|---|
| `OFFICIAL_JCI_FACT` | Cité du rapport JCI 2025, avec page, section et citation. |
| `LOCAL_REPORTED_FACT` | Écrit par l'OL dans sa saisie, avec citation. |
| `SEMANTIC_INTERPRETATION` | Classement, déduction ou calcul fait par NEXUS. |
| `PROPOSED_STANDARD` | Vocabulaire inventé par NEXUS, qui n'est **pas** officiel JCI. |

---

## 2. Schéma de base de données

Types neutres : `TEXT`, `INTEGER`, `DECIMAL`, `BOOLEAN`, `TIMESTAMP`, `JSON` (document JSON natif ou texte JSON selon le SGBD). **Origine** d'une colonne : **U** = saisie ou confirmation utilisateur, **IA** = proposée par un appel LLM, **S** = système (règle déterministe, référentiel ou compte).

Règles transverses :

- **Aucune colonne numérique de valeur n'a de défaut `0`.** `NULL` signifie inconnu.
- Pour les colonnes `JSON` qui portent un tableau, `NULL` signifie « clé absente » et `[]` signifie « liste vide ». La différence compte : `programme = []` veut dire « aucun programme » (règle R9).
- Toutes les énumérations sont celles de `measurement-object.schema.json` et de `taxonomy.config.json`. Elles sont vérifiées par code contre le référentiel chargé, jamais codées en dur dans une contrainte SQL.

### 2.1 `taxonomy_release`: référentiel de taxonomie versionné

Rôle : charger `taxonomy.config.json` tel quel. Toute liste de codes (axes A/B/C, piliers RISE, `input_type`, `output_type`, `outcome_type`, `target_group`, `activity_type`) est lue depuis cette table, jamais écrite en dur.

| Colonne | Type | Origine | Contrainte / note |
|---|---|---|---|
| `version` | TEXT | S | PK. Valeur de `meta.version` (actuellement `0.2.1`, qui ajoute `input_type` `[D-10]`) |
| `content` | JSON | S | Fichier intégral, non modifié |
| `checksum` | TEXT | S | Empreinte du fichier chargé |
| `loaded_at` | TIMESTAMP | S | |
| `is_active` | BOOLEAN | S | Une seule version active |

Chaque `project` et chaque `measurement` enregistre la `taxonomy_version` qui a servi à le classer.

### 2.2 `geo_mapping`: référentiel manuel pays / NO → `geographic_area`

Rôle : dériver `geographic_area`. **JCI ne publie pas cette table** : la carte p. 9 est illisible (VDX-01). Le référentiel est donc saisi à la main, versionné, et **chaque valeur qui en sort reste une `SEMANTIC_INTERPRETATION`** (`rule_id = GEO-FROM-COUNTRY`), jamais un fait JCI.

| Colonne | Type | Origine | Note |
|---|---|---|---|
| `country_iso2` | TEXT | S (saisie admin) | PK avec `mapping_version` |
| `mapping_version` | TEXT | S | |
| `geographic_area` | TEXT | S | `AFME` \| `AMERICA` \| `ASPAC` \| `EUROPE` |
| `confidence` | TEXT | S | `H` \| `M` \| `L` |
| `note` | TEXT | S | Origine de la correspondance |

### 2.3 `organization`

Rôle : les OL et les NO, et leur hiérarchie.

| Colonne | Type | Origine | Note |
|---|---|---|---|
| `organization_id` | TEXT | S | PK |
| `org_type` | TEXT | S | `local` \| `national` *(proposé)* |
| `name` | TEXT | S | Par exemple « JCI Bouaké Lumière » |
| `parent_organization_id` | TEXT | S | FK vers `organization`. Une OL a exactement 1 NO (règle R1) |
| `country_iso2` | TEXT | S | Joint à `geo_mapping` |

### 2.4 `app_user`

Rôle : les trois rôles actés (Admin OL, Admin National, Board mondial).

| Colonne | Type | Note |
|---|---|---|
| `user_id` | TEXT | PK |
| `organization_id` | TEXT | FK. OL pour `admin_ol`, NO pour `admin_national`, NULL pour `board_global` |
| `role` | TEXT | `admin_ol` \| `admin_national` \| `board_global` *(identifiants proposés)* |

### 2.5 `submission`: la pièce source (RAW)

Rôle : conserver pour toujours le texte saisi, tel quel `[D-04]`.

| Colonne | Type | Origine | Contrainte / note |
|---|---|---|---|
| `submission_id` | TEXT | S | PK. Sert de `source.document_id` |
| `organization_id` | TEXT | S | FK. L'OL du compte connecté |
| `user_id` | TEXT | S | FK |
| `raw_text` | TEXT | U | **NOT NULL, jamais modifié** (voir RI-07) |
| `raw_text_sha256` | TEXT | S | Calculé à l'insertion, revérifié à chaque lecture de traçabilité |
| `language` | TEXT | IA | Langue détectée |
| `submitted_at` | TIMESTAMP | S | |
| `pipeline_status` | TEXT | S | `received` → `extracted` → `standardized` → `awaiting_confirmation` → `confirmed` \| `failed` *(proposé)* |
| `pipeline_error` | TEXT | S | Message en cas d'échec |

Aucune opération de mise à jour n'est exposée sur `raw_text`.

### 2.6 `extraction_candidate`: sorties IA non encore confirmées

Rôle : stocker les sorties des étapes 2 et 3 (contrats en §4). Un candidat qui ne passe pas le schéma reste ici, visible, avec ses erreurs. Il n'entre jamais dans `measurement` tant qu'il est invalide.

| Colonne | Type | Origine | Note |
|---|---|---|---|
| `candidate_id` | TEXT | S | PK |
| `submission_id` | TEXT | S | FK |
| `stage` | TEXT | S | `structured` \| `standardized` |
| `payload` | JSON | IA | Objet du contrat d'extraction ou de mapping |
| `model_id` | TEXT | S | Modèle et version du prompt, par exemple `llm_extractor@v0` |
| `validation_errors` | JSON | S | Sortie des validateurs (§8) |
| `created_at` | TIMESTAMP | S | |

### 2.7 `project` et ses tables de classification

Rôle : le conteneur des MO d'une soumission. Les trois axes sont stockés **dans trois tables séparées**. Aucune ne référence les autres `[D-07]`.

**`project`**

| Colonne | Type | Origine | Champ canonique `[D-05]` |
|---|---|---|---|
| `project_id` | TEXT | S | PK. Sert de `subject.id` |
| `submission_id` | TEXT | S | FK |
| `organization_id` | TEXT | S | #2 `organization.local_organization` |
| `name` | TEXT | IA, corrigeable U | #1 `project.name` |
| `reporting_year` | INTEGER | S + IA | #3 `project.reporting_year`. NOT NULL (sinon le moteur refuse `PERIOD_MISMATCH`) |
| `period_start`, `period_end` | TEXT (date ISO) | IA | NULL autorisé |
| `outcome_status` | ENUM(`measured`,`pending_follow_up`,`none`) NOT NULL | U | #12 (D-20) : état des résultats du projet |
| `expected_outcome` | TEXT NULL | U | requis si `pending_follow_up` : effet attendu (libellé libre ou code `outcome_type`) |
| `follow_up_date` | DATE NULL | U | requis si `pending_follow_up` ; relance automatique post-MVP |
| `programme_confirmed` | BOOLEAN | U | Distingue « aucun programme, confirmé » de « pas encore classé » |
| `taxonomy_version` | TEXT | S | FK vers `taxonomy_release` |
| `confirmed_by`, `confirmed_at` | TEXT, TIMESTAMP | S | Posés à la confirmation de la fiche |

`activity.description` (champ #4) **est** `submission.raw_text` : il n'est pas dupliqué.

**Tables de classification** : même structure pour les quatre.

| Table | Axe | Colonne de code | Cardinalité |
|---|---|---|---|
| `project_area_of_opportunity` | A | `code` ∈ `BE`, `ID`, `IC`, `CI` | 1..n (R2) |
| `project_programme` | B | `code` ∈ `programme.values[].code` | 0..n (R9) |
| `project_rise_pillar` | B (composante) | `code` ∈ `REBUILD_ECONOMIES`, `WORKFORCE`, `MENTAL_HEALTH` | 1..n si `RISE` ∈ programmes, sinon 0 (R4) |
| `project_sdg` | C | `goal` INTEGER 1–17 et `role` ∈ `primary`, `secondary`, `unknown` | 1..n, exactement 1 `primary` (R5) |

Colonnes communes : `project_id` (FK), code, `layer` (= `SEMANTIC_INTERPRETATION`), `rule_id`, `confidence`, `proposed_by` (= `llm_classifier@v0`), `confirmed_by`, `confirmed_at`.

Affichage des piliers RISE : libellés `label` du jeu « RISE Pillars Covered ». Le `variant_label` reste chargé. Ce choix n'arbitre pas le conflit DQC-17, qui reste ouvert côté JCI. Le programme `RISE` porte deux jeux d'ODD déclarés (p. 26 et p. 85, DQC-16) : les deux restent dans le référentiel, et **aucun** ne sert à préremplir les ODD d'un projet.

### 2.8 `measurement`: table centrale, une ligne = un chiffre

Rôle : stocker un MO complet, conforme à `measurement-object.schema.json`. **Aucune ligne n'est insérée sans passer les validateurs (§8).** Les objets imbriqués sont éclatés en colonnes quand on filtre ou agrège dessus, et gardés en `JSON` sinon. La correspondance complète, champ par champ, est vérifiée en Annexe B.

| Colonne | Type | Origine | Note |
|---|---|---|---|
| `measurement_id` | TEXT | S | PK |
| `standard` | TEXT | S | Constante `PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1` |
| `created_at`, `updated_at` | TIMESTAMP | S | |
| `submission_id`, `project_id`, `organization_id` | TEXT | S | FK de service, NULL pour les chiffres JCI de référence et les agrégats |
| `taxonomy_version` | TEXT | S | |
| `metric_code` | TEXT | IA | NOT NULL. Code `input_type` (`VOLUNTEERS`, `VOLUNTEER_HOURS` `[D-10]`), `output_type` ou `outcome_type` du référentiel. Exceptions : les chiffres JCI de référence (subject `network`) gardent le code de leur exemple, par exemple `MEMBERS_BY_AREA` |
| `metric_label_source` | TEXT | IA | NOT NULL. **Mots exacts de la source** |
| `definition_status` / `definition_text` / `definition_layer` / `definition_source_ref` | TEXT | IA | Si `unknown`, alors texte = `NOT SPECIFIED IN THE SOURCE DOCUMENT`. **Jamais inventé** |
| `iaooi_value` / `iaooi_layer` / `iaooi_standard` / `iaooi_rule_id` / `iaooi_confidence` | TEXT | IA | `INPUT`, `ACTIVITY`, `OUTPUT`, `OUTCOME`, `IMPACT_CLAIM`, `CONTEXT` ou `UNCERTAIN`. Couche = `SEMANTIC_INTERPRETATION` |
| `source_wording_class` | TEXT | IA | Comment la source a nommé ce chiffre (par exemple « Measurable outcomes ») |
| `taxonomy_refs` | JSON | S | Copie, au moment de la standardisation, des axes du projet et des codes de mesure |
| `value` | DECIMAL | IA / U | **NULL autorisé, aucun défaut** |
| `value_status` | TEXT | IA / S | `extracted`, `calculated`, `estimated`, `unknown`, `visual_data_not_extracted` ou `conflicting` |
| `value_qualifier` | TEXT | IA | `exact`, `approx`, `at_least`, `at_most` ou `range` |
| `value_range` | JSON | IA | Requis si `range` |
| `unit_code` / `unit_dimension` / `unit_currency_code` / `unit_sub_code` | TEXT | IA | |
| `unit_normalization`, `formula`, `inputs`, `method`, `assumptions`, `conflicting_values` | JSON / TEXT | S | Voir le schéma. `formula` et `inputs` sont requis si `calculated` |
| `subject_type` / `subject_id` / `subject_name` | TEXT | S | `project`, `organization`, `event`, `program` ou `network` |
| `pop_internal_external` | TEXT | IA → **U** | `internal`, `external`, `mixed` ou `unknown` |
| `pop_count_type` | TEXT | IA → **U** | `direct`, `indirect`, `audience`, `unique`, `cumulative` ou `unknown` |
| `pop_dedup_basis` | TEXT | IA | `unique_persons`, `attendances`, `households` ou `unknown` |
| `pop_target_group` / `pop_base_population` / `pop_attributes` | JSON | IA | `base_population` est requis si l'unité est `percent` ou `ratio` |
| `period_type` / `period_start` / `period_end` / `period_reporting_year` | TEXT, INTEGER | S / IA | Pour toute mesure de projet : `period_type = reporting_year`, dates conservées `[D-11]` |
| `geography` | JSON | S | 4 niveaux `{value, layer, rule_id, confidence}`. `local_organization`, `national_organization` et `country_iso2` viennent du compte de l'OL, en couche `LOCAL_REPORTED_FACT` `[D-15]`. `geographic_area` vient de `geo_mapping`, en `SEMANTIC_INTERPRETATION`, `GEO-FROM-COUNTRY`. Jamais de clé `area` nue |
| `layer` | TEXT | S | Voir §1 |
| `source_origin` / `source_document_id` / `source_page` / `source_section` / `source_quote` / `source_submitted_at` / `source_language` | TEXT | S / IA | `source_quote` est une **sous-chaîne exacte** de `raw_text` pour une soumission |
| `source_span` | JSON | IA | `{start, end}` : positions dans `raw_text` |
| `confidence` | TEXT | IA | `H`, `M` ou `L` |
| `verification_status` | TEXT | S / U | `reported`, `flagged`, `validated` ou `verified` `[D-02]` |
| `evidence_refs`, `checks_passed`, `checks_failed`, `dq_refs`, `flag` | JSON | S / U | |
| `validated_by`, `validated_at` | TEXT | U | |
| `agg_equivalence_key` | TEXT | **S** | Calculée par `equivalence_key()` du moteur, **jamais par l'IA** |
| `agg_aggregable` | TEXT | S | Résultat de `eligibility()` du moteur `[D-14]` : `false` + raison si la valeur est inconnue, sous conflit ouvert, signalée, sans type de comptage ou en `percent`/`ratio` ; sinon `true`. Les refus entre deux mesures vont dans `refusal`, pas ici. Sérialisé en booléen JSON à l'export |
| `agg_refusal_reason` | TEXT | S | Énumération fermée du schéma |
| `agg_dedup_key` / `agg_suspected_duplicate_of` / `agg_coverage` | TEXT / JSON | S | `dedup_key` est stocké mais **non lu** `[D-03]` |

Index utiles : (`organization_id`, `period_reporting_year`), `agg_equivalence_key`, `metric_code`, `project_id`, `verification_status`.

### 2.9 Tables filles de `measurement`

| Table | Rôle | Colonnes |
|---|---|---|
| `derivation` | Lignage, étape par étape, porté par l'objet | `measurement_id` (FK), `position` INTEGER (ordre), `step`, `rule_id`, `agent`, `input_refs` JSON, `confidence`, `timestamp` |
| `measurement_relation` | Liens entre chiffres non additionnables (entonnoir, sous-ensemble) | `measurement_id` (FK), `relation_type` (`subset_of`, `funnel_stage`, `same_population_different_metric`, `restatement_of` ou `conflicts_with`), `target_measurement_id`, `note` |
| `measurement_parent` | Entrées d'un agrégat (`parent_measurement_ids`) | `measurement_id` (l'agrégat), `parent_measurement_id`, `position`. **Pas de FK bloquante** : l'intégrité est contrôlée par CTL-TRACE (§5) |
| `measurement_version` | Règle T3 : toute modification de valeur conserve l'ancienne | `measurement_id`, `version_no`, `snapshot` JSON (MO complet), `changed_by`, `changed_at` |

### 2.10 `aggregate` et `refusal`: résultats du moteur

Un agrégat **est lui-même un MO** (`value_status = calculated`, `layer = SEMANTIC_INTERPRETATION`, `source.origin = engine`). Il est écrit dans `measurement`, via `Aggregate.to_measurement_object()`, avec ses entrées dans `measurement_parent`. La table `aggregate` décrit l'exécution qui l'a produit.

**`aggregate`**

| Colonne | Type | Note |
|---|---|---|
| `aggregate_run_id` | TEXT | Identifiant d'exécution |
| `measurement_id` | TEXT | FK vers le MO agrégat |
| `view` | TEXT | `ol`, `national` ou `global` |
| `scope_organization_id` | TEXT | NULL pour `global` |
| `group_by` | TEXT | `subject`, `geography` ou `network` (paramètre du moteur) |
| `group_label` | TEXT | Par exemple `geographic_area:AFME` |
| `filters` | JSON | Année, axes A/B/C appliqués |
| `engine_version` | TEXT | Empreinte de `aggregation_engine.py` |
| `computed_at` | TIMESTAMP | |

**`refusal`** : une ligne par refus du moteur, sans exception.

| Colonne | Type | Note |
|---|---|---|
| `refusal_id` | TEXT | PK |
| `aggregate_run_id` | TEXT | NULL pour un contrôle de paire à la demande |
| `reason` | TEXT | Énumération `refusal_reason` du schéma |
| `measurement_ids` | JSON | Un id (exclusion individuelle) ou plusieurs (conflit de paire) |
| `detail` | TEXT | `Refusal.detail` (par exemple les deux clés comparées) |
| `explanation_fr` | TEXT | `Refusal.explain()` |
| `created_at` | TIMESTAMP | |

### 2.11 `quality_issue`: registre des conflits documentaires JCI

Rôle : charger `jci_data_quality_registry_v2.json`, qui contient 26 conflits `DQC-xx`, tous `UNRESOLVED`, et 9 visuels `VDX-xx` non extraits. Colonnes : `issue_id` (PK), `kind` (`conflict` ou `visual`), `subject`, `values` JSON (toutes les valeurs, aucune choisie), `resolution_status`, `displayed` BOOLEAN. `displayed = true` **uniquement** pour DQC-01, DQC-03, DQC-13 et DQC-24. Le registre compte **26** conflits. L'écart 53,47 % RISE contre 44,64 % Community Impact **n'en est pas un** (erreur de modélisation NEXUS, corrigée par D-07) et ne doit pas être ajouté.

---

## 3. Les trois écrans

### 3.1 Saisie

| | |
|---|---|
| **Affiche** | Un seul champ de texte multiligne, une consigne (« Racontez votre activité comme à un collègue, dans votre langue ») et un bouton « Envoyer ». Aucun menu, aucune case `[D-04]`. OL, NO, année et langue ne sont jamais demandés. |
| **L'utilisateur** | Écrit, puis envoie. |
| **Écrit en base** | `submission`, avec `raw_text`, `raw_text_sha256` et `pipeline_status = received`. Ensuite, de façon asynchrone : `extraction_candidate` pour les étapes 2 et 3. |
| **En cas d'échec** | Texte vide : refus côté client. Erreur ou délai dépassé à l'appel IA : `pipeline_status = failed`, le texte **reste enregistré**, l'écran affiche « Analyse impossible, votre texte est conservé » et propose « Relancer l'analyse », qui repart du même `submission_id`. On ne demande jamais de ressaisir. |

### 3.2 Confirmation (fiche préremplie)

**Affiche** : une fiche où chaque case porte son **origine** : *tu l'as écrit* (extrait avec citation), *déduit — à confirmer* (IA), *ton compte* (système) ou **manquant**. Chaque chiffre affiche sa phrase source surlignée dans le texte d'origine.

Contenu, dans l'ordre des 13 champs canoniques `[D-05]` : nom du projet, OL, année et période, domaine(s) d'intervention (axe A), ODD avec le principal (axe C), programme(s) (axe B, avec « aucun programme » comme option explicite) et piliers RISE (uniquement si RISE est coché), bénévoles, heures, bénéficiaires avec type de comptage et public, résultats mesurables.

Un bloc séparé, **« Classé à part — non compté comme bénéficiaires »**, liste les chiffres d'audience (`COMM_AUDIENCE`).

**Quatre confirmations humaines obligatoires**. Chacune exige une action explicite, et le bouton « Confirmer la fiche » reste inactif tant qu'une seule manque :

| # | Confirmation | Pourquoi elle est bloquante |
|---|---|---|
| C1 | `count_type` des bénéficiaires (`direct` / `indirect` / `audience`) | Sans lui, aucun total n'a de sens |
| C2 | `internal_external` (membres JCI / public externe) | Les deux populations ne s'additionnent jamais (R7) |
| C3 | ODD, avec exactement 1 principal | Le sur-étiquetage est le défaut documenté de la source (DQC-22) |
| C4 | ≥ 1 résultat mesurable **ou** case « aucun résultat mesuré à ce stade » | Seule question posée si le champ manque (`mvp-scope.md` §2, étape 3) |

Les axes A et B (et les piliers RISE) sont préremplis « déduit — à confirmer ». L'utilisateur les corrige d'un clic, et ils sont confirmés par la validation de la fiche (`confirmed_by`) `[D-16]`.

**L'utilisateur** : corrige une valeur, change une classification, répond à C1–C4, puis confirme.

**Écrit en base** lors de la confirmation, en une seule transaction :

- `project` et ses 4 tables de classification ;
- un `measurement` par chiffre retenu, avec `verification_status = reported` et `layer = LOCAL_REPORTED_FACT` ;
- les lignes `derivation` (`extract_number`, `classify`, `human_validation` si l'utilisateur a corrigé) ;
- les lignes `measurement_relation` proposées.

**Aucune ligne `measurement` n'est créée pour un résultat absent** : choisir « pas encore mesurable » (`outcome_status = pending_follow_up`, + effet attendu et date de suivi) ou « aucun effet mesurable visé » (`outcome_status = none`) **ne crée pas** de valeur 0 (D-20).

**En cas d'échec** : un candidat qui ne passe pas les validateurs reste affiché en rouge avec la question qui le débloque. Exemple : un pourcentage sans base affiche « Sur combien de personnes ? ». L'utilisateur peut répondre ou retirer le chiffre. Un code de taxonomie inconnu du référentiel est rejeté, jamais enregistré. Si la transaction échoue, rien n'est écrit, la fiche reste à l'écran et la saisie est conservée.

### 3.3 Tableaux de bord : un moteur, trois vues

| Vue | Rôle | Périmètre des MO envoyés au moteur |
|---|---|---|
| OL | `admin_ol` | MO de son `organization_id` |
| Nationale | `admin_national` | MO des OL dont `parent_organization_id` = sa NO |
| Mondiale | `board_global` | Tous les MO |

Le même appel `aggregate()` sert aux trois vues ; seul l'ensemble filtré en entrée change. Filtres disponibles : `reporting_year`, puis **chacun des trois axes, séparément**.

**Chaque vue affiche** :

1. **Agrégats** : une ligne par clé d'équivalence avec `metric_code`, valeur (préfixe « ≈ » si `approx`), unité, statut de vérification, couverture et nombre d'entrées. Un agrégat dont le statut est `reported` porte le badge « provisoire ».
2. **Refus** : toutes les lignes `refusal` de l'exécution, avec leur explication. Elles ne sont jamais masquées ni repliées par défaut.
3. **Traçabilité** : cliquer sur un agrégat descend vers ses MO d'entrée, puis vers le projet, puis vers l'OL, puis vers le texte brut, citation surlignée.
4. **Vue mondiale uniquement, « Chiffres publiés par JCI »** : les chiffres de référence `OFFICIAL_JCI_FACT` affichés **à côté** du calcul NEXUS, jamais à sa place (AGG-5), ainsi que les 4 conflits DQC-01, DQC-03, DQC-13 et DQC-24 avec toutes leurs valeurs.

Une valeur `NULL` s'affiche « inconnu ». **Aucune cible, aucun objectif, aucune jauge de progression, aucun pourcentage d'atteinte** `[D-09]`.

**Écrit en base** : `aggregate` (et les MO agrégats dans `measurement` et `measurement_parent`) et `refusal`, à chaque calcul. En cas d'échec du moteur, l'écran affiche la dernière exécution réussie avec sa date. **On n'affiche jamais un total partiel calculé hors moteur.**

---

## 4. Pipeline et contrats d'interface

| # | Étape | Entrée | Sortie | Exécutant | Écrit en base |
|---|---|---|---|---|---|
| 1 | **RAW** | Texte saisi | `submission` | Système | `submission` (immuable) |
| 2 | **STRUCTURED** | `raw_text` | Contrat d'extraction (§4.1) | **Appel LLM réel** (`llm_extractor@v0`) + contrôles déterministes | `extraction_candidate(stage=structured)` |
| 3 | **STANDARDIZED** | Contrat d'extraction + `taxonomy_release` active | Contrat de mapping (§4.2) | **Appel LLM réel** (`llm_classifier@v0`) + règles (clé d'équivalence, géographie) | `extraction_candidate(stage=standardized)` |
| 4 | **VALIDATED** | MO candidats + confirmations | MO conformes | Règles (validateurs §8) + **humain** (écran 3.2 ; revue nationale) | `project`, `measurement`, `derivation`, `measurement_relation` ; plus tard `verification_status` |
| 5 | **AGGREGATED** | MO filtrés par vue | Agrégats + refus | **Règle déterministe** : `aggregation_engine.py` | `measurement` (agrégats), `measurement_parent`, `aggregate`, `refusal` |

Aucune donnée ne saute d'étape. Un MO passe toujours par l'état « candidat » avant d'entrer dans `measurement`.

### 4.1 Contrat de sortie de l'extraction (étape 2)

Le prompt d'extraction n'existe pas encore. Voici le contrat autour duquel coder. L'identifiant `NEXUS-EXTRACTION-v0` et les noms de champs hors schéma MO sont *(proposés)*.

```json
{
  "contract": "NEXUS-EXTRACTION-v0",
  "submission_id": "SUB-...",
  "language": "fr",
  "project": {
    "name":   { "value": "Bootcamp entrepreneuriat Bouaké", "origin": "inferred", "quote": null },
    "period": { "start": "2025-09-03", "end": "2025-09-05", "reporting_year": 2025,
                "quote": "Du 3 au 5 septembre" }
  },
  "candidates": [
    {
      "candidate_id": "C1",
      "quote": "45 jeunes ont suivi les trois jours complets",
      "span": { "start": 83, "end": 127 },
      "metric_label_source": "jeunes ont suivi les trois jours complets",
      "value": 45,
      "value_qualifier": "exact",
      "value_range": null,
      "unit_raw": "jeunes",
      "is_rate": false,
      "base_population_raw": null,
      "definition_text": "personnes ayant suivi les trois jours complets",
      "confidence": "H"
    },
    {
      "candidate_id": "C2",
      "quote": "environ 150 heures au total",
      "span": { "start": 170, "end": 197 },
      "metric_label_source": "heures au total",
      "value": 150,
      "value_qualifier": "approx",
      "value_range": null,
      "unit_raw": "heures",
      "is_rate": false,
      "base_population_raw": null,
      "definition_text": null,
      "confidence": "H"
    }
  ],
  "unparsed_numbers": [
    { "quote": "3 au 5", "reason": "date, not a measurement" }
  ]
}
```

Obligations du contrat, chacune vérifiée par code :

- `quote` est une **sous-chaîne exacte** de `raw_text`, et `span` pointe sur elle (CTL-QUOTE).
- **Tout nombre du texte** apparaît soit dans `candidates`, soit dans `unparsed_numbers` avec une raison. Aucun chiffre n'est ignoré en silence (CTL-NUMBERS).
- `value = null` si le nombre est illisible ou absent. Jamais 0.
- « environ », « plus de », « au moins » deviennent `approx`, `at_least`, etc. Le qualificatif **ne change pas** `value_status` : une valeur extraite approximative reste `extracted`.
- `definition_text = null` si le texte ne définit rien. Il devient `definition.status = unknown` à l'étape 3.
- La sortie est validée contre ce contrat. JSON invalide → une nouvelle tentative, puis `pipeline_status = failed`.

### 4.2 Contrat de sortie du mapping (étape 3)

Pour chaque candidat : `metric_code`, `iaooi_class {value, rule_id: "MAP-METRIC", confidence}`, `unit {code, dimension}`, `population {count_type, internal_external, dedup_basis, target_group[]}`, `source_wording_class` et `definition {status, text}`. Au niveau du projet : `area_of_opportunity[]`, `programme[]`, `rise_pillars[]` et `sdgs[{goal, role}]`, chacun avec `confidence` et une justification. Viennent ensuite `activity_type[]` (déduit, jamais demandé `[D-08]`) et `relations[]` proposées (`subset_of`, `funnel_stage`, `same_population_different_metric`).

Contraintes :

- Chaque code est **contrôlé contre `taxonomy_release`**. Un code absent du référentiel est rejeté (CTL-TAXO).
- Les trois axes sont produits par **trois décisions séparées**, chacune avec sa propre ligne de dérivation. Aucune n'a l'autre en entrée (CTL-AXES).
- `typical_sdgs` et `chapter_placement_in_report` **ne servent pas** de règle de déduction.
- Un « Area » ambigu dans le texte reçoit la marque `AMBIGUOUS_AREA`. Le LLM ne tranche jamais (règle P7).
- Le LLM ne choisit pas `period.type` : **le système** le fixe à `reporting_year` pour toute mesure de projet, et reporte les dates extraites dans `start`/`end` `[D-11]`.
- Après le LLM, **le système** calcule `agg_equivalence_key` avec `equivalence_key()`, prend OL, NO et pays dans le compte `[D-15]` et dérive `geographic_area` depuis `geo_mapping`.

---

## 5. Règles inviolables

Chaque règle est associée à un contrôle nommé. Les contrôles V*n*, E*n* et les titres du schéma existent déjà dans les fichiers de §8. Les contrôles `CTL-*` sont *(proposés)* et mettent en œuvre une règle des sources.

| # | Règle | Exemple de violation | Contrôle automatique |
|---|---|---|---|
| RI-01 | **Un code de classement n'est jamais un fait JCI officiel** (P0/P5) | `metric_code` ou `iaooi_class` avec `layer = OFFICIAL_JCI_FACT` | Schéma : `iaooi_class.layer` et `taxonomy_refs.layer` valent la constante `SEMANTIC_INTERPRETATION` · `validate_provenance` **V6** |
| RI-02 | **Inconnu n'est jamais zéro** (P4) | Graphique illisible stocké `value = 0` (BAD-01) | Schéma « P4 - unknown is not zero » · **V3** · moteur `UNKNOWN_VALUE` · CTL-NODEFAULT : aucune colonne de valeur avec défaut 0 (test de migration) |
| RI-03 | **La clé d'équivalence commande l'agrégation** | Additionner deux chiffres parce qu'ils sont tous deux en `person` | **E1** : clé stockée = clé recalculée · le moteur regroupe par clé · `pair_compatibility()` → `SEMANTIC_NON_EQUIVALENCE` |
| RI-04 | **Membres JCI et public externe ne s'additionnent jamais** (R7) | 340 membres formés + 275 jeunes externes = 615 | `internal_external` est le 5ᵉ composant de la clé · confirmation C2 · test AC-06 |
| RI-05 | **Un chiffre JCI reste `reported` définitivement** (T4) | `OFFICIAL_JCI_FACT` passé `validated` ou `verified` (BAD-03) | Schéma « T4 » · **V11** · l'API de revue refuse toute transition sur `layer = OFFICIAL_JCI_FACT` |
| RI-06 | **Un refus se stocke et s'affiche** | Refus du moteur journalisé mais absent de l'écran ; `aggregable = false` sans raison (BAD-05) | Schéma « A refusal must state its reason » · CTL-REFUSAL : après chaque exécution, nombre de lignes `refusal` = `len(excluded) + len(refusals)` |
| RI-07 | **Le texte brut saisi n'est jamais modifié** | Correction d'une faute dans `raw_text` | Aucune route de mise à jour · CTL-RAW : `sha256(raw_text)` = `raw_text_sha256` à chaque lecture de traçabilité |
| RI-08 | **Tout fait cite sa source** (P1/P9) | MO local sans `source.quote` (BAD-06) ; citation reformulée | Schéma « P1/P9 » · **V2** · CTL-QUOTE : `source_quote` est une sous-chaîne de `raw_text` |
| RI-09 | **Un calcul n'est jamais officiel** (P2) | Somme d'abonnés stockée en `OFFICIAL_JCI_FACT` (BAD-02) | Schéma « P2 » · **V4** · **V10** |
| RI-10 | **Programmes = activités ; RISE seulement sous Community Impact** (`[D-23]`, `[D-24]`, remplace l'ancienne règle « trois axes indépendants » de D-07) | Projet réservé aux membres classé `CI` ; RISE proposé sur un projet sans `CI` | Validation : `rise_status = not_applicable` si `CI` ∉ Areas ; public 100 % interne ⇒ `CI` refusé · tests AC-17, AC-24, AC-25 |
| RI-11 | **Pas de ratio sans base** (DQC-12/13) | « 75 % placés » sans effectif (BAD-04) | Schéma « Ratio without a base is meaningless » |
| RI-12 | **Pas de clé `area` nue** (P7) | `{"area": "AFME"}` | **V9** · schéma `geography.additionalProperties = false` |
| RI-13 | **Aucune cible, aucun objectif** `[D-09]` | Colonne `target`, barre « 53 % / objectif 60 % » | CTL-NOTARGET : aucun identifiant `target`, `goal_value` ou `objective` dans le schéma de base ni dans l'API (vérification statique en CI) |
| RI-15 | **Un pourcentage ou un ratio ne s'additionne jamais** `[D-13]` | 20 % (OL A) + 30 % (OL B) affichés « 50 % » | `eligibility()` du moteur : refus `SEMANTIC_NON_EQUIVALENCE`, détail « unité non additive » · test AC-21 |
| RI-14 | **Traçabilité complète** | Agrégat mondial dont une entrée est introuvable | CTL-TRACE : chaque `measurement_parent` se résout, et chaque MO local se résout vers une `submission`. Sinon l'agrégat est affiché « chaîne incomplète » |

---

## 6. Critères d'acceptation

Les commandes supposent l'arborescence du dépôt. « Moteur démo » désigne `python3 backend/engine/aggregation_engine.py backend/engine/demo_measurements.json --group-by network`. « Validateur » désigne `python3 docs/technical/validate_measurement_objects.py`.

| ID | Étant donné | Quand | Alors |
|---|---|---|---|
| AC-01 | Deux saisies de vocabulaire différent : le texte FR de `mvp-scope.md` §2 (« 45 jeunes ont suivi les trois jours complets ») et un texte EN contenant « 80 youth were trained in livelihood skills » | Les deux passent les étapes 1 à 4 | Les deux MO ont `metric_code = PEOPLE_TRAINED`, `iaooi_value = OUTPUT`, `unit_code = person`, `pop_count_type = direct`, `pop_internal_external = external`, **la même `agg_equivalence_key`**, et le moteur les additionne dans un même agrégat |
| AC-02 | Le moteur démo | Il s'exécute | `PEOPLE_TRAINED` externe vaut ≈ 275 et ne contient pas `MO-CI-BOUAKE-REACH` ; `COMM_AUDIENCE` forme une ligne séparée (≈ 12 000 `view`) ; aucune valeur 12 045 ni 12 275 n'apparaît. `pair_compatibility(MO-TC1-TRAINED, MO-TC1-REACH)` renvoie `SEMANTIC_NON_EQUIVALENCE` |
| AC-03 | Le MO `BAD-04` (75 % sans base) | Le validateur s'exécute | Rejet : `population: 'base_population' is a required property`. Côté pipeline : « 75 % ont trouvé un emploi » sans effectif reste en `extraction_candidate`, **n'entre pas** dans `measurement`, et l'écran 3.2 pose la question de la base |
| AC-04 | `MO-VDX-01` (graphique illisible) et `BAD-01` (inconnu forcé à 0) | Insertion puis agrégation | `MO-VDX-01` est stocké avec `value = NULL`, exclu par le moteur (`UNKNOWN_VALUE`) et affiché « inconnu ». `BAD-01` est rejeté (`value: 0 is not of type 'null'`) |
| AC-05 | Un agrégat mondial `PEOPLE_TRAINED` issu de saisies réelles (AC-01) | Le Board ouvre la traçabilité | L'enchaînement agrégat → `measurement_parent` → MO d'entrée → `project` → OL → `submission.raw_text` affiche la phrase source surlignée ; CTL-RAW et CTL-TRACE passent |
| AC-06 | Le moteur démo | Il s'exécute | `MO-DE-MEMBERS-TRAINED` (340, `internal`, `event`) forme un agrégat distinct ; il n'est jamais sommé aux 275 externes |
| AC-07 | Le moteur démo | Il s'exécute | Refus `POPULATION_OVERLAP` sur `MO-DE-REACHED + MO-DE-GRADUATED`, stocké dans `refusal`. La valeur affichée est 200, jamais 320 |
| AC-08 | Le moteur démo | Il s'exécute | `MO-JCI-VOLUNTEERS` est exclu avec `OPEN_CONFLICT` (DQC-05) et apparaît dans le bloc Refus |
| AC-09 | `BAD-03` (chiffre JCI `verified`) | Le validateur s'exécute ; ou l'API de revue tente `validate` sur un `OFFICIAL_JCI_FACT` | Rejet dans les deux cas |
| AC-10 | Le moteur démo `[D-03]` | Il s'exécute | Les deux déclarations du jumelage (60 + 60) sont **toutes deux** comptées dans les ≈ 275 ; **aucun** refus `UNRESOLVED_DUPLICATE` |
| AC-11 | Le moteur démo | Il s'exécute | L'agrégat externe `PEOPLE_TRAINED` porte `value_qualifier = approx` (Lima est `approx`, AGG-3) et `verification_status = reported` (Manila est `reported`, AGG-2) |
| AC-12 | Toute exécution du moteur | Après écriture | CTL-REFUSAL : nombre de lignes `refusal` = exclus + refus de paire. Pour le moteur démo : **3** |
| AC-13 | Une `submission` existante | Tentative de modification de `raw_text` par l'API | Refus (aucune route) ; empreinte inchangée |
| AC-14 | `BAD-02`, `BAD-05`, `BAD-06` | Le validateur s'exécute | Les trois sont rejetés, pour les motifs P2, refus sans raison et P1 |
| AC-15 | Les 5 objets `valid` de `measurement-object.examples.json` | Insertion en base puis réexport en MO | Réexport **identique** à l'original, clés `_` exclues (comparaison profonde), et le validateur passe |
| AC-16 | Fiche de confirmation avec un des 18 champs obligatoires de `impact-science.md` §6 vide (ex. durée de l'activité, nombre de membres JCI bénévoles) `[D-28]` | Clic sur « Soumettre » ou appel direct à l'API de confirmation | Bouton inactif ; l'API répond 422 en nommant le champ ; rien n'est écrit. `0` saisi explicitement est accepté, un champ vide ne l'est jamais |
| AC-17 | (a) « Formation au leadership de 80 membres pendant le congrès national » ; (b) « Formation de 100 jeunes sans emploi + mise en relation avec des employeurs » `[D-24]` | Étape 3 puis confirmation | (a) `CI` non proposé, `rise_status = not_applicable`, bloc RISE masqué. (b) `CI` proposé, `rise_status = yes`, pilier `WORKFORCE`. Décocher `CI` sur (b) remet `rise_status = not_applicable` et efface les piliers |
| AC-18 | Le SG choisit « pas encore mesurable » ou « aucun effet mesurable visé » | Confirmation | `outcome_status ∈ {pending_follow_up, none}` ; si `pending_follow_up`, `expected_outcome` et `follow_up_date` non nuls ; **aucune** ligne `measurement` `OUTCOME` avec valeur 0 |
| AC-19 | Les trois vues du tableau de bord | Affichage | Aucun élément de cible ou d'objectif (CTL-NOTARGET) ; toute valeur `NULL` s'affiche « inconnu » |
| AC-20 | `demo_measurements.json` chargé en base | Le système calcule `agg_equivalence_key` avant validation | Les 11 objets passent le validateur (vérifié : sans clé calculée, 9 objets échouent) |
| AC-21 | Deux MO en `percent` de même clé (par exemple deux « taux d'insertion » avec leur base) | Le moteur s'exécute | Aucun agrégat produit ; deux lignes `refusal` `SEMANTIC_NON_EQUIVALENCE` avec le détail « unité non additive : percent (D-13) » ; les deux taux restent visibles par projet |
| AC-22 | Une saisie avec dates (« du 3 au 5 septembre ») et une autre sans date, même année, même métrique | Étapes 1 à 4 | Les deux MO ont `period_type = reporting_year` et la même clé ; les dates de la première sont conservées `[D-11]` |
| AC-23 | Les 9 textes de référence T1–T9 (`impact-science.md` §3) `[D-25]` `[D-26]` | Étapes 1 à 3 | Pour chacun : familles attendues présentes, Area principale attendue, `rise_status` attendu, ODD principal parmi ceux du tableau. Chaque valeur proposée porte une phrase justificative citée du texte |
| AC-24 | Un texte dont le public est 100 % membres JCI (T3, T5) | Étape 3, puis tentative de confirmer avec `CI` coché | L'IA ne propose pas `CI` ; l'API refuse la confirmation « public interne ⇒ Community Impact impossible (D-26) » |
| AC-25 | Tentatives de confirmation incohérentes sur RISE | API de confirmation | Refus si `rise_status = yes` sans `CI` ; refus si `rise_status = yes` sans pilier ; refus si `CI` coché et `rise_status` vide |
| AC-26 | Areas avec 0 ou 2 Areas `primary` | API de confirmation | Refus ; exactement 1 `primary` exigé |
| AC-27 | Famille `*_OTHER` ou `OTHER` sans libellé | API de confirmation | Refus ; libellé libre obligatoire |
| AC-28 | 5 ODD cochés, dont 1 principal, chacun justifié `[D-27]` | Confirmation | Accepté (aucun plafond). 0 ou 2 principaux ⇒ refus |
| AC-29 | 12 membres JCI bénévoles, durée 3 h `[D-30]` | Page de confirmation | Heures préremplies à 36, étiquette « calculé » ; ligne `derivation` avec la formule `VOLUNTEERS × activity_duration_hours`. Si le SG corrige à 50 : valeur stockée 50, origine `reported`, la dérivation n'est plus appliquée |
| AC-30 | Public mixte : 30 membres + 45 externes | Confirmation puis moteur | Deux mesures distinctes (`internal` / `external`) ; aucun agrégat ne vaut 75 ; « Personnes touchées — public externe » vaut 45 |
| AC-31 | Un projet BE (principale) + CI (secondaire) `[D-29]` | Tableau de bord | Il apparaît dans les blocs BE et CI (mention « Area secondaire ») ; la vue d'ensemble le compte une seule fois ; aucune somme des 4 blocs n'est affichée ; RISE affiché avec deux ratios étiquetés (base CI / base tous projets) |

---

## 7. Hors périmètre — ne pas construire

| Élément | Statut | Consigne pour l'agent de codage |
|---|---|---|
| **Déduplication** `[D-03]` | Désactivée : `DEDUP_ENABLED = False` | Ne pas activer ce drapeau. Ne pas écrire de fusion, de signalement ni de refus `UNRESOLVED_DUPLICATE`. `dedup_key` et `suspected_duplicate_of` sont **stockés et jamais lus**. Le double comptage du jumelage (TC5) est le comportement attendu. |
| **Import PDF** | Hors chemin critique | Aucun téléversement de fichier. La seule entrée est le texte libre. |
| **Type d'impact** (`impact_type`) `[D-08]` | Désactivé | Pas de champ, pas de question, pas de classement d'impact. |
| **Les 33 champs écartés** `[D-05]` | Hors MVP | Ne pas collecter, entre autres : `need_statement`, `objective`, `lead_contact`, `member_split`, ressources financières et en nature, partenaires, `participants_unique`, `registrations`/`attendees` saisis séparément, `physical_output`, méthode et horizon des résultats, `new_members` dédié, `impact[]`, `evidence[]`, témoignages, genre et âge, `twinning_partner_lo`, `award_entry`. Seuls les 13 champs de §3.2 existent à la saisie. |
| **Cible, objectif, trajectoire** `[D-09]` | Interdit | Aucune colonne, aucun calcul, aucun affichage de cible, y compris pour RISE. Le 53,47 % est un **constat publié**, pas un objectif. |
| **Définitions d'indicateurs JCI** | Interdit | 462 des 465 indicateurs n'ont pas de définition : ils restent `unknown`. Ne rien compléter. |
| **Valeurs de graphiques non extraits** | Interdit | Les 9 VDX restent `null`. |
| **Arbitrage des 26 conflits** | Interdit | Ne jamais choisir une valeur. En afficher 4 ; les 22 autres restent en base, non affichés. |
| Les 465 indicateurs en base | Hors MVP | Seule une dizaine de chiffres de référence JCI est chargée (voir O-05). |
| Statut `verified`, pièces justificatives | Hors chemin critique | L'état existe dans le schéma. Aucune interface de téléversement de preuve. |
| Liste de `activity_type` ou codes détaillés de `target_group` à la saisie `[D-08]` | Hors MVP | Déduits par l'IA, jamais demandés. |
| Conversion de devises, `unit_normalization` monétaire | Hors MVP | |
| Création automatique d'un DQC en cas d'écart avec JCI (AGG-5) | Hors MVP | Le seuil n'est pas fixé : afficher les deux chiffres, sans verdict. |
| Plafond du nombre d'ODD secondaires | Hors MVP | Le contrôle est « recommandé » mais aucune valeur n'est fixée. |

---

## 8. Fichiers à réutiliser tels quels

**À brancher, pas à réécrire.** Toute divergence entre une réimplémentation et ces fichiers est un bug de la réimplémentation. Ils sont en Python : quelle que soit la stack retenue, le plus sûr est de les appeler directement (import dans un service Python, ou appel en ligne de commande depuis un autre langage).

| Fichier | Rôle | Comment l'appeler |
|---|---|---|
| `docs/technical/measurement-object.schema.json` | Contrat du MO (JSON Schema Draft-07) | Validation de **tout** MO avant insertion. Chargé par le validateur ci-dessous. |
| `docs/technical/taxonomy.config.json` | Référentiel des codes, v0.2.1 | Chargé dans `taxonomy_release` au démarrage. Toute nouvelle version = nouvelle ligne, jamais une édition en place. |
| `docs/technical/validate_measurement_objects.py` | Schéma + règles E1–E6 | CLI : `python3 validate_measurement_objects.py <fichier.json>` (code 0 = OK). Import : `Draft7Validator(schema)` puis `validate_one(validator, obj)`, qui renvoie la liste des erreurs. **À garder dans le même dossier que le schéma** (chemin relatif `HERE`). Dépendance : `jsonschema`. |
| `Tier 2/validate_provenance.py` | Règles de provenance V1–V11. Version Tier 2, qui contient la version Tier 1 et ajoute V11 | CLI : `python3 validate_provenance.py <fichier.json>` (code 1 si violation). Import : `validate(path)` sur un fichier, ou `walk(obj, "$", {"in_norm": False, "fictional": False}, errors, stats)` sur un objet. **Politique `[D-12]`** : bloquant sur V1, V2, V3, V4, V6, V9, V10 et sur V11 « OFFICIAL_JCI_FACT cannot be validated/verified ». Non bloquant (journalisé en avertissement) : V5, V11 « invalid verification_status flagged », V11 « verified without evidence_ref ». Ces trois cas sont déjà couverts par le schéma. |
| `backend/engine/aggregation_engine.py` | Clé d'équivalence, éligibilité, refus, agrégats | `equivalence_key(m)` : calcul de la clé à l'étape 3. `aggregate(measurements, group_by, total_units)` renvoie un `EngineResult` avec `.aggregates`, `.refusals` et `.excluded`. `Aggregate.to_measurement_object(id, subject, period)` : MO à stocker. `pair_compatibility(a, b)` : explication à la demande. Avant l'appel, **exclure** les MO agrégats (`parent_measurement_ids` non vide) et les chiffres de référence JCI. Ne pas modifier `DEDUP_ENABLED`. Le refus des unités `percent`/`ratio` `[D-13]` est déjà intégré au moteur (`NON_ADDITIVE_UNITS`). |

Jeux de test prêts à l'emploi : `measurement-object.examples.json` (5 valides, 6 invalides) et `backend/engine/demo_measurements.json` (11 cas du moteur).

---

## Annexe A — Points d'entrée d'API

Les chemins sont *(proposés)*. Leur comportement est spécifié par §3 à §5.

| # | Méthode et chemin | Entrée | Sortie | Rôles |
|---|---|---|---|---|
| 1 | `POST /submissions` | `{raw_text}` | `{submission_id, pipeline_status}` ; lance les étapes 2 et 3 | admin_ol |
| 2 | `GET /submissions/{id}` | — | `{pipeline_status, pipeline_error, raw_text}` | propriétaire, niveaux supérieurs |
| 3 | `POST /submissions/{id}/retry` | — | `{pipeline_status}` (relance sur le même texte) | admin_ol |
| 4 | `GET /submissions/{id}/draft` | — | Fiche préremplie : champs, valeur, **origine**, citation, `span`, confirmations C1–C4 requises, candidats en erreur | admin_ol |
| 5 | `POST /submissions/{id}/confirm` | `{corrections[], confirmations{C1..C4}, axes{A,B,pillars,C}, outcome_status, expected_outcome?, follow_up_date?}` | `{project_id, measurement_ids[]}` ou `422 {errors[]}` (sortie des validateurs) | admin_ol |
| 6 | `GET /projects/{id}` | — | Projet, 4 tables de classification, MO rattachés | selon périmètre |
| 7 | `GET /measurements/{id}` | — | MO complet, reconstitué au format du schéma, avec `derivation[]` et `relations[]` | selon périmètre |
| 8 | `POST /measurements/{id}/review` | `{action: validate \| flag \| unflag, reason}` | MO mis à jour. Refus si `OFFICIAL_JCI_FACT` (T4) ou si `dq_refs` est présent (T6) | admin_national |
| 9 | `POST /aggregations/run` | `{view, scope_organization_id, group_by, filters{reporting_year, area_of_opportunity, programme, sdg}}` | `{aggregate_run_id, aggregates[], refusals[]}` | selon vue |
| 10 | `GET /dashboards/{view}` | `scope_organization_id`, filtres | Dernière exécution : agrégats, refus, chiffres JCI de référence et conflits affichés (vue mondiale) | selon vue |
| 11 | `GET /trace/{measurement_id}` | — | Chaîne complète jusqu'à `raw_text` avec citation surlignée, et résultats de CTL-RAW et CTL-TRACE | selon périmètre |
| 12 | `POST /aggregations/check-pair` | `{measurement_id_a, measurement_id_b}` | `{compatible: bool, refusal?}` via `pair_compatibility()` | tous |
| 13 | `GET /taxonomy` | — | `taxonomy_release` active | tous |

---

## Annexe B — Vérification : les 5 MO valides tiennent-ils dans le schéma de base ?

Méthode : énumération automatique de **tous** les chemins feuilles des 5 objets `valid` de `measurement-object.examples.json` (clés `_` exclues), puis rattachement de chaque chemin à une colonne. Validateur exécuté sur le fichier : 5/5 valides, 6/6 invalides rejetés.

| Chemin(s) dans le MO | Présent dans les objets n° | Destination |
|---|---|---|
| `measurement_id`, `standard`, `metric_code`, `metric_label_source`, `layer`, `value`, `value_status`, `verification_status` | 0–4 | Colonnes homonymes de `measurement` |
| `definition.status`, `.text`, `.layer` | 0–4 (`.layer` : 1) | `definition_status`, `definition_text`, `definition_layer` |
| `iaooi_class.value`, `.layer`, `.rule_id`, `.confidence`, `.standard` | 0–4 (`.standard` : 0–2) | `iaooi_*` |
| `source_wording_class` (dont `null` explicite) | 0, 1 | `source_wording_class` |
| `taxonomy_refs.*` (dont `programme: []` et `sdgs[].goal`/`.role`) | 1 | `taxonomy_refs` (JSON, `[]` conservé) |
| `value_qualifier` | 0–2, 4 | `value_qualifier` |
| `formula`, `inputs` | 4 | `formula`, `inputs` |
| `unit.code`, `.dimension` | 0–4 | `unit_code`, `unit_dimension` |
| `subject.type`, `.id`, `.name` | 0–4 (`.name` : 0–2, 4) | `subject_*` |
| `population.internal_external`, `.count_type`, `.dedup_basis`, `.target_group` | 0–4 | `pop_*` |
| `period.type`, `.reporting_year`, `.start`, `.end` | 0–4 (`.start`/`.end` : 1, 2) | `period_*` |
| `geography.{local_organization, country_iso2, geographic_area}.{value, layer, rule_id, confidence}` | 1 | `geography` (JSON) |
| `source.origin`, `.page`, `.section`, `.quote`, `.document_id`, `.language`, `.submitted_at` | 0–4 | `source_*` |
| `derivation[].step`, `.rule_id`, `.agent`, `.confidence`, `.input_refs` | 1, 4 | Table `derivation` (`position` conserve l'ordre) |
| `confidence` | 1, 4 | `confidence` |
| `checks_passed`, `dq_refs` | 1 ; 0, 3 | JSON |
| `validated_by`, `validated_at` | 1 | Colonnes homonymes |
| `relations[].relation_type`, `.measurement_id`, `.note` | 2 | Table `measurement_relation` |
| `parent_measurement_ids` | 4 | Table `measurement_parent` |
| `aggregation.aggregable` (booléen), `.equivalence_key` (dont `null` explicite en 0), `.refusal_reason` (dont `null` en 1), `.dedup_key`, `.coverage.{contributing_units, total_units, share}` | 0–4 | `agg_*` (`coverage` en JSON) |

**Résultat** : les 5 objets sont stockables **sans perte**. Provenance (`layer`, `source_*`, `derivation`), statut de vérification et clé d'équivalence ont chacun une colonne dédiée. Conditions pour que la restitution soit exacte (test AC-15) :

1. `agg_aggregable` est en `TEXT` et se resérialise en booléen JSON.
2. Il faut distinguer « clé absente » (`NULL`) de « valeur `null` explicite » pour `equivalence_key`, `refusal_reason` et `source_wording_class` : une colonne sentinelle, ou le stockage du sous-objet `aggregation` en JSON en plus des colonnes indexées.
3. `[]` et `NULL` restent distincts.

**Réserve d'intégrité** : l'objet 4 (`MO-AGG-CI-TRAINED-2025`) cite `MO-TC7-TRAINED` et `MO-TC9-TRAINED`, qui **n'existent pas** dans le fichier. C'est pour cette raison que `measurement_parent` n'a pas de FK bloquante. CTL-TRACE marquera cet agrégat « chaîne incomplète », ce qui est le comportement voulu.

---

## Annexe C — Points ouverts et arbitrages

Arbitrés par le Product Owner le 2026-09-18 au soir. Les décisions sont consignées dans `mvp-scope.md` §1 et les fichiers concernés ont été mis à jour.

| ID | Point | Décision | Fichiers modifiés |
|---|---|---|---|
| O-01 | D-09 non numérotée | **Résolu** : D-09 ajoutée au tableau des décisions | `mvp-scope.md` |
| O-02 | Nombre de confirmations | **D-16** : 4 bloquantes (C1–C4). Axes A/B validés par la confirmation de la fiche | `mvp-scope.md` |
| O-03 | Conflit entre les deux validateurs | **D-12** : le validateur du MO fait foi ; politique de `validate_provenance` en §8 | `mvp-scope.md` (aucun validateur modifié) |
| O-04 | Codes d'input absents | **D-10** : `input_type` = `VOLUNTEERS`, `VOLUNTEER_HOURS`. Pas de `BENEFICIARIES` générique | `taxonomy.config.json` → v0.2.1 |
| O-05 | Chiffres JCI de référence (AGG-5) | **Ouvert** : liste à fournir par le PO. Non bloquant pour le backend | — |
| O-06 | `period.type` dans la clé | **D-11** : `reporting_year` pour toute mesure de projet, dates conservées | `measurement-object.examples.json` (MO-TC1-TRAINED, MO-TC1-REACH), `measurement-object.md` (amendement) |
| O-07 | Sens de `aggregable` | **D-14** : éligibilité individuelle ; refus de paire dans `refusal` | `measurement-object.examples.json` (MO-TC1-REACH), `demo_measurements.json` (MO-CI-BOUAKE-REACH), `measurement-object.md` |
| O-08 | Somme de pourcentages | **D-13** : refusée par le moteur | `aggregation_engine.py` (`NON_ADDITIVE_UNITS`) |
| O-09 | `demo_measurements.json` sans clés | **Pas d'action** : la clé est calculée par le système (AC-20) | — |
| O-10 | Couche de `country_iso2` | **D-15** : `LOCAL_REPORTED_FACT` quand le pays vient du compte OL | `measurement-object.md` (amendement) |
| O-11 | Titre « 12 champs » | **Résolu** : « 13 champs » | `mvp-scope.md` |

Vérification après modifications : `validate_measurement_objects.py` → 5/5 valides et 6/6 invalides rejetés. Le moteur démo produit les mêmes 4 agrégats et 3 refus qu'avant. Un pourcentage est refusé avec « unité non additive ». Le couple MO-TC1-TRAINED / MO-TC1-REACH est refusé en `SEMANTIC_NON_EQUIVALENCE`.
