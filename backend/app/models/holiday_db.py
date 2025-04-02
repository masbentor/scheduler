from sqlalchemy import Column, Integer, String, Date
from ..config.database import Base

class HolidayDB(Base):
    """Database model for holidays"""
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)
    name = Column(String, nullable=True) 