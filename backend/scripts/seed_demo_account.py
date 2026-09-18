"""Cree un compte OL de demonstration (DEMO-OL / DEMO-USER).

Provisoire : tant que les vrais ecrans de compte (Phase 4) n'existent pas,
les submissions creees via l'API sont rattachees a ce compte par defaut
(voir app/schemas.py, SubmissionCreate).

Usage : python3 backend/scripts/seed_demo_account.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import models  # noqa: E402
from app.database import SessionLocal  # noqa: E402


def main() -> int:
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
        print("OK : DEMO-OL / DEMO-USER prets")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
