from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Month(Base):
    __tablename__ = "months"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    translation = Column(String(50))
    number = Column(Integer)
    
    days = relationship("Day", back_populates="month")

class Day(Base):
    __tablename__ = "days"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    month_id = Column(Integer, ForeignKey("months.id"))
    special_event = Column(Text, nullable=True)
    
    month = relationship("Month", back_populates="days")
    readings = relationship("Reading", back_populates="day")

class Reading(Base):
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("days.id"))
    period = Column(String(20))  # matin ou soir
    content = Column(Text)
    author = Column(String(100))
    source_book = Column(String(200))
    page = Column(String(50))
    reference = Column(String(50))
    
    day = relationship("Day", back_populates="readings")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    author = Column(String(100))
    url = Column(String(255)) 