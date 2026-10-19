import sys
import json
import asyncio
import time
import websockets

async def run_test():
    uri = "ws://localhost:8000/ws/chat"
    prompt = (
        "Build a modern React website for 'Vortex Flow' — a high-performance distributed event streaming engine "
        "and real-time pipeline platform. Include an interactive pipeline topology visualizer, live throughput and latency "
        "telemetry metrics with tabular numbers, architecture benchmarks, and a cluster configuration drawer. "
        "Ensure clean text-based branding, responsive layout, professional Lucide vector icons, and zero emojis."
    )

    print("=== STARTING VORTEX FLOW MULTI-AGENT E2E TEST ===")
    print(f"Connecting to {uri}...")

    async with websockets.connect(uri, ping_interval=60, ping_timeout=60, close_timeout=30) as ws:
        start_raw = await ws.recv()
        start_evt = json.loads(start_raw)
        print(f"[RECV] Session started: {start_evt.get('type') or start_evt.get('event')}")

        print(f"[SEND] Sending prompt: {prompt}")
        await ws.send(json.dumps({"type": "user_message", "content": prompt}))

        project_name = None
        events_received = []
        start_time = time.time()
        timeout = 240

        while time.time() - start_time < timeout:
            try:
                msg_raw = await asyncio.wait_for(ws.recv(), timeout=60.0)
                evt = json.loads(msg_raw)
                evt_type = evt.get("event") or evt.get("type")
                events_received.append(evt_type)

                if evt_type == "run_started":
                    project_name = evt.get("data", {}).get("project_name")
                    print(f"[*] Run started for project: {project_name}")

                elif evt_type == "language_selection_required":
                    print("[*] Language selection prompt received -> Selecting react")
                    p_name = evt.get("data", {}).get("project_name")
                    await ws.send(json.dumps({
                        "type": "language_selected",
                        "language": "react",
                        "project_name": p_name,
                        "content": prompt
                    }))

                elif evt_type == "project_selection_required":
                    print("[*] Project selection required -> Requesting _new_project_")
                    await ws.send(json.dumps({
                        "type": "project_selected",
                        "project_name": "_new_project_",
                        "content": prompt
                    }))

                elif evt_type == "generation_status_update":
                    state = evt.get("data", {}).get("state")
                    progress = evt.get("data", {}).get("progress_percent")
                    message = evt.get("data", {}).get("message")
                    print(f"[STATUS] [{progress}%] {state}: {message}")

                elif evt_type == "multi_agent_orchestration_completed":
                    print(f"[SUCCESS] Multi-Agent Orchestration completed!")
                    data = evt.get("data", {})
                    print(f"Project Dir: {data.get('project_dir')}")
                    print(f"Cycle Count: {data.get('cycle_count')}")
                    qa = data.get("qa_report", {})
                    print(f"QA Decision: {qa.get('decision')}, Score: {qa.get('overall_score')}")

                elif evt_type == "project_build_completed":
                    print(f"[BUILD COMPLETED] Project build completed event received.")

                elif evt_type == "agent_finished":
                    print("[DONE] Agent finished turn successfully!")
                    break

                elif evt_type == "error":
                    err = evt.get("data", {}).get("error")
                    print(f"[ERROR EVENT] {err}")

            except asyncio.TimeoutError:
                print(f"[HEARTBEAT] Still waiting for agent... ({int(time.time() - start_time)}s elapsed)")

    print(f"\nTotal events received: {len(events_received)}")
    return project_name

if __name__ == "__main__":
    proj = asyncio.run(run_test())
    print(f"Finished test for project: {proj}")
