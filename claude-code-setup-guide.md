# AM Copilot — Developer Setup Guide
# How to start this project with Claude Code and VS Code

---

## What you need installed before starting

| Tool | Version | Install |
|---|---|---|
| Python | 3.12.x | https://python.org/downloads or `pyenv install 3.12` |
| Node.js | 22.x | https://nodejs.org (needed for AWS CDK only) |
| Docker Desktop | Latest | https://docker.com/products/docker-desktop |
| Git | Any recent | Pre-installed on Mac/Linux |
| AWS CLI | v2 | https://aws.amazon.com/cli |
| VS Code | Latest | https://code.visualstudio.com |
| Claude Code | Latest | `npm install -g @anthropic/claude-code` |

---

## Part 1 — Get the project onto your machine

### Step 1 — Clone the repository

```bash
git clone <your-repo-url> am-copilot
cd am-copilot
```

If you do not have a repo yet, initialise one from the project folder:

```bash
cd am-copilot
git init
git add .
git commit -m "feat: initial project structure and documentation"
```

---

### Step 2 — Create your Python virtual environment

Always use Python 3.12 specifically. Check your version first:

```bash
python3 --version
# Should say Python 3.12.x
# If not, use: python3.12 -m venv .venv
```

Create and activate the environment:

```bash
# Mac / Linux
python3.12 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt)
python -m venv .venv
.venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of your terminal prompt. You will need to run `source .venv/bin/activate` every time you open a new terminal window.

---

### Step 3 — Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Verify it worked:

```bash
python -c "import fastapi, sqlalchemy, pydantic, boto3; print('All dependencies installed')"
```

---

### Step 4 — Set up environment variables

```bash
cp .env.example .env
```

Open `.env` in VS Code and fill in:

```
AWS_PROFILE=am-copilot-dev       ← your AWS profile name
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/amcopilot_dev  ← leave as-is for local
CTM_API_KEY=                      ← get from CTM sandbox account
CTM_ACCOUNT_ID=                   ← get from CTM sandbox account
CTM_WEBHOOK_SECRET=               ← set any string for local dev
```

Leave Bedrock, SQS, and Cognito values blank for now — you will fill those in on D1 when AWS is set up.

---

### Step 5 — Start the local database

Make sure Docker Desktop is running, then:

```bash
docker compose up -d
```

Verify it started:

```bash
docker compose ps
# Should show amcopilot-db as "healthy"
```

---

### Step 6 — Set up AWS credentials locally

You need an AWS profile named `am-copilot-dev` in your local credentials file.

```bash
aws configure --profile am-copilot-dev
```

Enter:
- AWS Access Key ID: `<your key>`
- AWS Secret Access Key: `<your secret>`
- Default region: `us-east-1`
- Default output format: `json`

Verify it works:

```bash
aws sts get-caller-identity --profile am-copilot-dev
# Should return your account ID and user ARN
```

**Important — request Bedrock model access now.** This can take hours to days:

1. Go to AWS Console → Bedrock → Model access
2. Request access to: `Claude Sonnet 4.5` (Anthropic)
3. Do this on Day 1. Do not wait until you need it.

---

## Part 2 — Open in VS Code

### Step 7 — Install VS Code extensions

Open VS Code, then install these extensions (Cmd+Shift+X / Ctrl+Shift+X):

| Extension | ID | Why |
|---|---|---|
| Python | `ms-python.python` | Python language support |
| Pylance | `ms-python.vscode-pylance` | Type checking and IntelliSense |
| Ruff | `charliermarsh.ruff` | Linting and formatting |
| YAML | `redhat.vscode-yaml` | For rubric YAML files |
| Docker | `ms-azuretools.vscode-docker` | For docker-compose |
| AWS Toolkit | `amazonwebservices.aws-toolkit-vscode` | AWS resource browser |
| GitLens | `eamodio.gitlens` | Git history and blame |
| Tailwind CSS IntelliSense | `bradlc.vscode-tailwindcss` | For frontend work |

---

### Step 8 — Configure VS Code for this project

Create the VS Code settings file:

```bash
mkdir -p .vscode
```

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v", "--tb=short", "-m", "not bedrock"],
  "python.testing.cwd": "${workspaceFolder}",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true,
    ".venv": true,
    "infra/cdk.out": true
  },
  "editor.rulers": [100],
  "yaml.schemas": {
    "https://json.schemastore.org/github-workflow.json": ".github/workflows/*.yml"
  }
}
```

Create `.vscode/launch.json` (debugger configs):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI — api-gateway",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["services.api-gateway.main:app", "--reload", "--port", "8000"],
      "env": { "ENVIRONMENT": "development" },
      "envFile": "${workspaceFolder}/.env",
      "jinja": true
    },
    {
      "name": "Pytest — unit tests only",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v", "-m", "not bedrock"],
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Pytest — gold standard QA (needs Bedrock)",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/gold-standard/", "-v", "-m", "bedrock"],
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

---

### Step 9 — Open the project

```bash
# From inside the am-copilot directory
code .
```

VS Code will open. In the bottom-left corner, confirm it shows `Python 3.12.x ('.venv')` as the interpreter. If not, press `Cmd+Shift+P` → `Python: Select Interpreter` → choose `.venv/bin/python`.

---

## Part 3 — Start Claude Code

### Step 10 — Install Claude Code

```bash
npm install -g @anthropic/claude-code
```

