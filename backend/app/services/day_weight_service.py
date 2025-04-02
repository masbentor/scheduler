from datetime import date
from typing import Dict, List
from app.models.assignment_history_db import DayType
from app.models.holiday import Holiday
from app.services.long_weekend_service import LongWeekendService

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
        self.long_weekend_service = LongWeekendService()
    
    def get_base_weight(self, day_type: DayType) -> float:
        """Get the base weight for a day type
        
        Args:
            day_type: Type of day to get weight for
            
        Returns:
            float: Weight for the day type
        """
        return self._weights[day_type]
    
    def set_weight(self, day_type: DayType, weight: float) -> None:
        """Set a custom weight for a day type
        
        Args:
            day_type: Type of day to set weight for
            weight: New weight value (must be positive)
            
        Raises:
            ValueError: If weight is not positive
        """
        if weight <= 0:
            raise ValueError("Weight must be positive")
        self._weights[day_type] = weight
    
    def calculate_weight(self, target_date: date, holidays: List[Holiday]) -> float:
        """Calculate the weight for a specific date
        
        Args:
            target_date: Date to calculate weight for
            holidays: List of holidays to consider
            
        Returns:
            float: Weight for the date
        """
        # Check if it's a middle day of a long holiday period
        if self.long_weekend_service.is_middle_day(target_date, holidays):
            return self.get_base_weight(DayType.LONG_WEEKEND_MIDDLE)
        
        # Check if it's a holiday
        for holiday in holidays:
            if target_date in holiday.get_dates():
                return self.get_base_weight(DayType.HOLIDAY)
        
        # Check if it's a weekend
        if self.is_weekend(target_date):
            return self.get_base_weight(DayType.WEEKEND)
        
        # Check if it's a Friday
        if self.is_friday(target_date):
            return self.get_base_weight(DayType.FRIDAY)
        
        # Regular day
        return self.get_base_weight(DayType.REGULAR)
    
    def is_weekend(self, target_date: date) -> bool:
        """Check if a date is a weekend (Saturday or Sunday)
        
        Args:
            target_date: Date to check
            
        Returns:
            bool: True if the date is a weekend
        """
        return target_date.weekday() >= 5
    
    def is_friday(self, target_date: date) -> bool:
        """Check if a date is a Friday
        
        Args:
            target_date: Date to check
            
        Returns:
            bool: True if the date is a Friday
        """
        return target_date.weekday() == 4
    
    def get_day_type(self, target_date: date, is_holiday: bool = False) -> DayType:
        """Get the type of a specific date
        
        Args:
            target_date: Date to check
            is_holiday: Whether the date is a holiday
            
        Returns:
            DayType: Type of the date
        """
        if is_holiday:
            return DayType.HOLIDAY
        
        if self.is_weekend(target_date):
            return DayType.WEEKEND
        
        if self.is_friday(target_date):
            return DayType.FRIDAY
        
        return DayType.REGULAR 