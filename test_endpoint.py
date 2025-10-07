from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import schemas
from datetime import date

# Version simplifiée pour test
class TestReadingCreate(BaseModel):
    date: str  # Changé en str pour le test
    title: str
    month_id: int
    morning_verse: str
    morning_author: str
    evening_verse: str
    evening_author: str

app = FastAPI()

@app.post("/test-reading/")
def test_reading(reading: TestReadingCreate):
    return {"message": "Test réussi", "data": reading}

models.Base.metadata.create_all(bind=engine)
