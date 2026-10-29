# LibraryHub — Library Management System

A responsive college library mini-project built with Python 3.12+, Flask, SQLite, Jinja2, HTML, CSS and JavaScript. It supports administrator and student accounts, catalogue management, circulation, returns, fine payments, reports and CSV export.

## Features

- Secure Werkzeug password hashing and role-protected admin routes.
- Admin dashboard for copies, titles, student count, active/overdue loans and unpaid fines.
- Searchable catalogue; add, edit and delete books with duplicate ISBN protection.
- Student registration, personal borrowing history and active-loan display.
- 14-day loans, configurable three-loan active limit (`LIBRARYHUB_LOAN_LIMIT`), atomic inventory changes, and ₹5/day overdue fines.
- Return operation is idempotent and restores inventory once; fine payments cannot exceed the balance.
- Reports, category inventory and downloadable loan CSV.
- SQLite schema and starter books are initialized automatically. Sample records are inserted only when the book table is empty.

## Requirements and installation

Python 3.12 or newer is recommended. SQLite is included with standard Python distributions.

### Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-venv
cd /path/to/libraryhub
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000.

### Windows PowerShell

```powershell
cd C:\path\to\libraryhub
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that PowerShell window, then activate again. Open http://127.0.0.1:5000.

## Demo credentials

- Administrator email: `admin@library.local`
- Administrator password: `Admin@123`

Change the demo password before deployment. Create a fresh admin password by changing the initial credentials in `init_db()` before the first run, or by updating the admin user's password hash with a small trusted Python/Werkzeug script. Set a strong random `SECRET_KEY` environment variable before deployment. Registration creates student accounts only; there is no public admin registration.

Optional settings:

- `SECRET_KEY`: Flask session secret (required to override the development default for deployment).
- `LIBRARYHUB_DB`: SQLite database file path (default `libraryhub.db` next to `app.py`).
- `LIBRARYHUB_LOAN_LIMIT`: maximum active loans per student (default `3`).
- `PORT`: local server port (default `5000`).

## Project structure

```text
app.py                       Flask routes, validation, database and business rules
templates/                   Jinja2 views
  base.html                  shared navigation and flash messages
  index.html                 searchable public catalogue
  login.html, register.html  authentication
  admin_dashboard.html       administrator overview
  manage_books.html          catalogue management
  book_form.html             add/edit book
  students.html              member list
  issue.html                 issue workflow
  loans.html                 returns and payment records
  student_dashboard.html     personal history
  reports.html               summary and CSV export
  error.html                 friendly 403/404 pages
static/style.css             responsive UI styling
static/app.js                navigation, confirmations and dismissible alerts
requirements.txt             Flask dependency
libraryhub.db                generated SQLite database (created on first run)
```

## Test cases

1. Open `/`; verify starter books and search by title, author, ISBN and category.
2. Register a student with a valid email and 8+ character password; verify duplicate emails and short passwords are rejected.
3. Sign in with the admin demo credentials; verify dashboard totals and protected navigation.
4. Add a book, try a duplicate ISBN, edit its copy count, search it, then delete it. Deletion is blocked while active loans or historical references exist.
5. Issue a book to a student. Verify the due date is 14 days later and availability decreases once.
6. Try issuing beyond the configurable active-loan limit or issuing unavailable stock; verify the operation is rejected without inventory changes.
7. Return a loan. Verify inventory increases once and a second return does not change it. For overdue test data, set `due_on` to a past date in SQLite and return; verify ₹5 per overdue day.
8. Record a partial fine payment, then try paying more than the balance; verify overpayment is rejected and unpaid fines update.
9. Sign in as student; verify only personal history is shown and `/admin` returns 403.
10. Visit Reports and download the CSV; check that the file contains the loan and payment columns.

## Troubleshooting

- `ModuleNotFoundError: flask`: activate the virtual environment and run `pip install -r requirements.txt`.
- Port already in use: set `PORT=5001` (PowerShell: `$env:PORT=5001`) and restart.
- Forgot admin password: preserve the database, then use a local Python script with `werkzeug.security.generate_password_hash()` to replace the administrator's `password_hash`.
- Reset development data: stop the server, back up or remove `libraryhub.db`, then run `python app.py`; this recreates the demo admin and sample catalogue. This deletes existing local circulation data.

## Run and basic checks

```bash
python -m venv .venv
# activate as shown above
pip install -r requirements.txt
python -m py_compile app.py
python app.py
```
