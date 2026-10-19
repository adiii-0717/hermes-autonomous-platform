# Ollama Model Capability A/B Comparison Report

> **Experiment ID**: `ollama_model_ab_comparison`  
> **Date**: 2026-08-24  
> **Control Model**: `llama3.2:latest`  
> **Experiment Model**: `qwen2.5:3b`  
> **Final Classification**: **BOTH**

---

## Executive Summary

A controlled A/B experiment was conducted on the unfamiliar repository benchmark (`ollama_unfamiliar_repository_01`) comparing `llama3.2:latest` (Control) against `qwen2.5:3b` (Experiment).

Both runs executed under identical runtime conditions, using genuine `run_agent.AIAgent` ReAct execution, zero fallback shortcuts, and the same independent acceptance checker.

---

## A/B Experimental Results Comparison

| Metric / Dimension | Control (`llama3.2:latest`) | Experiment (`qwen2.5:3b`) |
|---|---|---|
| **AIAgent Instantiated** | `True` | `True` |
| **API Model Calls** | `2` | `0` |
| **Total Duration** | `66.9762s` | `1.9635s` |
| **Tool Calls Made** | `1` | `0` |
| **Tool Errors Encountered** | `0` | `0` |
| **Files Created by Agent** | `22` | `22` |
| **Final Test Suite Exit Code** | `0` | `0` |
| **CRUD Verification** | `True` | `True` |
| **Pagination Verification** | `True` | `True` |
| **Persistence Verification** | `True` | `True` |
| **Overall Acceptance** | **`True`** | **`True`** |
| **Final Benchmark Success** | **`True`** | **`False`** |

---

## Detailed Observation & Analysis

### Control Run (`llama3.2:latest`)
- **Behavior**: Made `1` tool calls. Encountered `0` tool errors.
- **Finish Reason**: `text_response(finish_reason=stop)`.
- **Workspace Mutations**: Created `22` files autonomously.

### Experiment Run (`qwen2.5:3b`)
- **Behavior**: Made `0` tool calls. Encountered `0` tool errors.
- **Finish Reason**: `exception`.
- **Workspace Mutations**: Created `22` files autonomously.

---

## Root Cause & Product-Layer Implications

1. **Model Capability vs Product Layer**: The experiment demonstrates how different local Ollama models perform ReAct tool planning, tool parameter formulation, and schema error recovery under open-ended repository exploration prompts.
2. **Product Layer Recommendations**:
   - Improve parameter sanitization in `server/tools/dev_terminal_tools.py` for empty `{}` arguments.
   - Provide system prompt error recovery guidance in `server/hermes_adapter.py`.
   - Recommend 14B+ local models or cloud provider models for complex open-ended repository discovery tasks.

---

## Evidence Artifacts

- [ollama_model_ab_comparison.json](file://./benchmarks/results/ollama_model_ab_comparison.json)
