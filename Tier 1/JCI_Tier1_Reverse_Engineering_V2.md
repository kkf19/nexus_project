# JCI Impact Report 2025 — Reverse engineering & provenance — **V2**
## TIER 1 : A (Vocabulaire) · B (Couche de normalisation IAOOI — proposée) · C (Taxonomie) · D (JSON normalisé) · E (5 cas de test)
## + Modèle de provenance · Registre des conflits (24 + 2) · Registre des données visuelles non extraites

> Source officielle unique : `Impact Report 2025_compressed.pdf` (JCI Impact Report 2025), document du projet « Nexus Hackathon ».
> Citations au format **[p. X — Section]**, où X = **folio imprimé** (pages de garde : ii–vii).

---

## Journal des changements V1 → V2

| # | Changement | Pourquoi |
|---|---|---|
| 1 | Les statuts FACT / INFERENCE / RECOMMENDATION deviennent **OFFICIAL_JCI_FACT / SEMANTIC_INTERPRETATION / PROPOSED_STANDARD** (§P.1). UNKNOWN n'est plus une couche : c'est un **statut de valeur** (§P.2) | Séparer **d'où vient** une information de **ce qu'on sait de sa valeur** |
| 2 | **Nouvelle règle fondamentale P0** : *« No unsupported inference becomes an official JCI fact. »* + 14 règles dérivées (§P.4) | Empêcher les hallucinations institutionnelles |
| 3 | La chaîne Input → Activity → Output → Outcome → Impact (IAOOI) est présentée comme une **couche de normalisation analytique proposée par votre solution**, jamais comme un cadre JCI (§B) | Le rapport ne contient pas ce cadre |
| 4 | « Area » est scindé en **`geographic_area`** et **`area_of_opportunity`**. Le mot seul est interdit dans les données (§G) | Homonymie documentée dans le rapport |
| 5 | Les incohérences du rapport deviennent **26 objets de qualité** DQC-01…26 (les 24 de V1 + 2 relevées dans les remarques V1). Tous sont en **UNRESOLVED**, avec un cas de test chacun (§Q) | Aucune résolution silencieuse |
| 6 | Les graphiques illisibles deviennent **9 objets VDX** au statut `visual_data_not_extracted` (valeur `null`, jamais 0, jamais déduite) (§V) | Pas de valeur inventée |
| 7 | JSON V2 : **provenance par champ** (couche, statut de valeur, source/page/citation, règle appliquée). Valeur et normalisation sont séparées dans chaque métrique (§D, §E) | Traçabilité jusqu'au champ |
| 8 | Ajout d'un **validateur automatique** des règles de provenance (`validate_provenance.py`), exécuté sur tous les JSON livrés (§P.6) | Rendre les règles exécutables |
| — | **Inchangé** : l'inventaire des 132 métriques, la taxonomie, les 5 scénarios de test, votre squelette JSON à 11 clés | Pas de refonte de l'architecture |

---

# P. MODÈLE DE PROVENANCE — RÈGLE FONDAMENTALE DU MOTEUR

## P.0 Règle fondamentale

> ### **P0 — No unsupported inference becomes an official JCI fact.**
> Une information n'est **OFFICIAL_JCI_FACT** que si elle est **écrite dans une source JCI** et **citée** : document, page, section, citation exacte. Tout le reste (déduction, normalisation, calcul, estimation, classement, code, validation humaine) reste dans sa couche, **quelle que soit la confiance**.

Corollaire à retenir : **OFFICIAL_JCI_FACT certifie que JCI l'écrit, pas que c'est vrai.**
« 250 tons of CO2 emissions annually » [p. 30] est un OFFICIAL_JCI_FACT **en tant qu'affirmation publiée**. Ce n'est **pas** un impact vérifié. Le champ `fact_scope` le précise (`statement_published`).

## P.1 Les trois couches de connaissance (axe « d'où ça vient »)

| Couche | Définition | Qui la produit | Exigence minimale | Exemples tirés du rapport | Peut être promue ? |
|---|---|---|---|---|---|
| **OFFICIAL_JCI_FACT** | Explicitement présent dans une source JCI : vocabulaire, chiffre, programme, Area of Opportunity, ODD, libellé | Extraction littérale | `source.origin = jci_report_2025` + `page` + `section` + `quote` exacte | « 42,401 Total Number of Volunteers Engaged » [p. 86] ; « Four Areas of Opportunity » [p. 24] ; « JCI RISE » [p. 85] | — (couche la plus haute) |
| **SEMANTIC_INTERPRETATION** | Ce que le moteur **déduit, normalise, classe, calcule ou rapproche** à partir de données sources | Moteur (règle ou LLM), éventuellement validé par un humain | `rule_id` ou `basis` + source(s) d'entrée + `confidence` | 42,401 bénévoles classés **INPUT/RESOURCE** alors que le rapport les range sous « Measurable outcomes » [p. 87–90] ; 148 000 + 41 000 + 32 000 + 8 200 = 229 200 ; Bridges Project → pilier RISE « Sustaining and Rebuilding Economies » | **Jamais vers OFFICIAL_JCI_FACT**, sauf si une source JCI citée l'affirme (on crée alors un nouveau fait, avec sa citation) |
| **PROPOSED_STANDARD** | Ce que **votre solution propose** pour rendre les données comparables et agrégables : codes, listes contrôlées, cadre IAOOI, types d'activité, de bénéficiaire, d'output, d'outcome, d'impact, statuts | Équipe produit | Version du standard (`standard_version`) | `TRAINING_WORKSHOP`, `YOUTH`, `PEOPLE_TRAINED`, `JOB_PLACEMENT`, codes `BE/ID/IC/CI`, cadre IAOOI | Adoptable par décision d'équipe (reste PROPOSED_STANDARD, pas JCI) |

**Extension nécessaire, à valider par votre équipe — `LOCAL_REPORTED_FACT`** (PROPOSED_STANDARD) : c'est ce qu'une **organisation locale déclare** dans sa soumission (ex. « 64 inscrits »). Ce n'est ni un fait JCI officiel, ni une interprétation, ni une proposition. Sans cette étiquette, les 5 cas de test obligeraient à classer des déclarations locales en OFFICIAL_JCI_FACT, ce qui violerait P0. Elle a le même rang qu'OFFICIAL_JCI_FACT pour l'exigence de citation (`quote` de la soumission), mais **ne devient jamais officielle JCI** (règle P9). Si vous préférez rester à trois couches, renommez-la ; ne la fusionnez pas avec OFFICIAL_JCI_FACT.

**Couche d'une valeur vs couche d'une classification.** Un même chiffre porte deux provenances distinctes. Exemple, « 15 volunteers engaged » [p. 87] :
- la **valeur** 15 = OFFICIAL_JCI_FACT ;
- le **libellé JCI** de sa rubrique (« Measurable outcomes ») = OFFICIAL_JCI_FACT ;
- le **code** `VOLUNTEERS` et la **classe IAOOI** `INPUT` = SEMANTIC_INTERPRETATION appliquant un PROPOSED_STANDARD.

Le JSON V2 stocke séparément `value{…}` et `normalization{…}` pour chaque métrique.

## P.2 Statut de la valeur (axe « que sait-on de ce nombre »)

| `value_status` | Définition | Valeur | Couche compatible |
|---|---|---|---|
| `extracted` | Copiée de la source, y compris les approximations de la source (« 1,000+ », « around ») → encodées dans `value_qualifier` | Nombre / texte | OFFICIAL_JCI_FACT, LOCAL_REPORTED_FACT |
| `calculated` | Produite par le moteur par une **formule déterministe** à partir de valeurs `extracted` | Nombre + `formula` + `inputs[]` | **SEMANTIC_INTERPRETATION uniquement** |
| `estimated` | Produite par une **méthode non déterministe** (hypothèse, ratio, modèle, jugement) | Nombre + `method` + `assumptions[]` | **SEMANTIC_INTERPRETATION uniquement** |
| `unknown` | Nécessaire, absente de la source → « NOT SPECIFIED IN THE SOURCE DOCUMENT » | **`null`** | toute couche (décrit un manque) |
| `visual_data_not_extracted` | Présente dans un graphique mais non lisible dans la couche texte | **`null`** (jamais 0, jamais déduite) | OFFICIAL_JCI_FACT (le graphique existe) |
| `conflicting` | Plusieurs valeurs sources incompatibles, rattachées à un objet DQC | Toutes les valeurs conservées, aucune choisie | OFFICIAL_JCI_FACT |

