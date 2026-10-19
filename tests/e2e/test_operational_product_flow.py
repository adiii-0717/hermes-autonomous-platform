import os
import sys
import time
import json
import asyncio
import tempfile
import subprocess
import httpx
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmarks.unfamiliar_repo_builder import setup_unfamiliar_repository

async def run_operational_product_test():
    print("=================================================================")
    print("STARTING OPERATIONAL SOFTWARE DEVELOPMENT AGENT PRODUCT TEST")
    print("=================================================================")

    # 1. Setup workspace
    temp_dir = tempfile.TemporaryDirectory()
    workspace_path = Path(temp_dir.name).resolve()
    setup_unfamiliar_repository(workspace_path)
    print(f"1. Workspace Initialized: {workspace_path}")

    # 2. Launch FastAPI backend
    env = os.environ.copy()
    env["MODEL_PROVIDER"] = "ollama"
    env["MODEL_NAME"] = "llama3.2:latest"
    env["API_BASE_URL"] = "http://localhost:11434/v1"
    env["OPENAI_API_KEY"] = "ollama"

    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("2. Launching FastAPI Backend on http://127.0.0.1:8000...")
    await asyncio.sleep(2.5)

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=600.0) as client:
        # Check health
        h_res = await client.get("/api/health")
        print(f"   Health Check: {h_res.status_code} - {h_res.json()}")
        assert h_res.status_code == 200, "Backend server health check failed!"

        # Set workspace
        ws_res = await client.post("/api/workspace", json={"path": str(workspace_path)})
        print(f"3. Workspace Binding Status: {ws_res.status_code}, Body: {ws_res.text}")
        assert ws_res.status_code == 200, f"Workspace binding failed: {ws_res.text}"

        # Create Session
        s_res = await client.post("/api/sessions", json={"name": "operational_e2e_session"})
        session_data = s_res.json()
        session_id = session_data["session_id"]
        print(f"4. Session Created: {session_id}")

        # Send Multi-Step User Development Turn via REST API
        print("5. Sending Multi-Step Development Task to /api/chat...")
        prompt = "Inspect the workspace. Create hello.py containing a hello(name) function and write a test in tests/test_hello.py verifying it."
        
        chat_payload = {
            "session_id": session_id,
            "message": prompt
        }
        
        chat_res = await client.post("/api/chat", json=chat_payload)
        print(f"   Chat Response Status: {chat_res.status_code}")
        assert chat_res.status_code == 200, "Chat request failed!"
        chat_json = chat_res.json()
        print(f"   Turn Completed: {chat_json.get('status')}")

        # Verify File Changes & Diffs
        manifest_res = await client.get("/api/workspace/manifest")
        print(f"6. Workspace Manifest Inspected: {manifest_res.status_code} ({manifest_res.json().get('total_files')} files)")
        
        diff_res = await client.get("/api/workspace/health")
        print(f"   Workspace Health Inspected: {diff_res.status_code}")

        # 7. Test Human-in-the-Loop Approval Controller
        print("7. Testing Human-in-the-Loop Approval Controller via API...")
        appr_req_res = await client.post("/api/approval/request", json={
            "action_type": "HIGH_RISK_TERMINAL_COMMAND",
            "command": "rm -rf /tmp/test_dir",
            "timeout": 10.0
        })
        print(f"   Approval Request Created API: {appr_req_res.status_code} - {appr_req_res.json()}")
        assert appr_req_res.status_code == 200
        req_id = appr_req_res.json()["request_id"]
        
        # Respond via API
        resp_res = await client.post(f"/api/approvals/{req_id}/respond", json={"approved": True})
        print(f"   Approval Response API: {resp_res.status_code} - {resp_res.json()}")
        assert resp_res.status_code == 200
        assert resp_res.json()["approved"] is True

    # 8. Test Backend Server Restart & Session State Survival
    print("8. Testing Backend Server Restart & Session State Persistence...")
    server_process.terminate()
    server_process.wait()
    print("   Server Terminated.")

    # Re-launch backend server process
    server_process_2 = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    await asyncio.sleep(2.5)

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=600.0) as client2:
        h2_res = await client2.get("/api/health")
        print(f"   Re-launched Server Health: {h2_res.status_code}")
        assert h2_res.status_code == 200

        sessions_res = await client2.get("/api/sessions")
        sessions_data = sessions_res.json()
        sessions_list = sessions_data.get("sessions", []) if isinstance(sessions_data, dict) else sessions_data
        print(f"   Sessions Listed After Restart ({len(sessions_list)} sessions): {sessions_list}")
        found = any(isinstance(s, dict) and s.get("session_id") == session_id for s in sessions_list)
        assert found, f"Session {session_id} not found in {sessions_list} after server restart!"
        print("   ✅ Session Context & State Survived Server Restart!")

    server_process_2.terminate()
    server_process_2.wait()
    temp_dir.cleanup()

    print("\n=================================================================")
    print("OPERATIONAL PRODUCT E2E TEST COMPLETED SUCCESSFULLY (100% PASS)")
    print("=================================================================")

if __name__ == "__main__":
    asyncio.run(run_operational_product_test())
