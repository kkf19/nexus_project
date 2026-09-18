#!/usr/bin/env python3
"""
NEXUS — validateur du Measurement Object v1.

Usage:
    python3 validate_measurement_objects.py [examples.json ...]

Vérifie chaque objet contre measurement-object.schema.json, puis applique les
règles de cohérence qui ne s'expriment pas en JSON Schema (clé d'équivalence,
relations, cohérence des refus).

Les clés commençant par "_" sont des annotations de test et sont ignorées.
Un fichier d'exemples avec des blocs "valid" / "invalid" est traité comme une
suite de tests : les objets de "invalid" DOIVENT échouer.
"""
import json
import sys
import os

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("pip install jsonschema --break-system-packages")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "measurement-object.schema.json")

EQ_KEY_PARTS = [
    ("metric_code", lambda o: o.get("metric_code")),
    ("unit", lambda o: (o.get("unit") or {}).get("code")),
    ("iaooi", lambda o: (o.get("iaooi_class") or {}).get("value")),
    ("count_type", lambda o: (o.get("population") or {}).get("count_type")),
    ("int_ext", lambda o: (o.get("population") or {}).get("internal_external")),
    ("dedup_basis", lambda o: (o.get("population") or {}).get("dedup_basis")),
    ("period_type", lambda o: (o.get("period") or {}).get("type")),
    ("subject_type", lambda o: (o.get("subject") or {}).get("type")),
]


def strip_annotations(obj):
    if isinstance(obj, dict):
        return {k: strip_annotations(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [strip_annotations(v) for v in obj]
    return obj


def equivalence_key(obj):
    return "|".join(str(fn(obj)) for _, fn in EQ_KEY_PARTS)


def extra_rules(obj):
    """Règles hors JSON Schema."""
    errors = []
    agg = obj.get("aggregation") or {}

    # E1 — la clé d'équivalence stockée doit être celle que le moteur recalcule
    stored = agg.get("equivalence_key")
    if stored:
        expected = equivalence_key(obj)
        if stored != expected:
            errors.append(("E1", f"equivalence_key stockée != recalculée\n    stored:   {stored}\n    expected: {expected}"))

    # E2 — un objet agrégeable ne peut pas porter un count_type inconnu
    if agg.get("aggregable") is True:
        if (obj.get("population") or {}).get("count_type") == "unknown":
            errors.append(("E2", "aggregable=true avec population.count_type=unknown"))

    # E3 — un DQC ouvert interdit validated/verified (règle T6)
    if obj.get("dq_refs") and obj.get("verification_status") in ("validated", "verified"):
        errors.append(("E3", "verification_status avancé alors qu'un objet qualité (dq_refs) est rattaché"))

    # E4 — un agrégat (value_status=calculated) doit déclarer sa couverture (AGG-4)
    if obj.get("value_status") == "calculated" and obj.get("parent_measurement_ids"):
        if not agg.get("coverage"):
            errors.append(("E4", "agrégat sans aggregation.coverage (règle AGG-4)"))

    # E5 — une relation subset_of/funnel_stage impose la non-agrégation avec sa cible
    for rel in obj.get("relations", []) or []:
        if rel.get("relation_type") in ("subset_of", "funnel_stage", "same_population_different_metric"):
            if agg.get("aggregable") is True and not agg.get("equivalence_key"):
                errors.append(("E5", f"relation {rel.get('relation_type')} sans clé d'équivalence explicite"))

    # E6 — conflicting impose aggregable=false
    if obj.get("value_status") == "conflicting" and agg.get("aggregable") is not False:
        errors.append(("E6", "value_status=conflicting doit donner aggregable=false"))

    return errors


def validate_one(validator, obj):
    clean = strip_annotations(obj)
    errs = [("SCHEMA", f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}")
            for e in validator.iter_errors(clean)]
    errs += extra_rules(clean)
    return errs


def main(paths):
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)
    print("schema: OK (Draft-07)")

    total_fail = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        print(f"\n== {os.path.basename(path)}")

        if isinstance(data, dict) and ("valid" in data or "invalid" in data):
            for obj in data.get("valid", []):
                label = obj.get("_case", obj.get("measurement_id", "?"))
                errs = validate_one(validator, obj)
                if errs:
                    total_fail += 1
                    print(f"  [FAIL] attendu valide — {label}")
                    for code, msg in errs:
                        print(f"         {code}: {msg}")
                else:
                    print(f"  [ok]   {label}")

            for obj in data.get("invalid", []):
                label = obj.get("_expected_failure", obj.get("measurement_id", "?"))
                errs = validate_one(validator, obj)
                if errs:
                    print(f"  [ok]   rejeté comme prévu — {label}")
                    print(f"         → {errs[0][0]}: {errs[0][1].splitlines()[0]}")
                else:
                    total_fail += 1
                    print(f"  [FAIL] aurait dû être rejeté — {label}")
        else:
            objs = data if isinstance(data, list) else [data]
            for obj in objs:
                errs = validate_one(validator, obj)
                if errs:
                    total_fail += 1
                    print(f"  [FAIL] {obj.get('measurement_id', '?')}")
                    for code, msg in errs:
                        print(f"         {code}: {msg}")
                else:
                    print(f"  [ok]   {obj.get('measurement_id', '?')}")

    print(f"\n{'TOUS LES TESTS PASSENT' if total_fail == 0 else str(total_fail) + ' ÉCHEC(S)'}")
    return 1 if total_fail else 0


if __name__ == "__main__":
    args = sys.argv[1:] or [os.path.join(HERE, "measurement-object.examples.json")]
    sys.exit(main(args))
