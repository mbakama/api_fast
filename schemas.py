from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# ===================================================================
# SCHEMAS FOR BOOK
# ===================================================================

class BookBase(BaseModel):
    title: str
    author: str
    url: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None

class Book(BookBase):
    id: int
    class Config:
        from_attributes = True

# ===================================================================
# SCHEMAS FOR READING
# ===================================================================

class ReadingBase(BaseModel):
    period: str
    content: str
    author: str
    source_book: str
    page: Optional[str] = None
    reference: Optional[str] = None

class ReadingCreate(ReadingBase):
    day_id: int

class ReadingUpdate(BaseModel):
    period: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    source_book: Optional[str] = None
    page: Optional[str] = None
    reference: Optional[str] = None

class Reading(ReadingBase):
    id: int
    day_id: int
    class Config:
        from_attributes = True

# ===================================================================
# SCHEMAS FOR DAY
# ===================================================================

class DayBase(BaseModel):
    date: date
    special_event: Optional[str] = None

class DayCreate(DayBase):
    month_id: int

class DayUpdate(BaseModel):
    date: Optional[date] = None
    special_event: Optional[str] = None
    month_id: Optional[int] = None

class Day(DayBase):
    id: int
    month_id: int
    readings: List[Reading] = []
    class Config:
        from_attributes = True

# ===================================================================
# SCHEMAS FOR MONTH
# ===================================================================

class MonthBase(BaseModel):
    name: str
    translation: str
    number: int

class MonthCreate(MonthBase):
    pass

class MonthUpdate(BaseModel):
    name: Optional[str] = None
    translation: Optional[str] = None
    number: Optional[int] = None

class Month(MonthBase):
    id: int
    days: List[Day] = []
    class Config:
        from_attributes = True

# ===================================================================
# SCHEMAS FOR COMPLEX RESPONSES
# ===================================================================

class MonthlyReadingsResponse(BaseModel):
    month: str
    count: int
    readings: List[Reading]

# Update forward references to resolve circular dependencies
Month.model_rebuild()
Day.model_rebuild()
