# Business Requirements Document (BRD)
# AM Copilot — Phase A Trial

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Problem statement

Behavioral-health treatment centers live and die by the quality of their admissions intake
calls. A caller in crisis who reaches a poorly-handled intake agent often doesn't call back.
An agent who says the wrong thing — a diagnosis claim, an outcome guarantee — creates legal
exposure that costs far more than the call was worth.

Currently, managers at these centers have no systematic way to know which agents handle calls
well and which don't. QA is manual, slow, and covers maybe 5% of call volume. Coaching is
reactive — managers learn about problems after they've happened at scale.

AM Copilot solves this by automatically scoring every admissions call against a structured
rubric, surfacing the evidence behind each score, and producing a coaching queue managers can
act on immediately.

---

## 2. Client

**Name:** Alyssa
**Title:** CMO
**Organisation:** Behavioral-health treatment center (name withheld pending BAA)
**Current stack:** CTM (CallTrackingMetrics) + Dazos CRM
**CTM setup:** Sandbox sub-account provisioned for Phase A trial (synthetic data only)

### Original asks from Alyssa (discovery call)

| # | Ask | Phase |
|---|---|---|
| 1 | Outbound re-engagement nurture — AI calls/texts stalled admissions leads | Phase D |
| 2 | Smarter inbound VoiceAI agent | Phase D |
| 3 | Spam detection + tracking-number rotation | Phase D |
| 4 | **Call handling score for agent coaching** | **Phase A ← we are here** |
| 5 | Real-time / post-call manager alerts when calls go badly | Phase D |

Ask #4 was chosen for Phase A because:
- Lowest HIPAA exposure (scored on synthetic transcripts, not real patient data)
- Fastest path to a measurable, demonstrable outcome
- Foundational intelligence layer — all other asks depend on reliable call scoring

---

## 3. What AM Copilot is (and is not)

### Is
- An AI intelligence layer on top of CTM
- A call scoring and explainability engine
- A coaching and QA workflow tool
- A derived-insight store (~10 MB/agency/year)

### Is not
- A replacement for CTM
- A telephony platform
- A long-term transcript or recording store
- A HIPAA-covered entity during Phase A (synthetic data only)

**Architectural rule:** Webhooks in from CTM. REST API out to the dashboard.
CTM executes all operational actions. AM Copilot stores derived data only.

---

## 4. Success definition

Phase A is a success when:

| Criterion | Target |
|---|---|
| Overall score agreement | ≥ 80% of calls — AI score within ±1 of Alyssa's blind grade |
| Per-dimension agreement | ≥ 70% per dimension — AI score within ±1 of Alyssa's grade |
| Calls scored | 30 synthetic calls across 5 scenario types |
| Dashboard | Live, Alyssa can log in and use it |
| Evidence | Every score backed by transcript evidence with timestamps |

These criteria were set upfront with the client. They are fixed. Do not adjust them after D11.

---

## 5. Constraints

| Constraint | Detail |
|---|---|
| Timeline | 17 working days (weekdays only), 2 buffer days included (D7, D14) |
| Data | Synthetic only — no real PHI, no real patient calls |
| HIPAA | Phase A is outside the HIPAA boundary by design. No BAA required. |
| Budget | ~$4 AWS cost for Phase A trial |
| Team | Small team, likely 1–2 developers with Claude Code |
| AI engine | Claude Sonnet 4.5 via AWS Bedrock (locked — self-hosted Llama evaluated and rejected) |

---

## 6. Why synthetic data

Real CTM call records are PHI from the moment the call happens — even if the caller never
becomes a patient. HIPAA protects "information that relates to the health of an individual."
The word is individual, not patient.

This means any real admissions call recording or transcript is protected health information
regardless of outcome. Processing it requires a signed BAA.

**The solution:** Synthetic transcripts. No real individual exists in the data. No PHI.
No BAA required. The system and pipeline are production-shaped — only the data is fictional.

This is the entire reason Phase A can ship in 17 working days instead of 3 months.

---

## 7. Stakeholders and sign-off

| Role | Person | Sign-off required on |
|---|---|---|
| Client CMO | Alyssa | Rubric dimensions, success bar, Day 11 grading, Day 17 readout |
| Project lead | TBD | BRD, PRD, TSD, timeline |
| Developer | TBD | TSD, data architecture, prompt library |

---

## 8. Day 17 deliverable

What Alyssa receives at the readout:

- Live dashboard URL with her login credentials
- 30 synthetic calls scored across 5 scenario types
- Per-dimension scores with evidence drill-ins
- Three-way agreement chart: CMO vs AI vs gold-standard labels
- Disagreement log showing where rubric improved after D12 refinement
- Architecture one-pager
- Phase B proposal: BAA timeline, real-data pilot plan
- One-week test access — she uses it, she decides
