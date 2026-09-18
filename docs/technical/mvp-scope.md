# NEXUS — Périmètre MVP : les 13 champs canoniques et le flux de saisie

**Statut** : DÉCISION NEXUS du 2026-09-18, prise par le Product Owner.
**Remplace** : la liste des 45 champs de Tier 2 §G.2 pour tout ce qui concerne le MVP hackathon. Les 45 champs restent la cible produit à terme, documentée, non implémentée.

---

## 1. Décisions actées ce jour

| # | Décision | Statut |
|---|---|---|
| D-01 | Le Measurement Object v1 est la forme canonique de toute donnée chiffrée du système | **ACCEPTED** |
| D-02 | Quatre états de vérification : `reported` → `validated` → `verified`, plus `flagged` (bloquant) | **ACCEPTED** |
| D-03 | **La déduplication sort du périmètre MVP.** Un projet déclaré deux fois est compté deux fois. Aucun refus, aucun signalement | **ACCEPTED** |
| D-04 | La saisie se fait en **texte libre**, jamais par formulaire vide. Le système extrait, puis fait confirmer | **ACCEPTED** |
| D-05 | 13 champs canoniques (§3), pas 45 | **ACCEPTED** |
| D-06 | Aucune nouvelle vague d'analyse (pas de « Tier 3 ») | **ACCEPTED** |
| D-07 | **Les trois axes de classification JCI sont indépendants** : domaine d'intervention, programme, ODD. Aucun n'est emboîté dans un autre. Remplace la structure hiérarchique de `taxonomy.config.json` v0.1.0 | **ACCEPTED** |
| D-08 | La couche de mesure NEXUS est allégée pour le MVP : type de production et type de résultat actifs en entier ; groupe cible réduit à l'axe interne/externe ; type d'activité déduit sans liste imposée ; type d'impact désactivé | **ACCEPTED** |
| D-09 | **Aucune cible, aucun objectif, aucune trajectoire** n'est fixé, proposé ou affiché par NEXUS, y compris pour RISE (le 53,47 % est un constat). Voir §3 « Limite explicite » | **ACCEPTED** |
| D-10 | Deux codes de ressources ajoutés à la couche de mesure (`input_type`) : `VOLUNTEERS` (person) et `VOLUNTEER_HOURS` (hour). Codes PROPOSED_STANDARD, pas JCI. Pas de code générique `BENEFICIARIES` | **ACCEPTED** |
| D-11 | Toute mesure de projet produite par le pipeline porte `period.type = reporting_year` ; les dates exactes restent dans `period.start` / `period.end`. Les chiffres de deux OL se comparent donc sur l'année de reporting | **ACCEPTED** |
| D-12 | Le validateur du Measurement Object (schéma + E1–E6) fait foi et bloque. `validate_provenance.py` bloque sur V1–V4, V6, V9, V10 et V11 (chiffre JCI validé/vérifié) ; ses avertissements V5, V11 « flagged » et V11 « evidence_ref » sont non bloquants | **ACCEPTED** |
| D-13 | Les unités `percent` et `ratio` n'entrent jamais dans un total : le moteur les refuse (`SEMANTIC_NON_EQUIVALENCE`, motif « unité non additive ») ; elles restent affichées par projet | **ACCEPTED** |
| D-14 | `aggregation.aggregable` d'une mesure = son éligibilité individuelle (valeur connue, pas de conflit ouvert, pas signalée, type de comptage connu). Les refus entre deux mesures (ex. vues + personnes formées) sont produits par le moteur et stockés dans la table des refus | **ACCEPTED** |
| D-15 | `geography.country_iso2` issu du compte de l'OL est une donnée système : couche `LOCAL_REPORTED_FACT`, comme `local_organization`. `geographic_area` qui en découle reste `SEMANTIC_INTERPRETATION` (VDX-01) | **ACCEPTED** |
| D-16 | Quatre confirmations humaines bloquantes sur la fiche : type de comptage, interne/externe, ODD (1 principal), résultat mesurable ou « aucun ». Domaine et programme (+ piliers RISE) sont préremplis et validés par la confirmation de la fiche | **ACCEPTED** |
| D-17 | **Complétion guidée obligatoire.** Pour une saisie OL, aucun champ requis ne peut rester `unknown` à la soumission : après son texte libre, le SG répond aux questions de complétion (§2bis) sur ce qui manque. Une réponse peut être approximative (« environ ») mais jamais vide. Filet de sécurité moteur : une mesure sans période est refusée (`MISSING_PERIOD`). `unknown` reste légitime uniquement pour les sources qu'on ne peut pas interroger (rapport JCI, imports) | **ACCEPTED** (PO, 2026-09-18) |
| D-18 | **Profil OL à la création du compte** : nom de l'OL, organisation nationale, pays, zone JCI (AFME / AMERICA / ASPAC / EUROPE). Ces valeurs sont `LOCAL_REPORTED_FACT` et ne sont jamais extraites du texte ni questionnées à la saisie. Remplace, pour `geographic_area`, la déduction de D-15 (qui restait SEMANTIC_INTERPRETATION faute de table JCI, VDX-01) | **ACCEPTED** (PO, 2026-09-18) — supersède D-15 sur `geographic_area` |
| D-19 | `target_group` simplifié : interne / externe / mixte **obligatoire** ; famille de public **facultative** proposée par l'IA (6 familles + `OTHER` avec libellé libre du SG), jamais bloquante, jamais dans la clé d'équivalence ; libellé source toujours conservé. Taxonomie v0.2.2 | **ACCEPTED** (PO, 2026-09-18) |
| D-20 | Champ #12 à trois états (`outcome_status`) : `measured` (résultat concret chiffré déclaré) / `pending_follow_up` (effet attendu + date de suivi ; la réponse crée une nouvelle mesure) / `none` (activité réelle sans effet mesurable visé). Aucun des deux derniers ne crée de valeur 0. Relance automatique post-MVP | **ACCEPTED** (PO, 2026-09-18) |
| D-21 | Niveau de preuve obligatoire sur chaque résultat (« comment le sais-tu ? ») | **REJECTED** (PO, 2026-09-18) — la validation par l'organisation nationale suffit pour le MVP. Réouvrable après le hackathon |
| D-22 | **Vocabulaire de présentation** : dans les dashboards et le pitch, les résultats sont présentés sous le libellé « Impact », comme le fait JCI. Le modèle de données conserve inchangée la distinction INPUT / OUTPUT / OUTCOME. Garde-fou : les ressources (bénévoles, heures) et la portée de communication (vues, followers) ne sont **jamais** affichées sous « Impact » | **ACCEPTED** (PO, 2026-09-18) — garde-fou proposé par le Product Architect, à confirmer |

