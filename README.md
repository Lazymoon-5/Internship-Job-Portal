# CampusBridge Backend

Python/Flask backend for the CampusBridge (Placify) Internship & Placement Portal.

## Folder Structure
```
backend/
    app.py                      # App entry point, initializes DB on startup
    routes/student_routes.py    # All /api/student/* endpoints
    controllers/student_controller.py  # Business logic
    models/student.py           # Real MySQL queries (students, tokens, OTPs)
    config/
        config.py               # App settings
        database.py             # MySQL connection pool + table creation
        email_service.py        # Real email sending via Gmail SMTP
        google_auth.py          # Google Sign-In token verification
    .env.example                # Template — copy to .env and fill in real values
    requirements.txt
```

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows (if "path not found": venv\bin\activate)
pip install -r requirements.txt
```

1. Copy `.env.example` to `.env`
2. Fill in your real `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
3. Fill in `EMAIL_ADDRESS` and `EMAIL_APP_PASSWORD` (see Email section below)
4. Leave `GOOGLE_CLIENT_ID` blank until Google OAuth is set up (see Google Sign-In section)

```bash
python app.py
```

You should see `[DB] Connected and tables verified.` in the console — if
you instead see a `[DB] WARNING`, double check your `.env` values (most
common issue: wrong password, or DB_HOST not reachable from this machine).

Tables (`students`, `password_resets`, `otp_verifications`) are created
automatically on first run if they don't already exist — no manual SQL
needed.

## Current Status
- ✅ **Automatic MySQL / in-memory fallback** — if `DB_HOST` is blank or
  unreachable, the app automatically uses in-memory storage instead of
  crashing, so you can keep testing OTP/email/Google-login while
  waiting on real database credentials. Check the console on startup —
  it clearly prints which mode is active:
  ```
  [MODE] Using REAL MySQL database.
  ```
  or
  ```
  [MODE] DB not configured/reachable — using IN-MEMORY storage.
  [MODE] Data will reset when the server restarts.
  ```
  **Nothing needs to change in the code** to switch — just fill in
  `DB_HOST`/`DB_USER`/`DB_PASSWORD`/`DB_NAME` in `.env` once your
  database is hosted and reachable, and restart the server.
- ✅ Student Register — creates account as **unverified**, sends OTP
- ✅ OTP Verification — required before login works
- ✅ Resend OTP
- ✅ Student Login — blocked with a clear error until OTP is verified
- ✅ Forgot Password — sends a **real email** with reset link
- ✅ Reset Password
- ✅ Google Sign-In endpoint — built and ready, returns a clear error
  until `GOOGLE_CLIENT_ID` is configured (see below)
- ✅ CORS configured for the React frontend (`localhost:3000`)

## API Endpoints

### 1. Register
`POST /api/student/register`
```json
{
  "name": "Suher Shaikh",
  "email": "suher@college.edu",
  "password": "SecurePass123",
  "college": "XYZ Institute",
  "branch": "Computer Engineering"
}
```
Creates the account as **unverified** and emails an OTP. Response includes
`"email_sent": true/false` — if email delivery fails (e.g. bad Gmail
credentials), a `dev_otp` field is included as a fallback so testing
isn't blocked.

Errors: `400` missing fields, `409` email already registered

---

### 2. Verify OTP
`POST /api/student/verify-otp`
```json
{ "email": "suher@college.edu", "otp": "123456" }
```
Marks the account as verified. OTP expires after **10 minutes**, max
**5 incorrect attempts** before it's locked (must request a new one).

---

### 3. Resend OTP
`POST /api/student/resend-otp`
```json
{ "email": "suher@college.edu", "purpose": "registration" }
```

---

### 4. Login
`POST /api/student/login`
```json
{ "email": "suher@college.edu", "password": "SecurePass123" }
```
Returns `403` with `"requires_verification": true` if the account hasn't
verified its OTP yet.

---

### 5. Google Login
`POST /api/student/google-login`
```json
{ "id_token": "the-id-token-from-Google-Sign-In-on-the-frontend" }
```
Returns `501` until `GOOGLE_CLIENT_ID` is set in `.env`. See "Setting up
Google Sign-In" below for the full walkthrough.

---

### 6. Forgot Password
`POST /api/student/forgot-password`
```json
{ "email": "suher@college.edu" }
```
Sends a real email with the reset link. Always returns the same generic
success message whether or not the email is registered (prevents account
enumeration). Falls back to `dev_reset_link` in the response if email
sending fails.

---

### 7. Reset Password
`POST /api/student/reset-password`
```json
{
  "token": "token-from-the-email-link",
  "new_password": "NewSecurePass123",
  "confirm_password": "NewSecurePass123"
}
```

## Setting up real email (Gmail)
1. Create/use your dummy Gmail account.
2. Turn on **2-Step Verification**: Google Account → Security → 2-Step Verification.
3. Go to https://myaccount.google.com/apppasswords
4. Generate an App Password, choosing "Mail" as the app. Copy the 16-character code.
5. In `.env`:
   ```
   EMAIL_ADDRESS=your-dummy-account@gmail.com
   EMAIL_APP_PASSWORD=the16charactercode
   ```
   (No spaces in the app password, even if Google displays it with spaces.)
6. Restart the server and test `/register` or `/forgot-password` — check
   the dummy inbox for the actual email.

**If email fails to send:** the API doesn't crash — it logs the error to
the console and falls back to returning `dev_otp` / `dev_reset_link` in
the response so you can keep testing without a working inbox.

## Setting up Google Sign-In
1. Go to https://console.cloud.google.com/
2. Create a new project (or use an existing one)
3. APIs & Services → OAuth consent screen → configure (External, add app
   name + your email, save)
4. APIs & Services → Credentials → Create Credentials → OAuth client ID
   → Application type: **Web application**
5. Under "Authorized JavaScript origins", add your frontend URL (e.g.
   `http://localhost:3000`)
6. Copy the generated Client ID (`123...apps.googleusercontent.com`)
7. Put it in `.env` as `GOOGLE_CLIENT_ID`
8. On the **frontend**, integrate Google's Sign-In button using this same
   Client ID. When a user signs in, Google gives the frontend an
   `id_token` — send that to `POST /api/student/google-login`.

## Database Schema
```sql
students (id, name, email, password_hash, college, branch,
          is_verified, google_id, created_at)

password_resets (id, email, token, expires_at, created_at)

otp_verifications (id, email, otp_code, purpose, expires_at,
                    is_used, attempts, created_at)
```
All created automatically by `init_db()` on server startup.

## Frontend Connection Notes
- CORS is configured to allow `http://localhost:3000` and
  `http://127.0.0.1:3000`. If your React dev server runs on a different
  port, add it to the `origins` list in `app.py`.
- All responses are JSON with a `"success": true/false` field — check
  this first on the frontend before reading other fields.
- Store the returned `student` object (minus password) in frontend state
  after login/registration for use across the app.

## Notes for next steps
- Passwords are always hashed (`werkzeug.security`), never stored plain.
- Google-signed-up students get `is_verified = true` automatically (no
  OTP needed — Google already verified their email) and an unusable
  random password hash, since they'll always log in via Google.
- If you need session/token-based auth (JWT) for keeping users logged in
  across requests, that's a separate next step not yet included here —
  ask if you want it added.
