"""Pont vers backend/engine/aggregation_engine.py — fichier réutilisé TEL
QUEL (dev-brief.md §8). Ce module ne réimplémente aucune règle : il charge le
fichier existant depuis son emplacement d'origine et ré-exporte ses noms.

Toute divergence entre ce pont et aggregation_engine.py serait un bug de ce
pont, jamais du moteur (dev-brief.md §2 : "toute divergence entre une
réimplémentation et ces fichiers est un bug de la réimplémentation").
Ne jamais modifier DEDUP_ENABLED (D-03).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ENGINE_PATH = Path(__file__).resolve().parent.parent.parent / "engine" / "aggregation_engine.py"
if not _ENGINE_PATH.exists():
    raise FileNotFoundError(f"aggregation_engine.py introuvable à {_ENGINE_PATH}")

_spec = importlib.util.spec_from_file_location("aggregation_engine", _ENGINE_PATH)
_engine_module = importlib.util.module_from_spec(_spec)
sys.modules["aggregation_engine"] = _engine_module
_spec.loader.exec_module(_engine_module)

# Ré-exports directs — aucune logique ajoutée ici
equivalence_key = _engine_module.equivalence_key
eligibility = _engine_module.eligibility
pair_compatibility = _engine_module.pair_compatibility
aggregate = _engine_module.aggregate
report = _engine_module.report
load_measurements = _engine_module.load_measurements
Aggregate = _engine_module.Aggregate
Refusal = _engine_module.Refusal
EngineResult = _engine_module.EngineResult
DEDUP_ENABLED = _engine_module.DEDUP_ENABLED  # ne jamais modifier (D-03)
STANDARD = _engine_module.STANDARD
