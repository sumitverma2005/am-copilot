# AM Copilot — Phase A

AI call-scoring intelligence layer for behavioral-health admissions, built on top of CTM (CallTrackingMetrics).

> **Read `CLAUDE.md` first.** It is the single source of truth for architecture, stack, conventions, and the build timeline. Every Claude Code session loads it automatically.

---

## What this is

AM Copilot scores admissions intake calls across 8 rubric dimensions, explains every score with transcript evidence, and surfaces a coaching queue for managers — automatically, on top of the existing CTM stack.

Phase A: 17 working days, synthetic data only, no PHI, no BAA required.
Success criterion: ≥80% overall agreement, ≥70% per dimension vs client blind grading on D11.

---

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy · Pydantic v2 · boto3 |
| Frontend | Vite · React 18 · TypeScript · Tailwind CSS 4 · Recharts |
| AI | Claude Sonnet 4.5 via AWS Bedrock |
| Infrastructure | AWS CDK (TypeScript) · us-east-1 |
| Database | RDS PostgreSQL 16 |

---

## Project structure

```
am-copilot/
├── CLAUDE.md              ← start here (auto-loaded by Claude Code)
├── docs/                  ← all pre-dev documents (BRD, PRD, TSD, rubric, etc.)
├── services/              ← Python / FastAPI backends
├── apps/                  ← Vite + React frontends
├── packages/              ← shared Python libraries
├── infra/                 ← AWS CDK (TypeScript)
├── data/rubric/           ← rubric-v1.yaml (locked)
├── data/synthetic/        ← 30 generated calls + gold labels (generated D3–D4)
└── tests/                 ← Pytest suites
```

---

## Local setup

See the full step-by-step guide in `docs/claude-code-setup-guide.md`.

Quick version:

```bash
# 1. Clone and enter
git clone <repo-url> am-copilot && cd am-copilot

# 2. Python environment
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# 3. Environment variables
cp .env.example .env
# Edit .env with your local values

# 4. Verify setup
python -m pytest tests/ -v -m "not bedrock"
```

---

## Key documents

| Document | Purpose |
|---|---|
| `CLAUDE.md` | Project brain — read before anything |
| `docs/BRD.md` | Business requirements and client context |
| `docs/PRD.md` | Features, user stories, API surface |
| `docs/TSD.md` | Technical spec, DB schema, pipeline |
| `docs/rubric-spec.md` | 8-dimension scoring rubric |
| `docs/synthetic-data-spec.md` | Transcript generator spec |
| `docs/prompt-library.md` | All prompts + compliance rules |
| `docs/testing-plan.md` | D8 QA suite and D13 regression |

---

## Critical rules

- **Never store full transcripts** — evidence anchors only (max 200 chars)
- **Never hardcode credentials** — Secrets Manager in AWS, `.env` locally
- **Always version prompts and rubrics** — never edit in place
- **Synthetic data only in Phase A** — no real CTM production credentials
- **N/A is not zero** — excluded dimensions don't affect the weighted average
