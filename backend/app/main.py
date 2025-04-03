from fastapi import FastAPI, HTTPException, Path, Depends, Query, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Union
from datetime import date
import calendar
from sqlalchemy.orm import Session
import traceback
import asyncio
import logging

from .services.scheduler import SchedulerService
from .services.holiday_service import HolidayService
from .models.schemas import (
    GroupCreate,
    PersonCreate,
    BulkGroupsCreate,
    BulkPeopleAssignment,
    Schedule,
    Group
)
from .models.holiday import Holiday, HolidayBulkUpload, CSVHolidayUpload
from .config.settings import Settings, get_settings
from .utils.exceptions import (
    GroupNotFoundException,
    PersonNotFoundException,
    InsufficientGroupMembersError,
    InvalidScheduleError
)
from .utils.logging import logger
from .config.database import get_db, Base, engine
from .models.request import BulkGroupsRequest, BulkPeopleAssignmentRequest

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()
logger = logging.getLogger(__name__)

def get_scheduler(db: Session = Depends(get_db)) -> SchedulerService:
    """Get scheduler service instance with database session"""
    return SchedulerService(db)

def configure_cors(app: FastAPI, settings: Settings):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
        expose_headers=["*"]  # Expose all headers to the browser
    )

# Configure application
settings = get_settings()
configure_cors(app, settings)

# Holiday Management Endpoints

