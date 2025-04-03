# Medical Clinic Scheduling System

A comprehensive scheduling system designed for medical clinics to manage doctor assignments across different groups with fair distribution of workload.

## Overview

This system implements a sophisticated scheduling solution that ensures equitable distribution of work assignments while accounting for:
- Regular weekdays
- Weekends
- Holidays
- Long weekends
- Personal constraints (minimum/maximum days)
- Fair distribution across groups

## Project Structure

```
clinic/
├── backend/                 # Backend service
│   ├── app/                 # Application code
│   │   ├── models/          # Data models
│   │   │   ├── schemas.py   # Pydantic models
│   │   │   ├── group.py     # Group models
│   │   │   ├── person.py    # Person models
│   │   │   ├── holiday.py   # Holiday models
│   │   │   ├── holiday_db.py # Holiday database models
│   │   │   ├── request.py   # Request models
│   │   │   ├── assignment_history.py # Assignment tracking
│   │   │   └── assignment_history_db.py # Assignment database models
│   │   ├── services/        # Business logic
│   │   │   ├── scheduler.py             # Main scheduling logic
│   │   │   ├── holiday_service.py       # Holiday management
│   │   │   ├── day_weight_service.py    # Day weight calculations
│   │   │   ├── long_weekend_service.py  # Long weekend detection
│   │   │   └── assignment_history_service.py # Assignment tracking
│   │   ├── utils/           # Utilities
│   │   │   ├── exceptions.py # Custom exceptions
│   │   │   └── logging.py    # Logging configuration
│   │   ├── config/          # Configuration
│   │   │   ├── database.py  # Database setup
│   │   │   └── settings.py  # Application settings
│   │   ├── api/             # API modules (structure prepared)
│   │   └── main.py          # FastAPI application
│   ├── tests/               # Test files
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Dependencies
│   ├── requirements-dev.txt # Development dependencies
│   └── README.md            # Backend documentation
└── README.md                # This file
```

## Features

### 1. Group Management
- ✅ Create and manage multiple doctor groups
- ✅ Bulk group creation
- ✅ Group deletion
- ✅ List all groups and their members
- ✅ Flexible group size support

### 2. Doctor Management
- ✅ Add/remove doctors to/from groups
- ✅ Bulk doctor assignment to groups
- ✅ Individual doctor constraints:
  - ✅ Minimum days per month
  - ✅ Maximum days per month
- ✅ Track doctor assignments and history

### 3. Holiday Management
- ✅ Create and manage holidays
- ✅ Bulk holiday creation
- ✅ CSV import of holidays
- ✅ Date range and year-based filtering
- ✅ Update and delete holidays
- ✅ Special handling for holidays that span multiple days

### 4. Schedule Generation
- ✅ Generate monthly schedules
- ✅ Fair distribution of assignments
- ✅ Support for multiple groups
- ✅ Constraints handling:
  - ✅ No consecutive days for same doctor
  - ✅ Respect min/max days constraints
  - ✅ Fair distribution of weekends
- ✅ Schedule retrieval by year/month
- ✅ Individual doctor schedule retrieval

### 5. Assignment Types & Weights
- ✅ Different day types with weights:
  - Regular weekdays (1.0)
  - Fridays (1.2)
  - Weekends (1.5)
  - Holidays (2.0)
  - Long weekend middle days (2.5)
- ✅ Automatic weight calculation
- ✅ Special handling for holidays on weekends
- ✅ Long weekend detection and middle day identification

### 6. Assignment History & Fairness
- ✅ Track all assignments with:
  - Person assigned
  - Group
  - Date
  - Day type
  - Weight
- ✅ Cumulative statistics:
  - Regular days
  - Weighted days
  - Total days
- ✅ Fairness metrics:
  - Per person
  - Per group
  - Overall distribution
  - Standard deviation of workload

### 7. Database Schema
The system uses SQLite with SQLAlchemy ORM and includes the following tables:
- `groups`: Store group information
- `people`: Store doctor information and constraints
- `group_members`: Track group memberships
- `assignment_history`: Track all assignments with weights
- `holidays`: Store holiday information with start/end dates

## API Endpoints

### Groups
- `POST /groups`: Create a new group
- `GET /groups`: List all groups
- `DELETE /groups/{group_id}`: Delete a group
- `GET /groups/{group_id}/people`: Get group members
- `POST /groups/bulk`: Create multiple groups

### People
- `POST /groups/{group_id}/people`: Add person to group
- `DELETE /groups/{group_id}/people/{name}`: Remove person from group
- `POST /groups/people/bulk`: Bulk assign people to groups
- `GET /people/{person_name}/constraints`: Get person's constraints
- `GET /people/constraints`: Get all people's constraints

### Holidays
- `POST /holidays`: Create a new holiday
- `POST /holidays/bulk`: Create multiple holidays at once
- `POST /holidays/upload/csv`: Upload holidays from CSV file
- `GET /holidays`: Get holidays with optional filtering
- `GET /holidays/{holiday_id}`: Get a specific holiday
- `PUT /holidays/{holiday_id}`: Update a holiday
- `DELETE /holidays/{holiday_id}`: Delete a holiday

### Schedule
- `POST /schedule/{year}/{month}`: Generate monthly schedule
- `GET /schedule`: Get schedule (with optional year/month filter)
- `GET /schedule/person/{name}`: Get person's schedule

### Fairness Metrics
- `GET /fairness/metrics/{person}`: Get person's fairness metrics
- `GET /fairness/metrics/group/{group_id}`: Get group fairness metrics

### System
- `GET /health`: Health check endpoint
- `GET /`: Root endpoint with version information
- `DELETE /reset`: Reset all data (for testing purposes)

## Getting Started

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python -m uvicorn app.main:app --reload --port 8005
   ```

5. Access the API documentation at:
   - http://localhost:8005/docs
   - http://localhost:8005/redoc

## Example Usage

### 1. Create Groups
```bash
curl -X POST "http://localhost:8005/groups/bulk" -H "Content-Type: application/json" -d '{"group_ids": ["egyes", "kettes"]}'
```

### 2. Add Doctors to Groups
```bash
curl -X POST "http://localhost:8005/groups/people/bulk" -H "Content-Type: application/json" -d '{
  "egyes": [
    {"name": "Dr. Palatka Károly"},
    {"name": "Dr. Vitális Zsuzsanna"},
    {"name": "Dr. Bubán Tamás"}
  ],
  "kettes": [
    {"name": "Dr. Jakab Áron"},
    {"name": "Dr. Juhász Lilla"},
    {"name": "Dr. Fehér Eszter"}
  ]
}'
```

### 3. Add Holidays
```bash
curl -X POST "http://localhost:8005/holidays" -H "Content-Type: application/json" -d '{
  "name": "Easter",
  "start_date": "2024-03-29",
  "end_date": "2024-04-01"
}'
```

### 4. Generate Schedule
```bash
curl -X POST "http://localhost:8005/schedule/2024/4"
```

### 5. Retrieve Schedule
```bash
curl -X GET "http://localhost:8005/schedule?year=2024&month=4"
```

## License

MIT