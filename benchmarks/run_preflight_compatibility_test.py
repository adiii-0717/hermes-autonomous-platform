import os
import sys
import json
import time
import asyncio
import tempfile
import traceback
import subprocess
import requests
import builtins
import threading
from pathlib import Path

# Force unbuffered stdout printing
original_print = builtins.print
def print(*args, **kwargs):
    kwargs["flush"] = True
    original_print(*args, **kwargs)
builtins.print = print

# Setup paths to ensure server/ and hermes-agent/ imports work correctly
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
HERMES_AGENT_DIR = PROJECT_ROOT / "hermes-agent"
if str(HERMES_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(HERMES_AGENT_DIR))

# Setup Thread-Safe asyncio.create_task patch dynamically
main_loop = None
original_create_task = asyncio.create_task

def thread_safe_create_task(coro):
    global main_loop
    if main_loop is None:
        # The main thread loop will be active when this is first invoked
        try:
            main_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    try:
        loop = asyncio.get_running_loop()
        # If we are in the thread that runs the main event loop
        if main_loop is not None and loop is main_loop:
            return original_create_task(coro)
    except RuntimeError:
        pass
    
    if main_loop is not None:
        # Schedule thread-safely on the main loop
        return asyncio.run_coroutine_threadsafe(coro, main_loop)
    else:
        return original_create_task(coro)

asyncio.create_task = thread_safe_create_task

