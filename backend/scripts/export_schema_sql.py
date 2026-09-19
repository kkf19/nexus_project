"""Génère le DDL PostgreSQL du schéma (dev-brief.md §2) à partir des modèles
SQLAlchemy, SANS se connecter à aucune base — et les INSERT qui chargent la
taxonomie active et le registre de qualité JCI (dev-brief.md §2.1 et §2.11),
tels quels.

Utile quand la connexion directe à Postgres (port 5432) n'est pas joignable
depuis l'environnement d'exécution (seul HTTP(S) l'est, cas de ce sandbox) :
le fichier généré se colle tel quel dans l'éditeur SQL de Supabase — ce qui
fait a la fois ce que `scripts/init_db.py` ferait via psycopg2 (schéma +
taxonomie + registre qualité), sans jamais ouvrir de connexion directe.

Usage :
    python3 backend/scripts/export_schema_sql.py > supabase_init.sql
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app import models  # noqa: E402  (enregistre les tables sur Base.metadata)
from app.config import settings  # noqa: E402
from app.database import Base  # noqa: E402


def schema_sql() -> str:
    lines = [
        "-- NEXUS -- schema genere depuis backend/app/models.py (dev-brief.md section 2)",
        "-- Ne pas editer a la main : regenerer avec backend/scripts/export_schema_sql.py",
        "",
    ]
    for table in Base.metadata.sorted_tables:
        lines.append(str(CreateTable(table).compile(dialect=postgresql.dialect())).strip() + ";")
        lines.append("")
        for index in table.indexes:
            lines.append(str(CreateIndex(index).compile(dialect=postgresql.dialect())).strip() + ";")
        if table.indexes:
            lines.append("")
    return "\n".join(lines)


def taxonomy_seed_sql() -> str:
    raw = settings.taxonomy_config_path.read_text(encoding="utf-8")
    content = json.loads(raw)
    version = content["meta"]["version"]
    checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    escaped_version = version.replace("'", "''")
    return (
        "-- Charge le referentiel de taxonomie actif (dev-brief.md section 2.1), tel quel\n"
        f"INSERT INTO taxonomy_release (version, content, checksum, is_active)\n"
        f"VALUES ('{escaped_version}', $taxonomy_json${raw}$taxonomy_json$::json, '{checksum}', true)\n"
        "ON CONFLICT (version) DO NOTHING;\n"
    )


DISPLAYED_CONFLICT_IDS = {"DQC-01", "DQC-03", "DQC-13", "DQC-24"}  # dev-brief.md §2.11


def quality_issue_seed_sql() -> str:
    """Genere les INSERT pour `quality_issue`, depuis
    Tier 1/jci_data_quality_registry_v2.json tel quel (26 conflits, 9
    graphiques non extraits). `displayed = true` uniquement pour les 4
    conflits listés en §2.11 -- meme regle que scripts/init_db.py
    (load_quality_issues()), a garder synchronisee avec elle."""
    path = REPO_ROOT / "Tier 1" / "jci_data_quality_registry_v2.json"
    content = json.loads(path.read_text(encoding="utf-8"))

    def insert(issue_id: str, kind: str, subject: str | None, values: list,
               resolution_status: str, displayed: bool) -> str:
        # Dollar-quoting (comme taxonomy_seed_sql ci-dessus) : evite tout
        # probleme d'apostrophe dans les citations du rapport JCI.
        subject_sql = f"$qi_subject${subject}$qi_subject$" if subject is not None else "NULL"
        values_sql = f"$qi_values${json.dumps(values)}$qi_values$"
        return (
            f'INSERT INTO quality_issue (issue_id, kind, subject, "values", resolution_status, displayed)\n'
            f"VALUES ('{issue_id}', '{kind}', {subject_sql}, {values_sql}::json, "
            f"'{resolution_status}', {'true' if displayed else 'false'})\n"
            "ON CONFLICT (issue_id) DO NOTHING;"
        )

    lines = ["-- Charge le registre de qualite des donnees JCI (dev-brief.md section 2.11), tel quel"]
    for conflict in content.get("conflicts", []):
        issue_id = conflict["conflict_id"]
        lines.append(insert(
            issue_id, "conflict", conflict.get("subject"), conflict.get("values", []),
            conflict.get("resolution_status", "UNRESOLVED"), issue_id in DISPLAYED_CONFLICT_IDS,
        ))
    for visual in content.get("visual_data_not_extracted", []):
        issue_id = visual["visual_id"]
        chart = visual.get("chart")
        chart_label = chart.get("value") if isinstance(chart, dict) else chart
        values = [{
            "page": visual.get("page"), "section": visual.get("section"), "chart": visual.get("chart"),
            "missing": visual.get("missing"), "value": visual.get("value"),
            "value_status": visual.get("value_status"),
        }]
        lines.append(insert(issue_id, "visual", chart_label or visual.get("section"), values, "UNRESOLVED", False))

    return "\n\n".join(lines) + "\n"


if __name__ == "__main__":
    print(schema_sql())
    print(taxonomy_seed_sql())
    print(quality_issue_seed_sql())
