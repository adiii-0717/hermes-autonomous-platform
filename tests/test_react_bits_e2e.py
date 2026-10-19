import sys
import json
import asyncio
import time
import websockets

async def run_test():
    uri = "ws://localhost:8000/ws/chat"
    prompt = (
        "Build a modern React website for 'Aetheria AI Studio' — a cutting-edge generative AI research lab "
        "and model deployment platform. Use React Bits components including an animated background, "
        "DecryptedText hero typography, interactive SpotlightCards for our model showcase, StarBorder buttons, "
        "magnetic interactions, and professional Lucide React icons. Ensure clean text-based branding, "
        "responsive layout, and no emoji icons."
    )

    print("=== STARTING REACT BITS REAL E2E TEST ===")
    print(f"Connecting to {uri}...")

    async with websockets.connect(uri, ping_interval=60, ping_timeout=60, close_timeout=30) as ws:
        # Wait for session_started
        start_raw = await ws.recv()
        start_evt = json.loads(start_raw)
        print(f"[RECV] Session started: {start_evt.get('type') or start_evt.get('event')}")

        # Send user message requesting the website
        print(f"[SEND] Sending prompt: {prompt}")
        await ws.send(json.dumps({"type": "user_message", "content": prompt}))

        project_name = None
        events_received = []
        start_time = time.time()
        timeout = 240  # 4 minutes max for complete multi-agent cycle

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
                    print(f"Details: {json.dumps(evt.get('data', {}), indent=2)[:400]}")

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
