# Day 11 — Client Blind Grading Facilitation Guide
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. What this session is and why it matters

Day 11 is the moment the entire trial hinges on. Alyssa grades 30 synthetic calls
independently, without seeing the AI's scores. We then compare her grades to the AI's.

If ≥80% of calls agree overall and ≥70% agree per dimension, Phase A passes.
If not, we have one day (D12) to refine the rubric and rescore before the D17 readout.

Getting this session right is as important as building the system.

---

## 2. The anchoring risk

**The biggest failure mode is anchoring Alyssa on AI scores before she gives her own.**

If Alyssa sees an AI score of 72 before grading, she will anchor to it. Her grade will
cluster around that number even when her instinct says something different. This
artificially inflates agreement and destroys the calibration value of the session.

**Rule: Alyssa must not see any AI score until after she has submitted her own grade
for that call.**

This applies to:
- The dashboard (use a mode that hides AI scores)
- Conversation ("the AI scored this a 68..." — do not say this)
- Any summary or chart shown before grading is complete

---

## 3. What Alyssa receives before the session

Send 24 hours in advance:
- The grading sheet (Google Sheet or PDF — see section 5)
- A copy of the rubric with 0–5 anchors (from `docs/rubric-spec.md`)
- This instruction: "Score each call as if you were grading one of your own agents. Use
  your own judgment — there are no right or wrong answers. We'll compare notes afterward."

Do NOT send:
- Any AI scores
- Any mention of how many calls are expected to score high vs low
- Any framing that implies what a "good" score looks like

---

## 4. Session format

**Recommended:** Asynchronous grading, not a live session.

Give Alyssa 2–3 days to grade 30 calls at her own pace. Rushing produces less reliable
grades. Live grading sessions tend to make clients second-guess themselves.

**If a live session is preferred:**
- Block 90–120 minutes
- Grade in batches of 10 with a short break between
- Do not discuss any call until all 30 are graded
- Facilitator is present only to answer rubric clarification questions — not to grade

---

## 5. Grading sheet format

Alyssa grades each call using this structure per call:

```
Call ID: syn_007
Scenario: Family-caller

Dimension            | Your Score (0-5 or N/A) | Any notes?
---------------------|------------------------|------------------
Empathy & Rapport    |                        |
Insurance Verif.     |                        |
Clinical Screening   |                        |
Urgency Triage       |                        |
Family Caller        |                        |
Objection Handling   |                        |
Next-Step Clarity    |                        |
Compliance Language  |                        |

Overall impression: ____/100 (optional — for your reference)
```

**What Alyssa has access to during grading:**
- The transcript (in the dashboard, AI scores hidden)
- The rubric anchors (0–5 descriptions per dimension)
- The definition of each dimension (brief paragraph)

**What Alyssa does NOT have access to during grading:**
- AI scores
- AI evidence snippets
- AI coaching notes
- The gold-standard labels

---

## 6. After grading is complete

Once all 30 calls are graded:

1. Collect the grading sheet
2. Import Alyssa's grades into the system: `python scripts/import_client_grades.py --file alyssa_grades_d11.csv`
3. Run the agreement analysis: `python scripts/d11_agreement_report.py`
4. Share the comparison with Alyssa — **now she can see the AI scores**

The comparison view should show:
- Side-by-side: Alyssa's score vs AI score per dimension per call
- Delta highlighted: green if ±1, red if ≥2
- Overall agreement rate: X% of calls, Y% per dimension

---

## 7. Handling disagreements in the session debrief

Once Alyssa sees the comparison, the conversation should focus on *why* the AI
scored differently, not whether Alyssa or the AI is right.

**Good facilitation questions:**
- "On this call, you scored Empathy a 3 and the AI scored it a 5. What were you
  looking for that you felt was missing?"
- "For the compliance calls, the AI flagged all 6. Did any of those feel like false
  positives to you?"
- "Are there any dimensions where the AI's scoring felt consistently off?"

**What to capture from the debrief:**
For each significant disagreement (delta ≥ 2):
- Which dimension
- Alyssa's interpretation vs what the AI evaluated
- Whether this is a rubric wording issue, a weight issue, or a prompt issue

This becomes the D12 refinement brief.

---

## 8. D12 refinement triggers

| Pattern | Action |
|---|---|
| AI consistently scores dimension X higher than Alyssa | The rubric anchor for that score level needs to be more demanding. Update rubric-v2. |
| AI consistently scores dimension X lower than Alyssa | The rubric anchor needs to credit behaviours Alyssa values. Update rubric-v2. |
| Compliance flags feel too sensitive | Review regex rules — check if patterns are too broad. Update rules.py. |
| Compliance flags feel insufficient | Add patterns. Update rules.py. |
| One scenario type consistently disagrees | Review the synthetic transcripts for that type — may need richer nuance. |
| Disagreements are scattered, no pattern | Prompt issue. Update prompt wording. Update prompt-v2. |

**Rule:** Only change what the disagreement pattern points to.
Do not rewrite the entire rubric because of 3 disagreements in one dimension.

---

## 9. Success bar check

Before D13 rescoring, check where the current scores land:

```bash
python scripts/check_success_bar.py \
  --ai-scores results/d11_ai_scores.json \
  --client-grades results/d11_alyssa_grades.json
```

Output:
```
Overall agreement: 84% (target: ≥80%) ✓
Per-dimension agreement:
  empathy_rapport:          88% ✓
  insurance_verification:   78% ✓
  clinical_screening:       82% ✓
  urgency_triage:           74% ✓
  family_caller_handling:   69% ✗  ← needs refinement
  objection_handling:       83% ✓
  next_step_clarity:        91% ✓
  compliance_language:      96% ✓
```

Any dimension below 70% is a D12 refinement target.

---

## 10. What to do if Phase A fails the success bar

If after D13 rescoring the success bar is still not met:

1. Do not present Day 17 as a success. The success bar was set upfront with Alyssa.
2. Present an honest gap analysis: which dimensions are below threshold and by how much
3. Propose a 5-day extension (use the contingency time) for targeted rubric work
4. Show Alyssa that the system is close — 2–3 dimensions off by small margins is
   a refinement problem, not a fundamental architecture problem

The worst outcome is claiming success when the bar hasn't been met. Alyssa is the CMO
of a treatment centre. She will notice.
