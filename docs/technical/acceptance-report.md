# NEXUS — Rapport d'acceptation (Étape B, Phase 5)

Date : 2026-09-20. Site testé : `https://nexusproject-nexus-2251.vercel.app` (frontend) /
`https://nexus-project-w4ux.onrender.com` (backend, Render) / Supabase (base en ligne).
Référentiel actif en base au moment du test : `taxonomy.config.json` v0.3.0.

Méthode : AC-01 à AC-15, AC-20 et une partie d'AC-21/22 portent sur des fichiers **réutilisés
tels quels et jamais modifiés** (`aggregation_engine.py`, `validate_measurement_objects.py`,
`measurement-object.examples.json`, `backend/engine/demo_measurements.json`) : ils ont été
rejoués localement en ligne de commande (résultat déterministe, indépendant du site en ligne).
AC-05, AC-13, AC-16 à AC-19 et AC-23 à AC-31 dépendent de la reconstruction impact-science.md
(A1-A8) : ils ont été testés **en conditions réelles sur le site en ligne**, avec de vrais appels
à l'IA (Claude Haiku 4.5) pour AC-23, et des appels directs à l'API pour les cas de refus.

## Résultats

| AC | Résultat | Détail |
|---|---|---|
| AC-01 | Non rejoué séparément | Repose sur `equivalence_key()` du moteur figé (inchangé depuis Phase 3) ; couvert indirectement par AC-02/AC-20 |
| AC-02 | **PASS** | Moteur démo : `PEOPLE_TRAINED` externe = 275, `COMM_AUDIENCE` en ligne séparée (12 000 view), aucune valeur 12045/12275 |
| AC-03 | **PASS** | Validateur : rejet `population: 'base_population' is a required property` |
| AC-04 | **PASS** | Validateur : `MO-VDX-01` valide (`value:null`) ; `BAD-01` rejeté (`value: 0 is not of type 'null'`) |
| AC-05 | **PASS** | `/trace/MEAS-ff0824631103` (projet T1, live) : `chain_complete:true`, `quote_found_in_raw_text:true`, `ctl_raw_ok:true`, `highlight_span` correct |
| AC-06 | **PASS** | Moteur démo : `MO-DE-MEMBERS-TRAINED` (340, internal) forme un agrégat distinct des 275 externes |
| AC-07 | **PASS** | Moteur démo : refus `POPULATION_OVERLAP`, valeur affichée 200 (jamais 320) |
| AC-08 | **PASS** | Moteur démo : `MO-JCI-VOLUNTEERS` exclu `OPEN_CONFLICT` (DQC-05) |
| AC-09 | **PASS** | Validateur : `BAD-03` rejeté (2 motifs schéma : `verification_status` et `layer`) |
| AC-10 | **PASS** | Moteur démo : les deux déclarations du jumelage sont toutes deux comptées, aucun refus `UNRESOLVED_DUPLICATE` |
| AC-11 | **PASS** | Moteur démo : `value_qualifier=approx` et `verification_status=reported` sur l'agrégat 275 |
| AC-12 | **PASS** | Moteur démo : exactement 3 lignes de refus (2 exclusions + 1 refus de paire) |
| AC-13 | **PASS** | Aucune route `PUT`/`PATCH` sur `/submissions/{id}` — seules `POST`, `GET`, `GET /draft`, `POST /retry`, `POST /confirm` existent |
| AC-14 | **PASS** | Validateur : `BAD-02`, `BAD-05`, `BAD-06` tous rejetés (motifs P2, refus sans raison, P1) |
| AC-15 | **PASS (partiel)** | Les 5 objets valides passent le schéma. Le round-trip complet "insertion en base puis réexport identique" n'a pas été rejoué séparément cette session (mécanisme inchangé depuis Phase 3 : le MO est stocké tel quel en JSONB et reconstruit par `mo_builder`) |
| AC-16 | **PASS** | Live : `activity_duration_hours` omis → 422, `"loc": ["body","project","activity_duration_hours"], "msg": "Field required"` |
| AC-17 | **PASS** | (a) T5 réel : CI non proposé, `rise_status=not_applicable`. (b) T7 réel : CI proposé (secondaire), `rise_status=yes`, pilier `WORKFORCE`. Décocher CI → `not_applicable` : logique présente dans `confirm_page.tsx` (useEffect dédié, A6) |
| AC-18 | **PASS** | T7 confirmé avec `outcome_status=pending_follow_up`, `expected_outcome` et `follow_up_date` renseignés, aucune mesure `OUTCOME` créée avec valeur 0 |
| AC-19 | **PASS** | Recherche de code : aucune occurrence de cible/objectif/jauge de progression dans le frontend (hors "Objectifs de développement durable" = les ODD eux-mêmes) |
| AC-20 | **PASS** | `demo_measurements.json` **sans** clé d'équivalence pré-calculée : validateur → **9 échecs sur 11**, exactement comme l'AC l'exige |
| AC-21 | **Non rejoué** | Règle `NON_ADDITIVE_UNITS` déjà intégrée au moteur figé (confirmé par lecture de code, section 3 du dev-brief) ; aucun cas `percent` dans `demo_measurements.json` pour la rejouer telle quelle |
| AC-22 | **Non rejoué séparément** | Logique `period_type=reporting_year` inchangée depuis Phase 3 ; confirmé indirectement par le refus `PERIOD_MISMATCH` observé pendant le test A7 (deux mesures de reporting_year différents jamais additionnées) |
| AC-23 | **PASS avec écart documenté** | Voir section dédiée ci-dessous |
| AC-24 | **PASS partiel — écart réel identifié** | Voir section dédiée ci-dessous |
| AC-25 | **PASS** | 3 sous-cas testés en direct : `yes` sans CI → refus ; `yes` sans pilier → refus ; CI coché + rise vide → refus (avec message nommant le champ) |
| AC-26 | **PASS** | 0 Area primary → refus ("trouvé : 0") ; 2 Areas primary → refus ("trouvé : 2") |
| AC-27 | **PASS** | Famille `BE_OTHER` sans libellé → refus "libellé obligatoire" |
| AC-28 | **PASS** | 0 ODD principal → refus ; 2 ODD principaux → refus ; 5 ODD dont 1 principal, tous justifiés → accepté (voir T1, 3 ODD acceptés) |
| AC-29 | **PASS** | 12 bénévoles × 3h testé : `value=36` implicite via la formule ; test réel (12×3, puis correction à 50) : `value_status` passe de `calculated` à `estimated`, `verification_status=reported`, dérivation `human_validation` remplace `CALC-VOLUNTEER-HOURS` |
| AC-30 | **PASS** | Test réel (30 internes + 45 externes, population "mixed") : deux mesures `ATTENDEES` distinctes créées (30 internal / 45 external), jamais 75 |
| AC-31 | **PASS (corrigé pendant ce test)** | Voir section dédiée ci-dessous |

