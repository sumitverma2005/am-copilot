# Technical Specification Document (TSD)
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Stack

### Backend
| Component | Choice | Version | Reason |
|---|---|---|---|
| Language | Python | 3.12 | Mature ML/AI ecosystem, team alignment |
| API framework | FastAPI | Latest stable | Async, native Pydantic, auto OpenAPI docs |
| ORM | SQLAlchemy | 2.x | Industry standard, async support |
| Migrations | Alembic | Latest stable | Required alongside SQLAlchemy |
| Validation | Pydantic | v2 | FastAPI native, fast, strict typing |
| AWS SDK | boto3 | Latest stable | Only SDK for Bedrock + AWS services |
| Testing | Pytest | Latest stable | Industry standard |

### Frontend
| Component | Choice | Version | Reason |
|---|---|---|---|
| Build tool | Vite | Latest stable | Fast builds, simple config, no SSR overhead |
| Framework | React | 18 | Component model, team familiarity |
| Language | TypeScript | 5 | Type safety for team handoff |
| Styling | Tailwind CSS | 4 | Fast consistent UI, no CSS conflicts |
| Charts | Recharts | Latest stable | Simplest React chart library, good enough |

### Infrastructure
| Service | Purpose |
|---|---|
| AWS CDK (TypeScript) | Infrastructure as code |
| ECS Fargate | Backend container hosting |
| API Gateway | HTTP entrypoint, rate limiting |
| SQS | Evaluation job queue, decouples webhook from processing |
| RDS PostgreSQL 16 | Derived data store |
| S3 | Synthetic dataset, evaluation artifacts |
| Amazon Bedrock | Claude Sonnet 4.5 — call evaluation |
| Cognito | Auth (user pool + JWT) |
| KMS | Encryption at rest for RDS and S3 |
| Secrets Manager | All credentials and API keys |
| CloudWatch | Logs, metrics, alarms |
| CloudTrail | API audit trail |
| IAM + Identity Center | Least-privilege roles |
| Route53 + CloudFront | DNS and CDN for Vite frontend |

**Region:** us-east-1

---

## 2. Evaluation pipeline

This is the core of the system. Do not shortcut it.

```
CTM Webhook Event
       ↓
  API Gateway          ← validates webhook signature
       ↓
    SQS Queue          ← decouples ingestion from processing
       ↓
Evaluation Worker      ← SQS consumer (ECS Fargate)
       ↓
Transcript Retrieval   ← fetches from CTM API, never stored long-term
       ↓
  Normalization        ← speaker diarization, timestamp alignment, turn numbering
       ↓
Signal Extraction      ← keyword signals, urgency indicators, compliance triggers
       ↓
 Compliance Pass       ← DETERMINISTIC: regex + rules (before LLM)
       ↓
Dimension Evaluation   ← Bedrock / Claude Sonnet 4.5 per rubric
       ↓
Score Arbitration      ← applies weights, N/A exclusion, compliance override
       ↓
Evidence Generation    ← span extraction, timestamp anchoring, coaching suggestions
       ↓
Confidence Calculation ← per-dimension and overall confidence scores
       ↓
 Manager Summary       ← human-readable summary paragraph
       ↓
   Persistence         ← scores + evidence anchors → RDS (no transcript stored)
```

**Critical rule:** Compliance pass runs BEFORE the LLM evaluation. Deterministic rules
detect violations. The LLM provides contextual reasoning for the evidence record, but
cannot override a deterministic compliance flag.

---

## 3. Service breakdown

### 3.1 `services/api-gateway`
FastAPI application. Entry point for all HTTP traffic.

Responsibilities:
- Receive CTM webhooks → validate signature → publish to SQS
- Serve dashboard API endpoints (see PRD section 6)
- Cognito JWT validation middleware
- Request/response logging to CloudWatch

Key files:
```
services/api-gateway/
├── main.py              # FastAPI app, router registration
├── routers/
│   ├── calls.py         # /calls endpoints
│   ├── queues.py        # /queue/coaching, /queue/compliance
│   ├── disagreements.py # /disagreements
│   └── webhooks.py      # CTM webhook receiver
├── middleware/
│   └── auth.py          # Cognito JWT validation
├── models/              # Pydantic request/response models
└── tests/
```

### 3.2 `services/ctm-integration`
CTM API client and webhook ingestion.

Responsibilities:
- Fetch transcripts from CTM API given a call_id
- Normalise CTM webhook payloads to internal event schema
- Retry logic with exponential backoff
- Replay support — re-fetch transcript for any historical call_id

Key files:
```
services/ctm-integration/
├── client.py            # CTM REST API client (boto3 for AWS, httpx for CTM)
├── normalizer.py        # Webhook payload → internal event schema
├── transcript.py        # Transcript fetch + normalization
└── tests/
```

