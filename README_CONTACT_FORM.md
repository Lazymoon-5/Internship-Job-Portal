# Placify Backend — Contact Form API

Public endpoint for the Landing Website's Contact page. No
authentication required. Tested end-to-end against a real database.

## `POST /api/contact`

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "message": "I would like to know more about your placement services."
}
```
(`description` also accepted as an alias for `message`, in case the frontend field is named that.)

**Success (201):**
```json
{ "success": true, "message": "Thank you for reaching out! We'll get back to you soon." }
```

**Errors:**
- `400` — missing `name`, `email`, or `message`
- `400` — invalid email format
- `400` — message over 5000 characters

## What happens on submission
1. Saved to a new `contact_submissions` table (id, name, email, message, notified, created_at) — kept as a permanent record even if the email fails to send
2. An email is sent to **your team's own inbox** (not the submitter) with the submission details, so you actually see it land somewhere real

## Setup — one new environment variable
```
CONTACT_NOTIFICATION_EMAIL=your-team-inbox@gmail.com
```
If this isn't set, it falls back to whatever `SENDGRID_SENDER_EMAIL` is already configured as — so it'll work out of the box with zero extra config, but you may want a dedicated inbox for actual contact inquiries separate from your system's sending address.

**Note:** since this uses SendGrid, the recipient (`CONTACT_NOTIFICATION_EMAIL`) does NOT need to be a verified sender — only the address you're *sending from* needs verification, which is already set up. You can safely point this at any real inbox your team checks.

## Tested
- ✅ Valid submission → saved to DB, `201` returned
- ✅ Missing fields → `400`
- ✅ Invalid email format → `400`
- ✅ Graceful handling when email fails to send (doesn't crash, `notified` stays `false`, submission is still saved)
