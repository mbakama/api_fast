from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine
from datetime import date, datetime
from zoneinfo import ZoneInfo
from seed_data import get_day_info_from_gregorian, gregorian_to_bahai_date, get_feast_info
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Lectures Bahá'íes",
    description="API pour les lectures quotidiennes bahá'íes avec support Supabase",
    version="1.0.0"
)

# Fuseau horaire pour Kinshasa (UTC+1)
TIMEZONE = ZoneInfo("Africa/Kinshasa")

def get_current_date() -> date:
    """Retourne la date actuelle dans le fuseau horaire de Kinshasa"""
    return datetime.now(TIMEZONE).date()

# Dépendance
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/supabase/status")
def get_supabase_status():
    """Vérifier le statut de la connexion Supabase"""
    if supabase is None:
        return {"status": "error", "message": "Supabase n'est pas configuré"}

    try:
        # Test simple de connexion
        response = supabase.table('test').select("*").limit(1).execute()
        return {"status": "connected", "message": "Connexion Supabase réussie"}
    except Exception as e:
        return {"status": "error", "message": f"Erreur de connexion: {str(e)}"}

@app.get("/supabase/insert-test")
def insert_test_data():
    """Insérer des données de test dans Supabase"""
    if supabase is None:
        raise HTTPException(status_code=500, detail="Supabase n'est pas configuré")

    try:
        # Données de test
        test_data = {
            "test_field": "Hello from FastAPI",
            "created_at": datetime.now().isoformat()
        }

        # Insérer dans une table de test (à créer dans Supabase)
        response = supabase.table('test_data').insert(test_data).execute()

        return {
            "status": "success",
            "message": "Données insérées avec succès",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion: {str(e)}")

# ... existing code ...
