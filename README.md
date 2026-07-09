# CampusBridge Client (Company) Backend

Python/Flask backend for the Client/Company side of the CampusBridge
Internship & Placement Portal.

## Folder Structure
```
backend/
    app.py              # App entry point
    routes/              # URL routes (Blueprints)
    controllers/          # Business logic
    models/               # Data models (in-memory for now, will become MySQL models)
    config/                # App configuration + DB scaffold
```

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows (if you get "path not found", try: venv\bin\activate)
pip install -r requirements.txt
python app.py
```

Server runs at: `http://localhost:5000`

## Current Status
- ✅ Folder structure set up
- ✅ Client (Company) Register API
- ✅ Client (Company) Login API
- ✅ Forgot Password API (generates reset link)
- ✅ Reset Password API
- ⏳ No database connection yet — clients stored in an in-memory list
  (`models/client.py`). Swappable for MySQL later — see `config/database.py`.
- ⏳ No real email service yet — forgot-password returns the reset link
  directly in the response (`dev_reset_link`) for testing.

## API Endpoints

### 1. Register Company
`POST /api/client/register`
```json
{
  "company_name": "Nimbus Technologies",
  "email": "hr@nimbus.com",
  "password": "CompanyPass123",
  "industry": "IT Services",
  "website": "https://nimbus.com"
}
```
Success (201): returns `{"success": true, "message": ..., "client": {...}}`
Errors: `400` missing fields, `409` email already registered

---

### 2. Login Company
`POST /api/client/login`
```json
{
  "email": "hr@nimbus.com",
  "password": "CompanyPass123"
}
```
Success (200): returns `{"success": true, "message": "Login successful.", "client": {...}}`
Errors: `400` missing fields, `401` invalid email/password

---

### 3. Forgot Password
`POST /api/client/forgot-password`
```json
{ "email": "hr@nimbus.com" }
```
Success (200) — always the same generic message whether or not the
email exists (prevents email enumeration):
```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset link has been sent.",
  "dev_reset_link": "http://localhost:3000/reset-password?token=..."
}
```
`dev_reset_link` is temporary/dev-only — remove once real email sending
is added.

---

### 4. Reset Password
`POST /api/client/reset-password`
```json
{
  "token": "the-real-token-from-the-forgot-password-response",
  "new_password": "NewSecurePass123",
  "confirm_password": "NewSecurePass123"
}
```
Success (200): `{"success": true, "message": "Password has been reset successfully..."}`
Errors: `400` mismatch/missing/too short, invalid/expired/reused token

## How to test with Postman
1. Run `python app.py`
2. POST to `/api/client/register` with the JSON above → confirm `201` + `success: true`
3. POST to `/api/client/login` with same email/password → confirm `200` + `success: true`
4. POST to `/api/client/forgot-password` with the same email → copy the token from `dev_reset_link` in the response
5. POST to `/api/client/reset-password` using that **real copied token** (not the placeholder text) → confirm `200` + `success: true`
6. Try logging in again with the new password to confirm it actually changed

## Notes for next tasks
- Passwords are already hashed with `werkzeug.security`.
- `models/client.py` functions (`add_client`, `find_by_email`,
  `update_password`, etc.) are written so only their internals need to
  change to real SQL once MySQL credentials arrive — controllers/routes
  won't need to change.
