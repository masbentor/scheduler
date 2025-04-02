from pydantic import BaseModel, Field
from typing import List, Dict, Union, Optional
from datetime import date
from pydantic import validator

class GroupCreate(BaseModel):
    """Model for creating a new group"""
    name: str = Field(..., description="Name of the group")

class PersonBase(BaseModel):
    """Base model for person data"""
    name: str = Field(..., description="Name of the person")
    min_days: Optional[int] = Field(None, ge=0, description="Minimum number of days to schedule per month")
    max_days: Optional[int] = Field(None, ge=0, description="Maximum number of days to schedule per month")

    @validator('max_days')
    def validate_max_days(cls, v, values):
        if v is not None and values.get('min_days') is not None:
            if v < values['min_days']:
                raise ValueError('max_days must be greater than or equal to min_days')
        return v

class PersonCreate(PersonBase):
    """Model for creating a new person"""
    pass

class BulkGroupsCreate(BaseModel):
    """Model for bulk creating groups"""
    group_ids: List[Union[str, int]] = Field(..., description="List of group IDs to create")

class BulkPeopleAssignment(BaseModel):
    """Model for bulk assigning people to groups"""
    assignments: Dict[str, List[PersonBase]] = Field(
        ..., 
        description="Dictionary mapping group IDs to lists of people with optional constraints"
    )

class ScheduleEntry(BaseModel):
    """Model for a single schedule entry"""
    date: date
    assignments: Dict[str, str] = Field(..., description="Group ID to person assignments")

class Schedule(BaseModel):
    """Model for the complete schedule"""
    entries: Dict[str, Dict[str, str]] = Field(..., description="Date to assignments mapping")

class Group(BaseModel):
    """Model for a group with its members"""
    id: str
    members: List[str] = Field(default_factory=list, description="List of group members") 