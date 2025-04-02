#!/usr/bin/env python3
"""
Test script for holiday API endpoints
"""
import json
import csv
import requests
from datetime import date, timedelta
import tempfile
import os
import time

# Give the server a moment to start if needed
time.sleep(1)

BASE_URL = "http://localhost:8000"

def test_create_holiday():
    """Test creating a single holiday"""
    print("Testing create holiday...")
    
    # Create a holiday for tomorrow
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    try:
        response = requests.post(
            f"{BASE_URL}/holidays",
            json={
                "start_date": tomorrow,
                "name": "Test Holiday"
            }
        )
        
        print(f"Response: {response.status_code}")
        if response.status_code >= 400:
            print(f"Error: {response.text}")
            
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert "id" in data, "Missing ID in response"
        assert data["name"] == "Test Holiday", f"Wrong name: {data['name']}"
        
        holiday_id = data["id"]
        print(f"Created holiday with ID: {holiday_id}")
        return holiday_id
    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise

def test_get_holiday(holiday_id):
    """Test retrieving a specific holiday"""
    print(f"Testing get holiday with ID {holiday_id}...")
    
    response = requests.get(f"{BASE_URL}/holidays/{holiday_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["id"] == holiday_id, f"Wrong ID: {data['id']}"
    
    print(f"Successfully retrieved holiday: {data['name']}")
    return data

def test_update_holiday(holiday_id):
    """Test updating a holiday"""
    print(f"Testing update holiday with ID {holiday_id}...")
    
    # Update to a two-day holiday
    start_date = (date.today() + timedelta(days=1)).isoformat()
    end_date = (date.today() + timedelta(days=2)).isoformat()
    
    response = requests.put(
        f"{BASE_URL}/holidays/{holiday_id}",
        json={
            "start_date": start_date,
            "end_date": end_date,
            "name": "Updated Test Holiday"
        }
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["name"] == "Updated Test Holiday", f"Wrong name: {data['name']}"
    assert data["end_date"] is not None, "End date should be set"
    
    print(f"Successfully updated holiday to: {data['name']}")
    return data

def test_bulk_create_holidays():
    """Test creating multiple holidays at once"""
    print("Testing bulk create holidays...")
    
    # Create 3 holidays
    today = date.today()
    holidays = [
        {
            "start_date": (today + timedelta(days=10)).isoformat(),
            "name": "Bulk Holiday 1"
        },
        {
            "start_date": (today + timedelta(days=15)).isoformat(),
            "end_date": (today + timedelta(days=16)).isoformat(),
            "name": "Bulk Holiday 2"
        },
        {
            "start_date": (today + timedelta(days=20)).isoformat(),
            "name": "Bulk Holiday 3"
        }
    ]
    
    response = requests.post(
        f"{BASE_URL}/holidays/bulk",
        json={"holidays": holidays}
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data["created_count"] == 3, f"Expected 3 holidays, got {data['created_count']}"
    
    print(f"Successfully created {data['created_count']} holidays")

def test_csv_upload():
    """Test uploading holidays via CSV"""
    print("Testing CSV upload...")
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['start_date', 'end_date', 'name'])  # Header
        
        # Add some holidays
        today = date.today()
        writer.writerow([(today + timedelta(days=30)).isoformat(), '', 'CSV Holiday 1'])
        writer.writerow([(today + timedelta(days=35)).isoformat(), (today + timedelta(days=36)).isoformat(), 'CSV Holiday 2'])
        writer.writerow([(today + timedelta(days=40)).isoformat(), '', 'CSV Holiday 3'])
        
        file_path = csvfile.name
    
    try:
        # Upload the CSV file
        with open(file_path, 'rb') as file:
            response = requests.post(
                f"{BASE_URL}/holidays/upload/csv",
                files={"file": ("holidays.csv", file, "text/csv")}
            )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()
        assert data["created_count"] == 3, f"Expected 3 holidays, got {data['created_count']}"
        
        print(f"Successfully created {data['created_count']} holidays from CSV")
    finally:
        # Clean up
        os.unlink(file_path)

def test_get_holidays():
    """Test retrieving holidays with filters"""
    print("Testing get holidays...")
    
    # Get this year's holidays
    current_year = date.today().year
    response = requests.get(f"{BASE_URL}/holidays?year={current_year}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    holidays = response.json()
    assert isinstance(holidays, list), "Expected a list of holidays"
    
    print(f"Successfully retrieved {len(holidays)} holidays for {current_year}")
    return holidays

def test_delete_holiday(holiday_id):
    """Test deleting a holiday"""
    print(f"Testing delete holiday with ID {holiday_id}...")
    
    response = requests.delete(f"{BASE_URL}/holidays/{holiday_id}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "message" in data, "Missing confirmation message"
    
    print(f"Successfully deleted holiday: {data['message']}")
    
    # Verify it's gone
    response = requests.get(f"{BASE_URL}/holidays/{holiday_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

def main():
    """Run all holiday API tests"""
    print("=== Holiday API Tests ===")
    
    # First check if the API is available
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"API not available. Status code: {response.status_code}")
            return
    except Exception as e:
        print(f"API not available: {str(e)}")
        return
    
    print("API is available. Running tests...")
    
    # Create and manipulate a single holiday
    holiday_id = test_create_holiday()
    if not holiday_id:
        print("Failed to create holiday. Stopping tests.")
        return
        
    test_get_holiday(holiday_id)
    test_update_holiday(holiday_id)
    
    # Test bulk operations
    test_bulk_create_holidays()
    test_csv_upload()
    
    # List holidays and verify
    holidays = test_get_holidays()
    print(f"Found {len(holidays)} holidays in total")
    
    # Clean up
    test_delete_holiday(holiday_id)
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main() 