import os
import tempfile
import unittest
import asyncio
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestE2EScenarios(unittest.TestCase):

    def setUp(self):
        self.base_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.base_dir.name).resolve()
        self.adapter = HermesAgentAdapter(str(self.workspace_path))

    def tearDown(self):
        self.base_dir.cleanup()

    def test_e2e_feature_addition(self):
        self.adapter.file_tools.write_file("calculator.py", "def add(a, b):\n    return a + b\n")

        events = []
        async def event_callback(evt): events.append(evt)

        asyncio.run(self.adapter.process_user_turn(
            "sess_e2e_1",
            "Add multiplication support to calculator.py and run tests",
            event_callback
        ))

        self.assertTrue(any(e.get("event") == "assistant_message" for e in events))

    def test_e2e_debugging(self):
        self.adapter.file_tools.write_file("math_utils.py", "def add(a, b):\n    return a - b  # BUG\n")

        events = []
        async def event_callback(evt): events.append(evt)

        asyncio.run(self.adapter.process_user_turn(
            "sess_e2e_2",
            "Investigate failing application in math_utils.py, fix bug, and run tests",
            event_callback
        ))

        self.assertTrue(any(e.get("event") == "assistant_message" for e in events))

if __name__ == "__main__":
    unittest.main()
