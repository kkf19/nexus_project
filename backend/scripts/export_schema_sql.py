"""Génère le DDL PostgreSQL du schéma (dev-brief.md §2) à partir des modèles
SQLAlchemy, SANS se connecter à aucune base.

Utile quand la connexion directe à Postgres (port 5432) n'est pas joignable
depuis l'environnement d'exécution (seul HTTP(S) l'est, cas de ce sandbox) :
le fichier généré se colle tel quel dans l'éditeur SQL de Supabase.

Usage :
    python3 backend/scripts/export_schema_sql.py > supabase_init.sql
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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


if __name__ == "__main__":
    print(schema_sql())
    print(taxonomy_seed_sql())
