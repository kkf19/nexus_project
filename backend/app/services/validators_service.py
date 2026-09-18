"""Pont vers les deux validateurs réutilisés tels quels (dev-brief.md §8) :

- docs/technical/validate_measurement_objects.py  (schéma Draft-07 + règles E1-E6)
- Tier 2/validate_provenance.py                    (règles de provenance V1-V11)

Politique D-12, encodée ici et nulle part ailleurs : le validateur du MO fait
foi et bloque. validate_provenance bloque sur V1-V4, V6, V9, V10 et V11
("OFFICIAL_JCI_FACT cannot be validated/verified"). Ses avertissements V5,
V11 "invalid verification_status" et V11 "evidence_ref" sont non bloquants
(déjà couverts par le schéma dans les autres cas).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _load_module(name: str, path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{name} introuvable à {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_mo_validator = _load_module(
    "validate_measurement_objects", _REPO_ROOT / "docs" / "technical" / "validate_measurement_objects.py"
)
_provenance_validator = _load_module(
    "validate_provenance", _REPO_ROOT / "Tier 2" / "validate_provenance.py"
)

with open(_mo_validator.SCHEMA_PATH, encoding="utf-8") as _f:
    _SCHEMA = json.load(_f)

_schema_validator = Draft7Validator(_SCHEMA)

# Avertissements non bloquants selon D-12
_ALWAYS_WARNING_CODES = {"V5"}


def validate_measurement_object(obj: dict) -> list[tuple[str, str]]:
    """Schéma + règles E1-E6. Liste vide = objet valide. Fait foi (D-12)."""
    return _mo_validator.validate_one(_schema_validator, obj)


def validate_provenance(obj: dict) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    """Règles V1-V11 sur un objet déjà en mémoire.
    Retourne (violations_bloquantes, avertissements_non_bloquants) selon D-12."""
    errors: list = []
    stats: dict = {}
    _provenance_validator.walk(obj, "$", {"in_norm": False, "fictional": False}, errors, stats)

    blocking, warnings = [], []
    for code, path, msg in errors:
        is_v11_soft = code == "V11" and ("invalid verification_status" in msg or "evidence_ref" in msg)
        if code in _ALWAYS_WARNING_CODES or is_v11_soft:
            warnings.append((code, path, msg))
        else:
            blocking.append((code, path, msg))
    return blocking, warnings


def is_valid(obj: dict) -> tuple[bool, dict]:
    """Verdict combiné. Le schéma du MO fait foi (D-12)."""
    schema_errors = validate_measurement_object(obj)
    blocking, warnings = validate_provenance(obj)
    return (
        not schema_errors and not blocking,
        {
            "schema_errors": schema_errors,
            "provenance_blocking": blocking,
            "provenance_warnings": warnings,
        },
    )
