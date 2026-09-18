# NEXUS — Data Model (v0.1, DRAFT → proposé ACCEPTED)

**Statut** : PROPOSED_STANDARD, soumis à DECISION NEXUS. Ne pas considérer comme LOCKED tant que l'équipe n'a pas explicitement confirmé (voir « Décision requise » en fin de document).

**Sources** : Tier 1 (`JCI_Tier1_Reverse_Engineering_V2.md` — §P modèle de provenance, §C taxonomie, §D schéma JSON, §Q registre de conflits, §V registre visuel) + Tier 2 (`JCI_Tier2_Indicators_Collection_Lineage.md` — §F inventaire 465 indicateurs, §M modèle d'entités/ERD, §G modèle de collecte locale, §H qualité & lignage). Les deux jeux ont été croisés : aucune contradiction détectée entre Tier 1 et Tier 2 ; Tier 2 étend le vocabulaire de couche de Tier 1 (`verification_status`) sans le modifier (règle P10 respectée : la validation ne change jamais la couche).

**Ce document ne réécrit pas Tier 1/Tier 2** : il consolide ce qui doit devenir le schéma produit. Pour le détail (citations, pages, cas de test), se référer aux fichiers sources.

---

## 0. Rappel du principe de provenance (règle du moteur)

Toute donnée porte deux informations indépendantes, jamais fusionnées :

| Axe | Champ | Valeurs |
|---|---|---|
| **D'où ça vient** (`layer`) | couche | `OFFICIAL_JCI_FACT` · `LOCAL_REPORTED_FACT` · `SEMANTIC_INTERPRETATION` · `PROPOSED_STANDARD` |
| **Que sait-on du chiffre** (`value_status`) | statut de valeur | `extracted` · `calculated` · `estimated` · `unknown` (→ `null`, jamais 0) · `visual_data_not_extracted` (→ `null`) · `conflicting` |

Règle P0 : *No unsupported inference becomes an official JCI fact.* Une classification, un code de taxonomie ou un calcul n'est **jamais** `OFFICIAL_JCI_FACT`, même appliqué à une donnée JCI officielle (P5/P6, contrôle V6 du validateur). Combinaisons couche × statut interdites : voir Tier 1 §P.3 (ex. `OFFICIAL_JCI_FACT` + `calculated` est refusé — un calcul est toujours `SEMANTIC_INTERPRETATION`).

`validate_provenance.py` (Tier 1 + Tier 2) applique ces règles automatiquement. **Toute donnée qui entre dans la base doit passer ce validateur avant stockage** — c'est la version exécutable de ce chapitre.

---

## 1. Pipeline de transformation (niveaux jamais fusionnés)

```
RAW  →  STRUCTURED  →  STANDARDIZED  →  VALIDATED  →  AGGREGATED
```

| Niveau | Contenu | Couche typique |
|---|---|---|
| RAW | Texte libre exactement tel que saisi par l'organisation locale | `LOCAL_REPORTED_FACT`, `value_status=extracted` |
| STRUCTURED | Champs extraits du texte (LLM), non encore classés | `SEMANTIC_INTERPRETATION` (extraction) |
| STANDARDIZED | Champs mappés vers le vocabulaire/taxonomie NEXUS (`taxonomy.config.json`) | `SEMANTIC_INTERPRETATION` appliquant un `PROPOSED_STANDARD` |
| VALIDATED | Contrôles passés : cohérence, plausibilité, absence de conflit ouvert, éventuelle validation humaine | statut ajouté : `verification_status` (voir §4) |
| AGGREGATED | Autorisée à entrer dans une statistique globale, seulement si équivalence sémantique démontrée (§5) | `SEMANTIC_INTERPRETATION · calculated` |

Une donnée ne saute **jamais** directement RAW → AGGREGATED.

---

## 2. Entités (Tier 2 §M, cf. ERD complet dans le fichier source)

Entités attestées par le rapport JCI (existence = `OFFICIAL_JCI_FACT`) : `GlobalOrganization`, `GeographicArea` (4), `RegionalOffice` (4), `NationalOrganization` (114), `LocalOrganization` (4 641), `AlumniClub` (366) / `JuniorClub` (89), `Member` (147 670), `Senator` (84 375), `Program`, `Project`, `Event`, `EventSession`, `CompetitionParticipation`, `AwardEntry` / `AwardCategory`, `Recognition`, `TwinningAgreement` (113), `DevelopmentGrant`, `Donation` / `Donor`, `Partner` / `PartnerContribution`, `PetitionSignature` (67 101), `IHDActivity` (42), `CommunicationChannelMetric`, `SurveyResponse` (3 767).

Relations clés (ERD complet en Mermaid dans `JCI_Tier2_Indicators_Collection_Lineage.md` §M.2) :

```
GlobalOrganization ──< GeographicArea (4, OFFICIAL p.9)
GeographicArea ──< NationalOrganization (114, OFFICIAL p.10)
NationalOrganization ──< LocalOrganization (4641)
LocalOrganization ──< Member
LocalOrganization ──< Project

        ┌─ AreaOfOpportunity  (1..n)  ─┐   axe A
Project ┼─ Programme          (0..n)  ─┤   axe B   ← TROIS AXES INDÉPENDANTS
        └─ SDG                (1..n)  ─┘   axe C

Project >──o< RisePillar (uniquement si Programme = RISE)
Event ──< EventSession / AwardEntry / TwinningAgreement
TwinningAgreement >──< NationalOrganization (parties)
Member ──o Senator
```

**Les trois axes de classification sont indépendants** (DECISION NEXUS 2026-09-18). Un projet se classe séparément sur chacun : il peut relever du domaine Individual Development, appartenir au programme JCI RISE, et viser l'ODD 8 — les trois simultanément. Le programme **ne détermine pas** le domaine d'intervention, et réciproquement.

Preuve chiffrée : 53,47 % des projets déclarés 2025 sont RISE [p.85], alors que 44,64 % relèvent de Community Impact [p.86], sur la même base de 1 000+ projets. Si RISE était contenu dans Community Impact, sa part ne pourrait pas excéder 44,64 %. La version 0.1.0 du modèle, qui emboîtait le programme dans le domaine, était donc fausse — erreur de modélisation NEXUS, pas incohérence du rapport JCI. Aucun objet de conflit n'a été ouvert à ce titre.

Cardinalités marquées « OFFICIAL » dans la source : la relation elle-même est écrite dans le rapport. La cardinalité exacte reste une interprétation (`SEMANTIC_INTERPRETATION`).

**Point de vigilance produit** : la table `NationalOrganization/Country → GeographicArea` n'est **pas publiée** (VDX-01, graphique illisible). C'est un champ `SYSTEM-DERIVED` du modèle de collecte (§3, champ #4) qui n'a aujourd'hui **aucune source fiable** — à obtenir de JCI ou à construire manuellement comme référentiel externe versionné.

---

## 3. Enregistrement canonique `Project` — champs à collecter

Dérivé de Tier 2 §G (45 champs, chacun justifié par une preuve dans le rapport ou par la Road Map 2026, jamais par présomption). Chaque champ porte : une **exigence** (REQUIRED / RECOMMENDED / OPTIONAL), un **mode de production** (`LOCAL_INPUT` déclaré par l'OL · `AI-DERIVED` extrait/classé par le LLM · `SYSTEM-DERIVED` calcul déterministe/lookup), et une **exigence de validation** (`HUMAN-VALIDATED` obligatoire avant agrégation · `AUTO-CHECKED` par règle · `NONE`).

### 3.1 Identification (REQUIRED sauf mention)
`project.name` · `organization.local_organization` · `organization.national_organization` (SYSTEM-DERIVED) · `organization.geographic_area` (SYSTEM-DERIVED, ⚠ table manquante) · `project.reporting_year` · `project.period.start/end` (RECOMMENDED) · `organization.lead_contact` (RECOMMENDED, donnée personnelle, NONE)

### 3.2 Classification — les trois axes JCI, déclarés séparément

| Axe | Champ | Exigence | Production | Confirmation |
|---|---|---|---|---|
| **A — Domaine** | `project.area_of_opportunity[]` | REQUIRED ≥1 | IA propose | **HUMAN-VALIDATED** |
| **B — Programme** | `project.programme[]` (0..n ; « aucun » est une valeur légitime) | REQUIRED, vide autorisé | IA propose | **HUMAN-VALIDATED** |
| | `project.rise_pillars[]` | REQUIRED si programme = RISE | IA propose | **HUMAN-VALIDATED** |
| **C — ODD** | `sdgs[]` + `sdgs[].role` (1 principal) | REQUIRED ≥1 | IA propose | **HUMAN-VALIDATED** |

Aucun de ces trois axes ne se déduit d'un autre (règle R3).

Couche de mesure NEXUS, appliquée aux chiffres et non au projet : `activity.activity_types[]` (AI-DERIVED, aucun équivalent JCI) · `beneficiaries[].target_group` (RECOMMENDED, AI-DERIVED) · `beneficiaries[].internal_external` (REQUIRED, AI-DERIVED, **HUMAN-VALIDATED** — règle R7).

### 3.3 Description
`project.need_statement` (REQUIRED) · `project.objective` (RECOMMENDED) · `activity.description` (REQUIRED — source de l'extraction IA) · `submission.language` (SYSTEM/AI-DERIVED)

### 3.4 Inputs
`resources.volunteers` (REQUIRED) · `resources.volunteers.member_split` (RECOMMENDED) · `resources.volunteer_hours` total (REQUIRED) · `resources.cash` / `in_kind` + devise (RECOMMENDED, conversion SYSTEM-DERIVED) · `organization.partner_organizations[]` (RECOMMENDED)

### 3.5 Outputs
`beneficiaries[].count` (REQUIRED, **HUMAN-VALIDATED**) · `beneficiaries[].count_type` direct/indirect/audience (REQUIRED — sinon l'agrégat n'a pas de sens, **HUMAN-VALIDATED**) · `outputs.participants_unique` (RECOMMENDED) · `outputs.registrations` / `attendees` (OPTIONAL) · `outputs.people_trained` / `completions` (RECOMMENDED) · `outputs.physical_output` (OPTIONAL)

### 3.6 Outcomes
`outcome_status` (D-20 : `measured` → `outcomes[]` REQUIRED ≥1 ; `pending_follow_up` → effet attendu + date de suivi ; `none` — exigence Road Map 2026, **HUMAN-VALIDATED**) · `outcomes[].base_population` (REQUIRED si ratio) · `outcomes[].measurement.method` + `horizon` (RECOMMENDED, **HUMAN-VALIDATED**) · `outcomes.new_members` (OPTIONAL)

### 3.7 Impact
`impact[].claim_raw` (OPTIONAL) · `impact[].attribution_level` (REQUIRED si claim, **HUMAN-VALIDATED**)

### 3.8 Évidence / démographie / liens
`evidence[]` (RECOMMENDED, **HUMAN-VALIDATED** pour passer `verified`) · `evidence[].testimonial` (OPTIONAL) · `beneficiaries[].attributes.gender_share` (RECOMMENDED) · `beneficiaries[].attributes.age_band` (OPTIONAL) · `project.twinning_partner_lo` (REQUIRED si Twinning, **HUMAN-VALIDATED** — dédoublonnage) · `project.award_entry` (OPTIONAL)

### 3.9 Système (SYSTEM-DERIVED, non saisis)
`project_id`, `submission_id`, `submitted_at`, `source_document`, `provenance.*` (couche/statut/règle/citation), `data_quality.conflict_refs`, `data_quality.unknowns`

**Ce que le rapport ne permet pas de dériver** (à ne jamais présumer) : définition JCI d'un « beneficiary » (direct/indirect, dédoublonnage), définition d'un « volunteer » (membre ou non), seuils de plausibilité (heures/bénévole), format actuel exact du formulaire JCI, grille de notation des prix. Ces éléments restent `unknown` et doivent être conçus par NEXUS ou demandés à JCI, jamais inventés.

### 3.10 Minimum viable MVP (sous-ensemble REQUIRED en LOCAL_INPUT)

Pour la démo hackathon, **ne pas** brancher les 45 champs. Le sous-ensemble minimal, déjà justifié par un agrégat publié ou par la Road Map 2026 :

nom du projet, LO, année, area_of_opportunity, programme/RISE (+ pilier si RISE), SDG(s) + principal, besoin/contexte, description, bénévoles, heures totales, bénéficiaires + type de comptage, ≥1 résultat mesurable (ou « aucun mesuré »).

C'est ce sous-ensemble qui doit être branché en premier dans le pipeline d'extraction et le formulaire de saisie.

---

## 4. Statut de vérification (`verification_status`) — Tier 2 §H.2

Distinct de `layer` (d'où ça vient) et de `value_status` (comment le chiffre a été produit). Répond à « a-t-on contrôlé ce chiffre ? » :

`reported` (déclaré, non contrôlé) → `validated` (contrôles de cohérence passés : unités, arithmétique, plausibilité, absence de conflit ouvert) → `verified` (confronté à une pièce justificative, `evidence_ref` obligatoire).

Règles de transition (PROPOSED_STANDARD, ne changent jamais la couche — P10) :

- **T1** `reported → validated` : toutes les règles AUTO-CHECKED du champ passées + aucun DQC ouvert
- **T2** `validated → verified` : `evidence_ref` obligatoire vers une pièce stockée
- **T3** Tout changement de valeur repasse à `reported` et versionne (ancienne valeur conservée)
- **T4** Un `OFFICIAL_JCI_FACT` reste `reported` pour toujours — le moteur ne peut ni valider ni vérifier un chiffre JCI (le rapport ne décrit aucune méthode de vérification)
- **T5** `calculated` hérite du plus faible `verification_status` de ses entrées ; `estimated` ne dépasse jamais `validated`
- **T6** Un conflit DQC ouvert bloque le passage à `validated` des valeurs concernées
- **T7** Validation humaine (`validated_by`, `validated_at`) posée sur l'étape d'interprétation, jamais sur la valeur source brute

---

## 5. Règles d'agrégation (Tier 2 §H.4 AGG-1..5 + taxonomie R7/R8)

Une agrégation n'est autorisée que si définition, unité, population, période, scope et contexte sont compatibles entre les entrées. Sinon :

```
aggregation_status = REFUSED
reason = SEMANTIC_NON_EQUIVALENCE
```

- **AGG-1** On ne somme que des valeurs de même définition et même période
- **AGG-2** `verification_status` de l'agrégat = le plus faible des entrées
- **AGG-3** Si une entrée est `approx`, l'agrégat est `approx`
- **AGG-4** L'agrégat stocke sa couverture (part des projets contributeurs à ce total)
- **AGG-5** Un agrégat moteur n'est jamais substitué à un total JCI publié ; toute comparaison cite les deux et ouvre un DQC si l'écart dépasse un seuil (seuil = décision d'équipe, non fixé)
- **R7** Membres JCI (internes, ID) et bénéficiaires externes (CI) ne s'additionnent jamais
- **R8** Métriques CONTEXT et événements externes (GITEX, WCC…) ne sont jamais agrégés comme outputs NEXUS

Interdits classiques déjà identifiés dans le rapport source : `trained ≠ reached`, `registered ≠ unique participants`, `communication reach ≠ beneficiaries`, `impressions ≠ reach`.

---

## 6. Déduplication

Cas identifié dans le rapport : un Twinning (`TwinningAgreement`) peut être déclaré séparément par chaque LO/NO partenaire (règle R6, illustré par le cas de test TC5 Bénin–Canada). Règle produit : reconnaître `multiple_sources → one canonical project` avant tout comptage agrégé ; ne jamais compter un même projet deux fois au seul motif qu'il apparaît dans deux rapports locaux. Le champ `project.twinning_partner_lo` (§3.8) est **HUMAN-VALIDATED** précisément pour ce contrôle.

---

## 7. Lignage / traçabilité (Tier 2 §H.3/H.4)

Objectif produit : `Global metric → geographic_area → country → Local Organization → Project → source`. Le rapport JCI 2025 lui-même **ne permet pas** cette chaîne descendante (le meilleur cas, les bénévoles, est cassé à 3 niveaux sur 9 ; le pire cas, les 21 148 414 bénéficiaires, n'a aucune décomposition). C'est précisément l'écart que NEXUS doit combler pour les données **futures** collectées par le système — pas pour reconstruire rétroactivement les chiffres 2025. Le lignage `PROPOSED` complet (`LINEAGE-v0`, exemple TC1) est validé (0 violation) dans `jci_lineage_examples_v2.json`.

---

## 8. Ce qui reste explicitement `UNKNOWN` (registre, non bloquant pour construire)

| ID | Question | Impact | Bloquant ? |
|---|---|---|---|
| UNK-DM-01 | Table NationalOrganization/Country → GeographicArea | Empêche le calcul fiable de `organization.geographic_area` pour des pays hors des 5 cas de test | Non — utiliser un référentiel manuel provisoire, versionné, à corriger dès que la source existe |
| UNK-DM-02 | Définition JCI de « beneficiary » (direct/indirect, dédoublonnage) | Les totaux « bénéficiaires » restent non comparables entre eux | Non — NEXUS impose son propre `count_type` explicite en attendant |
| UNK-DM-03 | Définition JCI de « volunteer » (membre ou non) | Champ `member_split` restera à confiance modérée | Non |
| UNK-DM-04 | Format réel du formulaire de soumission JCI actuel | M.3 est une reconstruction (confiance H/M), pas une copie | Non — n'affecte pas le MVP, qui définit son propre formulaire |

---

## 9. Décision requise

Ce document consolide Tier 1 + Tier 2, déjà validés automatiquement (0 violation sur les livrables réels, pièges détectés correctement sur les tests négatifs) et mutuellement cohérents. Aucune preuve nouvelle ne vient les contredire.

**Proposition** : faire passer le statut du Measurement Object de `DRAFT` à `ACCEPTED` (pas encore `LOCKED` — reste `PROPOSED_STANDARD`, révisable si de vraies données de soumission JCI apparaissent), et lancer immédiatement la Phase 1 (backend) sur la base du sous-ensemble MVP (§3.10), pas des 45 champs complets.

**Ce qui n'est PAS proposé** : lancer un « Tier 3 » d'analyse supplémentaire. Le compte à rebours du hackathon (voir échange produit du 2026-09-18) rend cet investissement contre-productif — la matière est suffisante pour construire.
