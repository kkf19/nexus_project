# NEXUS — Hackathon JCI 2026

NEXUS transforme les textes libres décrivant des projets JCI en chiffres normalisés, reliés à leur phrase source exacte, et agrégés uniquement lorsque l'addition a un sens.

> Dépôt construit progressivement pendant le hackathon. Ce README est complété (stack finale, instructions de lancement, lien de démo) à la fin de la construction — voir `docs/technical/dev-brief.md` §6.

## Stack

- **Backend** : Python + FastAPI + SQLAlchemy
- **Base de données** : PostgreSQL (Supabase)
- **Frontend** : Next.js (React + TypeScript)
- **Pipeline IA** : Anthropic Claude Haiku 4.5 (extraction + classement taxonomie)
- **Hébergement** : Render/Railway (backend) · Vercel (frontend) · Supabase (base) · GitHub (dépôt)

## Documentation de référence

Toute la spécification fonctionnelle et technique est dans `docs/technical/` :
- `dev-brief.md` — référence de construction : schéma de base, contrats du pipeline IA, points d'entrée d'API, règles inviolables (RI-01 à RI-15), critères d'acceptation (AC-01 à AC-22)
- `mvp-scope.md` — décisions de cadrage (D-01 à D-22) et les 13 champs canoniques du MVP
- `taxonomy.config.json`, `measurement-object.schema.json`, `measurement-object.examples.json` — référentiels et contrat de données

## Fichiers réutilisés tels quels (ne jamais réécrire)

- `backend/engine/aggregation_engine.py` — moteur d'agrégation (clé d'équivalence, éligibilité, refus)
- `docs/technical/validate_measurement_objects.py` — validateur du schéma du Measurement Object
- `Tier 2/validate_provenance.py` — validateur des règles de provenance

## Backend — démarrage local

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # puis renseigner les vraies valeurs
python3 scripts/self_test.py   # auto-test sans base de données
python3 scripts/init_db.py     # crée le schéma + charge la taxonomie sur Supabase
uvicorn app.main:app --reload
```
