"""Provenance validator (V2). Enforces rule P0: No unsupported inference becomes an official JCI fact.

Usage: python3 validate_provenance.py file1.json [file2.json ...]
Exit code 1 if any violation.
"""
import json
import sys

OFF, LOC, SEM, PRO = "OFFICIAL_JCI_FACT", "LOCAL_REPORTED_FACT", "SEMANTIC_INTERPRETATION", "PROPOSED_STANDARD"
LAYERS = {OFF, LOC, SEM, PRO}
STATUSES = {"extracted", "calculated", "estimated", "unknown", "visual_data_not_extracted", "conflicting"}
ALLOWED = {  # §P.3
    OFF: {"extracted", "unknown", "visual_data_not_extracted", "conflicting"},
    LOC: {"extracted", "unknown", "conflicting"},
    SEM: {"calculated", "estimated", "unknown"},
    PRO: set(),
}
NORMALIZATION_KEYS = {"metric_code", "iaooi_class", "activity_type", "target_group", "outcome_type", "impact_type", "chart_label_association", "normalization"}
OFFICIAL_VOCAB_CONTEXT = {"label", "value", "name", "award_category", "attested_in_report", "chart"}  # where OFFICIAL is legitimate in fictional cases


def walk(node, path, ctx, errors, stats):
    if isinstance(node, dict):
        if "area" in node:
            errors.append(("V9", path, "bare key 'area' (use geographic_area / area_of_opportunity)"))
        layer = node.get("layer")
        if layer is not None:
            stats[layer] = stats.get(layer, 0) + 1
            if layer not in LAYERS:
                errors.append(("V1", path, f"unknown layer {layer}"))
            status = node.get("value_status")
            src = node.get("source") or {}
            if status is not None and status not in STATUSES:
                errors.append(("V1", path, f"unknown value_status {status}"))
            # V2 — official facts must be cited
            if layer == OFF:
                if src.get("origin") != "jci_report_2025":
                    errors.append(("V2", path, "OFFICIAL_JCI_FACT without origin=jci_report_2025"))
                elif status not in ("unknown", "visual_data_not_extracted"):
                    for k in ("page", "section", "quote"):
                        if not src.get(k):
                            errors.append(("V2", path, f"OFFICIAL_JCI_FACT without source.{k}"))
            if layer == LOC and status == "extracted" and not src.get("quote"):
                errors.append(("V2", path, "LOCAL_REPORTED_FACT without quote"))
            # V3 — unknown / visual => null, never 0
            if status in ("unknown", "visual_data_not_extracted") and node.get("value") is not None:
                errors.append(("V3", path, f"{status} with non-null value {node.get('value')!r}"))
            # V4 — calculated / estimated
            if status == "calculated" and (layer != SEM or not node.get("formula") or not node.get("inputs")):
                errors.append(("V4", path, "calculated without SEMANTIC_INTERPRETATION + formula + inputs"))
            if status == "estimated" and (layer != SEM or not node.get("method")):
                errors.append(("V4", path, "estimated without SEMANTIC_INTERPRETATION + method"))
            # V5 — interpretations need a rule/basis; validation never changes the layer
            if layer == SEM and not (node.get("rule_id") or node.get("basis")):
                errors.append(("V5", path, "SEMANTIC_INTERPRETATION without rule_id/basis"))
            if node.get("validated_by") and layer != SEM:
                errors.append(("V5", path, "validated_by on a non-interpretation layer"))
            # V6 — normalization fields are never official
            if layer == OFF and ctx["in_norm"]:
                errors.append(("V6", path, "normalization field marked OFFICIAL_JCI_FACT"))
            # V7 — fictional cases: OFFICIAL only for JCI vocabulary, with a JCI citation
            if ctx["fictional"] and layer == OFF and src.get("origin") != "jci_report_2025":
                errors.append(("V7", path, "fictional case value marked OFFICIAL_JCI_FACT"))
            # V10 — allowed layer × status combos
            if status is not None and layer in ALLOWED and status not in ALLOWED[layer]:
                errors.append(("V10", path, f"forbidden combination {layer} × {status}"))
        # V8 — conflict objects
        if "conflict_id" in node:
            vals = node.get("values", [])
            sourced = [v for v in vals if (v.get("source") or {}).get("page") or v.get("value_status") == "calculated"]
            if len(vals) < 2 or len(sourced) < len(vals):
                errors.append(("V8", path, "conflict needs ≥2 values, each sourced or calculated"))
            if node.get("resolution_status") == "UNRESOLVED" and node.get("resolution") is not None:
                errors.append(("V8", path, "UNRESOLVED with non-null resolution"))
            if node.get("resolution_status") not in ("UNRESOLVED", "RESOLVED_BY_JCI_SOURCE", "RESOLVED_BY_TEAM_DECISION"):
                errors.append(("V8", path, "invalid resolution_status"))
        fictional = ctx["fictional"] or node.get("fictional") is True
        for k, v in node.items():
            walk(v, f"{path}.{k}", {"in_norm": ctx["in_norm"] or k in NORMALIZATION_KEYS, "fictional": fictional}, errors, stats)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", ctx, errors, stats)


def validate(path):
    data = json.load(open(path, encoding="utf-8"))
    errors, stats = [], {}
    walk(data, "$", {"in_norm": False, "fictional": False}, errors, stats)
    return errors, stats


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        errs, stats = validate(f)
        print(f"== {f}: {len(errs)} violation(s) · layers: {stats}")
        for e in errs[:40]:
            print("  ", *e)
        bad += len(errs)
    sys.exit(1 if bad else 0)
