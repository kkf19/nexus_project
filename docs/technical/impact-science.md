# NEXUS — Science de l'impact v1 : classification, collecte, dashboard

**Statut** : PROPOSED — rédigé par le Product Architect le 2026-09-19, à partir des constats du Product Owner (PO). À valider par le second Product Architect, puis à transformer en consignes pour l'agent de code.
**Emplacement** : `docs/technical/impact-science.md`. C'est le seul nouveau document. Les autres fichiers (`taxonomy.config.json`, `mvp-scope.md`, `data-model.md`, `dev-brief.md`) sont **mis à jour, ni renommés ni remplacés**.
**Ce qui ne change pas** : la provenance, la règle « inconnu ≠ 0 », les refus d'agrégation, la séparation membres / public externe, la distinction ressources / productions / résultats, la complétion guidée (D-17), `outcome_status` (D-20) et le profil de l'OL (D-18).

---

## 0. En une phrase

> Pour chaque projet, NEXUS répond à quatre questions dans cet ordre : **Qu'est-ce qui a été fait ?** (famille d'activité) → **Dans quel(s) domaine(s) JCI ?** (les 4 Areas) → **Si Community Impact : est-ce RISE ?** → **Quels ODD ?**. Ensuite seulement, il mesure : pour qui, avec quelles ressources, avec quel résultat.

```
PROJET
 ├─ 1. FAMILLE D'ACTIVITÉ   (ce qui a été fait)      1..n   liste canonique + AUTRE
 │     └─ programme officiel JCI ? (CYE, Twinning…)  0..1   facultatif
 ├─ 2. AREA(S)              (où JCI crée la valeur)  1..n   exactement 1 principale
 │     └─ si COMMUNITY IMPACT ∈ areas
 ├─ 3.    RISE : oui / non  → pilier(s) 1..3 si oui
 ├─ 4. ODD                  (à quoi ça contribue)    1..n   aucun plafond, 1 justification par ODD
 └─ 5. MESURES              pour qui · ressources · résultat
```

---

## 1. Ce que les constats du PO changent dans nos décisions

| Décision actuelle | Ce qui change | Nouveau statut proposé |
|---|---|---|
| D-07 — trois axes indépendants : Area, Programme, ODD | Le **programme n'est plus un axe**. Un programme JCI (CYE, Twinning, Public Speaking…) est une **activité** : il se range dans une famille d'activité, comme n'importe quelle activité locale équivalente. RISE sort de l'axe programme et devient une **sous-classification de Community Impact** | D-07 → **SUPERSEDED** par D-23 / D-24 |
| D-08 — type d'activité déduit, sans liste imposée, jamais affiché | La famille d'activité devient la **première dimension** : liste canonique, confirmée par l'OL, affichée dans le dashboard | D-08 → **SUPERSEDED** sur ce point par D-25 |
| R2 — 1..n Areas | Ajout d'un rôle : **exactement 1 Area principale**, 0..n secondaires | D-26 |
| R5 — 1 ODD principal, n secondaires, plafond recommandé | Aucun plafond. Chaque ODD doit être justifié par une phrase du texte | D-27 |
| D-16 — 4 confirmations bloquantes | La liste des confirmations évolue (§5) | D-28 |

### Cohérence avec les chiffres JCI (point à connaître pour le pitch)

Le rapport JCI 2025 donne **53,47 % de projets RISE** [p.85] et **44,64 % de projets Community Impact** [p.86]. Si RISE est une sous-partie de Community Impact, comment RISE peut-il dépasser Community Impact ?

- **Explication compatible avec le modèle du PO (INFERENCE)** : la répartition par Area de la p.86 fait exactement 100 % alors que JCI écrit « some projects may fall under 2 or more Areas ». JCI ne compte donc probablement que l'**Area principale** de chaque projet. Un CYE ouvert au public est principalement Business & Entrepreneurship, secondairement Community Impact, et peut être RISE. Il gonfle la part de RISE sans compter dans les 44,64 % de CI.
- **Conséquence** : la règle NEXUS est « RISE seulement si Community Impact figure parmi les Areas, **principale ou secondaire** ». C'est précisément ce qui rend le rôle principal/secondaire indispensable.
- Le conflit reste enregistré comme non résolu côté JCI. NEXUS ne le tranche pas à la place de JCI.

