from datetime import date
import pytest
from app.services.day_weight_service import DayWeightService
from app.models.assignment_history_db import DayType

@pytest.fixture
def weight_service():
    return DayWeightService()

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

def test_weight_calculation(weight_service):
    """Test weight calculation for different scenarios"""
    # Regular day
    assert weight_service.calculate_weight(
        date(2024, 1, 1),  # Monday
        DayType.REGULAR
    ) == 1.0
    
    # Friday
    assert weight_service.calculate_weight(
        date(2024, 1, 5),  # Friday
        DayType.FRIDAY
    ) == 1.2
    
    # Weekend
    assert weight_service.calculate_weight(
        date(2024, 1, 6),  # Saturday
        DayType.WEEKEND
    ) == 1.5
    
    # Holiday
    assert weight_service.calculate_weight(
        date(2024, 1, 1),  # Monday holiday
        DayType.HOLIDAY
    ) == 2.0
    
    # Holiday on weekend (should use higher weight)
    assert weight_service.calculate_weight(
        date(2024, 1, 6),  # Saturday holiday
        DayType.HOLIDAY
    ) == 2.0
    
    # Long weekend middle day
    assert weight_service.calculate_weight(
        date(2024, 1, 1),
        DayType.REGULAR,
        is_long_weekend_middle=True
    ) == 2.5 