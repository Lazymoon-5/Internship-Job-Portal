# Placify Backend — Final Batch: Public Jobs, Message Applicants, Student Change Password

## 1. `GET /api/jobs` — genuinely public, no auth
Powers the Home page's "Latest Jobs" preview and any public job
browsing before login. Tested with zero `Authorization` header — works.

```
GET /api/jobs?limit=5                    -> latest 5, for Home preview
GET /api/jobs?search=&job_type=&location=&page=1&per_page=10
GET /api/jobs/<id>                       -> public job detail
```
Same underlying data as `/api/student/jobs` (only Admin-Approved jobs
shown) — this is just the same thing without requiring login.

## 2. `POST /api/client/jobs/<job_id>/message-applicants`
Sends a real email (via Resend) to every applicant of a job.

```json
{ "subject": "Update on your application", "message": "Thanks for applying!" }
```
Response reports a per-recipient count, since individual emails can
fail independently:
```json
{ "success": true, "message": "Message sent to 4 of 5 applicant(s).", "sent_count": 4, "failed_count": 1, "total_recipients": 5 }
```
Tested: graceful handling with no Resend key configured (reports 0
sent, doesn't crash), `400` if the job has no applicants yet, `404` if
you try to message a job that isn't yours (ownership enforced).

**If you actually wanted in-app notifications instead of/alongside real
emails** — say so and I'll add that using the existing `notifications`
table, which is already built but unused for this purpose.

## 3. `POST /api/student/change-password`
Was completely missing before — Admin and Client had it, Student
didn't. Now matches the same pattern exactly.
```json
{ "current_password": "...", "new_password": "...", "confirm_password": "..." }
```
Requires the student's JWT token. Minimum 6 characters (matches the
existing Reset Password rule). Tested: no-token block, wrong current
password, successful change, confirmed login works with new password
and not the old one.

---

All three fully tested against a real MySQL database in this delivery.
