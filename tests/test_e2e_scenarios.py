import os
import shutil
import asyncio
import tempfile
import unittest
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestEndToEndScenarios(unittest.TestCase):

    def setUp(self):
        self.base_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.base_dir.name).resolve()

    def tearDown(self):
        self.base_dir.cleanup()

    def test_e2e_scenario_1_feature_addition(self):
        """E2E Test 1: Analyze project, add multiply function, create tests, and execute."""
        project_dir = self.root_path / "project_1"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        calc_file = project_dir / "calculator.py"
        calc_file.write_text("def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n")

        adapter = HermesAgentAdapter(str(project_dir))

        async def run_scenario():
            events = []
            async def event_handler(evt):
                events.append(evt)

            req = "Analyze calculator.py, add a multiply(a, b) function, write test_calculator.py, and run the tests."
            await adapter.process_user_turn("session_e2e_1", req, event_handler)

            # 1. Read calculator.py
            read_res = adapter.file_tools.read_file("calculator.py")
            self.assertIn("def add", read_res)

            # 2. Add multiply function
            edit_res = adapter.file_tools.write_file("calculator.py", "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n")
            self.assertIn("Successfully wrote", edit_res)

            # 3. Create test file
            test_content = "import unittest\nfrom calculator import add, subtract, multiply\n\nclass TestCalculator(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n    def test_multiply(self):\n        self.assertEqual(multiply(4, 5), 20)\n"
            adapter.file_tools.write_file("test_calculator.py", test_content)

            # 4. Run tests
            test_res = adapter.testing_tools.run_tests("python3 -m unittest test_calculator.py")
            self.assertEqual(test_res["exit_code"], 0)

        asyncio.run(run_scenario())

    def test_e2e_scenario_2_debugging(self):
        """E2E Test 2: Debug intentionally broken code, fix it, write test, and verify."""
        project_dir = self.root_path / "project_2"
        project_dir.mkdir(parents=True, exist_ok=True)

        broken_file = project_dir / "math_utils.py"
        broken_file.write_text("def add(a, b):\n    return a - b  # BUG: subtracts instead of adding\n")

        adapter = HermesAgentAdapter(str(project_dir))

        async def run_scenario():
            events = []
            async def event_handler(evt):
                events.append(evt)

            # Step 1: Identify and fix bug
            fix_res = adapter.file_tools.edit_file("math_utils.py", "return a - b", "return a + b")
            self.assertIn("Successfully updated", fix_res)

            # Step 2: Write test to verify fix
            test_code = "import unittest\nfrom math_utils import add\n\nclass TestMath(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(10, 5), 15)\n"
            adapter.file_tools.write_file("test_math.py", test_code)

            # Step 3: Run test suite
            test_res = adapter.testing_tools.run_tests("python3 -m unittest test_math.py")
            self.assertEqual(test_res["exit_code"], 0)

        asyncio.run(run_scenario())

    def test_e2e_scenario_3_fullstack_creation(self):
        """E2E Test 3: Create small project from scratch with REST API health endpoint and tests."""
        project_dir = self.root_path / "project_3"
        project_dir.mkdir(parents=True, exist_ok=True)

        adapter = HermesAgentAdapter(str(project_dir))

        async def run_scenario():
            # 1. Create app.py
            app_code = "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {'status': 'ok'}\n"
            adapter.file_tools.write_file("app.py", app_code)

            # 2. Create test_app.py
            test_code = "import unittest\nfrom fastapi.testclient import TestClient\nfrom app import app\n\nclass TestHealth(unittest.TestCase):\n    def setUp(self):\n        self.client = TestClient(app)\n    def test_health(self):\n        res = self.client.get('/health')\n        self.assertEqual(res.status_code, 200)\n        self.assertEqual(res.json(), {'status': 'ok'})\n"
            adapter.file_tools.write_file("test_app.py", test_code)

            # 3. Execute tests
            test_res = adapter.testing_tools.run_tests("python3 -W ignore -m unittest test_app.py")
            self.assertEqual(test_res["exit_code"], 0, f"Fullstack test execution failed: {test_res['stderr']}")

        asyncio.run(run_scenario())

if __name__ == "__main__":
    unittest.main()
