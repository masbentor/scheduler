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