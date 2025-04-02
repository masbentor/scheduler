from datetime import date, timedelta
from typing import List, Set, Dict, Tuple
from app.models.holiday import Holiday
from app.models.assignment_history_db import DayType

class LongWeekendService:
    """Service for detecting and managing long weekends and their middle days"""
    
    def __init__(self):
        self._min_long_weekend_days = 3  # Minimum days to consider as a long weekend
    
    def find_long_weekends(self, holidays: List[Holiday], year: int, month: int) -> List[Dict[str, date]]:
        """Find all long weekends in a given month based on holiday periods
        
        Args:
            holidays: List of holidays to consider
            year: Year to check
            month: Month to check
            
        Returns:
            List of dictionaries containing start_date and end_date for each long weekend
        """
        long_weekends = []
        
        for holiday in holidays:
            # Get all dates in this holiday period
            holiday_dates = holiday.get_dates()
            
            # Skip if holiday doesn't overlap with target month
            if not any(d.year == year and d.month == month for d in holiday_dates):
                continue
            
            # If holiday period is long enough, it's a long weekend
            if len(holiday_dates) >= self._min_long_weekend_days:
                long_weekends.append({
                    'start_date': holiday_dates[0],
                    'end_date': holiday_dates[-1]
                })
        
        return long_weekends
    
    def get_middle_days(self, start_date: date, end_date: date) -> Set[date]:
        """Get the middle days of a long weekend period
        
        Args:
            start_date: Start date of the period
            end_date: End date of the period
            
        Returns:
            Set of dates that are middle days
        """
        if start_date >= end_date:
            return set()
        
        middle_days = set()
        current = start_date + timedelta(days=1)
        
        while current < end_date:
            middle_days.add(current)
            current += timedelta(days=1)
        
        return middle_days
    
    def is_middle_day(self, target_date: date, holidays: List[Holiday]) -> bool:
        """Check if a specific date is a middle day of a holiday period
        
        Args:
            target_date: Date to check
            holidays: List of holidays to consider
            
        Returns:
            bool: True if the date is a middle day of a holiday period
        """
        for holiday in holidays:
            dates = holiday.get_dates()
            if len(dates) >= self._min_long_weekend_days:
                if target_date in dates and target_date != dates[0] and target_date != dates[-1]:
                    return True
        return False
    
    def analyze_period(self, start_date: date, end_date: date, holidays: List[Holiday]) -> Dict[date, DayType]:
        """Analyze a period to determine day types, including long weekend detection
        
        Args:
            start_date: Start of the period to analyze
            end_date: End of the period to analyze
            holidays: List of holidays to consider
            
        Returns:
            Dictionary mapping dates to their day types
        """
        day_types = {}
        current = start_date
        
        # Create a map of holiday dates for faster lookup
        holiday_dates = {}
        for holiday in holidays:
            for d in holiday.get_dates():
                holiday_dates[d] = holiday
        
        while current <= end_date:
            # Check if it's part of a holiday period
            holiday = holiday_dates.get(current)
            
            if holiday:
                # If it's part of a long enough holiday period, check if it's a middle day
                if len(holiday.get_dates()) >= self._min_long_weekend_days:
                    dates = holiday.get_dates()
                    if current != dates[0] and current != dates[-1]:
                        day_types[current] = DayType.LONG_WEEKEND_MIDDLE
                    else:
                        day_types[current] = DayType.HOLIDAY
                else:
                    day_types[current] = DayType.HOLIDAY
            elif current.weekday() >= 5:  # Weekend
                day_types[current] = DayType.WEEKEND
            elif current.weekday() == 4:  # Friday
                day_types[current] = DayType.FRIDAY
            else:
                day_types[current] = DayType.REGULAR
            
            current += timedelta(days=1)
            
        return day_types 