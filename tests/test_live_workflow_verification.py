import os
import sys
import asyncio
import shutil
import json
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.hermes_adapter import HermesAgentAdapter, is_web_frontend_project
from server.agents.provider_manager import provider_manager


async def run_live_workflow_tests():
    print("=" * 70)
    print("STARTING LIVE WORKFLOW VERIFICATION SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: EXPLICIT REACT WEBSITE GENERATION WORKFLOW
    # -------------------------------------------------------------
    print("\n[TEST 1] Executing Explicit React Website Generation Workflow...")
    react_workspace = ROOT_DIR / "workspace" / "react_solaris_studio"
    if react_workspace.exists():
        shutil.rmtree(react_workspace, ignore_errors=True)
    react_workspace.mkdir(parents=True, exist_ok=True)

    adapter_react = HermesAgentAdapter(str(react_workspace))
    react_events = []

    async def react_callback(event):
        react_events.append(event)
        event_name = event.get("event")
        if event_name == "plan_created":
            title = event.get("data", {}).get("plan", {}).get("title")
            print(f"  -> Plan Created: {title}")
        elif event_name == "generation_status_update":
            state = event.get("data", {}).get("state")
            msg = event.get("data", {}).get("message")
            print(f"  -> Orchestrator State: {state} ({msg})")
        elif event_name == "multi_agent_orchestration_completed":
            status = event.get("data", {}).get("status")
            print(f"  -> MultiAgentOrchestrator Completed with status: {status}")
        elif event_name == "agent_finished":
            print(f"  -> Agent Finished: status={event.get('data', {}).get('status')}")

    react_prompt = "Build an architectural creative agency portfolio for Solaris Studio in React with interactive project cards, metrics grid, and clean vector icons"
    session_id_react = "session_react_test_001"

    print("Invoking adapter.process_user_turn with language='react'...")
    await adapter_react.process_user_turn(
        session_id=session_id_react,
        user_message=react_prompt,
        event_callback=react_callback,
        language="react"
    )

    event_types_react = [e.get("event") for e in react_events]
    print(f"\nReact Event Types Emitted: {set(event_types_react)}")

    # 1. Verify routing entered MultiAgentOrchestrator
    assert "multi_agent_orchestration_completed" in event_types_react, "FAIL: MultiAgentOrchestrator was NOT triggered for React request!"
    
    # 2. Verify 5-phase web plan was created
    plan_events = [e for e in react_events if e.get("event") == "plan_created"]
    assert len(plan_events) > 0, "FAIL: No plan_created event emitted!"
    plan_tasks = plan_events[0].get("data", {}).get("plan", {}).get("tasks", [])
    assert len(plan_tasks) == 5, f"Expected 5 web phases, got {len(plan_tasks)}"
    assert any("Creative Director" in t.get("description", "") for t in plan_tasks), "Creative Director missing from plan!"
    assert any("Visual QA" in t.get("description", "") for t in plan_tasks), "Visual QA missing from plan!"

    # 3. Verify files were generated in workspace
    files = list(react_workspace.glob("**/*"))
    rel_files = [str(f.relative_to(react_workspace)) for f in files if f.is_file()]
    print(f"Generated Files in {react_workspace.name}: {rel_files[:10]} (total: {len(rel_files)})")
    assert any(f.endswith(".html") or f.endswith(".jsx") or f.endswith(".js") for f in rel_files), "No web files created!"

    # 4. Verify Visual QA ran and produced report
    orch_events = [e for e in react_events if e.get("event") == "multi_agent_orchestration_completed"]
    qa_report = orch_events[0].get("data", {}).get("qa_report", {})
    print(f"Visual QA Decision: {qa_report.get('decision')} | Visual Available: {qa_report.get('visual_inspection_available')}")
    assert "decision" in qa_report, "Visual QA report has no decision!"

    # 5. Verify Zero-Emoji rule in generated code
    for code_file in react_workspace.glob("src/**/*.{jsx,js,tsx,ts}"):
        content = code_file.read_text(encoding="utf-8")
        for bad_emoji in ["👟", "🛒", "🍔", "🏀", "📊", "⭐", "🚀"]:
            assert bad_emoji not in content, f"Banned emoji {bad_emoji} found in {code_file.name}!"

    print("✓ [TEST 1] React Website Generation Workflow PASSED!\n")

    # -------------------------------------------------------------
    # TEST 2: BACKEND-ONLY REQUEST WORKFLOW
    # -------------------------------------------------------------
    print("[TEST 2] Executing Backend-Only Python Request Workflow...")
    backend_workspace = ROOT_DIR / "workspace" / "test_backend_calc"
    if backend_workspace.exists():
        shutil.rmtree(backend_workspace, ignore_errors=True)
    backend_workspace.mkdir(parents=True, exist_ok=True)

    adapter_backend = HermesAgentAdapter(str(backend_workspace))
    backend_events = []

    async def backend_callback(event):
        backend_events.append(event)
        event_name = event.get("event")
        if event_name == "plan_created":
            title = event.get("data", {}).get("plan", {}).get("title")
            print(f"  -> Plan Created: {title}")
        elif event_name == "agent_finished":
            print(f"  -> Agent Finished: status={event.get('data', {}).get('status')}")

    backend_prompt = "Build a Python CLI loan interest calculator using argparse with unit tests"
    session_id_backend = "session_backend_test_002"

    print("Invoking adapter.process_user_turn with language='python'...")
    await adapter_backend.process_user_turn(
        session_id=session_id_backend,
        user_message=backend_prompt,
        event_callback=backend_callback,
        language="python"
    )

    event_types_backend = [e.get("event") for e in backend_events]
    print(f"\nBackend Event Types Emitted: {set(event_types_backend)}")

    # 1. Verify MultiAgentOrchestrator was NOT triggered
    assert "multi_agent_orchestration_completed" not in event_types_backend, "FAIL: MultiAgentOrchestrator should NOT trigger for backend python request!"

    # 2. Verify backend 4-phase plan was created (NOT web 5-phase)
    b_plan_events = [e for e in backend_events if e.get("event") == "plan_created"]
    assert len(b_plan_events) > 0, "FAIL: No plan_created event emitted for backend!"
    b_plan_tasks = b_plan_events[0].get("data", {}).get("plan", {}).get("tasks", [])
    assert len(b_plan_tasks) == 4, f"Expected 4 backend phases, got {len(b_plan_tasks)}"
    assert any("Workspace & Dependency Analysis" in t.get("title", "") for t in b_plan_tasks)
    assert not any("Creative Director" in t.get("description", "") for t in b_plan_tasks)

    # 3. Verify no web boilerplate contamination
    assert not (backend_workspace / "index.html").exists(), "Contaminated backend with index.html!"
    assert not (backend_workspace / "style.css").exists(), "Contaminated backend with style.css!"
    assert not (backend_workspace / "app.js").exists(), "Contaminated backend with app.js!"

    print("✓ [TEST 2] Backend-Only Request Workflow PASSED!\n")

    print("=" * 70)
    print("ALL LIVE WORKFLOW VERIFICATION TESTS PASSED SUCCESSFULLY! (2/2)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_live_workflow_tests())
