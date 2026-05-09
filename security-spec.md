# Security & Compliance Specification
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Phase A posture: outside the HIPAA boundary

Phase A uses synthetic data only. No real patient data. No PHI. No BAA required.

This is the entire reason Phase A can ship in 17 working days. The system and pipeline
are production-shaped — only the data is fictional.

**What this means for the developer:**
- No HIPAA technical safeguards are required during Phase A
- The security controls below are best-practice infrastructure security, not HIPAA compliance
- Full HIPAA safeguards are Phase B scope — documented in the Phase B proposal

---

## 2. Secrets management

**Rule: Zero hardcoded credentials anywhere.**

| Where | What |
|---|---|
| All deployed environments | AWS Secrets Manager |
| Local development | `.env` file (gitignored, never committed) |
| CI/CD | GitHub OIDC → AWS role assumption (no stored secrets) |
| Code | Never — any credential in code is a blocker |

### Secrets inventory

```
/am-copilot/dev/
├── ctm-api-key
├── ctm-webhook-secret
├── database-url
└── cognito-client-secret
```

Accessed at runtime via boto3:
```python
import boto3
import json

def get_secret(secret_name: str) -> str:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

---

## 3. IAM — least privilege

### Principles
- Every service gets its own IAM role
- Roles have minimum permissions required for that service's function
- No `*` actions on any role
- No `AdministratorAccess` on any service role

### Role definitions

**Evaluation worker role:**
```json
{
  "Effect": "Allow",
  "Action": [
    "sqs:ReceiveMessage",
    "sqs:DeleteMessage",
    "sqs:GetQueueAttributes",
    "bedrock:InvokeModel",
    "s3:GetObject",
    "secretsmanager:GetSecretValue",
    "kms:Decrypt"
  ],
  "Resource": [
    "arn:aws:sqs:us-east-1:ACCOUNT:am-copilot-evaluation",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.claude-sonnet-4-5-*",
    "arn:aws:s3:::am-copilot-dev/synthetic/*",
    "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:/am-copilot/*",
    "arn:aws:kms:us-east-1:ACCOUNT:key/KEY_ID"
  ]
}
```

**API gateway role:**
```json
{
  "Effect": "Allow",
  "Action": [
    "sqs:SendMessage",
    "secretsmanager:GetSecretValue",
    "kms:Decrypt"
  ],
  "Resource": [...]
}
```

### CI/CD — OIDC (no long-lived credentials)

```yaml
# .github/workflows/deploy.yml (excerpt)
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT:role/am-copilot-github-actions
    aws-region: us-east-1
```

GitHub OIDC trust policy on the role allows GitHub Actions to assume it for the
`am-copilot` repository only. No AWS access keys stored in GitHub secrets.

---

## 4. Encryption

| At rest | Mechanism |
|---|---|
| RDS PostgreSQL | KMS-managed key (aws/rds or customer-managed) |
| S3 buckets | SSE-KMS, same key |
| Secrets Manager | KMS-managed by default |

| In transit | Mechanism |
|---|---|
| All API traffic | TLS 1.2+ via API Gateway / CloudFront |
| Database connections | SSL enforced (sslmode=require in connection string) |
| Bedrock calls | HTTPS only via boto3 |
| CTM API calls | HTTPS only |

---

## 5. Network isolation

- RDS has no public endpoint — accessible only from VPC
- ECS tasks run in private subnets
- API Gateway is the only public-facing endpoint
- S3 bucket has `BlockPublicAcls: true` and `BlockPublicPolicy: true`
- No security group has `0.0.0.0/0` on any port other than 443 (API Gateway handles this)

---

## 6. Audit trail

- CloudTrail enabled in us-east-1 — logs all AWS API calls
- CloudWatch Logs retention: 30 days for Phase A
- All score overrides attributed to authenticated user (Cognito user ID) and timestamped
- Compliance flag reviews attributed and timestamped

---

## 7. Authentication

- Cognito User Pool for the dashboard
- JWT tokens validated on every API request via middleware in FastAPI
- Token expiry: 1 hour access token, 30 days refresh token
- Phase A: single user (Alyssa) + developer accounts only

---

## 8. What NOT to implement in Phase A

These are Phase B items. Do not build them now:

- 42 CFR Part 2 compliance controls
- Formal risk analysis documentation
- Workforce training records
- Incident response plan
- Business Associate Agreement workflows
- Data retention and destruction policies
- Audit log integrity controls (WORM)
- PHI access controls and audit reports

---

## 9. Developer checklist before D1 deploy

- [ ] `.env` is in `.gitignore` — verify before first commit
- [ ] All secrets are in Secrets Manager — none in code or environment config files
- [ ] S3 bucket public access is blocked
- [ ] RDS has no public endpoint
- [ ] IAM roles use least privilege — no `*` actions
- [ ] CloudTrail is enabled
- [ ] GitHub OIDC role is configured — no AWS_ACCESS_KEY_ID in GitHub secrets
- [ ] Bedrock model access has been requested (can take hours to days)
