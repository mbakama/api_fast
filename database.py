from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# URL de la base de données
if os.environ.get("DATABASE_URL"):
    # Utiliser Supabase PostgreSQL en production
    SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
elif os.environ.get("RENDER"):
    # SQLite en mémoire pour Render
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
else:
    # SQLite local pour développement
    SQLALCHEMY_DATABASE_URL = "sqlite:///./bahai_readings.db"

# Configuration du moteur selon le type de BD
if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    # PostgreSQL (Supabase)
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
elif SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Autres types de BD
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
