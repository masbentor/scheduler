#!/bin/bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload 2>&1 | tee server_logs.txt 