D-09 : numérotation d'une décision déjà actée en §3, sans changement de fond. D-10 à D-16 : arbitrages du Product Owner du 2026-09-18 (soir) sur les points ouverts de `dev-brief.md` (O-02, O-03, O-04, O-06, O-07, O-08, O-10).

### Note sur D-07 (les trois axes)

Origine : connaissance métier du Product Owner, membre JCI — « JCI fait l'étude des projets souvent sur 3 angles : Programme, ODD et les 4 domaines d'intervention. Chacun des projets peut être rangé forcément quelque part dans tout ça. Pas seulement l'un. »

Cette information corrige une **erreur de modélisation NEXUS**, pas une incohérence de JCI. La version précédente rattachait chaque programme à un domaine et faisait hériter le projet du domaine de son programme. Les chiffres publiés démentaient cette structure : 53,47 % de projets RISE [p.85] contre 44,64 % de projets en Community Impact [p.86], sur la même base — un sous-ensemble ne peut excéder son ensemble.

Ce constat avait été identifié comme un possible 27ᵉ conflit documentaire JCI. **Il ne l'est pas, et n'a pas été enregistré comme tel.** Le registre reste à 26 conflits.

### Note sur D-03 (déduplication retirée)

Motif du Product Owner : l'effort d'explicitation est disproportionné par rapport au volume concerné.

