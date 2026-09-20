"""Cree/complete les organisations fictives multi-pays pour la video de demo
(2026-09-20), SANS toucher a l'authentification : toujours un seul compte
utilisateur DEMO-USER (decision du 2026-09-19 conservee a l'identique, voir
seed_demo_account.py). Ce script ne cree AUCUN projet ni mesure -- seulement
des lignes `organization` (metadata) -- donc il n'a aucun effet sur les
totaux affiches au tableau de bord. Peut etre lance a tout moment, y compris
bien avant l'enregistrement de la demo (contrairement au script de remise a
zero des mesures, a executer juste avant).

Complete aussi DEMO-OL (country_iso2, parent_organization_id) si elle existe
deja sans ces deux champs : c'est precisement ce qui rend la vue "Nationale"
vide aujourd'hui pour ce compte (limitation connue). Idempotent : peut etre
relance sans risque (mise a jour uniquement si un champ manque encore).

Cree 3 organisations nationales fictives et rattache une OL locale (fictive
ou existante) a chacune, pour permettre de simuler 3 pays differents dans la
video sans jamais construire d'ecran de connexion (D-04 inchangee) -- le
choix de "quelle OL" reste un simple menu deroulant cote frontend
(frontend/src/lib/config.ts, DEMO_ORGANIZATIONS), jamais une identite
authentifiee.

Usage : python3 backend/scripts/seed_demo_countries.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import models  # noqa: E402
from app.database import SessionLocal  # noqa: E402

NATIONAL_ORGS: list[tuple[str, str, str]] = [
    # (organization_id, name, country_iso2)
    ("NAT-BJ", "JCI Benin", "BJ"),
    ("NAT-CA", "JCI Canada", "CA"),
    ("NAT-FR", "JCI France", "FR"),
]

LOCAL_ORGS: list[tuple[str, str, str, str]] = [
    # (organization_id, name, parent_organization_id, country_iso2)
    ("DEMO-OL", "JCI Cotonou Etoile", "NAT-BJ", "BJ"),
    ("LOC-CA", "JCI Montreal", "NAT-CA", "CA"),
    ("LOC-FR", "JCE de Paris", "NAT-FR", "FR"),
]


def _upsert(db, org_id: str, org_type: str, name: str, parent_id: str | None, country: str | None) -> None:
    existing = db.get(models.Organization, org_id)
    if existing is None:
        db.add(models.Organization(
            organization_id=org_id, org_type=org_type, name=name,
            parent_organization_id=parent_id, country_iso2=country,
        ))
        print(f"cree : {org_id} ({name})")
        return
    changed = []
    if existing.country_iso2 is None and country is not None:
        existing.country_iso2 = country
        changed.append("country_iso2")
    if existing.parent_organization_id is None and parent_id is not None:
        existing.parent_organization_id = parent_id
        changed.append("parent_organization_id")
    print(f"{'complete (' + ', '.join(changed) + ')' if changed else 'deja a jour'} : {org_id} ({name})")


def main() -> int:
    db = SessionLocal()
    try:
        # Deux passes (nationales d'abord + flush) : meme prudence que
        # confirm_service.py vis-a-vis des contraintes de cle etrangere sur
        # Postgres quand parent et enfant sont ecrits dans la meme transaction.
        for org_id, name, country in NATIONAL_ORGS:
            _upsert(db, org_id, "national", name, None, country)
        db.flush()
        for org_id, name, parent_id, country in LOCAL_ORGS:
            _upsert(db, org_id, "local", name, parent_id, country)
        db.commit()
        print("OK")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
