# Placify Backend — Student Dashboard Update

Adds the full Student Dashboard: Profile (view + edit + 3-step
completion wizard), Certifications, Skills, Resumes, Browse Jobs, Job
Detail, and — importantly — the **Apply for Job** flow, which closes a
gap flagged weeks ago (previously only Admin could view/moderate jobs
and applications; now students can actually create them).

**Every endpoint below was tested end-to-end against a real MySQL
database**, including a full real user journey (register → verify →
login → complete profile wizard → add skills/certs → upload resumes →
browse jobs → view job detail → apply → view applied status), plus a
cross-check confirming a student's real application immediately shows
up correctly on the Admin side.

---

## ✅ Student login now issues a JWT token too

Matching Admin's security model exactly — Student login/Google-login
now return a `token` field. Every new Dashboard endpoint below requires
it:
```
Authorization: Bearer <token>
```
The student's identity is read from the verified token, never trusted
from the request body/URL — so a student can only ever see/edit their
own data.

**Note:** Existing Student auth endpoints (register, verify-otp,
forgot/reset-password) are unchanged and still work exactly as before
— only login now additionally returns a token.

---

## Two design decisions worth knowing about

### 1. "Waitlisted" stat card doesn't have a backing status
The Applied Status page design shows 4 stat cards: Total Applied,
Active Progress, Offers Received, **Waitlisted**. Our `applications`
table's status enum is `Applied/In Review/Shortlisted/Interview/
Offered/Rejected` — there's no distinct "Waitlisted" state. I
implemented the 4th card as **Rejected** instead, since that's the
most defensible mapping with the current schema. If your team actually
wants a true "Waitlisted" status (e.g. an application put on hold
without being rejected), that needs a schema change — a 7th enum value
— which I can add on request.

### 2. Resume/photo uploads are URL-only
Per your instruction, these endpoints just store whatever URL the
frontend gives them — no actual file upload handling exists in this
backend. Your frontend team needs to handle the actual file upload
(e.g. to Cloudinary, S3, or wherever) separately and pass the resulting
URL to these endpoints.

---

## New/changed Database Schema

**New tables:** `resumes`, `certifications`, `skills`
**New columns on `students`:** `department`, `current_year`,
`mobile_no`, `profile_summary`, `city`, `pincode`, `state`,
`linkedin_url`, `enrollment_no`, `college_address`, `course`,
`gpa_cgpa`, `profile_photo_url`, `profile_completed`
**New column on `applications`:** `resume_id`

All added automatically via `init_db()` on startup — **including
against your existing Aiven database**, since this uses safe individual
`ALTER TABLE` statements wrapped to skip columns that already exist
(no manual SQL needed this time, unlike the Admin update).

---

## API Reference

### Profile
| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/student/profile` | Full profile incl. certifications + skills |
| PUT | `/api/student/profile` | Partial updates — used by both Settings edit and the 3-step wizard. Include `"mark_completed": true` on the final wizard step |
| POST | `/api/student/profile/photo` | Body: `{photo_url}` |
| POST | `/api/student/profile/certifications` | Body: `{certificate_name, issued_by, file_url}` |
| DELETE | `/api/student/profile/certifications/<id>` | |
| POST | `/api/student/profile/skills` | Body: `{skill_name, level}` |
| DELETE | `/api/student/profile/skills/<id>` | |

### Resumes
| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/student/resumes` | |
| POST | `/api/student/resumes` | Body: `{filename, file_url}`. First upload auto-becomes primary. Max 5 resumes |
| PATCH | `/api/student/resumes/<id>/set-primary` | |
| DELETE | `/api/student/resumes/<id>` | If the deleted one was primary, the next most recent is auto-promoted |

### Browse Jobs
| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/student/jobs` | Query params: `search`, `job_type`, `location`, `page`, `per_page`. Only shows Admin-Approved jobs |
| GET | `/api/student/jobs/<id>` | 404 if not found OR not Approved (student can't distinguish which) |

### Apply / My Applications
| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/student/jobs/<id>/apply` | Body: `{cover_letter, portfolio_link, resume_id}` — `resume_id` optional, defaults to primary resume. `409` if already applied |
| GET | `/api/student/applications` | "My Applications" list |
| GET | `/api/student/applications/stats` | 4 stat cards (see note above on "Waitlisted") |
| GET | `/api/student/applications/<id>` | Full detail — only the owning student can view it |

---

## What still needs building (Company side)
This closes the **Student** half of the apply flow. The **Company**
"Post a Job" API (Company Dashboard → Job Posting page) still doesn't
exist — companies currently have no way to create job posts through
the app itself. Worth prioritizing next, since Admin/Student both now
depend on real job data existing.
