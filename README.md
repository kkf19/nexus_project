# NEXUS — Hackathon JCI 2026

NEXUS transforme les textes libres décrivant des projets JCI en chiffres normalisés, reliés à leur phrase source exacte, et agrégés uniquement lorsque l'addition a un sens.

## Lien de démo

- **Site** (frontend, Vercel) : https://nexusproject-nexus-2251.vercel.app
- **API** (backend, Render) : https://nexus-project-w4ux.onrender.com
- Compte utilisé : un compte de démonstration unique (`DEMO-OL` / `DEMO-USER`), pas d'écran de connexion dans ce MVP (décision D-04).
- L'écran « Vue d'ensemble » du tableau de bord charge en ~10 secondes (voir `docs/technical/acceptance-report.md`, section performance) ; toujours recommandé de le charger une première fois avant une démo live pour « réveiller » le service Render (offre gratuite). Lors d'un changement de vue ou d'année, l'écran précédent reste affiché avec une légère transition animée pendant le rechargement, plutôt qu'un texte de chargement.

## État d'avancement

- [x] Phase 1 — Socle backend (schéma de base, moteur et validateurs branchés, CRUD minimal)
- [x] Phase 2 — Pipeline IA (extraction + classement taxonomie, appels réels à Claude Haiku 4.5)
- [x] Phase 3 — Agrégation branchée sur l'API (`/aggregations/run`, `/dashboards/{view}`, `/trace/{id}`, `/aggregations/check-pair`, revue `/measurements/{id}/review`, `/projects/{id}` et `/measurements/{id}` complets)
- [x] Phase 4 — Frontend (les trois écrans : saisie, confirmation, tableaux de bord) — compte de démo unique `DEMO-OL`, pas d'écran de connexion pour le hackathon (décision du 2026-09-19)
- [x] **Révision classification (impact-science.md, D-23 à D-31)** — le 19/09, en cours de hackathon, le Product Owner a revu en profondeur la façon dont JCI classe réellement ses projets. Appliqué en 8 étapes (A1 à A8) sur le travail déjà construit des Phases 1 à 4, sans tout reconstruire : nouveau référentiel de taxonomie (v0.3.0), schéma de base additif, pipeline IA réordonné (famille d'activité → domaines → RISE si Community Impact → ODD), validation de confirmation réécrite, page de confirmation et tableau de bord (3 écrans) reconstruits, données de démonstration (8 projets-exemples) confirmées via le vrai pipeline IA sur le site en ligne.
- [x] Phase 5 — Bout en bout (AC-01 à AC-31) — voir `docs/technical/acceptance-report.md` pour le détail projet par projet, y compris deux écarts réels identifiés et documentés plutôt que masqués (AC-23, AC-24)
- [x] Phase 6 — Livrables finaux (ce README, nettoyage des fichiers de diagnostic temporaires, vérification qu'aucun secret n'est commité)

## Stack

- **Backend** : Python + FastAPI + SQLAlchemy
- **Base de données** : PostgreSQL (Supabase)
- **Frontend** : Next.js (React + TypeScript), Tailwind CSS
- **Pipeline IA** : Anthropic Claude Haiku 4.5 (extraction + classement taxonomie)
- **Hébergement** : Render (backend) · Vercel (frontend) · Supabase (base) · GitHub (dépôt)

## Comment JCI classe un projet (résumé — voir `impact-science.md` pour le détail)

Chaque projet est classé selon quatre dimensions, dans cet ordre, chacune confirmée par le SG :

1. **Famille d'activité** — *quelle forme* a pris l'action (formation, débat, plantation, distribution, jumelage…), indépendamment du thème. Nouvel axe (D-25), 1 à n par projet.
2. **Domaine d'intervention (Area of Opportunity)** — *dans quel domaine JCI* : Business & Entrepreneurship (BE), Individual Development (ID), International Cooperation (IC), Community Impact (CI). 1 à n Areas, dont exactement une « principale » (D-26). Règle dure : un public 100 % interne (membres JCI uniquement) ne peut jamais être classé Community Impact, ni en principal ni en secondaire.
3. **RISE** — posée *uniquement* si Community Impact figure parmi les domaines retenus. Oui/non, et si oui, 1 à 3 piliers (Reconstruire les économies, Mobiliser la main-d'œuvre, Préserver la santé mentale) (D-24).
4. **ODD** — 1 à n Objectifs de Développement Durable, sans plafond, dont exactement 1 principal ; chaque ODD retenu porte une phrase de justification citée du texte source, pour éviter le sur-étiquetage (D-27).

Ces trois axes de classification (famille mise à part, qui est une nouveauté NEXUS) sont indépendants entre eux — le programme JCI (CYE, Twinning, congrès…) n'est plus un axe de classification séparé depuis D-23 : c'est désormais une simple famille d'activité parmi d'autres.

Point de vigilance documenté (voir `impact-science.md` §1) : le rapport JCI 2025 publie 53,47 % de projets RISE mais seulement 44,64 % de projets Community Impact, alors que RISE est censé être un sous-ensemble de CI. Ce n'est pas une incohérence du rapport : JCI ne compte probablement que le domaine *principal* de chaque projet dans sa répartition par Area, alors que RISE s'applique dès que CI figure en principal *ou* en secondaire. C'est précisément ce qui justifie la distinction principal/secondaire dans NEXUS.

## Documentation de référence

Toute la spécification fonctionnelle et technique est dans `docs/technical/` :
- **`impact-science.md`** — la révision de classification (19/09) : les quatre dimensions ci-dessus, les définitions officielles JCI par domaine, les critères d'inclusion/exclusion RISE, la maquette des trois écrans du tableau de bord. Fait autorité sur `mvp-scope.md`/`dev-brief.md` en cas de contradiction.
- `dev-brief.md` — référence de construction : schéma de base, contrats du pipeline IA, points d'entrée d'API, règles inviolables (RI-01 à RI-15, dont RI-10 réécrite pour la règle dure Community Impact), critères d'acceptation **AC-01 à AC-31**
- `mvp-scope.md` — décisions de cadrage **D-01 à D-31** (D-23 à D-31 ajoutées le 19/09 pour la révision de classification) et les 13 champs canoniques du MVP
- `acceptance-report.md` — résultat des 31 critères d'acceptation testés sur le site en ligne (Phase 5), avec deux écarts réels documentés plutôt que masqués
- `taxonomy.config.json` (v0.3.0), `measurement-object.schema.json`, `measurement-object.examples.json` — référentiels et contrat de données

## Fichiers réutilisés tels quels (ne jamais réécrire)

- `backend/engine/aggregation_engine.py` — moteur d'agrégation (clé d'équivalence, éligibilité, refus)
- `docs/technical/validate_measurement_objects.py` — validateur du schéma du Measurement Object
- `Tier 2/validate_provenance.py` — validateur des règles de provenance

## Points d'entrée de l'API (Annexe A du dev-brief)

Les 13 points d'entrée sont câblés, plus un ajouté pendant la révision de classification. Les
cinq derniers appellent le moteur d'agrégation réutilisé tel quel :

- `POST /aggregations/run` — lance un calcul (`view`: ol/national/global,
  `scope_organization_id`, `group_by`: subject/geography/network, `filters`:
  année + les 3 axes séparément) ; écrit les agrégats et les refus en base.
- `GET /dashboards/{view}` — recalcule à la demande et affiche le résultat ;
  si le moteur échoue, retombe sur la dernière exécution réussie
  (`stale: true`). Vue mondiale uniquement : `official_jci_facts` (vide tant
  que la liste de référence JCI, point ouvert O-05, n'est pas fournie) et les
  4 conflits `quality_issues` affichés (dev-brief §2.11).
- `GET /dashboards/{view}/overview` — les trois écrans du tableau de bord
  (vue d'ensemble, par domaine, par ODD), ajouté pendant la révision de
  classification. Compte les projets distincts (jamais la somme des blocs,
  D-29) en plus des agrégats du moteur, qu'il ne recalcule jamais lui-même.
- `GET /trace/{measurement_id}` — remonte un agrégat jusqu'à ses mesures
  d'entrée, puis jusqu'au texte brut, avec la citation repérée dans le texte
  et la vérification d'intégrité (CTL-RAW, CTL-TRACE).
- `POST /aggregations/check-pair` — compatibilité de deux mesures à la
  demande (`pair_compatibility()` du moteur).
- `POST /measurements/{id}/review` — valider/signaler/lever un signalement ;
  refusé sur un chiffre JCI officiel ou sous conflit ouvert (T4, T6).

## Backend — démarrage local

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # puis renseigner les vraies valeurs
python3 scripts/self_test.py           # auto-test sans base de données (validateurs + moteur)
python3 scripts/export_schema_sql.py > ../supabase_init.sql   # nouvelle base uniquement (schéma complet)
python3 scripts/seed_demo_account.py   # crée le compte de démo DEMO-OL / DEMO-USER
uvicorn app.main:app --reload
```

Si la connexion directe à Postgres (port 5432) n'est pas joignable depuis votre réseau, `supabase_init.sql` se colle tel quel dans l'éditeur SQL de Supabase (Project → SQL Editor → New query → Run).

**Base déjà initialisée (mise à niveau v0.3.0)** : ne pas rejouer `supabase_init.sql` (il recréerait des tables déjà existantes et échouerait). Utiliser plutôt `backend/scripts/migration_v0_3_0.sql` — additif et idempotent (peut être relancé sans risque), à coller tel quel dans le même éditeur SQL Supabase.

## Déploiement du backend sur Render

1. Sur [render.com](https://render.com), **New +** → **Web Service** → connecter ce dépôt GitHub (`kkf19/nexus_project`).
2. Renseigner :
   - **Root Directory** : `backend`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Dans l'onglet **Environment**, ajouter ces variables (mêmes valeurs que dans votre `.env` local) :
   - `DATABASE_URL`
   - `ANTHROPIC_API_KEY`
   - `ANTHROPIC_MODEL` = `claude-haiku-4-5`
   - `TAXONOMY_CONFIG_PATH` = `docs/technical/taxonomy.config.json`
4. Créer le service. Render redéploie automatiquement à chaque `git push` sur `main`.

## Frontend — démarrage local

```bash
cd frontend
npm install
cp .env.local.example .env.local   # l'URL du backend Render y est déjà pré-remplie
npm run dev
```

Ouvrir `http://localhost:3000`.

## Déploiement du frontend sur Vercel

1. Sur [vercel.com](https://vercel.com), **Add New…** → **Project** → connecter ce dépôt GitHub (`kkf19/nexus_project`).
2. Dans la configuration du projet :
   - **Root Directory** : `frontend`
   - Le framework (Next.js) est détecté automatiquement, rien d'autre à changer.
3. Dans **Environment Variables**, ajouter :
   - `NEXT_PUBLIC_API_BASE_URL` = l'URL de votre service Render (ex. `https://nexus-project-w4ux.onrender.com`)
4. Cliquer **Deploy**. Vercel redéploie automatiquement à chaque `git push` sur `main`, et donne un lien de démo public (`*.vercel.app`).

Le compte utilisé par le site est le compte de démo unique `DEMO-OL` — il n'y a pas d'écran de connexion dans ce MVP (voir « État d'avancement » ci-dessus).
