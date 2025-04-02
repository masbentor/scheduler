from datetime import date
import pytest
from app.services.long_weekend_service import LongWeekendService
from app.models.holiday import Holiday
from app.models.assignment_history_db import DayType

@pytest.fixture
def long_weekend_service():
    return LongWeekendService()

@pytest.fixture
def sample_holidays():
    return [
        # Single day holiday
        Holiday(start_date=date(2024, 2, 6), name="Regular Holiday"),
        
        # 4-day Easter holiday
        Holiday(
            start_date=date(2024, 3, 29),
            end_date=date(2024, 4, 1),
            name="Easter"
        ),
        
        # 2-day bridge holiday
        Holiday(
            start_date=date(2024, 5, 23),
            end_date=date(2024, 5, 24),
            name="Bridge Holiday"
        ),
        
        # 3-day New Year holiday
        Holiday(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 3),
            name="New Year Holiday"
        )
    ]

def test_find_long_weekends(long_weekend_service, sample_holidays):
    """Test finding long weekends in a month"""
    # Test January 2024 (3-day New Year holiday)
    jan_long_weekends = long_weekend_service.find_long_weekends(sample_holidays, 2024, 1)
    assert len(jan_long_weekends) == 1
    assert jan_long_weekends[0]['start_date'] == date(2024, 1, 1)
    assert jan_long_weekends[0]['end_date'] == date(2024, 1, 3)
    
    # Test March/April 2024 (4-day Easter holiday)
    mar_long_weekends = long_weekend_service.find_long_weekends(sample_holidays, 2024, 3)
    assert len(mar_long_weekends) == 1
    assert mar_long_weekends[0]['start_date'] == date(2024, 3, 29)
    assert mar_long_weekends[0]['end_date'] == date(2024, 4, 1)
    
    # Test February 2024 (single day holiday - not a long weekend)
    feb_long_weekends = long_weekend_service.find_long_weekends(sample_holidays, 2024, 2)
    assert len(feb_long_weekends) == 0
    
    # Test May 2024 (2-day bridge holiday - not a long weekend)
    may_long_weekends = long_weekend_service.find_long_weekends(sample_holidays, 2024, 5)
    assert len(may_long_weekends) == 0

def test_get_middle_days(long_weekend_service):
    """Test getting middle days of a period"""
    # 4-day period
    middle_days = long_weekend_service.get_middle_days(
        date(2024, 3, 29),
        date(2024, 4, 1)
    )
    assert middle_days == {date(2024, 3, 30), date(2024, 3, 31)}
    
    # 3-day period
    middle_days = long_weekend_service.get_middle_days(
        date(2024, 1, 1),
        date(2024, 1, 3)
    )
    assert middle_days == {date(2024, 1, 2)}
    
    # 2-day period (no middle days)
    middle_days = long_weekend_service.get_middle_days(
        date(2024, 5, 23),
        date(2024, 5, 24)
    )
    assert len(middle_days) == 0

def test_is_middle_day(long_weekend_service, sample_holidays):
    """Test checking if a date is a middle day"""
    # Middle days of Easter holiday
    assert long_weekend_service.is_middle_day(date(2024, 3, 30), sample_holidays)  # Saturday
    assert long_weekend_service.is_middle_day(date(2024, 3, 31), sample_holidays)  # Sunday
    
    # Middle day of New Year holiday
    assert long_weekend_service.is_middle_day(date(2024, 1, 2), sample_holidays)
    
    # Not middle days
    assert not long_weekend_service.is_middle_day(date(2024, 2, 6), sample_holidays)  # Regular holiday
    assert not long_weekend_service.is_middle_day(date(2024, 3, 29), sample_holidays)  # Start of holiday
    assert not long_weekend_service.is_middle_day(date(2024, 4, 1), sample_holidays)  # End of holiday
    assert not long_weekend_service.is_middle_day(date(2024, 5, 24), sample_holidays)  # Part of 2-day holiday

def test_analyze_period(long_weekend_service, sample_holidays):
    """Test analyzing a period for day types"""
    # Analyze Easter period
    day_types = long_weekend_service.analyze_period(
        date(2024, 3, 28),  # Thursday
        date(2024, 4, 2),   # Tuesday
        sample_holidays
    )
    
    assert day_types[date(2024, 3, 28)] == DayType.REGULAR      # Thursday
    assert day_types[date(2024, 3, 29)] == DayType.HOLIDAY      # Good Friday (start)
    assert day_types[date(2024, 3, 30)] == DayType.LONG_WEEKEND_MIDDLE  # Saturday
    assert day_types[date(2024, 3, 31)] == DayType.LONG_WEEKEND_MIDDLE  # Easter Sunday
    assert day_types[date(2024, 4, 1)] == DayType.HOLIDAY      # Easter Monday (end)
    assert day_types[date(2024, 4, 2)] == DayType.REGULAR      # Tuesday
    
    # Analyze May bridge holiday period
    day_types = long_weekend_service.analyze_period(
        date(2024, 5, 22),  # Wednesday
        date(2024, 5, 25),  # Saturday
        sample_holidays
    )
    
    assert day_types[date(2024, 5, 22)] == DayType.REGULAR  # Wednesday
    assert day_types[date(2024, 5, 23)] == DayType.HOLIDAY  # Thursday (start)
    assert day_types[date(2024, 5, 24)] == DayType.HOLIDAY  # Friday (end)
    assert day_types[date(2024, 5, 25)] == DayType.WEEKEND  # Saturday 