# Synthetic Data Specification
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Purpose

30 synthetic transcripts are the entire dataset for Phase A. They are not demo filler.
They are evaluation infrastructure, regression infrastructure, calibration infrastructure,
and replay infrastructure.

Every transcript must be:
- Deterministic (seeded RNG, same seed = same output every run)
- Realistic enough that a treatment-centre CMO finds them credible
- Tagged with gold-standard labels so automated QA requires no manual scoring
- Behaviorally specific to behavioral-health admissions calls — not generic call-centre transcripts

---

## 2. Call distribution

| Scenario type | Count | Description |
|---|---|---|
| Excellent | 6 | Agent performs at Exemplary or Strong across all applicable dimensions |
| Family-caller | 6 | Caller is a family member, not the patient. Tests Dimension 5 and consent handling. |
| Insurance-confusion | 6 | Coverage issues, benefit confusion, self-pay pivot required |
| Urgency | 6 | Caller presents urgent signals — withdrawal, crisis, recent overdose |
| Compliance-failure | 6 | Agent makes at least one compliance violation — diagnostic claim or outcome guarantee |

Total: **30 calls**

---

## 3. Transcript structure

Each transcript is a JSON file with this structure:

```json
{
  "call_id": "syn_001",
  "generated_at": "2026-05-01T00:00:00Z",
  "seed": 42,
  "scenario_type": "excellent",
  "metadata": {
    "duration_seconds": 487,
    "caller_type": "patient",
    "campaign_source": "google_paid",
    "tracking_number": "+13125550001",
    "agent_id": "agent_003",
    "agent_name": "Marcus T."
  },
  "transcript": [
    {
      "turn": 1,
      "speaker": "agent",
      "timestamp_seconds": 0,
      "text": "Thank you for calling Sunrise Recovery, this is Marcus. How can I help you today?"
    },
    {
      "turn": 2,
      "speaker": "caller",
      "timestamp_seconds": 4,
      "text": "Hi... I'm not sure where to start. I've been struggling with drinking for a while and my wife thinks I need to get help."
    }
  ],
  "gold_labels": {
    "call_id": "syn_001",
    "scenario_type": "excellent",
    "expected_scores": {
      "empathy_rapport": 5,
      "insurance_verification": 4,
      "clinical_screening": 4,
      "urgency_triage": 3,
      "family_caller_handling": null,
      "objection_handling": 4,
      "next_step_clarity": 5,
      "compliance_language": 5
    },
    "expected_overall": 92,
    "compliance_override_triggered": false,
    "expected_flags": [],
    "escalation_required": false,
    "scenario_tags": ["patient-caller", "cooperative", "insurance-confirmed"],
    "coaching_notes": "Exemplary empathy opening. Minor: could have confirmed callback time more precisely."
  }
}
```

---

## 4. Scenario specifications

### 4.1 Excellent (6 calls)

**Goal:** Demonstrate what a high-performing intake call looks like. Every dimension at 4–5.

**Required elements:**
- Warm, unhurried opening — agent acknowledges caller's emotional state in first 2 turns
- Complete insurance verification — carrier, member ID, group number all captured
- Clinical screening — substance type, last use, severity, prior treatment all covered
- Urgency assessed correctly — no urgency signals manufactured
- Clear next step with time commitment before call ends
- Zero compliance violations
- Caller leaves call knowing exactly what happens next

**Caller personas to vary across 6 calls:**
- Patient calling for themselves, cooperative, insurance confirmed
- Patient calling for themselves, nervous, needs reassurance
- Family member (handled excellently — use as contrast to family-caller scenario)
- Patient with prior treatment history
- Patient with co-occurring mental health concern mentioned
- Self-pay patient, agent pivots smoothly to financing options

---

### 4.2 Family-caller (6 calls)

**Goal:** Test Dimension 5 (Family caller handling). Agent must navigate consent, HIPAA
framing, and the family member's own emotional state.

**Required elements:**
- Caller explicitly identifies as a family member (spouse, parent, sibling, adult child)
- Agent must handle consent/HIPAA framing — without being cold or legalistic
- Agent collects appropriate information about the patient
- Agent acknowledges the family member's own distress
- At least 2 calls where the agent handles this excellently (scores 4–5)
- At least 2 calls where the agent handles this poorly (scores 1–2) — for coaching contrast
- At least 2 calls where the agent handles this adequately (score 3)

**Caller personas:**
- Spouse calling about partner's alcohol dependency
- Parent calling about adult child's opioid use
- Adult child calling about parent's dependency
- Sibling calling urgently after an incident
- Employer calling on behalf of employee (tests consent edge case)
- Friend calling — agent must navigate non-family consent correctly

---

### 4.3 Insurance-confusion (6 calls)

**Goal:** Test Dimension 2 (Insurance verification) and Dimension 6 (Objection handling)
under difficult insurance conditions.

**Required elements:**
- At least 2 calls with out-of-network coverage — agent must pivot to alternatives
- At least 2 calls where caller doesn't know their insurance details
- At least 1 call where caller is uninsured — self-pay conversation
- At least 1 call where coverage is confirmed but caller balks at out-of-pocket cost
- All calls should include the insurance verification dialogue in detail

