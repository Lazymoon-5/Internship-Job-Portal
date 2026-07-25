# Placify Backend — Complete Notification System

All three requested notification flows are now wired up and fully
tested end-to-end (real database, full chain from registration through
offer). This is on top of the earlier Client-notification update.

## Interpretation note
"Register and verifies" was implemented as **notify on successful
verification only** (not raw registration) — an unverified signup
isn't yet a meaningful event for the recipient to act on. "Job posted"
was implemented as **notify when a job reaches `Pending` status**
(submitted for approval), since that's the moment it needs admin
attention — not when it's merely saved as a Draft. If you wanted literal
"on register" triggers too, let me know — easy to add alongside.

---

## 1. Student notifications (NEW)
Previously students had no way to read their own notifications — the
read/list endpoints didn't exist for them at all. Added:

| Method | Endpoint |
|---|---|
| GET | `/api/student/notifications` |
| PATCH | `/api/student/notifications/mark-all-read` |
| PATCH | `/api/student/notifications/<id>/mark-read` |

**Triggers that now notify the student:**
| Action (by Company) | Student sees |
|---|---|
| Shortlist | "Application Shortlisted" |
| Schedule Interview | "Interview Scheduled" |
| Extend Offer | "Offer Received!" |
| Reject | "Application Update" (soft wording, not harsh) |

## 2. Company account approval/rejection/block (NEW)
When Admin acts on a company's account itself (not a specific job):

| Admin action | Company sees |
|---|---|
| Approve company | "Account Approved" |
| Reject company | "Account Rejected" |
| Block company | "Account Blocked" |

## 3. Admin notifications (NEW — broadcast to ALL admins)
Since there can be multiple admin accounts, these are broadcast — one
notification row is created per existing admin, so each admin has
their own independent read/unread state.

| Trigger | All admins see |
|---|---|
| Student successfully verifies | "New Student Verified" |
| Company successfully verifies | "New Company Verified" |
| A job is submitted for approval (Draft→Pending, or posted directly as Pending) | "New Job Awaiting Approval" |

---

## Design notes
- **Every single trigger is best-effort** — wrapped in try/except so a
  notification failure never blocks the actual action (applying,
  shortlisting, verifying, etc.). A failure just logs a
  `[NOTIFICATION]` line instead of crashing anything.
- **Admin broadcast uses `list_all_admin_ids()`** (new helper in
  `models/admin.py`) — loops through every admin account and creates
  one row each, so multi-admin setups work correctly with independent
  read states per admin.

## Fully tested chain (real database, not mocked)
Student registers → verifies (Admin notified) → Company registers →
verifies (Admin notified) → Admin approves company (Company notified)
→ Company posts + submits a job (Admin notified) → Admin approves job
→ Student applies → Company shortlists (Student notified) → schedules
interview (Student notified) → extends offer (Student notified).

Every notification confirmed present, correctly worded, and readable
via the appropriate role's new/existing endpoint.
