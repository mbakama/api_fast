from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

# Configuration CORS pour permettre l'accès depuis Swagger UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, permet toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes HTTP
    allow_headers=["*"],  # Permet tous les headers
)

# Configuration pour supporter les caractères Unicode
@app.middleware("http")
async def add_unicode_support(request, call_next):
    response = await call_next(request)
    # S'assurer que la réponse supporte UTF-8
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

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
    
    return schemas.APIResponse(data=reading, message=f"Reading for {period}")


@app.get("/readings/{date_str}", response_model=schemas.APIResponse[List[schemas.Reading]])
def get_readings_by_date(date_str: str, db: Session = Depends(get_db)):
    try:
        requested_date = date.fromisoformat(date_str)
        day = db.query(models.Day).filter(models.Day.date == requested_date).first()
        if day is None:
            return schemas.APIResponse(code=404, message="Date not found", data=[])
        return schemas.APIResponse(data=day.readings)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")

@app.get("/readings/month/{month_name}", response_model=schemas.APIResponse[schemas.MonthlyReadingsResponse])
def get_readings_by_month(month_name: str, db: Session = Depends(get_db)):
    month = db.query(models.Month).filter(models.Month.name == month_name).first()
    if month is None:
        return schemas.APIResponse(code=404, message="Month not found")
    
    readings = []
    for day in month.days:
        readings.extend(day.readings)
    
    response_data = schemas.MonthlyReadingsResponse(
        id=month.id,
        month=month_name,
        count=len(readings),
        readings=readings
    )
    return schemas.APIResponse(data=response_data)

@app.get("/events", response_model=schemas.APIResponse[List[schemas.Event]])
def get_special_events(db: Session = Depends(get_db)):
    days = db.query(models.Day).filter(models.Day.special_event.isnot(None)).all()
    events = [schemas.Event(date=day.date, event=day.special_event) for day in days]
    return schemas.APIResponse(data=events)

@app.get("/books", response_model=schemas.APIResponse[List[schemas.Book]])
def get_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return schemas.APIResponse(data=books)

@app.post("/readings/daily/", response_model=schemas.APIResponse[schemas.Day], status_code=status.HTTP_201_CREATED, summary="Create daily readings (morning and evening)")
def create_daily_readings(daily_readings: schemas.DailyReadingsCreate, db: Session = Depends(get_db)):
    """
    Créer une nouvelle journée avec ses lectures du matin et du soir.
    Accepte tous les caractères Unicode (accents, apostrophes, etc.)
    """
    month = db.query(models.Month).filter(models.Month.id == daily_readings.month_id).first()
    if not month:
        return schemas.APIResponse(code=404, message=f"Month with id {daily_readings.month_id} not found.")

    # Conversion de la date si elle est une string
    if isinstance(daily_readings.date, str):
        try:
            from datetime import datetime
            reading_date = datetime.strptime(daily_readings.date, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Format de date invalide: {daily_readings.date}. Utilisez YYYY-MM-DD")
    else:
        reading_date = daily_readings.date

    day = db.query(models.Day).filter(models.Day.date == reading_date).first()
    if not day:
        day = models.Day(
            date=reading_date,
            title=daily_readings.title,
            month_id=month.id
        )
        db.add(day)
        db.flush()
    elif daily_readings.title:
        day.title = daily_readings.title

    # Création des lectures avec gestion des caractères Unicode
    morning_reading = models.Reading(
        period="matin",
        content=daily_readings.morning_verse,
        author=daily_readings.morning_author,
        reference=daily_readings.morning_reference,
        source_book=daily_readings.morning_reference or "Non spécifié",
        day_id=day.id
    )
    evening_reading = models.Reading(
        period="soir",
        content=daily_readings.evening_verse,
        author=daily_readings.evening_author,
        reference=daily_readings.evening_reference,
        source_book=daily_readings.evening_reference or "Non spécifié",
        day_id=day.id
    )
    db.add_all([morning_reading, evening_reading])

    try:
        db.commit()
        db.refresh(day)
        return schemas.APIResponse(code=201, message=f"Readings for {daily_readings.date} created successfully", data=day)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating daily readings: {str(e)}")

@app.post("/months/", response_model=schemas.APIResponse[schemas.Month], status_code=status.HTTP_201_CREATED)
def create_month(month: schemas.MonthCreate, db: Session = Depends(get_db)):
    db_month = models.Month(**month.model_dump())
    db.add(db_month)
    try:
        db.commit()
        db.refresh(db_month)
        return schemas.APIResponse(code=201, message="Month created successfully", data=db_month)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création du mois: {str(e)}")

@app.post("/days/", response_model=schemas.APIResponse[schemas.Day], status_code=status.HTTP_201_CREATED)
def create_day(day: schemas.DayCreate, db: Session = Depends(get_db)):
    month = db.query(models.Month).filter(models.Month.id == day.month_id).first()
    if not month:
        return schemas.APIResponse(code=404, message="Mois non trouvé")
    
    db_day = models.Day(**day.model_dump())
    db.add(db_day)
    try:
        db.commit()
        db.refresh(db_day)
        return schemas.APIResponse(code=201, message="Day created successfully", data=db_day)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création du jour: {str(e)}")

@app.post("/readings/", response_model=schemas.APIResponse[schemas.Reading], status_code=status.HTTP_201_CREATED)
def create_reading(reading: schemas.ReadingCreate, db: Session = Depends(get_db)):
    day = db.query(models.Day).filter(models.Day.id == reading.day_id).first()
    if not day:
        return schemas.APIResponse(code=404, message="Jour non trouvé")
    
    if reading.period not in ["matin", "soir"]:
        raise HTTPException(status_code=400, detail="La période doit être 'matin' ou 'soir'")
    
    db_reading = models.Reading(**reading.model_dump())
    db.add(db_reading)
    try:
        db.commit()
        db.refresh(db_reading)
        return schemas.APIResponse(code=201, message="Reading created successfully", data=db_reading)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création de la lecture: {str(e)}")

@app.post("/books/", response_model=schemas.APIResponse[schemas.Book], status_code=status.HTTP_201_CREATED)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    existing_book = db.query(models.Book).filter(
        models.Book.title == book.title,
        models.Book.author == book.author
    ).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="Ce livre existe déjà")
    
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    try:
        db.commit()
        db.refresh(db_book)
        return schemas.APIResponse(code=201, message="Book created successfully", data=db_book)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création du livre: {str(e)}")

