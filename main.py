from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import SessionLocal, engine
from datetime import date
from pydantic import BaseModel

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Lectures Bahá'íes",
    description="API pour les lectures quotidiennes bahá'íes",
    version="1.0.0"
)

# Dépendance
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ajout des nouveaux schémas pour la création
class MonthCreate(BaseModel):
    name: str
    translation: str
    number: int

class DayCreate(BaseModel):
    date: date
    special_event: Optional[str] = None
    month_id: int

class ReadingCreate(BaseModel):
    period: str
    content: str
    author: str
    source_book: str
    page: Optional[str] = None
    reference: Optional[str] = None
    day_id: int

class BookCreate(BaseModel):
    title: str
    author: str
    url: Optional[str] = None

# Schémas pour la mise à jour
class MonthUpdate(BaseModel):
    name: Optional[str] = None
    translation: Optional[str] = None
    number: Optional[int] = None

class DayUpdate(BaseModel):
    date: Optional[date] = None
    special_event: Optional[str] = None
    month_id: Optional[int] = None

class ReadingUpdate(BaseModel):
    period: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    source_book: Optional[str] = None
    page: Optional[str] = None
    reference: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None

@app.get("/readings/{date}", response_model=List[schemas.Reading])
def get_readings_by_date(date_str: str, db: Session = Depends(get_db)):
    try:
        requested_date = date.fromisoformat(date_str)
        day = db.query(models.Day).filter(models.Day.date == requested_date).first()
        if day is None:
            raise HTTPException(status_code=404, detail="Date non trouvée")
        return day.readings
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")

@app.get("/readings/month/{month_name}", response_model=List[schemas.Reading])
def get_readings_by_month(month_name: str, db: Session = Depends(get_db)):
    month = db.query(models.Month).filter(models.Month.name == month_name).first()
    if month is None:
        raise HTTPException(status_code=404, detail="Mois non trouvé")
    
    readings = []
    for day in month.days:
        readings.extend(day.readings)
    return readings

@app.get("/events", response_model=List[dict])
def get_special_events(db: Session = Depends(get_db)):
    days = db.query(models.Day).filter(models.Day.special_event.isnot(None)).all()
    return [{"date": day.date, "event": day.special_event} for day in days]

@app.get("/books", response_model=List[schemas.Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

# Ajout des nouvelles routes pour la création
@app.post("/months/", response_model=schemas.Month, status_code=status.HTTP_201_CREATED)
def create_month(month: MonthCreate, db: Session = Depends(get_db)):
    db_month = models.Month(**month.model_dump())
    db.add(db_month)
    try:
        db.commit()
        db.refresh(db_month)
        return db_month
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création du mois: {str(e)}")

@app.post("/days/", response_model=schemas.Day, status_code=status.HTTP_201_CREATED)
def create_day(day: DayCreate, db: Session = Depends(get_db)):
    # Vérifier si le mois existe
    month = db.query(models.Month).filter(models.Month.id == day.month_id).first()
    if not month:
        raise HTTPException(status_code=404, detail="Mois non trouvé")
    
    db_day = models.Day(**day.model_dump())
    db.add(db_day)
    try:
        db.commit()
        db.refresh(db_day)
        return db_day
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création du jour: {str(e)}")

@app.post("/readings/", response_model=schemas.Reading, status_code=status.HTTP_201_CREATED)
def create_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    # Vérifier si le jour existe
    day = db.query(models.Day).filter(models.Day.id == reading.day_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Jour non trouvé")
    
    # Vérifier si la période est valide
    if reading.period not in ["matin", "soir"]:
        raise HTTPException(status_code=400, detail="La période doit être 'matin' ou 'soir'")
    
    db_reading = models.Reading(**reading.model_dump())
    db.add(db_reading)
    try:
        db.commit()
        db.refresh(db_reading)
        return db_reading
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création de la lecture: {str(e)}")

@app.post("/books/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    # Vérifier si le livre existe déjà
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
        return db_book
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la création du livre: {str(e)}")

# Routes de mise à jour
@app.put("/months/{month_id}", response_model=schemas.Month)
def update_month(month_id: int, month: MonthUpdate, db: Session = Depends(get_db)):
    db_month = db.query(models.Month).filter(models.Month.id == month_id).first()
    if not db_month:
        raise HTTPException(status_code=404, detail="Mois non trouvé")
    
    for field, value in month.model_dump(exclude_unset=True).items():
        setattr(db_month, field, value)
    
    try:
        db.commit()
        db.refresh(db_month)
        return db_month
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.put("/days/{day_id}", response_model=schemas.Day)
def update_day(day_id: int, day: DayUpdate, db: Session = Depends(get_db)):
    db_day = db.query(models.Day).filter(models.Day.id == day_id).first()
    if not db_day:
        raise HTTPException(status_code=404, detail="Jour non trouvé")
    
    # Vérifier si le nouveau month_id existe
    if day.month_id is not None:
        month = db.query(models.Month).filter(models.Month.id == day.month_id).first()
        if not month:
            raise HTTPException(status_code=404, detail="Mois spécifié non trouvé")
    
    for field, value in day.model_dump(exclude_unset=True).items():
        setattr(db_day, field, value)
    
    try:
        db.commit()
        db.refresh(db_day)
        return db_day
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.put("/readings/{reading_id}", response_model=schemas.Reading)
def update_reading(reading_id: int, reading: ReadingUpdate, db: Session = Depends(get_db)):
    db_reading = db.query(models.Reading).filter(models.Reading.id == reading_id).first()
    if not db_reading:
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    
    # Vérifier si la période est valide
    if reading.period is not None and reading.period not in ["matin", "soir"]:
        raise HTTPException(status_code=400, detail="La période doit être 'matin' ou 'soir'")
    
    for field, value in reading.model_dump(exclude_unset=True).items():
        setattr(db_reading, field, value)
    
    try:
        db.commit()
        db.refresh(db_reading)
        return db_reading
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    
    try:
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la mise à jour: {str(e)}") 