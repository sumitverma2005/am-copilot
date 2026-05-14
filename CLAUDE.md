# AM Copilot — Project Brain

> Auto-loaded every Claude Code session. Read this before touching any file.

---

## What this system is

AM Copilot is an **AI intelligence layer** that sits on top of CTM (CallTrackingMetrics).
It scores admissions intake calls for a behavioral-health treatment center, explains those
scores with evidence, and surfaces coaching opportunities for managers.

**CTM is the system of record. AM Copilot is the intelligence layer.**

- Webhooks in from CTM
- REST API out to the dashboard
- Derived insights stored only (~10 MB/agency/year)
- CTM executes all operational actions

AM Copilot does NOT replace CTM. It does NOT store recordings. It does NOT store full transcripts.

---

## Phase A scope — the only scope that exists right now

Phase A proves one question: **can AI score admissions calls reliably enough to create
operational trust?**

- 17 working days
- Synthetic data only — no real patient data, no PHI, no BAA required
- 30 synthetic calls across 5 scenario types
- Success criterion: ≥80% overall agreement, ≥70% per dimension with client blind grading
- Day 17 deliverable: live dashboard the client can log into

Do not build anything outside Phase A scope. Every deferred item is documented in
`docs/PRD.md` under "Out of scope."

---

## Stack

### Backend
| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI |
| ORM | SQLAlchemy + Alembic (migrations) |
| Validation | Pydantic v2 |
| AWS SDK | boto3 |
| Testing | Pytest |

### Frontend
| Layer | Choice |
|---|---|
| Build tool | Vite |
| Framework | React 18 |
| Language | TypeScript |
| Styling | Tailwind CSS 4 |
| Charts | Recharts |

### Infrastructure (AWS CDK — TypeScript)
| Service | Purpose |
|---|---|
| ECS Fargate | Backend containers |
| API Gateway | HTTP entrypoint |
| SQS | Evaluation job queue |
| RDS PostgreSQL 16 | Derived data store |
| S3 | Synthetic dataset + artifacts |
| Amazon Bedrock | Claude Sonnet 4.5 scoring |
| Cognito | Auth |
| KMS | Encryption at rest |
| Secrets Manager | All credentials |
| CloudWatch | Logs + metrics |
| CloudTrail | Audit trail |
| IAM + Identity Center | Least-privilege roles |
| Route53 + CloudFront | DNS + CDN for frontend |

Region: **us-east-1**

---

## Folder structure

```
am-copilot/
├── CLAUDE.md                      ← you are here
├── CLAUDE.local.md                ← personal overrides, gitignored
├── .claudeignore
├── .mcp.json
├── .claude/
│   ├── settings.json
│   ├── skills/                    ← auto-invoked by Claude Code
│   │   ├── scoring-engine/SKILL.md
│   │   ├── evidence-engine/SKILL.md
│   │   ├── synthetic-data/SKILL.md
│   │   └── rubric/SKILL.md
│   ├── agents/
│   │   ├── evaluation-worker.md
│   │   └── compliance-checker.md
│   └── agent-memory/
├── docs/                          ← all pre-dev documents
│   ├── BRD.md
│   ├── PRD.md
│   ├── TSD.md
│   ├── rubric-spec.md
│   ├── synthetic-data-spec.md
│   ├── data-architecture.md
│   ├── prompt-library.md
│   ├── security-spec.md
│   ├── ui-ux-spec.md
│   ├── testing-plan.md
│   └── d11-facilitation-guide.md
├── services/                      ← Python / FastAPI backends
│   ├── api-gateway/
│   ├── ctm-integration/
│   ├── scoring-engine/
│   ├── compliance-engine/
│   ├── evidence-engine/
│   ├── evaluation-worker/
│   └── notification-service/
├── apps/                          ← Vite + React frontends
│   ├── dashboard/
│   ├── review-console/
│   └── admin-console/
├── packages/                      ← shared libraries
│   ├── rubric-engine/
│   ├── prompt-library/
│   ├── shared-types/
│   └── synthetic-data/
├── infra/                         ← AWS CDK (TypeScript)
├── data/
│   ├── synthetic/                 ← 30 generated calls + gold labels
│   └── rubric/rubric-v1.yaml
└── tests/
    ├── scoring/
    ├── compliance/
    └── gold-standard/
```

