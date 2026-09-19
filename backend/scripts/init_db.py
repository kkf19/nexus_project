"""Initialise le schéma PostgreSQL (Supabase), charge la taxonomie active et
le registre de qualité des données JCI (dev-brief.md §2.11).

Usage :
    python3 backend/scripts/init_db.py

Nécessite DATABASE_URL dans l'environnement ou dans un .env à la racine du
dépôt (voir .env.example). Ne recopie JAMAIS taxonomy.config.json ni
jci_data_quality_registry_v2.json en dur : chargés tels quels, à partir de
leurs identifiants propres (meta.version / conflict_id, visual_id).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

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


DISPLAYED_CONFLICT_IDS = {"DQC-01", "DQC-03", "DQC-13", "DQC-24"}  # dev-brief.md §2.11


def load_quality_issues() -> None:
    """Charge jci_data_quality_registry_v2.json tel quel (26 conflits, 9
    graphiques non extraits). `displayed = true` UNIQUEMENT pour les 4
    conflits listés en §2.11 — les 22 autres restent en base, non affichés
    (dev-brief.md §7, "arbitrage des 26 conflits interdit")."""
    path = REPO_ROOT / "Tier 1" / "jci_data_quality_registry_v2.json"
    content = json.loads(path.read_text(encoding="utf-8"))

    db = SessionLocal()
    try:
        created = 0
        for conflict in content.get("conflicts", []):
            issue_id = conflict["conflict_id"]
            if db.get(models.QualityIssue, issue_id):
                continue
            db.add(models.QualityIssue(
                issue_id=issue_id,
                kind="conflict",
                subject=conflict.get("subject"),
                values=conflict.get("values", []),
                resolution_status=conflict.get("resolution_status", "UNRESOLVED"),
                displayed=issue_id in DISPLAYED_CONFLICT_IDS,
            ))
            created += 1
        for visual in content.get("visual_data_not_extracted", []):
            issue_id = visual["visual_id"]
            if db.get(models.QualityIssue, issue_id):
                continue
            chart = visual.get("chart")
            chart_label = chart.get("value") if isinstance(chart, dict) else chart
            db.add(models.QualityIssue(
                issue_id=issue_id,
                kind="visual",
                subject=chart_label or visual.get("section"),
                values=[{
                    "page": visual.get("page"),
                    "section": visual.get("section"),
                    "chart": visual.get("chart"),
                    "missing": visual.get("missing"),
                    "value": visual.get("value"),
                    "value_status": visual.get("value_status"),
                }],
                resolution_status="UNRESOLVED",
                displayed=False,
            ))
            created += 1
        db.commit()
        total = len(content.get("conflicts", [])) + len(content.get("visual_data_not_extracted", []))
        print(f"quality_issue : {created} nouvelle(s) ligne(s) chargée(s) (registre : {total} au total, "
              f"{len(DISPLAYED_CONFLICT_IDS)} affichée(s) par défaut)")
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
    load_quality_issues()
    return 0


if __name__ == "__main__":
    sys.exit(main())
