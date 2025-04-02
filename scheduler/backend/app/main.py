from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Union

from .services.scheduler import SchedulerService
from .models.schemas import (
    GroupCreate,
    PersonCreate,
    BulkGroupsCreate,
    BulkPeopleAssignment,
    Schedule,
    Group
)
from .config.settings import Settings, get_settings
from .utils.exceptions import (
    GroupNotFoundException,
    PersonNotFoundException,
    InsufficientGroupMembersError,
    InvalidScheduleError
)
from .utils.logging import logger

app = FastAPI()
scheduler = SchedulerService()

def configure_cors(app: FastAPI, settings: Settings):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Configure application
settings = get_settings()
configure_cors(app, settings)

@app.post("/groups/bulk")
async def bulk_add_groups(
    data: BulkGroupsCreate,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Dict[str, bool]]:
    """Add multiple groups at once"""
    logger.info("Processing bulk group creation request")
    results = scheduler.bulk_add_groups(data.group_ids)
    return {
        "message": "Bulk group creation completed",
        "results": results
    }

@app.post("/groups/{group_id}/people")
async def add_person_to_group(
    group_id: Union[str, int],
    person: PersonCreate,
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Add a person to a group"""
    try:
        scheduler.add_person_to_group(
            person.name, 
            group_id,
            min_days=person.min_days,
            max_days=person.max_days
        )
        return {"message": f"Added {person.name} to group {group_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/groups/people/bulk")
async def bulk_add_people_to_groups(
    data: BulkPeopleAssignment,
    settings: Settings = Depends(get_settings)
) -> Dict[str, Dict[str, List[str]]]:
    """Add multiple people to multiple groups at once"""
    logger.info("Processing bulk people assignment request")
    try:
        results = scheduler.bulk_add_people_to_groups(data.assignments)
        return {
            "message": "Bulk people assignment completed",
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing bulk assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing bulk assignment")

@app.delete("/group/{group_id}/person/{name}")
async def remove_person(
    group_id: str = Path(..., description="Group ID - can be any string"),
    name: str = Path(..., description="Person name"),
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Remove a person from a group"""
    try:
        scheduler.remove_person_from_group(name, group_id)
        return {"message": f"Removed {name} from group {group_id}"}
    except (GroupNotFoundException, PersonNotFoundException) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/group/{group_id}")
async def delete_group(
    group_id: str = Path(..., description="Group ID - can be any string"),
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Delete a group"""
    try:
        scheduler.delete_group(group_id)
        return {"message": f"Deleted group {group_id}"}
    except GroupNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/groups")
async def get_groups(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Group]:
    """Get all groups and their members"""
    return scheduler.get_groups()

@app.post("/schedule/{year}/{month}")
async def generate_schedule(
    year: int,
    month: int,
    settings: Settings = Depends(get_settings)
) -> Schedule:
    """Generate a monthly schedule"""
    try:
        return scheduler.generate_monthly_schedule(year, month)
    except (InvalidScheduleError, InsufficientGroupMembersError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/schedule")
async def get_schedule(
    settings: Settings = Depends(get_settings)
) -> Schedule:
    """Get the current schedule"""
    schedule = scheduler.get_schedule()
    if not schedule:
        raise HTTPException(status_code=404, detail="No schedule has been generated yet")
    return schedule

@app.get("/schedule/person/{name}")
async def get_person_schedule(
    name: str,
    settings: Settings = Depends(get_settings)
) -> Dict[str, List[str]]:
    """Get a person's schedule"""
    dates = scheduler.get_person_schedule(name)
    if not dates:
        raise HTTPException(status_code=404, detail=f"No schedules found for {name}")
    return {"dates": dates}

@app.delete("/reset")
async def reset_data(
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Reset all data"""
    global scheduler
    scheduler = SchedulerService()
    logger.info("Reset all application data")
    return {"message": "All data has been reset"}

@app.get("/")
async def read_root(
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"} 