from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

class PersonCreate(BaseModel):
    name: str
    min_days: Optional[int] = Field(default=1, ge=0)
    max_days: Optional[int] = Field(default=31, ge=1)

class GroupCreate(BaseModel):
    group_id: Union[str, int]

class BulkGroupsCreate(BaseModel):
    group_ids: List[Union[str, int]]

class BulkPeopleAssignment(BaseModel):
    assignments: Dict[Union[str, int], List[PersonCreate]]

class Person(BaseModel):
    name: str
    min_days: int = Field(default=1, ge=0)
    max_days: int = Field(default=31, ge=1)
    assigned_dates: List[str] = Field(default_factory=list)

class Group(BaseModel):
    id: Union[str, int]
    members: List[Person] = Field(default_factory=list)

class Schedule(BaseModel):
    year: int
    month: int
    assignments: Dict[str, List[str]]  # date -> list of names
    groups: Dict[Union[str, int], Group]