from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class BookBase(BaseModel):
    title: str
    author: str
    url: Optional[str] = None

class Book(BookBase):
    id: int
    
    class Config:
        from_attributes = True

class ReadingBase(BaseModel):
    period: str
    content: str
    author: str
    source_book: str
    page: Optional[str] = None
    reference: Optional[str] = None

class Reading(ReadingBase):
    id: int
    day_id: int

    class Config:
        from_attributes = True

class DayBase(BaseModel):
    date: date
    special_event: Optional[str] = None

class Day(DayBase):
    id: int
    month_id: int
    readings: List[Reading] = []

    class Config:
        from_attributes = True

class MonthBase(BaseModel):
    name: str
    translation: str
    number: int

class Month(MonthBase):
    id: int
    days: List[Day] = []

    class Config:
        from_attributes = True 