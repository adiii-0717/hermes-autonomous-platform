import sys
import json
import asyncio
import websockets

async def run_diagnose(prompt_text):
    uri = "ws://localhost:8000/ws/chat"
    print(f"\n=== CONNECTING TO WEBSOCKET FOR PROMPT: {prompt_text[:60]}... ===")
    try:
        async with websockets.connect(uri) as websocket:
            # 1. Receive session start
            start_evt = await websocket.recv()
            print(f"[RECV] Session started event: {start_evt[:250]}")
            
            # 2. Send user message
            print(f"[SEND] Sending user_message")
            await websocket.send(json.dumps({"type": "user_message", "content": prompt_text}))
            
            # 3. Read events with a timeout
            while True:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(msg)
                    evt_type = data.get("event") or data.get("type")
                    print(f"[RECV] Event: {evt_type} -> {json.dumps(data)[:250]}")
                    
                    if evt_type in ["agent_finished", "language_selection_required", "project_selection_required"]:
                        print(f"Terminating receive loop due to terminal event: {evt_type}")
                        break
                except asyncio.TimeoutError:
                    print("[TIMEOUT] No event received for 10 seconds")
                    break
    except Exception as e:
        print(f"[ERROR] Connection/Communication failed: {e}")

async def main():
    # Test 1: Tiny request
    await run_diagnose("Create a Python calculator with tests.")
    
    # Test 2: Large request
    large_prompt = (
        "Build a personal finance management web application. Ask me which programming language I want to use before starting. "
        "The application should allow users to add income and expenses, categorize transactions, view their balance, "
        "filter transactions by date and category, and generate a monthly financial summary. Create a clean responsive UI, "
        "persist the data, include proper error handling, and write automated tests. After implementation, run the tests "
        "and verify the application works before reporting completion."
    )
    await run_diagnose(large_prompt)

if __name__ == "__main__":
    asyncio.run(main())