@app.put("/months/{month_id}", response_model=schemas.APIResponse[schemas.Month])
def update_month(month_id: int, month: schemas.MonthUpdate, db: Session = Depends(get_db)):
    db_month = db.query(models.Month).filter(models.Month.id == month_id).first()
    if not db_month:
        return schemas.APIResponse(code=404, message="Mois non trouvé")
    
    for field, value in month.model_dump(exclude_unset=True).items():
        setattr(db_month, field, value)
    
    try:
        db.commit()
        db.refresh(db_month)
        return schemas.APIResponse(data=db_month)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.put("/days/{day_id}", response_model=schemas.APIResponse[schemas.Day])
def update_day(day_id: int, day: schemas.DayUpdate, db: Session = Depends(get_db)):
    db_day = db.query(models.Day).filter(models.Day.id == day_id).first()
    if not db_day:
        return schemas.APIResponse(code=404, message="Jour non trouvé")
    
    if day.month_id is not None:
        month = db.query(models.Month).filter(models.Month.id == day.month_id).first()
        if not month:
            return schemas.APIResponse(code=404, message="Mois spécifié non trouvé")
    
    for field, value in day.model_dump(exclude_unset=True).items():
        setattr(db_day, field, value)
    
    try:
        db.commit()
        db.refresh(db_day)
        return schemas.APIResponse(data=db_day)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.put("/readings/{reading_id}", response_model=schemas.APIResponse[schemas.Reading])
def update_reading(reading_id: int, reading: schemas.ReadingUpdate, db: Session = Depends(get_db)):
    db_reading = db.query(models.Reading).filter(models.Reading.id == reading_id).first()
    if not db_reading:
        return schemas.APIResponse(code=404, message="Lecture non trouvée")
    
    if reading.period is not None and reading.period not in ["matin", "soir"]:
        raise HTTPException(status_code=400, detail="La période doit être 'matin' ou 'soir'")
    
    for field, value in reading.model_dump(exclude_unset=True).items():
        setattr(db_reading, field, value)
    
    try:
        db.commit()
        db.refresh(db_reading)
        return schemas.APIResponse(data=db_reading)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.put("/books/{book_id}", response_model=schemas.APIResponse[schemas.Book])
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        return schemas.APIResponse(code=404, message="Livre non trouvé")
    
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    
    try:
        db.commit()
        db.refresh(db_book)
        return schemas.APIResponse(data=db_book)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

# Nouveaux endpoints pour la conversion de dates Baha'i

@app.get("/bahai/today", summary="Informations Baha'i du jour actuel")
def get_today_bahai():
    """
    Retourne les informations du jour actuel au format Baha'i.
    Exemple: "26 SEP - 1 Asmá' (Noms - 9ème mois)"
    """
    try:
        current_date = get_current_date()
        info = get_day_info_from_gregorian(current_date)
        feast_info = get_feast_info(current_date)
        return schemas.APIResponse(
            code=200,
            message="Informations du jour actuel",
            data={
                "date_info": info, 
                "gregorian_date": current_date.isoformat(),
                "feast": feast_info
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des informations: {str(e)}")

@app.get("/bahai/date/{date_str}", summary="Conversion d'une date grégorienne vers le calendrier Baha'i")
def get_bahai_date_info(date_str: str):
    """
    Convertit une date grégorienne (format YYYY-MM-DD) vers le calendrier Baha'i.
    Retourne les informations formatées.
    """
    try:
        gregorian_date = date.fromisoformat(date_str)
        info = get_day_info_from_gregorian(gregorian_date)
        feast_info = get_feast_info(gregorian_date)
        bahai_day, bahai_month, bahai_year = gregorian_to_bahai_date(gregorian_date)
        
        return schemas.APIResponse(
            code=200,
            message=f"Conversion de la date {date_str}",
            data={
                "gregorian_date": date_str,
                "formatted_info": info,
                "feast": feast_info,
                "bahai_date": {
                    "day": bahai_day,
                    "month": bahai_month,
                    "year": bahai_year
                }
            }
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la conversion: {str(e)}")

@app.get("/bahai/convert", summary="Conversion avec paramètres de requête")
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

# =================== ENDPOINTS SUPABASE ===================

@app.get("/supabase/status")
def get_supabase_status():
    """Vérifier le statut de la connexion Supabase"""
    if supabase is None:
        return {"status": "error", "message": "Supabase n'est pas configuré"}

    try:
        # Test simple de connexion
        response = supabase.table('test_data').select("*").limit(1).execute()
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

@app.get("/supabase/test-data")
def get_test_data():
    """Récupérer les données de test depuis Supabase"""
    if supabase is None:
        raise HTTPException(status_code=500, detail="Supabase n'est pas configuré")

    try:
        response = supabase.table('test_data').select('*').execute()
        return {
            "status": "success",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")
