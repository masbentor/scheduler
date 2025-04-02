from fastapi import FastAPI, HTTPException, Path, Depends, Query, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Union
from datetime import date
from sqlalchemy.orm import Session
import traceback

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

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

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
        
        if year is not None:
            db_holidays = holiday_service.get_holidays_by_year(year)
        elif start_date is not None and end_date is not None:
            db_holidays = holiday_service.get_holidays_by_date_range(start_date, end_date)
        else:
            # Default to current year if no filters provided
            current_year = date.today().year
            db_holidays = holiday_service.get_holidays_by_year(current_year)
        
        return [
            {
                "id": holiday.id,
                "start_date": holiday.start_date,
                "end_date": holiday.end_date,
                "name": holiday.name
            }
            for holiday in db_holidays
        ]
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