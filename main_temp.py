from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine
from datetime import date, datetime
from zoneinfo import ZoneInfo
from seed_data import get_day_info_from_gregorian, gregorian_to_bahai_date, get_feast_info

# Temporairement désactivé pour permettre le démarrage du serveur
# import os
# from dotenv import load_dotenv
# from supabase import create_client, Client

# Charger les variables d'environnement
# load_dotenv()

# Configuration Supabase
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialiser le client Supabase
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Lectures Bahá'íes",
    description="API pour les lectures quotidiennes bahá'íes",
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

@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {"message": "API Bahá'íe fonctionne !", "status": "active"}

@app.get("/readings/today", response_model=schemas.APIResponse[schemas.Reading])
def get_readings_today(db: Session = Depends(get_db)):
    today = get_current_date()
    now = datetime.now(TIMEZONE)
    current_hour = now.hour

    # Déterminer la période: matin (0h-12h59) ou soir (13h-23h59)
    period = "matin" if current_hour < 13 else "soir"

    day = db.query(models.Day).filter(models.Day.date == today).first()
    if day is None:
        return schemas.APIResponse(code=404, message="No readings found for today", data=None)

    # Filtrer pour obtenir uniquement la lecture de la période actuelle
    reading = next((r for r in day.readings if r.period == period), None)
    if reading is None:
        return schemas.APIResponse(code=404, message=f"No reading found for period '{period}'", data=None)

    return schemas.APIResponse(
        code=200,
        message=f"Reading for {period} on {today}",
        data=reading
    )

@app.get("/convert-gregorian-to-bahai/{year}/{month}/{day}", response_model=schemas.APIResponse)
def convert_gregorian_to_bahai(year: int, month: int, day: int):
    """
    Convertit une date grégorienne vers le calendrier Baha'i en utilisant des paramètres séparés.
    """
    try:
        gregorian_date = date(year, month, day)
        info = get_day_info_from_gregorian(gregorian_date)
        feast_info = get_feast_info(gregorian_date)
        bahai_day, bahai_month, bahai_year = gregorian_to_bahai_date(gregorian_date)

        return schemas.APIResponse(
            code=200,
            message=f"Conversion de la date {gregorian_date}",
            data={
                "gregorian_date": {
                    "year": year,
                    "month": month,
                    "day": day,
                    "iso_format": gregorian_date.isoformat()
                },
                "formatted_info": info,
                "feast": feast_info,
                "bahai_date": {
                    "day": bahai_day,
                    "month": bahai_month,
                    "year": bahai_year
                }
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Date invalide: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la conversion: {str(e)}")

# =================== ENDPOINTS SUPABASE TEMPORAIREMENT DÉSACTIVÉS ===================
# Les endpoints Supabase seront réactivés une fois le problème d'import résolu

@app.get("/supabase/status")
def get_supabase_status():
    """Vérifier le statut de la connexion Supabase (temporairement désactivé)"""
    return {
        "status": "maintenance",
        "message": "Endpoints Supabase temporairement désactivés - Problème d'import à résoudre",
        "note": "Voir les logs du serveur pour plus de détails"
    }
