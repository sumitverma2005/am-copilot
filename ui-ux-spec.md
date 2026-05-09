# UI/UX Specification
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Design system

### Typography
| Role | Font | Weights |
|---|---|---|
| Display / headings | Fraunces | 300 (italic), 500, 700 |
| Body / UI | IBM Plex Sans | 300, 400, 500, 600 |
| Labels / code / mono | IBM Plex Mono | 400, 500 |

Google Fonts CDN. Load in Vite via `index.html`.

### Colour tokens

```css
:root {
  /* Brand */
  --navy-900: #0A1F3D;
  --navy-800: #12315C;
  --navy-700: #1C4775;
  --navy-600: #065A82;
  --teal-500: #1C7293;
  --amber:    #F5A623;
  --amber-soft: #FFF4DD;

  /* Text */
  --ink:    #0F172A;
  --text:   #1E293B;
  --muted:  #64748B;
  --faint:  #94A3B8;

  /* Surface */
  --border:         #E2E8F0;
  --border-strong:  #CBD5E1;
  --surface:        #F8FAFC;
  --surface-2:      #F1F5F9;
  --white:          #FFFFFF;

  /* Semantic */
  --green:      #10B981;
  --green-soft: #D1FAE5;
  --red:        #DC2626;
  --red-soft:   #FEE2E2;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06);
  --shadow-md: 0 4px 6px -1px rgba(15,23,42,0.06), 0 10px 20px -6px rgba(15,23,42,0.08);

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
}
```

### Score colour mapping

| Score | Background | Text | Usage |
|---|---|---|---|
| 80–100 | `--green-soft` | `#065F46` | Excellent / Strong |
| 60–79 | `--amber-soft` | `#92400E` | Acceptable / Needs improvement |
| 0–59 | `--red-soft` | `--red` | Poor / Unacceptable |
| N/A | `--surface-2` | `--muted` | Not applicable |

---

## 2. Screen inventory

| Screen | Route | Description |
|---|---|---|
| Login | `/login` | Cognito hosted UI or custom form |
| Call list | `/` | All 30 scored calls, filterable |
| Call detail | `/calls/:id` | Full evaluation for one call |
| Coaching queue | `/queue/coaching` | Calls below threshold |
| Compliance queue | `/queue/compliance` | Calls with flags |
| Disagreement log | `/disagreements` | All overrides, exportable |

---

## 3. Screen specifications

### 3.1 Call list (`/`)

**Layout:** Full-width table. Sticky header. No sidebar in Phase A.

**Topbar:**
- Left: "AM Copilot" brand mark (amber square, navy italic AM) + "Call Scoring · Phase A"
- Right: Logged-in user name + sign-out link

**Page header:**
- Eyebrow (IBM Plex Mono, uppercase, teal): "WEEK 43 · PHASE A TRIAL"
- Title (Fraunces 44px): "30 calls scored, *ready for review*"
- Sub (IBM Plex Sans 14px, muted): brief summary — "X need attention, Y on track"

**Filter chips:** All · Excellent · Family-caller · Insurance · Urgency · Compliance-failure

**Table columns:**
| Column | Type | Notes |
|---|---|---|
| Call ID | Mono text | e.g. `syn_001` |
| Scenario | Badge | Colour-coded by type |
| Agent | Text | Agent name |
| Duration | Text | e.g. `8m 12s` |
| Overall score | Score badge | Colour by range |
| Worst dimension | Text | Lowest-scoring applicable dimension name |
| Status | Badge | `Scored` / `Overridden` / `In review` |
| Compliance | Icon | Red warning icon if any flag |

**Row click:** Navigate to `/calls/:id`

---

### 3.2 Call detail (`/calls/:id`)

**Layout:** Two-column at ≥1024px. Single column on mobile.

**Left column (60%):**

*Brief header:*
- Agent avatar (initials, amber gradient)
- Agent name + call ID + date/time
- Call duration + scenario type badge
- Compliance flag warning if present (red banner)

