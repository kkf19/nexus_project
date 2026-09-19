"""Point d'entrée FastAPI.

Voir dev-brief.md Annexe A pour les 13 points d'entrée. Le pipeline IA
(Phase 2) et l'agrégation branchée sur le moteur — /aggregations/*,
/dashboards/*, /trace/* (Phase 3) — sont câblés depuis app.routers.aggregations.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import aggregations, measurements, projects, submissions, taxonomy

app = FastAPI(title="NEXUS API", version="0.1.0")

# Le frontend (Vercel) et l'API (Render) sont sur deux domaines differents :
# sans CORS, le navigateur bloque tous les appels fetch() du frontend.
# Pas d'authentification par cookie dans ce MVP (compte de demo unique,
# D-04) : autoriser toutes les origines est sans risque ici et evite de
# devoir mettre a jour cette liste a chaque redeploiement Vercel (URL de
# previsualisation differente a chaque fois).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions.router)
app.include_router(projects.router)
app.include_router(measurements.router)
app.include_router(taxonomy.router)
app.include_router(aggregations.router)


@app.on_event("startup")
def _seed_demo_account_if_needed() -> None:
    """Cree le compte de demonstration DEMO-OL / DEMO-USER au demarrage, si
    absent (operation idempotente : ne fait rien si deja present).

    Necessaire car l'hebergement (Render, offre gratuite) ne donne pas acces
    a une console/un shell pour lancer un script ponctuel comme
    backend/scripts/seed_demo_account.py directement sur la base en ligne.
    Tant que les vrais ecrans de compte (Phase 4) n'existent pas, les
    submissions creees via l'API sont rattachees a ce compte par defaut
    (voir app/schemas.py, SubmissionCreate).
    """
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        if not db.get(models.Organization, "DEMO-OL"):
            db.add(models.Organization(
                organization_id="DEMO-OL",
                org_type="local",
                name="OL Demo (a remplacer par un vrai compte, Phase 4)",
                country_iso2=None,
            ))
        if not db.get(models.AppUser, "DEMO-USER"):
            db.add(models.AppUser(
                user_id="DEMO-USER",
                organization_id="DEMO-OL",
                role="admin_ol",
            ))
        db.commit()
    except Exception:
        # Ne bloque jamais le demarrage de l'API pour ca ; l'absence du
        # compte demo remontera clairement plus tard via une 500/FK au
        # premier submissions si la base est reellement injoignable.
        db.rollback()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/admin/debug-seed")
def debug_seed():
    """Diagnostic temporaire (deploiement hackathon) : etat detaille de
    l'organisation/app_user demo, avec creation pas a pas (flush intermediaire)
    pour isoler precisement ou une eventuelle erreur se produit. A retirer une
    fois le socle production stabilise."""
    from sqlalchemy import select

    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    diag: dict = {}
    try:
        org_ids = db.execute(select(models.Organization.organization_id)).scalars().all()
        diag["organizations_in_db_before"] = org_ids
        if "DEMO-OL" not in org_ids:
            db.add(models.Organization(
                organization_id="DEMO-OL",
                org_type="local",
                name="OL Demo (a remplacer par un vrai compte, Phase 4)",
                country_iso2=None,
            ))
            db.flush()
            diag["organization_created"] = True
        else:
            diag["organization_created"] = False

        user_ids = db.execute(select(models.AppUser.user_id)).scalars().all()
        diag["users_in_db_before"] = user_ids
        if "DEMO-USER" not in user_ids:
            db.add(models.AppUser(
                user_id="DEMO-USER",
                organization_id="DEMO-OL",
                role="admin_ol",
            ))
            db.flush()
            diag["app_user_created"] = True
        else:
            diag["app_user_created"] = False

        db.commit()
        diag["status"] = "ok"
        return diag
    except Exception as exc:
        db.rollback()
        diag["error"] = str(exc)
        return diag
    finally:
        db.close()