# Import Hermes agent modules
os.environ["MODEL_PROVIDER"] = "ollama"
os.environ["MODEL_NAME"] = "gemma4:12b-hermes"
os.environ["API_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"  # Satisfy required key checks

from server.hermes_adapter import HermesAgentAdapter
import run_agent











def run_preflight_verifications():
    print("=== Running Pre-flight Verifications (Steps 1-7) ===")
    results = {}
    
    # 1. Confirm Ollama is running
    print("1. Confirming Ollama is running...")
    try:
        r = requests.get("http://localhost:11434/", timeout=5)
        results["ollama_running"] = (r.status_code == 200 or "Ollama" in r.text)
        print(f"   Status: {'Running' if results['ollama_running'] else 'Not Running'}")
    except Exception as e:
        results["ollama_running"] = False
        results["ollama_running_error"] = str(e)
        print(f"   Error: {e}")
        return results
        
    # 2. Confirm gemma4:12b-hermes appears in: GET http://localhost:11434/v1/models
    print("2. Confirming gemma4:12b-hermes is loaded...")
    try:
        r = requests.get("http://localhost:11434/v1/models", timeout=5)
        if r.status_code == 200:
            models = r.json().get("data", [])
            model_ids = [m.get("id") for m in models]
            results["gemma_model_found"] = "gemma4:12b-hermes" in model_ids
            results["available_models"] = model_ids
            print(f"   Found model gemma4:12b-hermes: {results['gemma_model_found']}")
            print(f"   Available models: {model_ids}")
        else:
            results["gemma_model_found"] = False
            results["models_endpoint_status"] = r.status_code
            print(f"   Failed to list models, status code: {r.status_code}")
    except Exception as e:
        results["gemma_model_found"] = False
        results["models_endpoint_error"] = str(e)
        print(f"   Error: {e}")
        
    # 3. Verify basic chat completion
    print("3. Verifying basic chat completion...")
    try:
        payload = {
            "model": "gemma4:12b-hermes",
            "messages": [{"role": "user", "content": "Respond with exactly the word SUCCESS."}],
            "temperature": 0.0
        }
        r = requests.post("http://localhost:11434/v1/chat/completions", json=payload, timeout=90)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"].strip()
            results["basic_chat_success"] = "success" in content.lower()
            results["basic_chat_response"] = content
            print(f"   Basic Chat Success: {results['basic_chat_success']} (Response: '{content}')")
        else:
            results["basic_chat_success"] = False
            results["basic_chat_status"] = r.status_code
            print(f"   Failed chat completion, status code: {r.status_code}")
    except Exception as e:
        results["basic_chat_success"] = False
        results["basic_chat_error"] = str(e)
        print(f"   Error: {e}")

    # 4. Verify native tool calling using a simple JSON-schema tool
    print("4. Verifying native tool/function calling...")
    try:
        tools = [{
            "type": "function",
            "function": {
                "name": "calculate_square",
                "description": "Calculate the square of a number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num": {
                            "type": "integer",
                            "description": "The number to square."
                        }
                    },
                    "required": ["num"]
                }
            }
        }]
        payload = {
            "model": "gemma4:12b-hermes",
            "messages": [{"role": "user", "content": "Use calculate_square tool for num = 7."}],
            "tools": tools,
            "tool_choice": {"type": "function", "function": {"name": "calculate_square"}},
            "temperature": 0.0
        }
        r = requests.post("http://localhost:11434/v1/chat/completions", json=payload, timeout=90)
        if r.status_code == 200:
            msg = r.json()["choices"][0]["message"]
            tool_calls = msg.get("tool_calls", [])
            results["tool_calling_success"] = len(tool_calls) > 0
            print(f"   Tool Calls generated: {len(tool_calls)}")
            if tool_calls:
                results["tool_call_name"] = tool_calls[0]["function"]["name"]
                results["tool_call_arguments_raw"] = tool_calls[0]["function"]["arguments"]
                print(f"   Called: {results['tool_call_name']} with args: {results['tool_call_arguments_raw']}")
                
                # 5. Verify valid JSON arguments matching the schema
                print("5. Verifying JSON arguments match the schema...")
                try:
                    args = json.loads(tool_calls[0]["function"]["arguments"])
                    results["tool_args_parsed"] = args
                    results["tool_args_valid"] = "num" in args and isinstance(args["num"], int)
                    print(f"   Args parsed: {args}, Valid schema: {results['tool_args_valid']}")
                except Exception as je:
                    results["tool_args_parsed"] = None
                    results["tool_args_valid"] = False
                    results["tool_args_parse_error"] = str(je)
                    print(f"   Failed to parse args: {je}")
            else:
                results["tool_args_valid"] = False
        else:
            results["tool_calling_success"] = False
            results["tool_calling_status"] = r.status_code
            print(f"   Failed tool calling API, status code: {r.status_code}")
    except Exception as e:
        results["tool_calling_success"] = False
        results["tool_calling_error"] = str(e)
        print(f"   Error: {e}")

    # 6. Specifically test a write_file-style schema where required parameter is "path", not "file_path"
    print("6. Verifying write_file-style schema ('path' parameter)...")
    try:
        tools = [{
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or overwrite a file in workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The relative path of the file."
                        },
                        "content": {
                            "type": "string",
                            "description": "The file content."
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        }]
        payload = {
            "model": "gemma4:12b-hermes",
            "messages": [{"role": "user", "content": "Use the write_file tool to write print('Hello') to hello.py."}],
            "tools": tools,
            "tool_choice": {"type": "function", "function": {"name": "write_file"}},
            "temperature": 0.0
        }
        r = requests.post("http://localhost:11434/v1/chat/completions", json=payload, timeout=90)
        if r.status_code == 200:
            msg = r.json()["choices"][0]["message"]
            tool_calls = msg.get("tool_calls", [])
            if tool_calls:
                results["write_file_tool_call_found"] = True
                raw_args = tool_calls[0]["function"]["arguments"]
                results["write_file_args_raw"] = raw_args
                try:
                    args = json.loads(raw_args)
                    results["write_file_args_parsed"] = args
                    results["write_file_has_path"] = "path" in args
                    results["write_file_has_file_path"] = "file_path" in args
                    print(f"   Arguments: {args}")
                    print(f"   Has 'path': {results['write_file_has_path']}, Has 'file_path': {results['write_file_has_file_path']}")
                except Exception as je:
                    results["write_file_args_parsed"] = None
                    results["write_file_has_path"] = False
                    results["write_file_has_file_path"] = False
                    print(f"   JSON Parse error: {je}")
            else:
                results["write_file_tool_call_found"] = False
                print("   No tool calls returned for write_file.")
        else:
            results["write_file_status"] = r.status_code
            print(f"   Failed write_file completion API, status code: {r.status_code}")
    except Exception as e:
        results["write_file_error"] = str(e)
        print(f"   Error: {e}")

    # 7. Test whether the model can recover after receiving a tool error
    print("7. Testing model recovery after a tool error...")
    try:
        messages = [
            {"role": "user", "content": "Use the write_file tool to write print('Hello') to forbidden.py."}
        ]
        tools = [{
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Create or overwrite a file in workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The relative path of the file."
                        },
                        "content": {
                            "type": "string",
                            "description": "The file content."
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        }]
        payload = {
            "model": "gemma4:12b-hermes",
            "messages": messages,
            "tools": tools,
            "tool_choice": {"type": "function", "function": {"name": "write_file"}},
            "temperature": 0.0
        }
        r = requests.post("http://localhost:11434/v1/chat/completions", json=payload, timeout=90)
        r.raise_for_status()
        assistant_msg = r.json()["choices"][0]["message"]
        tool_calls = assistant_msg.get("tool_calls", [])
        
        if tool_calls:
            tool_call_id = tool_calls[0]["id"]
            messages.append(assistant_msg)
            # Inject tool error response
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": "write_file",
                "content": "Error: Permission denied for forbidden.py. Writing to this directory is not allowed."
            })
            # Give direction to recover
            messages.append({
                "role": "user",
                "content": "The tool returned an error. Try writing it to allowed.py instead."
            })
            
            payload_turn2 = {
                "model": "gemma4:12b-hermes",
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.0
            }
            r2 = requests.post("http://localhost:11434/v1/chat/completions", json=payload_turn2, timeout=90)
            r2.raise_for_status()
            assistant_msg2 = r2.json()["choices"][0]["message"]
            tool_calls2 = assistant_msg2.get("tool_calls", [])
            
            results["recovery_attempt_tool_calls"] = []
            if tool_calls2:
                for tc in tool_calls2:
                    results["recovery_attempt_tool_calls"].append({
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"]
                    })
                try:
                    args2 = json.loads(tool_calls2[0]["function"]["arguments"])
                    results["recovery_success"] = (
                        tool_calls2[0]["function"]["name"] == "write_file" and 
                        args2.get("path") == "allowed.py"
                    )
                except Exception:
                    results["recovery_success"] = False
                print(f"   Recovery Tool Calls: {results['recovery_attempt_tool_calls']}, Recovery Success: {results['recovery_success']}")
            else:
                results["recovery_success"] = False
                results["recovery_text_response"] = assistant_msg2.get("content")
                print(f"   No tool calls in turn 2. Text response: '{assistant_msg2.get('content')}'")
        else:
            results["recovery_success"] = False
            results["recovery_error"] = "No tool call generated in Turn 1"
            print("   Failed: Turn 1 did not produce a tool call.")
    except Exception as e:
        results["recovery_success"] = False
        results["recovery_error"] = str(e)
        print(f"   Recovery test error: {e}")
        
    return results

