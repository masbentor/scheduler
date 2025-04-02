from datetime import date
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
import csv
from io import StringIO

class Holiday(BaseModel):
    """Model for storing holiday information"""
    start_date: date = Field(..., description="Start date of the holiday")
    end_date: Optional[date] = Field(None, description="End date for multi-day holidays")
    name: Optional[str] = Field(None, description="Optional name of the holiday")
    
    model_config = ConfigDict(from_attributes=True)

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

class CSVHolidayUpload(BaseModel):
    """Model for uploading holidays via CSV"""
    csv_content: str = Field(..., description="CSV content with holiday data")
    
    def parse_csv(self) -> List[Holiday]:
        """Parse CSV content into Holiday objects"""
        holidays = []
        csv_reader = csv.DictReader(StringIO(self.csv_content))
        
        for row in csv_reader:
            try:
                holiday_data = self._parse_row(row)
                holiday = Holiday(**holiday_data)
                holidays.append(holiday)
            except Exception as e:
                # Skip invalid rows but could also raise error
                continue
                
        return holidays
    
    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parse a CSV row into holiday data"""
        # Parse date fields
        start_date = self._parse_date(row.get('start_date'))
        
        # Parse end_date if present
        end_date = None
        if 'end_date' in row and row['end_date']:
            end_date = self._parse_date(row.get('end_date'))
            
        return {
            "start_date": start_date,
            "end_date": end_date,
            "name": row.get('name')
        }
    
    def _parse_date(self, date_str: str) -> date:
        """Parse a date string in multiple formats"""
        # Try different date formats
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']
        
        for fmt in formats:
            try:
                return date.fromisoformat(date_str)
            except ValueError:
                try:
                    from datetime import datetime
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
                    
        # If we get here, none of the formats worked
        raise ValueError(f"Could not parse date: {date_str}") 