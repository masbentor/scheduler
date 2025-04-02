from datetime import date, timedelta
from typing import Dict, Optional
from app.models.assignment_history_db import DayType

class DayWeightService:
    """Service for calculating weights for different day types"""
    
    def __init__(self):
        # Default weights for different day types
        self._weights: Dict[DayType, float] = {
            DayType.REGULAR: 1.0,        # Base weight for regular days
            DayType.FRIDAY: 1.2,         # Slightly higher for Fridays
            DayType.WEEKEND: 1.5,        # Higher for weekends
            DayType.HOLIDAY: 2.0,        # Double for holidays
            DayType.LONG_WEEKEND_MIDDLE: 2.5  # Highest for middle days of long weekends
        }
    
    def get_base_weight(self, day_type: DayType) -> float:
        """Get the base weight for a day type"""
        return self._weights[day_type]
    
    def set_weight(self, day_type: DayType, weight: float) -> None:
        """Set a custom weight for a day type"""
        if weight <= 0:
            raise ValueError("Weight must be positive")
        self._weights[day_type] = weight
    
    def calculate_weight(self, target_date: date, day_type: DayType, 
                        is_long_weekend_middle: bool = False) -> float:
        """Calculate the final weight for a given date and day type
        
        Args:
            target_date: The date to calculate weight for
            day_type: The type of day (regular, weekend, holiday, etc.)
            is_long_weekend_middle: Whether this is a middle day of a long weekend
            
        Returns:
            float: The calculated weight for the day
        """
        # If it's explicitly marked as a middle day of a long weekend,
        # use that weight regardless of other factors
        if is_long_weekend_middle:
            return self._weights[DayType.LONG_WEEKEND_MIDDLE]
            
        # Get the base weight for the day type
        weight = self._weights[day_type]
        
        # Special case: If it's a holiday that falls on a weekend,
        # use the higher of the two weights
        if day_type == DayType.HOLIDAY:
            if target_date.weekday() >= 5:  # Weekend
                weight = max(weight, self._weights[DayType.WEEKEND])
                
        return weight
    
    def is_weekend(self, target_date: date) -> bool:
        """Check if a date falls on a weekend"""
        return target_date.weekday() >= 5
    
    def is_friday(self, target_date: date) -> bool:
        """Check if a date falls on a Friday"""
        return target_date.weekday() == 4
    
    def get_day_type(self, target_date: date, is_holiday: bool = False) -> DayType:
        """Determine the type of day for a given date
        
        Args:
            target_date: The date to check
            is_holiday: Whether this date is marked as a holiday
            
        Returns:
            DayType: The determined day type
        """
        if is_holiday:
            return DayType.HOLIDAY
            
        if self.is_weekend(target_date):
            return DayType.WEEKEND
            
        if self.is_friday(target_date):
            return DayType.FRIDAY
            
        return DayType.REGULAR 