# Placify Backend — Client (Company) Dashboard Update

Adds the full Company Dashboard: Dashboard Overview, Company Profile
(3-step wizard), Post a Job (Draft/Submit flow), Jobs Posted (Listing
Management), and Applicant Management (view/shortlist/reject).

**This closes the "Company Post a Job" gap flagged repeatedly since the
Admin update** — companies can now actually create job posts through
the app, not just via the test-seed script.

**Every endpoint tested end-to-end against a real MySQL database**,
including a full real flow: register → verify → login (JWT) → complete
3-step profile wizard → post a job as draft → submit for approval →
Admin approves it → a real student applies → company views the
applicant (marking it seen) → shortlists them → confirmed the status
change reflects correctly on the student's own side too. One real bug
found and fixed during testing (stale `viewed_by_company` value in the
API response right after marking it viewed — fixed and re-verified).

---

## ✅ Client login now issues a JWT token too (same as Admin/Student)

Every new Company Dashboard endpoint requires:
```
Authorization: Bearer <token>
```
Client identity comes from the verified token — a company can only
ever see/edit its own jobs, applicants, and profile.

**Change Password** (new) works the same way as Admin's — no `client_id`
in the body, taken from the token.

---

## New Database Schema

**New columns on `clients`** (22 total): `contact`, `company_size`,
`year_established`, `city`, `pincode`, `state`, `address`,
`about_company`, `company_summary`, `hr_name`, `hr_contact_email`,
`hr_phone_number`, `facebook_url`, `linkedin_url`, `hiring_locations`,
`preferred_job_types`, `company_registration_number`, `cin_number`,
`gst_number`, `pan_number`, `terms_accepted`, `profile_completed`

**`jobs.status` enum expanded** from `Pending/Approved/Rejected/Closed`
to also include **`Draft`** (default for new jobs) and **`Filled`**
(company marks a position filled without formally closing the listing).

**New column on `applications`:** `viewed_by_company` (BOOLEAN) — powers
the "New/Unseen" stat on the Applicant Management page.

All applied automatically via `init_db()` on startup, including safely
against your existing Aiven database (individual `ALTER TABLE`
statements, each wrapped to skip if already applied).

---

## Job status lifecycle
```
Draft ──(company submits)──> Pending ──(Admin approves)──> Approved ──(company)──> Filled / Closed
                                  └──(Admin rejects)──> Rejected ──(company can edit & resubmit)
```
- **Draft, Pending, Rejected** jobs can be edited by the company
- **Approved** jobs are visible to students in Browse Jobs
- Only Admin can Approve/Reject; only the company can Draft/Submit/Close/Mark Filled

---

## API Reference

### Auth (Client)
| Method | Endpoint |
|---|---|
| POST | `/api/client/change-password` | *(new)* — `{current_password, new_password, confirm_password}`, no `client_id` needed |

*(Register/Login/OTP/Forgot-Reset unchanged from before — Login now additionally returns a `token`.)*

### Dashboard Overview page
| Method | Endpoint |
|---|---|
| GET | `/api/client/dashboard/stats` | Active Job Posts, Total Applicants, Shortlisted, Offers Made |
| GET | `/api/client/dashboard/recent-applications` | Last 5, across all this company's jobs |
| GET | `/api/client/dashboard/active-jobs` | For the "Active Jobs" panel |

### Company Profile page (3-step wizard + edit)
| Method | Endpoint |
|---|---|
| GET | `/api/client/profile` | Full profile |
| PUT | `/api/client/profile` | Partial update — same endpoint powers all 3 wizard steps + Settings edit. Add `"mark_completed": true` on the final step |

### Post a Job / Jobs Posted (Listing Management) page
| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/client/jobs` | Creates as `Draft` by default. Add `"submit_now": true` to submit directly for Admin approval (skips Draft) |
| GET | `/api/client/jobs` | This company's own jobs. Query: `search`, `status`, `page`, `per_page` |
| GET | `/api/client/jobs/stats` | Total Listings, Active Now, Positions Filled, Closed/Drafts |
| GET | `/api/client/jobs/<id>` | Single job detail (ownership-checked) |
| PUT | `/api/client/jobs/<id>` | Edit — only allowed while Draft/Pending/Rejected |
| PATCH | `/api/client/jobs/<id>/submit` | Draft → Pending |
| PATCH | `/api/client/jobs/<id>/close` | → Closed |
| PATCH | `/api/client/jobs/<id>/mark-filled` | → Filled |

### Applicant Management page + Applicant Profile page
| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/client/jobs/<job_id>/applicants/stats` | Total Received, New/Unseen, Shortlisted, Rejected |
| GET | `/api/client/jobs/<job_id>/applicants` | Query: `search`, `status`, `page`, `per_page` |
| GET | `/api/client/applicants/<application_id>` | Full applicant dossier — **automatically marks it as viewed** (drops the New/Unseen count) |
| PATCH | `/api/client/applicants/<application_id>/shortlist` | |
| PATCH | `/api/client/applicants/<application_id>/reject` | |

---

## Bug fixed during testing
`get_applicant_profile_for_client` marked an application as viewed in
the database correctly, but returned the **pre-update** value of
`viewed_by_company` in that same response (stale by one field). Fixed
so the response now reflects the update immediately — verified with a
second call showing `viewed_by_company: 1` right after viewing.

## What's still outstanding
- **Notification Settings** (seen in the Settings page frame, next to Change Password) — not built, no design/requirements given yet for what it should control.
- **Company logo/photo upload** — not part of these frames, not built.
- File uploads (job attachments, company documents mentioned in Hiring & Verification section) are URL-only, same as Student resumes — no backend file storage.
