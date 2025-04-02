# Scheduler Backend

This is the backend service for the Scheduler application, built with FastAPI.

## Features

- Group management
- Person assignment to groups
- Schedule generation
- RESTful API

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file with the following content:
```env
APP_NAME=Scheduler
VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Groups
- POST /groups/bulk - Add multiple groups
- POST /groups/{group_id}/people - Add person to group
- POST /groups/people/bulk - Bulk add people to groups
- DELETE /group/{group_id}/person/{name} - Remove person from group
- DELETE /group/{group_id} - Delete group
- GET /groups - Get all groups

### Schedule
- POST /schedule/{year}/{month} - Generate monthly schedule
- GET /schedule - Get current schedule
- GET /schedule/person/{name} - Get person's schedule

### System
- DELETE /reset - Reset all data
- GET / - Root endpoint
- GET /health - Health check

## Development

### Project Structure
```
app/
├── config/
│   └── settings.py
├── models/
│   └── schemas.py
├── services/
│   └── scheduler.py
├── utils/
│   ├── exceptions.py
│   └── logging.py
└── main.py
```

### Testing

Run tests using pytest:
```bash
pytest
```

## Error Handling

The application includes custom exceptions:
- GroupNotFoundException
- PersonNotFoundException
- InsufficientGroupMembersError
- InvalidScheduleError