@app.post("/holidays", status_code=status.HTTP_201_CREATED)
async def create_holiday(
    holiday: Holiday,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> Dict:
    """Create a new holiday"""
    try:
        holiday_service = HolidayService(db)
        db_holiday = holiday_service.create_holiday(holiday)
        return {
            "id": db_holiday.id,
            "start_date": db_holiday.start_date,
            "end_date": db_holiday.end_date,
            "name": db_holiday.name
        }
    except Exception as e:
        logger.error(f"Error creating holiday: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating holiday: {str(e)}"
        )

@app.post("/holidays/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_holidays(
    data: HolidayBulkUpload,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> Dict:
    """Upload multiple holidays at once"""
    try:
        holiday_service = HolidayService(db)
        db_holidays = holiday_service.bulk_create_holidays(data.holidays)
        return {
            "message": f"Successfully created {len(db_holidays)} holidays",
            "created_count": len(db_holidays)
        }
    except Exception as e:
        logger.error(f"Error creating bulk holidays: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating bulk holidays: {str(e)}"
        )

@app.post("/holidays/upload/csv", status_code=status.HTTP_201_CREATED)
async def upload_holidays_csv(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> Dict:
    """Upload holidays from a CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are supported"
            )
        
        # Read the CSV content
        csv_content = await file.read()
        csv_str = csv_content.decode("utf-8")
        
        # Parse the CSV
        csv_upload = CSVHolidayUpload(csv_content=csv_str)
        holidays = csv_upload.parse_csv()
        
        if not holidays:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid holidays found in CSV"
            )
        
        # Create the holidays
        holiday_service = HolidayService(db)
        db_holidays = holiday_service.bulk_create_holidays(holidays)
        
        return {
            "message": f"Successfully created {len(db_holidays)} holidays from CSV",
            "created_count": len(db_holidays)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading CSV: {str(e)}"
        )

@app.get("/holidays")
async def get_holidays(
    year: Optional[int] = Query(None, description="Filter by year"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get holidays with optional filtering"""
    try:
        holiday_service = HolidayService(db)
        
        # Use async timeout
        try:
            async with asyncio.timeout(10):  # 10 second timeout
                if year is not None:
                    db_holidays = holiday_service.get_holidays_by_year(year)
                elif start_date is not None and end_date is not None:
                    db_holidays = holiday_service.get_holidays_by_date_range(start_date, end_date)
                else:
                    # Default to current year if no filters provided
                    current_year = date.today().year
                    db_holidays = holiday_service.get_holidays_by_year(current_year)
                
                # Convert to list immediately to avoid lazy loading issues
                return [
                    {
                        "id": holiday.id,
                        "start_date": holiday.start_date,
                        "end_date": holiday.end_date,
                        "name": holiday.name
                    }
                    for holiday in db_holidays
                ]
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timed out while retrieving holidays"
            )
    except Exception as e:
        logger.error(f"Error retrieving holidays: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving holidays: {str(e)}"
        )

@app.get("/holidays/{holiday_id}")
async def get_holiday(
    holiday_id: int,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> Dict:
    """Get a specific holiday by ID"""
    try:
        holiday_service = HolidayService(db)
        holiday = holiday_service.get_holiday(holiday_id)
        
        if holiday is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Holiday with ID {holiday_id} not found"
            )
        
        return {
            "id": holiday.id,
            "start_date": holiday.start_date,
            "end_date": holiday.end_date,
            "name": holiday.name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving holiday: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving holiday: {str(e)}"
        )

@app.put("/holidays/{holiday_id}")
async def update_holiday(
    holiday_id: int,
    holiday: Holiday,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> Dict:
    """Update an existing holiday"""
    try:
        holiday_service = HolidayService(db)
        updated_holiday = holiday_service.update_holiday(holiday_id, holiday)
        
        if updated_holiday is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Holiday with ID {holiday_id} not found"
            )
        
        return {
            "id": updated_holiday.id,
            "start_date": updated_holiday.start_date,
            "end_date": updated_holiday.end_date,
            "name": updated_holiday.name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating holiday: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating holiday: {str(e)}"
        )

@app.delete("/holidays/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db)
) -> Dict:
    """Delete a holiday"""
    try:
        holiday_service = HolidayService(db)
        success = holiday_service.delete_holiday(holiday_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Holiday with ID {holiday_id} not found"
            )
        
        return {"message": f"Holiday with ID {holiday_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting holiday: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting holiday: {str(e)}"
        )

# Original Scheduler Endpoints

@app.post("/groups/bulk", status_code=status.HTTP_201_CREATED)
def bulk_add_groups(request: BulkGroupsRequest, db: Session = Depends(get_db)):
    """Add multiple groups at once"""
    try:
        scheduler = SchedulerService(db)
        success = scheduler.bulk_add_groups(request.group_ids)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add groups")
        return {"message": "Groups created successfully"}
    except Exception as e:
        logger.error(f"Error adding groups: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding groups: {str(e)}")

@app.post("/groups/{group_id}/people")
async def add_person_to_group(
    group_id: Union[str, int],
    person: PersonCreate,
    settings: Settings = Depends(get_settings)
) -> Dict[str, str]:
    """Add a person to a group"""
    try:
        scheduler = SchedulerService(db)
        scheduler.add_person_to_group(
            person.name, 
            group_id,
            min_days=person.min_days,
            max_days=person.max_days
        )
        return {"message": f"Added {person.name} to group {group_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/groups/people/bulk", status_code=status.HTTP_201_CREATED)
def bulk_add_people_to_groups(request: BulkPeopleAssignmentRequest, db: Session = Depends(get_db)):
    """Add multiple people to groups with their constraints"""
    try:
        scheduler = SchedulerService(db)
        success = scheduler.bulk_add_people_to_groups(request.assignments)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add people to groups")
        return {"message": "People added to groups successfully"}
    except Exception as e:
        logger.error(f"Error adding people to groups: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding people to groups: {str(e)}")

@app.delete("/groups/{group_id}")
async def delete_group(
    group_id: str,
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler)
) -> Dict[str, str]:
    """Delete a group"""
    if scheduler.delete_group(group_id):
        return {"message": f"Group {group_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

@app.delete("/groups/{group_id}/people/{name}")
async def remove_person_from_group(
    group_id: str,
    name: str,
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler)
) -> Dict[str, str]:
    """Remove a person from a group"""
    if scheduler.remove_person_from_group(name, group_id):
        return {"message": f"Removed {name} from group {group_id}"}
    raise HTTPException(status_code=404, detail=f"Person {name} or group {group_id} not found")

@app.get("/groups")
def get_all_groups(db: Session = Depends(get_db)):
    """Get all groups and their members"""
    try:
        scheduler = SchedulerService(db)
        return {"groups": scheduler._groups}
    except Exception as e:
        logger.error(f"Error getting groups: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting groups: {str(e)}")

@app.post("/schedule/{year}/{month}")
async def generate_monthly_schedule(
    year: int = Path(..., description="Year to generate schedule for"),
    month: int = Path(..., description="Month to generate schedule for"),
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler),
    holiday_service: HolidayService = Depends(lambda db=Depends(get_db): HolidayService(db))
) -> Schedule:
    """Generate a schedule for the specified month"""
    try:
        # Get holidays for the month to determine day types
        holidays = holiday_service.get_holidays_by_date_range(
            date(year, month, 1),
            date(year, month, calendar.monthrange(year, month)[1])
        )
        return scheduler.generate_monthly_schedule(year, month, holidays)
    except (InvalidScheduleError, InsufficientGroupMembersError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error generating schedule")

@app.get("/schedule")
async def get_schedule(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month"),
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler)
) -> Schedule:
    """Get the current schedule with optional year/month filtering"""
    schedule = scheduler.get_schedule(year, month)
    if not schedule:
        raise HTTPException(status_code=404, detail="No schedule found for the specified criteria")
    return schedule

