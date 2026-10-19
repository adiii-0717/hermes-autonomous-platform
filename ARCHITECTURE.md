# SOFTWARE DEVELOPMENT AGENT PRODUCT ARCHITECTURE

> **Foundation Framework**: [Hermes Agent](https://github.com/NousResearch/hermes-agent)  
> **Product Goal**: A web-based Software Development Agent product wrapping Hermes with project management, real-time activity visibility, security boundaries, and custom engineering tools.

---

## 1. System Overview Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEVELOPER WEB INTERFACE                            │
│                                                                             │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────────────┐  │
│  │ Chat & Plan│   │ Code/Files │   │ Terminal   │   │ Real-time Activity │  │
│  └────────────┘   └────────────┘   └────────────┘   └────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ WebSocket / REST API
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OUR PRODUCT BACKEND LAYER                          │
│                                                                             │
│  ┌────────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │ User Auth & Access │  │ Project & Workspaces│ │ Approval & Permissions │  │
│  └────────────────────┘  └───────────────────┘  └────────────────────────┘  │
│  ┌────────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │ Session Controller │  │ Activity Streamer │  │ Tool Security Boundary │  │
│  └────────────────────┘  └───────────────────┘  └────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP REST / RPC / Managed Subprocess
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HERMES AGENT RUNTIME ENGINE                         │
│                                                                             │
│  ┌─────────────────────┐  ┌───────────────────┐  ┌───────────────────────┐  │
│  │ Autonomous ReAct    │  │ FTS5 Memory &     │  │ Multi-Provider Model  │  │
│  │ Agent Loop          │  │ Skill Engine      │  │ Abstraction (OpenAI,  │  │
│  │                     │  │                   │  │ Anthropic, OpenRouter)│  │
│  └─────────────────────┘  └───────────────────┘  └───────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Tool Dispatch
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CUSTOM DEVELOPMENT TOOLSET                            │
│                                                                             │
│   File Operations  │  Terminal Exec  │  Git Workflows  │  Testing & Linter  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Execution Scoping
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ISOLATED PROJECT WORKSPACE                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Responsibility Division

### Our Backend Application Owns:
- **User & Auth**: Authentication, session access controls, workspace ownership.
- **Project & Workspace Management**: Isolated workspace directory setup (`/workspaces/:id`), git repo initialization, project metadata.
- **Security Boundary & Approvals**: Intercepting high-risk tool operations (shell execution, destructive file writes) for human user approval in the Web UI.
- **Streaming Gateway**: Relaying real-time agent output tokens, thinking steps, tool invocations, and terminal streams to the Web Frontend via WebSockets.
- **UI State**: Maintaining project tabs, open file diffs, active task state, and execution history log display.

### Hermes Agent Framework Owns:
- **Agent Reasoning & Loop**: Multi-step ReAct planning, context assembly, retry loops, and error reflection.
- **Model Interaction**: Multi-provider LLM calling, prompt formatting, context compression (`ContextCompressor`).
- **Memory & Skills**: SQLite FTS5 transcript indexing, cross-session memory queries, and procedural skill generation.
- **Tool Dispatching**: Tool parameter parsing, execution dispatching, and result formatting.

---

## 3. Development Tools Layer (Hermes Tool Extensions)

Our engineering focus is building first-class development tools using Hermes' native tool extension & MCP protocols:

| Tool Module | Registered Tools | Description |
|---|---|---|
| `dev_file_tools` | `read_file`, `write_file`, `edit_file`, `search_files`, `list_directory` | Fast workspace file manipulation with line range viewing and regex ripgrep search. |
| `dev_terminal_tools` | `execute_command`, `start_background_process`, `get_process_output` | Controlled terminal shell execution with timeout guards and stdout/stderr capture. |
| `dev_testing_tools` | `run_tests`, `run_linter`, `run_build` | Native runners for pytest, npm test, cargo test, and linting suites. |
| `dev_git_tools` | `git_status`, `git_diff`, `git_commit` | Seamless version control operations with diff tracking. |

---

## 4. Security & Isolation Model

1. **Path Sandboxing**: Hermes tools are configured with explicit workspace root boundaries (`allowed_paths`). Access outside the active workspace directory is rejected by path validation middleware.
2. **Command Approvals**: Shell execution requests undergo classification. Read-only commands (`ls`, `cat`, `git status`) run automatically; mutation/destructive commands (`rm`, `git reset --hard`) pause execution and emit an Approval Event to the Web UI for developer sign-off.
