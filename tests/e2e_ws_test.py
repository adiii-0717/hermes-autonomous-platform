import asyncio
import json
import websockets
import sys

async def run_test_1():
    uri = "ws://localhost:8000/ws/chat"
    print("=== STARTING TEST 1: EXPLICIT LANGUAGE ===")
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        # Receive session started
        session_event = await websocket.recv()
        print(f"Received session start event: {session_event[:300]}")
        
        prompt = "Build a simple calculator application in Python. It should support addition, subtraction, multiplication and division, with tests."
        print(f"Sending prompt: {prompt}")
        await websocket.send(json.dumps({"type": "user_message", "content": prompt}))
        
        while True:
            try:
                msg = await websocket.recv()
                data = json.loads(msg)
                evt_type = data.get("event") or data.get("type")
                
                # Print key events
                if evt_type in ["language_selection_required", "project_build_completed", "agent_finished", "tool_started", "tool_output"]:
                    print(f"[{evt_type.upper()}] Event data: {json.dumps(data, indent=2)}")
                elif evt_type == "assistant_message":
                    content = data.get("content", "") or data.get("data", {}).get("content", "")
                    print(f"[ASSISTANT] {content}")
                
                if evt_type == "agent_finished":
                    print("Test 1 completed!")
                    break
            except Exception as e:
                print(f"Error reading message: {e}")
                break

async def run_test_2():
    uri = "ws://localhost:8000/ws/chat"
    print("\n=== STARTING TEST 2: LANGUAGE SELECTION ===")
    async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as websocket:
        session_event = await websocket.recv()
        print(f"Received session start event: {session_event[:300]}")
        
        prompt = "Build a simple expense tracker with a web interface."
        print(f"Sending prompt: {prompt}")
        await websocket.send(json.dumps({"type": "user_message", "content": prompt}))
        
        project_name = None
        original_prompt = None
        
        while True:
            try:
                msg = await websocket.recv()
                data = json.loads(msg)
                evt_type = data.get("event") or data.get("type")
                
                if evt_type == "language_selection_required":
                    print(f"[{evt_type.upper()}] Received event! Data: {json.dumps(data, indent=2)}")
                    project_name = data.get("data", {}).get("project_name")
                    original_prompt = data.get("data", {}).get("prompt")
                    
                    # Simulate user selecting TypeScript
                    print(f"Simulating language selection: TypeScript for project: {project_name}")
                    selection_payload = {
                        "type": "language_selected",
                        "language": "typescript",
                        "project_name": project_name,
                        "content": original_prompt
                    }
                    await websocket.send(json.dumps(selection_payload))
                
                elif evt_type in ["project_build_completed", "agent_finished", "tool_started", "tool_output"]:
                    print(f"[{evt_type.upper()}] Event data: {json.dumps(data, indent=2)}")
                elif evt_type == "assistant_message":
                    content = data.get("content", "") or data.get("data", {}).get("content", "")
                    print(f"[ASSISTANT] {content}")
                
                if evt_type == "agent_finished" and project_name is not None:
                    print("Test 2 completed!")
                    break
            except Exception as e:
                print(f"Error reading message: {e}")
                break

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "2":
        await run_test_2()
    else:
        await run_test_1()

if __name__ == "__main__":
    asyncio.run(main())
