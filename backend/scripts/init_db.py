"""Initialise le schéma PostgreSQL (Supabase) et charge la taxonomie active.

Usage :
    python3 backend/scripts/init_db.py

Nécessite DATABASE_URL dans l'environnement ou dans un .env à la racine du
dépôt (voir .env.example). Ne recopie JAMAIS taxonomy.config.json en dur
(dev-brief.md §2.1) : le fichier est chargé tel quel et versionné dans
taxonomy_release, à partir de meta.version.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import models  # noqa: E402  (enregistre tous les modèles sur Base)
from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402


def load_taxonomy() -> None:
    path = settings.taxonomy_config_path
    raw = path.read_text(encoding="utf-8")
    content = json.loads(raw)
    version = content["meta"]["version"]
    checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    db = SessionLocal()
    try:
        existing = db.get(models.TaxonomyRelease, version)
        if existing:
            print(f"taxonomy_release {version} déjà chargée (checksum {existing.checksum[:12]}...)")
            return
        db.query(models.TaxonomyRelease).update({"is_active": False})
        db.add(models.TaxonomyRelease(version=version, content=content, checksum=checksum, is_active=True))
        db.commit()
        print(f"taxonomy_release {version} chargée et activée (checksum {checksum[:12]}...)")
    finally:
        db.close()


def main() -> int:
    if not settings.database_url:
        print("DATABASE_URL manquant — voir .env.example à la racine du dépôt.")
        return 2
    print(f"Création du schéma sur {engine.url.render_as_string(hide_password=True)} ...")
    Base.metadata.create_all(bind=engine)
    print("Schéma créé.")
    load_taxonomy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