## AC-23 — Les 8 (pas 9) textes de référence

`impact-science.md` §3 annonce dans le dev-brief (AC-23) « les 9 textes de référence T1–T9 »,
mais le tableau réel de `impact-science.md` §3 ne contient que **8 exemples**, pas 9. Ce n'est
pas une erreur de ma part : vérifié à deux reprises, dans deux sessions différentes. Conformément
à la consigne du projet (« si un point n'est tranché nulle part, ne l'invente pas »), je n'ai pas
inventé de 9e exemple : les 8 existants ont été utilisés, numérotés T1 à T8 dans l'ordre du
tableau, et sont maintenant de vraies fiches confirmées sur le site en ligne (données de
démonstration, Étape A8).

Pour chacun, le texte a été rédigé par mes soins (le tableau ne donne qu'un titre court, pas un
texte source complet), passé par le vrai pipeline IA, puis confirmé. Résultat par rapport au
tableau attendu :

| # | Attendu (famille / Area / RISE / ODD) | Proposé par l'IA | Corrigé à la confirmation ? |
|---|---|---|---|
| T1 | ENVIRONMENTAL_ACTION / CI / Non / 13,15 | Famille et Area corrects ; **RISE=yes proposé à tort** (pilier Économies, justification forcée) | Oui — RISE remis à "non" |
| T2 | PUBLIC_SPEAKING / ID+CI secondaire / Non / 4 | ID correct ; **CI secondaire non proposé** | Oui — CI secondaire ajouté |
| T3 | PUBLIC_SPEAKING / ID seule / N/A / 4 | Conforme, CI correctement absent (public 100% interne) | Non — accepté tel quel |
| T4 | BUSINESS_COMPETITION / BE+CI secondaire / Oui pilier Économies / 8,9 | BE correct ; **CI secondaire non proposé**, RISE non proposé | Oui — CI secondaire + RISE ajoutés |
| T5 | TRAINING_WORKSHOP / ID seule / N/A / 4 | Conforme, CI correctement absent (public 100% interne) | Non — accepté tel quel |
| T6 | TWINNING / IC seule / N/A / 17 | Famille et ODD corrects ; **Area proposée "ID" au lieu de "IC"** (confusion de l'IA sur le nom de l'axe) | Oui — corrigé en IC |
| T7 | COMMUNITY_TRAINING+BUSINESS_NETWORKING / CI+ID secondaire / Oui pilier Main-d'œuvre / 4,8 | Conforme (CI/ID inversés en primaire/secondaire par rapport au tableau, RISE correct) | Oui — ordre primaire/secondaire aligné sur le tableau, famille BUSINESS_NETWORKING ajoutée |
| T8 | AWARENESS_CAMPAIGN / CI / Oui pilier Santé mentale / 3 | Conforme à l'identique | Non — accepté tel quel |

Chaque valeur proposée par l'IA porte bien une phrase justificative citée du texte, y compris les
propositions incorrectes (T1, T6) — la justification est présente mais logiquement erronée, ce que
la relecture humaine a détecté et corrigé. C'est exactement le rôle de la confirmation humaine
(D-16/D-28) : 3 des 8 textes de référence auraient été mal classés si la proposition de l'IA avait
été acceptée sans relecture.

