# NEXUS — Hackathon JCI 2026

NEXUS transforme les textes libres décrivant des projets JCI en chiffres normalisés, reliés à leur phrase source exacte, et agrégés uniquement lorsque l'addition a un sens.

> Dépôt construit progressivement pendant le hackathon. Ce README est complété (lien de démo final) à la fin de la construction — voir `docs/technical/dev-brief.md` §6.

## État d'avancement

- [x] Phase 1 — Socle backend (schéma de base, moteur et validateurs branchés, CRUD minimal)
- [x] Phase 2 — Pipeline IA (extraction + classement taxonomie, appels réels à Claude Haiku 4.5)
- [x] Phase 3 — Agrégation branchée sur l'API (`/aggregations/run`, `/dashboards/{view}`, `/trace/{id}`, `/aggregations/check-pair`, revue `/measurements/{id}/review`, `/projects/{id}` et `/measurements/{id}` complets)
- [ ] Phase 4 — Frontend (les trois écrans)
- [ ] Phase 5 — Bout en bout (AC-01 à AC-22)
- [ ] Phase 6 — Livrables finaux

## Stack

- **Backend** : Python + FastAPI + SQLAlchemy
- **Base de données** : PostgreSQL (Supabase)
- **Frontend** : Next.js (React + TypeScript) — à venir
- **Pipeline IA** : Anthropic Claude Haiku 4.5 (extraction + classement taxonomie)
- **Hébergement** : Render (backend) · Vercel (frontend, à venir) · Supabase (base) · GitHub (dépôt)

## Documentation de référence

Toute la spécification fonctionnelle et technique est dans `docs/technical/` :
- `dev-brief.md` — référence de construction : schéma de base, contrats du pipeline IA, points d'entrée d'API, règles inviolables (RI-01 à RI-15), critères d'acceptation (AC-01 à AC-22)
- `mvp-scope.md` — décisions de cadrage (D-01 à D-22) et les 13 champs canoniques du MVP
- `taxonomy.config.json`, `measurement-object.schema.json`, `measurement-object.examples.json` — référentiels et contrat de données

## Fichiers réutilisés tels quels (ne jamais réécrire)

- `backend/engine/aggregation_engine.py` — moteur d'agrégation (clé d'équivalence, éligibilité, refus)
- `docs/technical/validate_measurement_objects.py` — validateur du schéma du Measurement Object
- `Tier 2/validate_provenance.py` — validateur des règles de provenance

## Points d'entrée de l'API (Annexe A du dev-brief)

Les 13 points d'entrée sont câblés. Les quatre derniers (Phase 3) appellent le
moteur d'agrégation réutilisé tel quel :

- `POST /aggregations/run` — lance un calcul (`view`: ol/national/global,
  `scope_organization_id`, `group_by`: subject/geography/network, `filters`:
  année + les 3 axes séparément) ; écrit les agrégats et les refus en base.
- `GET /dashboards/{view}` — recalcule à la demande et affiche le résultat ;
  si le moteur échoue, retombe sur la dernière exécution réussie
  (`stale: true`). Vue mondiale uniquement : `official_jci_facts` (vide tant
  que la liste de référence JCI, point ouvert O-05, n'est pas fournie) et les
  4 conflits `quality_issues` affichés (dev-brief §2.11).
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
python3 scripts/self_test_phase3.py    # auto-test de bout en bout (agrégation, tableaux de bord, traçabilité) sur SQLite jetable, sans Supabase
python3 scripts/export_schema_sql.py > ../supabase_init.sql   # si le schéma a changé
python3 scripts/seed_demo_account.py   # crée le compte de démo DEMO-OL / DEMO-USER
uvicorn app.main:app --reload
```

Si la connexion directe à Postgres (port 5432) n'est pas joignable depuis votre réseau, `supabase_init.sql` se colle tel quel dans l'éditeur SQL de Supabase (Project → SQL Editor → New query → Run).

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
