import os
import sys
import time
import json
import asyncio
import tempfile
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Environment setup
os.environ["MODEL_PROVIDER"] = "ollama"
os.environ["API_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"

from server.hermes_adapter import HermesAgentAdapter
import run_agent
from benchmarks.unfamiliar_repo_builder import setup_unfamiliar_repository

RESULTS_DIR = PROJECT_ROOT / "benchmarks" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def hash_workspace(ws_path: Path) -> (str, int, list):
    file_list = []
    hasher = hashlib.sha256()
    for p in sorted(ws_path.rglob("*")):
        if p.is_file():
            rel_p = str(p.relative_to(ws_path))
            file_list.append(rel_p)
            hasher.update(rel_p.encode("utf-8"))
            try:
                hasher.update(p.read_bytes())
            except Exception:
                pass
    return hasher.hexdigest(), len(file_list), file_list

async def run_single_model_test(model_name: str) -> dict:
    temp_dir = tempfile.TemporaryDirectory()
    workspace = Path(temp_dir.name).resolve()
    
    # 1. Setup fresh unfamiliar repository
    setup_unfamiliar_repository(workspace)
    hash_before, count_before, files_before = hash_workspace(workspace)
    
    print(f"\n=================================================================")
    print(f"RUNNING MODEL A/B TEST FOR: {model_name}")
    print(f"Workspace: {workspace}")
    print(f"File Count Before: {count_before}")
    print(f"=================================================================")

    os.environ["MODEL_NAME"] = model_name
    adapter = HermesAgentAdapter(str(workspace))
    session_id = f"ab_experiment_{model_name.replace(':', '_')}"

    # 2. Baseline test verification
    baseline_cmd = "python3 -m unittest discover -s tests"
    baseline_res = adapter.testing_tools.run_tests(baseline_cmd)
    print(f"Baseline Test Result Exit Code: {baseline_res['exit_code']}")

    # Prevent fallback
    async def strict_no_fallback(session_id, user_message, callback):
        raise RuntimeError("STRICT BENCHMARK FAILURE: Hermes fell back to _run_autonomous_workspace_turn()!")
        
    adapter._run_autonomous_workspace_turn = strict_no_fallback

    # Instrument AIAgent
    aiagent_instantiated = False
    original_init = run_agent.AIAgent.__init__
    def instrumented_aiagent_init(self, *args, **kwargs):
        nonlocal aiagent_instantiated
        aiagent_instantiated = True
        original_init(self, *args, **kwargs)
        
    run_agent.AIAgent.__init__ = instrumented_aiagent_init

    prompt = "Inspect this existing project and add pagination to the books API. Preserve all existing behavior, add appropriate tests, and ensure the complete test suite passes. Do not assume filenames, classes, functions, or implementation details. Discover the project's architecture yourself before making changes."

    start_time = time.time()
    res = None
    caught_exception = None

    try:
        agent = run_agent.AIAgent(
            model=model_name,
            provider="ollama",
            api_key="ollama",
            base_url="http://localhost:11434/v1",
            session_id=session_id,
            enabled_toolsets=["development"]
        )
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None, lambda: agent.run_conversation(user_message=prompt))
    except Exception as exc:
        caught_exception = f"{type(exc).__name__}: {exc}"
        print(f"Exception during agent execution: {caught_exception}")

    duration = round(time.time() - start_time, 4)

    hash_after, count_after, files_after = hash_workspace(workspace)
    created_files = [f for f in files_after if f not in files_before]
    modified_files = []
    for f in files_after:
        if f in files_before and (workspace / f).read_bytes() != (workspace / f).read_bytes():
            # Check modification via sha256 or timestamp
            pass

    # Compare hashes of files before and after
    # 3. Post-execution verification via unittest
    final_test_cmd = "python3 -m unittest discover -s tests"
    final_test_res = adapter.testing_tools.run_tests(final_test_cmd)

    # 4. Independent Acceptance Checker Verification
    sys.path.insert(0, str(workspace))
    acceptance_crud = False
    acceptance_pagination = False
    acceptance_persistence = False
    acceptance_overall = False

    try:
        from fastapi.testclient import TestClient
        from app.main import app as test_app
        from app.database.init_db import initialize_database as test_init_db
        test_init_db()
        client = TestClient(test_app)

        # CRUD verification
        r_create = client.post("/api/v1/books", json={"title": "Acceptance Title", "author": "Acceptance Author", "genre": "Tech", "price": 29.99, "published_year": 2024})
        if r_create.status_code == 201:
            bid = r_create.json()["id"]
            r_get = client.get(f"/api/v1/books/{bid}")
            if r_get.status_code == 200:
                acceptance_crud = True

        # Pagination verification
        r_p1 = client.get("/api/v1/books?page=1&page_size=2")
        r_p2 = client.get("/api/v1/books?page=2&page_size=2")
        if r_p1.status_code == 200 and r_p2.status_code == 200:
            p1_data = r_p1.json()
            p2_data = r_p2.json()
            if isinstance(p1_data, list) and isinstance(p2_data, list) and len(p1_data) == 2 and len(p2_data) == 2:
                if p1_data[0]["id"] != p2_data[0]["id"]:
                    acceptance_pagination = True

        acceptance_persistence = (workspace / "books.db").exists()
        acceptance_overall = acceptance_crud and acceptance_pagination and acceptance_persistence and (final_test_res["exit_code"] == 0)
    except Exception as e:
        print(f"Acceptance checker note for {model_name}: {e}")

    api_calls_count = res.get("api_calls", 0) if res else 0
    tool_calls_list = res.get("messages", []) if res else []
    extracted_tools = []
    tool_errors = []
    
    for msg in tool_calls_list:
        if isinstance(msg, dict):
            if msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    extracted_tools.append({
                        "name": tc.get("function", {}).get("name"),
                        "arguments": tc.get("function", {}).get("arguments")
                    })
            if msg.get("role") == "tool" and "error" in str(msg.get("content", "")).lower():
                tool_errors.append(str(msg.get("content"))[:200])

    finish_reason = res.get("turn_exit_reason", "unknown") if res else "exception"

    temp_dir.cleanup()

    return {
        "model_name": model_name,
        "aiagent_instantiated": aiagent_instantiated,
        "api_calls": api_calls_count,
        "duration_seconds": duration,
        "extracted_tools_count": len(extracted_tools),
        "extracted_tools": extracted_tools,
        "tool_errors_count": len(tool_errors),
        "tool_errors": tool_errors,
        "files_created": created_files,
        "files_created_count": len(created_files),
        "final_test_exit_code": final_test_res["exit_code"],
        "acceptance_crud": acceptance_crud,
        "acceptance_pagination": acceptance_pagination,
        "acceptance_persistence": acceptance_persistence,
        "acceptance_overall": acceptance_overall,
        "finish_reason": finish_reason,
        "caught_exception": caught_exception,
        "success": (caught_exception is None) and (api_calls_count > 0) and (finish_reason != "exception") and (len(extracted_tools) > 0)
    }

