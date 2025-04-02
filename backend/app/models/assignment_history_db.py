from sqlalchemy import Column, Integer, String, Date, Float, Enum, DateTime
from sqlalchemy.sql import func
from app.config.database import Base
import enum

class DayType(str, enum.Enum):
    """Enum for different types of days with their base weights"""
    REGULAR = "regular"  # Regular weekday (Mon-Thu)
    FRIDAY = "friday"    # Fridays (special handling)
    WEEKEND = "weekend"  # Weekend days
    HOLIDAY = "holiday"  # Official holidays
    LONG_WEEKEND_MIDDLE = "long_weekend_middle"  # Middle days of long weekends

class AssignmentHistoryDB(Base):
    """Database model for tracking assignment history and fairness metrics"""
    __tablename__ = "assignment_history"

    id = Column(Integer, primary_key=True, index=True)
    person = Column(String, index=True, nullable=False)
    group_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False, index=True)
    day_type = Column(Enum(DayType), nullable=False)
    weight = Column(Float, nullable=False)  # Actual weight applied to this assignment
    
    # Cumulative statistics for the person in their group
    cumulative_regular_days = Column(Integer, default=0)
    cumulative_weighted_days = Column(Float, default=0.0)
    cumulative_total_days = Column(Integer, default=0)

    # Timestamps for tracking
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 