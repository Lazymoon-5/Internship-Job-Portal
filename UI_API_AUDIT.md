# Placify — UI-to-API Coverage Audit (Client Dashboard)

Went through all 11 Client Dashboard screens element-by-element against
the built API. Found and fixed 5 real gaps; documenting everything here
so you know exactly what's deploy-ready vs. what still needs scoping.

---

## ✅ Fully covered (built, tested, matches UI)

| Screen | Status |
|---|---|
| **Dashboard** — 4 stat cards, Recent Applications, Active Jobs panel | ✅ Fixed: Active Jobs now includes deadline (needed for "Closing Soon") |
| **Company Profile overview** (100% complete, 3 sections) | ✅ Frontend can compute per-section completion by checking which fields are filled — no backend change needed |
| **Profile Wizard Section 1** (Basic Details) | ✅ All fields covered: company name, industry, contact, address, size, year, city, pincode, state |
| **Profile Wizard Section 2** (Company Information) | ✅ All fields covered: HR name/email/phone, Facebook, LinkedIn, website, about, summary |
| **Profile Wizard Section 3** (Hiring & Verification) | ✅ All fields covered: hiring locations, job types, registration/CIN/GST/PAN numbers, terms |
| **Post a Job** (all 3 sections) | ✅ Fixed: added missing `department` field. Draft vs. Submit flow confirmed working |
| **Jobs Posted / Listing Management** | ✅ Fixed: added `department` so "Role & Department" column has real data. All 4 stats confirmed accurate |
| **Applicant Management list** | ✅ Fixed: list now includes skills, GPA, year, summary — matches the rich applicant cards in the UI, not just name/college |
| **Applicant Profile detail** | ✅ Fixed: now includes skills list (Technical Proficiency tags) |
| **Recruiter Actions** (Shortlist/Reject/Schedule Interview) | ✅ Fixed: added dedicated Schedule Interview and Extend Offer endpoints — previously only Shortlist/Reject existed |
| **Settings → Change Password** | ✅ Fully working |

---

## ⚠️ Gaps found — NOT fixed (need scoping, not quick fixes)

These are real missing features, not bugs — flagging clearly so nothing
gets silently skipped before deployment.

| Missing | Where it's needed | Why not built now |
|---|---|---|
| **Export CSV** | Applicant Management page, top-right button | Needs a decision on exact CSV format/columns — quick to build once specified |
| **Message All Applicants** | Applicant Management page | This implies an actual messaging/email system to candidates — meaningfully bigger scope than a CRUD endpoint |
| **Notification Settings** | Settings page sidebar | No requirements/design given yet for what it should actually control |
| **"Placement Status: Eligible"** field | Applicant Profile page | Not in current schema — would need a definition of what makes a student "eligible" (e.g. min CGPA threshold?) before building |
| **Company logo/photo upload** | Not explicitly in these frames but common pattern | Not requested yet — flagging in case it's expected |

**My recommendation:** none of these block deployment of what's already built — they're additive features on top of a working core. Worth deciding with your team whether any are must-haves before your actual submission deadline, or can be "phase 2."

---

## 🐛 Real bug found and fixed during this audit
`get_applicant_profile_for_client` correctly updated `viewed_by_company`
in the database when a company viewed an applicant, but returned the
**stale pre-update value** in that same API response. Fixed — verified
with a follow-up call showing the corrected value immediately.

---

## Testing performed for this audit
Full fresh-database run: company register → verify → login (JWT) →
3-step profile wizard → post job with department → submit → Admin
approves → student (with skills + summary on profile) applies →
company sees enriched applicant list/detail → schedules interview →
extends offer → **confirmed on the student's own dashboard that the
full funnel (Applied → Interview → Offered) reflects correctly**.

Every single test in this final pass returned exactly the expected
result.
