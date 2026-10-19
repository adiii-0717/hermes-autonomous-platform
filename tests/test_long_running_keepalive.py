import os
import unittest
import asyncio
from fastapi.testclient import TestClient

# Set environment variable for keepalive interval before importing app
os.environ["HERMES_KEEPALIVE_INTERVAL"] = "0.2"

from server.main import app, adapter
from server.tasks import create_event

class TestLongRunningKeepalive(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.original_process_user_turn = adapter.process_user_turn

    def tearDown(self):
        adapter.process_user_turn = self.original_process_user_turn

    def test_websocket_keepalive_and_finish(self):
        # Mock process_user_turn to simulate a 1.5-second running task
        async def mock_process_user_turn(session_id, prompt, event_handler, language=None):
            for _ in range(3):
                await asyncio.sleep(0.5)
            # Emit finish events
            await event_handler(create_event("turn_complete", session_id, {}))
            await event_handler(create_event("agent_finished", session_id, {}))

        adapter.process_user_turn = mock_process_user_turn

        with self.client.websocket_connect("/ws/chat") as websocket:
            # 1. Receive session_started
            start_evt = websocket.receive_json()
            self.assertEqual(start_evt["event"], "session_started")

            # 2. Send language_selected message to bypass metadata extraction and trigger process_user_turn_with_keepalive immediately
            websocket.send_json({
                "type": "language_selected",
                "language": "python",
                "project_name": "temp_project",
                "content": "Simulate a long running task"
            })

            # 3. Read events until agent_finished is received
            events = []
            has_heartbeat = False
            has_finished = False

            while not has_finished:
                data = websocket.receive_json()
                evt_type = data.get("event") or data.get("type")
                events.append(data)
                
                if evt_type == "agent_heartbeat":
                    has_heartbeat = True
                    self.assertEqual(data["data"]["status"], "working")
                    self.assertGreaterEqual(data["data"]["elapsed_seconds"], 0)
                
                if evt_type == "agent_finished":
                    has_finished = True

            # 4. Assertions
            self.assertTrue(has_heartbeat, "Failed to receive agent_heartbeat keepalive messages")
            self.assertTrue(has_finished, "Failed to receive agent_finished event")
            print(f"Regression test passed! Received {len(events)} events in total, including heartbeats and agent_finished.")

    def test_websocket_keepalive_during_metadata_extraction(self):
        # Save original analyze_prompt_for_project
        original_analyze = adapter.analyze_prompt_for_project
        
        # Mock analyze_prompt_for_project to simulate a 1.5-second model call and return no language
        async def mock_analyze_prompt_for_project(user_message):
            for _ in range(3):
                await asyncio.sleep(0.5)
            return {
                "project_name": "temp_project",
                "language": None # force language_selection_required
            }

        adapter.analyze_prompt_for_project = mock_analyze_prompt_for_project

        try:
            with self.client.websocket_connect("/ws/chat") as websocket:
                # 1. Receive session_started
                start_evt = websocket.receive_json()
                self.assertEqual(start_evt["event"], "session_started")

                # 2. Send a user message to trigger new project metadata analysis
                websocket.send_json({
                    "type": "user_message",
                    "content": "Build a completely brand new application that does not exist"
                })

                # 3. Read events until language_selection_required is received
                events = []
                has_analyzing_heartbeat = False
                has_lang_selection = False

                while not has_lang_selection:
                    data = websocket.receive_json()
                    evt_type = data.get("event") or data.get("type")
                    events.append(data)
                    
                    if evt_type == "agent_heartbeat":
                        # Check that status is "analyzing_request" during metadata analysis
                        if data["data"]["status"] == "analyzing_request":
                            has_analyzing_heartbeat = True
                            self.assertGreaterEqual(data["data"]["elapsed_seconds"], 0)
                    
                    if evt_type == "language_selection_required":
                        has_lang_selection = True

                # 4. Assertions
                self.assertTrue(has_analyzing_heartbeat, "Failed to receive analyzing_request heartbeats during metadata extraction")
                self.assertTrue(has_lang_selection, "Failed to receive language_selection_required event")
                print(f"Metadata keepalive test passed! Received {len(events)} events, including analyzing_request heartbeats.")
        finally:
            adapter.analyze_prompt_for_project = original_analyze

    def test_tool_call_interceptor_unwrapping(self):
        # Verify that calling handle_function_call with a wrapped tool_call for a non-deferrable tool
        # is correctly unwrapped and executed.
        import model_tools
        from tools.registry import registry

        original_entry = registry.get_entry("search_files")
        
        called_args = []
        def mock_search_files_handler(args, **kwargs):
            called_args.append(args)
            return "Mocked search_files result"

        if original_entry:
            original_handler = original_entry.handler
            original_entry.handler = mock_search_files_handler
        else:
            original_handler = None

        try:
            res = model_tools.handle_function_call(
                function_name="tool_call",
                function_args={
                    "name": "search_files",
                    "arguments": {
                        "query": "test query",
                        "relative_path": "."
                    }
                }
            )

            self.assertEqual(res, "Mocked search_files result")
            self.assertEqual(len(called_args), 1)
            self.assertEqual(called_args[0].get("query"), "test query")
            print("Tool-call interceptor/unwrapping test passed successfully!")

        finally:
            if original_entry and original_handler:
                original_entry.handler = original_handler

if __name__ == "__main__":
    unittest.main()
