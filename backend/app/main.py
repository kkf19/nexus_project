"""Point d'entrée FastAPI.

Voir dev-brief.md Annexe A pour les 13 points d'entrée prévus. Seuls ceux qui
ne dépendent pas du pipeline IA (Phase 2) ou du moteur d'agrégation branché
(Phase 3) sont câblés ici pour l'instant — c'est le socle (Phase 1).
"""
from __future__ import annotations

from fastapi import FastAPI

from app.routers import measurements, projects, submissions, taxonomy

app = FastAPI(title="NEXUS API", version="0.1.0")

app.include_router(submissions.router)
app.include_router(projects.router)
app.include_router(measurements.router)
app.include_router(taxonomy.router)


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
    """Diagnostic temporaire (deploiement hackathon) : verifie/cree le compte
    demo et remonte l'erreur exacte si ca echoue, sans avoir besoin d'acceder
    aux logs Render. A retirer une fois le socle production stabilise."""
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        existing_org = db.get(models.Organization, "DEMO-OL")
        existing_user = db.get(models.AppUser, "DEMO-USER")
        created = []
        if not existing_org:
            db.add(models.Organization(
                organization_id="DEMO-OL",
                org_type="local",
                name="OL Demo (a remplacer par un vrai compte, Phase 4)",
                country_iso2=None,
            ))
            created.append("organization")
        if not existing_user:
            db.add(models.AppUser(
                user_id="DEMO-USER",
                organization_id="DEMO-OL",
                role="admin_ol",
            ))
            created.append("app_user")
        db.commit()
        return {
            "already_existed": {
                "organization": bool(existing_org),
                "app_user": bool(existing_user),
            },
            "created": created,
        }
    except Exception as exc:
        db.rollback()
        return {"error": str(exc)}
    finally:
        db.close()
