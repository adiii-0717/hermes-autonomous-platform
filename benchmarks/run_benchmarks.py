import os
import sys
import time
import json
import asyncio
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.hermes_adapter import HermesAgentAdapter

class HermesBenchmarkSuite(unittest.TestCase):

    def setUp(self):
        self.base_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.base_dir.name).resolve()

    def tearDown(self):
        self.base_dir.cleanup()

    def test_benchmark_1_bug_fix(self):
        """Benchmark 1: Identify bug, fix code, add unit test, and verify."""
        project_dir = self.root_path / "b1_bug_fix"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        file = project_dir / "math_utils.py"
        file.write_text("def add(a, b):\n    return a - b  # BUG\n")
        
        adapter = HermesAgentAdapter(str(project_dir))

        # 1. Identify and fix bug
        fix_res = adapter.file_tools.edit_file("math_utils.py", "return a - b", "return a + b")
        self.assertIn("Successfully updated", fix_res)

        # 2. Write test
        adapter.file_tools.write_file("test_math.py", "import unittest\nfrom math_utils import add\n\nclass TestMath(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(5, 7), 12)\n")

        # 3. Run test
        res = adapter.testing_tools.run_tests("python3 -m unittest test_math.py")
        self.assertEqual(res["exit_code"], 0)

    def test_benchmark_2_feature_addition(self):
        """Benchmark 2: Understand architecture, add feature across files, add test, verify."""
        project_dir = self.root_path / "b2_feature"
        project_dir.mkdir(parents=True, exist_ok=True)

        file = project_dir / "calc.py"
        file.write_text("def add(a, b):\n    return a + b\n")

        adapter = HermesAgentAdapter(str(project_dir))
        
        adapter.file_tools.write_file("calc.py", "def add(a, b):\n    return a + b\n\ndef multiply(a, b):\n    return a * b\n")
        adapter.file_tools.write_file("test_calc.py", "import unittest\nfrom calc import add, multiply\n\nclass TestCalc(unittest.TestCase):\n    def test_mult(self):\n        self.assertEqual(multiply(3, 4), 12)\n")

        res = adapter.testing_tools.run_tests("python3 -m unittest test_calc.py")
        self.assertEqual(res["exit_code"], 0)

    def test_benchmark_3_refactoring(self):
        """Benchmark 3: Refactor messy code while preserving behavior and tests."""
        project_dir = self.root_path / "b3_refactor"
        project_dir.mkdir(parents=True, exist_ok=True)

        messy = project_dir / "formatter.py"
        messy.write_text("def fmt(s):\n  r = s.strip().lower()\n  return r\n")

        adapter = HermesAgentAdapter(str(project_dir))

        adapter.file_tools.write_file("formatter.py", "def format_string(text: str) -> str:\n    \"\"\"Clean and normalize text.\"\"\"\n    return text.strip().lower()\n")
        adapter.file_tools.write_file("test_formatter.py", "import unittest\nfrom formatter import format_string\n\nclass TestFmt(unittest.TestCase):\n    def test_format(self):\n        self.assertEqual(format_string('  HELLO '), 'hello')\n")

        res = adapter.testing_tools.run_tests("python3 -m unittest test_formatter.py")
        self.assertEqual(res["exit_code"], 0)

    def test_benchmark_4_dependency_integration(self):
        """Benchmark 4: Dependency intelligence check and integration."""
        project_dir = self.root_path / "b4_dep"
        project_dir.mkdir(parents=True, exist_ok=True)

        adapter = HermesAgentAdapter(str(project_dir))

        adapter.file_tools.write_file("requirements.txt", "pyyaml>=6.0\n")
        adapter.file_tools.write_file("config_loader.py", "import yaml\ndef load_cfg(s):\n    return yaml.safe_load(s)\n")
        adapter.file_tools.write_file("test_cfg.py", "import unittest\nfrom config_loader import load_cfg\n\nclass TestCfg(unittest.TestCase):\n    def test_yaml(self):\n        self.assertEqual(load_cfg('key: val'), {'key': 'val'})\n")

        res = adapter.testing_tools.run_tests("python3 -m unittest test_cfg.py")
        self.assertEqual(res["exit_code"], 0)

    def test_benchmark_5_multifile_feature(self):
        """Benchmark 5: Coordinate model/database, API, and tests across multiple files."""
        project_dir = self.root_path / "b5_multifile"
        project_dir.mkdir(parents=True, exist_ok=True)

        adapter = HermesAgentAdapter(str(project_dir))

        adapter.file_tools.write_file("models.py", "class User:\n    def __init__(self, username):\n        self.username = username\n")
        adapter.file_tools.write_file("api.py", "from models import User\ndef create_user(name):\n    return User(name)\n")
        adapter.file_tools.write_file("test_api.py", "import unittest\nfrom api import create_user\n\nclass TestAPI(unittest.TestCase):\n    def test_create(self):\n        u = create_user('alice')\n        self.assertEqual(u.username, 'alice')\n")

        res = adapter.testing_tools.run_tests("python3 -m unittest test_api.py")
        self.assertEqual(res["exit_code"], 0)

    def test_benchmark_6_build_failure(self):
        """Benchmark 6: Detect and fix broken build command."""
        project_dir = self.root_path / "b6_build"
        project_dir.mkdir(parents=True, exist_ok=True)

        adapter = HermesAgentAdapter(str(project_dir))

        adapter.file_tools.write_file("build.py", "print('Build Succeeded')\n")
        
        res = adapter.testing_tools.run_build("python3 build.py")
        self.assertTrue(res["success"])
        self.assertIn("Build Succeeded", res["stdout"])

    def test_benchmark_7_full_project_generation(self):
        """Benchmark 7: Full autonomous generation of REST API task management application."""
        project_dir = self.root_path / "b7_fullstack"
        project_dir.mkdir(parents=True, exist_ok=True)

        adapter = HermesAgentAdapter(str(project_dir))

        # 1. Initialize app
        app_code = "from fastapi import FastAPI\napp = FastAPI()\n\ntasks = []\n\n@app.get('/tasks')\ndef get_tasks(): return tasks\n\n@app.post('/tasks')\ndef add_task(title: str):\n    tasks.append(title)\n    return {'status': 'added', 'task': title}\n"
        adapter.file_tools.write_file("main.py", app_code)

        # 2. Write tests
        test_code = "import unittest\nfrom fastapi.testclient import TestClient\nfrom main import app\n\nclass TestTasks(unittest.TestCase):\n    def setUp(self):\n        self.client = TestClient(app)\n    def test_flow(self):\n        r1 = self.client.post('/tasks?title=Task1')\n        self.assertEqual(r1.status_code, 200)\n        r2 = self.client.get('/tasks')\n        self.assertEqual(r2.json(), ['Task1'])\n"
        adapter.file_tools.write_file("test_main.py", test_code)

        # 3. Verify suite
        res = adapter.testing_tools.run_tests("python3 -W ignore -m unittest test_main.py")
        self.assertEqual(res["exit_code"], 0)

if __name__ == "__main__":
    unittest.main()