*Headline summary (Fraunces italic):*
- AI-generated 2–3 sentence manager summary
- e.g. "Marcus handled the opening with genuine empathy but missed a critical compliance boundary at 4:32."

*KPI strip (4 metrics):*
- Overall score
- Confidence
- Dimensions scored N/A
- Compliance flags

*Dimension breakdown table:*
- One row per dimension
- Columns: Dimension name | Score badge | Weight | Confidence | Override button
- Click any row → open evidence modal

*Override section (below table):*
- Dimension selector dropdown
- Score selector (0–5 or N/A)
- Comment field (required)
- Submit button

*Coaching notes:*
- Free text area
- Save button
- Saved notes persist to the evaluation record

**Right column (40%):**

*Radar chart (Recharts):*
- 8 axes, one per dimension
- Filled polygon showing scores
- N/A dimensions shown as dotted axis
- Colour: teal fill, navy stroke

*Agent comparison (Phase A: single agent only):*
- This week's average vs this call's score per dimension
- Simple bar chart

---

### 3.3 Evidence modal

Triggered by clicking any dimension row in the call detail.

**Modal structure:**
- Header: dimension name + score badge + eyebrow ("ROOT CAUSE" or "WHAT WORKED")
- Close button (✕)

**Evidence section:**
- Labelled "TRANSCRIPT EVIDENCE — N of M snippets"
- Each snippet displayed as a card:
  - Meta row: `AGENT · 4:32 · Campaign: Google Paid`
  - Quote: transcript text with key phrase highlighted in amber-soft
  - Rationale: 1–2 sentence AI rationale

**Coaching section:**
- Labelled "COACHING NOTE"
- AI coaching suggestion in plain text

**Compliance section (if compliance flag on this dimension):**
- Red eyebrow: "COMPLIANCE VIOLATION"
- Flagged phrase highlighted
- Contextual explanation
- Suggested alternative phrasing

**Footer:**
- Source attribution (mono, muted): "Sources: CTM transcript · rubric-v1 · prompt-v1"
- Close button

---

### 3.4 Coaching queue (`/queue/coaching`)

**Table columns:**
| Column | Notes |
|---|---|
| Agent | Name |
| Call | ID + date |
| Overall score | Score badge |
| Worst dimension | Name + score |
| In queue since | Relative date |
| Action | "Mark coached" button |

Sorted by overall score ascending. "Mark coached" fires `POST /queue/coaching/:id/complete`.

---

### 3.5 Compliance queue (`/queue/compliance`)

**Table columns:**
| Column | Notes |
|---|---|
| Agent | Name |
| Call | ID + date |
| Flag type | `DIAG_CLAIM` / `OUTCOME_GUARANTEE` / `CLINICAL_SCOPE` |
| Flagged phrase | Truncated, full on hover |
| Timestamp | In-call timestamp (e.g. `4:32`) |
| Action | "Mark reviewed" button with comment modal |

Sorted by date descending (most recent first).

---

### 3.6 Disagreement log (`/disagreements`)

**Table columns:**
| Column | Notes |
|---|---|
| Call ID | Link to call detail |
| Dimension | Name |
| AI score | Badge |
| Manager score | Badge |
| Delta | ±N |
| Comment | Truncated, full on hover |
| Manager | Name |
| Date | |

**Export button:** Downloads CSV of all rows.

---

## 4. Responsive behaviour

| Breakpoint | Behaviour |
|---|---|
| ≥ 1024px | Two-column call detail, full table |
| 768–1023px | Single column, table scrolls horizontally |
| < 768px | Single column, table collapses to cards |

---

## 5. Component conventions (Tailwind + React)

- All text colours via CSS variables (not Tailwind colour classes directly)
- Score badges: `<ScoreBadge score={n} />` — handles colour logic internally
- Dimension names: always display as human-readable ("Empathy & Rapport"), store as snake_case internally
- Loading states: skeleton shimmer on all data-dependent elements
- Error states: inline error message with retry button — no full-page error screens
- Empty states: friendly message + context-appropriate call to action
