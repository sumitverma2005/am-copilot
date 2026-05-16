# D8 Calibration Analysis — 2026-05-16

| | |
|---|---|
| Calls graded (human) | 30 |
| Calls with AI scores | 30 |
| Comparable (both)    | 30 |

## Overall Score Agreement (target: ≥80%)

17/30 calls within ±10 points — **57%** — **✗ FAIL**

## Per-Dimension Agreement (target: ≥70%, criterion: |delta| ≤ 1)

| Dimension | Compared | Agreement | Avg \|delta\| | Bias | Status |
|---|---|---|---|---|---|
| Empathy & rapport | 30 | 80% | 0.8 | ≈equal | ✓ PASS |
| Insurance verification | 28 | 86% | 0.9 | AI↑ | ✓ PASS |
| Clinical screening | 29 | 83% | 0.8 | AI↑ | ✓ PASS |
| Urgency triage | 30 | 67% | 1.0 | AI↑ | ✗ FAIL |
| Family caller handling | 7 | 86% | 0.7 | ≈equal | ✓ PASS |
| Objection handling | 12 | 67% | 1.6 | AI↑ | ✗ FAIL |
| Next-step clarity | 30 | 80% | 0.8 | AI↑ | ✓ PASS |
| Compliance language | 30 | 57% | 1.5 | AI↑ | ✗ FAIL |

## Dimensions Needing D9 Rubric Work

### Urgency triage
- Agreement: 67% (target: ≥70%)
- Avg |delta|: 1.0
- Avg signed delta (human − AI): -0.97
- AI consistently scores higher than human. Criteria may be too loose, or AI rewards the presence of keywords rather than execution quality.

### Objection handling
- Agreement: 67% (target: ≥70%)
- Avg |delta|: 1.6
- Avg signed delta (human − AI): -1.58
- AI consistently scores higher than human. Criteria may be too loose, or AI rewards the presence of keywords rather than execution quality.

### Compliance language
- Agreement: 57% (target: ≥70%)
- Avg |delta|: 1.5
- Avg signed delta (human − AI): -1.07
- AI consistently scores higher than human. Criteria may be too loose, or AI rewards the presence of keywords rather than execution quality.

## Outlier Calls (|delta| > 1 on any dimension)

| Call | Dimension | Human | AI | Delta |
|---|---|---|---|---|
| syn_028 | Objection handling | 0 | 5 | -5 |
| syn_028 | Next-step clarity | 1 | 5 | -4 |
| syn_028 | Compliance language | 1 | 5 | -4 |
| syn_028 | Urgency triage | 1 | 4 | -3 |
| syn_028 | Empathy & rapport | 3 | 5 | -2 |
| syn_029 | Objection handling | 0 | 5 | -5 |
| syn_029 | Compliance language | 1 | 5 | -4 |
| syn_029 | Empathy & rapport | 3 | 5 | -2 |
| syn_029 | Clinical screening | 2 | 4 | -2 |
| syn_029 | Urgency triage | 2 | 4 | -2 |
| syn_030 | Objection handling | 1 | 5 | -4 |
| syn_030 | Compliance language | 1 | 5 | -4 |
| syn_030 | Insurance verification | 2 | 4 | -2 |
| syn_030 | Clinical screening | 2 | 4 | -2 |
| syn_006 | Compliance language | 1 | 4 | -3 |
| syn_006 | Insurance verification | 1 | 3 | -2 |
| syn_006 | Urgency triage | 0 | 2 | -2 |
| syn_006 | Next-step clarity | 0 | 2 | -2 |
| syn_009 | Compliance language | 1 | 4 | -3 |
| syn_009 | Empathy & rapport | 3 | 1 | +2 |
| syn_009 | Family caller handling | 3 | 1 | +2 |
| syn_011 | Compliance language | 1 | 4 | -3 |
| syn_014 | Compliance language | 1 | 4 | -3 |
| syn_014 | Objection handling | 0 | 2 | -2 |
| syn_017 | Clinical screening | 2 | 5 | -3 |
| syn_017 | Urgency triage | 2 | 4 | -2 |
| syn_017 | Next-step clarity | 3 | 5 | -2 |
| syn_017 | Compliance language | 3 | 5 | -2 |
| syn_021 | Compliance language | 2 | 5 | -3 |
| syn_021 | Urgency triage | 1 | 3 | -2 |
| syn_023 | Empathy & rapport | 5 | 2 | +3 |
| syn_027 | Urgency triage | 1 | 4 | -3 |
| syn_027 | Empathy & rapport | 3 | 1 | +2 |
| syn_027 | Next-step clarity | 3 | 1 | +2 |
| syn_003 | Compliance language | 3 | 5 | -2 |
| syn_004 | Insurance verification | 1 | 3 | -2 |
| syn_004 | Urgency triage | 0 | 2 | -2 |
| syn_004 | Next-step clarity | 0 | 2 | -2 |
| syn_004 | Compliance language | 2 | 0 | +2 |
| syn_005 | Urgency triage | 0 | 2 | -2 |
| syn_008 | Urgency triage | 0 | 2 | -2 |
| syn_013 | Clinical screening | 5 | 3 | +2 |
| syn_015 | Empathy & rapport | 5 | 3 | +2 |
| syn_015 | Next-step clarity | 3 | 1 | +2 |
| syn_019 | Insurance verification | 1 | 3 | -2 |
| syn_019 | Clinical screening | 1 | 3 | -2 |
| syn_019 | Compliance language | 2 | 0 | +2 |
| syn_020 | Compliance language | 2 | 0 | +2 |
| syn_022 | Urgency triage | 3 | 5 | -2 |

## Overall Score Outliers (|delta| > 10 points)

| Call | Human Overall | AI Overall | Delta |
|---|---|---|---|
| syn_028 | 32 | 90 | -58 |
| syn_029 | 42 | 92 | -50 |
| syn_030 | 35 | 79 | -44 |
| syn_006 | 15 | 46 | -31 |
| syn_017 | 66 | 95 | -29 |
| syn_014 | 15 | 42 | -28 |
| syn_021 | 27 | 54 | -27 |
| syn_004 | 12 | 30 | -18 |
| syn_022 | 81 | 94 | -13 |
| syn_011 | 24 | 36 | -12 |
| syn_015 | 84 | 72 | +12 |
| syn_008 | 41 | 52 | -11 |
| syn_019 | 22 | 34 | -11 |

## Patterns and D9 Recommendations

3 dimension(s) require rubric refinement on D9. Suggested focus per dimension:

- **Urgency triage**: Lower the AI's effective bar — clarify that quality of execution matters, not just presence of keywords. Add 'score against' examples for hollow language.
- **Objection handling**: Lower the AI's effective bar — clarify that quality of execution matters, not just presence of keywords. Add 'score against' examples for hollow language.
- **Compliance language**: Lower the AI's effective bar — clarify that quality of execution matters, not just presence of keywords. Add 'score against' examples for hollow language.

---
*Generated by analyze_disagreements.py · rubric-v1 · 2026-05-16*
