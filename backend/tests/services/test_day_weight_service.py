from datetime import date
import pytest
from app.services.day_weight_service import DayWeightService
from app.models.assignment_history_db import DayType
from app.models.holiday import Holiday

@pytest.fixture
def weight_service():
    return DayWeightService()

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

def test_base_weights(weight_service):
    """Test the default base weights for different day types"""
    assert weight_service.get_base_weight(DayType.REGULAR) == 1.0
    assert weight_service.get_base_weight(DayType.FRIDAY) == 1.2
    assert weight_service.get_base_weight(DayType.WEEKEND) == 1.5
    assert weight_service.get_base_weight(DayType.HOLIDAY) == 2.0
    assert weight_service.get_base_weight(DayType.LONG_WEEKEND_MIDDLE) == 2.5

def test_set_custom_weight(weight_service):
    """Test setting custom weights"""
    weight_service.set_weight(DayType.HOLIDAY, 3.0)
    assert weight_service.get_base_weight(DayType.HOLIDAY) == 3.0

def test_invalid_weight():
    """Test setting invalid weight"""
    service = DayWeightService()
    with pytest.raises(ValueError):
        service.set_weight(DayType.REGULAR, 0)
    with pytest.raises(ValueError):
        service.set_weight(DayType.REGULAR, -1)

def test_weight_calculation(weight_service, sample_holidays):
    """Test weight calculation for different scenarios"""
    # Regular day (Thursday)
    assert weight_service.calculate_weight(
        date(2024, 3, 28),
        sample_holidays
    ) == 1.0
    
    # Friday
    assert weight_service.calculate_weight(
        date(2024, 3, 22),
        sample_holidays
    ) == 1.2
    
    # Regular weekend (Sunday)
    assert weight_service.calculate_weight(
        date(2024, 3, 24),
        sample_holidays
    ) == 1.5
    
    # Regular holiday (Tuesday)
    assert weight_service.calculate_weight(
        date(2024, 2, 6),
        sample_holidays
    ) == 2.0
    
    # Holiday on weekend (Easter Sunday)
    assert weight_service.calculate_weight(
        date(2024, 3, 31),
        sample_holidays
    ) == 2.5  # Middle day of Easter holiday
    
    # Middle day of long holiday (Easter Saturday)
    assert weight_service.calculate_weight(
        date(2024, 3, 30),
        sample_holidays
    ) == 2.5
    
    # Middle day of New Year holiday
    assert weight_service.calculate_weight(
        date(2024, 1, 2),
        sample_holidays
    ) == 2.5

def test_weekend_detection(weight_service):
    """Test weekend detection"""
    # Monday through Thursday
    assert not weight_service.is_weekend(date(2024, 1, 1))  # Monday
    assert not weight_service.is_weekend(date(2024, 1, 2))  # Tuesday
    assert not weight_service.is_weekend(date(2024, 1, 3))  # Wednesday
    assert not weight_service.is_weekend(date(2024, 1, 4))  # Thursday
    assert not weight_service.is_weekend(date(2024, 1, 5))  # Friday
    
    # Weekend days
    assert weight_service.is_weekend(date(2024, 1, 6))      # Saturday
    assert weight_service.is_weekend(date(2024, 1, 7))      # Sunday

def test_friday_detection(weight_service):
    """Test Friday detection"""
    # Not Friday
    assert not weight_service.is_friday(date(2024, 1, 1))  # Monday
    assert not weight_service.is_friday(date(2024, 1, 6))  # Saturday
    
    # Friday
    assert weight_service.is_friday(date(2024, 1, 5))      # Friday

def test_day_type_detection(weight_service):
    """Test day type detection for different dates"""
    # Monday (regular day)
    assert weight_service.get_day_type(date(2024, 1, 1)) == DayType.REGULAR
    
    # Friday
    assert weight_service.get_day_type(date(2024, 1, 5)) == DayType.FRIDAY
    
    # Saturday (weekend)
    assert weight_service.get_day_type(date(2024, 1, 6)) == DayType.WEEKEND
    
    # Sunday (weekend)
    assert weight_service.get_day_type(date(2024, 1, 7)) == DayType.WEEKEND
    
    # Holiday overrides other types
    assert weight_service.get_day_type(date(2024, 1, 1), is_holiday=True) == DayType.HOLIDAY 