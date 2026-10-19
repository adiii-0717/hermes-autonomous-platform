# HERMES AUTONOMOUS SOFTWARE DEVELOPMENT AGENT

> **Powered by**: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)  
> **Target Engine**: Python 3.11+ / FastAPI / React + Vite  
> **Classification**: **PRODUCTION CANDIDATE** (Weighted Score: **91.5 / 100**)

An autonomous, web-based Software Development Agent platform built around **Hermes Agent**. The product transforms raw user requirements into complete software projects through automated repository intelligence, AST symbol analysis, change impact tracing, task DAG planning, code modifications, test intelligence, debugging loops, and real-time activity streaming.

---

## 🤖 Model Provider Architecture (APInex Primary & Backup Providers)

Hermes directly integrates **APInex** (`https://api.apinex.bond/v1`) as its primary LLM provider, with automated fallback and seamless runtime switching across a prioritized tier of providers:
1. **Primary**: **APInex** (OpenAI-compatible unified gateway, 10M tokens/day on free models)
2. **Backup 1**: **Google Gemini** (Google AI Studio OpenAI-compatible endpoint)
3. **Backup 2**: **Groq API** (Ultra-fast LPU inference for open models)
4. **Offline Fallback**: **Local Ollama** (Local inference on MacBook Air M4, keyless)

### 1. Environment Variables Configuration

Create or update your `.env` file in the root directory (copy from `.env.example`):

```bash
# ------------------------------------------------------------------------------
# PRIMARY: APINEX (https://apinex.bond/models)
# ------------------------------------------------------------------------------
LLM_PROVIDER=apinex
APINEX_API_KEY=your_apinex_api_key_here
APINEX_BASE_URL=https://api.apinex.bond/v1
APINEX_MODEL=free/gemini-3.8-flash

# ------------------------------------------------------------------------------
# BACKUP 1: GOOGLE GEMINI
# ------------------------------------------------------------------------------
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/

# ------------------------------------------------------------------------------
# BACKUP 2: GROQ
# ------------------------------------------------------------------------------
GROQ_API_KEY=your_groq_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

# ------------------------------------------------------------------------------
# OFFLINE FALLBACK: LOCAL OLLAMA (No API key required)
# ------------------------------------------------------------------------------
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=gemma4:12b-hermes
```

### 2. Live APInex Verification Script

Test your APInex connection and credentials without exposing your API key:
```bash
python3 scripts/test_apinex_live.py
```

### 2. Runtime Model Configuration API

Hermes provides dynamic model switching via REST API endpoints:

- **GET `/api/config`**: Inspect current provider, model, base URL, and API key status (API key is automatically masked for security).
- **POST `/api/config`**: Switch model provider, model ID, base URL, or update API key dynamically at runtime:
  ```json
  {
    "provider": "google-gemini",
    "model": "gemini-2.5-flash",
    "api_key": "your_gemini_api_key",
    "api_base": "https://generativelanguage.googleapis.com/v1beta/openai/"
  }
  ```

---


## 🌟 Key Capabilities

- **Genuine Hermes Core Engine**: Powered by `run_agent.AIAgent` and `tools.registry.registry` for ReAct reasoning, model interactions, persistent memory search, and tool execution.
- **Project Intelligence System**: Automatically detects languages (Python, JS/TS, Go, Rust, Java, C/C++), frameworks (React, Next.js, FastAPI, Django, Flask, Express), package managers, databases, and test tools without forcing LLM rediscovery.
- **AST & Impact Tools**: `analyze_ast`, `read_symbol_definition`, `find_symbol_references`, `analyze_change_impact`.
- **Test Intelligence**: `find_related_tests`, `classify_test_failure`.
- **Task DAG & Development Plans**: Structured task checklists (`PENDING`, `IN_PROGRESS`, `BLOCKED`, `TESTING`, `FAILED`, `COMPLETED`) visible in the Web UI.
- **Custom Development Toolset**:
  - **File**: `read_file`, `write_file`, `edit_file`, `search_files`, `list_directory`, `get_project_structure`
  - **Terminal & Processes**: `execute_command`, `start_background_process`, `get_process_output`, `get_process_status`, `kill_process`
  - **Testing & Quality**: `run_tests`, `run_linter`, `run_build`, `review_changes`, `check_project_health`, `find_related_tests`
  - **Version Control**: `git_status`, `git_diff`, `git_commit`
