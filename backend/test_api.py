#!/usr/bin/env python3
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_root():
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_add_groups():
    print("Testing add groups endpoint...")
    payload = {"group_ids": ["test_group1", "test_group2"]}
    response = requests.post(f"{BASE_URL}/groups/bulk", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_add_person():
    print("Testing add person to group endpoint...")
    payload = {"name": "John Doe", "min_days": 1, "max_days": 5}
    response = requests.post(f"{BASE_URL}/groups/test_group1/people", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_get_groups():
    print("Testing get groups endpoint...")
    response = requests.get(f"{BASE_URL}/groups")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def test_generate_schedule():
    print("Testing generate schedule endpoint...")
    import datetime
    today = datetime.datetime.today()
    response = requests.post(f"{BASE_URL}/schedule/{today.year}/{today.month}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    print()

def run_all_tests():
    test_health()
    test_root()
    test_add_groups()
    test_add_person()
    test_get_groups()
    test_generate_schedule()

if __name__ == "__main__":
    run_all_tests() 