@app.get("/schedule/person/{name}")
async def get_person_schedule(
    name: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month"),
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler)
) -> Dict[str, List[str]]:
    """Get a person's schedule with optional year/month filtering"""
    dates = scheduler.get_person_schedule(name, year, month)
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

@app.get("/fairness/metrics/{person}")
async def get_person_fairness_metrics(
    person: str,
    group_id: str = Query(..., description="Group ID to get metrics for"),
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler)
) -> Dict:
    """Get fairness metrics for a person in a group"""
    stats = scheduler.assignment_history.get_person_stats(person, group_id)
    if not stats:
        raise HTTPException(status_code=404, detail=f"No statistics found for {person} in group {group_id}")
    return stats.model_dump()

@app.get("/fairness/metrics/group/{group_id}")
async def get_group_fairness_metrics(
    group_id: str,
    settings: Settings = Depends(get_settings),
    scheduler: SchedulerService = Depends(get_scheduler)
) -> Dict:
    """Get fairness metrics for an entire group"""
    metrics = scheduler.assignment_history.get_fairness_metrics(group_id)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for group {group_id}")
    return metrics

@app.get("/groups/{group_id}/people")
def get_group_members(group_id: str, db: Session = Depends(get_db)):
    """Get all members of a group"""
    try:
        scheduler = SchedulerService(db)
        if group_id not in scheduler._groups:
            raise HTTPException(status_code=404, detail=f"Group {group_id} not found")
        return {"members": scheduler._groups[group_id]}
    except Exception as e:
        logger.error(f"Error getting group members: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting group members: {str(e)}")

@app.get("/people/{person_name}/constraints")
def get_person_constraints(person_name: str, db: Session = Depends(get_db)):
    """Get constraints for a person"""
    try:
        scheduler = SchedulerService(db)
        if person_name not in scheduler._person_constraints:
            raise HTTPException(status_code=404, detail=f"No constraints found for {person_name}")
        return {"constraints": scheduler._person_constraints[person_name]}
    except Exception as e:
        logger.error(f"Error getting person constraints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting person constraints: {str(e)}")

@app.get("/people/constraints")
def get_all_constraints(db: Session = Depends(get_db)):
    """Get constraints for all people"""
    try:
        scheduler = SchedulerService(db)
        return {"constraints": scheduler._person_constraints}
    except Exception as e:
        logger.error(f"Error getting constraints: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting constraints: {str(e)}") 