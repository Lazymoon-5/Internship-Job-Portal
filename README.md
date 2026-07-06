# Placify Backend

Python/Flask backend for the Placify -  Internship & Placement Portal.

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
- ⏳ No database connection yet — students are stored in an in-memory list
  (`models/student.py`). This will be swapped for MySQL later without
  changing the controller logic.

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

## Notes for next tasks
- Passwords are already hashed with `werkzeug.security` (not stored in plain text),
  so this won't need to change when MySQL is added.
- `models/student.py` has `add_student()` and `find_by_email()` functions —
  when the DB task starts, only the internals of these two functions need
  to change to real SQL queries. Controllers/routes stay the same.