---

## Non-negotiable rules

1. **Never store full transcripts.** Store scores, evidence anchors, rubric metadata, evaluation lineage only.
2. **Never hardcode credentials.** All secrets live in AWS Secrets Manager. Local dev uses `.env` (gitignored).
3. **Always version prompts.** Every prompt has a `prompt_version` field. Increment on any change.
4. **Always version the rubric.** `rubric-v1.yaml` → `rubric-v2.yaml`. Never mutate in place.
5. **Synthetic data only in Phase A.** No real CTM production credentials. Sandbox sub-account only.
6. **N/A is not zero.** Dimensions scored N/A are excluded from the weighted average entirely.
7. **Compliance engine is deterministic first.** Rules and regex detect violations. LLM provides contextual reasoning, not sole authority.

---

## Naming conventions

- Python files: `snake_case.py`
- TypeScript files: `camelCase.ts` / `PascalCase.tsx` for components
- Database tables: `snake_case`
- Environment variables: `SCREAMING_SNAKE_CASE`
- Prompt versions: `prompt_v1`, `prompt_v2`
- Rubric versions: `rubric-v1.yaml`, `rubric-v2.yaml`
- Git branches: `feature/short-description`, `fix/short-description`
- Commits: `type(scope): description` — e.g. `feat(scoring): add N/A weight exclusion`

---

## 17-day build timeline

| Day | Focus |
|---|---|
| D1 | AWS account + baseline infra. **Request Bedrock model access immediately — takes hours to days.** |
| D2 | Rubric session + label schema locked |
| D3 | Synthetic transcripts batch 1 (excellent + family-caller, 12 calls) |
| D4 | Synthetic dataset complete (all 5 scenarios, 30 calls) + S3 populated |
| D5 | CTM ingestion + webhook plumbing live |
| D6 | Scoring engine on Bedrock — first scored call end-to-end |
| D7 | **Buffer 1** |
| D8 | Internal QA — automated Pytest against gold-standard labels |
| D9 | Dashboard build part 1 |
| D10 | Dashboard build part 2 + polish |
| D11 | **Client blind grading session** — see `docs/d11-facilitation-guide.md` |
| D12 | Rubric refinement on disagreements → push rubric-v2 |
| D13 | Rescore + verify success bar (≥80% / ≥70%) |
| D14 | **Buffer 2** |
| D15 | Phase B proposal draft |
| D16 | Readout prep |
| D17 | **Joint readout + Phase B pitch** |

---

## Infra setup notes

These steps must be completed once per AWS environment before CDK stacks can be deployed.
They are not part of the normal daily build — they are environment prerequisites.

### CDK bootstrap IAM requirement (completed D3)

The `am-copilot-dev` IAM user requires a custom inline policy to run `cdk bootstrap` and
`cdk deploy`. **Do not use `AdministratorAccess`** — follow least-privilege per
`docs/security-spec.md`.

Policy name: `AMCopilot-CDK-Bootstrap-Policy`
Required actions (scoped to this account/region):
- CloudFormation: `CreateStack`, `DescribeStacks`, `DeleteStack`, `UpdateStack`, `GetTemplate`, `CreateChangeSet`, `ExecuteChangeSet`, `DescribeChangeSet`, `DeleteChangeSet`
- S3: `CreateBucket`, `PutBucketPolicy`, `PutBucketVersioning`, `PutBucketPublicAccessBlock`, `PutEncryptionConfiguration`, `GetBucketLocation`, `PutObject`, `GetObject`, `DeleteObject`, `ListBucket`
- ECR: `CreateRepository`, `DescribeRepositories`, `PutLifecyclePolicy`
- SSM: `PutParameter`, `GetParameter`, `DeleteParameter`
- IAM: `CreateRole`, `DeleteRole`, `AttachRolePolicy`, `DetachRolePolicy`, `PutRolePolicy`, `DeleteRolePolicy`, `GetRole`, `PassRole`