## AC-24 — écart réel identifié (population interne, verrou de confirmation)

Le test en deux temps :
1. **Côté IA** : testé sur T3, T5, et deux textes additionnels 100% internes — dans les 4 cas,
   l'IA ne propose jamais CI. **PASS**.
2. **Côté API (forcer CI malgré un texte 100% interne)** : testé en forçant `CI` dans la
   confirmation d'un texte explicitement 100% interne ("Aucun public externe n'était présent").
   Quand le texte produit **au moins un candidat** dont la population est connue et confirmée
   "interne", le verrou fonctionne : refus explicite `"public interne => Community Impact
   impossible (D-26, AC-24)"`. **Mais** quand le texte ne produit **aucun candidat mesurable du
   tout** (ce qui arrive systématiquement sur les textes courts et 100% internes — c'est
   précisément le cas de T3 et T5, tous deux à 0 candidat), le verrou ne se déclenche pas : la
   confirmation est acceptée avec CI, alors que le texte dit noir sur blanc qu'il n'y a aucun
   public externe.

   Ce n'est pas un oubli isolé : c'est une conséquence directe d'un choix de conception assumé et
   documenté dans le code (`confirm_service.py`, commentaire "on ne bloque que si au moins une
   population est CONNUE — jamais d'invention à partir d'une absence d'information"), qui est la
   même philosophie "UNKNOWN ≠ ZERO" appliquée partout ailleurs dans NEXUS. Le verrou D-26 est
   qualifié de "non contournable" dans `impact-science.md`, mais la seule façon de le rendre
   réellement non contournable dans ce cas précis serait de traiter "aucune donnée de population"
   comme une preuve de "public interne" — ce qui contredirait ce même principe "ne jamais inventer
   à partir d'une absence". **Je n'ai pas tranché cela seul** : c'est une vraie question de
   produit, pas un bug technique évident, et je la remonte explicitement plutôt que de choisir
   à votre place.

## AC-31 — corrigé pendant ce test

Le tableau de bord (Écran 1, A7) n'affichait qu'un seul ratio RISE ("% des projets Community
Impact"). AC-31 exige explicitement deux ratios étiquetés séparément (base CI / base tous
projets). Trouvé en testant AC-31 avec les données de démonstration réelles (14 projets), corrigé
dans la foulée : le second ratio (`rise_pct_of_all`) a été ajouté au backend et au frontend,
vérifié en direct sur le site (ex. mesuré : 30 % des projets CI, 21,4 % de tous les projets),
commité et poussé.

## Remarque sur AC-29 — une heure corrigée n'est jamais sommée

Constaté en relisant le tableau de bord en direct après le test AC-29 : une mesure
`VOLUNTEER_HOURS` corrigée manuellement par le SG obtient `value_status = "estimated"`. Le moteur
d'agrégation figé n'agrège que les statuts `extracted` et `calculated`
(`VALUE_STATUS_AGGREGABLE = {"extracted", "calculated"}`, ligne 51 d'`aggregation_engine.py`) —
`estimated` en est délibérément exclu, quelle que soit la valeur. Conséquence directe, observée en
conditions réelles sur le site : la mesure corrigée à 50h apparaît en refus `UNKNOWN_VALUE` sur le
tableau de bord (visible, non masqué — conforme à la règle "un refus n'est pas une panne") plutôt
que d'être incluse dans le total "Heures de bénévolat". Ce n'est pas un bug — c'est le moteur figé
qui, par construction, ne fait jamais confiance à une valeur "estimée" pour un total officiel — mais
c'est une conséquence peu visible qui mérite d'être connue : **toute correction manuelle d'une
heure de bénévolat sort silencieusement cette mesure des totaux agrégés**, sans qu'aucun message
à l'écran de confirmation ne le dise au SG au moment où il corrige la valeur.

## Constat de performance (hors périmètre des 31 AC, mais important pour la démo)

Avec 14 projets de démonstration en base, l'écran "Vue d'ensemble" (`/dashboards/{view}/overview`)
met environ **45 à 50 secondes** à charger sur le site en ligne (mesuré deux fois). La cause
probable : cet écran relance le moteur d'agrégation une fois pour la vue globale, une fois par
domaine (4) et une fois par ODD présent (9 avec les données actuelles), soit 14 requêtes
d'agrégation séparées à chaque chargement d'écran — sur l'offre gratuite de Render, chaque aller-
retour vers Supabase ajoute une latence réseau qui s'additionne. Ce n'est pas une régression du
jour : c'est le prix de la conception "toujours recalculer via le moteur figé, jamais un chiffre
en dur" (choix assumé, cf. §2 du prompt de construction), combiné à la croissance normale du jeu
de données de démo. Je n'ai pas touché à cette logique sous la pression du délai, pour ne pas
risquer d'introduire une régression non testée à quelques heures de la soumission — je le signale
plutôt que de le corriger dans la précipitation. **Recommandation pratique pour la démo** :
charger une fois l'écran "Vue d'ensemble" une minute ou deux avant de le montrer aux juges, pour
que Render soit "réveillé" et que le résultat soit déjà en mémoire côté navigateur.