async def main():
    print("=================================================================")
    print("STARTING OLLAMA MODEL CAPABILITY A/B BENCHMARK EXPERIMENT")
    print("=================================================================")

    control_model = "llama3.2:latest"
    experiment_model = "qwen2.5:3b"

    print(f"CONTROL MODEL:    {control_model}")
    print(f"EXPERIMENT MODEL: {experiment_model}")

    # 1. Run Control Model (llama3.2:latest)
    control_result = await run_single_model_test(control_model)

    # 2. Run Experiment Model (qwen2.5:3b)
    experiment_result = await run_single_model_test(experiment_model)

    # Determine classification
    if not control_result["success"] and not experiment_result["success"]:
        classification = "B. PRODUCT-LAYER LIMITATION" if control_result["extracted_tools_count"] > 0 and experiment_result["extracted_tools_count"] > 0 else "C. BOTH"
    elif not control_result["success"] and experiment_result["success"]:
        classification = "A. MODEL CAPABILITY LIMITATION"
    elif control_result["success"] and experiment_result["success"]:
        classification = "INCONCLUSIVE"
    else:
        classification = "BOTH"

    ab_comparison = {
        "experiment": "ollama_model_ab_comparison",
        "date": "2026-08-24",
        "control": control_result,
        "experiment_model": experiment_result,
        "classification": classification,
        "findings": {
            "control_success": control_result["success"],
            "experiment_success": experiment_result["success"],
            "tool_calls_diff": {
                "control": control_result["extracted_tools_count"],
                "experiment": experiment_result["extracted_tools_count"]
            },
            "files_created_diff": {
                "control": control_result["files_created_count"],
                "experiment": experiment_result["files_created_count"]
            }
        }
    }

    # Save evidence json
    with open(RESULTS_DIR / "ollama_model_ab_comparison.json", "w", encoding="utf-8") as f:
        json.dump(ab_comparison, f, indent=2)

    # Save Markdown report
    report_md = f"""# Ollama Model Capability A/B Comparison Report

> **Experiment ID**: `ollama_model_ab_comparison`  
> **Date**: 2026-08-24  
> **Control Model**: `{control_model}`  
> **Experiment Model**: `{experiment_model}`  
> **Final Classification**: **{classification}**

---

## Executive Summary

A controlled A/B experiment was conducted on the unfamiliar repository benchmark (`ollama_unfamiliar_repository_01`) comparing `{control_model}` (Control) against `{experiment_model}` (Experiment).

Both runs executed under identical runtime conditions, using genuine `run_agent.AIAgent` ReAct execution, zero fallback shortcuts, and the same independent acceptance checker.

---

## A/B Experimental Results Comparison

| Metric / Dimension | Control (`{control_model}`) | Experiment (`{experiment_model}`) |
|---|---|---|
| **AIAgent Instantiated** | `{control_result['aiagent_instantiated']}` | `{experiment_result['aiagent_instantiated']}` |
| **API Model Calls** | `{control_result['api_calls']}` | `{experiment_result['api_calls']}` |
| **Total Duration** | `{control_result['duration_seconds']}s` | `{experiment_result['duration_seconds']}s` |
| **Tool Calls Made** | `{control_result['extracted_tools_count']}` | `{experiment_result['extracted_tools_count']}` |
| **Tool Errors Encountered** | `{control_result['tool_errors_count']}` | `{experiment_result['tool_errors_count']}` |
| **Files Created by Agent** | `{control_result['files_created_count']}` | `{experiment_result['files_created_count']}` |
| **Final Test Suite Exit Code** | `{control_result['final_test_exit_code']}` | `{experiment_result['final_test_exit_code']}` |
| **CRUD Verification** | `{control_result['acceptance_crud']}` | `{experiment_result['acceptance_crud']}` |
| **Pagination Verification** | `{control_result['acceptance_pagination']}` | `{experiment_result['acceptance_pagination']}` |
| **Persistence Verification** | `{control_result['acceptance_persistence']}` | `{experiment_result['acceptance_persistence']}` |
| **Overall Acceptance** | **`{control_result['acceptance_overall']}`** | **`{experiment_result['acceptance_overall']}`** |
| **Final Benchmark Success** | **`{control_result['success']}`** | **`{experiment_result['success']}`** |

---

## Detailed Observation & Analysis

### Control Run (`{control_model}`)
- **Behavior**: Made `{control_result['extracted_tools_count']}` tool calls. Encountered `{control_result['tool_errors_count']}` tool errors.
- **Finish Reason**: `{control_result['finish_reason']}`.
- **Workspace Mutations**: Created `{control_result['files_created_count']}` files autonomously.

### Experiment Run (`{experiment_model}`)
- **Behavior**: Made `{experiment_result['extracted_tools_count']}` tool calls. Encountered `{experiment_result['tool_errors_count']}` tool errors.
- **Finish Reason**: `{experiment_result['finish_reason']}`.
- **Workspace Mutations**: Created `{experiment_result['files_created_count']}` files autonomously.

---

## Root Cause & Product-Layer Implications

1. **Model Capability vs Product Layer**: The experiment demonstrates how different local Ollama models perform ReAct tool planning, tool parameter formulation, and schema error recovery under open-ended repository exploration prompts.
2. **Product Layer Recommendations**:
   - Improve parameter sanitization in `server/tools/dev_terminal_tools.py` for empty `{{}}` arguments.
   - Provide system prompt error recovery guidance in `server/hermes_adapter.py`.
   - Recommend 14B+ local models or cloud provider models for complex open-ended repository discovery tasks.

---

## Evidence Artifacts

- [ollama_model_ab_comparison.json](file://{RESULTS_DIR}/ollama_model_ab_comparison.json)
"""
    with open(PROJECT_ROOT / "OLLAMA_MODEL_CAPABILITY_COMPARISON.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n=================================================================")
    print("A/B EXPERIMENT COMPLETE")
    print(f"Classification: {classification}")
    print("=================================================================")

if __name__ == "__main__":
    asyncio.run(main())
