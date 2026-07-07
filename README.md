# CampusBridge Backend

Python/Flask backend for the CampusBridge Internship & Placement Portal.

## Folder Structure
```
backend/
    app.py              # App entry point
    routes/             # URL routes (Blueprints) — maps endpoints to controllers
    controllers/        # Business logic for each route
    models/             # Data models (in-memory for now, will become MySQL models)
    config/             # App configuration
```

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Server runs at: `http://localhost:5000`

## Current Status
- ✅ Folder structure set up
- ✅ Student Register API
- ✅ Student Login API
- ✅ Forgot Password API (generates reset link)
- ✅ Reset Password API
- ⏳ No database connection yet — students are stored in an in-memory list
  (`models/student.py`). This will be swapped for MySQL later without
  changing the controller logic. See `config/database.py` for the
  ready-to-activate connection scaffold.
- ⏳ No real email service yet — forgot-password returns the reset link
  directly in the API response (`dev_reset_link`) instead of emailing it,
  so the frontend team can test the flow now. Swap this for a real email
  send later (e.g. Flask-Mail/SMTP) in `controllers/student_controller.py`.

## API Endpoints

### 1. Register Student
`POST /api/student/register`

Request body:
```json
{
  "name": "Suher Shaikh",
  "email": "suher@college.edu",
  "password": "SecurePass123",
  "college": "XYZ Institute of Technology",
  "branch": "Computer Engineering"
}
```

Success response (201):
```json
{
  "success": true,
  "message": "Student registered successfully.",
  "student": {
    "id": 1,
    "name": "Suher Shaikh",
    "email": "suher@college.edu",
    "college": "XYZ Institute of Technology",
    "branch": "Computer Engineering"
  }
}
```

Error responses:
- `400` — missing required field(s)
- `409` — email already registered

---

### 2. Login Student
`POST /api/student/login`

Request body:
```json
{
  "email": "suher@college.edu",
  "password": "SecurePass123"
}
```

Success response (200):
```json
{
  "success": true,
  "message": "Login successful.",
  "student": {
    "id": 1,
    "name": "Suher Shaikh",
    "email": "suher@college.edu",
    "college": "XYZ Institute of Technology",
    "branch": "Computer Engineering"
  }
}
```

Error responses:
- `400` — missing email or password
- `401` — invalid email or password

---

### 3. Forgot Password
`POST /api/student/forgot-password`

Request body:
```json
{
  "email": "reset@college.edu"
}
```

Success response (200) — always returns this same generic message,
whether or not the email is registered (prevents email enumeration):
```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset link has been sent.",
  "dev_reset_link": "http://localhost:3000/reset-password?token=..."
}
```
`dev_reset_link` is a **temporary dev-only field** — remove it once real
email sending is wired up. Right now the "email" is just printed to the
server console (`[MOCK EMAIL] ...`).

Error responses:
- `400` — missing email

---

### 4. Reset Password
`POST /api/student/reset-password`

Request body:
```json
{
  "token": "the-token-from-the-reset-link",
  "new_password": "NewSecurePass123",
  "confirm_password": "NewSecurePass123"
}
```

Success response (200):
```json
{
  "success": true,
  "message": "Password has been reset successfully. You can now log in with your new password."
}
```

Error responses:
- `400` — missing token/passwords, passwords don't match, password too short (<6 chars)
- `400` — token invalid, expired (30 min), or already used

## Database (coming soon)
`config/database.py` has a ready-to-use `get_db_connection()` function
using `mysql-connector-python`, plus a `.env.example` showing the exact
variables needed (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME). Once real
credentials arrive:
1. Copy `.env.example` to `.env` and fill in the real values (`.env` is
   already gitignored, so credentials won't get pushed to GitHub).
2. Update the functions in `models/student.py` to query MySQL instead of
   the in-memory list — keep the same function names so nothing else
   in the app needs to change.

## Notes for next tasks
- Passwords are already hashed with `werkzeug.security` (not stored in plain text),
  so this won't need to change when MySQL is added.
- `models/student.py` has `add_student()` and `find_by_email()` functions —
  when the DB task starts, only the internals of these two functions need
  to change to real SQL queries. Controllers/routes stay the same.
