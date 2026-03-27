# ToolShare - Community Tool Lending Library

A full-stack web application for community tool lending. People can borrow tools (drills, ladders, garden gear) for short-term use with tracking of tool status, loan periods, due dates, and borrower limits.

## Architecture

- **Frontend:** React 19 + Vite + Tailwind CSS v4
- **Backend:** AWS Lambda (Python) with API Gateway
- **Database:** DynamoDB (single-table design)
- **Storage:** S3 for files
- **Notifications:** SNS for email alerts
- **Auth:** PBKDF2 password hashing + JWT tokens
- **Region:** eu-west-1

## AWS Services (6)

1. **Lambda** - Serverless API handler
2. **DynamoDB** - NoSQL database (toolshare-prod)
3. **API Gateway** - REST API endpoint (toolshare-api)
4. **S3** - File storage (toolshare-files-prod-vishvak) + Frontend hosting (toolshare-frontend-prod-vishvak)
5. **SNS** - Email notifications (toolshare-notifications)
6. **IAM** - Role-based access (toolshare-lambda-role)

## Project Structure

```
├── library/                  # Python library (toollibrary-nci)
│   ├── toollibrary/
│   │   ├── __init__.py
│   │   ├── loan.py          # LoanManager - due dates, fees, limits
│   │   ├── tool.py          # ToolManager - validation, status flow
│   │   ├── formatter.py     # LendingFormatter - reports, CSV
│   │   └── validator.py     # InputValidator - sanitization
│   ├── tests/
│   │   └── test_toollibrary.py  # 30+ unit tests
│   └── setup.py
├── backend/
│   ├── lambda_function.py   # Single Lambda handler (all routes)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── context/auth.jsx
│   │   ├── components/      # Navbar, ProtectedRoute
│   │   ├── pages/           # Dashboard, Tools, ToolDetail, Loans
│   │   ├── api.js
│   │   └── App.jsx
│   └── package.json
└── .github/workflows/deploy.yml  # CI/CD pipeline
```

## Features

- User registration and login with JWT authentication
- Add, edit, delete tools with categories and conditions
- Borrow tools with configurable loan periods (max 3 active loans)
- Return tools with automatic late fee calculation ($2/day)
- Dashboard with real-time stats (available, loaned, overdue)
- Tool search and category filtering
- SNS email notifications for borrowing events
- Overdue loan tracking and alerts

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Register new user |
| POST | /auth/login | Login |
| GET | /tools | List all tools |
| POST | /tools | Create tool |
| GET | /tools/{id} | Get tool details |
| PUT | /tools/{id} | Update tool |
| DELETE | /tools/{id} | Delete tool |
| POST | /tools/{id}/borrow | Borrow a tool |
| POST | /tools/{id}/return | Return a tool |
| GET | /loans | List user's loans |
| GET | /loans/overdue | List overdue loans |
| GET | /dashboard | Dashboard stats |
| POST | /subscribe | Subscribe to notifications |
| GET | /subscribers | List subscribers |

## Getting Started

### Backend
```bash
cd backend
# Deploy via GitHub Actions or manually with AWS CLI
```

### Frontend
```bash
cd frontend
npm install
echo "VITE_API_URL=https://your-api-id.execute-api.eu-west-1.amazonaws.com/prod" > .env
npm run dev
```

### Library
```bash
cd library
pip install -e .
python -m pytest tests/ -v
```

## GitHub Actions Secrets

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Author

Vishvaksen - NCI Cloud Programming Project