Conséquences assumées, pour mémoire :
- Le cas de test **TC5** (jumelage Bénin–Canada) produira désormais un double comptage. C'est le comportement attendu, plus un échec.
- Le champ `aggregation.dedup_key` **reste dans le schéma** : il ne coûte rien, ne s'affiche pas, et n'est simplement pas lu par le moteur. Cela évite une migration si la règle revient après le hackathon.
- Le code de déduplication reste dans `aggregation_engine.py` mais est désactivé par un drapeau, pas supprimé.
- Réponse préparée si un juré pose la question : *« la détection de double déclaration est modélisée et le champ existe ; sa résolution est hors périmètre 48h, parce qu'elle exige un arbitrage humain que nous ne voulions pas simuler. »*

---

## 2. Le flux de saisie (D-04)

> **Principe : le Secrétaire Général ne remplit jamais un formulaire vide. Il corrige une fiche déjà remplie.**

### Étape 1 — Il écrit

Un seul champ de texte. Pas de cases, pas de menus déroulants. Il raconte son activité comme il la raconterait à un collègue, dans sa langue.

```
Du 3 au 5 septembre, on a organisé un bootcamp entrepreneuriat à Bouaké.
45 jeunes ont suivi les trois jours complets, surtout des femmes.
12 membres de l'OL se sont mobilisés, environ 150 heures au total.
Le post Facebook a touché à peu près 12 000 personnes.
```

Ce texte est conservé intact, pour toujours. C'est la pièce source à laquelle tout chiffre pourra être relié.

### Étape 2 — Le système lui montre ce qu'il a compris

Une fiche **pré-remplie**, où chaque case indique son origine :

| Champ | Valeur proposée | Origine affichée |
|---|---|---|
| Nom du projet | Bootcamp entrepreneuriat Bouaké | *déduit du texte* |
| Organisation locale | JCI Bouaké Lumière | *ton compte* |
| Période | 3 → 5 septembre 2025 | *tu l'as écrit* |
| Domaine d'impact | Business & Entrepreneurship | *déduit — à confirmer* |
| ODD | 8 (principal), 5 (secondaire) | *déduit — à confirmer* |
| Bénévoles | 12 | *tu l'as écrit* |
| Heures | ≈ 150 | *tu l'as écrit — valeur approximative* |
| Bénéficiaires | 45 | *tu l'as écrit* |
| Type de comptage | direct | *déduit — à confirmer* |
| Public | externe (non-membres) | *déduit — à confirmer* |
| Résultat mesurable | — | **manquant** |
| 12 000 vues Facebook | audience de communication | *classé à part — non compté comme bénéficiaires* |

### Étape 3 — Il corrige et complète

Le système ne pose des questions **que sur ce qui manque et qui est obligatoire**. Ici, une seule :

> *« Un résultat mesurable a-t-il été observé ? (emplois créés, entreprises lancées, personnes certifiées…) — ou coche "aucun résultat mesuré à ce stade". »*

Trois champs sont **toujours** soumis à confirmation humaine, parce qu'une erreur y fabrique une fausse statistique :

1. **Le type de comptage des bénéficiaires** (direct / indirect / audience) — sans lui, aucun total n'a de sens
2. **Public interne (membres JCI) ou externe** — les deux populations ne s'additionnent jamais
3. **Les ODD** — parce que le sur-étiquetage est le défaut documenté du rapport JCI (17 ODD déclarés pour 4 heures de bénévolat, p. 89)

Le reste, l'IA le décide et le SG peut le corriger d'un clic.

### §2bis — Questions de complétion (D-17)

Le SG raconte d'abord librement. Ensuite, le système pose **uniquement** les questions dont la réponse n'est pas déjà dans son texte. Il ne peut pas soumettre tant qu'une question bloquante est sans réponse.

