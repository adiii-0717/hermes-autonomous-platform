import sys
import json
import asyncio
import websockets

async def main():
    uri = "ws://localhost:8000/ws/chat"
    prompt = (
        "Build a personal finance management web application. Ask me which programming language I want to use before starting. "
        "The application should allow users to add income and expenses, categorize transactions, view their balance, "
        "filter transactions by date and category, and generate a monthly financial summary. Create a clean responsive UI, "
        "persist the data, include proper error handling, and write automated tests."
    )
    
    print("=== CONNECTING TO REAL WEBSOCKET ===")
    async with websockets.connect(uri) as websocket:
        # 1. Receive session start
        start_evt = await websocket.recv()
        print(f"[RECV] Session started: {start_evt[:200]}")
        
        # 2. Send user message
        print(f"[SEND] Sending project prompt: {prompt[:60]}...")
        await websocket.send(json.dumps({"type": "user_message", "content": prompt}))
        
        # 3. Read events and verify heartbeats/language prompt
        project_name = None
        original_prompt = None
        has_analyzing_heartbeat = False
        
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            evt_type = data.get("event") or data.get("type")
            print(f"[RECV] Event: {evt_type} -> {json.dumps(data)[:250]}")
            
            if evt_type == "agent_heartbeat":
                status = data["data"].get("status")
                elapsed = data["data"].get("elapsed_seconds")
                print(f"[VERIFY] Heartbeat received: status={status}, elapsed={elapsed}s")
                if status == "analyzing_request":
                    has_analyzing_heartbeat = True
                
            elif evt_type == "language_selection_required":
                print(f"[VERIFY] Language selection prompt received successfully!")
                project_name = data.get("data", {}).get("project_name")
                original_prompt = data.get("data", {}).get("prompt")
                
                # 4. Respond with TypeScript language selection
                print(f"[SEND] Simulating language selection: typescript")
                selection_payload = {
                    "type": "language_selected",
                    "language": "typescript",
                    "project_name": project_name,
                    "content": original_prompt
                }
                await websocket.send(json.dumps(selection_payload))
                
            elif evt_type == "project_build_completed":
                print(f"[VERIFY] Project build completed: success={data.get('data', {}).get('success')}")
                
            elif evt_type == "agent_finished":
                print(f"[VERIFY] Agent finished turn successfully!")
                break
                
    # Final check
    if has_analyzing_heartbeat:
        print("\n=== REAL E2E WEBSOCKET TEST COMPLETED SUCCESSFULLY! ===")
    else:
        print("\n=== REAL E2E WEBSOCKET TEST FAILED: No heartbeats with status 'analyzing_request' were received ===")

if __name__ == "__main__":
    asyncio.run(main())
