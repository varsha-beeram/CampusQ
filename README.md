# CampusQ

## Smart Campus Queue & Service Management System

CampusQ is a full-stack web application designed to digitize campus service queues. Students can discover campus services, join digital queues, receive tokens, and track their queue status in real time. Staff can manage queues, while administrators can monitor users and system activity.

## Features

- Student, Staff, and Admin portals
- JWT-based authentication
- Role-based access control
- Department and service management
- Digital queue token generation
- Live queue tracking
- Estimated waiting time
- Staff queue management
- Admin dashboard
- Queue history
- Token cancellation

## Tech Stack

- **Frontend:** React.js, Vite, Axios, React Router, CSS
- **Backend:** Python, Flask, SQLAlchemy
- **Database:** SQLite
- **Authentication:** JWT

## Project Structure

```text
CampusQ/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── extensions.py
│   │   ├── models.py
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── style.css
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md


## Objective

To develop a digital campus queue management system that reduces physical waiting time, simplifies access to campus services, and enables students and staff to efficiently manage queues through a centralized platform.
