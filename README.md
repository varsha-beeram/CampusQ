# CampusQ

## Smart Campus Queue & Service Management System

CampusQ is a full-stack web application designed to digitize campus service queues. Students can find campus services, join queues, receive digital tokens, and track their queue status. Staff can manage queues, while administrators can monitor users and system activity.

## Features

- Student, Staff, and Admin portals
- JWT-based authentication
- Role-based access control
- Department and service browsing
- Digital queue token generation
- Live queue tracking
- Estimated waiting time
- Staff queue management
- Admin dashboard
- Queue history
- Token cancellation

## Tech Stack

- Frontend: React.js, Vite, Axios, React Router, CSS
- Backend: Python, Flask, SQLAlchemy
- Database: SQLite
- Authentication: JWT

## Project Structure

CampusQ/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── models.py
│   │   ├── extensions.py
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md

## Installation

### Backend

git clone https://github.com/varsha-beeram/CampusQ.git
cd CampusQ
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
python seed.py
python run.py

### Frontend

Open a new terminal:

cd CampusQ/frontend
npm install
npm run dev

## Demo Accounts

Student
Email: student@campusq.com
Password: Student@123

Staff
Email: staff@campusq.com
Password: Staff@123

Admin
Email: admin@campusq.com
Password: Admin@0123

## Project Objective

CampusQ aims to reduce physical waiting time and provide a convenient digital queue management system for campus services.
