# Placify Backend — v3 Doc Validation + New: Multiple Work Experiences

## Validation results — everything checked against real, tested code

| Item | Status | Evidence |
|---|---|---|
| §1.1 Register experience fields | ✅ Already done | Validated in prior delivery + this session's regression run |
| §1.2 Profile flat experience fields | ✅ Already done | Same |
| §1.2 **Multiple experiences array** | ✅ **NEW — built this session** | See below |
| §1.3 `gpa_cgpa` round-trip | ✅ Already done | Confirmed both `gpa`/`gpa_cgpa` read/write correctly |
| §2.1 Company address at registration | ✅ Already done | Confirmed required, persists into profile columns |
| §3 Date format (`YYYY-MM-DD`) | ✅ Already done | Confirmed clean format on all 4+ call sites |
| §4 `profile_completion` | ✅ Already done | Present on both Student and Client profile GETs |
| §5 change-password, E1-E6 emails, `applications_count`, CORS | ✅ Already done | **See warning below** |
| §6 Not a backend concern | N/A | No action needed, frontend-only items |

## ⚠️ About §5 appearing again as "still open"
This is the **third time** this same list has appeared in a change-request
doc as "pending," despite being built, tested, and delivered twice
already. At this point the most likely explanation isn't a backend gap
— it's that the deployed Render backend is running older code than
what's been delivered. **Before doing anything else**, please have
whoever manages deployment confirm:
1. Render's **Events** tab shows a deploy timestamp *after* the last
   zip was pushed
2. The deployed code actually contains `applications_count` — quickest
   check: `curl https://your-backend.onrender.com/api/admin/jobs` (with
   a valid admin token) and look for that exact field name in the response

If the deployed backend genuinely doesn't have these, something is
going wrong in the push/deploy step itself, not in what's being built —
worth debugging that pipeline specifically rather than re-requesting
the same features again.

---

## NEW: Multiple Work Experiences (§1.2 update)

### New table: `student_experiences`
```sql
CREATE TABLE student_experiences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_designation VARCHAR(200),
    company VARCHAR(200),
    duration VARCHAR(100),
    years DECIMAL(4,1) DEFAULT 0,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### How it works
`PUT /api/student/profile` now additionally accepts an `experiences` array:
```json
{
  "experiences": [
    { "job_designation": "SE Intern", "company": "Infosys", "duration": "Jun–Dec 2024", "years": 0.5 },
    { "job_designation": "Junior Dev", "company": "TCS", "duration": "2025", "years": 1 }
  ]
}
```

**Behavior: full replace on every save**, not incremental add/remove.
Each `PUT` with an `experiences` array wipes and re-inserts that
student's full experience list. This matches how a profile save
naturally works — the frontend sends its current complete list each
time. Tested — saving 2 entries, then saving again with just 1, correctly
leaves exactly 1 (not 3).

**Backward compatibility confirmed**: sending both the flat fields
(`job_designation`, `experience_company`, `experience_duration`,
`years_of_experience`) AND the `experiences` array in the same request
works correctly — both are stored independently, no conflict. A simple
frontend can send only the flat fields and ignore the array entirely,
exactly as the doc allows.

**Returned on:**
- `GET /api/student/profile` → `"experiences": [...]`
- `GET /api/client/applicants/<id>` → `"experiences": [...]`
- `GET /api/admin/applications/<id>` → `"experiences": [...]`

All three confirmed via direct testing — a saved 2-experience list showed
up correctly in a real applicant's Client and Admin views after a real
application was submitted.

---

## Testing performed this session
Fresh database → register Experienced student → verify/login → save
profile with both flat fields AND a 2-item experiences array in one
request → confirmed both round-trip correctly on GET → saved again with
1 item → confirmed old entries were replaced, not appended → registered
+ approved a company → posted + approved a job → student applied →
confirmed the experiences array appears correctly on both the Client's
and Admin's applicant detail views.