If the CDKToolkit stack gets stuck in `ROLLBACK_FAILED`: delete it via the CloudFormation
console (root/admin credentials), then re-run `cdk bootstrap`.

Bootstrap command:
```bash
cd infra && cdk bootstrap aws://{ACCOUNT_ID}/us-east-1 --profile am-copilot-dev
```

### Bedrock quota provisioning (new AWS accounts)

A fresh AWS account may have **all Bedrock inference quotas provisioned at 0** due to an
AWS new-account provisioning bug. This is NOT a code issue — the pipeline is correct.

Symptoms: `ValidationException: The provided model identifier is invalid` when calling
`invoke_model`, even with a valid model ID and correct cross-region inference profile.

Resolution: File an AWS Support case requesting quota increase for:
- `us-east-1` → Amazon Bedrock → Anthropic Claude Sonnet inference throughput
- Check Service Quotas console: all applied account-level values may show 0

Do not modify scoring logic to work around this. The fix is entirely on the AWS side.

---

## Open questions

| Question | Owner | Must resolve by |
|---|---|---|
| ~~What does CTM `GET /api/v1/calls/{id}` return for the transcript field?~~ **RESOLVED D3** — Two-endpoint model confirmed. See `services/ctm-integration/README.md`. | Dev | ~~D5~~ Done |

### CTM two-endpoint model (resolved)

CTM splits call data: metadata at `GET .../calls/{id}`, transcript at
`GET .../calls/{id}/transcription.json`. The `outline[]` array in the
transcription response is turn-by-turn diarized. Speaker role is determined
by `channel` number (`2=agent`, `1=caller`), not the `speaker` string.

**One Phase B verification still open:** Confirm `channel→role` mapping holds
on real treatment-center data. Mapping is isolated in `CHANNEL_TO_ROLE`
constant in `normalizer.py` for easy update. Do not block Phase A on this.

---

## Phase B — must-do before production

These items are explicitly deferred from Phase A. None of them block the D11 client
grading session. All must be resolved before any non-dev deployment or real patient data.

| # | Item | Location | Action required |
|---|---|---|---|
| 1 | **Bearer token verification** | `services/api-gateway/api_gateway/auth.py` · `require_auth()` | Currently accepts any non-empty Bearer token when bypass is off. Replace stub with real Cognito JWT verification (python-jose + JWKS endpoint). |
| 2 | **CTM channel→role mapping** | `services/ctm-integration/ctm_integration/constants.py` · `CHANNEL_TO_ROLE` | Confirm `{2: "agent", 1: "caller"}` mapping holds on real treatment-center CTM data. Mapping is isolated in one constant — update if wrong. |
| 3 | **CTM webhook HMAC-SHA256 signature** | `services/ctm-integration/ctm_integration/webhook.py` | Webhook signature verification against CTM's `X-CTM-Signature` header is not implemented. Verify the exact signing scheme from CTM docs, then add HMAC-SHA256 verification before processing any webhook payload. |
| 4 | **Bedrock quota provisioning** | AWS Service Quotas console | A fresh AWS account may have all Bedrock inference quotas at 0. File AWS Support case before any production scoring run. See "Infra setup notes → Bedrock quota provisioning" above. |

---

## Key documents (read before working on a subsystem)

| Document | Read before working on... |
|---|---|
| `docs/BRD.md` | Anything — context for every decision |
| `docs/rubric-spec.md` | Scoring engine, compliance engine, prompts |
| `docs/synthetic-data-spec.md` | Synthetic data generator |
| `docs/TSD.md` | Any backend service |
| `docs/data-architecture.md` | Database schema, S3 structure |
| `docs/prompt-library.md` | Bedrock calls, evaluation logic |
| `docs/PRD.md` | Dashboard, review console, API surface |
| `docs/ui-ux-spec.md` | Any frontend work |
| `docs/testing-plan.md` | D8 QA suite, gold-standard assertions |
| `docs/d11-facilitation-guide.md` | D11 client grading session |
| `docs/security-spec.md` | IAM, KMS, secrets, CI/CD |