async def run_smoke_test(workspace_path):
    print("\n=== Running Genuine Hermes AIAgent Smoke Test (Step 8) ===")
    
    # Initialize the adapter
    adapter = HermesAgentAdapter(str(workspace_path), model_config={
        "provider": "ollama",
        "model": "gemma4:12b-hermes",
        "api_key": "ollama",
        "api_base": "http://localhost:11434/v1"
    })
    
    session_id = "gemma4_12b_hermes_smoke_test_session"
    prompt = "Create a file hello.py containing a greet(name) function and create a test for it. Preserve existing behavior and make sure the test passes."
    
    metrics = {
        "process_user_turn_called": False,
        "aiagent_instantiated": False,
        "model_provider": "ollama",
        "model_name": "gemma4:12b-hermes",
        "api_base_url": "http://localhost:11434/v1",
        "total_execution_time": 0,
        "number_of_model_calls": 0,
        "tool_calls": [],
        "files_created_on_disk": [],
        "test_passes": False,
        "test_suite_exit_code": -1,
        "test_suite_stdout": "",
        "test_suite_stderr": "",
        "fallback_called": False,
        "deterministic_fallback_used": False,
        "exception_caught": None,
        "agent_response": None
    }
    
    # 1. Enforce STRICT no-fallback policy
    async def strict_no_fallback(session_id, user_message, callback):
        metrics["fallback_called"] = True
        metrics["deterministic_fallback_used"] = True
        raise RuntimeError("STRICT COMPATIBILITY FAILURE: Hermes fell back to _run_autonomous_workspace_turn()!")
        
    adapter._run_autonomous_workspace_turn = strict_no_fallback
    
    # 2. Instrument AIAgent instantiation and reference collection
    agent_ref = []
    original_init = run_agent.AIAgent.__init__
    def instrumented_init(self, *args, **kwargs):
        metrics["aiagent_instantiated"] = True
        agent_ref.append(self)
        original_init(self, *args, **kwargs)
        
    run_agent.AIAgent.__init__ = instrumented_init
    
    # 3. Intercept events from process_user_turn to log tool calls and outputs
    async def event_callback(event):
        event_type = event.get("type")
        payload = event.get("payload", {})
        if event_type == "tool_started":
            metrics["tool_calls"].append({
                "name": payload.get("tool"),
                "arguments": payload.get("args"),
                "status": "started",
                "error": None
            })
            print(f"   [Tool Started] {payload.get('tool')} with args: {payload.get('args')}")
        elif event_type == "tool_output":
            tool_name = payload.get("tool")
            result = payload.get("result")
            print(f"   [Tool Completed] {tool_name}")
            # Find the matching tool call in tool_calls list
            for tc in reversed(metrics["tool_calls"]):
                if tc["name"] == tool_name and tc["status"] == "started":
                    tc["status"] = "completed"
                    # Classify if error occurred
                    is_error = False
                    err_msg = None
                    if isinstance(result, dict) and "error" in result:
                        is_error = True
                        err_msg = result["error"]
                    elif isinstance(result, str) and ("error" in result.lower() or "failed" in result.lower() or "exception" in result.lower() or "permission denied" in result.lower()):
                        is_error = True
                        err_msg = result
                    
                    tc["error"] = err_msg
                    break
        elif event_type == "assistant_message":
            metrics["agent_response"] = payload.get("content")
            print(f"   [Agent Response] {payload.get('content')}")
            
    start_time = time.time()
    try:
        metrics["process_user_turn_called"] = True
        await adapter.process_user_turn(session_id, prompt, event_callback)
    except Exception as exc:
        metrics["exception_caught"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        print(f"Exception during smoke test: {exc}")
        
    metrics["total_execution_time"] = round(time.time() - start_time, 4)
    
    # 4. Extract API calls count
    if agent_ref:
        metrics["number_of_model_calls"] = getattr(agent_ref[0], "session_api_calls", 0)
    else:
        metrics["number_of_model_calls"] = 0
        
    # Restore original AIAgent.__init__
    run_agent.AIAgent.__init__ = original_init
    
    # 5. Check files created
    files_created = []
    for p in Path(workspace_path).rglob("*"):
        if p.is_file():
            files_created.append(str(p.relative_to(workspace_path)))
    metrics["files_created_on_disk"] = files_created
    print(f"   Created files: {files_created}")
    
    # 6. Run the generated test to verify if it passes
    test_files = [f for f in files_created if "test" in f and f.endswith(".py")]
    if test_files:
        test_file = test_files[0]
        print(f"   Found test file: {test_file}. Running test...")
        cmd = ["python3", "-m", "unittest", test_file]
        res = subprocess.run(cmd, cwd=workspace_path, capture_output=True, text=True)
        metrics["test_suite_exit_code"] = res.returncode
        metrics["test_suite_stdout"] = res.stdout
        metrics["test_suite_stderr"] = res.stderr
        metrics["test_passes"] = (res.returncode == 0)
        print(f"   Test exit code: {res.returncode}, Test passed: {metrics['test_passes']}")
    else:
        print("   No test file found. Attempting discovery...")
        cmd = ["python3", "-m", "unittest", "discover", "-s", "."]
        res = subprocess.run(cmd, cwd=workspace_path, capture_output=True, text=True)
        metrics["test_suite_exit_code"] = res.returncode
        metrics["test_suite_stdout"] = res.stdout
        metrics["test_suite_stderr"] = res.stderr
        metrics["test_passes"] = (res.returncode == 0)
        print(f"   Discover exit code: {res.returncode}, Test passed: {metrics['test_passes']}")
        
    # Calculate recovery from tool errors
    tool_errors = [tc for tc in metrics["tool_calls"] if tc["error"] is not None]
    metrics["tool_errors_encountered"] = len(tool_errors)
    if len(tool_errors) > 0:
        metrics["recovered_from_tool_errors"] = metrics["test_passes"]
    else:
        metrics["recovered_from_tool_errors"] = "N/A"
        
    return metrics

async def main():
    # Run steps 1-7
    verifications = run_preflight_verifications()
    
    # Check if Ollama is running and qwen model is loaded before proceeding
    if not verifications.get("ollama_running") or not verifications.get("gemma_model_found"):
        print("\n[CRITICAL FAILURE] Ollama is not running or gemma4:12b-hermes is not found! Stopping.")
        smoke_result = {
            "error": "Ollama not running or gemma4:12b-hermes model missing",
            "process_user_turn_called": False,
            "aiagent_instantiated": False,
            "fallback_called": False,
            "deterministic_fallback_used": False
        }
    else:
        # Run step 8 in a fresh temporary workspace
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = Path(temp_dir).resolve()
            print(f"\nFresh Temporary Workspace: {workspace_path}")
            smoke_result = await run_smoke_test(workspace_path)
            
    # Combine results
    final_evidence = {
        "verifications": verifications,
        "smoke_test": smoke_result
    }
    
    # Save the pre-flight evidence
    results_dir = PROJECT_ROOT / "benchmarks" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    evidence_file = results_dir / "gemma4_12b_hermes_preflight_evidence.json"
    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(final_evidence, f, indent=2)
        
    print(f"\nEvidence successfully saved to: {evidence_file}")
    
    # Classification
    success = verifications.get("ollama_running", False) and \
              verifications.get("gemma_model_found", False) and \
              verifications.get("basic_chat_success", False) and \
              verifications.get("tool_calling_success", False) and \
              verifications.get("tool_args_valid", False) and \
              verifications.get("write_file_has_path", False) and \
              smoke_result.get("test_passes", False) and \
              not smoke_result.get("fallback_called", False)
              
    print(f"\nOverall Compatibility Status: {'SUCCESS' if success else 'FAILURE'}")
    
    if not success:
        print("\nAnalyzing failure type...")
        # Determine classification category
        if not verifications.get("ollama_running") or not verifications.get("gemma_model_found"):
            classification = "C" # Ollama/infrastructure issue
            reason = "Ollama service is either offline or the required gemma4:12b-hermes model is not pulled."
        elif not verifications.get("tool_calling_success") or not verifications.get("tool_args_valid"):
            classification = "A" # Model capability limitation
            reason = "Model failed basic tool-calling JSON schema requirements."
        elif verifications.get("write_file_tool_call_found") and not verifications.get("write_file_has_path"):
            classification = "B" # Model/Hermes tool-call compatibility issue
            reason = "Model insisted on using 'file_path' instead of the required 'path' parameter for write_file."
        elif smoke_result.get("fallback_called"):
            classification = "B" # Model/Hermes tool-call compatibility issue
            reason = "Model caused Hermes Agent execution error, leading to deterministic fallback attempt."
        elif not smoke_result.get("test_passes"):
            classification = "A" # Model capability limitation
            reason = "Model failed to write a correct greet function or test that actually passes."
        else:
            classification = "D" # Hermes/product bug
            reason = "Unknown error occurred inside Hermes integration."
            
        print(f"Classification: Category {classification} - {reason}")
        final_evidence["failure_analysis"] = {
            "classification": classification,
            "reason": reason
        }
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump(final_evidence, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
