# Rubric Specification
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Draft — pending client sign-off on weights and compliance override
**Last updated:** 2026-05

---

## 1. Purpose

This document is the scoring contract. It defines exactly what the AI evaluates,
how it scores each dimension, how scores are weighted, and how the overall score
is calculated. Every synthetic call's gold-standard labels and every AI evaluation
must conform to this specification.

---

## 2. Scoring scale

Every dimension uses the same 0–5 scale:

| Score | Label | Behavioural anchor |
|---|---|---|
| 5 | Exemplary | A call you would use in agent training. Nothing to improve. |
| 4 | Strong | Solid work. One small coaching note at most. |
| 3 | Acceptable | Got the job done. Nothing wrong, nothing notable. |
| 2 | Needs improvement | Identifiable gaps a coaching session would address. |
| 1 | Poor | Significant problems on this dimension. |
| 0 | Unacceptable | Actively wrong, or a required step skipped entirely. |
| N/A | Not applicable | This dimension does not apply to this call. Excluded from average — NOT scored as zero. |

---

## 3. The eight dimensions

### Dimension 1 — Empathy & rapport
**Weight: 1.5×**

Did the agent acknowledge the caller's emotional state and build trust in the first 60
seconds? Callers to a treatment centre are rarely calm — they are anxious, exhausted,
sometimes calling at the worst moment of their year.

**Score for:**
- Agent slowed down and listened
- Matched the caller's emotional register
- Did not sound scripted or transactional
- Used the caller's name
- Acknowledged the difficulty of the situation before moving to information gathering

**Score against:**
- Jumping straight to intake questions without acknowledgement
- Flat or robotic tone
- Talking over the caller's emotional disclosures

**N/A:** Never — every call has a tone, and tone is always scoreable.

---

### Dimension 2 — Insurance verification
**Weight: 1.0×**

Did the agent collect and verify the right coverage details, in the right order,
without losing the caller along the way?

**Score for:**
- Carrier, plan type, member ID, and group number captured
- Verification framed as a step toward help, not gatekeeping
- Pivot to alternatives (self-pay, financing, sliding scale) if coverage was a problem
- Did not overwhelm caller with insurance jargon

**Score against:**
- Missing key fields (member ID, group number)
- Making coverage sound like a barrier
- No alternative offered when coverage was insufficient

**N/A:** If caller explicitly stated they are self-pay and agent confirmed and pivoted correctly, score the pivot under objection handling instead.

---

### Dimension 3 — Clinical screening
**Weight: 1.0×**

Did the agent ask the right diagnostic-adjacent questions to understand what the caller
needs — without overstepping into clinical territory?

**Score for:**
- Substance use history and type captured
- Severity indicators surfaced (frequency, last use, withdrawal symptoms)
- Prior treatment history asked
- Co-occurring mental health concerns noted if volunteered
- Agent stayed clearly in intake role — did not diagnose or clinically assess

**Score against:**
- Missing substance use history entirely
- Crossing into clinical territory ("that sounds like you have a dependency")
- Asking leading or diagnostic questions ("do you think you're an addict?")

**N/A:** Very short calls that were redirected before screening could begin.

---

### Dimension 4 — Urgency triage
**Weight: 1.0×**

Did the agent correctly assess whether this is a same-day need, a this-week need,
or something that can wait — and act on it?

**Score for:**
- Urgency signals caught (withdrawal, suicidal ideation, recent overdose, unsafe living situation)
- Appropriate escalation when urgency was high ("I want to make sure we get you in today")
- Correct de-escalation when urgency was low — no manufactured urgency
- Crisis protocol activated when suicidal ideation or overdose mentioned

**Score against:**
- Missing clear urgency signals in the transcript
- Treating a crisis caller like a routine inquiry
- Manufacturing urgency to pressure a non-urgent caller

**N/A:** Calls where the caller explicitly stated they were researching for a future need and there were no urgency signals.

---

### Dimension 5 — Family caller handling
**Weight: 1.0×**

When the caller is a family member rather than the patient — which is common in this
vertical — did the agent navigate that correctly?

**Score for:**
- HIPAA and consent framing handled without being legalistic or cold
- Right information about the patient collected without the agent speaking for the patient
- Family member's own emotional state acknowledged (they are often in crisis too)
- Agent explained what the family member can and cannot do

**Score against:**
- Collecting patient information without consent framing
- Ignoring the family member's distress
- Giving clinical information about the patient without appropriate framing

**N/A:** Caller is the patient themselves (confirmed in transcript).

---

### Dimension 6 — Objection handling
**Weight: 1.0×**

When cost, fear, family pressure, or "I'm not sure I'm ready" came up, did the agent
address it constructively?

