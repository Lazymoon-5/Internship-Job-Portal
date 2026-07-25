# Placify Backend — Response to Change Request v3

Everything below tested against a real, fresh database — not just
written and assumed correct.

---

## ⚠️ Important — please confirm before assuming anything is "still missing"
The v3 doc's §5 lists change-password, email triggers (E1-E6),
`applications_count`, and CORS as still pending. **All four were
already built and tested in the previous delivery**
(`placify_backend_v3_changes.zip`). If your team is still seeing these
as missing, the most likely explanation — based on the exact same
pattern we've hit multiple times before — is that zip was never
actually pushed/redeployed to your live Render backend. Please verify
via Render's Events tab that a deploy happened *after* that zip was
extracted into your project, before assuming any further backend work
is needed on those four items.

---

## 1.1 & 1.2 — Student experience fields
**New columns on `students`:** `experience_level` (`Fresher`/`Experienced`,
default `Fresher`), `years_of_experience`, `job_designation`,
`experience_company`, `experience_duration`.

**Register** (`POST /api/student/register`) now accepts optional
`experience_level` and `years_of_experience`:
- If `experience_level` is `"Experienced"`, `years_of_experience` is
  **required** and must be `> 0` — tested, returns clean `400` otherwise
- Defaults to `Fresher` / `0` if omitted entirely

**Profile** (`GET`/`PUT /api/student/profile`) — all 5 fields are now
part of the standard profile GET/PUT, editable the same way as every
other profile field (Settings page or wizard).

**Applicant views** — `GET /api/admin/applications/<id>` and
`GET /api/client/applicants/<id>` both now include all 5 experience
fields, so recruiters can see a candidate's experience level directly.

## 1.3 — `gpa` legacy alias
`PUT /api/student/profile` now accepts **either** `gpa` or `gpa_cgpa`
as the key — both write to the same column. `GET /api/student/profile`
returns **both** keys (`gpa_cgpa` and `gpa`) with the same value, so
either naming works on read too. Tested — saving via `gpa` correctly
persists and reads back through both keys.

## 2.1 — Company registration requires address
`POST /api/client/register` now requires `address`, `city`, `state`
(pincode stays optional) — returns `400` if missing. These are saved
into the **same columns** the Company Profile wizard already uses (no
schema duplication), via the existing profile-update mechanism —
confirmed the address is immediately visible on `GET /api/client/profile`
right after registration, before the wizard is ever touched.

## 3 — Job dates as plain `YYYY-MM-DD`
`last_date_to_apply` now returns as a clean date string everywhere a
job appears — Student browse/detail, Client jobs list/detail, Admin
jobs list, and the Client Dashboard's Active Jobs panel. Previously
returned as a full RFC-style timestamp
(`"Tue, 21 Jul 2026 00:00:00 GMT"`); confirmed fixed across all 4 call
sites via direct testing, not just one.

## 4 — `profile_completion` (0-100)
Added to both `GET /api/student/profile` and `GET /api/client/profile`
— a simple percentage of how many profile fields are actually filled
in. Not a spec'd exact formula (none was given), so this is a
reasonable first pass — happy to adjust the weighting/field list if
your team wants specific fields to count more.

---

## Testing summary
Fresh database → register Fresher student (no experience fields
needed) → register Experienced student without years (correctly
rejected) → register with years (accepted) → register company without
address (rejected) → with address (accepted, confirmed immediately
visible on profile) → verify + login both → update profile via legacy
`gpa` key → confirmed both `gpa`/`gpa_cgpa` read back correctly →
company posts + submits job with a deadline → admin approves → checked
date format on all 3 role's views (all clean `YYYY-MM-DD`) → student
applies → company views full applicant payload (all experience fields
+ resume URL present and correct).
