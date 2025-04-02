from datetime import date
import pytest
from app.models.holiday import Holiday, HolidayBulkUpload

def test_create_single_day_holiday():
    """Test creating a single day holiday"""
    holiday = Holiday(start_date=date(2024, 1, 1))
    assert holiday.start_date == date(2024, 1, 1)
    assert holiday.end_date is None
    assert not holiday.is_multi_day()
    assert holiday.get_dates() == [date(2024, 1, 1)]

def test_create_multi_day_holiday():
    """Test creating a multi-day holiday"""
    holiday = Holiday(
        start_date=date(2024, 12, 24),
        end_date=date(2024, 12, 26)
    )
    assert holiday.start_date == date(2024, 12, 24)
    assert holiday.end_date == date(2024, 12, 26)
    assert holiday.is_multi_day()
    assert holiday.get_dates() == [
        date(2024, 12, 24),
        date(2024, 12, 25),
        date(2024, 12, 26)
    ]

def test_invalid_end_date():
    """Test validation of end_date being after start_date"""
    with pytest.raises(ValueError, match="end_date must be equal to or after start_date"):
        Holiday(
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 1)
        )

def test_same_start_end_date():
    """Test holiday with same start and end date"""
    holiday = Holiday(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 1)
    )
    assert not holiday.is_multi_day()
    assert holiday.get_dates() == [date(2024, 1, 1)]

def test_holiday_with_name():
    """Test holiday with a name"""
    holiday = Holiday(
        start_date=date(2024, 1, 1),
        name="New Year's Day"
    )
    assert holiday.name == "New Year's Day"

def test_bulk_upload_model():
    """Test the bulk upload model"""
    holidays = [
        Holiday(start_date=date(2024, 1, 1), name="New Year's Day"),
        Holiday(
            start_date=date(2024, 12, 24),
            end_date=date(2024, 12, 26),
            name="Christmas"
        )
    ]
    bulk = HolidayBulkUpload(holidays=holidays)
    assert len(bulk.holidays) == 2
    assert bulk.holidays[0].name == "New Year's Day"
    assert bulk.holidays[1].is_multi_day() 