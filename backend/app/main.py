"""Point d'entrée FastAPI.

Voir dev-brief.md Annexe A pour les 13 points d'entrée prévus. Seuls ceux qui
ne dépendent pas du pipeline IA (Phase 2) ou du moteur d'agrégation branché
(Phase 3) sont câblés ici pour l'instant — c'est le socle (Phase 1).
"""
from __future__ import annotations

from fastapi import FastAPI

from app.routers import measurements, projects, submissions, taxonomy

app = FastAPI(title="NEXUS API", version="0.1.0")

app.include_router(submissions.router)
app.include_router(projects.router)
app.include_router(measurements.router)
app.include_router(taxonomy.router)


@app.get("/health")
def health():
    return {"status": "ok"}