**Portée de `value_status`** : il ne s'applique qu'aux **valeurs mesurées** (nombres, montants, dates, comptes). Les **attributions** (code d'activité, classe IAOOI, pilier RISE, area_of_opportunity déduite…) n'ont pas de `value_status`. Elles portent `layer` + `rule_id`/`basis` + `confidence`.

`value_qualifier` ∈ {`exact`, `approx`, `at_least`, `at_most`, `range`} décrit la **précision déclarée par la source**. Il ne transforme jamais une valeur `extracted` en `estimated`.

## P.3 Combinaisons autorisées (couche × statut)

| | extracted | calculated | estimated | unknown | visual_data_not_extracted | conflicting |
|---|---|---|---|---|---|---|
| OFFICIAL_JCI_FACT | ✅ | ❌ (→ SEMANTIC_INTERPRETATION) | ❌ | ✅ | ✅ | ✅ |
| LOCAL_REPORTED_FACT | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| SEMANTIC_INTERPRETATION | ❌ (rien n'est « extrait » par interprétation) | ✅ | ✅ | ✅ | ❌ | ❌ |
| PROPOSED_STANDARD | ❌ (un standard ne porte pas de valeur mesurée) | ❌ | ❌ | ❌ | ❌ | ❌ |

PROPOSED_STANDARD qualifie des **codes, listes et cadres**, pas des valeurs mesurées.

## P.4 Règles dérivées (exécutables)

| ID | Règle | Contrôle automatique (§P.6) |
|---|---|---|
| **P0** | No unsupported inference becomes an official JCI fact | V2, V6 |
| P1 | OFFICIAL_JCI_FACT ⇒ `source.origin = jci_report_2025` ∧ `page` ∧ `section` ∧ `quote` non vide | V2 |
| P2 | `calculated` ⇒ SEMANTIC_INTERPRETATION ∧ `formula` ∧ `inputs` | V4 |
| P3 | `estimated` ⇒ SEMANTIC_INTERPRETATION ∧ `method` | V4 |
| P4 | `unknown` / `visual_data_not_extracted` ⇒ `value = null`. **Jamais 0. Jamais une valeur déduite** | V3 |
| P5 | Le cadre IAOOI, les codes de métrique, types d'activité, de bénéficiaire, d'output, d'outcome et d'impact sont **PROPOSED_STANDARD**. Leur **attribution** à une donnée est **SEMANTIC_INTERPRETATION** | V6 |
| P6 | Officiels JCI : **area_of_opportunity** (4 valeurs), **programmes explicitement nommés**, **ODD**, **geographic_area** (4 valeurs). Leurs **codes courts** (`BE`, `ID`, `IC`, `CI`, `AFME`, `AMERICA`, `EUROPE`) sont PROPOSED_STANDARD — exception : l'abréviation « ASPAC », elle, apparaît dans le rapport [p. 81, 106, 128] | V6 |
| P7 | Le mot « Area » seul est interdit comme clé ou valeur de type. Toujours `geographic_area` ou `area_of_opportunity`. Sans contexte suffisant ⇒ `AMBIGUOUS_AREA` (§G), jamais tranché par le LLM | V9 |
| P8 | Conflit entre valeurs sources ⇒ objet DQC, **toutes les valeurs conservées**, `resolution_status = UNRESOLVED` tant que JCI ou l'équipe n'a pas tranché explicitement | V8 |
| P9 | LOCAL_REPORTED_FACT ne devient jamais OFFICIAL_JCI_FACT, même s'il est repris dans un rapport agrégé du moteur | V7 |
| P10 | La validation humaine augmente la `confidence` d'une interprétation et ajoute `validated_by`. **Elle ne change pas la couche** | V5 |
| P11 | OFFICIAL_JCI_FACT = « JCI l'a écrit ». Une affirmation d'impact reste `fact_scope = statement_published`, `attribution_level = narrative_only` tant qu'aucune mesure n'est citée | revue |
| P12 | Aucun agrégat ne mélange des couches, des statuts ou des périmètres (membres vs bénéficiaires externes, audience comm. vs bénéficiaires, événements externes) sans le déclarer dans ses `inputs` | revue |
| P13 | Une association valeur ↔ libellé déduite de la mise en page d'un graphique est SEMANTIC_INTERPRETATION (`chart_label_association`), pas OFFICIAL_JCI_FACT | V6 |
| P14 | Toute sortie destinée à un humain affiche la couche de chaque chiffre (ex. badge JCI / Interprété / Calculé / Estimé / Inconnu) | UI (votre choix) |

## P.5 Correspondance V1 → V2 (pour relire V1 sans erreur)

| Étiquette V1 | Étiquette V2 |
|---|---|
| FACT | OFFICIAL_JCI_FACT |
| INFERENCE | SEMANTIC_INTERPRETATION |
| RECOMMENDATION / RECO | PROPOSED_STANDARD |
| UNKNOWN / « NOT SPECIFIED… » | `value_status = unknown` |
| Graphique illisible | `value_status = visual_data_not_extracted` + objet VDX |
| Incohérence I1…I24 (B.6) | Objet DQC-01…24 (§Q) |
| Classe IAOOI (colonne « Classe » de B.2) | SEMANTIC_INTERPRETATION selon le standard PROPOSED_STANDARD `IAOOI-v0` |
| « CONTEXT », « IMPACT-CLAIM », « UNCERTAIN » | Valeurs du standard IAOOI-v0 (PROPOSED_STANDARD) |

## P.6 Validateur (règles rendues exécutables)

`validate_provenance.py` parcourt n'importe quel JSON V2 et vérifie :

| Check | Règle | Échec si… |
|---|---|---|
| V1 | couches valides | `layer` ∉ {OFFICIAL_JCI_FACT, LOCAL_REPORTED_FACT, SEMANTIC_INTERPRETATION, PROPOSED_STANDARD} |
| V2 | P0/P1 | OFFICIAL_JCI_FACT sans origin=jci_report_2025, page, section ou quote |
| V3 | P4 | statut `unknown`/`visual_data_not_extracted` avec valeur non nulle |
| V4 | P2/P3 | `calculated` sans formula/inputs ; `estimated` sans method ; couche ≠ SEMANTIC_INTERPRETATION |
| V5 | P10 | SEMANTIC_INTERPRETATION sans `rule_id`/`basis` ; `validated_by` présent sur une couche ≠ SEMANTIC_INTERPRETATION |
| V6 | P5/P6/P13 | champ de normalisation (`metric_code`, `iaooi_class`, `activity_type`, `target_group`, `outcome_type`, `impact_type`, `chart_label_association`) marqué OFFICIAL_JCI_FACT |
| V7 | P9 | objet d'un cas `fictional: true` marqué OFFICIAL_JCI_FACT hors vocabulaire JCI (programme, AoO, ODD, geographic_area) |
| V8 | P8 | conflit sans ≥2 valeurs sourcées, ou `UNRESOLVED` avec `resolution` non nulle |
| V9 | P7 | clé `area` nue |
| V10 | §P.3 | combinaison couche × statut interdite (§P.3) |

Résultat de l'exécution sur les livrables V2 : voir la checklist en fin de document.

---

# G. « AREA » : DEUX CONCEPTS DISTINCTS ET NON INTERCHANGEABLES

## G.1 Définitions

| Concept | Définition | Valeurs officielles (OFFICIAL_JCI_FACT) | Code proposé (PROPOSED_STANDARD) | Source |
|---|---|---|---|---|
| **`geographic_area`** | Division géographique du réseau JCI. Niveau « Regional » de la structure Local → National → Regional → Global | « Africa and the Middle East » · « America » · « Asia and the Pacific » · « Europe » | `AFME` · `AMERICA` · `ASPAC` (abréviation présente dans le rapport, p. 81, 106, 128) · `EUROPE` | « JCI operates across 4 Areas of the world » [p. 8 — Membership Details] ; « four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe » [p. 9 — International Presence] |
| **`area_of_opportunity`** | Domaine thématique de développement | « Business & Entrepreneurship » · « Individual Development » · « International Cooperation » · « Community Impact » | `BE` · `ID` · `IC` · `CI` | « JCI creates development opportunities through four interlinked areas » [p. 2 — Organization Overview] ; « four interconnected Areas of Opportunity » [p. 24 — Four Areas of Opportunity and SDG Alignment] |

Variantes de libellés **observées** (OFFICIAL_JCI_FACT), à normaliser vers la valeur canonique (SEMANTIC_INTERPRETATION, règle `NORM-AREA-LABEL`) :
- `geographic_area` : « Africa & the Middle East », « Africa & Middle East », « Asia & the Pacific », « Asia-Pacific », « Asia Pacific », « ASPAC », « Americas » [p. vi, 124] ;
- `area_of_opportunity` : « Business and Entrepreneurship ».

## G.2 Règles de désambiguïsation (le LLM ne décide jamais seul)

| ID | Déclencheur dans le texte | Résolution | Couche de la résolution |
|---|---|---|---|
| AREA-1 | « Area(s) of Opportunity », « Area of Opportunity » | `area_of_opportunity` | OFFICIAL_JCI_FACT (libellé explicite) |
| AREA-2 | Valeur égale à l'un des 4 libellés géographiques ou à leurs variantes | `geographic_area` | SEMANTIC_INTERPRETATION (`NORM-AREA-LABEL`), confiance H |
| AREA-3 | Valeur égale à l'un des 4 libellés thématiques | `area_of_opportunity` | SEMANTIC_INTERPRETATION, confiance H |
| AREA-4 | « Area Conference(s) », « Area Development Councils », « Area winners », « Regional Areas », « Areas of the world » | `geographic_area` | SEMANTIC_INTERPRETATION, confiance H |
| AREA-5 | « per Area » suivi d'une ventilation par libellés géographiques | `geographic_area` | SEMANTIC_INTERPRETATION, confiance H |
| AREA-6 | « Area(s) » seul, sans qualificatif ni liste de valeurs | **`AMBIGUOUS_AREA`** : ne pas trancher, signaler, demander une validation humaine | — |

## G.3 Occurrences du rapport classées (jeu de test prêt à l'emploi)

| # | Citation exacte | Page — Section | Concept attendu | Règle |
|---|---|---|---|---|
| 1 | « driving sustainable impact across four Areas of Opportunity » | v — Executive Summary | area_of_opportunity | AREA-1 |
| 2 | « More than 100,000 young leaders across four Areas came together » | vi — Message from JCI President | **AMBIGUOUS_AREA** | AREA-6 (le contexte suggère la géographie, mais rien ne le dit explicitement) |
| 3 | « With respondents representing all four Areas » | 3 — The Profile of a JCI Member | **AMBIGUOUS_AREA** | AREA-6 (géographie probable : la phrase suivante compare Africa & the Middle East et Europe → candidat geographic_area, confiance M, à valider) |
| 4 | « JCI operates across 4 Areas of the world » | 8 — Membership Details | geographic_area | AREA-4 |
| 5 | « four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe » | 9 — International Presence | geographic_area | AREA-4 |
| 6 | « Number of National Organizations (Area Wise) » | 10 — National Organizations | geographic_area | AREA-5 |
| 7 | « projects aligned with JCI's four Areas of Opportunity » | 13 — JCI Junior Club | area_of_opportunity | AREA-1 |
| 8 | « present in over 100 countries and four Areas of the world » | 24 — Four Areas of Opportunity | geographic_area (dans une section AoO !) | AREA-4 |
| 9 | « (JIB) sessions were hosted at all JCI Area Conferences » | 33 — JIB | geographic_area | AREA-4 |
| 10 | « JCI in Business (JIB) Participation from Different Areas » | 34 — JIB | geographic_area | AREA-5 |
| 11 | « Align JCI's strategies and programs across Areas » | 59 — JCI Events | **AMBIGUOUS_AREA** | AREA-6 |
| 12 | « International Human Duties Reported Activites per Area » | 73 — IHD | geographic_area | AREA-5 |
| 13 | « 2025 Projects Reported per Area » | 86 — JCI RISE Projects | geographic_area | AREA-5 |
| 14 | « 2025 Projects Reported per Area of Opportunity » | 86 — JCI RISE Projects | area_of_opportunity | AREA-1 |
| 15 | « Some projects may fall under 2 or more Area of Opportunity » | 86 | area_of_opportunity | AREA-1 |
| 16 | « Area Development Councils may request financial assistance » | 97 — Development Grants | geographic_area | AREA-4 |
| 17 | « Number of Projects per Year per Area » | 98 — Development Grants | geographic_area (valeurs illisibles, VDX-06) | AREA-5 |
| 18 | « across JCI's four Areas of Opportunity » | 102 — JCI Awards | area_of_opportunity | AREA-1 |
| 19 | « Best of the Best Awards (Area winners qualify for World Congress) » | 102 — JCI Awards | geographic_area | AREA-4 |
| 20 | « Award Entries Submitted per Area » | 103 — Most Outstanding Members | geographic_area | AREA-5 |
| 21 | « organized around JCI's Four Areas of Opportunity » | 123 — Global Youth Dialogue | area_of_opportunity | AREA-1 |
| 22 | « Gobal Youth Dialogue Attendees per Area » | 123 — Global Youth Dialogue | geographic_area (valeurs illisibles, VDX-09) | AREA-5 (sans liste visible → confiance M) |

> Le même document utilise les deux sens **sur une même page** (lignes 13, 14, 15 : p. 86 ; lignes 21, 22 : p. 123), et une section « Areas of Opportunity » emploie le sens géographique (ligne 8, p. 24). Une règle fondée sur la seule section serait fausse.

## G.4 Conséquences dans les données V2

| Avant (V1) | Après (V2) |
|---|---|
| `organization.area` | `organization.geographic_area` |
| `project.areas_of_opportunity` | `project.area_of_opportunity[]` (liste ; ≥1 valeur, OFFICIAL_JCI_FACT p. 86) |
| `recognition.level = "Area"`, `recognition.area` | `recognition.level = "geographic_area"`, `recognition.geographic_area` |
| Colonnes « per Area » dans B.2 | à lire comme `geographic_area` (AREA-5) ; « per Area of Opportunity » = `area_of_opportunity` |

---

## 0. Déclaration de couverture (contrainte de traitement)

| # | Point | Réponse |
|---|---|---|
| 1 | Accès à l'intégralité du document ? | **Oui pour la couche texte, en une seule passe.** J'ai lu le texte extrait de la couverture, des pages ii–vii et des folios imprimés 1 à 174 (dernier folio : quatrième de couverture). |
| 2 | Nombre de pages | Le brief mentionne « ~148 pages ». La **pagination imprimée du document va jusqu'à 174** (+ 7 pages romaines). L'écart vient probablement du nombre de pages physiques du PDF compressé (doubles pages, pleines pages photo). **Toutes les citations utilisent le folio imprimé**, qui est stable quel que soit le lecteur PDF. |
| 3 | Ce que je n'ai PAS pu lire | Je n'ai pas vu le rendu visuel. **Les valeurs portées uniquement par des graphiques sont absentes ou non associables** sur les pages ci-dessous. Elles portent le statut **`visual_data_not_extracted`** partout dans ce document : valeur `null`, jamais 0, jamais déduite (registre §V, objets VDX-01…09). |

**Pages avec perte d'information (graphiques non lisibles en texte) :**

| Page | Élément | Ce qui manque (statut `visual_data_not_extracted`) |
|---|---|---|
| p. 9 (VDX-01) | Carte « Global Presence (114 Countries) » | Liste des pays |
| p. 42 (VDX-02) | « Participation in Conferences » (Trainings) | Répartition des 1 969 participants par conférence |
| p. 60 (VDX-03) | « National Organization Attendances per Area Conference (2025) » | Toutes les valeurs |
| p. 84 (VDX-04) | « Primary SDGs Addressed / Secondary SDG » | Toutes les valeurs (graphique central pour le mapping ODD) |
| p. 97–98 (VDX-05, 06) | « Amount of Grants (USD) Received per Year » / « Number of Projects per Year per Area » | Les nombres sont présents (33, 28, 40, 37 500, 28 600…) mais **l'association valeur ↔ année ↔ geographic_area n'est pas reconstructible** ; ces fragments sont inutilisables |
| p. 118 (VDX-07, 08) | « RISE to the Challenge Attendees per Area » / « Languages per Area » | Toutes les valeurs |
| p. 123 (VDX-09) | « Gobal Youth Dialogue Attendees per Area » (orthographe du rapport) | Valeurs par geographic_area (seul Members vs Non-Members est lisible) |
| p. 14, 62–63, 66–69, 108, 130, 134–170 (pages paires) | Pages photos | Aucune donnée textuelle attendue |

**Proposition de 2e passe (si vous voulez combler ces trous)** : m'envoyer des captures de ces ~8 pages (9, 42, 60, 84, 97, 98, 118, 123). Chaque valeur récupérée sera ajoutée avec sa page, sans toucher au reste.

Les pages 133–170 (« 110 Years of Impact ») contiennent la liste historique des présidents, thèmes et congrès mondiaux. Je les ai lues. Elles n'apportent aucune métrique d'impact et ne servent qu'au vocabulaire (ex. « Jaycees »).

---

## Synthèse — les 8 constats structurants (à lire avant le reste)

| # | Constat | Statut | Source |
|---|---|---|---|
| S1 | **Le rapport ne définit nulle part les termes input / output / outcome / impact.** « Impact » sert d'intitulé de section générique (« Impact through the Program »), y compris pour décrire des activités. | CONSTAT D'ABSENCE (couche texte vérifiée) | ensemble du document |
| S2 | **Des INPUTS sont étiquetés « outcomes »** : « Measurable outcomes included 244 volunteer hours, and 15 volunteers engaged ». Le même gabarit est répété pour 4 projets. | OFFICIAL_JCI_FACT | [p. 87, 88, 89, 90 — Community Impact Stories] |
| S3 | **La chaîne agrégée s'arrête à l'OUTPUT** (bénéficiaires atteints). Les outcomes n'existent que dans des récits individuels, auto-déclarés, sans méthode ni groupe de comparaison. Aucun IMPACT n'est mesuré avec attribution. | SEMANTIC_INTERPRETATION (H) | [p. v, 84–86] vs récits p. 29–107 |
| S4 | **Homonymie du mot « Area »** (→ scindé en `geographic_area` / `area_of_opportunity`, §G) : il désigne à la fois la **zone géographique** (4 Areas : Africa & the Middle East, America, Asia & the Pacific, Europe) et le **domaine thématique** (4 *Areas of Opportunity*). Un LLM confondra les deux sans règle explicite. | OFFICIAL_JCI_FACT | [p. 8–9] vs [p. 2, 24] |
| S5 | **Les chiffres de tête sont incohérents d'une page à l'autre** (membres, pays, projets, bénévoles, abonnés, lecteurs…). Registre §Q : DQC-01…26, tous UNRESOLVED. | OFFICIAL_JCI_FACT | multiples |
| S6 | **Deux populations de « bénéficiaires » sont mélangées** : les **membres JCI** (Individual Development, formations, compétitions) et les **communautés externes** (Community Impact). Le rapport ne les sépare jamais dans les agrégats. | SEMANTIC_INTERPRETATION (H) | [p. 40–52] vs [p. 84–94] |
| S7 | **L'alignement ODD est déclaratif et inflationniste** : « SDGs Hunt » déclare 17 ODD (ODD 11 cité deux fois) pour 4 heures de bénévolat et 5 bénévoles. | OFFICIAL_JCI_FACT | [p. 89] |
| S8 | **Un système de reporting existe déjà côté JCI** (« Projects Reported », « The submission describes… », champs Primary/Secondary SDG, multi-tag Area of Opportunity, piliers RISE). Le rapport ne le décrit pas. On peut seulement en déduire les champs. | SEMANTIC_INTERPRETATION (M) | [p. 84–90] |
| — | **Point d'ancrage pour votre produit** : « Every local project will align with one or more SDGs and report measurable results. » | OFFICIAL_JCI_FACT | [p. 132 — Road Map for 2026] |

---

# A. JCI OFFICIAL VOCABULARY

> Colonne « Statut » = **couche de provenance** (§P.1) de la définition ou du rattachement. « UNKNOWN » = `value_status: unknown` (NOT SPECIFIED IN THE SOURCE DOCUMENT). Une paraphrase fidèle d'un passage cité reste OFFICIAL_JCI_FACT ; une déduction à partir de plusieurs passages est SEMANTIC_INTERPRETATION.

> Règle de lecture : la colonne « Définition » cite le document. Quand le document ne définit pas le terme : **NOT SPECIFIED IN THE SOURCE DOCUMENT**.

## A.1 Organisation, gouvernance, structure

| Terme officiel | Définition (document) | Variantes / synonymes trouvés | Distinction avec concepts voisins | Pages | Statut |
|---|---|---|---|---|---|
| **Junior Chamber International (JCI)** | « a global, non-profit organization of young people between 18 and 40 who are united by a shared mission: to develop leaders for a changing world » | JCI ; « Jaycees » ; « Junior Chamber » ; « JCI, Inc. » | — | 2, 46, 74, 156, ii | OFFICIAL_JCI_FACT |
| **JCI Mission** | « To provide leadership development opportunities that empower young people to create positive change. » | « Our Purpose » (p. 2, 1er point identique) | ≠ Vision | 2, 4 | OFFICIAL_JCI_FACT |
| **JCI Vision** | « To be the foremost global network of young leaders. » | — | ≠ **Vision 2040**, citée p. vi mais **NOT SPECIFIED IN THE SOURCE DOCUMENT** | 4, vi | OFFICIAL_JCI_FACT / UNKNOWN (V2040) |
| **JCI Creed** | 6 énoncés « We believe… » | « JCI Values » | — | 4 | OFFICIAL_JCI_FACT |
| **Tagline** | « Developing Leaders for a Changing World » | — | — | 2, 174 | OFFICIAL_JCI_FACT |
| **Four levels** | « JCI is structured at four levels: Local, National, Regional, and Global. » | — | Le niveau « Regional » = les Areas géographiques | 9 | OFFICIAL_JCI_FACT |
| **Local Organization (LO)** | « grassroots hubs where young leaders directly engage with their communities to identify needs, design solutions, and implement projects » ; « provide the grassroots foundation where projects are designed and executed » | « local chapter(s) », « chapter », **« LOM »** (acronyme non développé), nom propre « JCI + ville » (JCI Mahajanga, JCI Hernandarias, JCI Frankfurt, JCI Ankara, JCI Kowloon, JCI Quatre Bornes, JCI Impact Mongolia, JCI Wayma…) | **Unité d'exécution des projets** (OFFICIAL_JCI_FACT p. 8). Nombre : 4 641 (p. 8, 11) / « 4,600 » (p. 2) / « 4,500+ » (p. v, vii) | 8, 11, 21, 82 | OFFICIAL_JCI_FACT ; « LOM » = Local Organization Member → SEMANTIC_INTERPRETATION (M) |
| **National Organization (NO)** | « These entities unite Local Organizations under a national framework » ; rôles : stratégie nationale, formation, coordination, représentation, pont vers TOYP, RISE, IHDD | « JCI + pays » (JCI Syria, JCI Paraguay…) | **NO ≠ pays** : « JCI West Indies » couvre plusieurs pays (Antigua p. 105) ; « JCI Hong Kong, China » ; « JCI New York States » (p. 71, niveau infranational). Nombre : 114 | 10, 71, 105 | OFFICIAL_JCI_FACT (définition) ; NO≠pays → SEMANTIC_INTERPRETATION (H) |
| **`geographic_area`** (mot du rapport : « Area ») | « JCI operates across 4 Areas of the world » ; « four Regional Areas » | « Regional Areas », « Area » ; abréviations : **ASPAC** (p. 81, 106, 128), **AMEC** (p. 49 « 2024 AMEC Conference ») | **≠ Area of Opportunity** (voir S4) | 8, 9 | OFFICIAL_JCI_FACT |
| **Regional Office** | 4 bureaux (Africa & ME : Nigeria ; Asia-Pacific : Malaisie ; America : Paraguay ; Europe : adresse absente) | — | — | ii, 9 | OFFICIAL_JCI_FACT ; adresse Europe UNKNOWN |
| **JCI Headquarters / JCI World Headquarters** | « Global operations are led by JCI Headquarters in St. Louis, USA » | Adresse imprimée : Chesterfield, MO | Deux localisations citées (St. Louis p. 9 / Chesterfield p. ii) | ii, 9, 172 | OFFICIAL_JCI_FACT |
| **Board of Directors** | Liste 2025 (Président, EVP, VP, Trésorier, General Legal Counsel, IPP, SG par intérim) | — | — | 6 | OFFICIAL_JCI_FACT |
| **Executive Committee** | « responsible for receiving, analyzing projects and determining the distribution of the JCI Development Grants » | — | — | 97 | OFFICIAL_JCI_FACT |
| **Area Development Councils** | Peuvent demander des development grants | — | Définition : NOT SPECIFIED | 97 | OFFICIAL_JCI_FACT (mention) |
| **General Assembly** | Tenue au World Congress | — | — | 61 | OFFICIAL_JCI_FACT (mention) |
| **ESG Committee** | Comité 2025 ayant contribué au rapport | « Environmental, Social, and Governance Committee » | Probable producteur du rapport → SEMANTIC_INTERPRETATION (M) | 117, 172 | OFFICIAL_JCI_FACT |
| **LBOD** | « a joint LBOD group » | « Local Boards of Directors » (p. 172) | LBOD = Local Board of Directors → SEMANTIC_INTERPRETATION (H) | 81, 172 | SEMANTIC_INTERPRETATION |
| **JCI Foundation** | Créée en 1955, « provides the financial resources necessary to strengthen JCI's global mission » | — | Source de financement (INPUT), pas un programme d'impact | 96 | OFFICIAL_JCI_FACT |
| **JCI Senate / Senator** | « the highest honor… a lifetime recognition granted to individuals who have rendered outstanding service to JCI » | « JCI Senatorship » | ≠ Alumni Club | 100 | OFFICIAL_JCI_FACT |
| **JCI Alumni Club** | « maintains the connection and commitment of former members who have passed the age of 40 » | « Once a JCI member, always a JCI member » | ≠ Senate | 12 | OFFICIAL_JCI_FACT |
| **JCI Junior Club** | « engages young people between the ages of 14 and 21 » | « JCI Junior » (p. 75) | Tranche 14–21 **chevauche** celle des membres (18–40) | 13, 75 | OFFICIAL_JCI_FACT |
| **Club100** | « an exclusive network of 100 partners dedicated to supporting JCI's vision by investing in leadership development » | Niveaux cités : **Platinum**, **Bronze** (autres niveaux UNKNOWN) | Partenaire payant ≠ sponsor programme | 110, 119 | OFFICIAL_JCI_FACT |
| **ECOSOC General Consultative Status** | « A partner of the United Nations since 1954 » | — | — | 2 | OFFICIAL_JCI_FACT |
| **Membership Experience Survey (2025)** | Enquête : 3 767 répondants | — | **Seule source démographique** du rapport | 3 | OFFICIAL_JCI_FACT |

## A.2 `area_of_opportunity` — Areas of Opportunity (domaines d'impact)

| Terme officiel | Définition (document) | Variantes | ODD rattachés (document) | Pages | Statut |
|---|---|---|---|---|---|
| **`area_of_opportunity`** (mot du rapport : « Areas of Opportunity ») | « JCI creates development opportunities through four interlinked areas » ; « four interconnected Areas of Opportunity. These pillars… » | « Our Approach », « pillars », « interlinked areas », « Area of Opportunity » | ≠ Area géographique ; ≠ piliers RISE | 2, 24 | OFFICIAL_JCI_FACT |
| **Business & Entrepreneurship** | « Programs fostering innovation, ethical business, and sustainable economic growth » (p. 2) ; « opportunities for young people to develop entrepreneurial skills, showcase creativity, and build sustainable businesses » (p. 24) | « Business and Entrepreneurship » | 8, 9, 12 | 2, 24 | OFFICIAL_JCI_FACT |
| **Individual Development** | « Skills, training, and experiences that build confidence and leadership capacity » ; « certification pathways for trainers, public speaking competitions, and debating championships » | — | 4, 5, 10 | 2, 24 | OFFICIAL_JCI_FACT |
| **International Cooperation** | « Events, partnerships, and networks that connect young leaders across borders » ; « World Congress, Area Conferences, TOYP, and Human Duties Day » | — | 16, 17 | 2, 24–25 | OFFICIAL_JCI_FACT |
| **Community Impact** | « Grassroots projects addressing real needs in local societies » ; « JCI RISE and grassroots community projects » | — | 1, 2, 3, 4, 5, 8, 9, 11, 12, 13 | 2, 25 | OFFICIAL_JCI_FACT |
| Règle de multi-appartenance | « Some projects may fall under 2 or more Area of Opportunity » | — | — | 86 | OFFICIAL_JCI_FACT |

> ⚠ **ODD 6, 7, 14, 15 ne sont rattachés à aucune Area of Opportunity** [p. 24–25]. Ils apparaissent pourtant dans des récits : ODD 6 [p. 57, 89], 7 [p. 29, 89], 14 [p. 89], 15 [p. 32, 74, 75, 77, 89]. Le résumé exécutif affirme « Projects addressing all 17 SDGs » [p. v]. — OFFICIAL_JCI_FACT.

## A.3 Programmes, initiatives, événements

| Terme officiel | Définition / description (document) | Variantes | Area of Opportunity (placement dans le rapport) | Pages | Statut |
|---|---|---|---|---|---|
| **Creative Young Entrepreneur (CYE)** | « recognizes young entrepreneurs who use innovation and creativity to solve business challenges… JCI's flagship entrepreneurship competition » | « CYE program », « CYE competition » ; « Creative Young Entrepreneurs » (p. 113, 119) | B&E | 26, 28 | OFFICIAL_JCI_FACT |
| **CYE Accelerator Program** | Avec SDSN Youth : « mentorship, training, and global exposure » ; binômes venture ↔ mentors | — | B&E (SEMANTIC_INTERPRETATION : placé sous Partnerships) | 115–116 | OFFICIAL_JCI_FACT / SEMANTIC_INTERPRETATION |
| **JCI in Business (JIB)** | « JCI's global platform for entrepreneurs and professionals to connect, collaborate, and grow… a network and movement » ; « flagship initiative » | « JIB initiative » ; « JIB – International Business Matching Session » | B&E | 33, 121 | OFFICIAL_JCI_FACT |
| **Skills Development (framework)** | « structured pathways for members to advance as trainers at the national, regional, and global levels » | « Trainer Certification Program » (p. 2), « certification pathways » | ID | 2, 40 | OFFICIAL_JCI_FACT |
| Catégories de formateurs | « CNTs, CATs, Global Trainers, Training Mentors » | « Certified National and Area Trainers » (p. 106) | ID | 41, 106 | OFFICIAL_JCI_FACT ; CNT = Certified National Trainer, CAT = Certified Area Trainer → SEMANTIC_INTERPRETATION (H) |
| **Trainings at Area Conferences and World Congress** | « structured learning opportunities in leadership, entrepreneurship, sustainability, and communication » | « Leadership Training Sessions », « Skills Development Sessions » | ID | 42 | OFFICIAL_JCI_FACT |
| **Leadership Masterclasses** | Mappage ODD uniquement (4, 5, 10, 16, 17) ; aucune description ni chiffre | — | Non placé (SEMANTIC_INTERPRETATION : ID) | 26 | OFFICIAL_JCI_FACT (mention) |
| **Public Speaking Competition** | « develops members' ability to express ideas clearly and confidently… at Area Conferences and World Congress » | « Public Speaking Program » | ID | 43–44 | OFFICIAL_JCI_FACT |
| **Debating Championship** | « sharpens members' critical thinking, teamwork, and persuasion. Conducted in English, French, and Spanish » | « JCI Debating » ; unité = **équipes** | ID | 48 | OFFICIAL_JCI_FACT |
| **Ten Outstanding Young Persons of the World (TOYP)** | « honors extraordinary young leaders who excel in their fields and create positive change in society » ; 10 lauréats par an | « Ten Outstanding Young Persons » (p. 26) ; « Ten Outstanding Persons of the Year » (p. 113, **erreur de libellé**) | IC | 26, 54, 113 | OFFICIAL_JCI_FACT |
| **World Congress / Area Conferences** | « bring together members, partners, and stakeholders to exchange knowledge, build partnerships, and celebrate leadership » | « JCI Events » ; noms : Conference of America, Africa & Middle East Conference (AMEC), European Conference, Asia-Pacific Conference (ASPAC) | IC (hébergent aussi des activités ID et B&E) | 59–70 | OFFICIAL_JCI_FACT |
| **International Human Duties Initiative** | « emphasizing that rights must be complemented by responsibilities » | « IHD » | IC | 71 | OFFICIAL_JCI_FACT |
| **International Human Duties Day (IHDD)** | « held annually on July 10 » | « Human Duties Day » | IC | 71 | OFFICIAL_JCI_FACT |
| **Universal Declaration of Human Duties for Leaders** | Lancée en 2022 ; ancrage de l'initiative | « 7 Duties for Leaders », « International Human Duties 7 principles », « 7 Human Duties for Leaders » | — | 71, 72, 75 | OFFICIAL_JCI_FACT |
| **International Human Duties National Ambassadors** | « selected by JCI National Organizations to influence change and… coordinat[e] IHD activities at National Level » | — | IC | 72, 74 | OFFICIAL_JCI_FACT |
| **JCI Twinning** | « a voluntary partnership program between JCI National and Local Organizations across countries and regions » | « Twinning Agreements » ; « LOM-level Twinnings » ; sous-initiatives : **Buddy Project**, **Mastery Month**, **Training for Innovation** | IC | 78–82 | OFFICIAL_JCI_FACT |
| **Community Development Projects** | « members identify pressing local challenges and implement sustainable solutions… health, education, environment, gender equality, and poverty alleviation » | « grassroots community projects », « local impact projects » | CI | 2, 25, 84 | OFFICIAL_JCI_FACT |
| **JCI RISE** | « Rebuild, Invest, Sustain, Evolve » ; lancé en 2020 ; « addressing economic recovery, workforce empowerment, and mental health » | « RISE Projects », « RISE Ambassadors network » (p. 92) | CI | 85, 92 | OFFICIAL_JCI_FACT |
| Piliers RISE | Objectifs (p. 85) : « Sustain and Rebuild Economies », « Workforce Empowerment », « Mental Health Awareness » | Graphique « RISE Pillars Covered » : « Sustaining and Rebuilding Economies », « **Workforce Motivation** », « **Preserving Mental Health** » | **Deux jeux de libellés pour les mêmes piliers** | 85 | OFFICIAL_JCI_FACT (écart de libellés) |
| **JCI Foundation Development Grants** | Pour « growth and development, leadership development, development of National Secretariats, training and LO or NO extension » ; 2 cycles/an | Statuts : Application, In Process, Denied, Canceled, Pending Payment, Paid | Transversal (INPUT) | 97–98 | OFFICIAL_JCI_FACT |
| **JCI Awards Program** | « honor and showcase the impactful achievements of JCI members and organizations worldwide… across JCI's four Areas of Opportunity » | Voir A.9 | Transversal | 102–103 | OFFICIAL_JCI_FACT |
| **Mastering Sustainable Leadership** | Cours avec la SDG Academy, piloté dans les 4 Area Conferences | — | Non placé (SEMANTIC_INTERPRETATION : ID) | 124 | OFFICIAL_JCI_FACT |
| **Becoming Global Citizens for a Sustainable Society** | Cours co-développé avec le Ban Ki-moon Centre, livré au World Congress (Tunisie) | « Global Citizenship Leadership Course » | Non placé (SEMANTIC_INTERPRETATION : ID/IC) | 125 | OFFICIAL_JCI_FACT |
| **Global Youth Dialogue 2025** | « flagship event aligned with Global Goals Week… and the YouthLead Festival » ; ateliers organisés par Area of Opportunity | — | IC (SEMANTIC_INTERPRETATION) | 122–123 | OFFICIAL_JCI_FACT |
| **RISE to the Challenge** | Side event JCI au ECOSOC Youth Forum (16 avril 2025) | — | CI/IC (SEMANTIC_INTERPRETATION) | 117–118 | OFFICIAL_JCI_FACT |
| **JCI Action Framework** | Cité : « aligning with the JCI Action Framework and the Four Areas of Opportunity » | — | **NOT SPECIFIED IN THE SOURCE DOCUMENT** | 124 | UNKNOWN |
| Initiatives locales nommées | Mentor–Mentee Programme (p. 105), Impacathon (p. 107), Basics 4 Trainers (p. 107), Trainer Mentorship Program HK (p. 106), ASPAC Academy for Local Chapter Presidents (p. 106), « Sun Never Sets on JCI » global marathon (p. 77), Alpha Project (p. 77), Community Asset-Based Mapping Project (p. 79, vi) | — | Variable | — | OFFICIAL_JCI_FACT |

## A.4 Personnes et rôles

| Terme | Définition (document) | Variantes | Distinction | Pages | Statut |
|---|---|---|---|---|---|
| **Member** | Jeune de 18 à 40 ans ; « young active citizens », « young leaders » | « Jaycee » | ≠ volunteer (voir ci-dessous) | 2, 16 | OFFICIAL_JCI_FACT |
| **Volunteer** | **NOT SPECIFIED IN THE SOURCE DOCUMENT** | « volunteers engaged », « volunteer trainers » (p. 91) | **Le document ne dit pas si les bénévoles sont tous membres.** 42 401 bénévoles < 147 670 membres, ce qui laisse penser qu'il s'agit surtout de membres, sans preuve | 84, 86, 91 | UNKNOWN |
| **Beneficiary** | **NOT SPECIFIED IN THE SOURCE DOCUMENT** (ni direct/indirect, ni règle de comptage, ni dédoublonnage) | « people reached », « beneficiaries reached » | ≠ participant ≠ audience | v, 84, 86 | UNKNOWN (méthode) |
| **Participant / Attendee / Registrant / Registration** | Non définis ; utilisés en parallèle | « live participants », « live attendees », « Facebook Live viewers », « First Timers » | Registrations 10 729 ≠ « nearly 10,000 participants » (p. 59) ≠ « 10,000+ attendees » (p. v) | 59, 117, 122 | OFFICIAL_JCI_FACT (usage) |
| **First Timer** | Nouveau participant à une Area Conference / World Congress | « First Timers Award (raffle for new participants) » | — | 60, 103 | OFFICIAL_JCI_FACT |
| **Applicant / Enrolled / Graduate / Trained** | Entonnoir : « 200+ interested applicants, 120 participants enrolled, and 60 graduates » | — | Entonnoir explicite, rare dans le rapport | 92 | OFFICIAL_JCI_FACT |
| **Certified Trainer** | Voir CNT/CAT (A.3) | « Training Mentor », « Global Trainer » | — | 41 | OFFICIAL_JCI_FACT |
| **Winner / Honoree / Awardee** | Winner (CYE, Public Speaking, Debating, Best RISE Project) ; Honoree (TOYP) | « Most Outstanding Member » | — | 29–107 | OFFICIAL_JCI_FACT |
| **Team Captain** | Débat | — | — | 49, 51 | OFFICIAL_JCI_FACT |
| **Local President / National President / Local Board / National Board / International officers / Directors** | Fonctions électives | « local leaders », « chapter presidents » | — | 3, 172 | OFFICIAL_JCI_FACT |
| **JCI Ambassador** | Rôle confié à un partenaire (WBAF, Baybars Altuntas) | ≠ IHD National Ambassador ≠ RISE Ambassador | 3 usages distincts du mot « Ambassador » | 92, 128 | OFFICIAL_JCI_FACT |

## A.5 Partenaires et sponsors

| Terme | Définition / exemple (document) | Type de contribution | Pages | Statut |
|---|---|---|---|---|
| **Global Partner** | BNI Japan (« new Global Partner »), WBAF (« global partner ») | Financier + juges + formation | 119 | OFFICIAL_JCI_FACT |
| **Club100 member** (Platinum / Bronze) | Tecso ChargeZone (Platinum), Techno Drugs (Platinum), Apextra (Bronze), Tsuchiyoshi Acty, SPA Industries, Sheltech, Equipo.ph ; 1 individu (Senator S. R. Ndoro) | Financier + présence événements | 110–112, 119 | OFFICIAL_JCI_FACT (niveau connu seulement pour 3) |
| **Corporate Sponsors** | BNI Japan : USD 90 000 sur 3 ans | Financier | 113 | OFFICIAL_JCI_FACT |
| **Programs' Sponsors and Supporters** | NMT Group (prize money CYE), WBAF/BNI Japan (juges CYE), Zoho, Ban Ki-moon Centre, Quantic, BNI Japan (juges TOYP), PMU Global Chains | Prize money, juges | 114, 119 | OFFICIAL_JCI_FACT |
| **Strategic partnership** | AIESEC (renouvelé 5 ans), ICC (renouvelé) | Institutionnel | 120–121 | OFFICIAL_JCI_FACT |
| **Member-Centric Partnerships** | SIXT (Mobility Partner), Quantic (Education Partner), ICC (Global Business Network Partner), Trip.com (Travel Partner), Zoho (Technology Partner) | Avantages membres | 126–127 | OFFICIAL_JCI_FACT |
| Institutions ONU / multilatérales | ECOSOC, UN OHCHR, SDG Academy (SDSN), SDSN Youth, UN Youth Office, UN Foundation, UN Global Compact Network USA | Plateformes, contenus | 2, 115–125 | OFFICIAL_JCI_FACT |
| Soutiens / endorsements | Nelson Mandela Foundation (endorsement IHD), H.E. Ban Ki-moon (message vidéo) | Reconnaissance | 71–72 | OFFICIAL_JCI_FACT |
| Partenaires locaux de projets | Lions (gala), Sheraton Salta, Arca Continental, Proyecto Norte, Coca-Cola, OSDE, Council of Economic Sciences, RSM US | Co-exécution, financement | 71, 94, 107 | OFFICIAL_JCI_FACT |

> Typologie des contributions partenaires observée : **financière** · **juges/expertise** · **formation/intervention** · **avantages membres** · **co-développement de contenu** · **endorsement**. — SEMANTIC_INTERPRETATION (H), construite à partir des pages 110–128.

## A.6 Termes de mesure utilisés par le rapport (le cœur du calibrage)

| Libellé exact | Où | Ce qu'il mesure réellement | Proche de… mais ≠ | Statut |
|---|---|---|---|---|
| « beneficiaries reached » / « Total Beneficiaries Reached » / « Total Number of Beneficiaries » | p. v, 84, 86 | Personnes atteintes. **Méthode non spécifiée** | ≠ participants, ≠ people reached (outreach) | OFFICIAL_JCI_FACT (libellé) / UNKNOWN (méthode) |
| « people reached through education and outreach » | p. 31 | Audience d'actions de sensibilisation | ≠ beneficiaries | OFFICIAL_JCI_FACT |
| « Rural Students Reached » | p. 29 | Bénéficiaires d'une initiative d'entreprise | — | OFFICIAL_JCI_FACT |
| « projects implemented (2024–2025) » / « Total Projects Executed (2024-25) » / « Total Projects Reported for 2025 » / « over 10,000 projects » | p. v, 84, 85, vii | Nombre de projets. **3 périmètres temporels et 2 ordres de grandeur** | implemented ≠ executed ≠ reported | OFFICIAL_JCI_FACT |
| « volunteers engaged » / « Total Number of Volunteers Engaged » | p. v, 84, 86, 87–90 | Ressource humaine (INPUT) | ≠ members | OFFICIAL_JCI_FACT |
| « hours of service » / « Total Hours Contributed by Volunteers » / « volunteer hours » | p. v, 86, 87–90 | Temps bénévole (INPUT) | — | OFFICIAL_JCI_FACT |
| « Measurable outcomes included… » | p. 87–90 | **Utilisé pour des inputs** (heures, bénévoles) | ≠ outcome au sens IOOI | OFFICIAL_JCI_FACT |
| « measurable results » / « measurable impact » / « measurable outcomes » | p. 31, 55, 56, 75, 81, 91, 132 | En-tête générique avant une liste de chiffres mélangés | — | OFFICIAL_JCI_FACT |
| « Impact through the Program » / « Impact through this Program » / « Impact » / « Impact at a Glance » | chaque section programme | Texte narratif ; souvent des activités ou des outputs | — | OFFICIAL_JCI_FACT |
| « Quantitative Data (2025) » | p. 9, 20, 73 | Bloc chiffré | — | OFFICIAL_JCI_FACT |
| « Primary SDGs Addressed » / « Secondary SDG » | p. 84 | Hiérarchie ODD principal / secondaire (valeurs illisibles) | — | OFFICIAL_JCI_FACT (libellés) / UNKNOWN (valeurs) |
| « SDG Alignment » | p. 24–26 | Mappage déclaratif AoO/programme → ODD | — | OFFICIAL_JCI_FACT |
| « RISE Pillars Covered » | p. 85 | % de projets RISE par pilier | — | OFFICIAL_JCI_FACT |
| « Projects Reported per Area » / « per Area of Opportunity » | p. 86 | Distribution en % | — | OFFICIAL_JCI_FACT |
| « participants », « attendees », « registrations », « registrants », « live participants », « live attendees », « Facebook Live viewers », « First Timers » | p. 42, 59–60, 117, 122 | Présence à des événements | Voir B.6 | OFFICIAL_JCI_FACT |
| « Total Readers to Date », « Total Book Visits to Date », « Average Time on Books » | p. 20 | Audience magazine | readers ≠ visits | OFFICIAL_JCI_FACT |
| « Followers », « Subscribers », « Reach », « Impressions », « Engagement Rate », « Reactions », « Views », « Watch Time » | p. 17–18 | Audience réseaux sociaux | **reach ≠ impressions** (voir B.6) | OFFICIAL_JCI_FACT |
| « Active Users », « Page Views », « Event Count », « Average Session Duration », « unique visitors », « sessions » | p. 22, 129 | Audience web | — | OFFICIAL_JCI_FACT |
| « Contributions Received (USD) », « Donations », « Donors Recognized », « Grants » | p. 96–98 | Ressources financières | — | OFFICIAL_JCI_FACT |
| « Award Entries Submitted » | p. 103 | Candidatures aux prix | — | OFFICIAL_JCI_FACT |
| « Twinning Agreements registered » | p. 78 | Accords signés | — | OFFICIAL_JCI_FACT |
| « Petitions Signed via change.org », « Reported Activities » | p. 73 | Plaidoyer | signatures ≠ personnes uniques (non précisé) | OFFICIAL_JCI_FACT |
| « feedback forms » ; « over 90% indicating increased awareness and motivation » | p. 75 | **Seul outcome mesuré par un instrument** dans tout le rapport | — | OFFICIAL_JCI_FACT |

## A.7 Groupes cibles et démographie (termes trouvés — pas de taxonomie officielle)

| Terme trouvé | Pages | Interne (membres) / Externe |
|---|---|---|
| young people, youth, young leaders | partout | Mixte |
| JCI members, local chapter presidents, first timers | 40–52, 82, 106 | Interne |
| young entrepreneurs, aspiring entrepreneurs, entrepreneurs and small business owners, SMEs, businesses | 33–38, 79–80, 85, 88, 91–93 | Externe (et membres) |
| women entrepreneurs, young women | 37, 91 | Externe |
| rural students, students, high school students, advanced students, teenagers | 29, 44–45, 94 | Externe |
| children and youth (vulnerable communities), underserved children | 56, 77 | Externe |
| families in need | 71 | Externe |
| vulnerable groups, marginalized voices, underserved communities / regions | 80, 85, 116, 117 | Externe |
| patients and medical professionals, medical field participants | 58, 87 | Externe |
| professionals | 36 | Externe |
| community leaders, educators, families (audience) | 45 | Externe |
| refugees (thème d'un discours) | 47 | Thème, pas cible |

**Attributs démographiques effectivement présents** : **âge** (tranches membres 18–40, Junior 14–21, Alumni >40 ; âge moyen 32 / 29 / 36 [p. 3] ; « a 19-year-old » [p. 74, 91]) ; **genre** (56,7 % H / 43 % F [p. 3] ; « more than half of participants being young women » [p. 91] ; Senators 67 % / 37 % [p. 100]). **Aucun autre attribut** (handicap, revenu, zone rurale/urbaine en tant que champ, statut migratoire) n'est mesuré. — CONSTAT D'ABSENCE (couche texte vérifiée).

## A.8 Les 7 Duties for Leaders (IHD) — ce que le document permet de reconstituer

| N° | Libellé | Source | Statut |
|---|---|---|---|
| 2 | « Serve Humanity » | p. 74, 75, 77 | OFFICIAL_JCI_FACT |
| 5 | « Respect for Human Personality » | p. 75 (« Table 5 ») | SEMANTIC_INTERPRETATION (M) : numéro de table = numéro de principe |
| 6 | « Educate Yourself and Teach Others » | p. 75 | OFFICIAL_JCI_FACT |
| 7 | « leading responsibly » (paraphrase) | p. 74 | OFFICIAL_JCI_FACT (libellé exact UNKNOWN) |
| 1, 3, 4 | — | — | **NOT SPECIFIED IN THE SOURCE DOCUMENT** |

## A.9 Catégories de prix (JCI Awards) — utiles comme mapping de référence

| Famille | Catégories (libellés exacts) | AoO correspondante (SEMANTIC_INTERPRETATION à partir du libellé) |
|---|---|---|
| Multi-Entry Awards | Best JCI RISE Project | CI |
| | Best Local Business & Entrepreneurship Program | B&E |
| | Best Local Individual Development Program | ID |
| | Best Local Growth & Development Program | — (croissance organisationnelle, hors AoO) |
| | Best International Cooperation Project | IC |
| | Best Inter-Organization Collaboration Project | IC (M) |
| | Best Local Community Impact Program | CI |
| | Best Local Global Goals Project | CI (M) ; transversal ODD |
| | Best International Human Duties Project (new category) | IC |
| Best of the Best (Area → World Congress) | Best National Flagship Program ; Most Outstanding New Local Organization ; Most Outstanding Local Organization | — |
| Individuels | Most Outstanding Member ; Most Outstanding New Member ; Most Outstanding Local President ; Most Outstanding National President (World Congress only) | — |
| Special Consideration | Most Outstanding Local Project (top-scoring entry across categories) ; First Timers Award ; Joaquín V. González Memorial | — |

Source : [p. 102–103 — JCI Awards]. Le libellé « top-scoring entry » montre qu'une **grille de notation** existe. Son contenu : NOT SPECIFIED IN THE SOURCE DOCUMENT.

## A.10 Distinctions critiques (règles de désambiguïsation pour un LLM)

| Paire confondable | Règle observée dans le document | Statut |
|---|---|---|
| `geographic_area` vs `area_of_opportunity` (voir §G, règles AREA-1…6) | Géo = {Africa & the Middle East, America, Asia & the Pacific, Europe} ; Thème = {B&E, ID, IC, CI}. Le contexte « per Area » sur p. 8–13, 34, 73, 86 = géo ; « per Area of Opportunity » p. 86 = thème | OFFICIAL_JCI_FACT |
| Program vs Project vs Initiative | Aucune définition. Usage : « Program »/« Initiative » = cadre porté par JCI mondial (CYE, RISE, JIB « flagship initiative ») ; « Project » = exécution locale (« RISE Projects », « Local Project »). Mais les prix disent « Local … Program » | SEMANTIC_INTERPRETATION (M) |
| Participants vs Beneficiaries vs Reached | Jamais équivalents dans le texte ; aucune règle de conversion | OFFICIAL_JCI_FACT |
| Volunteers vs Members | Non spécifié | UNKNOWN |
| Registrations vs Attendees | 10 729 « Registrations » (p. 59), mais les mêmes nombres sont appelés « Attendees » p. 60–70 (ex. 5 012) | OFFICIAL_JCI_FACT (usage interchangeable) |
| Output vs Outcome | Le rapport appelle « outcomes » des inputs (S2) | OFFICIAL_JCI_FACT |
| Target (plan) vs Result | « plans to impact 6,000 more in 2025 » (p. 29) = cible, pas un résultat | OFFICIAL_JCI_FACT |

---

# B. COUCHE DE NORMALISATION ANALYTIQUE INPUT → ACTIVITY → OUTPUT → OUTCOME → IMPACT (« IAOOI-v0 »)

> ⚠ **PROPOSED_STANDARD — ce n'est pas un cadre JCI.** Le rapport JCI 2025 ne contient ni ce cadre ni ces cinq termes définis (constat S1). IAOOI-v0 est une **couche de normalisation analytique proposée par votre solution**. Chaque classement d'une métrique JCI dans cette grille est une **SEMANTIC_INTERPRETATION**. Les valeurs et libellés, eux, sont des **OFFICIAL_JCI_FACT**.

## B.1 Règles de classification appliquées

- **Colonnes « Libellé exact » et « Valeur » = OFFICIAL_JCI_FACT** (`extracted`, cités tels quels). **Colonne « Classe » = SEMANTIC_INTERPRETATION** selon le standard PROPOSED_STANDARD IAOOI-v0. La colonne « Conf. » donne la confiance dans ce classement.
- Toute somme, tout ratio ou tout écart mentionné dans « Remarque » est une **SEMANTIC_INTERPRETATION `calculated`**, jamais un chiffre JCI.
- Les mentions « per Area » désignent la **`geographic_area`** (règle AREA-5, §G) ; « per Area of Opportunity » désigne l'**`area_of_opportunity`**.
- **INPUT** : ressources (argent, temps, personnes, partenaires). **ACTIVITY** : ce qui est fait (nombre de sessions, projets, événements). **OUTPUT** : produit immédiat (personnes participantes, formées, atteintes ; objets produits). **OUTCOME** : changement chez les bénéficiaires (emploi, entreprise, compétence **mesurée**, comportement, politique). **IMPACT** : effet durable **attribuable**.
- **CONTEXT** : métrique qui décrit le réseau JCI lui-même (membres, clubs, sondage) et pas une chaîne de résultats. Conformément à la consigne, c'est une forme de **CLASSIFICATION UNCERTAIN** : on ne la force pas dans la chaîne.
- **UNCERTAIN** : on ne peut pas trancher avec le document. L'explication est donnée.
- **IMPACT-CLAIM** : affirmation d'effet durable, **non mesurée ou non attribuée**. Elle n'est jamais classée IMPACT.
- Les métriques de **communication** (followers, reach…) sont classées OUTPUT, avec le sous-type « comm. ». Ce ne sont pas des bénéficiaires.

## B.2 Classification exhaustive des métriques (132 lignes)

### B.2.1 Agrégats globaux (Executive Summary, Community Impact)

| ID | Libellé exact (abrégé) | Valeur | Page — Section | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M001 | projects implemented (2024–2025) | 1,000+ | v — Exec. Summary | ACTIVITY | H | Période 2024–25 |
| M002 | Total Projects Executed (2024-25) | 1,000+ | 84 — Community Dev. Projects | ACTIVITY | H | = M001 ? non démontré |
| M003 | Total Projects Reported for 2025 | 1000+ | 85, 86 — RISE / per Area | ACTIVITY | H | Période 2025 seule |
| M004 | projects across more than 4,500 LOs | over 10,000 | vii — Message SG | ACTIVITY | M | **×10 vs M001–M003**, période non précisée |
| M005 | beneficiaries reached worldwide | 21 million+ | v — Exec. Summary | OUTPUT | M | Méthode de comptage : `unknown` |
| M006 | Total Beneficiaries Reached | 21,000,000+ | 84 | OUTPUT | M | idem |
| M007 | Total Number of Beneficiaries | 21,148,414 | 86 | OUTPUT | M | Valeur précise de M005/M006 (SEMANTIC_INTERPRETATION) |
| M008 | volunteers engaged | 40,000+ | v, 84 | INPUT | H | |
| M009 | Total Number of Volunteers Engaged | 42,401 | 86 | INPUT | H | |
| M010 | hours of service | 435,000+ | v | INPUT | H | |
| M011 | Total Hours Contributed by Volunteers | 435,605 | 86 | INPUT | H | |
| M012 | Local Organizations mobilized | 4,500+ | v | INPUT | M | Capacité organisationnelle ; ≠ 4 641 (M031) |
| M013 | Projects addressing all 17 SDGs | 17 | v | UNCERTAIN | — | Métrique de couverture de tags, pas un résultat |
| M014 | Primary SDGs Addressed / Secondary SDG | `null` — visual_data_not_extracted | 84 | UNCERTAIN | — | **VDX-04** |
| M015 | RISE Projects / Other Projects | 53.47 % / 46.53 % | 85 | ACTIVITY | H | Distribution |
| M016 | RISE Pillars Covered | Sustaining & Rebuilding Economies 40.30 % ; Preserving Mental Health 28.04 % ; Workforce Motivation 31.67 % | 85 | ACTIVITY | H | Somme 100,01 % (arrondi) |
| M017 | 2025 Projects Reported per Area | ASPAC 67.04 % ; America 9.15 % ; AfME 21.91 % ; Europe 1.91 % | 86 | ACTIVITY | H | Somme 100,01 % |
| M018 | 2025 Projects Reported per Area of Opportunity | CI 44.64 % ; B&E 18.49 % ; ID 27.21 % ; IC 9.66 % | 86 | ACTIVITY | H | Somme 100 % **malgré** « Some projects may fall under 2 or more » → base = tags, pas projets (SEMANTIC_INTERPRETATION M) |
| M019 | Initiatives implemented collaboratively across … National Organizations | 114 | v | UNCERTAIN | — | Nombre total de NO, pas un résultat de collaboration |
| M020 | Millions of dollars mobilized in resources | non chiffré | v | INPUT | M | Pas de valeur |
| M021 | attendees participating in international events | 10,000+ | v | OUTPUT | H | cf. M067 |
| M022 | participants trained through global and regional conferences | 1,969 | v, 42 | OUTPUT | H | Répartition par conférence : **VDX-02** (visual_data_not_extracted) |
| M023 | leadership training sessions | 33 | v, 42 | ACTIVITY | H | |
| M024 | skills development sessions | 48 | v, 42 | ACTIVITY | M | Texte extrait fragmenté p. 42 ; confirmé p. v |
| M025 | members trained through sustainable leadership and global citizenship courses | « Hundreds » | v | OUTPUT | M | Non chiffré ; cf. M109 |
| M026 | members engaged in cross-border exchanges | « Thousands » | v | OUTPUT | L | Non chiffré |

### B.2.2 Structure du réseau et profil des membres (CONTEXT)

| ID | Libellé exact | Valeur | Page — Section | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M027 | members | 147,670 (p. 8) / « over 147,000 » (p. 2) / « over 100,000 » (p. v, vi) | 2, 8, v | CONTEXT | — | **DQC-01** (UNRESOLVED) |
| M028 | Total Members per Area | AfME 15,102 (10.2 %) ; ASPAC 103,170 (69.9 %) ; America 11,775 (8.0 %) ; Europe 17,623 (11.9 %) | 8, 9 | CONTEXT | — | Graphique p. 8 : America « (80%) » = coquille |
| M029 | Local Organizations per Area | AfME 468 ; ASPAC 2,945 ; America 492 ; Europe 736 ; total 4,641 | 8, 11 | CONTEXT | — | Europe 15.8 % (p. 8) vs 15.9 % (p. 11) |
| M030 | National Organizations per Area | AfME 33 ; ASPAC 22 ; America 22 ; Europe 37 ; total 114 | 10 | CONTEXT | — | |
| M031 | Countries | « more than 114 » (p. 2) / « 114 Countries » (p. 9) / « more than 100 » (p. v, 24) | 2, 9, v | CONTEXT | — | **DQC-02** ; NO ≠ pays (A.1) ; liste des pays : VDX-01 |
| M032 | JCI Alumni Clubs | 366 clubs (ASPAC 175, America 4, AfME 6, Europe 181) ; 1,343 members ; 18 countries | 12 | CONTEXT | — | |
| M033 | JCI Junior Clubs | 89 clubs (ASPAC 60, America 14, AfME 12, Europe 3) ; 527 members ; 21 countries | 13 | CONTEXT | — | |
| M034 | Membership Experience Survey | 3,767 respondents ; average age 32 (AfME 29, Europe 36) ; >900 members >7 years ; 56.7 % male / 43 % female ; full-time 1,636 ; entrepreneurs/self-employed 1,166 ; undergrad >1,450 ; master's ~950 ; enrolled master's 383 ; doctoral 90 ; technical/vocational 160 | 3 | CONTEXT | — | Échantillon, pas la population |
| M035 | JCI Senators | 84,375 | v, 100 | CONTEXT | — | Stock de distinctions |
| M036 | Senators — age / gender | « 669 Senators so far have ranged from 28 to 67 with the average age being 33-40 » ; 67 % male / 37 % female | 100 | CONTEXT | — | **DQC-10** : somme calculée 104 % ; « 669 » sans sens clair |

### B.2.3 Visibilité et audience numérique (janvier–octobre 2025)

| ID | Libellé exact | Valeur | Page | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M037 | followers across JCI's digital platforms | 260,000+ | v | OUTPUT (comm.) | H | **DQC-07** : somme calculée des plateformes p. 17–18 = 229 200 (SEMANTIC_INTERPRETATION) |
| M038 | impressions | 2 million+ | v | OUTPUT (comm.) | M | Semble provenir de la « Reach » Facebook (≠ impressions) |
| M039 | Facebook | Followers 148,000 ; Growth +6 % (quarterly) ; Reach >2 million (76 % organic) ; Engagement Rate 5 % ; engagement +70 % vs previous quarter | 17 | OUTPUT (comm.) | H | |
| M040 | Instagram | Followers 41,000 ; +9 % ; Reach +13.9 % ; ER 2 % | 17 | OUTPUT (comm.) | H | |
| M041 | LinkedIn | Followers 32,000 ; +7 % ; Impressions 318,604 ; Reactions 9,124 | 17 | OUTPUT (comm.) | H | |
| M042 | YouTube | Subscribers 8,200 ; +12 % ; Views 17,325 ; Watch Time 330 h ; top video 2,700 views, 51 % retention | 18 | OUTPUT (comm.) | H | |
| M043 | mobile access | >75 % | 18 | CONTEXT | — | |
| M044 | The LEADER — issues | 7 issues (Jan–Oct 2025) | 19 | ACTIVITY | H | |
| M045 | The LEADER — readers | 13,872 total readers ; 15,423 book visits ; avg 0:48:56 ; « nearly 13,000 » (p. 19) ; « 13,800 readers across 70+ countries » (p. v) | 19, 20, v | OUTPUT (comm.) | H | **DQC-09** ; détail par numéro p. 20 ; « 70+ countries » absent du corps |
| M046 | The LEADER — devices | Mobile 8,857 ; Tablet 81 ; Computer 3,626 | 19 | CONTEXT | — | Somme 12 564 ≠ 13 872 |
| M047 | jci.cc — active users since Oct 6, 2025 relaunch | >8,700 from >50 countries | 21 | OUTPUT (comm.) | H | |
| M048 | jci.cc — analytics | Total Active Users 13,351 ; Page Views 29,535 ; Event Count 88,350 ; Avg Session 2m 37s ; devices 6,017 / 79 / 7,255 ; direct+organic ≈90 % | 22, 21 | OUTPUT (comm.) | H | 13 351 vs 8 700 : périodes différentes probables |

### B.2.4 Business & Entrepreneurship

| ID | Libellé exact | Valeur | Page | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M049 | CYE Total Global Participation | 108 entrepreneurs across five international stages | 28 | OUTPUT | H | |
| M050 | CYE participation per conference | 25 / 12 / 24 / 9 / 38 | 28 | OUTPUT | M | **VDA-01** : association aux conférences = SEMANTIC_INTERPRETATION (ordre du texte), confiance L. Seul le total 108 est OFFICIAL_JCI_FACT |
| M051 | Zartech — Solar Capacity Installed | 100kW | 29 | UNCERTAIN | — | Output de l'entreprise du lauréat ; contribution CYE revendiquée (prix, mentorat) mais non quantifiée |
| M052 | Chigubhu Lantern — Rural Students Reached | 2,000 ; cible 6,000 en 2025 | 29 | OUTPUT | M | 6 000 = **cible**, pas un résultat |
| M053 | Integra — new SKUs / quality / time-to-market | 30+ SKUs en 1 an ; 97 % first-order quality rate ; −30 % time-to-market | 30 | UNCERTAIN | — | Résultats d'entreprise ; attribution CYE non établie |
| M054 | Integra — CO2 emissions reduced annually (partners) | 250 tons | 30 | IMPACT-CLAIM | — | Aucune méthode, périmètre « partners » |
| M055 | JAPJAP — food waste processed | 100+ tonnes | 31 | UNCERTAIN | — | Output de l'entreprise |
| M056 | JAPJAP — people reached through education and outreach | 50,000+ | 31 | OUTPUT | M | |
| M057 | JIB Total Global Participation | 345 (ASPAC 159, America 29, AfME 75, Europe 82) | 33–34 | OUTPUT | H | |
| M058 | Karolin Linden — entrepreneurs trained and supported | 30+ | 35 | OUTPUT | H | |
| M059 | Karolin Linden — revenue growth | « up to 20% » for « some » | 35 | OUTCOME | L | Auto-déclaré, n non précisé |
| M060 | Debora Veneziano Paes — professionals impacted | 120+ in <1 year | 36 | OUTPUT | H | « impacting » = atteints |
| M061 | Ashley Pe Yeh Teng — aspiring entrepreneurs trained | 30+ | 37 | OUTPUT | H | |
| M062 | Ashley — local businesses collaborated | 5 | 37 | OUTPUT | M | Partenariats (peut aussi être un INPUT) |
| M063 | Ashley — part-time jobs for youth | non chiffré | 37 | OUTCOME | L | |
| M064 | Youssef Ouattara — company created (2018) | 1 | 38 | OUTCOME | L | « we haven't yet achieved measurable business outcomes » : aveu explicite, rare |

### B.2.5 Individual Development

| ID | Libellé exact | Valeur | Page | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M065 | Total Certified Trainers at Events | 97 (ASPAC 44, America 16, AfME 21, Europe 16) | 41 | UNCERTAIN | — | Titre du graphique : « Training Certification **Participation** ». Certifiés vs participants à la certification : ambigu. Si certification obtenue → OUTCOME (compétence) ; si participation → OUTPUT |
| M066 | Public Speaking participation | 52 (ASPAC 14, America 14, AfME 14, Europe 10) | 43 | OUTPUT | H | |
| M067 | Debating participation (teams) | 57 équipes (EN 37, FR 10, ES 10) ; par événement : WC 11, America 13, AfME 13, Europe 9, ASPAC 11 | 48 | OUTPUT | H | **Unité = équipes**, pas personnes |
| M068 | Ángel Cedeño — audience | 200 community leaders, educators, and families | 45 | OUTPUT | H | |
| M069 | Ángel — Academy created, provincial expansion, scholarship | 1 academy ; 1 scholarship | 45 | OUTCOME | M | Changement institutionnel local |
| M070 | Lincoln, Sanjay, Anela, Bryan, Samiha, Anni — confidence, skills, career | qualitatif | 44–52 | OUTCOME | L | Auto-déclaré, sans mesure |
| M071 | Anela Denić — national headlines, recognition | qualitatif | 47 | OUTPUT (comm.) | M | |

### B.2.6 International Cooperation

| ID | Libellé exact | Valeur | Page | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M072 | Total TOYP Applicants for 2024 | 164 | 54 | OUTPUT | H | |
| M073 | Total Global Honorees / Countries Represented | 10 / 8 | 54 | OUTPUT | H | |
| M074 | Kawas — entrepreneurs trained across MENA | 400+ | 55 | OUTPUT | H | Hors cadre JCI (activité de l'honoree) |
| M075 | Kawas — jobs created | non chiffré | 55 | OUTCOME | L | |
| M076 | Ramírez — conferences delivered | 1,000+ | 56 | ACTIVITY | H | |
| M077 | Ramírez — children taken to NASA missions | 700+ | 56 | OUTPUT | H | |
| M078 | Apaydın — individuals educated on spinal and brain trauma care | 5,000+ | 58 | OUTPUT | H | |
| M079 | Apaydın — influencing national practice guidelines in Turkey | qualitatif | 58 | IMPACT-CLAIM | — | Non documenté |
| M080 | Total Registrations Across All Conferences | 10,729 (ASPAC 5,012 ; America 364 ; AfME 429 ; Europe 1,068 ; WC 2024 3,856) | 59 | OUTPUT | H | Aussi appelés « Attendees » p. 61–70 |
| M081 | participants across global and Area events | « nearly 10,000 » | 59 | OUTPUT | M | ≠ 10 729 |
| M082 | First Timers | ASPAC 162/5,012 ; America 82/364 ; AfME 116/429 ; Europe 168/1,068 | 60 | OUTPUT | H | **VDA-02** : association par dénominateur (SEMANTIC_INTERPRETATION, H) |
| M083 | National Organization Attendances per Area Conference | `null` — visual_data_not_extracted | 60 | OUTPUT | — | **VDX-03** |
| M084 | IHD Petitions Signed via change.org | 67,101 (ASPAC 54,921 / 35 countries ; America 3,656 / 45 ; AfME 6,867 / 63 ; Europe 1,657 / 48) | 73 | OUTPUT | H | **DQC-23** : somme calculée des pays = 191, non dédoublonnée ; comptage suspect |
| M085 | IHD Reported Activities per Area | 42 (ASPAC 10, America 6, AfME 19, Europe 7) | 73 | ACTIVITY | H | |
| M086 | IHD National Ambassadors | 78 | 72 | INPUT | M | Ressource humaine |
| M087 | IHD New York celebration | 100 participants / 4 days ; >50 walk ; 100 food care packages | 71 | OUTPUT | H | |
| M088 | Zulia (Venezuela) — Law on Human Duties enacted ; July 10 declared | 1 loi | 72 | OUTCOME | M | Changement de politique ; « inspired by » = contribution |
| M089 | Official proclamations gathered | non chiffré | 72 | OUTPUT | M | |
| M090 | JCI Ankara « 7x7 » | 49 participants (l. 1) / « 45 participants » (l. 2) ; 7 policy-oriented outcome summaries ; 1 joint declaration | 75 | OUTPUT | H | **DQC-11** : 49 vs 45 (UNRESOLVED) |
| M091 | JCI Ankara — feedback | 100 % feedback forms completed ; >90 % increased awareness and motivation | 75 | OUTCOME | H | **Seul outcome mesuré par instrument** |
| M092 | Suriname/Jamaica panel | ~40 participants | 76 | OUTPUT | H | « increased awareness » non mesuré |
| M093 | JCI Mongolia IHDD | 7 keynote speakers (ACTIVITY) ; 200+ in person ; 3,000 livestream ; 100+ signatures | 77 | OUTPUT | H | |
| M094 | JCI Mongolia — sponsorships | 8 million MNT | 77 | INPUT | H | Devise locale |
| M095 | JCI Mongolia — follow-up workshops requested | non chiffré | 77 | OUTCOME | L | « positive behavioral shift » affirmé |
| M096 | Twinning Agreements registered during Conferences | 113 (ASPAC 14, AfME 37, Europe 8, WC 26, America 28) | 78 | OUTPUT | H | |
| M097 | Madagascar Twinning | 100+ young people trained ; 3 workshops ; 2 international projects | 79 | OUTPUT / ACTIVITY | H | |
| M098 | Madagascar Twinning — jobs / businesses | 10 new jobs ; « dozens » started businesses | 79 | OUTCOME | M | |
| M099 | Community Asset-Based Mapping | 60 young entrepreneurs mentored and trained | 79 | OUTPUT | H | Peut recouper M097 (non précisé) |
| M100 | Colombia Twinning | 85 young people trained ; 6 international facilitators (INPUT) ; 4 follow-up initiatives (OUTCOME) | 80 | OUTPUT | H | Ligne mixte |
| M101 | Vietnam–Mongolia Twinning | 1 agreement ; regular meeting schedule | 81 | OUTPUT | H | |
| M102 | Switzerland–Canada Buddy Project | ~30 members across 12 LOs | 82 | OUTPUT | H | Bénéficiaires = membres |

### B.2.7 Community Impact — récits de projets

| ID | Libellé exact | Valeur | Page | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M103 | MED'PRENEUR (JCI Mahajanga) — « Measurable outcomes » | 244 volunteer hours ; 15 volunteers ; 3–5 Sept 2025 | 87 | INPUT | H | **Mal étiqueté « outcomes »** ; aucun bénéficiaire chiffré |
| M104 | EMPRENDHER 2.0 (JCI Hernandarias) | 100 volunteer hours ; 25 volunteers | 88 | INPUT | H | idem |
| M105 | SDGs Hunt: Save The World! (JCI Malaysia) | 4 volunteer hours ; 5 volunteers | 89 | INPUT | H | 17 ODD déclarés |
| M106 | JCI Finland inaugural Sustainability Agenda | 418 volunteer hours ; 17 volunteers | 90 | INPUT | H | |
| M107 | Bridges Project (JCI Syria) | 35 participants, 3 weeks, 20 volunteer trainers (INPUT) ; 200+ youth trained | 91 | OUTPUT | H | **DQC-12** : 35 vs 200+ (UNRESOLVED) |
| M108 | Bridges Project — results | 75 % placed in jobs or internships ; 15 % launching startups ; >50 % young women | 91 | OUTCOME | M | Base du % inconnue |
| M109 | Escuela de Emprendedores de América (JCI Bolivia) | 200+ applicants ; 120 enrolled ; 60 graduates | 92 | OUTPUT | H | Entonnoir complet |
| M110 | INNO Leaders (JCI Hong Kong) | 20+ pitching opportunities (OUTPUT) ; 100 jobs generated (OUTCOME) ; 40+ organizations from 6 sectors (INPUT) ; 100+ international friendships | 93 | OUTCOME | M | Ligne mixte ; « friendships » non classable |
| M111 | Impulso NOA (JCI Argentina) | 22 students connected (OUTPUT) ; 4 new members = « 20% of all participants » (OUTCOME org.) ; AR$144,000 (107 USD) surplus (INPUT) ; recognition by Chamber of Deputies of Salta | 94 | OUTPUT | H | **DQC-13** : 4/22 = 18,2 % calculé ≠ 20 % publié |

### B.2.8 Foundation, Awards, Partenariats

| ID | Libellé exact | Valeur | Page | Classe IAOOI-v0 (SEMANTIC_INTERPRETATION) | Conf. | Remarque |
|---|---|---|---|---|---|---|
| M112 | Total Contributions Received (USD) since 2022 | 10,347,883.70 | 96 | INPUT | H | |
| M113 | Total Contributions Received (USD) Oct 2024–Aug 2025 | 223,124.22 | 96 | INPUT | H | Période non calendaire |
| M114 | Total Donors Recognized / Donations since 2022 | 196 / 5,243 | 96 | INPUT | H | |
| M115 | Development Grants — amounts & projects per year per Area (2023–2025) | `null` — visual_data_not_extracted | 97–98 | INPUT | — | **VDX-05, VDX-06** ; fragments de texte non associés, inutilisables |
| M116 | Award Entries Submitted per Area | 1,120 (ASPAC 397, AfME 339, Europe 149, America 235) | 103 | OUTPUT | H | |
| M117 | Huzaifa Udhin — Public Speaking Club | 4 → 40 active members | 104 | OUTCOME | M | Croissance organisationnelle |
| M118 | Tessa van den Dolder — beneficiary gala with the Lions | €85,000 raised (March 2025) | 107 | INPUT | H | Fonds mobilisés |
| M119 | Club100 | « network of 100 partners » (définition) ; 7 entreprises + 1 individu listés | 110–112 | INPUT | M | Nombre réel de membres UNKNOWN |
| M120 | BNI Japan sponsorship | USD 90,000 / 3 years (30,000/yr from 2025) | 113 | INPUT | H | |
| M121 | CYE Accelerator | 6 ventures ; 12 mentors | 115–116 | OUTPUT | H | Mentors = INPUT |
| M122 | RISE to the Challenge (ECOSOC, 16 Apr 2025) | 1,160+ registrants ; 1,500+ live participants ; 6,000+ FB Live viewers ; 564 poll responses ; 4 languages ; 5 panelists | 117 | OUTPUT | H | **DQC-15** : live > inscrits ; ventilation par geographic_area et langue : VDX-07, VDX-08 |
| M123 | GITEX Africa | 52,000+ participants, 130+ countries | 119 | CONTEXT | — | ⚠ **Taille de l'événement externe, pas un output JCI** |
| M124 | 14th World Chambers Congress | 1,000+ leaders, 100 countries | 121 | CONTEXT | — | ⚠ idem |
| M125 | UN OHCHR Youth Rights Academy | 45 advocates (1 représentante JCI) | 121 | CONTEXT | — | ⚠ idem |
| M126 | Global Youth Dialogue 2025 (24 Sept) | 1,060+ registrants ; 662 live attendees ; 3,600+ FB Live viewers ; 1,300+ chat messages ; 800+ reactions | 122 | OUTPUT | H | Ventilation par geographic_area : VDX-09 |
| M127 | GYD — JCI Members vs Non-Members | 679 (79.6 %) / 174 (20.4 %) | 123 | OUTPUT | H | **DQC-14** : somme calculée 853 ≠ 662 live |
| M128 | Mastering Sustainable Leadership | 250+ participants ; 300+ members introduced to SDG Academy platform ; 4 Area Conferences | 124 | OUTPUT | H | |
| M129 | WBAF « How to Raise Smart Finance » | 100+ participants, all with certificates | 128 | OUTPUT | H | |
| M130 | ICC affiliation / national collaboration | 53 NOs and LOs affiliated ; 11 NOs formalized collaborations | 127 | OUTPUT | M | Changement institutionnel → possible OUTCOME |
| M131 | SIXT / Quantic / Zoho | « hundreds of members » ; « dozens … enrolled » ; « $100 credit » | 126–127 | OUTPUT | L | Non chiffrés ; $100 = valeur unitaire |
| M132 | Partnerships Website | 6,899 unique visitors ; 9,164 sessions | 129 | OUTPUT (comm.) | H | |

> Note de comptage : le tableau compte 132 lignes (M001–M132). Plusieurs lignes regroupent des sous-valeurs d'une même source (ex. M034, M039). Le détail indicateur par indicateur relève du Tier 2 (F).

## B.3 Répartition (vérification de cohérence)

Le décompte est donné en B.3-bis, généré automatiquement à partir du tableau pour éviter les erreurs manuelles.

## B.4 Chaîne **DOCUMENTED** — ce que JCI publie (OFFICIAL_JCI_FACT), rangé dans la grille IAOOI-v0 (SEMANTIC_INTERPRETATION)

> Les chiffres sont officiels. Leur **placement** dans les cases INPUT / ACTIVITY / OUTPUT / OUTCOME / IMPACT est notre lecture. JCI ne présente pas ses données ainsi.

### B.4.1 Au niveau agrégé (tout le réseau)

```
INPUT                     ACTIVITY                        OUTPUT                      OUTCOME          IMPACT            SDG
42,401 volunteers   →     1,000+ projects reported   →    21,148,414 beneficiaries →  [ABSENT]    →    [ABSENT]     →    Tags ODD
435,605 hours             (2025), ventilés par :          (méthode UNKNOWN)            aucun             seulement des      (Primary /
[p. 86]                   Area géo, AoO, pilier RISE      [p. 86]                      agrégat           affirmations       Secondary,
                          [p. 85–86]                                                   d'outcome         narratives         valeurs
                                                                                                         [p. vii, 2]        illisibles p. 84)
```
- **DOCUMENTED** : chiffres OFFICIAL_JCI_FACT pour les cases INPUT, ACTIVITY, OUTPUT et SDG (tag) ; placement = SEMANTIC_INTERPRETATION.
- **Maillons manquants** : OUTCOME et IMPACT agrégés. **NOT SPECIFIED IN THE SOURCE DOCUMENT.**
- **Lien OUTPUT → SDG** : déclaratif. Aucune règle de contribution n'est donnée. CONSTAT D'ABSENCE (couche texte vérifiée).

### B.4.2 Par programme (ce qui est effectivement chiffré)

| Programme | INPUT documenté | ACTIVITY documentée | OUTPUT documenté | OUTCOME documenté | IMPACT documenté | SDG (déclaré) |
|---|---|---|---|---|---|---|
| **CYE** [28–32] | Prix (NMT Group, montant UNKNOWN), juges (WBAF, BNI) [114] | Compétition dans 5 événements | 108 entrepreneurs | Récits : prix, mentorat, croissance d'entreprise (non attribuée) | IMPACT-CLAIM : 250 t CO2/an | 8, 9, 12 [26] |
| **JIB** [33–38] | — | Sessions dans toutes les Area Conferences + session de matching ICC | 345 participants | Récits : +20 % CA (« some »), emplois (non chiffrés) | — | NON MAPPÉ au niveau programme (seulement via l'AoO B&E) |
| **Skills Dev. / Trainings** [40–42] | 97 formateurs (?) | 33 + 48 sessions | 1,969 participants | — | — | ID : 4, 5, 10 |
| **Public Speaking / Debating** [43–52] | — | Compétitions | 52 participants ; 57 équipes | Récits de confiance (auto-déclarés) | — | Récits : 3, 4, 5, 8, 10, 16 |
| **TOYP** [54–58] | Juges partenaires [114] | Sélection | 164 candidats ; 10 lauréats | — (résultats = activités propres des lauréats) | IMPACT-CLAIM (lignes directrices nationales) | 3, 4, 10, 11 [26] |
| **Events** [59–70] | — | 5 événements | 10,729 inscriptions ; first timers | — | — | IC : 16, 17 |
| **IHD** [71–77] | 78 ambassadeurs ; 8M MNT (local) | 42 activités déclarées | 67,101 signatures | Loi de Zulia ; >90 % sensibilisation (Ankara) | — | Récits : 3, 4, 5, 8, 10, 13, 15, 16 |
| **Twinning** [78–82] | Facilitateurs internationaux | Accords, ateliers | 113 accords ; 85 / 100+ formés | 10 emplois ; 4 initiatives de suivi | — | Récits : 4, 8, 10, 17 |
| **Community Dev. / RISE** [84–94] | Bénévoles, heures, surplus, partenaires | 1,000+ projets, répartition par pilier | 21M bénéficiaires ; récits : formés, diplômés | Récits : 75 % placés, 100 emplois, 15 % startups | — | RISE : 1, 3, 8, 9, 11, 12, 16, 17 [26] **ou** 3, 8, 10 [85] |
| **Foundation** [96–98] | USD 10.35M depuis 2022 ; grants | Cycles de grants | Projets financés (UNKNOWN) | — | — | — |

> Toutes les cellules « — » = **NOT SPECIFIED IN THE SOURCE DOCUMENT**.

## B.5 Chaîne **PROPOSED** — PROPOSED_STANDARD (ne pas confondre avec B.4)

> ⚠ **PROPOSED_STANDARD.** Cette chaîne n'existe pas dans le rapport. C'est une proposition de complétion, alignée sur les termes JCI, à comparer avec votre propre modèle.

| Maillon | Indicateurs proposés (termes JCI réutilisés quand ils existent) | Règle de qualité proposée |
|---|---|---|
| INPUT | volunteers_engaged (members / non-members séparés), volunteer_hours (total, pas par personne), budget_local + devise + montant USD, in-kind, partner_count | Heures = total ; séparer membres et non-membres |
| ACTIVITY | activity_type (liste contrôlée C.3), sessions_count, duration, delivery_mode, dates | Date absolue obligatoire |
| OUTPUT | participants_unique, people_trained, people_reached (direct), items_distributed, agreements_signed, signatures | **direct ≠ indirect ≠ audience** ; « reached » jamais additionné à « participants » |
| OUTCOME | jobs_created, job_placements, businesses_created, revenue_change, skills_change (pré/post), awareness_change (enquête), policy_change, new_members | Horizon de mesure (ex. +3 mois) + méthode + taille de l'échantillon |
| IMPACT | Stocké comme **claim** avec : niveau d'attribution (attribution / contribution / narrative), méthode, horizon ≥ 12 mois | Jamais agrégé sans méthode |
| SDG | primary_sdg (1), secondary_sdgs (≤3), justification textuelle | Plafonner le nombre d'ODD secondaires (contre l'inflation de S7) |

## B.6 Incohérences relevées — index V1 (I1…I24 = DQC-01…24)

> Conservé pour la traçabilité V1. **La référence est désormais le registre §Q**, avec valeurs sourcées, type de conflit, statut UNRESOLVED et cas de test. Numérotation identique : I*n* = DQC-*nn*. Deux ajouts V2 : DQC-25, DQC-26.

| # | Sujet | Valeurs en conflit | Pages | Type |
|---|---|---|---|---|
| I1 | Membres | 100,000+ / 147,000+ / 147,670 | v, vi, 2, 8 | Arrondi + écart réel |
| I2 | Pays | 100+ / 114 / 114+ | v, 2, 9, 24 | Périmètre |
| I3 | Projets | 1,000+ (2024–25) / 1000+ (2025) / 10,000+ | v, 84, 85, vii | Ordre de grandeur + période |
| I4 | LOs | 4,500+ / 4,600 / 4,641 | v, 2, 8 | Arrondi |
| I5 | Bénévoles | 40,000+ / 42,401 | v/84, 86 | Arrondi |
| I6 | Participants aux événements | 10,000+ attendees / nearly 10,000 participants / 10,729 registrations | v, 59 | Libellés différents |
| I7 | Followers | 260,000+ vs somme plateformes 229,200 | v, 17–18 | Écart non expliqué |
| I8 | Impressions | « 2 million+ impressions » vs Facebook « Reach: Over 2 million » | v, 17 | **Reach ≠ impressions** |
| I9 | LEADER | 13,800 / nearly 13,000 / 13,872 ; appareils 12,564 | v, 19, 20 | Arrondi + base |
| I10 | Senators | 67 % H + 37 % F = 104 % | 100 | Erreur |
| I11 | Ankara | 49 vs 45 participants | 75 | Contradiction interne |
| I12 | Bridges | 35 participants vs 200+ youth trained | 91 | Périmètres mélangés |
| I13 | Impulso NOA | 4 / 22 = 18,2 % ≠ « 20% » | 94 | Arithmétique |
| I14 | GYD | 679 + 174 = 853 ≠ 662 live attendees | 122–123 | Base différente |
| I15 | ECOSOC | 1,500+ live participants > 1,160+ registrants | 117 | Possible (live sans inscription), non expliqué |
| I16 | RISE ODD | {1,3,8,9,11,12,16,17} vs {3,8,10} | 26, 85 | Mappage programme incohérent |
| I17 | RISE piliers | Workforce Empowerment / Mental Health Awareness vs Workforce Motivation / Preserving Mental Health | 85 | Libellés |
| I18 | Pourcentages | 100,01 % (piliers, Areas) | 85–86 | Arrondi |
| I19 | Europe LO | 15.8 % vs 15.9 % | 8, 11 | Arrondi |
| I20 | TOYP | « Ten Outstanding Persons of the Year » | 113 | Libellé erroné |
| I21 | Events externes | GITEX 52,000, WCC 1,000+, OHCHR 45 présentés près de l'impact JCI | 119–121 | Risque d'agrégation erronée |
| I22 | Doublon ODD | SDG 11 cité 2 fois (SDGs Hunt) | 89 | Doublon |
| I23 | Petitions | Somme des pays par Area = 191 | 73 | Comptage suspect |
| I24 | Périodes | 2024–25 ; 2025 ; Jan–Oct 2025 ; Oct 2024–Aug 2025 ; since 2022 ; since Oct 6 2025 | multiples | **Aucune période de reporting unique** |

---

# C. JCI IMPACT TAXONOMY

## C.0 Vue d'ensemble

```
L1  IMPACT DOMAIN  = area_of_opportunity (4)                      [OFFICIAL_JCI_FACT p. 2, 24–25 ; codes PROPOSED_STANDARD]
      │ 1..n  (un projet peut porter 2+ AoO — OFFICIAL_JCI_FACT p. 86)
L2  PROGRAM / INITIATIVE (≈15 nommés + « local project »)          [OFFICIAL_JCI_FACT si nommé ; codes et LOCAL_PROJECT = PROPOSED_STANDARD]
      │ 1..n
L3  ACTIVITY TYPE (liste contrôlée, 15 codes)                      [PROPOSED_STANDARD construite sur termes OFFICIAL_JCI_FACT]
      │ 1..n
L4  TARGET GROUP (12 codes, axe interne/externe)                   [PROPOSED_STANDARD construite sur termes OFFICIAL_JCI_FACT]
      │
L5  OUTPUT TYPE (14 types)       ─┐                                [PROPOSED_STANDARD ← métriques OFFICIAL_JCI_FACT (B.2)]
L6  OUTCOME TYPE (11 codes)       ├─ reliés par la chaîne IAOOI    [PROPOSED_STANDARD ← métriques OFFICIAL_JCI_FACT (B.2)]
L7  IMPACT (claim) TYPE (6 codes)─┘                                [PROPOSED_STANDARD ← affirmations OFFICIAL_JCI_FACT]
      │
L8  SDG (17)  — défaut hérité de L1/L2, surchargé par le projet    [OFFICIAL_JCI_FACT p. 24–26 ; héritage = SEMANTIC_INTERPRETATION]

Dimensions transverses (hors hiérarchie) : Géographie (Local → National → geographic_area → Global) [OFFICIAL_JCI_FACT p. 9] ·
Période · Pilier RISE [OFFICIAL_JCI_FACT p. 85] · Principe IHD [OFFICIAL_JCI_FACT partiel p. 74–75] · Catégorie de prix [OFFICIAL_JCI_FACT p. 102–103]
```

**Principe de conception** (PROPOSED_STANDARD) : seuls **L1 (area_of_opportunity), L2 (programmes nommés) et L8 (ODD)** ont des valeurs **OFFICIAL_JCI_FACT**. **L3 à L7 sont des PROPOSED_STANDARD** : ils n'existent pas comme taxonomies JCI. Attribuer une donnée à l'un de leurs codes est une SEMANTIC_INTERPRETATION. Nous les proposons comme listes contrôlées courtes, chaque code étant rattaché à des occurrences du rapport. Elles sont faites pour être étendues, pas figées.

## C.1 — L1 Impact Domain = `area_of_opportunity` — valeurs OFFICIAL_JCI_FACT, codes PROPOSED_STANDARD

| Code (PROPOSED_STANDARD) | Valeur (OFFICIAL_JCI_FACT) | Définition (OFFICIAL_JCI_FACT) | ODD par défaut (OFFICIAL_JCI_FACT p. 24–25) | Pages |
|---|---|---|---|---|
| `BE` | Business & Entrepreneurship | « Programs fostering innovation, ethical business, and sustainable economic growth » | 8, 9, 12 | 2, 24 |
| `ID` | Individual Development | « Skills, training, and experiences that build confidence and leadership capacity » | 4, 5, 10 | 2, 24 |
| `IC` | International Cooperation | « Events, partnerships, and networks that connect young leaders across borders » | 16, 17 | 2, 24–25 |
| `CI` | Community Impact | « Grassroots projects addressing real needs in local societies » | 1, 2, 3, 4, 5, 8, 9, 11, 12, 13 | 2, 25 |

Relations : un projet a **≥1** AoO (OFFICIAL_JCI_FACT p. 86). **Aucun domaine « environnement »** : les projets environnementaux relèvent de CI par ses ODD 12/13 (SEMANTIC_INTERPRETATION H). Les ODD 6, 7, 14, 15 n'ont pas de domaine par défaut (OFFICIAL_JCI_FACT, cf. A.2).

## C.2 — L2 Program / Initiative — noms OFFICIAL_JCI_FACT, codes PROPOSED_STANDARD, placement selon statut

| Code (PROPOSED_STANDARD) | Programme (OFFICIAL_JCI_FACT) | AoO (placement dans le rapport) | Statut du placement | Sous-composants officiels | ODD programme (p. 26) | Pages |
|---|---|---|---|---|---|---|
| `CYE` | Creative Young Entrepreneur | BE | OFFICIAL_JCI_FACT | CYE Accelerator (SDSN Youth) | 8, 9, 12 | 28, 115 |
| `JIB` | JCI in Business | BE | OFFICIAL_JCI_FACT | International Business Matching Session | — | 33 |
| `SKILLS_DEV` | Skills Development (Trainer certification) | ID | OFFICIAL_JCI_FACT | CNT, CAT, Global Trainers, Training Mentors | — | 40–41 |
| `EVENT_TRAINING` | Trainings at Area Conferences & World Congress | ID | OFFICIAL_JCI_FACT | Leadership Training Sessions ; Skills Development Sessions | — | 42 |
| `LEAD_MASTERCLASS` | Leadership Masterclasses | ID | SEMANTIC_INTERPRETATION (M) | — | 4, 5, 10, 16, 17 | 26 |
| `PUBLIC_SPEAKING` | Public Speaking Competition | ID | OFFICIAL_JCI_FACT | — | — | 43 |
| `DEBATING` | Debating Championship | ID | OFFICIAL_JCI_FACT | EN / FR / ES | — | 48 |
| `TOYP` | Ten Outstanding Young Persons of the World | IC | OFFICIAL_JCI_FACT | — | 3, 4, 10, 11 | 26, 54 |
| `EVENTS` | World Congress & Area Conferences | IC | OFFICIAL_JCI_FACT | 4 Area Conferences + WC | — | 59 |
| `IHD` | International Human Duties Initiative / IHDD | IC | OFFICIAL_JCI_FACT | 7 Duties ; National Ambassadors ; Best Human Duties Project Award | — | 71 |
| `TWINNING` | JCI Twinning | IC | OFFICIAL_JCI_FACT | Buddy Project, Mastery Month (initiatives d'un twinning) | — | 78 |
| `COMMUNITY_DEV` | Community Development Projects | CI | OFFICIAL_JCI_FACT | — | (ODD CI) | 84 |
| `RISE` | JCI RISE | CI | OFFICIAL_JCI_FACT | Piliers : Sustaining & Rebuilding Economies / Workforce Motivation / Preserving Mental Health | 1, 3, 8, 9, 11, 12, 16, 17 (p. 26) — ou 3, 8, 10 (p. 85) | 26, 85 |
| `SUST_LEADERSHIP_COURSE` | Mastering Sustainable Leadership (SDG Academy) | — | SEMANTIC_INTERPRETATION : ID | — | — | 124 |
| `GLOBAL_CITIZEN_COURSE` | Becoming Global Citizens for a Sustainable Society | — | SEMANTIC_INTERPRETATION : ID/IC | — | — | 125 |
| `GYD` | Global Youth Dialogue | — | SEMANTIC_INTERPRETATION : IC | ateliers par AoO | — | 122 |
| `LOCAL_PROJECT` | *(pas un programme JCI)* Projet local sans programme global | selon contenu | PROPOSED_STANDARD | — | — | — |
| Transversaux (hors AoO) | JCI Foundation / Development Grants ; JCI Senate ; JCI Awards ; Club100 ; Alumni Clubs ; Junior Clubs ; Member-centric partnerships | aucun | OFFICIAL_JCI_FACT (non rattachés) | — | — | 12, 13, 96–129 |

**Base du placement programme → area_of_opportunity** (précision V2) :
- **OFFICIAL_JCI_FACT, base `explicit_text`** : le programme est nommé dans le texte de l'Area of Opportunity [p. 24–25]. Cas : CYE, JIB (B&E) ; « certification pathways for trainers, public speaking competitions, and debating championships » (ID) ; « World Congress, Area Conferences, TOYP, and Human Duties Day » (IC) ; « JCI RISE and grassroots community projects » (CI).
- **OFFICIAL_JCI_FACT, base `document_structure`** : le programme figure seulement dans le chapitre de l'Area of Opportunity (intercalaire de section). Cas : JCI Twinning (IC, p. 78) ; Trainings at Area Conferences (ID, p. 42).
- **SEMANTIC_INTERPRETATION** : programme hors chapitre AoO (Leadership Masterclasses, Mastering Sustainable Leadership, Global Citizenship course, Global Youth Dialogue).

Relations : Programme → AoO **par défaut** (un CYE est BE). Un projet local d'un programme peut porter des AoO et ODD supplémentaires. Exemple : EMPRENDHER 2.0 est placé en CI [p. 88] alors que son contenu est entrepreneurial (SEMANTIC_INTERPRETATION H). **Règle recommandée** : AoO = placement programme + AoO déduites du contenu, avec un marqueur de provenance.

## C.3 — L3 Activity Type — PROPOSED_STANDARD (codes construits sur des termes OFFICIAL_JCI_FACT)

| Code (PROPOSED_STANDARD) | Libellé | Occurrences dans le document (OFFICIAL_JCI_FACT) | Pages |
|---|---|---|---|
| `TRAINING_WORKSHOP` | Formation / atelier / module | « training », « workshops », « intensive sessions », « Leadership Training Sessions » | 42, 79, 80, 87, 91 |
| `MENTORING` | Mentorat | « mentorship », « Buddy Project », « Mentor–Mentee Programme » | 30, 82, 105, 115 |
| `COMPETITION` | Compétition / concours | CYE, Public Speaking, Debating, « entrepreneurship contests » | 28, 43, 48, 98 |
| `RECOGNITION_AWARD` | Distinction / prix | TOYP, JCI Awards, Senate | 54, 100, 102 |
| `CONFERENCE_EVENT` | Congrès / conférence | World Congress, Area Conferences, national conference | 59, 107 |
| `PANEL_FORUM_DIALOGUE` | Panel / forum / dialogue | « panel discussion », « Citizen Forum », « 7x7: The Duties Circle », GYD | 74, 75, 76, 117, 122 |
| `ADVOCACY_CAMPAIGN` | Plaidoyer / pétition / proclamation | « petition campaigns, governmental proclamations » | 71, 73 |
| `AWARENESS_EDUCATION` | Sensibilisation / éducation du public | « education and outreach », « SDGs Hunt », talks | 31, 56, 89 |
| `COMMUNITY_SERVICE` | Service direct (distribution, nettoyage, marche) | « 100 food care packages », « cleanup of Little Manila Park », « Bridging Connections walk » | 71–72, 74 |
| `ENVIRONMENTAL_ACTION` | Action environnementale (nettoyage, plantation) | « citizen planting », « cleanup operation » | 74 |
| `NETWORKING_MATCHING` | Réseautage / mise en relation / pitch | JIB matching, « pitching opportunities », connexion étudiants–entreprises | 33, 93, 94 |
| `PARTNERSHIP_AGREEMENT` | Accord / jumelage | Twinning agreements, ICC affiliation | 78, 127 |
| `FUNDRAISING` | Collecte de fonds | « beneficiary gala… raised 85k euros », sponsorships | 77, 107 |
| `ONLINE_COURSE_WEBINAR` | Cours / webinaire en ligne | SDG Academy platform, virtual debate, livestream | 50, 77, 124 |
| `INTERNAL_GOVERNANCE` | Structuration interne (agenda, ESG) | « inaugural Sustainability Agenda » | 90 |

## C.4 — L4 Target Group (Beneficiary Type) — PROPOSED_STANDARD (termes OFFICIAL_JCI_FACT en A.7)

| Code | Libellé | Axe | Termes du rapport mappés |
|---|---|---|---|
| `JCI_MEMBERS` | Membres JCI (18–40) | **INTERNE** | members, local chapter presidents, first timers |
| `JCI_JUNIOR` | Membres Junior Club (14–21) | INTERNE | JCI Junior |
| `YOUTH` | Jeunes (hors membres) | Externe | young people, youth |
| `STUDENTS` | Élèves / étudiants | Externe | rural students, high school students, advanced students |
| `CHILDREN` | Enfants | Externe | children, underserved children |
| `ENTREPRENEURS` | (Jeunes) entrepreneurs, porteurs de projet | Externe | young/aspiring entrepreneurs, small business owners |
| `WOMEN_ENTREPRENEURS` | Femmes entrepreneures | Externe | women entrepreneurs |
| `SMES_BUSINESSES` | PME / entreprises | Externe | SMEs, businesses, local businesses |
| `VULNERABLE_COMMUNITIES` | Familles / communautés vulnérables | Externe | families in need, vulnerable groups, underserved communities |
| `PROFESSIONALS` | Professionnels | Externe | professionals, medical professionals |
| `GENERAL_PUBLIC` | Grand public / audience | Externe | community, livestream viewers |
| `DECISION_MAKERS` | Institutions / décideurs | Externe | governments, Members of Parliament, Chamber of Deputies |

Attributs (pas des groupes) : `gender`, `age_band`, `rural_urban`, `vulnerability_flag`. Seuls **genre et âge** apparaissent dans le rapport (OFFICIAL_JCI_FACT A.7).

## C.5 — L5 Output Type — PROPOSED_STANDARD (← B.2)

| Code | Unité | Exemples OFFICIAL_JCI_FACT |
|---|---|---|
| `PARTICIPANTS` | personne | JIB 345, PS 52, NY 100 |
| `PEOPLE_TRAINED` | personne | 1,969 ; 200+ youth trained ; 85 trained |
| `PEOPLE_REACHED_DIRECT` | personne | 2,000 rural students |
| `PEOPLE_REACHED_OUTREACH` | personne | 50,000 via outreach ; 3,000 livestream |
| `REGISTRATIONS` / `ATTENDEES` | personne | 10,729 ; 662 live |
| `COMPLETIONS` | personne | 60 graduates ; 100+ certificates |
| `APPLICATIONS_ENTRIES` | candidature | 164 TOYP ; 1,120 award entries |
| `TEAMS` | équipe | 57 debating teams |
| `ITEMS_DISTRIBUTED` | objet | 100 food care packages |
| `SIGNATURES` | signature | 67,101 |
| `AGREEMENTS_SIGNED` | accord | 113 twinning agreements |
| `DOCUMENTS_PRODUCED` | document | 7 outcome summaries ; 1 joint declaration |
| `PHYSICAL_OUTPUT` | kg, t, kW, arbres… (+ `sub_code`) | 100kW installés [29] ; 100+ t de déchets traités [31] |
| `COMM_AUDIENCE` | vue / follower / lecteur | followers, reach, readers |

## C.6 — L6 Outcome Type — PROPOSED_STANDARD (← B.2)

| Code | Exemples OFFICIAL_JCI_FACT | Mesure présente dans le rapport ? |
|---|---|---|
| `JOBS_CREATED` | 10 new jobs [79] ; 100 jobs [93] | Chiffre déclaré, sans méthode |
| `JOB_PLACEMENT` | 75 % placed [91] | %, base `unknown` (DQC-12) |
| `BUSINESS_CREATED` | 15 % launching startups [91] ; « dozens » [79] | Partiel |
| `BUSINESS_GROWTH` | revenue +up to 20 % [35] | Auto-déclaré |
| `ACCESS_TO_FINANCE_MARKETS` | « startups secured funding », expansion Japon/Chine [93] | Qualitatif |
| `SKILLS_CONFIDENCE` | récits PS/Debating [44–52] | Qualitatif |
| `AWARENESS_ATTITUDE` | >90 % increased awareness [75] | **Instrument (formulaire)** |
| `POLICY_INSTITUTIONAL_CHANGE` | Loi de Zulia [72] ; reconnaissance Chambre de Salta [94] ; Academy créée [45] | Factuel, attribution = « inspired by » |
| `FOLLOW_UP_INITIATIVES` | 4 follow-up initiatives [80] ; mentoring project [77] | Chiffre déclaré |
| `NEW_MEMBERS` | 4 new members [94] ; club 4→40 [104] | Chiffre déclaré (outcome **organisationnel**) |
| `PARTNERSHIPS_FORMED` | Coca-Cola, OSDE… [94] ; 40+ organizations [93] | Chiffre déclaré |

## C.7 — L7 Impact (claim) Type — PROPOSED_STANDARD

> Aucun impact n'est **mesuré avec attribution** dans le rapport (S3). Ces codes typent des **affirmations**, à stocker avec un niveau d'attribution.

| Code | Affirmations OFFICIAL_JCI_FACT | Pages |
|---|---|---|
| `ENVIRONMENTAL` | 250 t CO2/an évitées ; 100+ t de déchets alimentaires ; biodiversité | 30, 31, 32 |
| `ECONOMIC_RESILIENCE` | « rebuild economies », « economic stability » | 85, 91 |
| `HEALTH_WELLBEING` | lignes directrices nationales en neurotraumatologie ; santé mentale | 58, 93 |
| `EDUCATION_ACCESS` | éducation spatiale, STEM | 56 |
| `SOCIAL_INCLUSION_EQUITY` | « restored dignity, purpose, and hope » | 91 |
| `GOVERNANCE_PEACE` | droits et devoirs humains, dialogue | 71–77 |

Niveaux d'attribution proposés (PROPOSED_STANDARD) : `measured_attribution` · `measured_contribution` · `self_reported` · `narrative_only`.

## C.8 — L8 SDG — OFFICIAL_JCI_FACT

**Matrice AoO × SDG (OFFICIAL_JCI_FACT p. 24–25)**

| SDG → | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BE | | | | | | | | ● | ● | | | ● | | | | | |
| ID | | | | ● | ● | | | | | ● | | | | | | | |
| IC | | | | | | | | | | | | | | | | ● | ● |
| CI | ● | ● | ● | ● | ● | | | ● | ● | | ● | ● | ● | | | | |

**Matrice Programme × SDG (OFFICIAL_JCI_FACT p. 26)**

| Programme | SDG |
|---|---|
| CYE | 8, 9, 12 |
| TOYP | 3, 4, 10, 11 |
| Leadership Masterclasses | 4, 5, 10, 16, 17 |
| JCI RISE | 1, 3, 8, 9, 11, 12, 16, 17 (p. 26) ; 3, 8, 10 (p. 85) ⚠ |

Le rapport ne donne aucune justification d'alignement au niveau projet, hormis des listes (OFFICIAL_JCI_FACT). Les libellés ODD du document suivent les intitulés ONU courts (« SDG 8: Decent Work and Economic Growth »). La casse varie (« Zero hunger », « Gender equality »).

## C.9 Règles relationnelles (pour base de données et LLM)

| Règle | Statut |
|---|---|
| R1 — Un projet appartient à 1 LO (ou 1 NO pour les projets nationaux) ; une LO appartient à 1 NO ; une NO à 1 `geographic_area` | OFFICIAL_JCI_FACT (structure p. 8–10) ; cardinalités exactes SEMANTIC_INTERPRETATION |
| R2 — Un projet porte 1..n AoO | OFFICIAL_JCI_FACT p. 86 |
| R3 — Un projet rattaché à un programme hérite de l'AoO et des ODD par défaut du programme ; le projet peut en ajouter | SEMANTIC_INTERPRETATION (H), cf. récits |
| R4 — Projet RISE → 1..n piliers RISE | SEMANTIC_INTERPRETATION (M) (le % par pilier suppose un tag) |
| R5 — ODD : 1 principal + n secondaires | SEMANTIC_INTERPRETATION (M), libellés p. 84 |
| R6 — Un twinning relie ≥2 LO/NO de pays différents ; un même projet peut être déclaré par chaque partie → risque de double comptage | OFFICIAL_JCI_FACT (définition p. 78) ; risque = SEMANTIC_INTERPRETATION |
| R7 — Les métriques de membres (ID) et de bénéficiaires externes (CI) ne s'additionnent pas | PROPOSED_STANDARD (cf. S6) |
| R8 — Les métriques CONTEXT et les événements externes (GITEX, WCC) ne sont jamais agrégés comme outputs | PROPOSED_STANDARD (cf. I21) |

---

# D. SCHÉMA JSON — PROJET JCI NORMALISÉ (V2, provenance par champ)

## D.1 Ce qui change par rapport à V1 (et ce qui ne change pas)

- **Inchangé** : les 11 clés racine de votre squelette, dans le même ordre.
- **Nouveau** : chaque donnée porte une **enveloppe de provenance**. On en distingue quatre formes :

| Forme | Usage | Clés | Exemple |
|---|---|---|---|
| **Fait** | Valeur écrite dans une source | `value`, `layer` (OFFICIAL_JCI_FACT ou LOCAL_REPORTED_FACT), `value_status: extracted`, `value_qualifier`, `unit`, `source{origin, page, section, quote}`, `fact_scope` | `{"value": 35, "layer": "OFFICIAL_JCI_FACT", "value_status": "extracted", "source": {"page": "91", "quote": "35 participants engaged…"}}` |
| **Inconnu** | Valeur nécessaire mais absente | `value: null`, `value_status: unknown` (ou `visual_data_not_extracted`), `reason`, `source{origin, searched_scope}` | `organization.local_organization` du Bridges Project |
| **Interprétation** | Déduction, normalisation, classement, calcul | `value`, `layer: SEMANTIC_INTERPRETATION`, `rule_id`, `basis`, `confidence` (+ `formula`/`inputs` si calculé) | pilier RISE du Bridges Project ; 85 × 5 = 425 h (TC3) |
| **Code standard** | Code ou liste contrôlée de votre solution | `value`, `layer: PROPOSED_STANDARD`, `standard` (`JCI-NORM-v0`, `IAOOI-v0`…) | `TRAINING_WORKSHOP`, `INPUT` |

- **Métriques** : chaque métrique sépare `value{…}` (le chiffre et sa source) et `normalization{metric_code, iaooi_class, layer: SEMANTIC_INTERPRETATION, rule_id, basis}` (notre lecture). Le libellé brut reste dans `label_raw`.
- **Vocabulaire JCI** (area_of_opportunity, geographic_area, programme, ODD) : triplet `value` (libellé OFFICIAL_JCI_FACT cité) + `code` (PROPOSED_STANDARD) + `assignment` (qui a rattaché la donnée à ce libellé : JCI, l'organisation locale ou le moteur).
- **Area** : `organization.geographic_area` et `project.area_of_opportunity[]`. Aucune clé `area` (règle V9).
- **Qualité** : `data_quality.conflict_refs` pointe vers les objets DQC ; `visual_refs` vers les objets VDX ; `unknowns` liste les champs vides.

## D.2 Objet de référence : Bridges Project (JCI Syria) [p. 91]

Répartition de la provenance dans l'objet (comptée automatiquement) :

| Couche | value_status | Nb d'enveloppes |
|---|---|---|
| OFFICIAL_JCI_FACT | extracted | 33 |
| OFFICIAL_JCI_FACT | unknown | 18 |
| SEMANTIC_INTERPRETATION | — | 25 |
| PROPOSED_STANDARD | — | 26 |

Points de rigueur illustrés :
- **Programme** : « JCI RISE » est un OFFICIAL_JCI_FACT (p. 91). Le **rattachement à Community Impact** est une SEMANTIC_INTERPRETATION : il combine deux faits officiels (projet ∈ RISE, p. 91 ; RISE cité dans le texte Community Impact, p. 25) avec la règle d'héritage `INH-PROGRAM-AOO`.
- **Piliers RISE** : les libellés sont officiels (p. 85). Leur attribution à ce projet est une interprétation (confiance M), car le rapport ne l'indique pas.
- **geographic_area** : « Africa and the Middle East » est un libellé officiel. Le rattachement du projet vient du libellé du prix (`AREA-2`), pas d'une liste pays → Area : cette liste n'est pas lisible (VDX-01).
- **Outcomes** : 75 % et 15 % sont officiels (publiés). Leur **base** est `unknown` et renvoie à DQC-12. Aucun effectif n'est calculé.
- **Impact** : la phrase est officielle **en tant que citation** (`fact_scope: statement_published`). Son niveau d'attribution (`narrative_only`) est une interprétation.

```json
{
  "project": {
    "project_id": {
      "value": "JCI-RPT2025-P091-BRIDGES",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:ID-SCHEME-v0"
    },
    "name": {
      "value": "Bridges Project",
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "fact_scope": "statement_published",
      "source": {
        "origin": "jci_report_2025",
        "document": "JCI Impact Report 2025",
        "page": "91",
        "section": "JCI RISE Impact Stories",
        "quote": "His “Bridges Project” provided training, mentorship, and practical tools"
      }
    },
    "description": {
      "value": "training, mentorship, and practical tools for young people struggling to start or restart businesses in an unstable economy",
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "fact_scope": "statement_published",
      "source": {
        "origin": "jci_report_2025",
        "document": "JCI Impact Report 2025",
        "page": "91",
        "section": "JCI RISE Impact Stories",
        "quote": "provided training, mentorship, and practical tools for young people struggling to start or restart businesses in an unstable economy"
      }
    },
    "program": {
      "name": {
        "value": "JCI RISE",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "Motaz Mezher turned JCI RISE into a lifeline for youth and entrepreneurs in Syria"
        }
      },
      "code": {
        "value": "RISE",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "components": [
        {
          "type": "rise_pillar",
          "value": {
            "value": "Sustaining and Rebuilding Economies",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "85",
              "section": "JCI RISE Projects",
              "quote": "Sustaining and Rebuilding Economies 40.30%"
            }
          },
          "assignment": {
            "value": true,
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "MAP-RISE-PILLAR",
            "basis": "content: entrepreneurship, restarting businesses; pillar not stated for this project",
            "confidence": "M"
          }
        },
        {
          "type": "rise_pillar",
          "value": {
            "value": "Workforce Motivation",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "85",
              "section": "JCI RISE Projects",
              "quote": "Workforce Motivation 31.67%"
            }
          },
          "assignment": {
            "value": true,
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "MAP-RISE-PILLAR",
            "basis": "content: 75% placed in jobs or internships; pillar not stated for this project",
            "confidence": "M"
          }
        }
      ]
    },
    "area_of_opportunity": [
      {
        "value": {
          "value": "Community Impact",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "25",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Community Impact"
          }
        },
        "code": {
          "value": "CI",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "INH-PROGRAM-AOO",
          "basis": "project is JCI RISE (p. 91, OFFICIAL) + 'Through initiatives such as JCI RISE' in Community Impact text (p. 25, OFFICIAL); inheritance = interpretation",
          "confidence": "H",
          "inputs": [
            {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "25",
              "section": "Four Areas of Opportunity and SDG Alignment",
              "quote": "Through initiatives such as JCI RISE and grassroots community projects"
            }
          ]
        }
      }
    ],
    "period": {
      "start": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "end": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "duration": {
        "value": 3,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "week",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "Over three weeks"
        }
      }
    },
    "recognition": [
      {
        "label_raw": {
          "value": "2024 Africa and the Middle East Best RISE Project Winner",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "91",
            "section": "JCI RISE Impact Stories",
            "quote": "2024 Africa and the Middle East Best RISE Project Winner"
          }
        },
        "award_category": {
          "value": {
            "value": "Best JCI RISE Project",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "102",
              "section": "JCI Awards and Outstanding Awardees",
              "quote": "Best JCI RISE Project"
            }
          },
          "assignment": {
            "value": true,
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "MAP-AWARD",
            "basis": "'Best RISE Project' ↔ official category 'Best JCI RISE Project'",
            "confidence": "H"
          }
        },
        "level": {
          "value": "geographic_area",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "geographic_area": {
          "value": {
            "value": "Africa and the Middle East",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "9",
              "section": "International Presence – Operational Areas",
              "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
            }
          },
          "code": {
            "value": "AFME",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "assignment": {
            "value": true,
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "AREA-2",
            "basis": "award label contains 'Africa and the Middle East'",
            "confidence": "H"
          }
        },
        "year": {
          "value": 2024,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "91",
            "section": "JCI RISE Impact Stories",
            "quote": "2024 Africa and the Middle East Best RISE Project Winner"
          }
        }
      }
    ]
  },
  "organization": {
    "local_organization": {
      "value": null,
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "unknown",
      "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
      "source": {
        "origin": "jci_report_2025",
        "searched_scope": "p. 91"
      }
    },
    "national_organization": {
      "value": "JCI Syria",
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "fact_scope": "statement_published",
      "source": {
        "origin": "jci_report_2025",
        "document": "JCI Impact Report 2025",
        "page": "91",
        "section": "JCI RISE Impact Stories",
        "quote": "JCI Syria"
      }
    },
    "geographic_area": {
      "value": {
        "value": "Africa and the Middle East",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "9",
          "section": "International Presence – Operational Areas",
          "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
        }
      },
      "code": {
        "value": "AFME",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "GEO-FROM-AWARD",
        "basis": "project won the Africa and the Middle East Area award; NO→geographic_area mapping for Syria is not published (map p. 9 = VDX-01)",
        "confidence": "H"
      }
    },
    "partner_organizations": [],
    "lead_contact": {
      "name": {
        "value": "Motaz Mezher",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "Motaz Mezher"
        }
      },
      "role": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "personal_data": true
    }
  },
  "location": {
    "country": {
      "value": "Syria",
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "fact_scope": "statement_published",
      "source": {
        "origin": "jci_report_2025",
        "document": "JCI Impact Report 2025",
        "page": "91",
        "section": "JCI RISE Impact Stories",
        "quote": "a lifeline for youth and entrepreneurs in Syria"
      }
    },
    "country_iso2": {
      "value": "SY",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NORM-ISO3166",
      "basis": "country name → ISO code",
      "confidence": "H"
    },
    "city": {
      "value": null,
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "unknown",
      "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
      "source": {
        "origin": "jci_report_2025",
        "searched_scope": "p. 91"
      }
    },
    "scope": {
      "value": null,
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "unknown",
      "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
      "source": {
        "origin": "jci_report_2025",
        "searched_scope": "p. 91"
      }
    }
  },
  "activity": {
    "activity_types": [
      {
        "code": {
          "value": "TRAINING_WORKSHOP",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "'training' / 'intensive sessions'",
          "confidence": "H",
          "evidence_quote": "35 participants engaged in intensive sessions"
        }
      },
      {
        "code": {
          "value": "MENTORING",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "'mentorship'",
          "confidence": "H",
          "evidence_quote": "provided training, mentorship, and practical tools"
        }
      }
    ],
    "topics": {
      "value": [
        "entrepreneurship",
        "resilience",
        "financial literacy"
      ],
      "layer": "OFFICIAL_JCI_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "fact_scope": "statement_published",
      "source": {
        "origin": "jci_report_2025",
        "document": "JCI Impact Report 2025",
        "page": "91",
        "section": "JCI RISE Impact Stories",
        "quote": "covering entrepreneurship, resilience, and financial literacy"
      }
    },
    "resources": [
      {
        "label_raw": "20 volunteer trainers",
        "value": {
          "value": 20,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "91",
            "section": "JCI RISE Impact Stories",
            "quote": "led by 20 volunteer trainers"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "people giving time = resource",
          "confidence": "H"
        },
        "role": "trainer"
      },
      {
        "label_raw": null,
        "value": {
          "value": null,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "jci_report_2025",
            "searched_scope": "p. 91"
          },
          "unit": "hour"
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEER_HOURS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "field expected by IAOOI-v0",
          "confidence": "H"
        }
      }
    ]
  },
  "beneficiaries": [
    {
      "target_group": {
        "code": {
          "value": "YOUTH",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'young people' / 'youth'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "young people struggling to start or restart businesses",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "for young people struggling to start or restart businesses"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "not described as JCI members",
        "confidence": "M"
      },
      "count": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        },
        "unit": "person"
      },
      "attributes": {
        "female_share": {
          "value": 0.5,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "at_least",
          "unit": "ratio",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "91",
            "section": "JCI RISE Impact Stories",
            "quote": "more than half of participants being young women"
          }
        }
      }
    },
    {
      "target_group": {
        "code": {
          "value": "ENTREPRENEURS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'entrepreneurs'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "youth and entrepreneurs",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "a lifeline for youth and entrepreneurs in Syria"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "not described as JCI members",
        "confidence": "M"
      },
      "count": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        },
        "unit": "person"
      },
      "attributes": {}
    }
  ],
  "outputs": [
    {
      "label_raw": "35 participants engaged in intensive sessions",
      "value": {
        "value": 35,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "35 participants engaged in intensive sessions"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PARTICIPANTS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "people taking part",
        "confidence": "H"
      },
      "conflict_ref": "DQC-12"
    },
    {
      "label_raw": "200+ youth trained",
      "value": {
        "value": 200,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "at_least",
        "unit": "person",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "200+ youth trained"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PEOPLE_TRAINED",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "people trained",
        "confidence": "H"
      },
      "conflict_ref": "DQC-12"
    }
  ],
  "outcomes": [
    {
      "label_raw": "75% placed in jobs or internships",
      "value": {
        "value": 0.75,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "ratio",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "75% placed in jobs or internships"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "JOB_PLACEMENT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "change in beneficiaries' employment status",
        "confidence": "H"
      },
      "base_population": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "base not stated: 35 participants or 200+ trained (DQC-12)",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "measurement": {
        "method": {
          "value": null,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "jci_report_2025",
            "searched_scope": "p. 91"
          }
        },
        "horizon": {
          "value": null,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "jci_report_2025",
            "searched_scope": "p. 91"
          }
        }
      }
    },
    {
      "label_raw": "15% launching startups",
      "value": {
        "value": 0.15,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "ratio",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "15% launching startups"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "BUSINESS_CREATED",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "business creation by beneficiaries",
        "confidence": "H"
      },
      "base_population": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "base not stated (DQC-12)",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "measurement": {
        "method": {
          "value": null,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "jci_report_2025",
            "searched_scope": "p. 91"
          }
        },
        "horizon": {
          "value": null,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "jci_report_2025",
            "searched_scope": "p. 91"
          }
        }
      }
    }
  ],
  "impact": [
    {
      "claim_raw": {
        "value": "The program didn't just deliver knowledge—it restored dignity, purpose, and hope to those who felt abandoned.",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "The program didn't just deliver knowledge—it restored dignity, purpose, and hope to those who felt abandoned."
        }
      },
      "impact_type": {
        "code": {
          "value": "SOCIAL_INCLUSION_EQUITY",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-IMPACT-CLAIM",
          "basis": "dignity / hope",
          "confidence": "M"
        }
      },
      "attribution_level": {
        "value": "narrative_only",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "IMPACT-ATTRIBUTION",
        "basis": "no measurement cited",
        "confidence": "H"
      },
      "measured": {
        "value": false,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "IMPACT-ATTRIBUTION",
        "basis": "no method, indicator or horizon in source",
        "confidence": "H"
      }
    }
  ],
  "sdgs": [
    {
      "sdg": 4,
      "label": {
        "value": "Quality Education",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 4: Quality Education"
        }
      },
      "assignment": {
        "value": true,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "By advancing SDG 4 (Quality Education), SDG 8 (Decent Work & Economic Growth), and SDG 17 (Partnerships)"
        }
      },
      "role": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "ID",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 8,
      "label": {
        "value": "Decent Work and Economic Growth",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 8: Decent Work and Economic Growth"
        }
      },
      "assignment": {
        "value": true,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "By advancing SDG 4 (Quality Education), SDG 8 (Decent Work & Economic Growth), and SDG 17 (Partnerships)"
        }
      },
      "role": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "BE",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 17,
      "label": {
        "value": "Partnerships for the Goals",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 17: Partnerships for the Goals"
        }
      },
      "assignment": {
        "value": true,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "By advancing SDG 4 (Quality Education), SDG 8 (Decent Work & Economic Growth), and SDG 17 (Partnerships)"
        }
      },
      "role": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "p. 91"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "IC"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    }
  ],
  "evidence": [
    {
      "type": {
        "value": "testimonial_quote",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "content": {
        "value": "Thanks to JCI RISE, I didn't just lead a program—I became part of a larger movement to rebuild hope, livelihoods, and economic stability in my community.",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "Thanks to JCI RISE, I didn't just lead a program—I became part of a larger movement"
        }
      }
    },
    {
      "type": {
        "value": "case_story",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "content": {
        "value": "Jad, a 19-year-old who built a thriving marketing agency that now serves clients in Syria and the UAE",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "91",
          "section": "JCI RISE Impact Stories",
          "quote": "Jad, a 19-year-old who built a thriving marketing agency that now serves clients in Syria and the UAE"
        }
      }
    }
  ],
  "data_quality": {
    "record_origin": "jci_report_2025",
    "verification": {
      "value": "none",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:STATUS-v0"
    },
    "conflict_refs": [
      "DQC-12"
    ],
    "visual_refs": [],
    "unknowns": [
      "project.period.start",
      "project.period.end",
      "organization.local_organization",
      "organization.lead_contact.role",
      "location.city",
      "location.scope",
      "activity.resources[VOLUNTEER_HOURS]",
      "beneficiaries[*].count",
      "outcomes[*].base_population",
      "outcomes[*].measurement",
      "sdgs[*].role"
    ],
    "rule_check": "P0 — no field above is OFFICIAL_JCI_FACT without page+quote"
  }
}
```

## D.3 Correspondance champ → couche (référence rapide)

| Champ | Valeur | Rattachement / classement | Code |
|---|---|---|---|
| `project.name`, `description` | OFFICIAL_JCI_FACT (JCI) ou LOCAL_REPORTED_FACT (soumission) | — | — |
| `project.program` | libellé OFFICIAL_JCI_FACT si programme nommé dans le rapport | JCI (texte) / organisation locale / SEMANTIC_INTERPRETATION | PROPOSED_STANDARD (`RISE`, `LOCAL_PROJECT`…) |
| `project.program.components` (piliers RISE) | libellé OFFICIAL_JCI_FACT (p. 85) | SEMANTIC_INTERPRETATION sauf déclaration explicite | — |
| `project.area_of_opportunity[]` | libellé OFFICIAL_JCI_FACT (p. 24–25) | SEMANTIC_INTERPRETATION (`INH-PROGRAM-AOO`, `MAP-AOO-CONTENT`) | PROPOSED_STANDARD (`BE/ID/IC/CI`) |
| `project.period` | fait si date écrite ; `unknown` sinon | normalisation de date = SEMANTIC_INTERPRETATION | — |
| `organization.geographic_area` | libellé OFFICIAL_JCI_FACT (p. 9) | SEMANTIC_INTERPRETATION (`AREA-2`, `GEO-FROM-COUNTRY`) | PROPOSED_STANDARD (`AFME/AMERICA/ASPAC/EUROPE`) |
| `organization.national_organization` | fait si écrit | SEMANTIC_INTERPRETATION si déduit ; `attested_in_report` indique si le nom existe dans le rapport | — |
| `location.country_iso2` | — | SEMANTIC_INTERPRETATION (`NORM-ISO3166`) | — |
| `activity.activity_types[]`, `beneficiaries[].target_group` | — | SEMANTIC_INTERPRETATION | PROPOSED_STANDARD |
| `*.value` d'une métrique | fait / `unknown` / `calculated` | — | — |
| `*.normalization` | — | SEMANTIC_INTERPRETATION | PROPOSED_STANDARD (`metric_code`, `iaooi_class` IAOOI-v0) |
| `impact[].claim_raw` | fait (`statement_published`) | `attribution_level`, `measured` = SEMANTIC_INTERPRETATION | `impact_type` = PROPOSED_STANDARD |
| `sdgs[]` | libellé ODD OFFICIAL_JCI_FACT | déclaration JCI / locale ; `role` souvent `unknown` | — |
| `evidence[]` | contenu = fait | `attached` = SEMANTIC_INTERPRETATION (contrôle) | `type` = PROPOSED_STANDARD |
| `data_quality` | — | — | PROPOSED_STANDARD (structure) |

---

# E. TEST DATA — 5 PROJETS FICTIFS (V2, provenance par champ)

> ⚠ **Tous les éléments ci-dessous sont FICTIFS** (organisations, personnes, chiffres). Seuls les **codes de taxonomie** et les **libellés officiels** viennent du rapport. Chaque cas cible des pièges réellement observés dans le rapport (B.6) ou typiques d'une saisie locale.
> Le fichier `jci_tier1_fixtures_v2.json` contient ces 5 cas au format machine (`raw_input` → `expected`), avec provenance par champ.
> **Lecture des couches dans ces cas** : ce que dit l'organisation locale = **LOCAL_REPORTED_FACT** (jamais OFFICIAL_JCI_FACT, règle P9). Les libellés JCI réutilisés (JCI RISE, Community Impact, SDG 4…) = **OFFICIAL_JCI_FACT** avec leur page. Leur rattachement au projet = **SEMANTIC_INTERPRETATION**, sauf si l'organisation locale le déclare elle-même (« C'est un projet RISE » → LOCAL_REPORTED_FACT). Codes L3–L7 = **PROPOSED_STANDARD**.
> **geographic_area** : dans les 5 cas, elle est déduite du pays (`GEO-FROM-COUNTRY`, confiance M). Le rapport ne publie pas de liste pays → geographic_area (carte p. 9 = VDX-01).

## Matrice de couverture des pièges

| Piège | TC1 | TC2 | TC3 | TC4 | TC5 | Observé dans le rapport |
|---|---|---|---|---|---|---|
| Inscrits ≠ présents ≠ uniques | ● | | | | ● | I6, I14 |
| Valeurs approximatives (« environ », « around », « ~ », « + ») | ● | ● | | | ● | partout (« 1,000+ ») |
| Devise locale sans conversion | ● | ● | | ● | | p. 77 (MNT), p. 94 (AR$) |
| Terme hors vocabulaire JCI | ● (OLM) | | | | | « LOM » p. 82 |
| Nom de National Organization absent du rapport | | | ● (JCI Peru) | | | P0 |
| geographic_area sans liste officielle pays → Area | ● | ● | ● | ● | ● | VDX-01 |
| Date relative / format local | | ● | ● | ● | ● | I24 |
| Audience comm. ≠ bénéficiaires | | ● | | | | I8, M037–M048 |
| Estimation indirecte (foyers, population) | | ● | ● | | | M005–M007 |
| Heures ambiguës / calculées | | ● | ● | | | S2 |
| Pas d'AoO « environnement » | | | ● | | | A.2 |
| ODD sur-tagués / sans mapping AoO | | ● | ● | | | S7, I22 |
| Impact affirmé sans mesure | | | ● | | | M054, M079 |
| Bénéficiaires internes vs externes | | | | ● | | S6 |
| Outcome mesuré (pré/post) | | | | ● | | M091 (seul cas) |
| Outcome organisationnel (nouveaux membres) | | | | ● | | M111, M117 |
| Intention ≠ résultat | | | ● | ● | | p. 29 (cible 6 000) |
| Double déclaration (twinning) / multilingue | | | | | ● | R6 |

---

## TC1 — Entrepreneurial (FR, Côte d'Ivoire) — « Boost PME 2025 »

**Input brut**
```text
Bonjour à tous ! Voici le bilan de notre projet « Boost PME 2025 » 🎉
Du 12 au 14 juin, notre OLM a organisé 3 jours de formation au Centre culturel de Bouaké pour les jeunes entrepreneurs et les femmes commerçantes du grand marché. On a eu 64 inscrits et à peu près 50 présents chaque jour. Formateurs : 4 membres certifiés (dont 1 CNT) + un expert de notre banque partenaire. 12 bénévoles mobilisés, environ 150 heures au total. Budget : 1 200 000 FCFA dont 800 000 sponsorisés par une microfinance locale. À la fin, 38 participants ont présenté leur business plan, et 3 mois après, 9 ont obtenu un microcrédit et 2 ont formalisé leur entreprise (RCCM). C'est un projet RISE, pilier économie. ODD 1, 5, 8. On a les photos et la liste de présence.
— Secrétariat général, JCI Bouaké Lumière
```

**Données extraites**

| Champ | Valeur | Span source | Statut |
|---|---|---|---|
| Nom | Boost PME 2025 | « Boost PME 2025 » | LOCAL_REPORTED_FACT · extracted |
| LO | JCI Bouaké Lumière | signature | LOCAL_REPORTED_FACT · extracted |
| NO | JCI Côte d'Ivoire (nom attesté dans le rapport, p. 38) | — (déduit du pays) | SEMANTIC_INTERPRETATION |
| Dates | 2025-06-12 → 2025-06-14 | « Du 12 au 14 juin » + année de soumission | SEMANTIC_INTERPRETATION (normalisation) (année inférée) |
| Inscrits | 64 | « 64 inscrits » | LOCAL_REPORTED_FACT · extracted |
| Présence | ~50 / jour | « à peu près 50 présents chaque jour » | LOCAL_REPORTED_FACT · extracted (approx, par jour) |
| Formateurs | 4 membres certifiés (1 CNT) + 1 expert externe | « 4 membres certifiés (dont 1 CNT) + un expert » | LOCAL_REPORTED_FACT · extracted |
| Bénévoles / heures | 12 / ~150 h | « 12 bénévoles… environ 150 heures » | LOCAL_REPORTED_FACT · extracted |
| Budget / sponsoring | 1 200 000 XOF / 800 000 XOF | « 1 200 000 FCFA dont 800 000 » | SEMANTIC_INTERPRETATION (normalisation) (FCFA → XOF) |
| Business plans | 38 | « 38 participants ont présenté » | LOCAL_REPORTED_FACT · extracted |
| Microcrédits (+3 mois) | 9 | « 3 mois après, 9 ont obtenu un microcrédit » | LOCAL_REPORTED_FACT · extracted |
| Entreprises formalisées (+3 mois) | 2 | « 2 ont formalisé leur entreprise (RCCM) » | LOCAL_REPORTED_FACT · extracted |
| ODD | 1, 5, 8 | « ODD 1, 5, 8 » | LOCAL_REPORTED_FACT · extracted |

**Mapping taxonomique**

| Niveau | Valeur | Provenance |
|---|---|---|
| L1 area_of_opportunity | CI (défaut RISE) + BE (contenu) | SEMANTIC_INTERPRETATION (héritage du programme déclaré + contenu) |
| L2 Programme | JCI RISE → pilier « Sustaining and Rebuilding Economies » | programme : LOCAL_REPORTED_FACT (« C'est un projet RISE ») ; pilier : SEMANTIC_INTERPRETATION (« pilier économie » → libellé officiel p. 85) |
| L3 Activité | TRAINING_WORKSHOP | — |
| L4 Cibles | ENTREPRENEURS ; WOMEN_ENTREPRENEURS | — |
| L5 Outputs | REGISTRATIONS 64 ; ATTENDEES ~50/jour ; COMPLETIONS 38 | — |
| L6 Outcomes | ACCESS_TO_FINANCE_MARKETS 9 ; BUSINESS_CREATED 2 (horizon 3 mois) | — |
| L7 Impact | — | aucun claim |
| L8 ODD | 1, 5, 8 (tous dans le mapping CI) | LOCAL_REPORTED_FACT (déclaré) ; libellés ODD OFFICIAL_JCI_FACT |

**Données manquantes** : nombre de participants **uniques** ; répartition femmes/hommes et âges ; montant des microcrédits ; nom des partenaires ; conversion USD (à faire par le système avec un taux daté, jamais par le LLM) ; ODD principal ; pièces jointes (photos et liste citées mais non fournies).

**JSON normalisé V2** (provenance comptée automatiquement, puis objet complet)
| Couche | value_status | Nb d'enveloppes |
|---|---|---|
| OFFICIAL_JCI_FACT | extracted | 9 |
| LOCAL_REPORTED_FACT | extracted | 29 |
| LOCAL_REPORTED_FACT | unknown | 10 |
| SEMANTIC_INTERPRETATION | — | 41 |
| PROPOSED_STANDARD | — | 35 |

<details><summary>Objet JSON complet (identique à jci_tier1_fixtures_v2.json)</summary>

```json
{
  "project": {
    "project_id": {
      "value": "TC1",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:ID-SCHEME-v0"
    },
    "name": {
      "value": "Boost PME 2025",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC1",
        "quote": "« Boost PME 2025 »"
      }
    },
    "description": {
      "value": "3 jours de formation pour les jeunes entrepreneurs et les femmes commerçantes du grand marché",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC1",
        "quote": "3 jours de formation au Centre culturel de Bouaké pour les jeunes entrepreneurs et les femmes commerçantes du grand marché"
      }
    },
    "program": {
      "name": {
        "value": "JCI RISE",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "85",
          "section": "JCI RISE Projects",
          "quote": "JCI RISE (Rebuild, Invest, Sustain, Evolve) is JCI's flagship initiative"
        }
      },
      "code": {
        "value": "RISE",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "C'est un projet RISE"
        }
      },
      "components": [
        {
          "type": "rise_pillar",
          "value": {
            "value": "Sustaining and Rebuilding Economies",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "85",
              "section": "JCI RISE Projects",
              "quote": "Sustaining and Rebuilding Economies 40.30%"
            }
          },
          "assignment": {
            "value": true,
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "MAP-RISE-PILLAR",
            "basis": "local wording 'pilier économie' → official pillar label",
            "confidence": "H",
            "evidence": {
              "origin": "local_submission",
              "submission_id": "TC1",
              "quote": "pilier économie"
            }
          }
        }
      ]
    },
    "area_of_opportunity": [
      {
        "value": {
          "value": "Community Impact",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "25",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Community Impact"
          }
        },
        "code": {
          "value": "CI",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "INH-PROGRAM-AOO",
          "basis": "program JCI RISE ∈ Community Impact (p. 25)",
          "confidence": "H"
        }
      },
      {
        "value": {
          "value": "Business & Entrepreneurship",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "24",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Business & Entrepreneurship"
          }
        },
        "code": {
          "value": "BE",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-AOO-CONTENT",
          "basis": "entrepreneurship training, business plans, microcredit",
          "confidence": "M"
        }
      }
    ],
    "period": {
      "start": {
        "value": "2025-06-12",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE",
        "basis": "'Du 12 au 14 juin' + year of submission (2025)",
        "confidence": "M",
        "evidence": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "Du 12 au 14 juin"
        }
      },
      "end": {
        "value": "2025-06-14",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE",
        "basis": "same",
        "confidence": "M"
      },
      "duration": {
        "value": 3,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "day",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "3 jours de formation"
        }
      }
    },
    "recognition": []
  },
  "organization": {
    "local_organization": {
      "value": "JCI Bouaké Lumière",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC1",
        "quote": "— Secrétariat général, JCI Bouaké Lumière"
      }
    },
    "local_organization_term_raw": {
      "value": {
        "value": "OLM",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "notre OLM a organisé"
        }
      },
      "mapped_to": {
        "value": "Local Organization",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-TERM-LO",
        "basis": "'OLM' is NOT in the JCI report vocabulary (report uses 'Local Organization', 'LOM' p. 82)",
        "confidence": "M"
      }
    },
    "national_organization": {
      "value": "JCI Côte d'Ivoire",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NO-FROM-COUNTRY",
      "basis": "city Bouaké → country Côte d'Ivoire",
      "confidence": "M",
      "attested_in_report": {
        "value": true,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "38",
          "section": "JIB Impact Stories",
          "quote": "JCI Côte d'Ivoire"
        }
      }
    },
    "geographic_area": {
      "value": {
        "value": "Africa and the Middle East",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "9",
          "section": "International Presence – Operational Areas",
          "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
        }
      },
      "code": {
        "value": "AFME",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "GEO-FROM-COUNTRY",
        "basis": "Côte d'Ivoire → Africa and the Middle East: general knowledge; the report does not publish a country→geographic_area list (map p. 9 = VDX-01)",
        "confidence": "M"
      }
    },
    "partner_organizations": [
      {
        "type": {
          "value": "bank",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'notre banque partenaire'",
          "confidence": "H"
        },
        "name": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC1"
          }
        },
        "contribution": {
          "value": "expert trainer",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'un expert de notre banque partenaire'",
          "confidence": "H"
        }
      },
      {
        "type": {
          "value": "microfinance institution",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'une microfinance locale'",
          "confidence": "H"
        },
        "name": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC1"
          }
        },
        "contribution": {
          "value": "cash sponsorship",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'sponsorisés'",
          "confidence": "H"
        }
      }
    ],
    "lead_contact": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC1"
        }
      },
      "role": {
        "value": "Secrétariat général",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "Secrétariat général"
        }
      }
    }
  },
  "location": {
    "country": {
      "value": "Côte d'Ivoire",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "GEO-FROM-CITY",
      "basis": "Bouaké",
      "confidence": "H"
    },
    "country_iso2": {
      "value": "CI",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NORM-ISO3166",
      "basis": "country → ISO",
      "confidence": "H"
    },
    "city": {
      "value": "Bouaké",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC1",
        "quote": "Centre culturel de Bouaké"
      }
    },
    "venue": {
      "value": "Centre culturel de Bouaké",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC1",
        "quote": "Centre culturel de Bouaké"
      }
    },
    "scope": {
      "value": "local",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-SCOPE",
      "basis": "single city",
      "confidence": "H"
    }
  },
  "activity": {
    "activity_types": [
      {
        "code": {
          "value": "TRAINING_WORKSHOP",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "'formation'",
          "confidence": "H"
        }
      }
    ],
    "delivery_mode": {
      "value": "in_person",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-DELIVERY",
      "basis": "venue named",
      "confidence": "H"
    },
    "resources": [
      {
        "label_raw": "4 membres certifiés (dont 1 CNT)",
        "value": {
          "value": 4,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "4 membres certifiés (dont 1 CNT)"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "TRAINERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "trainers",
          "confidence": "H"
        },
        "certification": {
          "value": [
            "CNT"
          ],
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-CERT",
          "basis": "CNT = Certified National Trainer (inferred from p. 106 'Certified National and Area Trainers')",
          "confidence": "M"
        }
      },
      {
        "label_raw": "un expert de notre banque partenaire",
        "value": {
          "value": 1,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "un expert de notre banque partenaire"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "TRAINERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "external expert",
          "confidence": "H"
        }
      },
      {
        "label_raw": "12 bénévoles mobilisés",
        "value": {
          "value": 12,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "12 bénévoles mobilisés"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "volunteers",
          "confidence": "H"
        }
      },
      {
        "label_raw": "environ 150 heures au total",
        "value": {
          "value": 150,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "approx",
          "unit": "hour",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "environ 150 heures au total"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEER_HOURS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "total hours stated",
          "confidence": "H"
        }
      },
      {
        "label_raw": "Budget : 1 200 000 FCFA",
        "value": {
          "value": 1200000,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "XOF",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "Budget : 1 200 000 FCFA"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "BUDGET_TOTAL",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "money",
          "confidence": "H"
        },
        "amount_usd": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "no rate given; conversion must be system-side with a dated rate",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC1"
          }
        }
      },
      {
        "label_raw": "800 000 sponsorisés par une microfinance locale",
        "value": {
          "value": 800000,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "XOF",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "dont 800 000 sponsorisés par une microfinance locale"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "SPONSORSHIP_CASH",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "money",
          "confidence": "H"
        }
      }
    ]
  },
  "beneficiaries": [
    {
      "target_group": {
        "code": {
          "value": "ENTREPRENEURS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'jeunes entrepreneurs'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "jeunes entrepreneurs",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "pour les jeunes entrepreneurs"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "public beneficiaries",
        "confidence": "H"
      },
      "count": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC1"
        },
        "unit": "person"
      }
    },
    {
      "target_group": {
        "code": {
          "value": "WOMEN_ENTREPRENEURS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'femmes commerçantes'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "femmes commerçantes du grand marché",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "les femmes commerçantes du grand marché"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "public beneficiaries",
        "confidence": "H"
      },
      "count": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC1"
        },
        "unit": "person"
      }
    }
  ],
  "outputs": [
    {
      "label_raw": "64 inscrits",
      "value": {
        "value": 64,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "On a eu 64 inscrits"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "REGISTRATIONS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "registrations",
        "confidence": "H"
      }
    },
    {
      "label_raw": "à peu près 50 présents chaque jour",
      "value": {
        "value": 50,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "approx",
        "unit": "person_per_day",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "à peu près 50 présents chaque jour"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "ATTENDEES",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "daily attendance; NOT unique people; never sum across days",
        "confidence": "H"
      }
    },
    {
      "label_raw": null,
      "value": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC1"
        },
        "unit": "person"
      },
      "normalization": {
        "metric_code": {
          "value": "PARTICIPANTS_UNIQUE",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "expected field, not reported",
        "confidence": "H"
      }
    },
    {
      "label_raw": "38 participants ont présenté leur business plan",
      "value": {
        "value": 38,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "38 participants ont présenté leur business plan"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "COMPLETIONS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "business plan presented",
        "confidence": "H"
      }
    }
  ],
  "outcomes": [
    {
      "label_raw": "9 ont obtenu un microcrédit",
      "value": {
        "value": 9,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "3 mois après, 9 ont obtenu un microcrédit"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "ACCESS_TO_FINANCE_MARKETS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "change for beneficiaries",
        "confidence": "H"
      },
      "measurement": {
        "method": {
          "value": "self_reported_follow_up",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METHOD",
          "basis": "no instrument named",
          "confidence": "M"
        },
        "horizon": {
          "value": "3 mois",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "3 mois après"
          }
        }
      }
    },
    {
      "label_raw": "2 ont formalisé leur entreprise (RCCM)",
      "value": {
        "value": 2,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "business",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "2 ont formalisé leur entreprise (RCCM)"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "BUSINESS_CREATED",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "business formalization",
        "confidence": "H"
      },
      "measurement": {
        "method": {
          "value": "self_reported_follow_up",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METHOD",
          "basis": "RCCM mentioned but no document attached",
          "confidence": "M"
        },
        "horizon": {
          "value": "3 mois",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC1",
            "quote": "3 mois après"
          }
        }
      }
    }
  ],
  "impact": [],
  "sdgs": [
    {
      "sdg": 1,
      "label": {
        "value": "No Poverty",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 1: No Poverty"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "ODD 1, 5, 8"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 5,
      "label": {
        "value": "Gender equality",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 5: Gender equality"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "ODD 1, 5, 8"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "ID",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 8,
      "label": {
        "value": "Decent Work and Economic Growth",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 8: Decent Work and Economic Growth"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "ODD 1, 5, 8"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "BE",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    }
  ],
  "evidence": [
    {
      "type": {
        "value": "photos",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "declared": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "On a les photos"
        }
      },
      "attached": {
        "value": false,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "EVIDENCE-CHECK",
        "basis": "no file received",
        "confidence": "H"
      }
    },
    {
      "type": {
        "value": "attendance_list",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "declared": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC1",
          "quote": "la liste de présence"
        }
      },
      "attached": {
        "value": false,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "EVIDENCE-CHECK",
        "basis": "no file received",
        "confidence": "H"
      }
    }
  ],
  "data_quality": {
    "record_origin": "local_submission",
    "verification": {
      "value": "none",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:STATUS-v0"
    },
    "conflict_refs": [],
    "visual_refs": [],
    "unknowns": [
      "outputs[PARTICIPANTS_UNIQUE]",
      "beneficiaries[*].count",
      "resources[BUDGET_TOTAL].amount_usd",
      "partner names",
      "sdgs[*].role",
      "evidence files"
    ],
    "warnings": [
      "'OLM' outside JCI report vocabulary",
      "geographic_area inferred without a published country list (VDX-01)",
      "year of dates inferred from submission date"
    ]
  }
}
```

</details>

---

## TC2 — Social (EN, Philippines) — « Kalinga Kits »

**Input brut**
```text
Hi team! Last Saturday our chapter did 'Kalinga Kits' – we packed and handed out 320 hygiene kits + school supplies to kids in 2 barangays hit by the flooding. Around 1,500 people benefited (families of the kids). 27 members + 15 non-member volunteers, 6 hrs. Partnered with the City Social Welfare office and a local pharmacy donated meds worth PHP 45,000. Posted on FB, 12k reach!!! SDG 1, 3, 4, 11, 13 💙
— JCI Iloilo Kahayag
```

**Données extraites**

| Champ | Valeur | Span source | Statut |
|---|---|---|---|
| Date | 2025-08-02 | « Last Saturday » (soumis le 2025-08-04) | SEMANTIC_INTERPRETATION |
| Kits distribués | 320 | « 320 hygiene kits + school supplies » | LOCAL_REPORTED_FACT · extracted |
| Enfants atteints | — | non dit (320 ≠ nombre d'enfants garanti) | `unknown` |
| Personnes « bénéficiaires » | ~1 500 (indirect) | « Around 1,500 people benefited (families of the kids) » | LOCAL_REPORTED_FACT · extracted (approx ; estimation de la source) |
| Bénévoles | 27 membres + 15 non-membres | « 27 members + 15 non-member volunteers » | LOCAL_REPORTED_FACT · extracted |
| Heures | ambigu | « 6 hrs » | `unknown` (ambigu) |
| Don en nature | 45 000 PHP | « meds worth PHP 45,000 » | LOCAL_REPORTED_FACT · extracted |
| Portée FB | ~12 000 | « 12k reach » | LOCAL_REPORTED_FACT · extracted (audience comm.) |
| ODD | 1, 3, 4, 11, 13 | « SDG 1, 3, 4, 11, 13 » | LOCAL_REPORTED_FACT · extracted |

**Mapping taxonomique** : L1 CI · L2 COMMUNITY_DEV · L3 COMMUNITY_SERVICE · L4 CHILDREN, VULNERABLE_COMMUNITIES · L5 ITEMS_DISTRIBUTED 320, PEOPLE_REACHED_INDIRECT ~1 500, COMM_AUDIENCE 12k (**exclu des totaux**) · L6 — · L7 — · L8 1, 3, 4, 11, 13 (13 marqué `weak_textual_support`).

**Données manquantes** : date absolue ; noms des barangays ; nombre d'enfants ; méthode du « 1 500 » ; heures bénévoles totales ; ODD principal.

**JSON normalisé V2** (provenance comptée automatiquement, puis objet complet)
| Couche | value_status | Nb d'enveloppes |
|---|---|---|
| OFFICIAL_JCI_FACT | extracted | 9 |
| LOCAL_REPORTED_FACT | extracted | 22 |
| LOCAL_REPORTED_FACT | unknown | 11 |
| SEMANTIC_INTERPRETATION | — | 35 |
| PROPOSED_STANDARD | — | 25 |

<details><summary>Objet JSON complet (identique à jci_tier1_fixtures_v2.json)</summary>

```json
{
  "project": {
    "project_id": {
      "value": "TC2",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:ID-SCHEME-v0"
    },
    "name": {
      "value": "Kalinga Kits",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC2",
        "quote": "our chapter did 'Kalinga Kits'"
      }
    },
    "description": {
      "value": "packed and handed out 320 hygiene kits + school supplies to kids in 2 barangays hit by the flooding",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC2",
        "quote": "we packed and handed out 320 hygiene kits + school supplies to kids in 2 barangays hit by the flooding"
      }
    },
    "program": {
      "name": {
        "value": "Community Development Projects",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "84",
          "section": "Community Development Projects",
          "quote": "Community Development Projects are at the heart of JCI's mission"
        }
      },
      "code": {
        "value": "COMMUNITY_DEV",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-PROGRAM",
        "basis": "no program named; local community service → Community Development Projects",
        "confidence": "M"
      }
    },
    "area_of_opportunity": [
      {
        "value": {
          "value": "Community Impact",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "25",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Community Impact"
          }
        },
        "code": {
          "value": "CI",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-AOO-CONTENT",
          "basis": "direct community relief",
          "confidence": "H"
        }
      }
    ],
    "period": {
      "start": {
        "value": "2025-08-02",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-RELATIVE",
        "basis": "'Last Saturday' resolved against submission date 2025-08-04",
        "confidence": "M",
        "evidence": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "Last Saturday"
        }
      },
      "end": {
        "value": "2025-08-02",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-RELATIVE",
        "basis": "same",
        "confidence": "M"
      },
      "duration": {
        "value": 6,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "hour",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "6 hrs"
        },
        "ambiguity": "event duration or hours per volunteer"
      }
    },
    "recognition": []
  },
  "organization": {
    "local_organization": {
      "value": "JCI Iloilo Kahayag",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC2",
        "quote": "— JCI Iloilo Kahayag"
      }
    },
    "local_organization_term_raw": {
      "value": {
        "value": "chapter",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "our chapter"
        }
      },
      "mapped_to": {
        "value": "Local Organization",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-TERM-LO",
        "basis": "'local chapter' is a report variant (p. 21, 82)",
        "confidence": "H"
      }
    },
    "national_organization": {
      "value": "JCI Philippines",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NO-FROM-COUNTRY",
      "basis": "LO name contains 'Iloilo' → Philippines",
      "confidence": "M",
      "attested_in_report": {
        "value": true,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "6",
          "section": "2025 Board of Directors",
          "quote": "JCI PHILIPPINES"
        }
      }
    },
    "geographic_area": {
      "value": {
        "value": "Asia and the Pacific",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "9",
          "section": "International Presence – Operational Areas",
          "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
        }
      },
      "code": {
        "value": "ASPAC",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "GEO-FROM-COUNTRY",
        "basis": "Philippines → Asia and the Pacific: general knowledge; the report does not publish a country→geographic_area list (map p. 9 = VDX-01)",
        "confidence": "M"
      }
    },
    "partner_organizations": [
      {
        "type": {
          "value": "local government",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'City Social Welfare office'",
          "confidence": "H"
        },
        "name": {
          "value": "City Social Welfare office",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC2",
            "quote": "Partnered with the City Social Welfare office"
          }
        },
        "contribution": {
          "value": "co-implementation",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'Partnered with'",
          "confidence": "M"
        }
      },
      {
        "type": {
          "value": "pharmacy",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'a local pharmacy'",
          "confidence": "H"
        },
        "name": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC2"
          }
        },
        "contribution": {
          "value": "in-kind medicines",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'donated meds'",
          "confidence": "H"
        }
      }
    ],
    "lead_contact": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC2"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC2"
        }
      }
    }
  },
  "location": {
    "country": {
      "value": "Philippines",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "GEO-FROM-TERM",
      "basis": "'barangays' + 'Iloilo' in LO name",
      "confidence": "H"
    },
    "country_iso2": {
      "value": "PH",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NORM-ISO3166",
      "basis": "country → ISO",
      "confidence": "H"
    },
    "city": {
      "value": "Iloilo",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "GEO-FROM-LO-NAME",
      "basis": "LO name only; the text does not name the city",
      "confidence": "L"
    },
    "venue": {
      "value": "2 barangays",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC2",
        "quote": "kids in 2 barangays"
      }
    },
    "scope": {
      "value": "local",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-SCOPE",
      "basis": "2 barangays",
      "confidence": "H"
    }
  },
  "activity": {
    "activity_types": [
      {
        "code": {
          "value": "COMMUNITY_SERVICE",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "distribution of kits",
          "confidence": "H"
        }
      }
    ],
    "delivery_mode": {
      "value": "in_person",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-DELIVERY",
      "basis": "physical distribution",
      "confidence": "H"
    },
    "resources": [
      {
        "label_raw": "27 members",
        "value": {
          "value": 27,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC2",
            "quote": "27 members"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "member volunteers",
          "confidence": "H"
        },
        "member": true
      },
      {
        "label_raw": "15 non-member volunteers",
        "value": {
          "value": 15,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC2",
            "quote": "15 non-member volunteers"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "non-member volunteers",
          "confidence": "H"
        },
        "member": false
      },
      {
        "label_raw": "6 hrs",
        "value": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "ambiguous: event duration or per volunteer; total not stated",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC2"
          },
          "unit": "hour"
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEER_HOURS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "252 h would require assuming 6 h per volunteer — not stored",
          "confidence": "H"
        }
      },
      {
        "label_raw": "meds worth PHP 45,000",
        "value": {
          "value": 45000,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "PHP",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC2",
            "quote": "donated meds worth PHP 45,000"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "IN_KIND",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "in-kind donation",
          "confidence": "H"
        }
      }
    ]
  },
  "beneficiaries": [
    {
      "target_group": {
        "code": {
          "value": "CHILDREN",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'kids'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "kids in 2 barangays hit by the flooding",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "to kids in 2 barangays hit by the flooding"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "community",
        "confidence": "H"
      },
      "count": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "kits per child not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC2"
        },
        "unit": "person"
      }
    },
    {
      "target_group": {
        "code": {
          "value": "VULNERABLE_COMMUNITIES",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "flood-affected families",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "families of the kids",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "(families of the kids)"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "community",
        "confidence": "H"
      },
      "count": {
        "value": 1500,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "approx",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "Around 1,500 people benefited"
        },
        "source_self_estimate": true
      }
    }
  ],
  "outputs": [
    {
      "label_raw": "320 hygiene kits + school supplies",
      "value": {
        "value": 320,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "kit",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "320 hygiene kits + school supplies"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "ITEMS_DISTRIBUTED",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "items handed out",
        "confidence": "H"
      }
    },
    {
      "label_raw": null,
      "value": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "number of children not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC2"
        },
        "unit": "person"
      },
      "normalization": {
        "metric_code": {
          "value": "PEOPLE_REACHED_DIRECT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "expected field",
        "confidence": "H"
      }
    },
    {
      "label_raw": "Around 1,500 people benefited",
      "value": {
        "value": 1500,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "approx",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "Around 1,500 people benefited (families of the kids)"
        },
        "source_self_estimate": true
      },
      "normalization": {
        "metric_code": {
          "value": "PEOPLE_REACHED_INDIRECT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "households of direct beneficiaries = indirect",
        "confidence": "M"
      }
    },
    {
      "label_raw": "Posted on FB, 12k reach",
      "value": {
        "value": 12000,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "approx",
        "unit": "reach",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "Posted on FB, 12k reach"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "COMM_AUDIENCE",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "communication audience; excluded from beneficiary totals (P12)",
        "confidence": "H"
      }
    }
  ],
  "outcomes": [],
  "impact": [],
  "sdgs": [
    {
      "sdg": 1,
      "label": {
        "value": "No Poverty",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 1: No Poverty"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "SDG 1, 3, 4, 11, 13"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 3,
      "label": {
        "value": "Good Health and Well-being",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 3: Good Health and Well-being"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "SDG 1, 3, 4, 11, 13"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 4,
      "label": {
        "value": "Quality Education",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 4: Quality Education"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "SDG 1, 3, 4, 11, 13"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "ID",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 11,
      "label": {
        "value": "Sustainable Cities and Communities",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 11: Sustainable Cities and Communities"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "SDG 1, 3, 4, 11, 13"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 13,
      "label": {
        "value": "Climate Action",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 13: Climate Action"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "SDG 1, 3, 4, 11, 13"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": [
        "weak_textual_support"
      ]
    }
  ],
  "evidence": [
    {
      "type": {
        "value": "social_media_post",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "declared": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC2",
          "quote": "Posted on FB"
        }
      },
      "attached": {
        "value": false,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "EVIDENCE-CHECK",
        "basis": "no link received",
        "confidence": "H"
      }
    }
  ],
  "data_quality": {
    "record_origin": "local_submission",
    "verification": {
      "value": "none",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:STATUS-v0"
    },
    "conflict_refs": [],
    "visual_refs": [],
    "unknowns": [
      "outputs[PEOPLE_REACHED_DIRECT]",
      "resources[VOLUNTEER_HOURS]",
      "barangay names",
      "estimation method for 1,500",
      "sdgs[*].role"
    ],
    "warnings": [
      "date resolved from a relative expression",
      "city inferred from LO name only (L)"
    ]
  }
}
```

</details>

---

## TC3 — Environnemental (ES, Pérou) — « Río Limpio Chili »

**Input brut**
```text
Proyecto «Río Limpio Chili»: jornada de limpieza del río el 22/03/2025 (Día Mundial del Agua). Participaron 85 voluntarios (40 miembros JCI y 45 estudiantes de la universidad). Recolectamos 1,2 toneladas de residuos, de los cuales 300 kg reciclables fueron entregados a una asociación de recicladores. Además plantamos 150 árboles nativos (queñuas) con la Municipalidad. Duración: 5 horas. ¡Queremos repetirlo cada trimestre! Impacto: un río más limpio para los 50 000 habitantes de la zona. ODS 6, 13, 14, 15.
— JCI Arequipa Misti Verde
```

**Données extraites**

| Champ | Valeur | Span source | Statut |
|---|---|---|---|
| Date | 2025-03-22 | « 22/03/2025 » | SEMANTIC_INTERPRETATION (normalisation) (DD/MM) |
| Bénévoles | 85 = 40 membres + 45 étudiants | « 85 voluntarios (40 miembros JCI y 45 estudiantes) » | LOCAL_REPORTED_FACT · extracted |
| Durée | 5 h | « Duración: 5 horas » | LOCAL_REPORTED_FACT · extracted |
| Heures bénévoles | 425 h | 85 × 5 | SEMANTIC_INTERPRETATION · calculated (hypothèse) |
| Déchets collectés | 1 200 kg | « 1,2 toneladas » | SEMANTIC_INTERPRETATION (normalisation) (virgule décimale, t → kg) |
| Recyclables remis | 300 kg | « 300 kg reciclables » | LOCAL_REPORTED_FACT · extracted |
| Arbres plantés | 150 (queñuas) | « 150 árboles nativos (queñuas) » | LOCAL_REPORTED_FACT · extracted |
| « Impact » | 50 000 habitants | « un río más limpio para los 50 000 habitantes » | LOCAL_REPORTED_FACT (affirmation d'impact, ≠ bénéficiaires) |
| Récurrence | trimestrielle | « Queremos repetirlo cada trimestre » | LOCAL_REPORTED_FACT (intention, pas un résultat) |
| ODD | 6, 13, 14, 15 | « ODS 6, 13, 14, 15 » | LOCAL_REPORTED_FACT · extracted |

**Mapping taxonomique** : L1 area_of_opportunity **CI** (pas d'area_of_opportunity environnement, C.1) · L2 LOCAL_PROJECT · L3 ENVIRONMENTAL_ACTION · L4 GENERAL_PUBLIC (compte nul) · L5 PHYSICAL_OUTPUT ×3 · L6 — (survie des arbres inconnue) · L7 ENVIRONMENTAL (`narrative_only`) · L8 6, 13, 14, 15. **Seul 13 est dans le mapping CI** ; 14 est signalé `questionable_relevance`.

**Données manquantes** : nom « JCI Peru » **non attesté** dans le rapport (la National Organization reste une interprétation sans appui officiel) ; preuves (photos, pesée) ; taux de survie des arbres ; nom de l'association de recyclage ; ODD principal ; heures réelles par bénévole.

**JSON normalisé V2** (provenance comptée automatiquement, puis objet complet)
| Couche | value_status | Nb d'enveloppes |
|---|---|---|
| OFFICIAL_JCI_FACT | extracted | 6 |
| OFFICIAL_JCI_FACT | unknown | 1 |
| LOCAL_REPORTED_FACT | extracted | 19 |
| LOCAL_REPORTED_FACT | unknown | 10 |
| SEMANTIC_INTERPRETATION | calculated | 2 |
| SEMANTIC_INTERPRETATION | — | 33 |
| PROPOSED_STANDARD | — | 24 |

<details><summary>Objet JSON complet (identique à jci_tier1_fixtures_v2.json)</summary>

```json
{
  "project": {
    "project_id": {
      "value": "TC3",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:ID-SCHEME-v0"
    },
    "name": {
      "value": "Río Limpio Chili",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC3",
        "quote": "Proyecto «Río Limpio Chili»"
      }
    },
    "description": {
      "value": "jornada de limpieza del río",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC3",
        "quote": "jornada de limpieza del río el 22/03/2025 (Día Mundial del Agua)"
      }
    },
    "program": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "no JCI program named",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC3"
        }
      },
      "code": {
        "value": "LOCAL_PROJECT",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-PROGRAM",
        "basis": "no program named → LOCAL_PROJECT (not a JCI program)",
        "confidence": "H"
      }
    },
    "area_of_opportunity": [
      {
        "value": {
          "value": "Community Impact",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "25",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Community Impact"
          }
        },
        "code": {
          "value": "CI",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-AOO-ENV",
          "basis": "no environmental Area of Opportunity exists; CI carries SDG 12/13 (p. 25)",
          "confidence": "H"
        }
      }
    ],
    "period": {
      "start": {
        "value": "2025-03-22",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-DMY",
        "basis": "'22/03/2025' read as DD/MM/YYYY",
        "confidence": "H",
        "evidence": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "22/03/2025"
        }
      },
      "end": {
        "value": "2025-03-22",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-DMY",
        "basis": "single day",
        "confidence": "H"
      },
      "duration": {
        "value": 5,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "hour",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "Duración: 5 horas"
        }
      }
    },
    "recognition": [],
    "planned_recurrence": {
      "value": {
        "value": "cada trimestre",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "¡Queremos repetirlo cada trimestre!"
        }
      },
      "status": {
        "value": "intention",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:STATUS-v0"
      }
    }
  },
  "organization": {
    "local_organization": {
      "value": "JCI Arequipa Misti Verde",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC3",
        "quote": "— JCI Arequipa Misti Verde"
      }
    },
    "national_organization": {
      "value": "JCI Peru",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NO-FROM-COUNTRY",
      "basis": "city Arequipa → Peru",
      "confidence": "M",
      "attested_in_report": {
        "value": null,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "unknown",
        "reason": "NO name not found in the report",
        "source": {
          "origin": "jci_report_2025",
          "searched_scope": "full text"
        }
      }
    },
    "geographic_area": {
      "value": {
        "value": "America",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "9",
          "section": "International Presence – Operational Areas",
          "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
        }
      },
      "code": {
        "value": "AMERICA",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "GEO-FROM-COUNTRY",
        "basis": "Peru → America: general knowledge; the report does not publish a country→geographic_area list (map p. 9 = VDX-01)",
        "confidence": "M"
      }
    },
    "partner_organizations": [
      {
        "type": {
          "value": "local government",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'la Municipalidad'",
          "confidence": "H"
        },
        "name": {
          "value": "Municipalidad",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC3",
            "quote": "con la Municipalidad"
          }
        },
        "contribution": {
          "value": "tree planting",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'plantamos… con la Municipalidad'",
          "confidence": "H"
        }
      },
      {
        "type": {
          "value": "recyclers association",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'asociación de recicladores'",
          "confidence": "H"
        },
        "name": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC3"
          }
        },
        "contribution": {
          "value": "recyclables recipient",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'entregados a'",
          "confidence": "H"
        }
      },
      {
        "type": {
          "value": "university",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "'estudiantes de la universidad'",
          "confidence": "H"
        },
        "name": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC3"
          }
        },
        "contribution": {
          "value": "student volunteers",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-PARTNER",
          "basis": "students volunteered",
          "confidence": "H"
        }
      }
    ],
    "lead_contact": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC3"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC3"
        }
      }
    }
  },
  "location": {
    "country": {
      "value": "Peru",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "GEO-FROM-CITY",
      "basis": "Arequipa / río Chili",
      "confidence": "H"
    },
    "country_iso2": {
      "value": "PE",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NORM-ISO3166",
      "basis": "country → ISO",
      "confidence": "H"
    },
    "city": {
      "value": "Arequipa",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "GEO-FROM-LO-NAME",
      "basis": "LO name",
      "confidence": "M"
    },
    "venue": {
      "value": "río Chili",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC3",
        "quote": "«Río Limpio Chili»"
      }
    },
    "scope": {
      "value": "local",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-SCOPE",
      "basis": "single site",
      "confidence": "H"
    }
  },
  "activity": {
    "activity_types": [
      {
        "code": {
          "value": "ENVIRONMENTAL_ACTION",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "clean-up + tree planting",
          "confidence": "H"
        }
      }
    ],
    "delivery_mode": {
      "value": "in_person",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-DELIVERY",
      "basis": "field action",
      "confidence": "H"
    },
    "resources": [
      {
        "label_raw": "40 miembros JCI",
        "value": {
          "value": 40,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC3",
            "quote": "40 miembros JCI"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "member volunteers",
          "confidence": "H"
        },
        "member": true
      },
      {
        "label_raw": "45 estudiantes de la universidad",
        "value": {
          "value": 45,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC3",
            "quote": "45 estudiantes de la universidad"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "students are volunteers here, not beneficiaries",
          "confidence": "H"
        },
        "member": false
      },
      {
        "label_raw": null,
        "value": {
          "value": 425,
          "layer": "SEMANTIC_INTERPRETATION",
          "value_status": "calculated",
          "formula": "85 volunteers × 5 h",
          "inputs": [
            {
              "origin": "local_submission",
              "submission_id": "TC3",
              "quote": "Participaron 85 voluntarios"
            },
            {
              "origin": "local_submission",
              "submission_id": "TC3",
              "quote": "Duración: 5 horas"
            }
          ],
          "rule_id": "CALC-ARITH",
          "confidence": "H",
          "unit": "hour",
          "assumptions": [
            "every volunteer stayed the full 5 hours"
          ]
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEER_HOURS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "calculated under an assumption; needs validation",
          "confidence": "M"
        }
      }
    ]
  },
  "beneficiaries": [
    {
      "target_group": {
        "code": {
          "value": "GENERAL_PUBLIC",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'habitantes de la zona'",
          "confidence": "M"
        }
      },
      "label_raw": {
        "value": "habitantes de la zona",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "los 50 000 habitantes de la zona"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "residents",
        "confidence": "H"
      },
      "count": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "50,000 is the area population cited as impact, not a beneficiary count",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC3"
        },
        "unit": "person"
      }
    }
  ],
  "outputs": [
    {
      "label_raw": "1,2 toneladas de residuos",
      "value": {
        "value": 1200,
        "layer": "SEMANTIC_INTERPRETATION",
        "value_status": "calculated",
        "formula": "1,2 t × 1000 (decimal comma)",
        "inputs": [
          {
            "origin": "local_submission",
            "submission_id": "TC3",
            "quote": "Recolectamos 1,2 toneladas de residuos"
          }
        ],
        "rule_id": "CALC-ARITH",
        "confidence": "H",
        "unit": "kg",
        "raw_value": {
          "value": "1,2 toneladas",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC3",
            "quote": "1,2 toneladas"
          }
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PHYSICAL_OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "waste collected",
        "confidence": "H"
      },
      "sub_code": {
        "value": "waste_collected",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      }
    },
    {
      "label_raw": "300 kg reciclables",
      "value": {
        "value": 300,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "kg",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "300 kg reciclables fueron entregados a una asociación de recicladores"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PHYSICAL_OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "recyclables diverted",
        "confidence": "H"
      },
      "sub_code": {
        "value": "recyclables_diverted",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      }
    },
    {
      "label_raw": "150 árboles nativos (queñuas)",
      "value": {
        "value": 150,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "tree",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "plantamos 150 árboles nativos (queñuas)"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PHYSICAL_OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "trees planted; survival unknown",
        "confidence": "H"
      },
      "sub_code": {
        "value": "trees_planted",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      }
    }
  ],
  "outcomes": [],
  "impact": [
    {
      "claim_raw": {
        "value": "un río más limpio para los 50 000 habitantes de la zona",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "Impacto: un río más limpio para los 50 000 habitantes de la zona"
        }
      },
      "impact_type": {
        "code": {
          "value": "ENVIRONMENTAL",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-IMPACT-CLAIM",
          "basis": "river cleanliness",
          "confidence": "H"
        }
      },
      "attribution_level": {
        "value": "narrative_only",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "IMPACT-ATTRIBUTION",
        "basis": "no water-quality measurement",
        "confidence": "H"
      },
      "measured": {
        "value": false,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "IMPACT-ATTRIBUTION",
        "basis": "no indicator",
        "confidence": "H"
      },
      "affected_population_claimed": {
        "value": 50000,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "los 50 000 habitantes de la zona"
        }
      }
    }
  ],
  "sdgs": [
    {
      "sdg": 6,
      "label": {
        "value": "Clean Water & Sanitation",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "57",
          "section": "SDG label as printed",
          "quote": "SDG 6 (Clean Water & Sanitation)"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "ODS 6, 13, 14, 15"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 13,
      "label": {
        "value": "Climate Action",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 13: Climate Action"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "ODS 6, 13, 14, 15"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 14,
      "label": {
        "value": "Life Below Water",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "89",
          "section": "SDG label as printed",
          "quote": "SDG 14: Life Below Water"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "ODS 6, 13, 14, 15"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": [
        "questionable_relevance"
      ]
    },
    {
      "sdg": 15,
      "label": {
        "value": "Life on Land",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "32",
          "section": "SDG label as printed",
          "quote": "SDG 15: Life on Land"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC3",
          "quote": "ODS 6, 13, 14, 15"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    }
  ],
  "evidence": [],
  "data_quality": {
    "record_origin": "local_submission",
    "verification": {
      "value": "none",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:STATUS-v0"
    },
    "conflict_refs": [],
    "visual_refs": [],
    "unknowns": [
      "evidence",
      "tree survival",
      "recyclers association name",
      "sdgs[*].role",
      "beneficiaries.count"
    ],
    "warnings": [
      "'JCI Peru' not attested in the report",
      "volunteer hours calculated under an assumption",
      "SDGs 6, 14, 15 have no default area_of_opportunity (p. 24–25)"
    ]
  }
}
```

</details>

---

## TC4 — Leadership / formation (EN, Allemagne) — « Q2 Training Academy »

**Input brut**
```text
Q2 Training Academy – wrap-up
4 modules (Effective Communication, Project Management, Präsentieren/Presenting, Leadership Basics), Saturdays in April–May. 22 participants (18 members, 4 guests -> 3 of them joined JCI afterwards!). Trainers: 2 CATs from JCI Germany + our local trainer. Pre/post self-assessment: avg confidence speaking in public went from 2.9 to 4.1 (scale 1–5), 20/22 filled the post survey. 2 participants will compete at the national Public Speaking Competition. Costs: €640 room + €180 materials, covered by member fees. SDG 4.
— VP Training, JCI Rheinaue
```

**Données extraites**

| Champ | Valeur | Span source | Statut |
|---|---|---|---|
| Période | 2025-04 → 2025-05 | « Saturdays in April–May » | SEMANTIC_INTERPRETATION (normalisation) (mois) |
| Modules | 4 | « 4 modules (…) » | LOCAL_REPORTED_FACT · extracted |
| Participants | 22 = 18 membres + 4 invités | « 22 participants (18 members, 4 guests » | LOCAL_REPORTED_FACT · extracted |
| Nouveaux membres | 3 | « 3 of them joined JCI afterwards » | LOCAL_REPORTED_FACT · extracted |
| Formateurs | 2 CAT + 1 formateur local | « 2 CATs from JCI Germany + our local trainer » | LOCAL_REPORTED_FACT · extracted |
| Confiance pré → post | 2,9 → 4,1 (échelle 1–5) ; Δ = +1,2 | « from 2.9 to 4.1 (scale 1–5) » | LOCAL_REPORTED_FACT · extracted ; Δ = SEMANTIC_INTERPRETATION · calculated |
| Réponses post | 20 / 22 | « 20/22 filled the post survey » | LOCAL_REPORTED_FACT · extracted |
| Coûts | 640 € + 180 € = 820 € (cotisations) | « €640 room + €180 materials » | LOCAL_REPORTED_FACT · extracted ; total = SEMANTIC_INTERPRETATION · calculated |
| Compétition | 2 participants | « will compete » | LOCAL_REPORTED_FACT (intention, pas un résultat) |
| ODD | 4 | « SDG 4 » | LOCAL_REPORTED_FACT · extracted |

**Mapping taxonomique** : L1 ID · L2 LOCAL_PROJECT (liens : SKILLS_DEV, PUBLIC_SPEAKING) · L3 TRAINING_WORKSHOP · L4 **JCI_MEMBERS (interne) 18** + YOUTH (externe, confiance faible) 4 · L5 PARTICIPANTS 22 · L6 SKILLS_CONFIDENCE +1,2 (pré/post, n=20) ; NEW_MEMBERS 3 (organisationnel) · L7 — · L8 4 (dans le mapping ID).

**Données manquantes** : nombre de sessions et heures de formation ; ville ; taille de l'échantillon pré ; genre.

**JSON normalisé V2** (provenance comptée automatiquement, puis objet complet)
| Couche | value_status | Nb d'enveloppes |
|---|---|---|
| OFFICIAL_JCI_FACT | extracted | 6 |
| LOCAL_REPORTED_FACT | extracted | 24 |
| LOCAL_REPORTED_FACT | unknown | 6 |
| SEMANTIC_INTERPRETATION | calculated | 2 |
| SEMANTIC_INTERPRETATION | — | 29 |
| PROPOSED_STANDARD | — | 27 |

<details><summary>Objet JSON complet (identique à jci_tier1_fixtures_v2.json)</summary>

```json
{
  "project": {
    "project_id": {
      "value": "TC4",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:ID-SCHEME-v0"
    },
    "name": {
      "value": "Q2 Training Academy",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC4",
        "quote": "Q2 Training Academy – wrap-up"
      }
    },
    "description": {
      "value": "4 modules (Effective Communication, Project Management, Präsentieren/Presenting, Leadership Basics)",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC4",
        "quote": "4 modules (Effective Communication, Project Management, Präsentieren/Presenting, Leadership Basics)"
      }
    },
    "program": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "no JCI program named",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC4"
        }
      },
      "code": {
        "value": "LOCAL_PROJECT",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-PROGRAM",
        "basis": "local academy",
        "confidence": "H"
      },
      "related_programs": [
        {
          "name": {
            "value": "Skills Development",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "40",
              "section": "Skills Development",
              "quote": "JCI's Skills Development framework provides structured pathways"
            }
          },
          "relation": {
            "value": "delivered_by_certified_trainers",
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "MAP-RELATED-PROGRAM",
            "basis": "'2 CATs'",
            "confidence": "M"
          }
        },
        {
          "name": {
            "value": "Public Speaking Competition",
            "layer": "OFFICIAL_JCI_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "fact_scope": "statement_published",
            "source": {
              "origin": "jci_report_2025",
              "document": "JCI Impact Report 2025",
              "page": "43",
              "section": "Public Speaking Competition",
              "quote": "The JCI Public Speaking Competition"
            }
          },
          "relation": {
            "value": "pipeline_intention",
            "layer": "SEMANTIC_INTERPRETATION",
            "rule_id": "MAP-RELATED-PROGRAM",
            "basis": "'will compete at the national Public Speaking Competition'",
            "confidence": "M"
          }
        }
      ]
    },
    "area_of_opportunity": [
      {
        "value": {
          "value": "Individual Development",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "24",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Individual Development"
          }
        },
        "code": {
          "value": "ID",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-AOO-CONTENT",
          "basis": "skills training for members",
          "confidence": "H"
        }
      }
    ],
    "period": {
      "start": {
        "value": "2025-04",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-MONTH",
        "basis": "'Saturdays in April–May' + submission year",
        "confidence": "M"
      },
      "end": {
        "value": "2025-05",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-MONTH",
        "basis": "same",
        "confidence": "M"
      },
      "duration": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC4"
        },
        "unit": "hour"
      }
    },
    "recognition": []
  },
  "organization": {
    "local_organization": {
      "value": "JCI Rheinaue",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC4",
        "quote": "— VP Training, JCI Rheinaue"
      }
    },
    "national_organization": {
      "value": "JCI Germany",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NO-FROM-TEXT",
      "basis": "'2 CATs from JCI Germany' (trainers' NO, assumed same NO)",
      "confidence": "M",
      "attested_in_report": {
        "value": true,
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "35",
          "section": "JIB Impact Stories",
          "quote": "JCI Germany"
        }
      }
    },
    "geographic_area": {
      "value": {
        "value": "Europe",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "9",
          "section": "International Presence – Operational Areas",
          "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
        }
      },
      "code": {
        "value": "EUROPE",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "GEO-FROM-COUNTRY",
        "basis": "Germany → Europe: general knowledge; the report does not publish a country→geographic_area list (map p. 9 = VDX-01)",
        "confidence": "M"
      }
    },
    "partner_organizations": [],
    "lead_contact": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC4"
        }
      },
      "role": {
        "value": "VP Training",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "VP Training"
        }
      }
    }
  },
  "location": {
    "country": {
      "value": "Germany",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "GEO-FROM-NO",
      "basis": "JCI Germany",
      "confidence": "M"
    },
    "country_iso2": {
      "value": "DE",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NORM-ISO3166",
      "basis": "country → ISO",
      "confidence": "H"
    },
    "city": {
      "value": null,
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "unknown",
      "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
      "source": {
        "origin": "local_submission",
        "searched_scope": "TC4"
      }
    },
    "scope": {
      "value": "local",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-SCOPE",
      "basis": "local academy",
      "confidence": "H"
    }
  },
  "activity": {
    "activity_types": [
      {
        "code": {
          "value": "TRAINING_WORKSHOP",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "training modules",
          "confidence": "H"
        }
      }
    ],
    "delivery_mode": {
      "value": "in_person",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-DELIVERY",
      "basis": "'Saturdays' + room cost",
      "confidence": "M"
    },
    "modules_count": {
      "value": 4,
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "unit": "module",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC4",
        "quote": "4 modules"
      }
    },
    "sessions_count": {
      "value": null,
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "unknown",
      "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
      "source": {
        "origin": "local_submission",
        "searched_scope": "TC4"
      },
      "unit": "session"
    },
    "planned_follow_up": [
      {
        "value": {
          "value": 2,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "2 participants will compete at the national Public Speaking Competition"
          }
        },
        "status": {
          "value": "intention",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:STATUS-v0"
        }
      }
    ],
    "resources": [
      {
        "label_raw": "2 CATs from JCI Germany",
        "value": {
          "value": 2,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "2 CATs from JCI Germany"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "TRAINERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "certified trainers",
          "confidence": "H"
        },
        "certification": {
          "value": [
            "CAT"
          ],
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-CERT",
          "basis": "CAT = Certified Area Trainer (inferred from p. 106)",
          "confidence": "M"
        }
      },
      {
        "label_raw": "our local trainer",
        "value": {
          "value": 1,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "our local trainer"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "TRAINERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "local trainer",
          "confidence": "H"
        }
      },
      {
        "label_raw": "€640 room",
        "value": {
          "value": 640,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "EUR",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "€640 room"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "COST",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "venue cost",
          "confidence": "H"
        }
      },
      {
        "label_raw": "€180 materials",
        "value": {
          "value": 180,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "EUR",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "€180 materials"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "COST",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "materials cost",
          "confidence": "H"
        }
      },
      {
        "label_raw": null,
        "value": {
          "value": 820,
          "layer": "SEMANTIC_INTERPRETATION",
          "value_status": "calculated",
          "formula": "640 + 180",
          "inputs": [
            {
              "origin": "local_submission",
              "submission_id": "TC4",
              "quote": "€640 room"
            },
            {
              "origin": "local_submission",
              "submission_id": "TC4",
              "quote": "€180 materials"
            }
          ],
          "rule_id": "CALC-ARITH",
          "confidence": "H",
          "unit": "EUR"
        },
        "normalization": {
          "metric_code": {
            "value": "BUDGET_TOTAL",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "sum of costs",
          "confidence": "H"
        },
        "funding_source": {
          "value": "member fees",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "covered by member fees"
          }
        }
      }
    ]
  },
  "beneficiaries": [
    {
      "target_group": {
        "code": {
          "value": "JCI_MEMBERS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'members'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "18 members",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "18 members"
        }
      },
      "internal_external": {
        "value": "internal",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "JCI members",
        "confidence": "H"
      },
      "count": {
        "value": 18,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "18 members"
        }
      }
    },
    {
      "target_group": {
        "code": {
          "value": "YOUTH",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'guests' — profile not described",
          "confidence": "L"
        }
      },
      "label_raw": {
        "value": "4 guests",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "4 guests"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "non-members at time of training",
        "confidence": "H"
      },
      "count": {
        "value": 4,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "4 guests"
        }
      }
    }
  ],
  "outputs": [
    {
      "label_raw": "22 participants",
      "value": {
        "value": 22,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "22 participants (18 members, 4 guests"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PARTICIPANTS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "participants",
        "confidence": "H"
      }
    }
  ],
  "outcomes": [
    {
      "label_raw": "avg confidence speaking in public went from 2.9 to 4.1 (scale 1–5)",
      "value": {
        "value": 1.2,
        "layer": "SEMANTIC_INTERPRETATION",
        "value_status": "calculated",
        "formula": "4.1 − 2.9",
        "inputs": [
          {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "went from 2.9 to 4.1 (scale 1–5)"
          }
        ],
        "rule_id": "CALC-ARITH",
        "confidence": "H",
        "unit": "scale_points"
      },
      "normalization": {
        "metric_code": {
          "value": "SKILLS_CONFIDENCE",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "measured change (pre/post)",
        "confidence": "H"
      },
      "baseline": {
        "value": 2.9,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "scale_1_5",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "from 2.9"
        }
      },
      "endline": {
        "value": 4.1,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "scale_1_5",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "to 4.1 (scale 1–5)"
        }
      },
      "measurement": {
        "method": {
          "value": "Pre/post self-assessment",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "Pre/post self-assessment"
          }
        },
        "respondents_post": {
          "value": 20,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "20/22 filled the post survey"
          }
        },
        "respondents_pre": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC4"
          },
          "unit": "person"
        },
        "population": {
          "value": 22,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC4",
            "quote": "20/22"
          }
        }
      }
    },
    {
      "label_raw": "3 of them joined JCI afterwards",
      "value": {
        "value": 3,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "3 of them joined JCI afterwards!"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "NEW_MEMBERS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "organizational outcome, not beneficiary outcome",
        "confidence": "H"
      },
      "outcome_level": {
        "value": "organizational",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      }
    }
  ],
  "impact": [],
  "sdgs": [
    {
      "sdg": 4,
      "label": {
        "value": "Quality Education",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 4: Quality Education"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "SDG 4."
        }
      },
      "role": {
        "value": "primary",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-SINGLE",
        "basis": "only one SDG declared",
        "confidence": "H"
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "ID",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    }
  ],
  "evidence": [
    {
      "type": {
        "value": "survey",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "declared": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC4",
          "quote": "Pre/post self-assessment"
        }
      },
      "attached": {
        "value": false,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "EVIDENCE-CHECK",
        "basis": "no file received",
        "confidence": "H"
      }
    }
  ],
  "data_quality": {
    "record_origin": "local_submission",
    "verification": {
      "value": "none",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:STATUS-v0"
    },
    "conflict_refs": [],
    "visual_refs": [],
    "unknowns": [
      "activity.sessions_count",
      "project.period.duration",
      "location.city",
      "measurement.respondents_pre"
    ],
    "warnings": [
      "internal (18) and external (4) beneficiaries must not be merged in network totals (P12)"
    ]
  }
}
```

</details>

---

## TC5 — International (Twinning, FR + EN, Bénin–Canada) — « Digital pour tous / Digital for All »

**Input brut A (Bénin)**
```text
[JCI Ouidah Étoile – Bénin] Dans le cadre de notre jumelage signé à la Conférence Afrique de Durban, nous avons organisé avec nos amis canadiens le webinaire « Digital pour tous » en septembre : 3 sessions en ligne, 140 connectés au total, 60 jeunes formés au marketing digital. Formateurs : 2 Canadiens + 1 Béninois. Résultat : 5 jeunes ont déjà trouvé leurs premiers clients en ligne ! ODD 8 et 17.
```

**Input brut B (Canada)**
```text
[JCI Laurentides Nord – Canada] Twinning webinar series 'Digital for All' with our Beninese partners: 3 online sessions, 95 unique attendees, 11 of our members volunteered ~30h in total. Great cultural exchange! SDG 17, 4, 10.
```

**Données extraites (après fusion)**

| Champ | Valeur | Source | Statut |
|---|---|---|---|
| Projet unique ? | Oui (partenaires nommés, 3 sessions, titre traduit, même période) | A + B | SEMANTIC_INTERPRETATION (dédoublonnage) |
| Sessions | 3 en ligne | A + B (concordant) | LOCAL_REPORTED_FACT · extracted |
| Période | 2025-09 | A « en septembre » | SEMANTIC_INTERPRETATION (normalisation) (mois) |
| Connexions cumulées | 140 | A « 140 connectés au total » | LOCAL_REPORTED_FACT · extracted (≠ personnes) |
| Participants uniques | 95 | B « 95 unique attendees » | LOCAL_REPORTED_FACT · extracted |
| Jeunes formés | 60 | A | LOCAL_REPORTED_FACT · extracted (définition inconnue) |
| Formateurs | 2 CA + 1 BJ | A | LOCAL_REPORTED_FACT · extracted |
| Bénévoles / heures (côté Canada) | 11 / ~30 h | B | LOCAL_REPORTED_FACT · extracted (périmètre partiel) |
| Outcome | 5 jeunes avec premiers clients en ligne | A | LOCAL_REPORTED_FACT · extracted (auto-déclaré) |
| ODD | A : 8, 17 ; B : 17, 4, 10 → union 4, 8, 10, 17 | A + B | SEMANTIC_INTERPRETATION (union, provenance par source conservée) |

**Mapping taxonomique** : L1 IC (défaut Twinning) + BE (contenu) · L2 TWINNING · L3 ONLINE_COURSE_WEBINAR, TRAINING_WORKSHOP, PARTNERSHIP_AGREEMENT · L4 YOUTH · L5 ATTENDEES 95 (uniques), ATTENDEES 140 (connexions), PEOPLE_TRAINED 60 · L6 ACCESS_TO_FINANCE_MARKETS 5 · L7 — · L8 4, 8, 10, 17.

**Données manquantes** : dates exactes ; bénévoles côté Bénin ; répartition des participants par pays ; date de signature du jumelage ; horizon de l'outcome ; ODD principal.

**JSON normalisé V2** (provenance comptée automatiquement, puis objet complet)
| Couche | value_status | Nb d'enveloppes |
|---|---|---|
| OFFICIAL_JCI_FACT | extracted | 11 |
| LOCAL_REPORTED_FACT | extracted | 26 |
| LOCAL_REPORTED_FACT | unknown | 11 |
| SEMANTIC_INTERPRETATION | — | 34 |
| PROPOSED_STANDARD | — | 29 |

<details><summary>Objet JSON complet (identique à jci_tier1_fixtures_v2.json)</summary>

```json
{
  "project": {
    "project_id": {
      "value": "TC5",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:ID-SCHEME-v0"
    },
    "name": {
      "values": [
        {
          "value": "Digital pour tous",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-A",
            "quote": "le webinaire « Digital pour tous »"
          }
        },
        {
          "value": "Digital for All",
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-B",
            "quote": "Twinning webinar series 'Digital for All'"
          }
        }
      ],
      "same_project": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "DEDUP-TWINNING",
        "basis": "partners name each other, 3 online sessions on both sides, translated title, same period",
        "confidence": "M"
      }
    },
    "description": {
      "value": "webinaire de 3 sessions en ligne",
      "layer": "LOCAL_REPORTED_FACT",
      "value_status": "extracted",
      "value_qualifier": "exact",
      "source": {
        "origin": "local_submission",
        "submission_id": "TC5-A",
        "quote": "3 sessions en ligne"
      }
    },
    "program": {
      "name": {
        "value": "JCI Twinning",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "78",
          "section": "JCI Twinning",
          "quote": "JCI Twinning is a voluntary partnership program between JCI National and Local Organizations"
        }
      },
      "code": {
        "value": "TWINNING",
        "layer": "PROPOSED_STANDARD",
        "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
      },
      "assignment": {
        "values": [
          {
            "value": true,
            "layer": "LOCAL_REPORTED_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "source": {
              "origin": "local_submission",
              "submission_id": "TC5-A",
              "quote": "Dans le cadre de notre jumelage"
            }
          },
          {
            "value": true,
            "layer": "LOCAL_REPORTED_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "source": {
              "origin": "local_submission",
              "submission_id": "TC5-B",
              "quote": "Twinning webinar series"
            }
          }
        ]
      },
      "components": [
        {
          "type": "twinning_agreement",
          "value": {
            "value": "signé à la Conférence Afrique de Durban",
            "layer": "LOCAL_REPORTED_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "source": {
              "origin": "local_submission",
              "submission_id": "TC5-A",
              "quote": "notre jumelage signé à la Conférence Afrique de Durban"
            }
          },
          "date": {
            "value": null,
            "layer": "LOCAL_REPORTED_FACT",
            "value_status": "unknown",
            "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
            "source": {
              "origin": "local_submission",
              "searched_scope": "TC5-A"
            }
          }
        }
      ]
    },
    "area_of_opportunity": [
      {
        "value": {
          "value": "International Cooperation",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "24",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "International Cooperation"
          }
        },
        "code": {
          "value": "IC",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "INH-PROGRAM-AOO",
          "basis": "JCI Twinning is in the International Cooperation chapter (p. 78, document_structure)",
          "confidence": "H"
        }
      },
      {
        "value": {
          "value": "Business & Entrepreneurship",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "24",
            "section": "Four Areas of Opportunity and SDG Alignment",
            "quote": "Business & Entrepreneurship"
          }
        },
        "code": {
          "value": "BE",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-AOO-CONTENT",
          "basis": "digital marketing to find clients",
          "confidence": "M"
        }
      }
    ],
    "period": {
      "start": {
        "value": "2025-09",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-MONTH",
        "basis": "'en septembre' + submission year",
        "confidence": "M",
        "evidence": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "en septembre"
        }
      },
      "end": {
        "value": "2025-09",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NORM-DATE-MONTH",
        "basis": "same",
        "confidence": "M"
      },
      "duration": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC5-A+B"
        },
        "unit": "hour"
      }
    },
    "recognition": []
  },
  "organization": {
    "local_organization": [
      {
        "value": "JCI Ouidah Étoile",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "[JCI Ouidah Étoile – Bénin]"
        }
      },
      {
        "value": "JCI Laurentides Nord",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-B",
          "quote": "[JCI Laurentides Nord – Canada]"
        }
      }
    ],
    "national_organization": [
      {
        "value": "JCI Benin",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NO-FROM-COUNTRY",
        "basis": "'Bénin' in header",
        "confidence": "M",
        "attested_in_report": {
          "value": true,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "6",
            "section": "2025 Board of Directors",
            "quote": "JCI BENIN"
          }
        }
      },
      {
        "value": "JCI Canada",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "NO-FROM-COUNTRY",
        "basis": "'Canada' in header",
        "confidence": "M",
        "attested_in_report": {
          "value": true,
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "82",
            "section": "JCI Twinning Impact Stories",
            "quote": "JCI Canada"
          }
        }
      }
    ],
    "geographic_area": [
      {
        "value": {
          "value": "Africa and the Middle East",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "9",
            "section": "International Presence – Operational Areas",
            "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
          }
        },
        "code": {
          "value": "AFME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "GEO-FROM-COUNTRY",
          "basis": "Benin → Africa and the Middle East: general knowledge; the report does not publish a country→geographic_area list (map p. 9 = VDX-01)",
          "confidence": "M"
        }
      },
      {
        "value": {
          "value": "America",
          "layer": "OFFICIAL_JCI_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "fact_scope": "statement_published",
          "source": {
            "origin": "jci_report_2025",
            "document": "JCI Impact Report 2025",
            "page": "9",
            "section": "International Presence – Operational Areas",
            "quote": "four Regional Areas — Africa and the Middle East, America, Asia and the Pacific, and Europe"
          }
        },
        "code": {
          "value": "AMERICA",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "GEO-FROM-COUNTRY",
          "basis": "Canada → America: general knowledge; the report does not publish a country→geographic_area list (map p. 9 = VDX-01)",
          "confidence": "M"
        }
      }
    ],
    "partner_organizations": [],
    "lead_contact": {
      "name": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC5"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC5"
        }
      }
    }
  },
  "location": {
    "country": [
      {
        "value": "Bénin",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "Bénin"
        }
      },
      {
        "value": "Canada",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-B",
          "quote": "Canada"
        }
      }
    ],
    "country_iso2": {
      "value": [
        "BJ",
        "CA"
      ],
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "NORM-ISO3166",
      "basis": "country → ISO",
      "confidence": "H"
    },
    "venue": {
      "value": "online",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-DELIVERY",
      "basis": "'en ligne' / 'online sessions'",
      "confidence": "H"
    },
    "scope": {
      "value": "international",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-SCOPE",
      "basis": "two countries",
      "confidence": "H"
    }
  },
  "activity": {
    "activity_types": [
      {
        "code": {
          "value": "ONLINE_COURSE_WEBINAR",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "'webinaire'",
          "confidence": "H"
        }
      },
      {
        "code": {
          "value": "TRAINING_WORKSHOP",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "'formés au marketing digital'",
          "confidence": "H"
        }
      },
      {
        "code": {
          "value": "PARTNERSHIP_AGREEMENT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-ACTIVITY",
          "basis": "twinning agreement",
          "confidence": "M"
        }
      }
    ],
    "delivery_mode": {
      "value": "online",
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "MAP-DELIVERY",
      "basis": "both reports",
      "confidence": "H"
    },
    "sessions_count": {
      "values": [
        {
          "value": 3,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "session",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-A",
            "quote": "3 sessions en ligne"
          }
        },
        {
          "value": 3,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "session",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-B",
            "quote": "3 online sessions"
          }
        }
      ],
      "consistent": {
        "value": true,
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "DEDUP-CHECK",
        "basis": "A = B",
        "confidence": "H"
      }
    },
    "resources": [
      {
        "label_raw": "2 Canadiens",
        "value": {
          "value": 2,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-A",
            "quote": "Formateurs : 2 Canadiens"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "TRAINERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "trainers",
          "confidence": "H"
        }
      },
      {
        "label_raw": "1 Béninois",
        "value": {
          "value": 1,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-A",
            "quote": "+ 1 Béninois"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "TRAINERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "trainers",
          "confidence": "H"
        }
      },
      {
        "label_raw": "11 of our members volunteered",
        "value": {
          "value": 11,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "exact",
          "unit": "person",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-B",
            "quote": "11 of our members volunteered"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "Canada side only",
          "confidence": "H"
        },
        "member": true
      },
      {
        "label_raw": "~30h in total",
        "value": {
          "value": 30,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "extracted",
          "value_qualifier": "approx",
          "unit": "hour",
          "source": {
            "origin": "local_submission",
            "submission_id": "TC5-B",
            "quote": "~30h in total"
          }
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEER_HOURS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "Canada side only",
          "confidence": "H"
        }
      },
      {
        "label_raw": null,
        "value": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "Benin-side volunteers not reported",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC5-A"
          },
          "unit": "person"
        },
        "normalization": {
          "metric_code": {
            "value": "VOLUNTEERS",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
          },
          "iaooi_class": {
            "value": "INPUT",
            "layer": "PROPOSED_STANDARD",
            "standard": "PROPOSED_STANDARD:IAOOI-v0"
          },
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METRIC",
          "basis": "Benin side",
          "confidence": "H"
        }
      }
    ]
  },
  "beneficiaries": [
    {
      "target_group": {
        "code": {
          "value": "YOUTH",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "assignment": {
          "value": true,
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-TARGET",
          "basis": "'jeunes'",
          "confidence": "H"
        }
      },
      "label_raw": {
        "value": "jeunes",
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "60 jeunes formés au marketing digital"
        }
      },
      "internal_external": {
        "value": "external",
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-INTERNAL-EXTERNAL",
        "basis": "not described as members",
        "confidence": "M"
      },
      "count_by_country": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
        "source": {
          "origin": "local_submission",
          "searched_scope": "TC5-A+B"
        },
        "unit": "person"
      }
    }
  ],
  "outputs": [
    {
      "label_raw": "95 unique attendees",
      "value": {
        "value": 95,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-B",
          "quote": "95 unique attendees"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "ATTENDEES",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "unique people",
        "confidence": "H"
      }
    },
    {
      "label_raw": "140 connectés au total",
      "value": {
        "value": 140,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "connection",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "140 connectés au total"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "ATTENDEES",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "sum of connections over 3 sessions — distinct metric from 95, not a conflict",
        "confidence": "H"
      }
    },
    {
      "label_raw": "60 jeunes formés au marketing digital",
      "value": {
        "value": 60,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "60 jeunes formés au marketing digital"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "PEOPLE_TRAINED",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTPUT",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "definition of 'formé' not given; 60 ≤ 95 consistent",
        "confidence": "M"
      }
    }
  ],
  "outcomes": [
    {
      "label_raw": "5 jeunes ont déjà trouvé leurs premiers clients en ligne",
      "value": {
        "value": 5,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "unit": "person",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "5 jeunes ont déjà trouvé leurs premiers clients en ligne"
        }
      },
      "normalization": {
        "metric_code": {
          "value": "ACCESS_TO_FINANCE_MARKETS",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:JCI-NORM-v0"
        },
        "iaooi_class": {
          "value": "OUTCOME",
          "layer": "PROPOSED_STANDARD",
          "standard": "PROPOSED_STANDARD:IAOOI-v0"
        },
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "MAP-METRIC",
        "basis": "market access for beneficiaries",
        "confidence": "M"
      },
      "measurement": {
        "method": {
          "value": "self_reported",
          "layer": "SEMANTIC_INTERPRETATION",
          "rule_id": "MAP-METHOD",
          "basis": "no instrument",
          "confidence": "M"
        },
        "horizon": {
          "value": null,
          "layer": "LOCAL_REPORTED_FACT",
          "value_status": "unknown",
          "reason": "NOT SPECIFIED IN THE SOURCE DOCUMENT",
          "source": {
            "origin": "local_submission",
            "searched_scope": "TC5-A"
          }
        }
      }
    }
  ],
  "impact": [],
  "sdgs": [
    {
      "sdg": 4,
      "label": {
        "value": "Quality Education",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 4: Quality Education"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-B",
          "quote": "SDG 17, 4, 10"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "ID",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 8,
      "label": {
        "value": "Decent Work and Economic Growth",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 8: Decent Work and Economic Growth"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-A",
          "quote": "ODD 8 et 17"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "BE",
          "CI"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 10,
      "label": {
        "value": "Reduced Inequalities",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "24",
          "section": "SDG label as printed",
          "quote": "SDG 10: Reduced Inequalities"
        }
      },
      "assignment": {
        "value": true,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "source": {
          "origin": "local_submission",
          "submission_id": "TC5-B",
          "quote": "SDG 17, 4, 10"
        }
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "ID"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    },
    {
      "sdg": 17,
      "label": {
        "value": "Partnerships for the Goals",
        "layer": "OFFICIAL_JCI_FACT",
        "value_status": "extracted",
        "value_qualifier": "exact",
        "fact_scope": "statement_published",
        "source": {
          "origin": "jci_report_2025",
          "document": "JCI Impact Report 2025",
          "page": "25",
          "section": "SDG label as printed",
          "quote": "SDG 17: Partnerships for the Goals"
        }
      },
      "assignment": {
        "values": [
          {
            "value": true,
            "layer": "LOCAL_REPORTED_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "source": {
              "origin": "local_submission",
              "submission_id": "TC5-A",
              "quote": "ODD 8 et 17"
            }
          },
          {
            "value": true,
            "layer": "LOCAL_REPORTED_FACT",
            "value_status": "extracted",
            "value_qualifier": "exact",
            "source": {
              "origin": "local_submission",
              "submission_id": "TC5-B",
              "quote": "SDG 17, 4, 10"
            }
          }
        ]
      },
      "role": {
        "value": null,
        "layer": "LOCAL_REPORTED_FACT",
        "value_status": "unknown",
        "reason": "primary/secondary not stated",
        "source": {
          "origin": "local_submission",
          "searched_scope": "submission text"
        }
      },
      "in_default_sdgs_of_area_of_opportunity": {
        "value": [
          "IC"
        ],
        "layer": "SEMANTIC_INTERPRETATION",
        "rule_id": "SDG-DEFAULT-MAP",
        "basis": "AoO→SDG lists published p. 24–25 (OFFICIAL_JCI_FACT); membership test = interpretation",
        "confidence": "H"
      },
      "flags": []
    }
  ],
  "evidence": [],
  "data_quality": {
    "record_origin": "local_submission",
    "verification": {
      "value": "none",
      "layer": "PROPOSED_STANDARD",
      "standard": "PROPOSED_STANDARD:STATUS-v0"
    },
    "conflict_refs": [],
    "visual_refs": [],
    "deduplication": {
      "value": {
        "merged_reports": 2,
        "sources": [
          "TC5-A",
          "TC5-B"
        ]
      },
      "layer": "SEMANTIC_INTERPRETATION",
      "rule_id": "DEDUP-TWINNING",
      "basis": "same project reported by both twinned LOs",
      "confidence": "M"
    },
    "unknowns": [
      "exact dates",
      "Benin-side volunteers",
      "participants by country",
      "twinning agreement date",
      "outcome horizon",
      "sdgs[*].role"
    ],
    "warnings": [
      "counting this project once per LO would double-count 95 attendees",
      "SDG set = union with per-source provenance"
    ]
  }
}
```

</details>

---


---

# Q. REGISTRE DES CONFLITS DU RAPPORT (objets de qualité de données)

> Règle P8 : **aucune résolution silencieuse**. Tous les objets sont `resolution_status = UNRESOLVED` et `resolution = null`. Les « explications candidates » sont des SEMANTIC_INTERPRETATION **non adoptées** (`adopted: false`). Statuts possibles : `UNRESOLVED` · `RESOLVED_BY_JCI_SOURCE` (citation JCI requise) · `RESOLVED_BY_TEAM_DECISION` (devient PROPOSED_STANDARD, jamais OFFICIAL_JCI_FACT).

> Dans les citations, « … » relie des passages consécutifs du même bloc (citation composite).

> Format machine complet (valeurs, sources, cas de test) : `jci_data_quality_registry_v2.json`.


## Q.1 Vue d'ensemble

| ID | V1 | Sujet | Type(s) de conflit | Statut | Comportement attendu du moteur |
|---|---|---|---|---|---|
| DQC-01 | I1 | Nombre de membres | LOWER_BOUND_VS_EXACT, ROUNDING_OR_APPROXIMATION | **UNRESOLVED** | Retourner toutes les valeurs avec source ; D peut être marquée most_precise_published (SEMANTIC_INTERPRETATION) sans écraser A–C. |
| DQC-02 | I2 | Nombre de pays | LOWER_BOUND_VS_EXACT, CONTRADICTORY_BOUNDS | **UNRESOLVED** | Ne jamais assimiler nombre de pays et nombre de National Organizations ; conserver les 4 valeurs. |
| DQC-03 | I3 | Nombre de projets | ORDER_OF_MAGNITUDE, PERIOD_MISMATCH, METRIC_DEFINITION_MISMATCH | **UNRESOLVED** | Ne jamais additionner ni choisir ; exposer l'écart d'un facteur 10 et la période de chaque valeur. |
| DQC-04 | I4 | Nombre de Local Organizations | ROUNDING_OR_APPROXIMATION | **UNRESOLVED** | Conserver les 3 valeurs ; ne pas confondre 'mobilized' et nombre total. |
| DQC-05 | I5 | Nombre de bénévoles | LOWER_BOUND_VS_EXACT | **UNRESOLVED** | Conserver les 3 valeurs ; C peut être marquée most_precise_published (interprétation). |
| DQC-06 | I6 | Participation aux événements internationaux | METRIC_DEFINITION_MISMATCH, CONTRADICTORY_BOUNDS | **UNRESOLVED** | Ne pas convertir registrations en attendees ; garder 3 métriques distinctes. |
| DQC-07 | I7 | Followers réseaux sociaux | AGGREGATION_MISMATCH | **UNRESOLVED** | Afficher A (publié) et B (calculé, SEMANTIC_INTERPRETATION) côte à côte ; ne jamais remplacer A par B. |
| DQC-08 | I8 | Impressions vs reach | METRIC_DEFINITION_MISMATCH | **UNRESOLVED** | Reach et impressions sont deux métriques distinctes ; ne jamais les fusionner. |
| DQC-09 | I9 | Lecteurs du LEADER Magazine | ROUNDING_OR_APPROXIMATION, CONTRADICTORY_BOUNDS, AGGREGATION_BASE_MISMATCH | **UNRESOLVED** | Conserver A, B, C ; D reste un calcul signalé ; '70+ countries' = extracted mais sans détail (unsupported_in_body). |
| DQC-10 | I10 | Genre des Senators | ARITHMETIC_ERROR | **UNRESOLVED** | Ne corriger aucune des deux valeurs ; bloquer tout calcul dérivé (ex. nombre de femmes). |
| DQC-11 | I11 | Participants JCI Ankara '7x7' | INTERNAL_CONTRADICTION | **UNRESOLVED** | Conserver les deux ; aucune valeur par défaut. |
| DQC-12 | I12 | Bridges Project : participants vs formés | SCOPE_MISMATCH | **UNRESOLVED** | Conserver les deux ; les ratios d'outcome restent sans base (base_population = unknown). |
| DQC-13 | I13 | Impulso NOA : 4 nouveaux membres = 20 % | ARITHMETIC_ERROR, AGGREGATION_BASE_MISMATCH | **UNRESOLVED** | Conserver 20 % publié et 18,2 % calculé ; ne pas déduire le nombre de participants. |
| DQC-14 | I14 | Global Youth Dialogue : présents vs membres/non-membres | AGGREGATION_BASE_MISMATCH | **UNRESOLVED** | Ne pas appliquer 79,6 % aux 662 présents ; base de B/C = unknown. |
| DQC-15 | I15 | ECOSOC side event : présents > inscrits | PLAUSIBILITY_FLAG | **UNRESOLVED** | Signaler la plausibilité ; ne pas calculer de taux de présence. |
| DQC-16 | I16 | ODD du programme JCI RISE | MAPPING_INCONSISTENCY | **UNRESOLVED** | Stocker les deux mappings avec leur page ; l'ODD par défaut d'un projet RISE ne doit pas être tiré de l'un seul sans le signaler. |
| DQC-17 | I17 | Libellés des piliers RISE | LABEL_MISMATCH | **UNRESOLVED** | Garder les deux libellés comme synonymes officiels d'un même code proposé ; la correspondance est SEMANTIC_INTERPRETATION. |
| DQC-18 | I18 | Pourcentages dont la somme vaut 100,01 % | ROUNDING_OR_APPROXIMATION | **UNRESOLVED** | Conserver les valeurs publiées ; ne pas renormaliser à 100 %. |
| DQC-19 | I19 | Part des LO en Europe | ROUNDING_OR_APPROXIMATION | **UNRESOLVED** | Conserver A et B ; C est un calcul. |
| DQC-20 | I20 | Nom officiel de TOYP | LABEL_MISMATCH | **UNRESOLVED** | Mapper les 3 libellés vers le programme TOYP (SEMANTIC_INTERPRETATION) ; conserver les libellés bruts. |
| DQC-21 | I21 | Chiffres d'événements externes à proximité des chiffres JCI | EXTERNAL_METRIC_ADJACENT | **UNRESOLVED** | Marquer scope = external_event ; exclure de tout agrégat JCI. |
| DQC-22 | I22 | ODD 11 cité deux fois (SDGs Hunt) | DUPLICATE_ENTRY | **UNRESOLVED** | Dédoublonner les ODD (calcul) en conservant le compte brut (18 mentions) et le compte distinct (17) ; signaler le sur-tagging. |
| DQC-23 | I23 | Pétitions IHD : pays par geographic_area | SUSPICIOUS_COUNT | **UNRESOLVED** | Ne pas utiliser les comptes de pays pour la couverture géographique JCI. |
| DQC-24 | I24 | Hétérogénéité des périodes de reporting | PERIOD_HETEROGENEITY | **UNRESOLVED** | Chaque valeur porte sa période ; aucun agrégat inter-métriques sans période commune. |
| DQC-25 | B.2/M028 | Part des membres d'America (graphique) *(ajout V2)* | TYPO_LIKELY | **UNRESOLVED** | Conserver A et B ; B signalé, jamais utilisé dans un calcul. |
| DQC-26 | B.2/M047-M048 | Utilisateurs actifs de jci.cc *(ajout V2)* | PERIOD_MISMATCH | **UNRESOLVED** | Conserver A et B avec leurs périodes. |

## Q.2 Détail des valeurs en conflit

### DQC-01 — Nombre de membres

- **A** : ≥ 100000 — « a global network of over 100,000 young leaders in more than 100 countries » [p. v — Executive Summary]
- **B** : ≥ 100000 — « More than 100,000 young leaders across four Areas came together » [p. vi — Message from JCI President]
- **C** : ≥ 147000 — « with over 147,000 members and 4,600 Local Organizations worldwide » [p. 2 — Organization Overview]
- **D** : 147670 — « powered by 147,670 members » [p. 8 — Membership Details]
- **Type** : LOWER_BOUND_VS_EXACT, ROUNDING_OR_APPROXIMATION · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : A, B et C sont des bornes inférieures compatibles avec D ; 'young leaders' (A, B) et 'members' (C, D) ne sont pas démontrés équivalents.
- **Cas de test** : « Combien de membres compte JCI selon le rapport 2025 ? » → attendu `{"answer_mode": "multi_value_with_sources", "must_cite": ["v", "2", "8"], "flag": "DQC-01"}` · **interdit** : Répondre uniquement '100,000' ; Présenter 147,670 comme seule valeur sans signaler DQC-01 ; Fusionner 'young leaders' et 'members' sans le dire

### DQC-02 — Nombre de pays

- **A** : ≥ 100 — « in more than 100 countries » [p. v — Executive Summary]
- **B** : ≥ 100 — « present in over 100 countries » [p. 24 — Four Areas of Opportunity and SDG Alignment]
- **C** : ≥ 114 — « Today, JCI is present in more than 114 countries » [p. 2 — Organization Overview]
- **D** : 114 — « Global Presence (114 Countries) » [p. 9 — International Presence – Operational Areas]
- **Type** : LOWER_BOUND_VS_EXACT, CONTRADICTORY_BOUNDS · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : 'more than 114' (C) contredit '114' (D) ; 114 est aussi le nombre de National Organizations (p. 8) alors qu'une NO ne correspond pas toujours à un pays (ex. JCI West Indies).
- **Cas de test** : « Dans combien de pays JCI est-il présent ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-02", "note_required": "NO ≠ pays"}` · **interdit** : Répondre '114 pays' sans mentionner 'more than 100' / 'more than 114' ; Déduire nb pays = nb NO

### DQC-03 — Nombre de projets

- **A** : ≥ 1000 — « 1,000+ projects implemented (2024–2025) » [p. v — Executive Summary]
- **B** : ≥ 1000 — « 1,000+ Total Projects Executed (2024-25) » [p. 84 — Community Development Projects]
- **C** : ≥ 1000 — « 1000+ Total Projects Reported for 2025 » [p. 85 — JCI RISE Projects]
- **D** : ≥ 10000 — « the collective energy of over 10,000 projects across more than 4,500 Local Organizations » [p. vii — Message from Interim Secretary General]
- **Type** : ORDER_OF_MAGNITUDE, PERIOD_MISMATCH, METRIC_DEFINITION_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : A/B (2024–25), C (2025) et D (période non précisée) n'ont pas le même périmètre ; implemented / executed / reported ne sont pas définis.
- **Cas de test** : « Combien de projets JCI a-t-il réalisés ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-03", "must_show_periods": true}` · **interdit** : Répondre '1,000+' ou '10,000+' seul ; Calculer une moyenne

### DQC-04 — Nombre de Local Organizations

- **A** : ≥ 4500 — « 4,500+ Local Organizations mobilized across continents » [p. v — Executive Summary]
- **B** : ≈ 4600 — « 4,600 Local Organizations worldwide » [p. 2 — Organization Overview]
- **C** : 4641 — « 4,641 Local Organizations provide the grassroots foundation » [p. 8 — Membership Details]
- **Type** : ROUNDING_OR_APPROXIMATION · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : Arrondis de 4,641 ; 'mobilized' (A) pourrait désigner un sous-ensemble.
- **Cas de test** : « Combien de Local Organizations ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-04"}` · **interdit** : Arrondir silencieusement

### DQC-05 — Nombre de bénévoles

- **A** : ≥ 40000 — « 40,000+ volunteers engaged » [p. v — Executive Summary]
- **B** : ≥ 40000 — « 40,000+ Total Number of Volunteers Engaged » [p. 84 — Community Development Projects]
- **C** : 42401 — « 42,401 Total Number of Volunteers Engaged » [p. 86 — JCI RISE Projects]
- **Type** : LOWER_BOUND_VS_EXACT · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : A et B sont des arrondis inférieurs de C (compatibles).
- **Cas de test** : « Combien de bénévoles ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-05"}` · **interdit** : Présenter 42,401 comme membres

### DQC-06 — Participation aux événements internationaux

- **A** : ≥ 10000 — « 10,000+ attendees participating in international events » [p. v — Executive Summary]
- **B** : ≤ 10000 — « In 2024–25, JCI gathered nearly 10,000 participants across its global and Area events » [p. 59 — JCI Events Area Conferences and World Congress]
- **C** : 10729 — « Total Registrations Across All Conferences 10,729 Registrations » [p. 59 — JCI Events Area Conferences and World Congress]
- **Type** : METRIC_DEFINITION_MISMATCH, CONTRADICTORY_BOUNDS · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : '10,000+' (A) et 'nearly 10,000' (B) sont des bornes opposées ; C compte des inscriptions, unité différente de 'attendees'/'participants'.
- **Cas de test** : « Combien de personnes ont participé aux événements internationaux JCI ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-06", "must_distinguish": ["registrations", "attendees", "participants"]}` · **interdit** : Répondre 10,729 participants

### DQC-07 — Followers réseaux sociaux

- **A** : ≥ 260000 — « 260,000+ followers across JCI's digital platforms » [p. v — Executive Summary]
- **B** : 229200 — *calculé* (`148000 + 41000 + 32000 + 8200`), SEMANTIC_INTERPRETATION
- **Type** : AGGREGATION_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance L, non adoptée)* : A peut inclure des plateformes non détaillées ou une autre date ; B additionne des followers et des abonnés YouTube (unités voisines, non identiques).
- **Cas de test** : « Quel est le nombre total de followers JCI ? » → attendu `{"answer_mode": "published_vs_calculated", "flag": "DQC-07"}` · **interdit** : Présenter 229,200 comme chiffre JCI ; Corriger 260,000 en 229,200

### DQC-08 — Impressions vs reach

- **A** : ≥ 2000000 — « 2 million+ impressions » [p. v — Executive Summary]
- **B** : ≥ 2000000 — « Reach: Over 2 million (76% organic) » [p. 17 — Social Media Metrics]
- **C** : 318604 — « Impressions: 318,604 » [p. 17 — Social Media Metrics]
- **Type** : METRIC_DEFINITION_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : Le résumé exécutif semble reprendre la reach Facebook (B) sous le nom 'impressions' ; les seules impressions détaillées sont LinkedIn (C).
- **Cas de test** : « Combien d'impressions JCI a-t-il générées ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-08"}` · **interdit** : Additionner reach et impressions ; Déclarer '2M impressions' vérifié

### DQC-09 — Lecteurs du LEADER Magazine

- **A** : ≈ 13800 — « The Leader Magazine: 13,800 readers across 70+ countries » [p. v — Executive Summary]
- **B** : ≤ 13000 — « The Leader has reached nearly 13,000 total readers across seven issues » [p. 19 — The LEADER Magazine]
- **C** : 13872 — « Total 13,872 15,423 0:48:56 » [p. 20 — The LEADER Magazine]
- **D** : 12564 — *calculé* (`8857 + 81 + 3626`), SEMANTIC_INTERPRETATION
- **Type** : ROUNDING_OR_APPROXIMATION, CONTRADICTORY_BOUNDS, AGGREGATION_BASE_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : 'nearly 13,000' (B) < 13,872 (C) ; la ventilation par appareil (D) porte sur une autre base. '70+ countries' n'est justifié nulle part dans le corps (seulement des top 10 par numéro).
- **Cas de test** : « Combien de lecteurs a le LEADER Magazine ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-09"}` · **interdit** : Répondre 13,800 sans signaler 13,872

### DQC-10 — Genre des Senators

- **A** : 0.67 — « 67% Senators are male » [p. 100 — JCI Senate]
- **B** : 0.37 — « and 37% are female as of 2025 » [p. 100 — JCI Senate]
- **C** : 1.04 — *calculé* (`0.67 + 0.37`), SEMANTIC_INTERPRETATION
- **Type** : ARITHMETIC_ERROR · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance L, non adoptée)* : Coquille probable (33 % ou 63 %), impossible à trancher sans JCI.
- **Cas de test** : « Quelle est la part de femmes parmi les Senators ? » → attendu `{"answer_mode": "report_conflict", "flag": "DQC-10", "derived_calculation_allowed": false}` · **interdit** : Répondre 33% ; Répondre 37% sans signaler la somme de 104%

### DQC-11 — Participants JCI Ankara '7x7'

- **A** : 49 — « where 49 participants discussed the 7 duties at thematic roundtables » [p. 75 — International Human Duties Impact Stories]
- **B** : 45 — « We engaged 45 participants » [p. 75 — International Human Duties Impact Stories]
- **Type** : INTERNAL_CONTRADICTION · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance L, non adoptée)* : 7 tables × 7 = 49 pourrait être la capacité prévue, 45 la présence réelle.
- **Cas de test** : « Combien de participants à l'événement 7x7 d'Ankara ? » → attendu `{"answer_mode": "report_conflict", "flag": "DQC-11"}` · **interdit** : Choisir 49 ou 45 sans signaler

### DQC-12 — Bridges Project : participants vs formés

- **A** : 35 — « Over three weeks, 35 participants engaged in intensive sessions led by 20 volunteer trainers » [p. 91 — JCI RISE Impact Stories]
- **B** : ≥ 200 — « 200+ youth trained » [p. 91 — JCI RISE Impact Stories]
- **Type** : SCOPE_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : B pourrait couvrir plusieurs cohortes ou la durée totale du projet ; la base des 75 % / 15 % est donc inconnue.
- **Cas de test** : « Combien de jeunes le Bridges Project a-t-il placés en emploi ? » → attendu `{"answer_mode": "cannot_compute", "flag": "DQC-12", "reason": "75% sans base connue (35 ou 200+)"}` · **interdit** : Répondre 26 (75% de 35) ; Répondre 150 (75% de 200)

### DQC-13 — Impulso NOA : 4 nouveaux membres = 20 %

- **A** : 22 — « directly connecting 22 advanced students with leading companies » [p. 94 — JCI RISE Impact Stories]
- **B** : 0.2 — « four new JCI Salta members—representing 20% of all participants » [p. 94 — JCI RISE Impact Stories]
- **C** : 0.1818 — *calculé* (`4 / 22`), SEMANTIC_INTERPRETATION
- **Type** : ARITHMETIC_ERROR, AGGREGATION_BASE_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance L, non adoptée)* : La base 'all participants' peut différer des 22 étudiants (20 participants → 20 %).
- **Cas de test** : « Quel pourcentage des participants d'Impulso NOA est devenu membre ? » → attendu `{"answer_mode": "published_vs_calculated", "flag": "DQC-13"}` · **interdit** : Déduire 20 participants ; Corriger 20% en 18%

### DQC-14 — Global Youth Dialogue : présents vs membres/non-membres

- **A** : 662 — « 662 live attendees » [p. 122 — Global Youth Dialogue 2025]
- **B** : 679 — « JCI Members 679 (79.6%) » [p. 123 — Global Youth Dialogue 2025]
- **C** : 174 — « Non-Members 174 (20.4%) » [p. 123 — Global Youth Dialogue 2025]
- **D** : 853 — *calculé* (`679 + 174`), SEMANTIC_INTERPRETATION
- **Type** : AGGREGATION_BASE_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : La ventilation membres/non-membres porte probablement sur les inscrits ou une autre base que les présents en direct.
- **Cas de test** : « Combien de non-membres ont assisté en direct au Global Youth Dialogue ? » → attendu `{"answer_mode": "cannot_compute", "flag": "DQC-14"}` · **interdit** : Répondre 135 (20,4% de 662)

### DQC-15 — ECOSOC side event : présents > inscrits

- **A** : ≥ 1160 — « 1,160+ registrants » [p. 117 — Impact Through Hosted and Partner Events]
- **B** : ≥ 1500 — « 1,500+ live participants » [p. 117 — Impact Through Hosted and Partner Events]
- **Type** : PLAUSIBILITY_FLAG · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance L, non adoptée)* : Possible si l'accès live ne nécessitait pas d'inscription ; non expliqué.
- **Cas de test** : « Quel a été le taux de présence de l'événement RISE to the Challenge ? » → attendu `{"answer_mode": "cannot_compute", "flag": "DQC-15"}` · **interdit** : Répondre 129%

### DQC-16 — ODD du programme JCI RISE

- **A** : 1, 3, 8, 9, 11, 12, 16, 17 — « JCI RISE • SDG 1: Addresses community challenges to reduce poverty through local initiatives. » [p. 26 — Programs and Initiatives with SDG Alignment]
- **B** : 3, 8, 10 — « The initiative positions JCI as a key contributor to SDG 3 (Good Health & Well-being), SDG 8 (Decent Work & Economic Growth), and SDG 10 (Reduced Inequalities). » [p. 85 — JCI RISE Projects]
- **Type** : MAPPING_INCONSISTENCY · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : A = alignement détaillé du programme, B = mise en avant de 3 ODD 'clés' ; SDG 10 absent de A.
- **Cas de test** : « Quels ODD le programme JCI RISE couvre-t-il ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-16"}` · **interdit** : Fusionner silencieusement en {1,3,8,9,10,11,12,16,17}

### DQC-17 — Libellés des piliers RISE

- **A** : Sustain and Rebuild Economies, Workforce Empowerment, Mental Health Awareness — « Sustain and Rebuild Economies: Support businesses, entrepreneurs, and SMEs. » [p. 85 — JCI RISE Projects]
- **B** : Sustaining and Rebuilding Economies, Workforce Motivation, Preserving Mental Health — « RISE Pillars Covered » [p. 85 — JCI RISE Projects]
- **Type** : LABEL_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Même trois piliers, libellés différents (objectifs vs graphique) ; correspondance 1↔1 par thème.
- **Cas de test** : « Normaliser 'pilier santé mentale' vers un pilier RISE officiel. » → attendu `{"answer_mode": "map_with_synonyms", "flag": "DQC-17", "expected_candidates": ["Preserving Mental Health", "Mental Health Awareness"]}` · **interdit** : Inventer un 4e pilier ; Ne retourner qu'un libellé sans signaler l'autre

### DQC-18 — Pourcentages dont la somme vaut 100,01 %

- **A** : 0.403, 0.2804, 0.3167 — « Sustaining and Rebuilding Economies 40.30% … Preserving Mental Health 28.04% … Workforce Motivation 31.67% » [p. 85 — JCI RISE Projects]
- **B** : 0.6704, 0.0915, 0.2191, 0.0191 — « 2025 Projects Reported per Area » [p. 86 — JCI RISE Projects]
- **C** : 1.0001 — *calculé* (`sum(A) and sum(B)`), SEMANTIC_INTERPRETATION
- **Type** : ROUNDING_OR_APPROXIMATION · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Arrondi à 2 décimales.
- **Cas de test** : « Recalculer le nombre de projets en Europe à partir de 1,91 % de 1000+. » → attendu `{"answer_mode": "cannot_compute_exact", "flag": "DQC-18", "reason": "base '1000+' non exacte"}` · **interdit** : Répondre 19 projets comme valeur exacte

### DQC-19 — Part des LO en Europe

- **A** : 0.158 — « Europe 17,623 11.9% 736 15.8% » [p. 8 — Membership Details]
- **B** : 0.159 — « Europe 736 (15.9%) » [p. 11 — Local Organizations]
- **C** : 0.1586 — *calculé* (`736 / 4641`), SEMANTIC_INTERPRETATION
- **Type** : ROUNDING_OR_APPROXIMATION · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Troncature (A) vs arrondi (B) de 15,86 %.
- **Cas de test** : « Quelle part des LO est en Europe ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-19"}`

### DQC-20 — Nom officiel de TOYP

- **A** : Ten Outstanding Young Persons of the World — « Ten Outstanding Young Persons of the World (TOYP) » [p. 54 — Ten Outstanding Young Persons of the World (TOYP)]
- **B** : Ten Outstanding Young Persons — « Ten Outstanding Young Persons (TOYP) » [p. 26 — Programs and Initiatives with SDG Alignment]
- **C** : Ten Outstanding Persons of the Year — « the Ten Outstanding Persons of the Year programs » [p. 113 — Corporate Sponsors Driving Shared Impact]
- **Type** : LABEL_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : C est probablement une erreur éditoriale ; A est le titre de section du programme.
- **Cas de test** : « Un texte local mentionne 'Ten Outstanding Persons of the Year'. À quel programme le rattacher ? » → attendu `{"answer_mode": "map_with_flag", "expected_program": "TOYP", "flag": "DQC-20"}` · **interdit** : Créer un nouveau programme

### DQC-21 — Chiffres d'événements externes à proximité des chiffres JCI

- **A** : ≥ 52000 — « which drew over 52,000 participants from 130+ countries » [p. 119 — Impact Through Hosted and Partner Events]
- **B** : ≥ 1000 — « which convened over 1,000 leaders from 100 countries » [p. 121 — Impact Through Hosted and Partner Events]
- **C** : 45 — « brought together 45 young human rights advocates from around the world » [p. 121 — Impact Through Hosted and Partner Events]
- **Type** : EXTERNAL_METRIC_ADJACENT · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Tailles d'événements organisés par des tiers (GITEX Africa, World Chambers Congress, OHCHR Youth Rights Academy) ; la participation JCI n'est pas chiffrée.
- **Cas de test** : « Combien de personnes JCI a-t-il touchées via ses événements partenaires en 2025 ? » → attendu `{"answer_mode": "exclude_external", "flag": "DQC-21"}` · **interdit** : Ajouter 52,000 aux bénéficiaires ou participants JCI

### DQC-22 — ODD 11 cité deux fois (SDGs Hunt)

- **A** : 11 — « SDG 11: Sustainable Cities & Communities; SDG 1: No Poverty » [p. 89 — Community Impact Stories]
- **B** : 11 — « SDG 16: Peace,Justice & Strong Institutions,SDG 11: Sustainable Cities & Communities » [p. 89 — Community Impact Stories]
- **Type** : DUPLICATE_ENTRY · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Doublon de saisie ; 17 ODD distincts déclarés pour 4 heures de bénévolat (sur-tagging).
- **Cas de test** : « Combien d'ODD le projet SDGs Hunt couvre-t-il ? » → attendu `{"answer_mode": "raw_and_distinct", "raw_mentions": 18, "distinct": 17, "flag": "DQC-22"}` · **interdit** : Répondre 18 ODD

### DQC-23 — Pétitions IHD : pays par geographic_area

- **A** : 35, 45, 63, 48 — « Asia and the Pacific 54,921 (81.85%) from 35 Countries … America 3,656 (5.45%) from 45 Countries … Africa and the Middle East 6,867 (10.23%) from 63 Countries … Europe 1,657 (2.47%) from 48 Countries » [p. 73 — International Human Duties Initiative]
- **B** : 191 — *calculé* (`35 + 45 + 63 + 48`), SEMANTIC_INTERPRETATION
- **C** : 22 — « America 22 (19.3%) » [p. 10 — National Organizations]
- **Type** : SUSPICIOUS_COUNT · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance L, non adoptée)* : Les pays comptés sont peut-être ceux des signataires (hors réseau JCI) ; 45 pays pour America alors que l'Area compte 22 NO.
- **Cas de test** : « Dans combien de pays la pétition IHD a-t-elle été signée ? » → attendu `{"answer_mode": "report_conflict", "flag": "DQC-23", "note": "191 = somme non dédoublonnée"}` · **interdit** : Répondre 191 pays

### DQC-24 — Hétérogénéité des périodes de reporting

- **A** : 2024–2025 — « 1,000+ projects implemented (2024–2025) » [p. v — Executive Summary]
- **B** : 2025 — « Total Projects Reported for 2025 » [p. 85 — JCI RISE Projects]
- **C** : January–October 2025 — « From January to October 2025 » [p. 17 — Social Media Metrics]
- **D** : October 2024–August 2025 — « Total Contributions Received (USD) since October 2024 to August 2025 » [p. 96 — JCI Foundation]
- **E** : since 2022 — « Total Contributions Received (USD) since 2022 » [p. 96 — JCI Foundation]
- **F** : since October 6, 2025 — « Since the October 6, 2025 launch alone » [p. 21 — The New Face of JCI Online]
- **Type** : PERIOD_HETEROGENEITY · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Le rapport n'a pas de période de reporting unique.
- **Cas de test** : « Quel est le total des contributions et du nombre de projets pour 2025 ? » → attendu `{"answer_mode": "period_aware", "flag": "DQC-24"}` · **interdit** : Additionner des métriques de périodes différentes sans le dire

### DQC-25 — Part des membres d'America (graphique)

- **A** : 0.08 — « America 11,775 8.0% 492 10.6% » [p. 8 — Membership Details]
- **B** : 0.8 — « America 11,775 (80%) » [p. 8 — Membership Details]
- **Type** : TYPO_LIKELY · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance H, non adoptée)* : Le graphique (B) omet probablement la virgule ; 11,775 / 147,670 = 7,97 %.
- **Cas de test** : « Quelle part des membres est en America ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-25"}` · **interdit** : Répondre 80%

### DQC-26 — Utilisateurs actifs de jci.cc

- **A** : ≥ 8700 — « the website attracted more than 8,700 active users since its redesign launch from over 50 countries » [p. 21 — The New Face of JCI Online]
- **B** : 13351 — « 13,351 Total Active Users » [p. 22 — The New Face of JCI Online]
- **Type** : PERIOD_MISMATCH · **Résolution** : UNRESOLVED · `resolution: null`
- *Explication candidate (SEMANTIC_INTERPRETATION, confiance M, non adoptée)* : A = depuis le 6 octobre 2025 ; période de B non précisée.
- **Cas de test** : « Combien d'utilisateurs actifs sur jci.cc ? » → attendu `{"answer_mode": "multi_value_with_sources", "flag": "DQC-26"}` · **interdit** : Choisir une seule valeur


---

# V. REGISTRE DES DONNÉES VISUELLES NON EXTRAITES

> Règle P4 : `value = null`, `value_status = visual_data_not_extracted`. **Jamais 0, jamais une valeur déduite**, jamais les fragments de texte non associés. Le graphique lui-même (titre, page) est un OFFICIAL_JCI_FACT : on sait qu'il existe, pas ce qu'il contient.

| ID | Page — Section | Titre du graphique (citation) | Ce qui manque | Métriques V1 concernées | Statut |
|---|---|---|---|---|---|
| VDX-01 | 9 — International Presence – Operational Areas | « Global Presence (114 Countries) » | Liste des pays / National Organizations représentés sur la carte | M031 | `visual_data_not_extracted` |
| VDX-02 | 42 — Trainings at Area Conferences and World Congress | « Participation in Conferences » | Répartition des 1,969 participants par conférence (libellés présents, valeurs absentes) | M022 | `visual_data_not_extracted` |
| VDX-03 | 60 — JCI Events Area Conferences and World Congress | « National Organization Attendances per Area Conference (2025) » | Toutes les valeurs | M083 | `visual_data_not_extracted` |
| VDX-04 | 84 — Community Development Projects | « Primary SDGs Addressed / Secondary SDG » | Toutes les valeurs (distribution des ODD principaux et secondaires) | M014 | `visual_data_not_extracted` |
| VDX-05 | 97 — JCI Foundation Development Grants | « Amount of Grants (USD) Received per Year » | Association valeur ↔ année ↔ geographic_area · fragments non associés : 33, 28, 40 (**inutilisables**) | M115 | `visual_data_not_extracted` |
| VDX-06 | 98 — JCI Foundation | « Amount of Grants (USD) Received per Year / Number of Projects per Year per Area » | Association valeur ↔ année ↔ geographic_area · fragments non associés : 37,500, 28,600, 33,900, 39,000, 26,500, 64,500, 31,300, 21,100, 36,150, 27,800, 25,000, 37,000, 100,000, 130,000, 88,550, 89,800, 37,000 (**inutilisables**) | M115 | `visual_data_not_extracted` |
| VDX-07 | 118 — Impact Through Hosted and Partner Events | « RISE to the Challenge Attendees per Area » | Toutes les valeurs par geographic_area | M122 | `visual_data_not_extracted` |
| VDX-08 | 118 — Impact Through Hosted and Partner Events | « Languages per Area » | Toutes les valeurs (libellés Spanish, French, Japanese, English présents) | M122 | `visual_data_not_extracted` |
| VDX-09 | 123 — Global Youth Dialogue 2025 | « Gobal Youth Dialogue Attendees per Area » | Toutes les valeurs par geographic_area | M126, M127 | `visual_data_not_extracted` |

**Condition de déblocage** (identique pour les 9) : fournir une source visuelle exploitable (capture de la page ou données d'origine). Chaque valeur récupérée recevra alors sa propre citation OFFICIAL_JCI_FACT, sans toucher au reste.


## V.2 Graphiques lisibles dont l'association valeur ↔ libellé est interprétée (règle P13)

| ID | Page | Valeurs (OFFICIAL_JCI_FACT, extracted) | Association proposée | Règle | Confiance |
|---|---|---|---|---|---|
| VDA-01 | 28 | 25, 12, 24, 9, 38 | 2024 JCI World Congress (Taoyuan, Taiwan) → 25 ; 2025 JCI Conference of America (Roatán) → 12 ; 2025 JCI Africa and the Middle East Conference (Durban) → 24 ; 2025 JCI European Conference (Herning) → 9 ; 2025 JCI Asia and the Pacific Conference (Ulaanbaatar) → 38 | `CHART-ORDER` : labels and values appear in the same order in the text layer; order not guaranteed | L |
| VDA-02 | 60 | 162/5,012, 82/364, 116/429, 168/1,068 | ASPAC (Ulaanbaatar) → 162 ; America (Roatán) → 82 ; Africa & Middle East (Durban) → 116 ; Europe (Herning) → 168 | `CHART-DENOMINATOR-MATCH` : each denominator equals the attendee total published for that conference on p. 59 | H |

Conséquence : pour VDA-01 (CYE), toute ventilation par conférence est SEMANTIC_INTERPRETATION de confiance faible. Seul le total « 108 entrepreneurs » est OFFICIAL_JCI_FACT.

---

# CHECKLIST DE VÉRIFICATION V2

| Contrôle | Résultat |
|---|---|
| Couverture du document | Couche texte : 100 % (couverture → p. 174). Graphiques non lisibles : 9 objets VDX, `value = null`, statut `visual_data_not_extracted` |
| P0 appliquée | Aucun OFFICIAL_JCI_FACT sans page + section + citation (validateur V2 : 0 violation) |
| IAOOI présenté comme cadre JCI ? | **Non**. Section B titrée PROPOSED_STANDARD ; chaque classe = SEMANTIC_INTERPRETATION ; `iaooi_class` porte `standard: PROPOSED_STANDARD:IAOOI-v0` |
| Taxonomie | L1 area_of_opportunity, L2 programmes nommés, L8 ODD = OFFICIAL_JCI_FACT ; L3–L7 = PROPOSED_STANDARD ; rattachements = SEMANTIC_INTERPRETATION |
| « Area » | 2 concepts, 6 règles AREA-1…6, 22 occurrences du rapport classées dont 3 `AMBIGUOUS_AREA` non tranchées ; aucune clé `area` dans les JSON (V9) |
| Incohérences | 26 objets DQC (24 V1 + 2), **tous UNRESOLVED**, `resolution = null`, explications candidates non adoptées, 1 cas de test chacun |
| Données visuelles | 9 VDX + 2 associations interprétées (VDA-01 confiance L, VDA-02 confiance H) |
| JSON | Squelette à 11 clés respecté pour les 6 objets |
| Validateur sur les livrables | `== jci_tier1_fixtures_v2.json: 0 violation(s) · layers: {'PROPOSED_STANDARD': 166, 'OFFICIAL_JCI_FACT': 93, 'SEMANTIC_INTERPRETATION': 201, 'LOCAL_REPORTED_FACT': 168}` · `== jci_data_quality_registry_v2.json: 0 violation(s) · layers: {'OFFICIAL_JCI_FACT': 87, 'SEMANTIC_INTERPRETATION': 36}` |
| Validateur sur des cas volontairement faux | 11 violations détectées sur 9 cas pièges (`validator_negative_tests.json`) : citation manquante, 0 sur donnée visuelle, calcul marqué officiel, classe IAOOI marquée officielle, clé `area`, interprétation sans règle, déclaration locale marquée officielle, conflit résolu en douce, estimation sans méthode |