*Note de précision : le rapport indique 53,47 % de RISE, pas 45 %. Les 44,64 % correspondent à la part de Community Impact.*

---

## 2. Dimension 1 — Famille d'activité

### Principe

- La famille d'activité décrit **la forme de l'action** : former, débattre, concourir, planter, sensibiliser, jumeler…
- Elle ne décrit pas le thème (santé, éducation…). Le thème est porté par les ODD.
- Un projet peut avoir **plusieurs familles**. Exemple : un bootcamp avec un concours de pitch final → `ENTREPRENEURSHIP_TRAINING` + `BUSINESS_COMPETITION`.
- Chaque famille a une **Area habituelle** (`home_area`). C'est une **suggestion** pour l'IA, jamais une règle d'héritage : l'Area du projet se décide en §3.
- Chaque Area possède un code **AUTRE** avec un libellé libre obligatoire (« quelle activité a renforcé le développement individuel, qui n'est ni un débat, ni… ? »). Si un même libellé AUTRE revient souvent, c'est le signal pour ajouter une famille à la version suivante de la taxonomie.

### Programme officiel JCI (champ facultatif)

À côté de la famille, un champ facultatif : **« Est-ce l'édition locale ou nationale d'un programme officiel JCI ? »** (CYE, Public Speaking Competition, Debating Championship, Twinning, TOYP, JIB, Global Leadership Masterclass…). La valeur par défaut est « non ».

- Un concours de prise de parole organisé par une OL = `PUBLIC_SPEAKING`, programme officiel = non.
- La JCI Public Speaking Competition = `PUBLIC_SPEAKING`, programme officiel = PSC.
- **Les deux alimentent ensemble le compteur « Public Speaking » d'Individual Development.** C'est exactement la limite du rapport JCI actuel que NEXUS corrige : aujourd'hui, JCI ne compte que ses propres programmes.

### Liste canonique v1 (PROPOSED_STANDARD — vocabulaire NEXUS, pas JCI)

La colonne « Programmes JCI rattachés » est **OFFICIAL_JCI_FACT** (source : jci.cc/what-we-do, consulté le 2026-09-19, et rapport 2025). Le reste est une proposition NEXUS.

#### Individual Development — `ID`

| Code | Libellé | Définition | Exemples | Programmes JCI rattachés |
|---|---|---|---|---|
| `TRAINING_WORKSHOP` | Formation / atelier | Session d'apprentissage ponctuelle (quelques heures à quelques jours) | atelier leadership, formation gestion du temps, séminaire | Trainings at Area Conferences & World Congress |
| `CERTIFICATION_TRAINING` | Formation certifiante / de formateurs | Parcours qui délivre une certification ou forme des formateurs | CNT, CAT, formation de formateurs nationaux | Skills Development (CNT, CAT, Global Trainers) |
| `ACADEMY_MASTERCLASS` | Académie / masterclass / programme long | Parcours structuré en plusieurs modules sur plusieurs semaines | académie du leadership, masterclass, cycle de formation | JCI Global Leadership Masterclass |
| `ONLINE_COURSE` | Cours en ligne / webinaire | Apprentissage à distance | webinaire, cours SDG Academy | Mastering Sustainable Leadership ; Becoming Global Citizens |
| `PUBLIC_SPEAKING` | Prise de parole en public | Concours, atelier ou club d'éloquence | concours d'éloquence d'OL, club de prise de parole | JCI Public Speaking Competition |
| `DEBATE` | Débat | Concours ou session de débat contradictoire | tournoi de débat inter-OL | JCI Debating Championship |
| `MENTORING_COACHING` | Mentorat / coaching | Accompagnement individuel ou en petit groupe dans la durée | parrainage de nouveaux membres, coaching de carrière | Training Mentors |
| `ID_OTHER` | Autre (préciser) | — | — | — |

#### Business & Entrepreneurship — `BE`

| Code | Libellé | Définition | Exemples | Programmes JCI rattachés |
|---|---|---|---|---|
| `ENTREPRENEURSHIP_TRAINING` | Formation à l'entrepreneuriat | Formation centrée sur la création ou la gestion d'entreprise | bootcamp, atelier business plan, éducation financière | — |
| `BUSINESS_COMPETITION` | Concours d'entrepreneurs / pitch | Compétition entre porteurs de projets ou d'entreprises | concours de pitch, prix du jeune entrepreneur | Creative Young Entrepreneur (CYE) Competition |
| `INCUBATION_ACCELERATION` | Incubation / accélération | Accompagnement structuré d'entreprises dans la durée | programme d'accélération, incubateur | CYE Accelerator Program |
| `BUSINESS_NETWORKING` | Rencontres d'affaires | Mise en relation d'entreprises ou d'entrepreneurs | business matching, salon, afterwork d'affaires | JCI in Business (JIB) |
| `ENTREPRENEUR_MENTORING` | Mentorat d'entrepreneurs | Accompagnement individuel d'entrepreneurs | parrainage par des chefs d'entreprise | — |
| `BE_OTHER` | Autre (préciser) | — | — | — |

#### International Cooperation — `IC`

| Code | Libellé | Définition | Exemples | Programmes JCI rattachés |
|---|---|---|---|---|
| `TWINNING` | Jumelage | Accord ou activité entre organisations JCI de pays différents | jumelage Bénin–Canada, Buddy Project | JCI Twinning |
| `INTERNATIONAL_EVENT` | Congrès / conférence internationale | Participation à un rassemblement JCI multi-pays, ou organisation d'un tel rassemblement | CAMO, conférence de zone, congrès mondial | Area Conferences ; World Congress |
| `INTERNATIONAL_EXCHANGE` | Échange / délégation / visite | Déplacement ou accueil de membres d'un autre pays | délégation, échange culturel | — |
| `CROSS_BORDER_PROJECT` | Projet transfrontalier | Projet mené conjointement par des organisations de plusieurs pays | projet commun entre deux OL de deux pays | — |
| `INTERNATIONAL_RECOGNITION` | Distinction internationale | Candidature ou désignation à une distinction JCI internationale | sélection nationale TOYP | Ten Outstanding Young Persons (TOYP) |
| `IC_OTHER` | Autre (préciser) | — | — | — |

#### Community Impact — `CI`

La définition JCI des Community Development Projects [p.84] cite les thèmes « health, education, environment, gender equality, and poverty alleviation ». Dans NEXUS, **les thèmes sont lus à travers les ODD**. Les familles ci-dessous décrivent ce qui a été **fait** pour la communauté.

| Code | Libellé | Définition | Exemples |
|---|---|---|---|
| `AWARENESS_CAMPAIGN` | Sensibilisation / campagne | Informer ou changer des comportements dans la population | campagne dépistage, sensibilisation santé mentale, caravane |
| `COMMUNITY_TRAINING` | Formation du public | Former des non-membres à une compétence utile | formation de jeunes sans emploi, alphabétisation numérique |
| `HEALTH_ACTION` | Action de santé | Soins, dépistage, don de sang, consultations | journée de dépistage, collecte de sang |
| `ENVIRONMENTAL_ACTION` | Action environnementale | Action physique sur l'environnement | plantation d'arbres, nettoyage de plage, recyclage |
| `DONATION_DISTRIBUTION` | Dons / distribution | Remise de biens à des bénéficiaires | kits scolaires, vivres, fournitures |
| `INFRASTRUCTURE_EQUIPMENT` | Infrastructure / équipement | Construire, réhabiliter ou équiper un lieu collectif | forage, salle de classe, bibliothèque |
| `FUNDRAISING` | Collecte de fonds | Levée de fonds pour une cause | gala, course solidaire |
| `ADVOCACY` | Plaidoyer | Démarche auprès des décideurs | pétition, proclamation, rencontre avec une mairie |
| `CI_OTHER` | Autre (préciser) | — | — |

Programme JCI rattaché à CI : **JCI RISE**. Il n'est pas une famille d'activité : c'est la classification du §4.

#### Transversal (sans Area habituelle)

| Code | Libellé | Remarque |
|---|---|---|
| `CONFERENCE_FORUM` | Conférence / panel / forum | Area selon le public et le sujet |
| `NETWORKING_SOCIAL` | Réseautage / événement social | Souvent ID (interne) |
| `OTHER` | Autre (préciser) | Si aucune Area n'est évidente |

**Exclu du reporting d'impact** : l'administration interne (assemblée générale, élections, réunion de bureau). Si c'est le seul contenu d'une saisie, NEXUS le signale : « activité de gouvernance, pas un projet ».

---

## 3. Dimension 2 — Les 4 Areas (colonne vertébrale)

### Définitions

Définitions officielles citées mot pour mot (source : jci.cc/what-we-do, consulté le 2026-09-19 ; définitions courtes du rapport 2025 p.24-25 déjà présentes dans `taxonomy.config.json`) :

| Area | Définition officielle JCI | Programmes que JCI y range |
|---|---|---|
| **Business & Entrepreneurship** | « JCI empowers young leaders to innovate, grow, and succeed in the dynamic world of business and entrepreneurship. » | CYE Competition, CYE Accelerator, JIB |
| **International Cooperation** | JCI's global events foster « leadership and cross-border collaboration » | TOYP, Area Conferences, World Congress |
| **Individual Development** | « JCI offers diverse opportunities for growth through training, masterclasses, workshops, and online courses. » | JCI Global Leadership Masterclass |
| **Community Impact** | « JCI equips members with tools and resources to lead impactful projects that address community needs. » | JCI RISE |

### Règles opérationnelles NEXUS (PROPOSED — c'est ce qui empêche l'IA de classer en l'air)

L'IA suit cet ordre. Elle cite la phrase du texte qui justifie chaque Area retenue.

| Area | Retenir si… (signaux d'inclusion) | Ne pas retenir si… (signaux d'exclusion) |
|---|---|---|
| **ID** | L'activité **développe les compétences, la confiance ou le leadership de personnes** : formation, débat, prise de parole, mentorat, académie | Le développement de compétences n'est qu'un moyen accessoire d'une action communautaire (exemple : 10 bénévoles briefés avant une plantation) |
| **BE** | L'activité vise la **création, la croissance ou la mise en relation d'entreprises ou d'entrepreneurs** | La simple présence de sponsors ou de partenaires privés |
| **IC** | L'activité implique **au moins deux pays** : jumelage, événement multi-pays, projet ou échange transfrontalier | Un événement national qui a quelques invités étrangers sans collaboration réelle |
| **CI** | Le **public bénéficiaire est externe** (non-membres, ou public ouvert à tous) **et** l'activité répond à un **besoin de la communauté** | Le public est **exclusivement composé de membres JCI** : formations de congrès, formations officielles internes, académies internes, jumelages, CAMO, congrès mondial. **Règle dure : public 100 % interne → jamais CI** |

**Area principale** = celle qui décrit le mieux l'objectif premier du projet. Toutes les autres Areas retenues sont secondaires.

### Exemples de référence (ils deviendront des tests)

| Projet | Famille | Areas | RISE | ODD (exemples) |
|---|---|---|---|---|
| Plantation de 500 arbres avec des lycéens | `ENVIRONMENTAL_ACTION` | CI (principale) | Non — aucun pilier concerné | 13, 15 |
| Concours d'éloquence ouvert aux étudiants de la ville | `PUBLIC_SPEAKING` | ID (principale), CI (secondaire : public externe) | Non | 4 |
| Concours d'éloquence interne à l'OL | `PUBLIC_SPEAKING` | ID uniquement | Non applicable | 4 |
| Édition nationale du CYE, ouverte au public | `BUSINESS_COMPETITION` + programme CYE | BE (principale), CI (secondaire) | Oui — pilier Économies | 8, 9 |
| Formation de 80 membres au congrès national | `TRAINING_WORKSHOP` | ID uniquement | Non applicable | 4 |
| Jumelage JCI Bouaké – JCI Montréal | `TWINNING` | IC uniquement | Non applicable | 17 |
| Formation de 100 jeunes sans emploi + mise en relation avec des employeurs | `COMMUNITY_TRAINING` + `BUSINESS_NETWORKING` | CI (principale), ID (secondaire) | Oui — pilier Main-d'œuvre | 4, 8 |
| Caravane de sensibilisation au stress des étudiants | `AWARENESS_CAMPAIGN` | CI | Oui — pilier Santé mentale | 3 |

---

## 4. Dimension 3 — RISE (uniquement si CI figure parmi les Areas)

- **Définition officielle** [p.85] : « JCI RISE (Rebuild, Invest, Sustain, Evolve) is JCI's flagship initiative addressing economic recovery, workforce empowerment, and mental health. »
- **Question posée** : uniquement si CI figure parmi les Areas, principale ou secondaire. Réponse : oui ou non. Si c'est oui, choisir 1 à 3 piliers.
- **Libellés affichés** : ceux du site JCI actuel (vérifiés le 2026-09-19). Le rapport emploie deux autres jeux de libellés (conflit DQC-17, laissé ouvert).

| Pilier (libellé officiel) | Retenir si… (critère NEXUS) | Ne relève pas de ce pilier… |
|---|---|---|
| **Sustaining and rebuilding economies** | Soutien direct à des entreprises, entrepreneurs, PME, activités génératrices de revenus. Rapport p.85 : « Support businesses, entrepreneurs, and SMEs » | Collecte de fonds caritative sans dimension économique |
| **Motivating the workforce** | Employabilité, compétences professionnelles, insertion, placement, motivation des travailleurs | Formation scolaire générale sans visée professionnelle |
| **Preserving mental health and well-being** | Santé mentale, bien-être psychologique, stress, soutien psychosocial | Santé physique seule (dépistage, don de sang) → non RISE |

**RISE = oui** veut dire : le projet remplit le critère d'au moins un pilier, l'IA le justifie par une phrase du texte, et l'OL le confirme. La simple présence du mot « RISE » dans le texte ne suffit pas. Dans l'interface, l'affichage est « Aligné RISE — confirmé par l'OL ».

---

## 5. Dimension 4 — ODD

- De **1 à n** ODD, **sans plafond**. Tout ODD réellement touché est coché.
- **Garde-fou contre le sur-étiquetage** (le rapport JCI déclare les 17 ODD pour un projet de 4 heures, p.89) : chaque ODD porte **une phrase de justification tirée du texte**. Un ODD sans justification n'est pas proposé par l'IA.
- **ODD principal** : on garde exactement 1 ODD principal. Ce n'est pas une limite, c'est l'information « quel ODD est au cœur du projet ». JCI emploie la même distinction (« Primary SDGs / Secondary SDG », p.84) et elle est déjà codée. *Point à valider (Q4).*
- Correspondances ODD ↔ Area ou pilier RISE publiées par JCI : ce sont des **indices** pour l'IA, jamais des règles automatiques.

---

## 6. Dimension 5 — Mesures : ce que l'on collecte

On part du dashboard pour déterminer ce qu'on demande. Chaque bloc du dashboard (§7) a besoin de quatre familles de données :

| Bloc de données | Question au SG | Champs (existants, sauf ★) | Obligatoire |
|---|---|---|---|
| **Quoi** | « Racontez votre projet » | texte libre ; ★ familles d'activité (IA) ; ★ programme officiel JCI (facultatif) | oui (famille) |
| **Où / alignement** | — (l'IA propose, le SG confirme) | Areas ★ + principale ; ★ RISE oui/non + piliers ; ODD + justification | oui |
| **Pour qui** | C2, C3 | participants / bénéficiaires, direct / indirect / audience, interne / externe / mixte | oui |
| **Avec quoi** | C4, C5 | bénévoles, heures de bénévolat | oui |
| **Quel résultat** | C7 | `outcome_status` : mesuré / suivi prévu / aucun | oui |
| **Quand / qui déclare** | C1 + compte OL | période, année, OL, pays, zone | oui |

**Hors MVP** : budget, nombre de sessions par famille, entité « Activité » distincte du projet. Pour le MVP, **1 saisie = 1 projet = 1 activité réalisée** par famille déclarée. C'est vrai pour l'immense majorité des projets d'OL. Le cas « un projet regroupe 7 activités » est documenté comme évolution.

### Confirmations humaines (remplace D-16)

Le SG voit une fiche préremplie dans l'ordre des 4 questions. Il confirme ou corrige chaque bloc :

1. Famille(s) d'activité (+ libellé si AUTRE)
2. Areas + Area principale
3. RISE oui/non + piliers — affiché **seulement** si CI est coché
4. ODD (+ principal)
5. Public interne / externe / mixte
6. Type de comptage (direct / indirect / audience)
7. Résultat (`outcome_status`)

Le programme officiel JCI est facultatif et n'est pas bloquant.

---

## 7. Le dashboard

### Principe d'affichage

Deux lectures, jamais mélangées :

- **CE QUE JCI A FAIT** : activités et projets, par Area et par famille.
- **CE QUI A CHANGÉ** : personnes touchées, productions, résultats mesurés, sous le libellé « Impact » (D-22).

Les ressources (bénévoles, heures) sont affichées **à côté**, jamais sous « Impact ».

### Écran 1 — Vue d'ensemble (filtres : année, zone, pays, OL)

| Indicateur | Règle de calcul |
|---|---|
| Projets | nombre de **projets uniques** |
| Personnes touchées — public externe | somme des bénéficiaires **directs externes**. Jamais l'audience (vues, followers), jamais le public indirect |
| Membres JCI mobilisés / formés | somme séparée, jamais additionnée au public externe (R7) |
| Heures de bénévolat | somme, projets uniques |
| Projets avec résultat mesuré | nombre de projets en `outcome_status = measured` |
| Projets RISE | nombre, et % des projets CI |
| Pays / OL actives | nombre distinct |

### Écran 2 — Un bloc par Area (4 blocs identiques)

Exemple pour **Individual Development — 2026** :

```
INDIVIDUAL DEVELOPMENT                         212 projets (dont 38 hors Area principale)
─────────────────────────────────────────────
Ce qui a été fait
  Formations / ateliers ............... 57
  Débats .............................. 25
  Prise de parole en public ........... 18   (dont 2 éditions officielles JCI)
  Formations certifiantes ............. 14
  Mentorat ............................ 9
  Autre ............................... 7   → voir les libellés
Ressources
  Bénévoles 640 · Heures 4 820
Impact
  Membres formés 3 100 · Public externe formé 1 450 · Projets avec résultat mesuré 31
ODD les plus cités : 4 · 5 · 8
```

Règles :
- Un projet multi-Area apparaît **dans chaque bloc** de ses Areas, avec la mention « Area secondaire ». Dans la vue d'ensemble, il n'est compté **qu'une fois**. Le compteur « Projets » d'un bloc = nombre de projets d'Area ; le total global = nombre de projets uniques. **La somme des 4 blocs n'est jamais affichée comme un total.**
- Chaque ligne « famille » = nombre de projets qui déclarent cette famille dans cette Area.
- Cliquer sur un chiffre ouvre la liste des projets, puis le texte source (traçabilité, inchangée).
- Le bloc **Community Impact** ajoute : RISE oui/non, la répartition par pilier, et les ODD comme lecture thématique (santé = ODD 3, éducation = 4, environnement = 13/14/15, égalité femmes-hommes = 5, pauvreté = 1/2).

### Écran 3 — ODD

Pour chaque ODD : nombre de projets (principal / secondaire séparés), personnes touchées, projets avec résultat mesuré.

### Ce qui reste inchangé

Le moteur d'agrégation, les refus (unité non additive, audience ≠ bénéficiaires, interne ≠ externe, période manquante) et le panneau de traçabilité.

---

## 8. Consignes pour l'agent de code (après validation)

Principe : **modifier, pas reconstruire**. Aucun fichier renommé.

| # | Composant | Changement |
|---|---|---|
| 1 | `taxonomy.config.json` → v0.3.0 | Ajouter `activity_family` (§2) avec `code, label, definition, examples, home_area, official_programmes`. L'ancien `activity_type` devient un alias pour la compatibilité. Ajouter les définitions officielles des Areas et les signaux d'inclusion / d'exclusion (§3). Déplacer RISE sous CI avec ses critères (§4). L'axe `programme` devient `official_programme` (facultatif) |
| 2 | Base de données | `project_area_of_opportunity` : ajouter la colonne `role` (primary / secondary). Nouvelle table `project_activity_family` (`code`, `other_label`, `confirmed_by`). `project` : ajouter `rise_status` (yes / no / not_applicable). `project_rise_pillar` : inchangée. `project_programme` : conservée pour le programme officiel ; RISE n'y est plus écrit |
| 3 | Pipeline IA (`ai_pipeline.py`) | Classifier dans l'ordre famille → Areas (règles §3) → RISE si CI → ODD. Une justification (phrase citée) par valeur. Règle dure : public 100 % interne ⇒ pas de CI |
| 4 | Validation (`confirm_service.py`) | Exactement 1 Area principale. RISE obligatoire si CI, interdit sinon. Piliers ≥ 1 si RISE = oui. AUTRE ⇒ libellé obligatoire. ≥ 1 ODD, exactement 1 principal |
| 5 | Page de confirmation | Ordre des blocs du §6. Bloc RISE affiché seulement si CI est coché |
| 6 | Dashboard | Écrans 1-2-3 du §7, en réutilisant les rubriques existantes (ressources / impact / portée) |
| 7 | Tests | Les 8 exemples du §3 deviennent des fixtures de classification |

---

## 9. Décisions proposées (à inscrire dans `mvp-scope.md` après validation)

| # | Décision proposée |
|---|---|
| D-23 | Les programmes JCI sont des activités : ils se rangent dans une famille d'activité et un champ facultatif « programme officiel » les identifie. L'axe Programme de D-07 est supprimé |
| D-24 | RISE est une sous-classification de Community Impact : question oui/non posée seulement si CI figure parmi les Areas (principale ou secondaire) ; 1 à 3 piliers si oui |
| D-25 | La famille d'activité est la 1ʳᵉ dimension : liste canonique v1 (§2), 1..n par projet, AUTRE + libellé libre, confirmée par l'OL |
| D-26 | Areas : 1..n, exactement 1 principale. Public 100 % interne ⇒ jamais CI |
| D-27 | ODD : 1..n sans plafond, 1 principal, une justification par ODD |
| D-28 | Nouvelle liste des confirmations humaines (§6) |
| D-29 | Dashboard : deux lectures (fait / changé), un bloc par Area, projets uniques au global (§7) |

## 10. Questions ouvertes pour la validation

- **Q1** — Un projet ouvert au public mais sans « besoin communautaire » évident (exemple : un concours d'éloquence ouvert aux étudiants) est-il CI ? La proposition dit oui, en Area secondaire.
- **Q2** — La liste des familles du §2 : manque-t-il des activités JCI fréquentes ? Faut-il en retirer ?
- **Q3** — Les critères des piliers RISE (§4) correspondent-ils à la pratique JCI réelle ?
- **Q4** — Garde-t-on un ODD principal obligatoire (recommandé) ?
- **Q5** — Accepte-t-on « 1 saisie = 1 projet » pour le MVP, l'entité Activité étant reportée ?
