# Scheduler Application

This repository contains a scheduling system with a FastAPI backend.

## Refactoring Summary

This codebase has been refactored to consolidate two separate backends into a single, unified backend with all features. The following changes were made:

1. Consolidated the duplicate backend implementations into a single backend
2. Retained the more advanced features from the scheduler backend:
   - Database persistence with SQLAlchemy
   - More comprehensive API functionality
   - Holiday handling
   - Assignment history tracking
3. Removed redundant code and simplified the project structure

## Project Structure

```
clinic/
├── backend/             # Consolidated backend service
│   ├── app/             # Application code
│   │   ├── models/      # Pydantic models & DB models
│   │   ├── services/    # Business logic
│   │   ├── utils/       # Utilities
│   │   ├── config/      # Configuration
│   │   └── main.py      # FastAPI application
│   ├── tests/           # Test files
│   ├── requirements.txt # Dependencies
│   └── README.md        # Backend documentation
├── README.md            # This file
└── ...
```

## Features

- Group management (create, delete, list)
- Person assignment to groups with constraints
- Schedule generation with fair distribution
- Bulk operations support
- Database persistence
- Holiday handling
- Assignment history tracking

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
   python -m uvicorn app.main:app --reload
   ```

5. Access the API documentation at:
   - http://localhost:8000/docs
   - http://localhost:8000/redoc

## API Testing

A simple test script is provided to verify API functionality:

```bash
python backend/test_api.py
```

## License

MIT

# Fair Scheduling System with Holiday Management

## Overview
This system implements a fair scheduling solution with comprehensive holiday management capabilities. It ensures equitable distribution of work assignments while accounting for holidays, weekends, and special scheduling considerations.

## Features Implemented

### 1. Holiday Management
- ✅ Single holiday creation, retrieval, update, and deletion
- ✅ Bulk holiday upload support
- ✅ CSV import functionality
- ✅ Date range and year-based filtering
- ✅ Multi-day holiday support
- ✅ Automatic validation of date ranges

### 2. Assignment Tracking
- ✅ Track assignments by person, date, and day type
- ✅ Store historical assignment data
- ✅ Calculate and maintain cumulative statistics
- ✅ Support for different day types (regular, Friday, weekend, holiday)

### 3. Weight System
- ✅ Configurable weights for different day types:
  - Regular weekdays: 1.0 (base weight)
  - Fridays: 1.2
  - Weekends: 1.5
  - Holidays: 2.0
  - Long weekend middle days: 2.5
- ✅ Automatic weight calculation based on day type
- ✅ Special handling for holidays on weekends
- ✅ Support for custom weight configuration

### 4. Database Schema
The system uses SQLite with SQLAlchemy ORM and includes the following tables:

#### Holidays Table
```sql
CREATE TABLE holidays (
    id INTEGER PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE,
    name VARCHAR
);
```

### 5. API Endpoints

#### Holiday Management

1. **Create Holiday**
   - Endpoint: `POST /holidays`
   - Input Format:
   ```json
   {
     "start_date": "2025-01-01",
     "end_date": "2025-01-02",  // Optional
     "name": "New Year's Day"    // Optional
   }
   ```

2. **Bulk Create Holidays**
   - Endpoint: `POST /holidays/bulk`
   - Input Format:
   ```json
   {
     "holidays": [
       {
         "start_date": "2025-01-01",
         "end_date": "2025-01-02",
         "name": "New Year's Day"
       },
       {
         "start_date": "2025-12-25",
         "name": "Christmas Day"
       }
     ]
   }
   ```

3. **CSV Upload**
   - Endpoint: `POST /holidays/upload/csv`
   - Expected CSV Format:
   ```csv
   start_date,end_date,name
   2025-01-01,2025-01-02,New Year's Holiday
   2025-12-25,,Christmas Day
   ```
   - Notes:
     - Dates can be in formats: YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, DD/MM/YYYY
     - `end_date` is optional
     - `name` is optional

4. **Get Holidays**
   - Endpoint: `GET /holidays`
   - Query Parameters:
     - `year`: Filter by year (e.g., `2025`)
     - `start_date`: Filter by start date (YYYY-MM-DD)
     - `end_date`: Filter by end date (YYYY-MM-DD)
   - Response Format:
   ```json
   [
     {
       "id": 1,
       "start_date": "2025-01-01",
       "end_date": "2025-01-02",
       "name": "New Year's Day"
     }
   ]
   ```

5. **Get Single Holiday**
   - Endpoint: `GET /holidays/{holiday_id}`
   - Response Format: Same as above

6. **Update Holiday**
   - Endpoint: `PUT /holidays/{holiday_id}`
   - Input Format: Same as Create Holiday

7. **Delete Holiday**
   - Endpoint: `DELETE /holidays/{holiday_id}`
   - Response:
   ```json
   {
     "message": "Holiday with ID {holiday_id} deleted successfully"
   }
   ```

## Validation Rules

1. **Date Validation**
   - `end_date` must be equal to or after `start_date`
   - Dates must be valid calendar dates
   - Future dates are allowed

2. **CSV Upload Validation**
   - Must be a valid CSV file
   - Must contain at least `start_date` column
   - Invalid rows are skipped during import

## Error Handling

The API returns appropriate HTTP status codes:
- `201`: Resource created successfully
- `200`: Request successful
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Server error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Development Setup

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Running the Server**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Running Tests**
   ```bash
   cd backend
   python -m pytest tests/
   ```

## Next Steps

Upcoming features:
- [ ] Fairness tracking system
- [ ] Assignment history tracking
- [ ] Weighted day type handling
- [ ] Long weekend detection
- [ ] Advanced scheduling algorithm

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.