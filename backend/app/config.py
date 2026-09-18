"""Configuration centrale. Toutes les valeurs sensibles viennent de variables
d'environnement, jamais du code (dev-brief.md §3, "Secrets")."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent

load_dotenv(REPO_ROOT / ".env")


class Settings:
    database_url: str | None = os.getenv("DATABASE_URL")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    taxonomy_config_path: Path = REPO_ROOT / os.getenv(
        "TAXONOMY_CONFIG_PATH", "docs/technical/taxonomy.config.json"
    )


settings = Settings()
