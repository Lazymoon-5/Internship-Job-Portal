# Placify Backend — Admin Dashboard Update

This adds the full Admin backend on top of the existing Student + Client
system: Dashboard Overview, Manage Students, Manage Companies, Manage
Job Posts, Manage Applications, Application/Job Detail pages, Reports &
Analytics, Notifications, and Change Password.

**Every endpoint below was actually tested end-to-end against a real
MySQL database** (seed admin → seed test student/company/job/application →
call every endpoint → verify results), not just written. One real bug
was found and fixed during testing (see Bug Fixes section).

---

## ✅ Auth is now implemented (JWT)

Every Admin route (except `/api/admin/login`) now requires a valid JWT
token, verified server-side before any business logic runs. **Fully
tested**, including confirming unauthorized requests are actually
rejected — not just that authorized ones succeed.

**How it works:**
1. `POST /api/admin/login` on success returns a `token` field alongside
   the `admin` object.
2. The frontend must store this token (e.g. in memory, or `localStorage`
   if acceptable for your security needs) and send it on every
   subsequent Admin API call as a header:
   ```
   Authorization: Bearer <token>
   ```
3. If the header is missing, malformed, or the token is invalid/expired,
   the request is rejected with `401` before touching any data.

**Token expiry:** 24 hours. After that, the admin must log in again to
get a fresh token. Logging in again does **not** invalidate previously
issued tokens (they simply expire naturally on their own) — this is
standard JWT behavior, not a bug.

**Change Password** no longer accepts `admin_id` in the request body —
it now uses the identity from the verified token, closing the earlier
gap where anyone could pass a different admin's ID.

### Frontend integration note
On the Admin Login page, after a successful login response, store the
`token` field. On every other Admin API call, attach it:
```js
fetch(`${API_BASE_URL}/api/admin/dashboard/stats`, {
  headers: { Authorization: `Bearer ${token}` }
})
```
If any Admin API call returns `401`, redirect back to the Admin Login
page — the token is missing/expired.

---

## Old "Known limitation" section (RESOLVED)

---

## New Database Tables
```sql
jobs (id, client_id, title, description, job_type, required_skills,
      eligibility_criteria, location, salary_stipend, last_date_to_apply,
      status, created_at)

applications (id, student_id, job_id, cover_letter, portfolio_link,
              status, admin_notes, applied_at, updated_at)

notifications (id, user_type, user_id, title, message, is_read, created_at)
```
Plus new columns:
- `students.status` — `'Active'` or `'Blocked'`
- `clients.admin_status` — `'Pending'`, `'Approved'`, `'Rejected'`, or `'Blocked'`

All created/altered automatically via `init_db()` on server startup —
**but only for a fresh database**. If you're running this against your
existing Aiven database, the new columns (`status`, `admin_status`) on
the already-existing `students`/`clients` tables need to be added
manually, since `CREATE TABLE IF NOT EXISTS` doesn't alter existing
tables. Run this once against your real DB:
```sql
ALTER TABLE students ADD COLUMN status ENUM('Active','Blocked') DEFAULT 'Active';
ALTER TABLE clients ADD COLUMN admin_status ENUM('Pending','Approved','Rejected','Blocked') DEFAULT 'Pending';
```

## ⚠️ Second important gap — no public "create" APIs for jobs/applications yet
This delivery covers the **Admin side** (view, moderate, manage) of Jobs
and Applications. It does NOT include:
- Company's "Post a Job" API (Company Dashboard → Job Posting page)
- Student's "Apply for Job" API (Student Dashboard → Apply for Job page)

Without those, `jobs` and `applications` tables will be empty in your
real app — Admin pages will just show zeros/empty lists until those two
APIs exist. `scripts/seed_test_data.py` creates fake test data so this
Admin backend could be verified working now — **don't rely on that
script for anything beyond testing**.

---

## Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env`, fill in real DB credentials (+ Resend,
Google Client ID from before).

**Create your first admin:**
```bash
python scripts/seed_admin.py
```

**Run the server:**
```bash
python app.py
```

---

## API Reference

All admin routes require nothing special to call right now (see
security warning above) — just hit them directly.

### Auth
- `POST /api/admin/login` — `{email, password}`
- `POST /api/admin/change-password` — `{admin_id, current_password, new_password, confirm_password}` (min 10 chars)

### Dashboard Overview page
- `GET /api/admin/dashboard/stats` — total students/companies/jobs/applications
- `GET /api/admin/dashboard/recent-applications` — last 5 applications

### Manage Students page
- `GET /api/admin/students?search=&status=&page=1&per_page=10`
- `GET /api/admin/students/<id>`
- `PATCH /api/admin/students/<id>/block`
- `PATCH /api/admin/students/<id>/unblock`
- `DELETE /api/admin/students/<id>`

### Manage Companies page
- `GET /api/admin/companies?search=&status=&page=1&per_page=10`
- `GET /api/admin/companies/<id>`
- `PATCH /api/admin/companies/<id>/approve`
- `PATCH /api/admin/companies/<id>/reject`
- `PATCH /api/admin/companies/<id>/block`
- `DELETE /api/admin/companies/<id>`

### Manage Job Posts page + Job Post Detail page
- `GET /api/admin/jobs/stats` — Total Posts, Pending Review, Active Jobs, Total Applications cards
- `GET /api/admin/jobs?search=&status=&page=1&per_page=10`
- `GET /api/admin/jobs/<id>` — full detail incl. company info + application breakdown (for Job Post Detail page)
- `PATCH /api/admin/jobs/<id>/approve`
- `PATCH /api/admin/jobs/<id>/reject`
- `PATCH /api/admin/jobs/<id>/close`

### Manage Applications page + Application Detail page
- `GET /api/admin/applications/stats` — Total Applied, Pending Review, Shortlisted, Rejected cards
- `GET /api/admin/applications?search=&status=&page=1&per_page=10`
- `GET /api/admin/applications/<id>` — full applicant dossier (for Application Detail page)
- `PATCH /api/admin/applications/<id>/shortlist` — optional `{admin_notes}`
- `PATCH /api/admin/applications/<id>/reject` — optional `{admin_notes}`

### Reports & Analytics page
- `GET /api/admin/reports/monthly-applications?months=6` — for the bar chart
- `GET /api/admin/reports/status-breakdown` — for the donut chart

### Notifications page
- `GET /api/admin/notifications?admin_id=1&page=1&per_page=20`
- `PATCH /api/admin/notifications/mark-all-read` — `{admin_id}`
- `PATCH /api/admin/notifications/<id>/mark-read`

---

## Bug fixes made during testing
- **Monthly applications report returned literal `"%Y-%m"` instead of
  real dates** like `"2026-07"` — caused by incorrectly escaping `%`
  characters in the SQL `DATE_FORMAT()` call (mixed up Python
  string-formatting rules with the DB driver's own parameter
  substitution, which doesn't need that escaping). Fixed and re-verified.

## What still needs building (in priority order)
1. **Auth middleware (JWT)** — see warning above, genuinely important
2. **Company "Post a Job" API** — needed for Manage Job Posts to have real data
3. **Student "Apply for Job" API** — needed for Manage Applications to have real data
4. **Frontend wiring** for all these new Admin endpoints