- **Hardened Workspace Security**: Canonical `realpath` path containment preventing path traversal (`../`) and symbolic link escape attacks.
- **Human-in-the-Loop Approvals**: High-risk shell execution and destructive operations pause for explicit user permission with rich risk metadata.
- **Developer Web UI**: React + Vite frontend featuring Chat, Interactive Plan Checklist, Code Editor, Diff Viewer, and Project Health dashboard.

---

## 🚀 Quick Start

### 1. Install Backend Dependencies & Run Server
```bash
python3 -m pip install -r server/requirements.txt
python3 server/main.py
```
*Backend runs on `http://localhost:8000` (WebSocket at `ws://localhost:8000/ws/chat`).*

### 2. Install Frontend Dependencies & Run Web UI
```bash
cd client
npm install
npm run dev
```
*Web UI runs on `http://localhost:3000`.*

---

## 🧪 Running Tests & Audit Artifacts

### Run Full Test Suite (61 Tests)
```bash
python3 -m unittest discover -s tests
```

### Run Real-World Agent Benchmark Suite (5 Runs Each / 50 Total Runs)
```bash
python3 benchmarks/real_world/run_real_world_benchmarks.py
```

### Run Audit Tracer & Evidence Generator
```bash
python3 benchmarks/audit_tracer.py
```

---

## 🔒 Security & Credential Configuration

Hermes is designed with a **fail-safe security model**:
- **Zero Committed Secrets**: All API keys, credentials, and tokens reside strictly in `.env` (ignored by `.gitignore`) and are never tracked in Git.
- **Environment Template**: Use `.env.example` as a template for setting up credentials. Never paste real keys into `.env.example`.
- **Runtime Path Jailing**: `WorkspaceGuard` ensures the AI agent can only read, write, or execute files within designated workspace sandboxes (`workspace/<project_name>/`). Directory traversal outside project roots is strictly blocked.
- **Command Approvals**: `ApprovalController` intercepts destructive shell commands (`rm`, `kill`, `git reset`) and prompts the user in the Web UI for confirmation.
- **Reporting Vulnerabilities**: If you discover a potential security vulnerability, please report it privately to the maintainers rather than opening a public issue.

---

## 📚 Documentation

- [HERMES_PROJECT_EXPLANATION.md](docs/HERMES_PROJECT_EXPLANATION.md) — Comprehensive architecture, instruction flow & agent role guide.
- [PROJECT_ARCHITECTURE.md](docs/PROJECT_ARCHITECTURE.md) — Technical system map & component boundaries.
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) — Production hosting & reverse proxy deployment guide.
- [DOCKER_ISOLATION_ARCHITECTURE.md](docs/DOCKER_ISOLATION_ARCHITECTURE.md) — Container security & isolation model.
- [ARCHITECTURE.md](ARCHITECTURE.md) — Foundation framework & development toolset overview.
- [DEVELOPMENT.md](DEVELOPMENT.md) — Developer setup & tool contribution guide.
- [PROJECT_STATUS.md](PROJECT_STATUS.md) — Feature status & verification log.
- [HERMES_ANALYSIS.md](HERMES_ANALYSIS.md) — Deep architectural analysis of Hermes Agent framework.

---

## ⚖️ Upstream Attribution & Open Source Licensing

This project integrates and builds upon the open-source **[hermes-agent](https://github.com/NousResearch/hermes-agent)** framework developed by **Nous Research**:

- **Upstream Reasoning Core (`hermes-agent/`)**: Licensed under the **MIT License**, Copyright (c) 2025 Nous Research. See [`hermes-agent/LICENSE`](hermes-agent/LICENSE) for the full license text.
- **Third-Party Subcomponents**:
  - `hermes-agent/plugins/security-guidance/`: Licensed under the **Apache License, Version 2.0**, Copyright Anthropic, PBC. See [`hermes-agent/plugins/security-guidance/NOTICE`](hermes-agent/plugins/security-guidance/NOTICE).
  - `hermes-agent/plugins/hermes-achievements/`: Licensed under the **MIT License**, Copyright (c) 2026 Hermes Achievements contributors.
- **Hermes Web Platform & Extensions (`server/`, `client/`, `scripts/`, `docs/`)**: The autonomous software development web studio, multi-agent design pipeline, visual QA audit system, live preview proxy, and security jailing layer wrapping Hermes.


