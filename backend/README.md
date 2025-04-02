# Scheduler Backend

A FastAPI-based backend service for managing group schedules. This is the consolidated backend service that combines functionality from both previous backends.

## Features

- Group management (create, delete, list)
- Person management (add to group, remove from group)
- Schedule generation with fair distribution
- Bulk operations support
- Comprehensive error handling
- Logging
- Configuration management
- Type safety with Pydantic models
- Database persistence with SQLAlchemy
- Holiday handling

## Project Structure

```
backend/
├── app/
│   ├── api/            # API routes
│   ├── models/         # Pydantic models
│   ├── services/       # Business logic
│   ├── utils/          # Utilities
│   ├── config/         # Configuration
│   └── main.py        # FastAPI application
├── tests/             # Test files
├── requirements.txt   # Dependencies
└── README.md         # This file
```

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:
```env
DEBUG=False
ALLOWED_ORIGINS=["http://localhost:5173"]
MIN_GROUP_MEMBERS=2
```

## Running the Application

1. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Groups
- `POST /groups/bulk` - Create multiple groups
- `POST /groups/people/bulk` - Add multiple people to groups
- `POST /group/{group_id}/person/{name}` - Add person to group
- `DELETE /group/{group_id}/person/{name}` - Remove person from group
- `DELETE /group/{group_id}` - Delete group
- `GET /groups` - List all groups

### Schedules
- `POST /schedule/{year}/{month}` - Generate monthly schedule
- `GET /schedule` - Get current schedule
- `GET /schedule/person/{name}` - Get person's schedule

### System
- `DELETE /reset` - Reset all data
- `GET /health` - Health check
- `GET /` - API information

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Server Error

Custom exceptions are defined in `app.utils.exceptions` and are mapped to appropriate HTTP responses.

## Development

### Running Tests
```bash
pytest
```

### Code Coverage
```bash
coverage run -m pytest
coverage report
```

## Design Decisions

1. **Modular Structure**: Code is organized into logical modules for better maintainability.
2. **Type Safety**: Extensive use of type hints and Pydantic models.
3. **Configuration Management**: Environment-based configuration using pydantic-settings.
4. **Error Handling**: Custom exceptions for clear error reporting.
5. **Logging**: Comprehensive logging for debugging and monitoring.
6. **Dependency Injection**: FastAPI's dependency injection for configuration and services.

## Scheduling Algorithm

The scheduling algorithm ensures:
1. One person from each group is scheduled each day
2. No person is scheduled on consecutive days
3. Fair distribution of assignments
4. Handling of edge cases (insufficient members, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Create a pull request

## License

MIT License 