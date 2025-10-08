from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

try:
    # Charge les variables d'environnement depuis un fichier .env si présent
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv est optionnel en production
    pass


def _normalize_postgres_driver(url: str) -> str:
    """Force l'utilisation du driver psycopg3 si une URL Postgres générique est fournie.

    Supabase fournit souvent des URLs de forme postgresql://. SQLAlchemy utilisera
    par défaut psycopg2 si disponible. Comme nous dépendons de psycopg (v3), on
    convertit en postgresql+psycopg:// pour garantir la compatibilité.
    """
    if url and (url.startswith("postgresql://") or url.startswith("postgres://")):
        return url.replace("postgres://", "postgresql+psycopg://").replace(
            "postgresql://", "postgresql+psycopg://"
        )
    return url


def get_database_url() -> str:
    # Priorité aux variables d'environnement (Supabase)
    env_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    if env_url:
        return _normalize_postgres_driver(env_url)

    # Compat hébergeur
    if os.environ.get("RENDER"):
        # Mémoire SQLite (corrigé au format valide)
        return "sqlite:///:memory:"

    # Fallback local SQLite
    return "sqlite:///./bahai_readings.db"


SQLALCHEMY_DATABASE_URL = get_database_url()

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()