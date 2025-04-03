from pydantic import BaseModel
from typing import Dict, List, Optional

class PersonAssignment(BaseModel):
    name: str
    min_days: Optional[int] = None
    max_days: Optional[int] = None

class BulkGroupsRequest(BaseModel):
    group_ids: List[str]

class BulkPeopleAssignmentRequest(BaseModel):
    assignments: Dict[str, List[PersonAssignment]] 