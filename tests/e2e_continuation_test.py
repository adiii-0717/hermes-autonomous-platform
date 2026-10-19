import asyncio
import json
import websockets
import sys
import os
import shutil
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

async def run_continuation_flow():
    # 1. Setup Phase 3 unrelated folder to test isolation later
    unrelated_dir = PROJECT_ROOT / "workspace" / "unrelated_project"
    unrelated_dir.mkdir(parents=True, exist_ok=True)
    dont_touch_file = unrelated_dir / "dont_touch.txt"
    dont_touch_file.write_text("DO NOT TOUCH", encoding="utf-8")
    
    # Clean up existing calculator to start Phase 1 fresh
    calc_dir = PROJECT_ROOT / "workspace" / "calculator"
    if calc_dir.exists():
        shutil.rmtree(calc_dir)
        
    uri = "ws://localhost:8000/ws/chat"
    
    # =========================================================================
    # PHASE 1: Build a calculator in Python
    # =========================================================================
    print("\n=== STARTING PHASE 1: CREATE Python CALCULATOR ===")
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        session_event = await websocket.recv()
        print(f"Session start: {session_event[:200]}")
        
        prompt = "Build a simple calculator application in Python. It should support addition, subtraction, multiplication and division, with tests."
        print(f"Sending prompt: {prompt}")
        await websocket.send(json.dumps({"type": "user_message", "content": prompt}))
        
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            evt_type = data.get("event") or data.get("type")
            
            if evt_type in ["project_build_completed", "agent_finished", "tool_started"]:
                print(f"[{evt_type.upper()}] {json.dumps(data.get('data', {}))}")
            elif evt_type == "assistant_message":
                print(f"[ASSISTANT] {data.get('content') or data.get('data', {}).get('content', '')}")
                
            if evt_type == "agent_finished":
                break
                
    # Verify Phase 1 output
    manifest_file = calc_dir / ".project_manifest.json"
    assert manifest_file.exists(), "Manifest file must exist"
    with open(manifest_file, "r") as f:
        manifest = json.load(f)
        assert "python" in [lang.lower() for lang in manifest.get("languages", [])], "Language must be Python"
    print("=== PHASE 1 SUCCESS ===")
    
    # =========================================================================
    # PHASE 2: Continue existing project
    # =========================================================================
    print("\n=== STARTING PHASE 2: CONTINUE Python CALCULATOR ===")
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        session_event = await websocket.recv()
        print(f"Session start: {session_event[:200]}")
        
        # Modify existing calculator
        prompt = "Add percentage and square-root operations to the calculator and add tests for them."
        print(f"Sending prompt: {prompt}")
        await websocket.send(json.dumps({"type": "user_message", "content": prompt}))
        
        build_completed_data = None
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            evt_type = data.get("event") or data.get("type")
            
            if evt_type == "language_selection_required" or evt_type == "project_selection_required":
                raise AssertionError(f"Unexpected disambiguation event: {evt_type}")
                
            if evt_type == "project_build_completed":
                build_completed_data = data.get("data", {})
                print(f"[{evt_type.upper()}] {json.dumps(build_completed_data)}")
            elif evt_type in ["agent_finished", "tool_started"]:
                print(f"[{evt_type.upper()}] {json.dumps(data.get('data', {}))}")
            elif evt_type == "assistant_message":
                print(f"[ASSISTANT] {data.get('content') or data.get('data', {}).get('content', '')}")
                
            if evt_type == "agent_finished":
                break
                
    # Verify Phase 2 output
    assert build_completed_data is not None, "Should have received build completion data"
    assert build_completed_data.get("success") is True, "Build and tests should be successful"
    assert len(build_completed_data.get("files_modified", [])) > 0, "Calculator files should have been modified"
    print("=== PHASE 2 SUCCESS ===")

    # =========================================================================
    # PHASE 3: Verify isolation
    # =========================================================================
    print("\n=== STARTING PHASE 3: ISOLATION VERIFICATION ===")
    assert dont_touch_file.exists(), "Unrelated file must exist"
    assert dont_touch_file.read_text(encoding="utf-8") == "DO NOT TOUCH", "Unrelated file content must be untouched"
    print("=== PHASE 3 SUCCESS ===")
    
    print("\nAll E2E continuation and isolation phases passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_continuation_flow())
