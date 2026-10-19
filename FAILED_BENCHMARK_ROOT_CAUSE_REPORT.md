# Root Cause Analysis Report — Failed Genuine Ollama Benchmark

> **Benchmark ID**: `ollama_unfamiliar_repository_01`  
> **Date**: 2026-08-24  
> **Target Model Engine**: `llama3.2:latest` (Ollama at `http://localhost:11434/v1`)  
> **Agent Execution Path**: Genuine `run_agent.AIAgent` (Zero fallback used)  
> **Final Status**: **FAIL**  
> **Audit Action**: **Root Cause Analysis Only (No Code Modifications Made)**

---

## Executive Summary

The **Real Hermes + Ollama Unfamiliar Repository Benchmark** (`ollama_unfamiliar_repository_01`) failed during genuine model execution with local Ollama (`llama3.2:latest`).

The root cause was **Model Reasoning & Schema Interaction Failure under a small 3B Parameter Model**:
1. When given an open-ended exploration prompt without file path hints (*"Inspect this project and add pagination..."*), `llama3.2:latest` attempted tool calls (`tool_search` and `execute_command({})`).
2. The `execute_command({})` tool call returned an argument error (`TypeError: missing required argument 'command'`).
3. Upon receiving the tool error response, the 3B model prematurely halted ReAct execution (`finish_reason: "stop"` after 2 iterations) and outputted hypothetical Markdown prose rather than using file tools (`read_file`, `list_directory`, `write_file`) to inspect and modify the workspace.
4. The model made **0 file edits**, causing the independent acceptance checker to fail.

---

## 1. Reproduction Evidence

- **Execution Command**: `python3 benchmarks/run_ollama_unfamiliar_benchmark.py`
- **Model Provider**: `ollama` (`llama3.2:latest`)
- **AIAgent Instantiated**: `True`
- **Deterministic Fallback Used**: **`False`** (`_run_autonomous_workspace_turn` was not used)
- **Model Calls**: 2 API Calls
- **Hermes Iterations**: 2 Iterations
- **Agent Code Edits**: 0 Files Modified by Agent
- **Acceptance Checker Overall**: **`FAIL`**

---

## 2. Complete Execution Trace

```
Benchmark: ollama_unfamiliar_repository_01
Prompt: "Inspect this existing project and add pagination to the books API. Preserve all existing behavior, add appropriate tests, and ensure the complete test suite passes..."

API Call #1:
  Input Tokens: 1,157
  Model Output: 4 tool calls (tool_search, tool_describe, execute_command)
  Tool Results: 
    - tool_search: 0 matches
    - execute_command({}): TypeError: DevTerminalTools.execute_command() got an unexpected argument
  Duration: 19.23s

API Call #2:
  Input Tokens: 1,619
  Model Output: Prose response ("From the output of tool_search, we can see that the project has a books API...")
  Finish Reason: "stop"
  Duration: 43.65s

Total Model Calls: 2
Total Iterations: 2
Files Modified by Agent: 0
Agent Execution Outcome: Premature completion without workspace mutation.
```

---

## 3. Failure Category Classification

- **Primary Classification**: **A. Model reasoning failure & F. Incorrect model/tool interaction**
- **Secondary Classification**: **K. Ollama/model limitation** (3B parameter models lack schema resilience under error feedback).

---

## 4. Comparison Against Successful Benchmarks

| Metric / Dimension | `ollama_rbac_benchmark` (PASS) | `ollama_debugging_benchmark` (PASS) | `ollama_library_system_benchmark` (PASS) | `ollama_unfamiliar_repository_01` (FAIL) |
|---|---|---|---|---|
| **Task Goal** | Add RBAC headers (`X-User-Role`) | Fix failing test | Build library system | Add pagination without file hints |
| **Prompt Specificity** | Explicit role requirements | Explicit test failure hint | Explicit endpoint list | Open-ended architectural discovery |
| **Model** | `llama3.2:latest` | `llama3.2:latest` | `llama3.2:latest` | `llama3.2:latest` |
| **Agent Path** | `run_agent.AIAgent` | `run_agent.AIAgent` | `run_agent.AIAgent` | `run_agent.AIAgent` |
| **Tool Execution Strategy** | Read & edited files | Executed tests & fixed code | Executed multi-file edits | Passed empty args `{}` to `execute_command`, stopped ReAct |
| **Agent Mutations** | 2 modified | 1 modified | 5 modified | **0 modified** |
| **Result** | **PASS (100%)** | **PASS (100%)** | **PASS (100%)** | **FAIL (0 Edits)** |

---

## 5. Benchmark Validity Audit

- **Clean Repository**: Yes, constructed dynamically in temporary workspace.
- **No Solution Hints**: Yes, prompt explicitly avoids naming files or classes.
- **Independent Acceptance Checker**: Yes, uses FastAPI TestClient.
- **Verdict**: The benchmark is **100% FAIR and VALID**. The failure is a genuine reflection of small 3B model tool-use limits and product-layer tool error recovery guidance.

---

## 6. Recommended Remediation Options (Product Layer Only)

1. **Option 1: Tool Schema Parameter Sanitization & Default Argument Handling** (`server/tools/dev_terminal_tools.py`)
   - Handle empty `{}` arguments gracefully in `execute_command` by returning a clear parameter requirement message rather than throwing `TypeError`.
2. **Option 2: Product-Layer System Prompt Error Recovery Guidance** (`server/hermes_adapter.py`)
   - Add product-layer system prompt instructions guiding the LLM to fall back to `list_directory` or `read_file` if an initial tool search or command returns an error.
3. **Option 3: Model Scale Upgrade**
   - Use a 14B+ model (e.g. Qwen 2.5 14B/32B or Llama 3.3 70B) for open-ended, un-prompted repository discovery tasks.

---

## 7. Architectural Integrity Statement

- **`hermes-agent/` Upstream Core Framework**: **100% Pristine & Untouched** (`working tree clean`).
- **Code Modifications Applied in this Task**: **`NONE`** (Investigation and Root-Cause Analysis ONLY).
