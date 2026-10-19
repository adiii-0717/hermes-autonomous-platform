# Genuine Hermes + Ollama `qwen3.5:4b` Integration Smoke Test Report

## Executive Summary

A controlled, genuine integration smoke test of the Hermes AIAgent system powered by local Ollama `qwen3.5:4b` was conducted in a fresh temporary workspace (`/private/var/folders/.../tmpir8bb8zg`). The execution strictly passed through `HermesAgentAdapter.process_user_turn()` and instantiated `run_agent.AIAgent` without using deterministic fallbacks, mocks, or external API gateways.

- **Final Classification**: **FAIL**
- **AIAgent Instantiated**: **True** (`run_agent.AIAgent` initialized with `provider="ollama"`, `model="qwen3.5:4b"`, `base_url="http://localhost:11434/v1"`)
- **Deterministic Fallback Used**: **False** (`used_deterministic_fallback = false`)
- **Execution Duration**: **264.32 seconds**
- **Root Cause**: `qwen3.5:4b` attempted tool calls using an invalid parameter name (`"file_path"` instead of `"path"`) for `write_file` and `read_file`. After encountering tool execution errors (`TypeError`), it attempted empty dictionary calls and meta-tool searches, eventually exhausting output tokens (`finish_reason='length'`) without creating `hello.py` or its unit test.

---

## Execution Instrumentation Summary

| Field | Value |
| :--- | :--- |
| `process_user_turn()` Called | **True** |
| `run_agent.AIAgent` Instantiated | **True** |
| `MODEL_PROVIDER` | `ollama` |
| `MODEL_NAME` | `qwen3.5:4b` |
| `API_BASE_URL` | `http://localhost:11434/v1` |
| `OPENAI_API_KEY` | `ollama` (non-secret placeholder) |
| Deterministic Fallback Used | **False** (`_run_autonomous_workspace_turn` bypass confirmed) |
| Total Execution Time | **264.32 seconds** |
| Tool Calls Count | **6 tool call attempts** |
| Files Created | `['.project_manifest.json']` (Workspace files: 0) |

---

## Detailed Tool Calling Trace & Parameter Analysis

| # | Tool Attempted | Arguments Provided | Tool Result / Error Message |
| :-: | :--- | :--- | :--- |
| 1 | `write_file` | `{"file_path": ".../greeting.py", "content": "def greet..."}` | `[TOOL_ERROR] TypeError: DevFileTools.write_file() got an unexpected keyword argument 'file_path'` |
| 2 | `read_file` | `{"file_path": ".../greeting.py"}` | `[TOOL_ERROR] TypeError: DevFileTools.read_file() got an unexpected keyword argument 'file_path'` |
| 3 | `write_file` | `{}` | `[TOOL_ERROR] TypeError: DevFileTools.write_file() got an unexpected keyword argument` |
| 4 | `tool_describe` | `{"name": "write_file"}` | `'write_file' is not a deferrable tool. If you see it in the tools list already, call it directly.` |
| 5 | `write_file` | `{}` | `[TOOL_ERROR] TypeError: DevFileTools.write_file() got an unexpected keyword argument` |
| 6 | `tool_search` | `{"query": "filesystem write create file text python test", "limit": 5}` | Returned 21 tool matches |
| 7 | *Loop Termination* | *N/A* | `finish_reason='length'` (Model hit max output tokens limit) |

---

## Independent Acceptance Verification

| Criteria | Requirement | Result |
| :--- | :--- | :---: |
| **1. Source File Created** | Python source file containing greeting function exists in workspace | **FAIL ❌** (0 source files created) |
| **2. Test File Created** | Unit test suite file exists in workspace | **FAIL ❌** (0 test files created) |
| **3. Test Suite Status** | Automated test suite exits with code 0 | **FAIL ❌** (No test suite to run) |
| **4. Genuine Workspace Changes** | Source code files created by agent | **FAIL ❌** |
| **5. Zero Fallback Used** | Autonomous fallback loop bypassed completely | **PASS ✓** (`used_deterministic_fallback = false`) |
| **6. AIAgent Instantiation** | `run_agent.AIAgent` genuinely executed turn | **PASS ✓** (`run_agent_aiagent_instantiated = true`) |

---

## Component Distinction & Audit

- **Genuine Qwen3.5 Model Execution**: **True** (Executed 6 turns via `http://localhost:11434/v1`).
- **Genuine Hermes AIAgent Execution**: **True** (Instantiated and orchestrated turn loop).
- **Genuine Hermes Tool Execution**: **True** (Dispatched `write_file`, `read_file`, `tool_describe`, `tool_search` to Hermes tool handlers).
- **Deterministic Fallback Execution**: **False** (`_run_autonomous_workspace_turn()` was not called).
- **Independent Acceptance Checker**: **Fail** (Source and test files were not produced).

---

## Conclusion & Classification

- **Classification**: **MODEL CAPABILITY LIMITATION**
- **Summary**: `qwen3.5:4b` successfully connects to Hermes via Ollama's OpenAI-compatible endpoint, instantiates the genuine `AIAgent`, and makes real tool calls. However, its small 4B parameter size results in tool schema hallucinations (e.g. inventing `"file_path"` instead of inspecting `"path"` in the JSON schema) and an inability to recover from tool parameter errors, causing the model to enter a loop and hit max token limits (`finish_reason='length'`).

---

## Next Steps

Since the smoke test resulted in **FAIL** due to model tool parameter hallucination, we **STOP** here and report these exact results as instructed before attempting any larger benchmark.
