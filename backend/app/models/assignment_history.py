from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .assignment_history_db import DayType

class AssignmentHistory(BaseModel):
    """Model for tracking assignment history and fairness metrics"""
    person: str = Field(..., description="Name of the person assigned")
    group_id: str = Field(..., description="ID of the group the person belongs to")
    assignment_date: date = Field(..., description="Date of the assignment")
    day_type: DayType = Field(..., description="Type of day (regular, weekend, holiday, etc.)")
    weight: float = Field(..., description="Weight applied to this assignment")
    
    # Cumulative statistics
    cumulative_regular_days: int = Field(0, description="Total regular days assigned to this person")
    cumulative_weighted_days: float = Field(0.0, description="Total weighted days assigned to this person")
    cumulative_total_days: int = Field(0, description="Total days assigned to this person")

class AssignmentStats(BaseModel):
    """Model for assignment statistics"""
    regular_days: int = Field(0, description="Count of regular weekday assignments")
    friday_count: int = Field(0, description="Count of Friday assignments")
    weekend_days: int = Field(0, description="Count of weekend day assignments")
    holiday_days: int = Field(0, description="Count of holiday assignments")
    long_weekend_days: int = Field(0, description="Count of long weekend middle day assignments")
    total_weighted_score: float = Field(0.0, description="Total weighted score of all assignments")
    total_assignments: int = Field(0, description="Total number of assignments")
    
    model_config = ConfigDict(from_attributes=True) 