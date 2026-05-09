# Data Architecture
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Core principle

**Store derived data only. Never store full transcripts.**

| Store | Never store |
|---|---|
| Scores (0–5 per dimension) | Full call transcripts |
| Evidence anchors (short quoted spans + timestamps) | Call recordings |
| Rubric version used | Raw PHI of any kind |
| Prompt version used | |
| Confidence scores | |
| Compliance flags (phrase + timestamp) | |
| Coaching notes | |
| Manager overrides | |
| Evaluation lineage (model ID, rubric, prompt) | |

Target: **~10 MB / agency / year** for derived data.

This is what keeps Phase A outside the HIPAA boundary. Transcript text is fetched
from CTM at evaluation time, processed in memory, and not persisted. Only the
derived artifacts are written to RDS.

---

## 2. Data stores

### 2.1 RDS PostgreSQL 16

**Purpose:** All derived evaluation data.
**Encryption:** KMS-managed key, encryption at rest.
**Access:** Backend services only via SQLAlchemy. No direct public access.
**Backup:** Automated daily snapshots, 7-day retention.

Full schema in `docs/TSD.md` section 4.

**Tables:**
- `evaluations` — one row per scored call
- `dimension_scores` — one row per dimension per call (8 rows max per evaluation)
- `evidence_anchors` — 1–3 rows per dimension per call
- `compliance_flags` — one row per triggered flag
- `score_overrides` — one row per manager override
- `coaching_queue` — one row per call in coaching queue

### 2.2 S3

**Purpose:** Synthetic transcript files (Phase A) + evaluation artifacts.
**Encryption:** KMS-managed key, server-side encryption.
**Access:** Evaluation worker only (read). No public access.

```
s3://am-copilot-dev/
├── synthetic/
│   ├── manifest.json              ← index of all 30 calls
│   ├── syn_001_excellent.json
│   ├── syn_002_excellent.json
│   ├── ...
│   └── syn_030_compliance_failure.json
├── rubric/
│   ├── rubric-v1.yaml             ← locked, never mutated
│   └── rubric-v2.yaml             ← added on D12 after refinement
└── artifacts/
    └── evaluations/
        └── {call_id}/
            └── raw_response.json  ← Bedrock raw output (for debugging only, TTL 30 days)
```

**Note:** Raw Bedrock responses in `artifacts/` have a 30-day lifecycle policy.
They exist for debugging only. Delete after Phase A trial concludes.

---

## 3. Rubric versioning

The rubric is the most important versioned artifact in the system. Every evaluation
record stores the rubric version used, enabling replay and regression testing.

```
data/rubric/
├── rubric-v1.yaml    ← D2: initial rubric, used through D11
└── rubric-v2.yaml    ← D12: refined after client grading session
```

**Rule:** Never edit a rubric file in place. Always create a new version.
Bump the version in the `RUBRIC_VERSION` environment variable to activate.

---

## 4. Prompt versioning

Same principle as rubric versioning. Every evaluation record stores the prompt version used.

```
packages/prompt-library/
├── evaluation/
│   ├── prompt-v1.py    ← initial evaluation prompt
│   └── prompt-v2.py    ← if refinement needed on D12
├── compliance/
│   └── prompt-v1.py    ← compliance contextual reasoning prompt
└── evidence/
    └── prompt-v1.py    ← evidence extraction prompt
```

---

## 5. Transcript handling (not stored)

Transcripts flow through the system in memory only:

```
CTM API → evaluation_worker (memory) → scoring_engine (memory) → evidence_engine (memory)
                                                                          ↓
                                                              evidence anchors → RDS
                                                              (short spans only, not full transcript)
```

The full transcript text never touches the database. Only quoted spans of
50–200 characters are stored as evidence anchors, with their timestamps.

---

## 6. Data flow diagram

```
[CTM Sandbox]
      │
      │ webhook (call.completed)
      ▼
[API Gateway] ──────────────────────────────────────────────────────┐
      │                                                              │
      │ publish job                                                  │
      ▼                                                              │
   [SQS]                                                             │
      │                                                              │
      │ consume job                                                  │
      ▼                                                              │
[Evaluation Worker]                                                  │
      │                                                              │
      │ fetch transcript (memory only, not stored)                   │
      ▼                                                              │
[CTM Integration] ──── transcript text (in memory) ───►             │
                                                      │             │
      ┌───────────────────────────────────────────────┘             │
      │                                                              │
      ▼                                                              │
[Compliance Engine] ── flags ──────────────────────────────────►    │
      │                                                              │
      ▼                                                              │
[Scoring Engine] ──── Bedrock call ──► scores ────────────────►     │
      │                                                              │
      ▼                                                              │
[Evidence Engine] ──── evidence anchors ──────────────────────►     │
      │                                                              │
      ▼                                                              │
[RDS PostgreSQL] ◄──── derived data only (no transcript) ────────────┘
      │
      │ read
      ▼
[Dashboard API] ──── JSON ────► [Vite / React Dashboard]
```

---

## 7. What the developer must never do

- Write a full transcript or any portion > 200 characters to the database
- Write recording URLs to the database
- Log transcript text to CloudWatch
- Store CTM credentials in code or environment files committed to git
- Create an S3 bucket with public access
- Create RDS with a public endpoint
