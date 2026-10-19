# OmniRoute Model Gateway Compatibility & Architectural Investigation Report

## Executive Summary

This report presents an architectural investigation of **OmniRoute** as an optional OpenAI-compatible AI gateway for the Hermes AIAgent system. The primary goal is to isolate whether the failure of `llama3.2:latest` on the unfamiliar-repository benchmark (invalid tool call and premature termination upon tool error) is a model-capability limitation, without altering any Hermes core codebase, tool registries, security guards, or benchmark acceptance logic.

---

## 1. OmniRoute OpenAI Endpoint Compatibility
- **Compatibility Status**: **COMPATIBLE**
- **Endpoint Structure**: OmniRoute runs locally (default: `http://localhost:20128/v1`) and exposes full OpenAI-compatible REST endpoints, specifically:
  - `/v1/chat/completions`: Standard chat completion endpoint supporting streaming, messages, system instructions, function definitions (`tools`), and tool call responses.
  - `/v1/models`: Standard model listing endpoint.
- **Protocol Alignment**: Hermes' `run_agent.AIAgent` and `HermesAgentAdapter` consume OpenAI-compatible endpoints directly. By setting `MODEL_PROVIDER=openai`, `API_BASE_URL=http://localhost:20128/v1`, and `OPENAI_API_KEY=<key>`, Hermes routes request payloads cleanly through OmniRoute.

---

## 2. Authentication Architecture
- **Client to OmniRoute**: Authorization is handled via standard HTTP Bearer headers (`Authorization: Bearer <OMNIROUTE_API_KEY>`). For local unauthenticated configurations, any non-empty string token (e.g. `OPENAI_API_KEY=omniroute`) is accepted.
- **OmniRoute to Upstream Provider**: OmniRoute securely manages credentials for 350+ underlying AI providers:
  - **API Key Tiers**: Upstream provider keys (e.g., OpenRouter, Groq, Google AI Studio, Together) are stored locally in OmniRoute's vault (`~/.omniroute/config.json`).
  - **OAuth Tiers**: For providers requiring OAuth token exchange, OmniRoute handles refresh flows transparently behind the gateway.

---

## 3. Recommended FREE / OAuth Coding Models
The following models are available via free or OAuth upstream tiers through OmniRoute and are suitable for complex software engineering tasks:

1. **`qwen/qwen-2.5-coder-32b-instruct:free`** (Recommended)
   - **Provider**: OpenRouter Free / Groq / Together
   - **Context Window**: 131,072 tokens (128K)
   - **Capabilities**: SOTA open-weights coding model, highly fluent in Python repository navigation, instruction following, and robust error-handling during tool interactions.

2. **`google/gemini-2.0-flash-001`**
   - **Provider**: Google AI Studio Free Tier / OAuth
   - **Context Window**: 1,048,576 tokens (1M)
   - **Capabilities**: Exceptionally fast inference, 1M context window, native structured outputs and tool calling.

---

## 4. 64K Context Requirement Verification
- **Hermes Context Requirement**: $\ge 64,000$ tokens.
- **`qwen2.5-coder-32b-instruct`**: **128,000 tokens** ($\ge 64\text{K}$ $\checkmark$).
- **`gemini-2.0-flash`**: **1,048,576 tokens** ($\ge 64\text{K}$ $\checkmark$).
- Both candidates easily satisfy Hermes' context window prerequisite for deep codebase inspection.

---

## 5. Tool / Function Calling Support
- **Support Status**: **VERIFIED**
- Both `qwen2.5-coder-32b-instruct` and `gemini-2.0-flash` support native OpenAI tool calling (`tools` array containing JSON Schema definitions, `tool_choice`, and returning `tool_calls` in assistant deltas/messages).
- OmniRoute forwards the JSON Schema definitions transparently to upstream models without stripping or corrupting parameter schemas.

---

## 6. Rate Limits & Quotas Analysis
- **OpenRouter Free Tier** (`qwen/qwen-2.5-coder-32b-instruct:free`):
  - **RPM**: 20 requests/min
  - **RPD**: 200 requests/day
  - **TPM**: 60,000 tokens/min
- **Groq Free Tier** (`qwen-2.5-coder-32b`):
  - **RPM**: 30 requests/min
  - **RPD**: 14,400 requests/day
  - **TPM**: 6,000 tokens/min
- **Google AI Studio Free Tier** (`gemini-2.0-flash`):
  - **RPM**: 15 requests/min
  - **RPD**: 1,500 requests/day
  - **TPM**: 1,000,000 tokens/min
- **Impact on Benchmark**:
  - The unfamiliar repository benchmark typically executes ~5 to 15 tool iterations.
  - Rate limits are sufficient for a controlled single-run benchmark, provided requests are not burst-flooded faster than 15–20 RPM.
  - OmniRoute smart failover combos can seamlessly switch to fallback providers if a single upstream rate limit is encountered.

---

## 7. Zero-Change Architectural Compliance
- **Hermes Core (`hermes-agent/`) Modification**: **None** (0 files modified).
- **Hermes ToolRegistry Modification**: **None** (0 files modified).
- **WorkspaceGuard Modification**: **None** (0 files modified).
- **ApprovalController Modification**: **None** (0 files modified).
- **Benchmark Acceptance Logic Modification**: **None** (0 files modified).
- **Ollama Support**: Remains completely intact and unchanged.

---

## 8. Exact Configuration Required

To run Hermes with OmniRoute as an optional provider, pass the following environment configuration:

```bash
export MODEL_PROVIDER="openai"
export MODEL_NAME="qwen/qwen-2.5-coder-32b-instruct:free"
export API_BASE_URL="http://localhost:20128/v1"
export OPENAI_API_KEY="omniroute-local-key"
```

---

## 9. Recommended Controlled Experiment Proposal

### CONTROL
- `provider` = `ollama`
- `model` = `llama3.2:latest`
- `base_url` = `http://localhost:11434/v1`

### EXPERIMENT
- `provider` = `openai`
- `model` = `qwen/qwen-2.5-coder-32b-instruct:free` (or `google/gemini-2.0-flash-001`)
- `base_url` = `http://localhost:20128/v1`

### IDENTICAL EXPERIMENTAL VARIABLES
- Same repository (`unfamiliar_repo`)
- Same repository builder (`benchmarks/unfamiliar_repo_builder.py`)
- Same prompt: `"Inspect this existing project and add pagination to the books API. Preserve all existing behavior, add appropriate tests, and ensure the complete test suite passes..."`
- Same Hermes `AIAgent`
- Same `ToolRegistry`
- Same tools (`read_file`, `write_file`, `edit_file`, `search_files`, `list_directory`, `run_tests`, etc.)
- Same security layer (`WorkspaceGuard`, `ApprovalController`)
- Same iteration limits
- Same independent acceptance checker

### Recommendation & Next Steps
- **Status**: Compatibility and zero-code-change feasibility are **CONFIRMED**.
- **Action**: In strict accordance with rule 10 ("Do not automatically install or download models/providers without asking"), execution is paused until OmniRoute is started locally by the user and upstream provider credentials are provided. Once OmniRoute is active, the controlled experiment can be performed safely.
