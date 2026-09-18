"""Connexion SQLAlchemy à PostgreSQL (Supabase).

La connexion n'est établie qu'à l'usage (lazy) : ce module s'importe sans
erreur même sans DATABASE_URL valide, ce qui permet de tester le reste du
code (services, schémas) sans base de données disponible.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    url = settings.database_url or "postgresql://placeholder:placeholder@localhost/placeholder"
    return create_engine(url, pool_pre_ping=True, future=True)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
