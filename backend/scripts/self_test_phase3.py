"""Auto-test de bout en bout de la Phase 3 (agregation branchee sur l'API).

A la difference de self_test.py (qui teste les ponts vers les fichiers
reutilises SANS base de donnees), ce script exerce le vrai parcours HTTP --
confirmation d'une fiche, calcul d'agregation, tableau de bord, tracabilite,
revue, verification de paire -- sur une base SQLite jetable (fichier local,
supprime a la fin). Aucun reseau, aucun secret requis : c'est pourquoi ce
script peut tourner n'importe quand, y compris sans acces a Supabase.

Il ne re-teste PAS le pipeline IA (deja verifie en conditions reelles,
Phase 2) : les etapes STRUCTURED/STANDARDIZED sont simulees par des
`extraction_candidate` ecrits directement, avec des valeurs realistes
(scenario AC-01 du dev-brief : deux formulations differentes, meme metrique,
un seul agregat). Ce qui EST teste ici, en conditions reelles (vraie route
HTTP, vraie base, vrais validateurs, vrai moteur) : la confirmation d'une
fiche, /aggregations/run, /dashboards/{view}, /trace/{id},
/measurements/{id}/review et /aggregations/check-pair.

Usage : python3 backend/scripts/self_test_phase3.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

_TMP_DB = Path(tempfile.gettempdir()) / "nexus_self_test_phase3.db"
_TMP_DB.unlink(missing_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"

from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  [ok]   {label}")
    else:
        print(f"  [FAIL] {label}" + (f" — {detail}" if detail else ""))
        FAILURES.append(label)


def setup_database() -> None:
    Base.metadata.create_all(bind=engine)
    sys.path.insert(0, str(BACKEND_DIR / "scripts"))
    import init_db  # noqa: E402 — reutilise load_taxonomy()/load_quality_issues(), jamais recopies

    init_db.load_taxonomy()
    init_db.load_quality_issues()

    db = SessionLocal()
    try:
        db.add(models.Organization(organization_id="NO-DEMO", org_type="national", name="NO Demo"))
        db.add(models.Organization(organization_id="OL-A", org_type="local", name="OL Alpha",
                                    parent_organization_id="NO-DEMO", country_iso2="CI"))
        db.add(models.Organization(organization_id="OL-B", org_type="local", name="OL Beta",
                                    parent_organization_id="NO-DEMO", country_iso2="PH"))
        db.add(models.Organization(organization_id="OL-C", org_type="local", name="OL Gamma (autre reseau)"))
        db.flush()
        db.add(models.AppUser(user_id="USER-A", organization_id="OL-A", role="admin_ol"))
        db.add(models.AppUser(user_id="USER-B", organization_id="OL-B", role="admin_ol"))
        db.add(models.AppUser(user_id="USER-C", organization_id="OL-C", role="admin_ol"))
        db.commit()
    finally:
        db.close()


def seed_submission(*, submission_id: str, organization_id: str, user_id: str, raw_text: str,
                     candidate_id: str, quote: str, value: float, metric_code: str,
                     iaooi_value: str, unit_code: str, count_type: str, internal_external: str,
                     reporting_year: int) -> None:
    """Ecrit directement submission + extraction_candidate(structured, standardized),
    comme si le pipeline IA (Phase 2, deja teste en conditions reelles) venait
    de reussir -- ce script teste ce qui vient APRES : confirmation et
    agregation (Phase 3)."""
    import hashlib

    start = raw_text.index(quote)
    end = start + len(quote)

    db = SessionLocal()
    try:
        db.add(models.Submission(
            submission_id=submission_id, organization_id=organization_id, user_id=user_id,
            raw_text=raw_text, raw_text_sha256=hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
            language="fr", pipeline_status="awaiting_confirmation",
        ))
        db.add(models.ExtractionCandidate(
            candidate_id=f"CAND-{submission_id}-S", submission_id=submission_id, stage="structured",
            model_id="llm_extractor@v0",
            payload={"language": "fr", "project": {}, "candidates": [{
                "candidate_id": candidate_id, "quote": quote, "span": {"start": start, "end": end},
                "metric_label_source": quote, "value": value, "value_qualifier": "exact",
                "definition_text": None, "confidence": "H",
            }]},
        ))
        db.add(models.ExtractionCandidate(
            candidate_id=f"CAND-{submission_id}-M", submission_id=submission_id, stage="standardized",
            model_id="llm_classifier@v0",
            payload={
                "project_classification": {"activity_type": []},
                "candidate_mappings": [{
                    "candidate_id": candidate_id, "metric_code": metric_code, "iaooi_value": iaooi_value,
                    "confidence": "H", "unit_code": unit_code, "unit_dimension": "count",
                    "count_type": count_type, "internal_external": internal_external,
                    "dedup_basis": "unique_persons", "target_group": [], "source_wording_class": None,
                    "definition_status": "unknown", "definition_text": None,
                }],
                "relations": [],
            },
        ))
        db.commit()
    finally:
        db.close()


def confirm(client: TestClient, submission_id: str, *, reporting_year: int) -> dict:
    payload = {
        "project": {"name": None, "reporting_year": reporting_year, "outcome_status": "none"},
        "axes": {"area_of_opportunity": ["ID"], "programme": [], "rise_pillars": [],
                 "sdgs": [{"goal": 4, "role": "primary"}]},
        "confirmations": {"C1": True, "C2": True, "C3": True, "C4": True},
        "candidates": [],
        "confirmed_by": "TEST-USER",
    }
    resp = client.post(f"/submissions/{submission_id}/confirm", json=payload)
    check(f"confirm({submission_id}) -> 200", resp.status_code == 200, f"{resp.status_code}: {resp.text[:300]}")
    return resp.json() if resp.status_code == 200 else {}


def main() -> int:
    setup_database()

    with TestClient(app) as client:
        health = client.get("/health")
        check("GET /health -> 200", health.status_code == 200)

        # --- Scenario AC-01 : deux vocabulaires differents, meme metrique, meme annee ---
        seed_submission(
            submission_id="SUB-A", organization_id="OL-A", user_id="USER-A",
            raw_text="En 2025, 45 jeunes ont suivi les trois jours complets de notre formation en leadership.",
            candidate_id="C-A", quote="45 jeunes ont suivi les trois jours complets",
            value=45, metric_code="PEOPLE_TRAINED", iaooi_value="OUTPUT", unit_code="person",
            count_type="direct", internal_external="external", reporting_year=2025,
        )
        seed_submission(
            submission_id="SUB-B", organization_id="OL-B", user_id="USER-B",
            raw_text="In 2025, 80 youth were trained in livelihood skills over the year.",
            candidate_id="C-B", quote="80 youth were trained in livelihood skills",
            value=80, metric_code="PEOPLE_TRAINED", iaooi_value="OUTPUT", unit_code="person",
            count_type="direct", internal_external="external", reporting_year=2025,
        )
        # Troisieme OL, hors reseau NO-DEMO : doit compter en vue mondiale, pas nationale.
        seed_submission(
            submission_id="SUB-C", organization_id="OL-C", user_id="USER-C",
            raw_text="En 2025, 30 jeunes ont participe a notre atelier de sensibilisation.",
            candidate_id="C-C", quote="30 jeunes ont participe",
            value=30, metric_code="PEOPLE_TRAINED", iaooi_value="OUTPUT", unit_code="person",
            count_type="direct", internal_external="external", reporting_year=2025,
        )
        # Membres JCI (internal) : ne doit JAMAIS se sommer avec les externes (RI-04).
        seed_submission(
            submission_id="SUB-D", organization_id="OL-A", user_id="USER-A",
            raw_text="Nos 20 membres benevoles ont ete formes a l'animation d'ateliers cette annee.",
            candidate_id="C-D", quote="20 membres benevoles ont ete formes",
            value=20, metric_code="PEOPLE_TRAINED", iaooi_value="OUTPUT", unit_code="person",
            count_type="direct", internal_external="internal", reporting_year=2025,
        )
        # Meme metrique, annee differente : doit produire un refus PERIOD_MISMATCH
        # si on n'isole pas 2025 (le filtre reporting_year doit l'exclure).
        seed_submission(
            submission_id="SUB-E", organization_id="OL-B", user_id="USER-B",
            raw_text="In 2024, 15 youth completed our training program.",
            candidate_id="C-E", quote="15 youth completed our training program",
            value=15, metric_code="PEOPLE_TRAINED", iaooi_value="OUTPUT", unit_code="person",
            count_type="direct", internal_external="external", reporting_year=2024,
        )

        confirm(client, "SUB-A", reporting_year=2025)
        confirm(client, "SUB-B", reporting_year=2025)
        confirm(client, "SUB-C", reporting_year=2025)
        confirm(client, "SUB-D", reporting_year=2025)
        confirm(client, "SUB-E", reporting_year=2024)

        # --- Annexe A #9 : POST /aggregations/run ---
        run_ol_a = client.post("/aggregations/run", json={
            "view": "ol", "scope_organization_id": "OL-A", "group_by": "network",
            "filters": {"reporting_year": 2025},
        }).json()
        ol_a_external = next((a["value"] for a in run_ol_a.get("aggregates", [])
                              if a["metric_code"] == "PEOPLE_TRAINED" and a["population"]["internal_external"] == "external"), None)
        ol_a_internal = next((a["value"] for a in run_ol_a.get("aggregates", [])
                              if a["metric_code"] == "PEOPLE_TRAINED" and a["population"]["internal_external"] == "internal"), None)
        check("vue OL (OL-A, 2025) : agregat externe = 45, interne = 20 (deux agregats distincts, RI-04)",
              ol_a_external == 45 and ol_a_internal == 20, str(run_ol_a.get("aggregates")))

        run_national = client.post("/aggregations/run", json={
            "view": "national", "scope_organization_id": "NO-DEMO", "group_by": "network",
            "filters": {"reporting_year": 2025},
        }).json()
        nat_aggregates = run_national.get("aggregates", [])
        external_total = next((a["value"] for a in nat_aggregates
                               if a["metric_code"] == "PEOPLE_TRAINED" and a["population"]["internal_external"] == "external"), None)
        internal_total = next((a["value"] for a in nat_aggregates
                               if a["metric_code"] == "PEOPLE_TRAINED" and a["population"]["internal_external"] == "internal"), None)
        check("vue nationale (NO-DEMO, 2025) : externe = 45+80 = 125 (AC-01)", external_total == 125, str(nat_aggregates))
        check("vue nationale (NO-DEMO, 2025) : interne = 20, jamais fondu avec l'externe (RI-04/AC-06)",
              internal_total == 20, str(nat_aggregates))
        check("vue nationale : OL-C (hors reseau) exclu, donc pas de 30 dans le total",
              external_total != 155, str(nat_aggregates))

        run_global = client.post("/aggregations/run", json={
            "view": "global", "scope_organization_id": None, "group_by": "network",
            "filters": {"reporting_year": 2025},
        }).json()
        global_external = next((a["value"] for a in run_global.get("aggregates", [])
                                if a["metric_code"] == "PEOPLE_TRAINED" and a["population"]["internal_external"] == "external"), None)
        check("vue mondiale (2025) : externe = 45+80+30 = 155 (OL-C inclus)", global_external == 155, str(run_global))

        run_all_years = client.post("/aggregations/run", json={
            "view": "national", "scope_organization_id": "NO-DEMO", "group_by": "network", "filters": {},
        }).json()
        period_mismatch = [r for r in run_all_years.get("refusals", []) if r["reason"] == "PERIOD_MISMATCH"]
        check("sans filtre d'annee : le melange 2024/2025 produit un refus PERIOD_MISMATCH",
              len(period_mismatch) >= 1, str(run_all_years.get("refusals")))
        check("chaque refus de paire porte l'aggregate_run_id de l'agregat de son seau (CTL-REFUSAL)",
              all(r["aggregate_run_id"] is not None for r in period_mismatch), str(period_mismatch))

        # --- Annexe A #10 : GET /dashboards/{view} ---
        dash_global = client.get("/dashboards/global", params={"reporting_year": 2025}).json()
        check("GET /dashboards/global : aucun 'stale' au premier calcul", dash_global.get("stale") is False)
        check("GET /dashboards/global : 4 conflits DQC affiches (dev-brief 2.11)",
              len(dash_global.get("quality_issues", [])) == 4,
              str([q["issue_id"] for q in dash_global.get("quality_issues", [])]))
        check("GET /dashboards/global : aucune cible/objectif dans la reponse (RI-13)",
              not any(k in dash_global for k in ("target", "goal_value", "objective")))
        check("GET /dashboards/global : official_jci_facts present (vide tant que O-05 n'est pas fourni)",
              dash_global.get("official_jci_facts") == [])

        dash_ol = client.get("/dashboards/ol", params={"scope_organization_id": "OL-A", "reporting_year": 2025}).json()
        check("GET /dashboards/ol : pas de bloc quality_issues hors vue mondiale",
              "quality_issues" not in dash_ol)

        # --- Annexe A #11 : GET /trace/{measurement_id} ---
        agg_id = next(a["measurement_id"] for a in run_national.get("aggregates", [])
                      if a["metric_code"] == "PEOPLE_TRAINED" and a["population"]["internal_external"] == "external")
        trace = client.get(f"/trace/{agg_id}").json()
        check("GET /trace : chaine complete jusqu'au texte source (CTL-TRACE)", trace.get("chain_complete") is True, str(trace)[:500])
        leaves = [e for e in trace["entries"] if e.get("kind") == "leaf"]
        check("GET /trace : 2 mesures locales retrouvees (SUB-A + SUB-B)", len(leaves) == 2, str(len(leaves)))
        check("GET /trace : la citation exacte est retrouvee dans le texte source (CTL-RAW)",
              all(l["submission"]["quote_found_in_raw_text"] and l["ctl_raw_ok"] for l in leaves), str(leaves))

        trace_missing = client.get("/trace/MEAS-INEXISTANT").json()
        check("GET /trace sur un id inconnu -> 404 propre (pas une 500)",
              client.get("/trace/MEAS-INEXISTANT").status_code == 404)

        # --- Annexe A #7 : GET /measurements/{id} reconstruit un MO complet ---
        leaf_id = leaves[0]["measurement_id"]
        mo = client.get(f"/measurements/{leaf_id}").json()
        check("GET /measurements/{id} : MO complet avec derivation[]", bool(mo.get("derivation")), str(mo.get("derivation")))
        check("GET /measurements/{id} : aggregation.equivalence_key present (calculee par le moteur, RI-03)",
              mo.get("aggregation", {}).get("equivalence_key") not in (None, ""))

        # --- Annexe A #6 : GET /projects/{id} ---
        project_id = mo["subject"]["id"]
        project = client.get(f"/projects/{project_id}").json()
        check("GET /projects/{id} : 4 tables de classification presentes",
              set(project.get("axes", {}).keys()) == {"area_of_opportunity", "programme", "rise_pillars", "sdgs"})
        check("GET /projects/{id} : MO rattaches presents", len(project.get("measurements", [])) >= 1)

        # --- Annexe A #12 : POST /aggregations/check-pair ---
        leaf_ids = [l["measurement_id"] for l in leaves]
        pair = client.post("/aggregations/check-pair",
                            json={"measurement_id_a": leaf_ids[0], "measurement_id_b": leaf_ids[1]}).json()
        check("check-pair(SUB-A, SUB-B) : compatibles (meme cle d'equivalence)", pair.get("compatible") is True, str(pair))

        internal_leaf = client.get("/aggregations/run")  # sanity: GET not allowed on POST-only route
        check("GET /aggregations/run (mauvaise methode) -> 405, pas une 500", internal_leaf.status_code == 405)

        # --- Annexe A #8 : POST /measurements/{id}/review ---
        review_ok = client.post(f"/measurements/{leaf_id}/review", json={"action": "validate", "reason": None}).json()
        check("review(validate) : verification_status = validated", review_ok.get("verification_status") == "validated")

        review_flag = client.post(f"/measurements/{leaf_id}/review",
                                   json={"action": "flag", "reason": "a verifier"}).json()
        check("review(flag) : verification_status = flagged, raison conservee",
              review_flag.get("verification_status") == "flagged" and review_flag.get("flag", {}).get("reason") == "a verifier")

        review_unflag = client.post(f"/measurements/{leaf_id}/review", json={"action": "unflag"}).json()
        check("review(unflag) : retour a reported", review_unflag.get("verification_status") == "reported")

        # Chiffre JCI officiel : la revue doit toujours etre refusee (T4/RI-05).
        db = SessionLocal()
        try:
            db.add(models.Measurement(
                measurement_id="MEAS-JCI-TEST", standard="PROPOSED_STANDARD:MEASUREMENT-OBJECT-v1",
                metric_code="VOLUNTEERS", metric_label_source="test", layer="OFFICIAL_JCI_FACT",
                value=100, value_status="extracted", verification_status="reported",
            ))
            db.commit()
        finally:
            db.close()
        resp_jci = client.post("/measurements/MEAS-JCI-TEST/review", json={"action": "validate"})
        check("review sur un chiffre JCI officiel -> refuse (409, T4/RI-05)", resp_jci.status_code == 409, str(resp_jci.status_code))

        review_missing = client.post("/measurements/MEAS-INEXISTANT/review", json={"action": "validate"})
        check("review sur une mesure inconnue -> 404", review_missing.status_code == 404)

    _TMP_DB.unlink(missing_ok=True)

    print()
    if FAILURES:
        print(f"ECHEC(S) : {len(FAILURES)}/{len(FAILURES)} test(s) rate(s) ci-dessus")
        return 1
    print("TOUS LES AUTO-TESTS PHASE 3 PASSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