| # | Question posée au SG | Alimente | Bloquante |
|---|---|---|---|
| C1 | Quand l'activité a-t-elle eu lieu ? (date ou période) | `period` | oui |
| C2 | Combien de personnes y ont participé ? Toutes ont-elles suivi l'activité jusqu'au bout ? Sinon, combien ? | `PEOPLE_TRAINED` / `PARTICIPANTS` + relation d'entonnoir | oui |
| C3 | Ces personnes sont-elles des membres JCI, un public externe, ou les deux ? | `internal_external` | oui |
| C4 | Combien de membres JCI ont été mobilisés ? Combien d'intervenants ou de volontaires externes ? | `VOLUNTEERS` (interne / externe) | oui |
| C5 | Combien d'heures ont-ils donné ? (total, ou moyenne par personne) | `VOLUNTEER_HOURS` | oui |
| C6 | Combien de temps l'activité a-t-elle duré pour les participants, hors pauses ? | durée (contexte, non agrégée) | non |
| C7 | À la fin, qu'est-ce que les participants ont **concrètement** en main qu'ils n'avaient pas avant ? Combien ? — sinon : « pas encore mesurable » (quel effet attendu, et quand vérifier ?) ou « aucun effet mesurable visé » | `outcome_status` + `outcomes[]` (champ 12, D-20) | oui |
| C8 | Confirme les ODD proposés (1 principal) | `sdgs[]` | oui |

Principe : le SG connaît ces informations, mais il ne sait pas qu'elles comptent. La question lui apprend ce qui fait la mesure.

### Ce que le SG ne saisit jamais

L'organisation nationale, la zone géographique, l'identifiant du projet, la date de soumission, la langue, et toute la provenance : le système les déduit ou les connaît déjà.

---

## 3. Les 13 champs canoniques

| # | Champ | Origine | Confirmation humaine |
|---|---|---|---|
| 1 | `project.name` — nom du projet | déduit du texte, corrigeable | non |
| 2 | `organization.local_organization` — l'OL | compte connecté | non |
| 3 | `project.reporting_year` — année de reporting | système + texte | non |
| 4 | `activity.description` — **le texte brut saisi** | saisie libre | — |
| 5 | `project.area_of_opportunity[]` — domaine(s) d'intervention · **axe A** | IA propose | **oui** |
| 6 | `sdgs[]` + rôle principal/secondaire · **axe C** | IA propose | **oui** |
| 7 | `resources.volunteers` — nombre de bénévoles | extrait du texte | non |
| 8 | `resources.volunteer_hours` — heures totales | extrait du texte | non |
| 9 | `beneficiaries.count` — nombre de bénéficiaires | extrait du texte | non |
| 10 | `beneficiaries.count_type` — direct / indirect / audience | IA propose | **oui** |
| 11 | `beneficiaries.internal_external` — membres JCI ou public externe | IA propose | **oui** |
| 12 | `outcome_status` (D-20) : `measured` + `outcomes[]` ≥1, **ou** `pending_follow_up` + effet attendu + date de suivi, **ou** `none` | saisie, sollicitée via C7 | **oui** |
| 13 | `project.programme[]` · **axe B** — dont JCI RISE. « Aucun programme » est une valeur légitime, pas un vide | IA propose | **oui** |
| 13b | `project.rise_pillars[]` — conditionnel, n'apparaît que si le projet est RISE | IA propose | **oui** |

### Pourquoi le champ 13 n'est pas une option

Décidé le 2026-09-18 : JCI classe ses projets sur **trois axes indépendants** — domaine d'intervention, programme, ODD. Un projet peut relever d'Individual Development, appartenir à RISE, et viser l'ODD 8, les trois à la fois.

Les axes A et C figurant déjà dans les champs canoniques, omettre l'axe B laisserait le modèle bancal : le système saurait dire de quel domaine et de quel ODD relève un projet, mais pas de quel programme — alors que le programme est l'axe porteur de la stratégie long terme de JCI (RISE, lancé en 2020, couvre 53,47 % des projets déclarés en 2025).

Coût réel : une case pré-cochée par l'IA, plus un sélecteur de pilier qui n'apparaît que si le projet est RISE. Le SG ne fait rien tant que la proposition est juste.

Ce que ça débloque, et que le rapport JCI 2025 ne permet pas : comparer ce que produisent les projets RISE et les projets non-RISE, à domaine égal. JCI publie aujourd'hui le pourcentage de projets RISE, mais **aucune donnée sur ce que RISE produit de différent**.

