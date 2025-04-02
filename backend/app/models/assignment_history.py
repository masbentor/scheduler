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

class FairnessMetrics(BaseModel):
    """Model for tracking fairness metrics per person"""
    person: str = Field(..., description="Name of the person")
    group_id: str = Field(..., description="ID of the group the person belongs to")
    
    # Year-to-date statistics
    ytd_regular_days: int = Field(0, description="Year-to-date regular weekday assignments")
    ytd_friday_days: int = Field(0, description="Year-to-date Friday assignments")
    ytd_weekend_days: int = Field(0, description="Year-to-date weekend assignments")
    ytd_holiday_days: int = Field(0, description="Year-to-date holiday assignments")
    ytd_long_weekend_days: int = Field(0, description="Year-to-date long weekend middle day assignments")
    ytd_weighted_score: float = Field(0.0, description="Year-to-date total weighted score")
    ytd_total_assignments: int = Field(0, description="Year-to-date total assignments")
    
    # Fairness scores
    fairness_score: float = Field(0.0, description="Overall fairness score (0-1)")
    weighted_fairness_score: float = Field(0.0, description="Fairness score for weighted days (0-1)")
    regular_fairness_score: float = Field(0.0, description="Fairness score for regular days (0-1)")
    
    # Last assignment info
    last_assignment_date: Optional[date] = Field(None, description="Date of last assignment")
    days_since_last_assignment: int = Field(0, description="Days since last assignment")
    
    model_config = ConfigDict(from_attributes=True)

    def calculate_fairness_scores(self, group_averages: AssignmentStats) -> None:
        """Calculate fairness scores based on group averages"""
        if group_averages.total_assignments == 0:
            return

        # Calculate regular days fairness
        if group_averages.regular_days > 0:
            self.regular_fairness_score = min(1.0, self.ytd_regular_days / group_averages.regular_days)

        # Calculate weighted days fairness
        if group_averages.total_weighted_score > 0:
            self.weighted_fairness_score = min(1.0, self.ytd_weighted_score / group_averages.total_weighted_score)

        # Overall fairness is average of regular and weighted scores
        self.fairness_score = (self.regular_fairness_score + self.weighted_fairness_score) / 2 