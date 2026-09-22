# CampusQ — Smart Campus Queue & Service Management System

A final-year level full-stack queue-management project using:

- React + Vite
- Flask REST API
- SQLAlchemy
- SQLite
- JWT authentication
- Role-based access: STUDENT, STAFF, ADMIN

## What is implemented

### Student
- Registration and login
- Department/service discovery
- One active token per service per day
- Backend-generated serial/token
- Live current-serving token
- People ahead / queue position
- Estimated wait time
- Expected turn time
- Assigned counter information
- Auto-refresh while waiting
- "Your turn is next" state
- Cancel token
- Queue history

### Staff
- Assigned service queue
- Live waiting list
- Call next
- Start service
- Complete service
- Skip token
- Student notifications
- Queue statistics

### Admin
- Dashboard metrics
- User list
- Role-aware access

## Why SQLite?

SQLite is a real relational SQL database and is appropriate for a small/medium academic deployment where a separate database server is unnecessary. It reduces infrastructure and deployment complexity while still supporting tables, relationships, transactions, constraints and SQL. SQLAlchemy keeps the persistence layer portable, so the project can later move to PostgreSQL or MySQL when higher concurrency or managed production infrastructure is required.

## Run on Windows

### Backend
```cmd
cd backend
python -m venv venv
venv\Scriptsctivate
pip install -r requirements.txt
python seed.py
python run.py
```

Backend: http://localhost:5000

### Frontend
Open another CMD:
```cmd
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Demo accounts

Student:
`student@campusq.com` / `Student@123`

Staff:
`staff@campusq.com` / `Staff@123`

Admin:
`admin@campusq.com` / `Admin@123`

Staff 2:
`staff2@campusq.com` / `Staff@123`

The seed creates a realistic live queue for the first academic service so the student demo can immediately show a current-serving token, people ahead and estimated wait.

## Important production note

SQLite is file-based. For a public deployment with persistent multi-user data, use persistent storage or migrate the SQLAlchemy database URL to a managed PostgreSQL/MySQL database. The application code is structured so the database layer can be migrated later.
