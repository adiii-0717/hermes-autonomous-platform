# HERMES AGENT ARCHITECTURE & INTEGRATION ANALYSIS

> **Document Version**: 1.0  
> **Target Framework**: NousResearch/hermes-agent (Python 3.11+)  
> **Purpose**: Technical assessment of Hermes Agent capabilities, APIs, memory, tool systems, and session management to establish the core foundation for our Software Development Agent product.

---

## Executive Summary & Core Principle

**Primary Directive**: We are building a **Software Development Agent Product powered by Hermes Agent**. We will **NOT** build or reimplement an underlying agent framework from scratch.

Hermes Agent provides a production-grade, self-improving, autonomous agent loop with persistent FTS5 memory, multi-provider model abstractions, built-in tool registries, MCP support, and multi-backend execution runtimes. Our engineering effort is focused on building:
1. **The Product Layer**: Modern Web Frontend (Chat, Files, Plan, Terminal, Diff, Visual Debugger) and Backend API Orchestrator (Auth, Workspace Isolation, Security Boundary, Session Management).
2. **Software Engineering Tooling**: Specialized Hermes custom tools for file operations, terminal process management, AST code analysis, testing, linting, and Git workflows.
3. **Workspace & Security Boundary**: Isolated sandboxes (Docker/local workspace containment) and fine-grained command permission controls around Hermes execution.

---

## 1. Hermes Capabilities & Feature Matrix

| Capability Area | Built-in Hermes Functionality | Our Reuse Strategy |
|---|---|---|
| **Agent Execution Loop** | ReAct cycle, turn context management, error recovery, empty response guards, iteration budgets, reasoning reflection. | **100% Reuse** (Do not rebuild agent loop). |
| **Tool System** | 40+ built-in tools, MCP (Model Context Protocol) client/server, custom tool registry, parameter schema validation. | **Reuse Framework**, supply custom Dev Tools via MCP & Python Tool extensions. |
| **Memory System** | Persistent FTS5 full-text search, SQLite `SessionDB`, `MEMORY.md`/`USER.md`, autonomous Skill creation. | **100% Reuse** (Store project notes & skills in Hermes memory). |
| **Session & History** | `SessionStore`, `SessionEntry` state machine, auto-reset policies, SQLite turn transcript history, rewind/retry/compress commands. | **100% Reuse** (Map our backend Session IDs to Hermes session keys). |
| **Model Providers** | Native support for OpenAI, Anthropic, OpenRouter, Nous Portal, Bedrock, Vertex, Gemini, Ollama, LM Studio, vLLM. | **100% Reuse** (Pass replacement configuration to Hermes). |
| **Terminal & Execution** | Execution backends: Local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox. Process backgrounding, streaming output. | **Reuse & Sandbox** (Configure Docker / Local workspace scoping). |
| **Streaming & Events** | `plugin_stream_hooks`, Gateway stream consumers, WebSocket/Server-Sent Events streaming, token/tool-progress callbacks. | **Integrate Stream** (Bridge Hermes stream events to Frontend WebSockets). |

---

## 2. Integration Methods Evaluation

