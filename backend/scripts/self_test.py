"""Auto-test SANS base de données.

Vérifie que les ponts vers les fichiers réutilisés
(services/engine_service.py, services/validators_service.py) produisent
EXACTEMENT les mêmes résultats que ces fichiers appelés directement en ligne
de commande. Toute divergence serait un bug du pont, jamais des fichiers
d'origine (dev-brief.md §8).

Usage : python3 backend/scripts/self_test.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services import engine_service, validators_service  # noqa: E402


def test_validators() -> bool:
    print("== validators_service — measurement-object.examples.json ==")
    examples_path = REPO_ROOT / "docs" / "technical" / "measurement-object.examples.json"
    data = json.loads(examples_path.read_text(encoding="utf-8"))

    ok = 0
    for obj in data.get("valid", []):
        valid, detail = validators_service.is_valid(obj)
        label = obj.get("_case", obj.get("measurement_id"))
        if valid:
            ok += 1
            print(f"  [ok]   {label}")
        else:
            print(f"  [FAIL] attendu valide — {label} — {detail}")

    for obj in data.get("invalid", []):
        valid, detail = validators_service.is_valid(obj)
        label = obj.get("_expected_failure", obj.get("measurement_id"))
        if not valid:
            ok += 1
            print(f"  [ok]   rejeté comme prévu — {label}")
        else:
            print(f"  [FAIL] aurait dû être rejeté — {label}")

    total = len(data.get("valid", [])) + len(data.get("invalid", []))
    print(f"  -> {ok}/{total} attendus corrects\n")
    return ok == total


def test_engine() -> bool:
    print("== engine_service — demo_measurements.json ==")
    demo_path = BACKEND_DIR / "engine" / "demo_measurements.json"
    measurements = engine_service.load_measurements(str(demo_path))
    measurements = [m for m in measurements if not m.get("parent_measurement_ids")]
    result = engine_service.aggregate(measurements, group_by="network")
    total_refus = len(result.excluded) + len(result.refusals)
    print(f"  agrégats : {len(result.aggregates)}  |  refus : {total_refus}  (attendu : 4 et 3 — AC-12)")
    ok = len(result.aggregates) == 4 and total_refus == 3
    print("  [ok]" if ok else "  [FAIL] ne correspond pas au moteur démo de référence")
    return ok


def main() -> int:
    results = [test_validators(), test_engine()]
    if all(results):
        print("TOUS LES AUTO-TESTS PASSENT")
        return 0
    print("ÉCHEC(S) DANS LES AUTO-TESTS")
    return 1


if __name__ == "__main__":
    sys.exit(main())
