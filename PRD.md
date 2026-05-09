# Product Requirements Document (PRD)
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. User personas

### Primary: Admissions Manager (Alyssa)
- Wants to know which agents handled calls well this week
- Wants to see the evidence behind any score — not just a number
- Wants a coaching queue she can act on Monday morning
- Does not want to listen to calls manually
- Will override AI scores she disagrees with

### Secondary: Admissions Agent (being coached)
- Receives coaching feedback based on their scored calls
- Not a system user in Phase A — managers consume insights and relay coaching

### System: Claude Code developer
- Needs CLAUDE.md and all docs to implement without ambiguity
- Works within the 17-day timeline with two buffer days

---

## 2. In-scope features — Phase A only

### 2.1 Call scoring
- Every synthetic call is evaluated against the 8-dimension rubric
- Each dimension receives a score (0–5) or N/A
- An overall weighted score (0–100) is calculated per the formula in `rubric-spec.md`
- Compliance override applied if Dimension 8 = 0 (pending client confirmation)
- Confidence score attached to every evaluation (low confidence → human review queue)

### 2.2 Evidence drill-in
- Every dimension score is backed by 1–3 transcript evidence snippets
- Each snippet includes: speaker, timestamp, quoted text, rationale
- Manager can click any dimension score to see the evidence
- Evidence is presented in a modal — not a separate page

### 2.3 Coaching queue
- Calls scoring below a threshold (default: overall < 70) appear in coaching queue
- Queue shows: agent name, call date, overall score, worst-performing dimension
- Manager can mark a call as "Coaching done" to clear it from queue
- Queue is sorted by overall score ascending (worst first)

### 2.4 Human override
- Manager can override any dimension score (0–5 or N/A)
- Override requires a comment (free text, required)
- Override recalculates overall score immediately
- Original AI score and override are both stored — override does not erase AI score
- Override is timestamped and attributed to the manager

### 2.5 Disagreement log
- All overrides are collected into a disagreement log
- Log shows: call ID, dimension, AI score, manager score, manager comment, date
- Used on D12 to identify rubric refinement opportunities
- Exportable as CSV

### 2.6 Dashboard — call list view
- Table of all 30 scored calls
- Columns: call ID, scenario type, agent, date, overall score, status (scored / in review / overridden)
- Filterable by scenario type, score range, status
- Sortable by all columns
- Click a row → call detail view

### 2.7 Dashboard — call detail view
- Call metadata: ID, agent, date, duration, campaign source
- Overall score displayed prominently
- 8-dimension score breakdown — radar chart + table
- Evidence drill-in per dimension (modal on click)
- Override controls per dimension
- Coaching notes field (free text, saved to the call record)

### 2.8 Compliance queue
- All calls with any compliance flag appear here regardless of overall score
- Shows: call ID, agent, flag type, flagged phrase, timestamp
- Sorted by date descending (most recent first)
- Manager can mark as "Reviewed" with a comment

---

## 3. Out of scope — Phase A

These items are explicitly deferred. Do not build them.

- Real-time call scoring (streaming)
- Audio playback within the dashboard
- Outbound re-engagement (Ask #1)
- VoiceAI improvements (Ask #2)
- Spam detection / number rotation (Ask #3)
- Real-time manager alerts (Ask #5)
- Multi-agency / multi-tenant support
- Agent-facing portal
- Full replay platform (D12 has light replay only)
- Three-environment model (dev/staging/prod) — dev only in Phase A
- 12-scenario synthetic coverage (Phase A uses 5 scenarios)
- Synthetic audio / TTS — deferred indefinitely

---

## 4. User stories

### Scoring
- As a manager, I want every call automatically scored so I don't have to listen to calls manually
- As a manager, I want to see which dimension caused a low score so I know what to coach
- As a manager, I want to see the exact transcript excerpt that drove a score so I can verify it
- As a manager, I want low-confidence evaluations flagged for my review so I can trust the results

### Overrides
- As a manager, I want to override a score I disagree with so the system reflects my judgment
- As a manager, I want my override and the AI's original score both preserved so I can track drift

### Compliance
- As a manager, I want every compliance violation surfaced immediately regardless of overall score
- As a manager, I want to see the exact phrase that triggered the flag and its timestamp

### Coaching
- As a manager, I want a coaching queue of the worst calls each week so I know where to focus
- As a manager, I want to mark calls as coached so my queue stays actionable

---

## 5. CTM webhook integration

Phase A uses a CTM sandbox sub-account populated with synthetic data.

**Webhook events consumed:**
- `call.completed` — triggers evaluation pipeline
- `call.transcribed` — transcript ready, evaluation can proceed

**Webhook payload minimum required fields:**
```json
{
  "event": "call.completed",
  "call_id": "ctm_12345",
  "recording_url": "https://...",
  "transcript_url": "https://...",
  "duration": 487,
  "tracking_number": "+13125550001",
  "agent_id": "agent_003",
  "timestamp": "2026-05-01T14:23:00Z"
}
```

**Processing flow:**
1. Webhook received → API Gateway → SQS queue
2. Evaluation worker picks from SQS
3. Fetches transcript from CTM API
4. Runs evaluation pipeline
5. Stores scores + evidence anchors in RDS
6. Dashboard reads from RDS via API

---

## 6. API surface

The dashboard consumes these endpoints from the FastAPI backend:

| Method | Path | Description |
|---|---|---|
| GET | `/calls` | List all calls with summary scores |
| GET | `/calls/{call_id}` | Full call detail — scores, evidence, metadata |
| GET | `/calls/{call_id}/evidence/{dimension}` | Evidence snippets for a dimension |
| POST | `/calls/{call_id}/override` | Submit a score override |
| GET | `/queue/coaching` | Coaching queue (calls below threshold) |
| GET | `/queue/compliance` | Compliance queue (calls with flags) |
| POST | `/queue/coaching/{call_id}/complete` | Mark coaching done |
| POST | `/queue/compliance/{call_id}/review` | Mark compliance review done |
| GET | `/disagreements` | Full disagreement log |
| GET | `/disagreements/export` | CSV export |
| GET | `/health` | Health check |

All endpoints require Cognito JWT authentication via `Authorization: Bearer <token>` header.

All responses return `application/json`. Errors return `{ "error": "message", "code": "ERROR_CODE" }`.