Hermes Agent can be integrated into our product through four candidate architectures:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INTEGRATION OPTIONS MATRIX                         │
├─────────────────┬──────────────────────┬──────────────────┬─────────────────┤
│ Integration Mode│ Primary Mechanism    │ Pros             │ Cons            │
├─────────────────┼──────────────────────┼──────────────────┼─────────────────┤
│ Option A        │ Direct Python        │ Lowest latency,  │ Process coupling│
│ (Library)       │ `from run_agent      │ in-memory state, │ requires Python │
│                 │  import AIAgent`     │ tight control    │ backend layer   │
├─────────────────┼──────────────────────┼──────────────────┼─────────────────┤
│ Option B        │ CLI / Subprocess     │ Process isolation│ Process overhead│
│ (Subprocess)    │ `python run_agent.py │ easy restart,    │ stdio parsing   │
│                 │  --json-stream`      │ crash containment│ complexity      │
├─────────────────┼──────────────────────┼──────────────────┼─────────────────┤
│ Option C        │ Gateway API / Service│ Out-of-proc RPC, │ Service lifecycle│
│ (Service/REST)  │ `gateway/run.py`     │ scale horizontal,│ overhead        │
│                 │ HTTP/WS Port 8642    │ standard OpenAI  │                 │
│                 │                      │ compatible endpoints│              │
├─────────────────┼──────────────────────┼──────────────────┼─────────────────┤
│ Option D        │ ACP / MCP Server     │ Standard protocol│ Extra translation│
│ (MCP/ACP)       │ `mcp_serve.py`       │ multi-agent ecosystem layer        │
└─────────────────┴──────────────────────┴──────────────────┴─────────────────┘
```

### Recommendation for Our Product: **Hybrid Service / Gateway (Option C) + Direct SDK Hook (Option A)**

1. **Backend Orchestrator**: Runs Hermes Agent Gateway as a managed sidecar service (`gateway/run.py` or `hermes gateway`).
2. **API Communication**: Our FastAPI/Node backend communicates with Hermes over HTTP REST & WebSockets for bidirectional event streaming, session management, and approval handling.
3. **Execution Isolation**: Each user project workspace is mounted as an isolated target directory for Hermes' execution backends.

---

## 3. Tool Registration & Development Tool Architecture

Hermes provides a clean, modular tool extension framework in `tools/registry.py` and `tools/mcp_tool.py`.

### How Tools Work in Hermes
- **Native Python Tools**: Registered with `@register_tool` or class-based definitions defining JSON schema signatures, docstrings, and execution handlers.
- **MCP Integration**: Any MCP (Model Context Protocol) server (Stdio or SSE) can be plugged into Hermes via configuration (`cli-config.yaml` or environment).
- **Skills System**: Procedural memory (`skills/` directory adhering to `agentskills.io` standard) providing workflow instructions dynamically injected into system prompts when requested.

### Development Tools to Build for Hermes
We will implement specialized software development tools using Hermes' native tool registry / MCP server format:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 OUR CUSTOM DEVELOPMENT TOOLS FOR HERMES                      │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ Tool Category     │ Planned Tools                                           │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ File System       │ `read_file`, `write_file`, `edit_file` (diff-based),    │
│                   │ `search_files` (ripgrep), `list_directory`, `file_tree` │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Terminal & Exec   │ `execute_command`, `start_background_process`,          │
│                   │ `get_process_output`, `kill_process`                    │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Code & Quality    │ `run_tests` (pytest/jest/vitest), `run_linter`,         │
│                   │ `run_build`, `analyze_ast`                              │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Version Control   │ `git_status`, `git_diff`, `git_commit`, `git_checkout`  │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ Project Context   │ `get_project_structure`, `read_symbol_definition`       │
└───────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 4. Session & State Management

Hermes manages sessions via `gateway/session.py` and SQLite `SessionDB`:

- **Session Identification**: `session_key` deterministically generated from `(platform, chat_id, thread_id)`.
- **Session Metadata**: `SessionEntry` tracks active tokens, USD cost estimates, last prompt tokens, and lifecycle state flags (`suspended`, `resume_pending`, `is_fresh_reset`).
- **Transcript Persistence**: Transcripts are saved in SQLite (`SessionDB`). Full rewind (`rewind_session`), retry (`/retry`), and context compaction (`/compress`) are handled transparently.
- **Integration Mapping**: Our backend maps `ProjectWorkspace ID + User Session ID` directly into Hermes `session_key`.

---

## 5. Memory System & Learning Loop

Hermes possesses an advanced 3-tier memory system:
1. **Short-Term Context**: Managed by `ContextCompressor` with prompt caching and token budgeting.
2. **Long-Term Full-Text Search**: SQLite FTS5 search across all past session transcripts, allowing natural language queries for historical decisions.
3. **Procedural Memory (Skills & Rules)**:
   - `MEMORY.md` and `USER.md` profile files.
   - Autonomous skill crystallization: After completing complex multi-step tasks, Hermes distills successful workflows into `.md` skill files in `~/.hermes/skills/`.

---

## 6. Model Integration & Configuration

Hermes abstracts model interactions via `agent/model_metadata.py` and provider adapters.

Configuration is entirely dynamic:
```yaml
model:
  provider: "openrouter" # openrouter, openai, anthropic, portal, local, etc.
  name: "anthropic/claude-3.5-sonnet"
  api_base: "https://openrouter.ai/api/v1"
  api_key: "${OPENROUTER_API_KEY}"
```
Switching models requires zero code changes. Our backend will pass project-configured model settings directly to the Hermes runtime.

---

## 7. Security & Sandboxing Boundary

Hermes includes `tools/approval.py` and `tools/path_security.py` for permission checking. In our application product:

```text
  USER REQUEST
       │
       ▼
 ┌───────────┐      Approved      ┌─────────────────┐
 │ OUR BACKEND│ ─────────────────►│ HERMES RUNTIME  │
 │ SECURITY  │                    │ (Isolated       │
 │ BOUNDARY  │◄─────────────────  │  Workspace)     │
 └───────────┘ Require Approval   └─────────────────┘
```

1. **Workspace Containment**: Hermes' root directory is restricted to `/workspaces/{project_id}`.
2. **Command Allowlist & Human-in-the-Loop**: Potentially destructive terminal commands (e.g. `rm -rf`, `git push --force`) trigger approval requests back through our Backend to the Web UI.

---

## 8. Functionality We Will NOT Rebuild

To comply with the primary requirement, we explicitly declare **NO REINVENTION** of the following core components:

| Component | Status | Decision Rationale |
|---|---|---|
| Agent ReAct Loop | **DO NOT BUILD** | Reused from Hermes `run_agent.py` & `conversation_loop.py`. |
| LLM Provider Wrappers | **DO NOT BUILD** | Reused from Hermes `agent/` adapters. |
| Tool Dispatch & Registry | **DO NOT BUILD** | Reused from Hermes `tools/registry.py`. |
| FTS5 Memory & Search | **DO NOT BUILD** | Reused from Hermes `hermes_state_search.py` & `memory_manager.py`. |
| Transcript Logging | **DO NOT BUILD** | Reused from Hermes SQLite `SessionDB`. |
| Context Compactor | **DO NOT BUILD** | Reused from Hermes `context_compressor.py`. |

---

## 9. Next Steps & Development Roadmap

1. **Phase 1**: Initialize our product repository structure with UI, Backend API Layer, and Hermes sidecar integration harness.
2. **Phase 2**: Implement the Hermes sidecar adapter and bridge WebSocket streaming to the Web Frontend.
3. **Phase 3**: Build high-quality development tools (`file_tools`, `terminal_tool`, `git_tools`, `test_tools`) into Hermes.
4. **Phase 4**: Add workspace sandboxing and permission approval management.
