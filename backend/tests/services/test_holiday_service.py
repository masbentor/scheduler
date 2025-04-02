import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base
from app.models.holiday import Holiday
from app.models.holiday_db import HolidayDB
from app.services.holiday_service import HolidayService

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def holiday_service(db_session):
    return HolidayService(db_session)

def test_create_holiday(holiday_service):
    """Test creating a single holiday"""
    holiday = Holiday(
        start_date=date(2024, 1, 1),
        name="New Year's Day"
    )
    db_holiday = holiday_service.create_holiday(holiday)
    assert db_holiday.start_date == date(2024, 1, 1)
    assert db_holiday.name == "New Year's Day"
    assert db_holiday.end_date is None

def test_create_multi_day_holiday(holiday_service):
    """Test creating a multi-day holiday"""
    holiday = Holiday(
        start_date=date(2024, 12, 24),
        end_date=date(2024, 12, 26),
        name="Christmas"
    )
    db_holiday = holiday_service.create_holiday(holiday)
    assert db_holiday.start_date == date(2024, 12, 24)
    assert db_holiday.end_date == date(2024, 12, 26)
    assert db_holiday.name == "Christmas"

def test_bulk_create_holidays(holiday_service):
    """Test creating multiple holidays at once"""
    holidays = [
        Holiday(start_date=date(2024, 1, 1), name="New Year's Day"),
        Holiday(
            start_date=date(2024, 12, 24),
            end_date=date(2024, 12, 26),
            name="Christmas"
        )
    ]
    db_holidays = holiday_service.bulk_create_holidays(holidays)
    assert len(db_holidays) == 2
    assert db_holidays[0].name == "New Year's Day"
    assert db_holidays[1].name == "Christmas"

def test_get_holiday(holiday_service):
    """Test retrieving a holiday by ID"""
    holiday = Holiday(start_date=date(2024, 1, 1), name="New Year's Day")
    db_holiday = holiday_service.create_holiday(holiday)
    
    retrieved = holiday_service.get_holiday(db_holiday.id)
    assert retrieved is not None
    assert retrieved.start_date == date(2024, 1, 1)
    assert retrieved.name == "New Year's Day"

def test_get_holidays_by_date_range(holiday_service):
    """Test retrieving holidays within a date range"""
    holidays = [
        Holiday(start_date=date(2024, 1, 1), name="New Year's Day"),
        Holiday(start_date=date(2024, 3, 15), name="National Holiday"),
        Holiday(start_date=date(2024, 12, 24), end_date=date(2024, 12, 26), name="Christmas")
    ]
    holiday_service.bulk_create_holidays(holidays)
    
    results = holiday_service.get_holidays_by_date_range(
        date(2024, 3, 1),
        date(2024, 12, 1)
    )
    assert len(results) == 1
    assert results[0].name == "National Holiday"

def test_get_holidays_by_year(holiday_service):
    """Test retrieving all holidays in a year"""
    holidays = [
        Holiday(start_date=date(2024, 1, 1), name="New Year's Day 2024"),
        Holiday(start_date=date(2025, 1, 1), name="New Year's Day 2025")
    ]
    holiday_service.bulk_create_holidays(holidays)
    
    results = holiday_service.get_holidays_by_year(2024)
    assert len(results) == 1
    assert results[0].name == "New Year's Day 2024"

def test_update_holiday(holiday_service):
    """Test updating a holiday"""
    holiday = Holiday(start_date=date(2024, 1, 1), name="New Year's Day")
    db_holiday = holiday_service.create_holiday(holiday)
    
    updated = Holiday(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2),
        name="Extended New Year"
    )
    result = holiday_service.update_holiday(db_holiday.id, updated)
    
    assert result is not None
    assert result.name == "Extended New Year"
    assert result.end_date == date(2024, 1, 2)

def test_delete_holiday(holiday_service):
    """Test deleting a holiday"""
    holiday = Holiday(start_date=date(2024, 1, 1), name="New Year's Day")
    db_holiday = holiday_service.create_holiday(holiday)
    
    assert holiday_service.delete_holiday(db_holiday.id) is True
    assert holiday_service.get_holiday(db_holiday.id) is None 