### 3.3 `services/scoring-engine`
Bedrock evaluation. The AI scoring layer.

Responsibilities:
- Load rubric from `data/rubric/rubric-v{n}.yaml`
- Construct evaluation prompt from transcript + rubric
- Call Bedrock (Claude Sonnet 4.5)
- Parse structured score output
- Apply N/A handling — excluded dimensions do not contribute to weighted average
- Apply score arbitration — weights, compliance override

Key files:
```
services/scoring-engine/
├── scorer.py            # Main scoring orchestrator
├── bedrock_client.py    # boto3 Bedrock wrapper, retry logic
├── rubric_loader.py     # Loads and validates rubric YAML
├── score_arbitrator.py  # Weighted average, N/A exclusion, compliance override
└── tests/
```

### 3.4 `services/compliance-engine`
Deterministic compliance detection. Runs before LLM.

Responsibilities:
- Regex-based prohibited phrase detection
- Severity mapping (which violations are score-0 vs warnings)
- Escalation rules (suicidal ideation, overdose → immediate flag)
- Returns structured compliance result before scoring engine calls Bedrock

Key files:
```
services/compliance-engine/
├── detector.py          # Main compliance detection orchestrator
├── rules.py             # Rule definitions (phrases, patterns, severity)
├── escalation.py        # Crisis escalation detection
└── tests/
```

### 3.5 `services/evidence-engine`
Explainability layer. Every score needs evidence.

Responsibilities:
- Extract transcript spans that support each dimension score
- Anchor evidence to timestamps
- Generate coaching recommendation per dimension
- Rank evidence snippets by relevance (1–3 per dimension)
- Assign confidence score per dimension

Key files:
```
services/evidence-engine/
├── extractor.py         # Transcript span extraction
├── anchor.py            # Timestamp anchoring
├── coaching.py          # Coaching suggestion generation
├── ranker.py            # Evidence relevance ranking
├── confidence.py        # Confidence scoring
└── tests/
```

### 3.6 `services/evaluation-worker`
SQS consumer. Orchestrates the full pipeline.

Responsibilities:
- Poll SQS for evaluation jobs
- Coordinate pipeline: ctm-integration → compliance-engine → scoring-engine → evidence-engine
- Handle failures — dead letter queue, retry count, CloudWatch alarm on DLQ depth
- Idempotent processing — duplicate SQS messages do not create duplicate evaluations
- Write final evaluation record to RDS

Key files:
```
services/evaluation-worker/
├── worker.py            # SQS polling loop
├── pipeline.py          # Pipeline orchestration
├── idempotency.py       # Duplicate detection
└── tests/
```

### 3.7 `services/notification-service`
Manager alerts. Minimal in Phase A.

Phase A scope: CloudWatch alarm → SNS → email when a compliance violation is detected.
Real-time alerting is Phase D scope.

---

## 4. Database schema

**Rule:** Never store full transcripts. Store derived data only.

### Tables

