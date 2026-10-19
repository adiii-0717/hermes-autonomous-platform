import sys
import json
import asyncio
import time
import websockets

WEBSITES = [
    {
        "name": "react_velour_fashion",
        "prompt": (
            "Build a modern online React website for 'Velour Atelier' — an editorial high fashion and haute couture store. "
            "Include an autumn lookbook showcase, exclusive collection pieces with French sizing selector, "
            "slide-over luxury shopping bag drawer with currency toggle, and atelier provenance craftsmanship notes. "
            "Ensure clean text-based branding, responsive layout, professional Lucide vector icons, and zero emojis."
        )
    },
    {
        "name": "react_osteria_restaurant",
        "prompt": (
            "Build a modern online React website for 'Osteria Terra' — an artisanal fine dining and organic gastronomy restaurant. "
            "Include an autumn degustazione 7-course tasting menu, harvest dish presentations with sommelier wine pairings, "
            "an interactive table reservation booking drawer with guest and time selection, and estate olive-wood hearth philosophy. "
            "Ensure clean text-based branding, responsive layout, professional Lucide vector icons, and zero emojis."
        )
    },
    {
        "name": "react_nexus_agency",
        "prompt": (
            "Build a modern online React website for 'Nexus Creative' — a high-contrast architectural design studio and digital systems agency portfolio. "
            "Include an interactive case study showcase with live metrics, client roster infinite ticker, "
            "agency telemetry counters, and a project scoping and proposal estimation drawer. "
            "Ensure clean text-based branding, responsive layout, professional Lucide vector icons, and zero emojis."
        )
    }
]

async def build_website(target: dict):
    uri = "ws://localhost:8000/ws/chat"
    prompt = target["prompt"]
    name = target["name"]

    print(f"\n{'='*70}")
    print(f"=== GENERATING: {name.upper()} ===")
    print(f"Connecting to {uri}...")

    async with websockets.connect(uri, ping_interval=60, ping_timeout=60, close_timeout=30) as ws:
        start_raw = await ws.recv()
        start_evt = json.loads(start_raw)
        print(f"[RECV] Session started: {start_evt.get('type') or start_evt.get('event')}")

        print(f"[SEND] Sending prompt for {name}...")
        await ws.send(json.dumps({"type": "user_message", "content": prompt}))

        project_name = None
        start_time = time.time()
        timeout = 300
        completed = False

        while time.time() - start_time < timeout:
            try:
                msg_raw = await asyncio.wait_for(ws.recv(), timeout=60.0)
                evt = json.loads(msg_raw)
                evt_type = evt.get("event") or evt.get("type")

                if evt_type == "run_started":
                    project_name = evt.get("data", {}).get("project_name")
                    print(f"[*] Run started: project_name={project_name}")

                elif evt_type == "language_selection_required":
                    p_name = evt.get("data", {}).get("project_name") or name
                    print(f"[*] Selecting language 'react' for {p_name}...")
                    await ws.send(json.dumps({
                        "type": "language_selected",
                        "language": "react",
                        "project_name": p_name,
                        "content": prompt
                    }))

                elif evt_type == "project_selection_required":
                    print("[*] Project selection required -> Selecting _new_project_")
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
                    data = evt.get("data", {})
                    qa = data.get("qa_report", {})
                    print(f"[ORCHESTRATION COMPLETED] Dir: {data.get('project_dir')}, QA Score: {qa.get('overall_score')}, Decision: {qa.get('decision')}")
                    completed = True

                elif evt_type == "project_build_completed":
                    print(f"[BUILD COMPLETED] Project build completed event received.")

                elif evt_type == "agent_finished":
                    print(f"[DONE] Agent finished turn successfully for {name}!")
                    break

                elif evt_type == "error":
                    err = evt.get("data", {}).get("error")
                    print(f"[ERROR EVENT] {err}")

            except asyncio.TimeoutError:
                print(f"[HEARTBEAT] Still generating... ({int(time.time() - start_time)}s elapsed)")

        print(f"Completed {name}: success={completed}")
        return project_name or name

async def main():
    results = []
    for site in WEBSITES:
        res = await build_website(site)
        results.append(res)
        await asyncio.sleep(2)
    print("\n" + "="*70)
    print("ALL 3 WEBSITES GENERATED:")
    for r in results:
        print(f" - {r}")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
