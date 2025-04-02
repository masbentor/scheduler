from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import extract
from ..models.holiday import Holiday
from ..models.holiday_db import HolidayDB

class HolidayService:
    """Service for managing holidays in the database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_holiday(self, holiday: Holiday) -> HolidayDB:
        """Create a new holiday in the database"""
        db_holiday = HolidayDB(
            start_date=holiday.start_date,
            end_date=holiday.end_date,
            name=holiday.name
        )
        self.db.add(db_holiday)
        self.db.commit()
        self.db.refresh(db_holiday)
        return db_holiday
    
    def bulk_create_holidays(self, holidays: List[Holiday]) -> List[HolidayDB]:
        """Create multiple holidays in the database"""
        db_holidays = [
            HolidayDB(
                start_date=holiday.start_date,
                end_date=holiday.end_date,
                name=holiday.name
            )
            for holiday in holidays
        ]
        self.db.add_all(db_holidays)
        self.db.commit()
        for holiday in db_holidays:
            self.db.refresh(holiday)
        return db_holidays
    
    def get_holiday(self, holiday_id: int) -> Optional[HolidayDB]:
        """Get a holiday by its ID"""
        return self.db.query(HolidayDB).filter(HolidayDB.id == holiday_id).first()
    
    def get_holidays_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[HolidayDB]:
        """Get all holidays that fall within the given date range"""
        return self.db.query(HolidayDB).filter(
            HolidayDB.start_date >= start_date,
            HolidayDB.start_date <= end_date
        ).all()
    
    def get_holidays_by_year(self, year: int) -> List[HolidayDB]:
        """Get all holidays in a specific year"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        return self.get_holidays_by_date_range(start_date, end_date)
    
    def update_holiday(self, holiday_id: int, holiday: Holiday) -> Optional[HolidayDB]:
        """Update an existing holiday"""
        db_holiday = self.get_holiday(holiday_id)
        if db_holiday is None:
            return None
            
        db_holiday.start_date = holiday.start_date
        db_holiday.end_date = holiday.end_date
        db_holiday.name = holiday.name
        
        self.db.commit()
        self.db.refresh(db_holiday)
        return db_holiday
    
    def delete_holiday(self, holiday_id: int) -> bool:
        """Delete a holiday by its ID"""
        db_holiday = self.get_holiday(holiday_id)
        if db_holiday is None:
            return False
            
        self.db.delete(db_holiday)
        self.db.commit()
        return True 