```sql
-- Core evaluation record
CREATE TABLE evaluations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id         VARCHAR(255) NOT NULL UNIQUE,
    agent_id        VARCHAR(255),
    call_timestamp  TIMESTAMPTZ NOT NULL,
    duration_seconds INTEGER,
    scenario_type   VARCHAR(50),             -- synthetic only: scenario tag
    rubric_version  VARCHAR(20) NOT NULL,    -- e.g. 'rubric-v1'
    prompt_version  VARCHAR(20) NOT NULL,    -- e.g. 'prompt-v1'
    model_id        VARCHAR(100) NOT NULL,   -- e.g. 'claude-sonnet-4-5'
    overall_score   NUMERIC(5,2),
    compliance_override_triggered BOOLEAN DEFAULT FALSE,
    confidence_overall NUMERIC(4,3),         -- 0.000 to 1.000
    status          VARCHAR(50) DEFAULT 'scored',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Per-dimension scores
CREATE TABLE dimension_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id   UUID REFERENCES evaluations(id) ON DELETE CASCADE,
    dimension       VARCHAR(50) NOT NULL,    -- e.g. 'empathy_rapport'
    raw_score       SMALLINT,               -- 0–5, NULL = N/A
    weighted_score  NUMERIC(5,2),
    weight          NUMERIC(3,1) NOT NULL,
    confidence      NUMERIC(4,3),
    ai_rationale    TEXT,
    coaching_note   TEXT,
    is_na           BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Evidence anchors (replaces full transcript storage)
CREATE TABLE evidence_anchors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id   UUID REFERENCES evaluations(id) ON DELETE CASCADE,
    dimension       VARCHAR(50) NOT NULL,
    turn_number     INTEGER NOT NULL,
    timestamp_seconds INTEGER NOT NULL,
    speaker         VARCHAR(20) NOT NULL,   -- 'agent' or 'caller'
    text_snippet    TEXT NOT NULL,          -- the quoted span (short)
    relevance_rank  SMALLINT NOT NULL,      -- 1 = most relevant
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Compliance flags
CREATE TABLE compliance_flags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id   UUID REFERENCES evaluations(id) ON DELETE CASCADE,
    flag_code       VARCHAR(50) NOT NULL,   -- e.g. 'DIAG_CLAIM'
    matched_phrase  TEXT NOT NULL,
    turn_number     INTEGER NOT NULL,
    timestamp_seconds INTEGER NOT NULL,
    severity        VARCHAR(20) NOT NULL,   -- 'critical', 'warning'
    reviewed        BOOLEAN DEFAULT FALSE,
    reviewed_by     VARCHAR(255),
    reviewed_at     TIMESTAMPTZ,
    review_comment  TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Manager overrides
CREATE TABLE score_overrides (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id   UUID REFERENCES evaluations(id) ON DELETE CASCADE,
    dimension       VARCHAR(50) NOT NULL,
    ai_score        SMALLINT,
    manager_score   SMALLINT,
    manager_comment TEXT NOT NULL,
    overridden_by   VARCHAR(255) NOT NULL,
    overridden_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Coaching queue status
CREATE TABLE coaching_queue (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id   UUID REFERENCES evaluations(id) ON DELETE CASCADE UNIQUE,
    coached         BOOLEAN DEFAULT FALSE,
    coached_by      VARCHAR(255),
    coached_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes
```sql
CREATE INDEX idx_evaluations_call_id ON evaluations(call_id);
CREATE INDEX idx_evaluations_status ON evaluations(status);
CREATE INDEX idx_evaluations_overall_score ON evaluations(overall_score);
CREATE INDEX idx_dimension_scores_evaluation_id ON dimension_scores(evaluation_id);
CREATE INDEX idx_evidence_anchors_evaluation_id ON evidence_anchors(evaluation_id);
CREATE INDEX idx_compliance_flags_reviewed ON compliance_flags(reviewed);
CREATE INDEX idx_coaching_queue_coached ON coaching_queue(coached);
```

---

## 5. Bedrock integration

**Model:** `claude-sonnet-4-5` (via `amazon.claude-sonnet-4-5-20251001-v1:0` ARN)

**Request Bedrock model access on D1.** Approval can take hours to days.

```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def evaluate_call(transcript: str, rubric: dict, prompt_version: str) -> dict:
    prompt = build_evaluation_prompt(transcript, rubric)

    response = bedrock.invoke_model(
        modelId='amazon.claude-sonnet-4-5-20251001-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4096,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }),
        contentType='application/json',
        accept='application/json'
    )

    result = json.loads(response['body'].read())
    return parse_evaluation_response(result['content'][0]['text'])
```

**Retry logic:** Exponential backoff on `ThrottlingException` and `ServiceUnavailableException`.
Max 3 retries. Log all retries to CloudWatch.

**Token budget:** Max 4096 output tokens per evaluation. If a transcript exceeds 60,000
input tokens, chunk and evaluate in sections.

---

## 6. Prompt versioning

Every prompt has:
- A version identifier stored in the evaluation record
- A corresponding file in `packages/prompt-library/`
- An immutable history — never edit a prompt in place, always create a new version

See `docs/prompt-library.md` for all prompt definitions.

---

## 7. Environment variables

All secrets via AWS Secrets Manager in deployed environments.
Local dev uses `.env` (gitignored, never committed).

```bash
# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=xxxxxxxxxxxx

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/amcopilot

# CTM
CTM_API_KEY=<from Secrets Manager>
CTM_ACCOUNT_ID=<sandbox sub-account ID>
CTM_WEBHOOK_SECRET=<for signature validation>

# Bedrock
BEDROCK_MODEL_ID=amazon.claude-sonnet-4-5-20251001-v1:0

# SQS
EVALUATION_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/xxx/am-copilot-evaluation

# Auth
COGNITO_USER_POOL_ID=us-east-1_xxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx

# App
RUBRIC_VERSION=rubric-v1
PROMPT_VERSION=prompt-v1
COACHING_QUEUE_THRESHOLD=70
LOW_CONFIDENCE_THRESHOLD=0.65
```

---

## 8. CI/CD

- GitHub Actions
- OIDC auth to AWS — no long-lived AWS credentials in GitHub secrets
- On push to `main`: run Pytest → build Docker image → push to ECR → deploy to ECS
- On PR: run Pytest only
- CDK deploy is manual (developer runs `cdk deploy` from local with appropriate role)
