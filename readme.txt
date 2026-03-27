Community Tool Lending Library
==============================
Student: Vishvaksen Machana
Student ID: 25173421
Email: x25173421@student.ncirl.ie
Module: Cloud Platform Programming
Institution: National College of Ireland

Project Overview
----------------
A cloud-native web application enabling community members to share tools through
a managed lending system. Integrates 7 AWS services with local mock modes.

AWS Services (7)
----------------
1. DynamoDB - NoSQL database for tools, users, lending records
2. S3 - Object storage for tool images/photos
3. Lambda - Serverless functions (validation, notifications, reports)
4. API Gateway - REST API endpoint management
5. Cognito - User authentication and authorization
6. Step Functions - Lending workflow orchestration
7. CloudWatch - Monitoring, logging, and overdue scheduling

Custom Library: lendlib
-----------------------
OOP Python library with classes: Tool, User, LendingRecord, InventoryManager,
LendingManager, AvailabilityChecker, OverdueDetector, BorrowerHistory

Project Structure
-----------------
Vishvaksen/
  backend/       - Flask REST API backend
  frontend/      - React single-page application
  lendlib/       - Custom OOP Python library
  report/        - IEEE LaTeX report and architecture diagrams
  venv/          - Python virtual environment

Setup Instructions
------------------
1. Create and activate virtual environment:
   python3 -m venv venv
   source venv/bin/activate

2. Install Python dependencies:
   pip install -r backend/requirements.txt
   pip install -e lendlib/

3. Run backend tests:
   cd backend && python -m pytest tests/ -v

4. Run library tests:
   cd lendlib && python -m pytest tests/ -v

5. Start Flask backend:
   cd backend && python app.py

6. Install frontend dependencies:
   cd frontend && npm install

7. Build frontend:
   cd frontend && npm run build

8. Generate diagrams:
   cd report && python architecture.py

9. Compile LaTeX report:
   cd report && pdflatex main.tex && pdflatex main.tex
