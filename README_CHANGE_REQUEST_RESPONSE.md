# Placify Backend — Response to Frontend Change Requests (v1 + v2)

Everything marked REQUIRED in both docs is done and tested end-to-end
against a real database. Details below, organized to match the
original request docs.

---

## v1 §1 REQUIRED

### 1.1 Student change-password
**Already existed** — confirmed present and working (`POST /api/student/change-password`, JWT-protected). No change needed.

### 1.2 CORS for new frontend domain
**Upgraded, not just fixed.** Instead of hardcoding a domain, CORS now
reads additional allowed origins from an env var:
```
ALLOWED_ORIGINS=https://your-new-frontend.com,https://another-domain.com
```
Add this to Render's Environment tab (comma-separated, no spaces needed).
Local dev origins (`localhost:3000`, `localhost:5173`, etc.) are always
allowed regardless. This means future frontend domain changes need
**zero code changes** — just update the env var and redeploy.

---

## v1 §2 VERIFY, FIX IF MISSING — all 4 items checked against actual code

- **2.1 applications count** — was named `application_count` (admin) /
  `applicant_count` (client), neither of which matched any frontend-accepted
  variant. Renamed both to **`applications_count`** (the preferred key).
- **2.2 Dates on list rows** — verified already present (`created_at` on
  jobs, `applied_at` on applications) via existing `SELECT j.*` / `a.*` patterns.
- **2.3 Admin applicant detail completeness** — was missing resume URL,
  skills, certificates. Fixed (see v2 §1.1 below — same fix covers both docs).
- **2.4 Company status field** — verified `admin_status` already present on every company row.

---

## v2 §1 REQUIRED FOR MONDAY

### 1.1 Complete applicant payload — Admin AND Client
Both `GET /api/admin/applications/<id>` and `GET /api/client/applicants/<id>`
now return every field from your table:
```json
{
  "student_name": "...", "student_email": "...", "phone": "...",
  "gpa_cgpa": "...", "resume_url": "...", "cover_letter": "...",
  "skills": [{"skill_name": "...", "level": "..."}],
  "certificates": [{"certificate_name": "...", "issued_by": "...", "file_url": "..."}],
  "profile_photo": "...", "college": "...", "branch": "...",
  "applied_at": "...", "status": "..."
}
```
`resume_url` comes from a `LEFT JOIN` to the resumes table via `resume_id`
(previously only the raw `resume_id` was returned, no actual link).
Tested — confirmed every field populates correctly end-to-end.

### 1.2 Resume Drive link validation
**Implemented at resume upload, not at the apply endpoint** — worth
flagging this deviation: in our architecture, the resume URL is
submitted via `POST /api/student/resumes` (file_url field), and `apply`
just references an already-uploaded `resume_id`. Validating at upload
time gives the same protection (bad links can never reach an
application) and is the only point where the raw URL is actually
available.

Rejects anything that isn't a Google Drive file link or a `.pdf` URL,
with your exact requested error copy about "Anyone with the link —
Viewer" sharing. Tested — invalid links correctly rejected with `400`,
valid Drive links accepted.

### 1.3 CORS + change-password
Same as v1 §1.1/1.2 above — already done.

### 1.4 Cloudinary profile photo field name
Since file upload handling itself is out of scope (per your team's
earlier decision — backend just stores whatever URL the frontend
gives it), this was just a field-naming fix: `profile_photo_url` (the
DB column) is now aliased as **`profile_photo`** in both applicant
detail responses, matching your frontend's expected key.

---

## v2 §2 EMAIL NOTIFICATIONS — all 6 triggers wired

All six use the existing SendGrid integration, sent **after** the DB
commit, wrapped in try/except so an email failure never fails the
actual API action — matching your implementation notes exactly.

| # | Trigger | Wired into | Status |
|---|---|---|---|
| E1 | Student applies → confirmation to student | `apply_to_job` | ✅ |
| E2 | Student applies → alert to company | `apply_to_job` | ✅ |
| E3 | Shortlist / Interview / Offer → student | `shortlist_applicant`, `schedule_interview`, `extend_offer` | ✅ |
| E4 | Reject → student (neutral/kind tone) | `reject_applicant` | ✅ |
| E5 | Admin approves job → company | `approve_job` | ✅ |
| E6 | Admin rejects job → company (with reason if provided) | `reject_job` | ✅ |

**Bonus:** discovered your DB developer had already added a
`rejection_reason` column to the live `jobs` table independently of
what I'd built. Added matching schema support (safe `ALTER TABLE` for
existing databases + included in fresh installs) and wired it through
`PATCH /api/admin/jobs/<id>/reject` — now accepts an optional
`{"rejection_reason": "..."}` body, stored and included in E6's email.

**Tested:** every trigger confirmed firing (checked via `[EMAIL]` log
lines) — all correctly attempt to send and fail gracefully in this
test environment (no real SendGrid key configured here); will send for
real once deployed with your actual key.

---

## v2 §3 STRONGLY RECOMMENDED

- **3.1 Applicant counts on job lists** — done, see v1 §2.1 above (same fix).
- **3.2 Dates on all list rows** — verified already present, see v1 §2.2 above.

---

## Not done (still optional per both docs)
- Newsletter subscribe (`POST /api/newsletter`)
- Notification preferences
- Applicants CSV export

None of these were marked REQUIRED for Monday. Happy to build any of
them next if there's time before the demo — each is a small, contained
addition given everything else already in place.

---

## Testing summary
Full real-database run: register → verify → login (both roles) →
resume upload (invalid link rejected, valid Drive link accepted) →
company posts + submits job → admin approves → student applies (E1+E2
fire) → company views complete applicant profile (all new fields
verified present) → admin rejects a second job with a reason (E6 fires,
reason persisted and returned correctly).
