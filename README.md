# LibraryHub — Library Management System

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask 3.x" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Status-Ready%20to%20Run-28A745?style=for-the-badge" alt="Ready to run" />
</div>

A responsive library management web application designed for college or institutional use. This project helps manage books, students, borrowing records, fines, and reports using a simple Flask + SQLite architecture.

It includes both admin and student capabilities, making it useful for a real-world library workflow without requiring a heavy database setup.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
  - [Ubuntu / Debian](#ubuntu--debian)
  - [macOS](#macos)
  - [Windows](#windows)
- [How to Run the Project](#how-to-run-the-project)
- [Demo Login Credentials](#demo-login-credentials)
- [How to Use the System](#how-to-use-the-system)
  - [For Admin](#for-admin)
  - [For Students](#for-students)
- [Environment Variables](#environment-variables)
- [Useful Commands](#useful-commands)
- [Database and App Behavior](#database-and-app-behavior)
- [Troubleshooting](#troubleshooting)
- [Project Notes](#project-notes)

## Overview

LibraryHub is a compact library management system built using:

- Python
- Flask
- SQLite
- HTML, CSS, and JavaScript
- Jinja2 templates

The system supports:

- Public book catalog browsing
- Student registration and login
- Admin dashboard
- Book management
- Loan issuance and return
- Fine calculation
- Reports export
- Search and filtering

This is ideal for academic projects, mini-capstone work, and practical library automation demos.

## Features

- Secure login for admin and students
- Admin dashboard with key library statistics
- Searchable and filterable book catalog
- Add, edit, and delete book records
- Duplicate ISBN protection
- Loan issuance with active loan limits
- Due dates and overdue fine calculation
- Return operation with inventory restoration
- Partial fine payment support
- Downloadable CSV loan report
- SQLite database auto-initialization
- Starter sample books added automatically

## Technology Stack

- Backend: Python 3.12+
- Framework: Flask 3.x
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Templating: Jinja2
- Security: Werkzeug password hashing

## Project Structure

```text
IBM-7th-sem-project/
├── app.py                     # Main Flask application and business logic
├── requirements.txt          # Project dependencies
├── libraryhub.db             # SQLite database generated on first run
├── static/
│   ├── app.js                # UI and form interaction logic
│   └── style.css            # Styling and responsive UI layout
├── templates/
│   ├── base.html            # Shared layout and navigation
│   ├── index.html           # Public catalog page
│   ├── login.html           # Login page
│   ├── register.html        # Student registration page
│   ├── admin_dashboard.html # Admin overview dashboard
│   ├── manage_books.html    # Book listing and controls
│   ├── book_form.html       # Add/edit book form
│   ├── students.html        # Student management page
│   ├── issue.html           # Book issue form
│   ├── loans.html           # Loan and return management
│   ├── student_dashboard.html# Student-specific borrowing data
│   ├── reports.html         # Summary and report page
│   └── error.html           # 403 / 404 page
├── README.md                # Project documentation
└── .gitignore               # Git ignore rules
```

## Prerequisites

Before running the project, make sure your system has:

- Python 3.12 or newer
- pip package manager
- A terminal / command prompt
- Internet access to install dependencies

SQLite is included with Python by default, so no separate installation is usually needed.

## Installation Guide

### Ubuntu / Debian

Open a terminal and run:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
cd /path/to/IBM-7th-sem-project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS

```bash
cd /path/to/IBM-7th-sem-project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows

Open PowerShell in the project folder:

```powershell
cd C:\path\to\IBM-7th-sem-project
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again and continue.

## How to Run the Project

After installation, start the app with:

```bash
python app.py
```

Then open the browser and visit:

```text
http://127.0.0.1:5000
```

If you want to change the port:

```bash
PORT=5001 python app.py
```

On Windows PowerShell:

```powershell
$env:PORT = 5001
python app.py
```

## Demo Login Credentials

The project creates a default administrator automatically on first run:

- Email: `admin@library.local`
- Password: `Admin@123`

Important:

- Change the default password before using the project in a real environment.
- The admin account is created only if no admin user already exists.

## How to Use the System

### For Admin

1. Log in using the admin credentials.
2. Open the admin dashboard to view totals and recent activity.
3. Manage books from the book management page.
4. Add title, author, ISBN, category, and copy count.
5. Use issue management to assign books to students.
6. Track returns, overdue fines, and payments.
7. Download CSV reports from the reports section.

### For Students

1. Register a new account from the registration page.
2. Sign in with your email and password.
3. View your borrowing history and active loans.
4. Check due dates and outstanding fine information.

## Default Workflow

A normal library cycle in this app works like this:

1. Admin adds books to the system.
2. Students register and log in.
3. Admin issues books to students.
4. Students return books on time.
5. Overdue days trigger fine calculation.
6. Admin tracks payments and reports.

## Environment Variables

The app supports the following environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Used for Flask session security | `change-this-secret-before-deployment` |
| `LIBRARYHUB_DB` | Location of SQLite database file | `libraryhub.db` in project folder |
| `LIBRARYHUB_LOAN_LIMIT` | Maximum active loans per student | `3` |
| `PORT` | Local app server port | `5000` |
| `FLASK_DEBUG` | Enables debug mode | `0` / disabled |

Example:

```bash
export SECRET_KEY="my_secure_secret"
export LIBRARYHUB_DB="./libraryhub.db"
export LIBRARYHUB_LOAN_LIMIT="3"
export PORT="5000"
python app.py
```

## Useful Commands

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

### Check syntax

```bash
python -m py_compile app.py
```

### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Database and App Behavior

When the project starts, it automatically:

- Creates the SQLite database if it does not exist
- Creates required tables if missing
- Inserts the default admin account if no admin exists
- Adds starter sample books if the books table is empty

Important:

- The database file is created in the project directory as `libraryhub.db`
- If you want to reset your local testing data, delete `libraryhub.db` and restart the app

## Troubleshooting

### `ModuleNotFoundError: flask`

Run:

```bash
python -m pip install -r requirements.txt
```

Then restart the app after activating the virtual environment.

### Port already in use

Use another port:

```bash
PORT=5001 python app.py
```

or on Windows:

```powershell
$env:PORT=5001
python app.py
```

### Forgotten admin password

Use a secure password reset method or recreate the database if you are in a local development setup.

### Database reset

If you want a clean start:

```bash
rm libraryhub.db
python app.py
```

On Windows:

```powershell
Remove-Item libraryhub.db
python app.py
```

## Project Notes

This project is a strong example of a full-stack mini web app using Python and Flask. It demonstrates:

- Database design
- CRUD operations
- Session-based authentication
- Role-based access control
- Form input validation
- Business logic for a real library workflow
- Simple reporting and CSV export

## Summary

LibraryHub is a practical library management project that combines admin functionality, student access, and real library operations in a clean and easy-to-use web interface. It is suitable for academic submission, demonstration, and further extension.

If you want, I can also generate:

- a more premium GitHub-style README with badges and screenshots section
- a project report in Word-style format
- a presentation outline for this library management system
- an improved UI/UX design suggestion for the frontend

---

Project Repository: `VishvijayPS/IBM-7th-sem-project`