**Score for:**
- Acknowledged the objection before responding (did not immediately counter)
- Offered concrete alternatives where relevant (financing, family support resources, peer stories)
- Avoided defensive, dismissive, or salesy language
- Did not push past a stated "no" inappropriately

**Score against:**
- Jumping to counter-arguments before acknowledging the concern
- Repeating the same response when the caller pushed back
- High-pressure tactics
- Giving up entirely on a wavering caller who still wanted help

**N/A:** Calls where no objections were raised and the caller was fully cooperative throughout.

---

### Dimension 7 — Next-step clarity
**Weight: 1.0×**

Did the caller leave the call knowing exactly what happens next, by when, and who owns it?

**Score for:**
- Specific next step set (admissions appointment, callback, document submission)
- Timing stated clearly ("we'll call you back within the hour")
- Ownership clear ("I'm going to send you an email right now")
- Follow-up commitments captured in the system (agent confirmed this verbally)

**Score against:**
- Vague close ("we'll be in touch")
- No next step set before ending the call
- Timing unclear or missing
- Caller had to ask what happens next

**N/A:** Calls that ended because the caller was not eligible or declined to proceed.

---

### Dimension 8 — Compliance language
**Weight: 1.5×**

Did the agent stay on the right side of what they are licensed to say?

**Score for:**
- No diagnostic language used ("you have an addiction," "this sounds like depression")
- No outcome guarantees ("you'll be fine," "we cure this," "30 days and you'll be better")
- Standard intake language used for sensitive topics
- Appropriate referral language when clinical questions arose ("our clinical team will assess...")

**Score against (any of these = score of 0, see compliance override rule below):**
- Diagnostic claims about the caller or patient
- Treatment outcome guarantees
- Promising specific clinical outcomes
- Statements that could constitute unauthorised practice of medicine

**N/A:** Never — compliance language applies to every call.

---

## 4. Weighting rules

| Dimension | Weight multiplier |
|---|---|
| Empathy & rapport | 1.5× |
| Insurance verification | 1.0× |
| Clinical screening | 1.0× |
| Urgency triage | 1.0× |
| Family caller handling | 1.0× |
| Objection handling | 1.0× |
| Next-step clarity | 1.0× |
| Compliance language | 1.5× |

---

## 5. Overall score calculation

```
For each applicable dimension:
  weighted_score = raw_score (0–5) × weight_multiplier

overall = (sum of weighted_scores) / (sum of weight_multipliers for applicable dimensions) × 20

Result: 0–100
```

### Worked example — standard call (no N/A dimensions)

| Dimension | Raw | Weight | Weighted |
|---|---|---|---|
| Empathy & rapport | 4 | 1.5 | 6.0 |
| Insurance verification | 3 | 1.0 | 3.0 |
| Clinical screening | 4 | 1.0 | 4.0 |
| Urgency triage | 3 | 1.0 | 3.0 |
| Family caller handling | N/A | — | — |
| Objection handling | 4 | 1.0 | 4.0 |
| Next-step clarity | 5 | 1.0 | 5.0 |
| Compliance language | 4 | 1.5 | 6.0 |

Sum of weighted scores: 31.0
Sum of applicable weights: 1.5 + 1.0 + 1.0 + 1.0 + 1.0 + 1.0 + 1.5 = 8.0
Overall score: (31.0 / 8.0) × 20 = **77.5 → round to 78**

---

## 6. Compliance override rule

**PENDING CLIENT SIGN-OFF**

Proposed rule: If Dimension 8 (Compliance language) receives a score of 0, the overall
call score is overridden to 0 regardless of all other dimension scores.

Rationale: A compliance violation creates legal exposure that no amount of good empathy
or clear next steps can offset.

This rule must be confirmed by Alyssa before it is implemented. It significantly
changes scoring math for any call with a compliance failure scenario.

**Implementation note:** The compliance engine runs as a deterministic pre-pass using
rules and regex before the LLM evaluation. A regex match on prohibited phrases triggers
a score of 0 on Dimension 8. The LLM then provides contextual reasoning for the evidence
record, but does not override the deterministic result.

---

## 7. Gold-standard label schema

Every synthetic call must carry this JSON block as ground truth for automated QA:

```json
{
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
```

**Field rules:**
- `expected_scores`: null = N/A (dimension excluded from average)
- `expected_overall`: pre-calculated integer using formula in section 5
- `compliance_override_triggered`: true if dimension 8 = 0 and override rule is active
- `expected_flags`: list of compliance flag codes triggered (empty if clean)
- `escalation_required`: true if urgency triage should have triggered crisis protocol
