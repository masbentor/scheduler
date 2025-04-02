from datetime import date
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class Holiday(BaseModel):
    """Model for storing holiday information"""
    start_date: date = Field(..., description="Start date of the holiday")
    end_date: Optional[date] = Field(None, description="End date for multi-day holidays")
    name: Optional[str] = Field(None, description="Optional name of the holiday")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        if v is not None:
            start_date = info.data.get('start_date')
            if start_date and v < start_date:
                raise ValueError('end_date must be equal to or after start_date')
        return v

    def is_multi_day(self) -> bool:
        """Check if this is a multi-day holiday"""
        return self.end_date is not None and self.end_date != self.start_date

    def get_dates(self) -> List[date]:
        """Get all dates covered by this holiday"""
        if not self.end_date or self.end_date == self.start_date:
            return [self.start_date]
        
        dates = []
        current = self.start_date
        while current <= self.end_date:
            dates.append(current)
            # Create new date object for next day
            current = date.fromordinal(current.toordinal() + 1)
        return dates

class HolidayBulkUpload(BaseModel):
    """Model for bulk uploading holidays"""
    holidays: List[Holiday] = Field(..., description="List of holidays to upload") 