**Limite explicite (DECISION NEXUS)** : le 53,47 % est un **constat**, et il le reste. NEXUS ne fixe aucune cible RISE, n'en propose aucune, et n'affiche aucune progression vers un objectif. Définir une cible relève de la stratégie de JCI, pas de son outil de mesure. Le système rend la comparaison *possible* ; c'est à JCI seule de décider si elle veut en faire un indicateur de pilotage et à quel niveau le placer. Un tableau de bord qui afficherait une cible que JCI n'a jamais déclarée fabriquerait un fait institutionnel — précisément ce que la règle P0 interdit.

Chaque champ retenu est justifié par un agrégat effectivement publié par JCI ou par l'engagement de la Road Map 2026 (« Every local project will align with one or more SDGs and report measurable results », p. 132). Aucun champ n'est présent par confort de modélisation.

---

## 4. Ce qui est écarté du MVP, et pourquoi ce n'est pas une perte

Trois ensembles sont souvent confondus. Ils n'ont ni la même nature, ni le même coût.

### Les 465 indicateurs — **dossier de preuves, pas base de données**

Ce sont les 465 chiffres que JCI a publiés dans son rapport 2025. Ils ne sont pas ce que le système collecte : ils sont ce qui justifie nos choix. Poids au runtime : **zéro**.

Usage MVP : charger une dizaine de chiffres globaux JCI comme points de comparaison, pour que le moteur puisse dire *« nous calculons X, JCI publie Y »* sans jamais substituer l'un à l'autre (règle AGG-5).

**Constat le plus important de tout l'inventaire** — la répartition des 465 indicateurs :

| Catégorie | Nombre | Ce que ça décrit |
|---|---|---|
| OUTPUT | 234 | ce qui a été produit (personnes formées, objets distribués…) |
| CONTEXT | 124 | la structure du réseau (membres, pays, clubs…) |
| ACTIVITY | 37 | ce qui a été fait |
| INPUT | 37 | ce qui a été mobilisé (bénévoles, heures) |
| UNCERTAIN | 20 | inclassable en l'état |
| **OUTCOME** | **12** | **ce qui a changé** |
| **IMPACT-CLAIM** | **1** | **une revendication d'impact** |

**13 chiffres sur 465 parlent de changement réel. 2,8 %.** Sur 174 pages de rapport d'impact. Et sur les 12 outcomes, aucun n'a de méthode de mesure décrite, et l'un d'eux est « dozens » — un mot, pas un nombre.

C'est l'argument central du pitch, et il est chiffré.

### Les 26 conflits — **registre de gouvernance, pas dette technique**

Contradictions internes au rapport JCI, conservées sans arbitrage. Poids au runtime : **zéro**.

Retenus pour la démo (4 sur 26, les plus parlants) :

| Réf | Sujet | Les valeurs |
|---|---|---|
| DQC-01 | Nombre de membres | 100 000 (p. v) · 147 000 (p. 2) · 147 670 (p. 8) |
| DQC-03 | Nombre de projets | 1 000+ (p. v, 84, 85) · 10 000+ (p. vii) — **facteur 10** |
| DQC-13 | Impulso NOA | 4 nouveaux membres sur 22 déclarés « 20 % » — le calcul donne 18,18 % |
| DQC-24 | Périodes de reporting | 2024–2025 · 2025 · janvier–octobre 2025 · octobre 2024–août 2025, dans le même document |

Les 22 autres restent dans le registre, consultables, non affichés.

### Les 45 champs → 12 — **la seule vraie coupe**

C'est ici que se joue le risque de trop-plein, et il est traité par le §3 ci-dessus. Les 33 champs écartés restent documentés dans Tier 2 §G.2 comme cible produit.

---

## 5. Ce que cette réduction ne touche pas

Le périmètre a été réduit sur le **volume de saisie**, jamais sur les **règles de sens**. Restent intégralement actives :

- les quatre couches de provenance et la règle P0
- `unknown` n'est jamais `0`
- le refus d'agrégation sur non-équivalence sémantique
- la séparation membres JCI / public externe
- la distinction effort / production / résultat
- la traçabilité du total global jusqu'à la phrase source

Ce sont elles qui font la valeur du produit. Un MVP à 13 champs qui les respecte vaut mieux qu'un MVP à 45 champs qui les perd.
