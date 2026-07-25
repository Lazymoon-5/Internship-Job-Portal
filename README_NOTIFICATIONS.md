# Placify Backend — Client Notifications Now Wired Up

The `notifications` table and its list/mark-read functions already
existed, but **nothing was actually creating notifications anywhere** —
it was dead infrastructure. This wires it up for real, plus adds the
Client-side endpoints to read them (only Admin had those before).

**Tested end-to-end**: student applies → company gets a notification;
admin approves a job → company gets notified; admin rejects a job →
company gets notified. Mark-all-read confirmed working, unread count
accurate throughout.

## New: Client Notification Endpoints
(Mirrors Admin's pattern exactly)

| Method | Endpoint |
|---|---|
| GET | `/api/client/notifications` | Query: `page`, `per_page` |
| PATCH | `/api/client/notifications/mark-all-read` |
| PATCH | `/api/client/notifications/<id>/mark-read` |

## When notifications now get created automatically

| Trigger | Notification sent to | Title |
|---|---|---|
| Student applies to a job | The job's company | "New Application Received" |
| Admin approves a job post | The job's company | "Job Post Approved" |
| Admin rejects a job post | The job's company | "Job Post Rejected" |

All three are **best-effort** — wrapped in try/except so that if
notification creation somehow fails, it never blocks or breaks the
actual action (applying, approving, rejecting) that triggered it. A
failure just prints a `[NOTIFICATION]` log line instead of crashing
anything.

## Not yet wired up (worth knowing)
- Shortlist / Reject / Schedule Interview / Extend Offer actions (Client side) don't currently notify the **student** — only Company-facing notifications exist so far. If students should also get notified when their application status changes, that's a similar quick addition — just say the word.
- Company approval/rejection by Admin (the company's own account status, `admin_status`) doesn't send a notification yet either — only job-level approve/reject does.
