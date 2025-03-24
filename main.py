from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

import uvicorn
import os

import model


# Modèle Pydantic
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float

    class Config:
        from_attributes = True

app = FastAPI(
    title="Mon API FastAPI",
    description="Une API simple créée avec FastAPI",
    version="1.0.0"
)

# Configuration de la base de données
if os.environ.get("RENDER"):
    # En production sur Render
    SQLALCHEMY_DATABASE_URL = "sqlite:///memory:"
else:
    # En développement local
    SQLALCHEMY_DATABASE_URL = "sqlite:///./items.db"

# Dépendance pour obtenir la session DB
def get_db():
    db = model.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Bienvenue sur mon API FastAPI!"}

@app.get("/items/", response_model=List[Item])
async def get_items(db: Session = Depends(get_db)):
    items = db.query(model.ItemDB).all()
    return items

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(model.ItemDB).filter(model.ItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    return item

@app.post("/items/", response_model=Item)
async def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = model.ItemDB(**item.model_dump(exclude={'id'}))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 