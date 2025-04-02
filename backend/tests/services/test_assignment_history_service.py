import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base
from app.models.assignment_history import AssignmentHistory, AssignmentStats
from app.models.assignment_history_db import AssignmentHistoryDB, DayType
from app.services.assignment_history_service import AssignmentHistoryService

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
def history_service(db_session):
    return AssignmentHistoryService(db_session)

def test_record_assignment(history_service):
    """Test recording a single assignment"""
    assignment = AssignmentHistory(
        person="John",
        group_id="group1",
        assignment_date=date(2024, 1, 1),
        day_type=DayType.REGULAR,
        weight=1.0
    )
    
    result = history_service.record_assignment(assignment)
    assert result.person == "John"
    assert result.group_id == "group1"
    assert result.day_type == DayType.REGULAR
    assert result.weight == 1.0
    assert result.cumulative_regular_days == 1
    assert result.cumulative_weighted_days == 1.0
    assert result.cumulative_total_days == 1

def test_record_multiple_assignments(history_service):
    """Test recording multiple assignments for the same person"""
    assignments = [
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 1),
            day_type=DayType.REGULAR,
            weight=1.0
        ),
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 2),
            day_type=DayType.HOLIDAY,
            weight=2.0
        )
    ]
    
    for assignment in assignments:
        result = history_service.record_assignment(assignment)
    
    assert result.cumulative_regular_days == 1  # Only one regular day
    assert result.cumulative_weighted_days == 3.0  # Total weights: 1.0 + 2.0
    assert result.cumulative_total_days == 2  # Two total days

def test_get_person_stats(history_service):
    """Test getting statistics for a person"""
    # Create some assignments
    assignments = [
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 1),
            day_type=DayType.REGULAR,
            weight=1.0
        ),
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 6),
            day_type=DayType.WEEKEND,
            weight=1.5
        ),
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 7),
            day_type=DayType.HOLIDAY,
            weight=2.0
        )
    ]
    
    for assignment in assignments:
        history_service.record_assignment(assignment)
    
    stats = history_service.get_person_stats("John", "group1")
    assert stats.regular_days == 1
    assert stats.weekend_days == 1
    assert stats.holiday_days == 1
    assert stats.total_assignments == 3
    assert stats.total_weighted_score == 4.5

def test_get_group_stats(history_service):
    """Test getting statistics for an entire group"""
    # Create assignments for multiple people
    assignments = [
        # John's assignments
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 1),
            day_type=DayType.REGULAR,
            weight=1.0
        ),
        # Jane's assignments
        AssignmentHistory(
            person="Jane",
            group_id="group1",
            assignment_date=date(2024, 1, 2),
            day_type=DayType.REGULAR,
            weight=1.0
        )
    ]
    
    for assignment in assignments:
        history_service.record_assignment(assignment)
    
    stats = history_service.get_group_stats("group1")
    assert len(stats) == 2
    assert stats["John"].regular_days == 1
    assert stats["Jane"].regular_days == 1
    assert stats["John"].total_assignments == 1
    assert stats["Jane"].total_assignments == 1

def test_get_fairness_metrics(history_service):
    """Test calculating fairness metrics for a group"""
    # Create assignments with uneven distribution
    assignments = [
        # John has more weighted assignments
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 1),
            day_type=DayType.HOLIDAY,
            weight=2.0
        ),
        AssignmentHistory(
            person="John",
            group_id="group1",
            assignment_date=date(2024, 1, 2),
            day_type=DayType.WEEKEND,
            weight=1.5
        ),
        # Jane has fewer weighted assignments
        AssignmentHistory(
            person="Jane",
            group_id="group1",
            assignment_date=date(2024, 1, 3),
            day_type=DayType.REGULAR,
            weight=1.0
        )
    ]
    
    for assignment in assignments:
        history_service.record_assignment(assignment)
    
    metrics = history_service.get_fairness_metrics("group1")
    assert metrics["weighted_std_dev"] > 0  # Should have some deviation
    assert metrics["max_weighted_diff"] == 2.5  # Difference between 3.5 and 1.0
    assert metrics["max_total_diff"] == 1  # Difference between 2 and 1 assignments 