**Common patterns to include:**
- Caller reads off wrong member ID — agent catches and corrects
- Caller on Medicaid in a state where coverage varies — agent handles uncertainty
- Caller has coverage but high deductible — agent pivots to payment plans
- Caller on employer plan, worried about confidentiality — agent addresses correctly

---

### 4.4 Urgency (6 calls)

**Goal:** Test Dimension 4 (Urgency triage). Agent must recognise urgency signals and
respond proportionally — neither ignoring them nor over-escalating non-urgent calls.

**Required elements:**
- At least 2 calls with active withdrawal symptoms mentioned
- At least 1 call with suicidal ideation — agent must activate crisis protocol
- At least 1 call with recent overdose (within 48 hours)
- At least 1 call where urgency is correctly assessed as low (caller researching for future)
- At least 1 call where agent misses urgency signal (for coaching contrast)

**Crisis protocol trigger words to include:**
- "I've been thinking about hurting myself"
- "I don't see the point anymore"
- "I overdosed last night"
- "I'm shaking and I can't stop" (withdrawal signal)
- "I need to get in today or I'm going to use again"

**Important:** Calls with suicidal ideation must show the agent following a defined
crisis protocol — warm transfer to crisis line or immediate escalation. Do not show
the agent handling this conversationally.

---

### 4.5 Compliance-failure (6 calls)

**Goal:** Test Dimension 8 (Compliance language) and the deterministic compliance engine.
Every call must contain at least one triggerable compliance violation.

**Required violations to distribute across the 6 calls:**

| Violation type | Example phrase | Flag code |
|---|---|---|
| Diagnostic claim | "It sounds like you have a dependency problem" | `DIAG_CLAIM` |
| Diagnostic claim | "What you're describing sounds like addiction" | `DIAG_CLAIM` |
| Outcome guarantee | "Don't worry, we'll get you better" | `OUTCOME_GUARANTEE` |
| Outcome guarantee | "Our 30-day program cures this" | `OUTCOME_GUARANTEE` |
| Treatment promise | "You'll be fine after treatment" | `OUTCOME_GUARANTEE` |
| Scope violation | "I think you need residential, not outpatient" | `CLINICAL_SCOPE` |

**Distribution:**
- 2 calls with diagnostic claim only (agent otherwise performs well)
- 2 calls with outcome guarantee only (agent otherwise performs well)
- 1 call with both types (agent is generally poor)
- 1 call where violation is subtle — tests sensitivity of compliance engine

**Each compliance-failure call must:**
- Contain the exact phrase that triggers the regex rule (see `docs/prompt-library.md`)
- Have `compliance_override_triggered: true` in gold labels (if override rule is active)
- Have the violation timestamped so evidence engine can anchor it
- Have `expected_scores.compliance_language: 0`

---

## 5. Determinism and reproducibility

```python
# Generator must use seeded RNG throughout
import random
import faker

MASTER_SEED = 42

def create_generator(scenario_type: str, call_index: int):
    seed = MASTER_SEED + hash(scenario_type) + call_index
    rng = random.Random(seed)
    fake = faker.Faker()
    fake.seed_instance(seed)
    return rng, fake
```

The same seed must always produce the same transcript. This is required for:
- D8 automated QA (compare AI scores against gold labels)
- D12 rubric refinement (rescore the same calls with rubric-v2)
- D13 regression check (verify v2 didn't break v1 wins)

---

## 6. Domain authenticity constraints

The transcripts must pass a credibility check with a treatment-centre CMO.
The following must be accurate to behavioral-health admissions:

**Realistic elements:**
- Treatment centre names should sound like real centres (Sunrise Recovery, Clearview Wellness)
- Insurance carriers should be real: Aetna, BlueCross, Cigna, United, Medicaid
- Substance types: alcohol, opioids (heroin, fentanyl, prescription opioids), methamphetamine, benzodiazepines
- Clinical terminology used correctly but at intake level — not clinical assessment level
- Call duration: 4–12 minutes for most calls, 2–3 minutes for short/redirected calls

**Avoid:**
- Generic call-centre language ("your call is important to us")
- Unrealistic caller composure — distress is normal in this context
- Clinical terms used incorrectly
- Insurance processes that don't match real US health insurance workflows

---

## 7. File naming and location

```
data/synthetic/
├── syn_001_excellent.json
├── syn_002_excellent.json
├── syn_003_excellent.json
├── syn_004_excellent.json
├── syn_005_excellent.json
├── syn_006_excellent.json
├── syn_007_family_caller.json
...
├── syn_025_compliance_failure.json
├── syn_026_compliance_failure.json
├── syn_027_compliance_failure.json
├── syn_028_compliance_failure.json
├── syn_029_compliance_failure.json
└── syn_030_compliance_failure.json
```

A manifest file at `data/synthetic/manifest.json` lists all 30 calls with their
scenario type, seed, and expected overall score for quick reference.