Verify:

```bash
claude --version
```

---

### Step 11 — Authenticate Claude Code

```bash
claude login
```

This opens a browser window. Log in with your Anthropic account. Claude Code will store the credential locally.

---

### Step 12 — Open Claude Code in the project

```bash
# Make sure you are inside the project folder
cd am-copilot

# Start Claude Code
claude
```

Claude Code will:
1. Automatically read `CLAUDE.md` — the project brain
2. Load all 4 skills from `.claude/skills/`
3. Make the 2 agents from `.claude/agents/` available
4. Apply the permissions from `.claude/settings.json`

You will see the Claude Code prompt. The first message Claude sends will confirm it has read CLAUDE.md.

---

### Step 13 — Verify Claude Code has context

Type this as your first message:

```
What is this project, what stack are we using, and what should I build first?
```

Claude Code should answer with:
- AM Copilot is an AI call-scoring intelligence layer on top of CTM for behavioral-health admissions
- Python 3.12 / FastAPI / SQLAlchemy / Pydantic v2 / boto3 on the backend
- Vite / React 18 / TypeScript / Tailwind on the frontend
- First task is the synthetic transcript generator in `packages/synthetic-data/`

If Claude Code answers correctly — you are ready to build.

---

### Step 14 — Run the project verification check

Before writing any code, confirm the environment is clean:

```bash
# In a separate terminal (not the Claude Code terminal)

# 1. Activate venv
source .venv/bin/activate

# 2. Run unit tests (should all pass — no code written yet means no failures)
python -m pytest tests/ -v -m "not bedrock"
# Expected: "no tests ran" or 0 failures

# 3. Confirm database is reachable
docker compose ps
# Expected: amcopilot-db running and healthy

# 4. Confirm AWS credentials work
aws sts get-caller-identity --profile am-copilot-dev
# Expected: your account ID returned
```

---

## Part 4 — Working with Claude Code day to day

### How to give Claude Code a task

Be specific. Reference the docs. Examples:

```
# Good
Build the synthetic transcript generator in packages/synthetic-data/generate.py
following the spec in docs/synthetic-data-spec.md. Use seeded RNG with MASTER_SEED=42,
generate all 5 scenario types, 6 calls each, and output to data/synthetic/.

# Not specific enough
Build the data generator
```

```
# Good
Build the compliance engine in services/compliance-engine/rules.py.
The regex patterns are already written in docs/prompt-library.md section 5.
Port them exactly — do not invent new patterns.

# Not specific enough
Add compliance detection
```

---

### Using skills (auto-triggered)

When Claude Code is working on a subsystem, it reads the relevant SKILL.md automatically. You can also trigger one manually:

```
Read .claude/skills/scoring-engine/SKILL.md before we start on the scoring engine
```

---

### Using agents

```
# Trigger the evaluation worker agent
Use the evaluation-worker agent to run syn_001 through the full pipeline in dry-run mode

# Trigger the compliance checker agent
Use the compliance-checker agent to test the phrase "it sounds like you have a dependency problem"
```

---

### Switching between Claude Code and VS Code

Claude Code runs in the terminal. VS Code runs alongside it. The typical workflow:

1. **Claude Code** — write the code, run tests, debug
2. **VS Code** — review diffs, browse files, use the debugger, read docs side-by-side

You do not have to choose one. Keep both open. Claude Code handles the "write and run" loop. VS Code handles the "read and review" loop.

---

### Resuming after a break

Every new Claude Code session starts fresh. To restore full context:

```bash
cd am-copilot
claude
```

Then paste the continuation prompt from `am-copilot-continuation-prompt.txt` as your first message. This restores all project decisions, stack choices, and current state instantly.

---

## Part 5 — Day 1 checklist

Work through this in order on your first day:

```
□ All tools installed (Python 3.12, Node, Docker, AWS CLI, VS Code, Claude Code)
□ .env filled in with AWS profile and CTM sandbox credentials
□ docker compose up -d running and healthy
□ AWS credentials verified with: aws sts get-caller-identity
□ Bedrock model access requested in AWS Console (do this NOW — takes hours to days)
□ VS Code extensions installed
□ Claude Code authenticated and opened in project folder
□ Claude Code confirmed it read CLAUDE.md correctly (Step 13 test)
□ Unit tests passing: pytest tests/ -m "not bedrock"
□ First task given to Claude Code: synthetic transcript generator
```

---

## Common issues

**`(.venv)` not showing in terminal**
Run `source .venv/bin/activate` again. You need to do this in every new terminal window.

**`ModuleNotFoundError` when running code**
Your venv is not active or dependencies are not installed. Run:
```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
```

**`docker: Cannot connect to the Docker daemon`**
Docker Desktop is not running. Open it from your Applications folder.

**`botocore.exceptions.NoCredentialsError`**
Your AWS profile is not configured. Run:
```bash
aws configure --profile am-copilot-dev
```

**`claude: command not found`**
Claude Code is not installed or not on your PATH. Run:
```bash
npm install -g @anthropic/claude-code
# Then restart your terminal
```

**Claude Code does not seem to know the project context**
CLAUDE.md may not have loaded. Type:
```
Read CLAUDE.md and summarise the project for me
```

**Bedrock returns `AccessDeniedException`**
Model access has not been approved yet. Check the AWS Console → Bedrock → Model access. It can take up to 24 hours.
