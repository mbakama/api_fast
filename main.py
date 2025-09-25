from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine
from datetime import date

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

@app.get("/readings/{date}", response_model=schemas.APIResponse[List[schemas.Reading]])
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
    month = db.query(models.Month).filter(models.Month.id == daily_readings.month_id).first()
    if not month:
        return schemas.APIResponse(code=404, message=f"Month with id {daily_readings.month_id} not found.")

    day = db.query(models.Day).filter(models.Day.date == daily_readings.date).first()
    if not day:
        day = models.Day(
            date=daily_readings.date,
            title=daily_readings.title,
            month_id=month.id
        )
        db.add(day)
        db.flush()
    elif daily_readings.title:
        day.title = daily_readings.title

    morning_reading = models.Reading(
        period="matin",
        content=daily_readings.morning_verse,
        author=daily_readings.morning_author,
        reference=daily_readings.morning_reference,
        source_book=daily_readings.morning_reference,
        day_id=day.id
    )
    evening_reading = models.Reading(
        period="soir",
        content=daily_readings.evening_verse,
        author=daily_readings.evening_author,
        reference=daily_readings.evening_reference,
        source_book=daily_readings.evening_reference,
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
