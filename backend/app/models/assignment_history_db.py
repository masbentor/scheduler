from sqlalchemy import Column, Integer, String, Date, Float, Enum, DateTime, ForeignKey
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

    @classmethod
    def get_base_weight(cls, day_type: 'DayType') -> float:
        """Get the base weight for a day type"""
        weights = {
            cls.REGULAR: 1.0,
            cls.FRIDAY: 1.2,
            cls.WEEKEND: 1.5,
            cls.HOLIDAY: 2.0,
            cls.LONG_WEEKEND_MIDDLE: 2.5
        }
        return weights[day_type]

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

class FairnessMetricsDB(Base):
    """Database model for tracking fairness metrics per person"""
    __tablename__ = "fairness_metrics"

    id = Column(Integer, primary_key=True, index=True)
    person = Column(String, index=True, nullable=False)
    group_id = Column(String, index=True, nullable=False)
    
    # Year-to-date statistics
    ytd_regular_days = Column(Integer, default=0)
    ytd_friday_days = Column(Integer, default=0)
    ytd_weekend_days = Column(Integer, default=0)
    ytd_holiday_days = Column(Integer, default=0)
    ytd_long_weekend_days = Column(Integer, default=0)
    ytd_weighted_score = Column(Float, default=0.0)
    ytd_total_assignments = Column(Integer, default=0)
    
    # Rolling fairness scores
    fairness_score = Column(Float, default=0.0)  # Overall fairness score (0-1)
    weighted_fairness_score = Column(Float, default=0.0)  # Fairness score for weighted days
    regular_fairness_score = Column(Float, default=0.0)  # Fairness score for regular days
    
    # Last assignment tracking
    last_assignment_date = Column(Date, nullable=True)
    days_since_last_assignment = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    class Config:
        orm_mode = True 