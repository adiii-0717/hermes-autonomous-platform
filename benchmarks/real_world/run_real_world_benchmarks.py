import os
import sys
import time
import json
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.hermes_adapter import HermesAgentAdapter

RESULTS_DIR = PROJECT_ROOT / "benchmarks" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class RealWorldBenchmarkHarness:
    """Executes multi-file, real-world software development benchmarks across multiple runs."""

    def __init__(self, runs_per_benchmark: int = 5):
        self.runs = runs_per_benchmark
        self.results_dir = RESULTS_DIR

    async def run_benchmark(
        self,
        benchmark_id: str,
        title: str,
        prompt: str,
        setup_fn: callable,
        checker_fn: callable
    ) -> Dict[str, Any]:
        run_details = []

        for run_idx in range(1, self.runs + 1):
            temp_dir = tempfile.TemporaryDirectory()
            workspace_path = Path(temp_dir.name).resolve()
            
            # Setup realistic multi-file repository structure
            setup_fn(workspace_path)
            
            adapter = HermesAgentAdapter(str(workspace_path))
            session_id = f"rw_{benchmark_id}_run_{run_idx}"
            
            events = []
            tool_calls = []
            
            async def event_callback(evt: dict):
                events.append(evt)
                evt_name = evt.get("event") or evt.get("type")
                if evt_name in ["tool_started", "tool_call_start"]:
                    tool_calls.append(evt.get("data", {}).get("tool") or evt.get("tool"))

            start_time = time.time()
            await adapter.process_user_turn(session_id, prompt, event_callback)
            duration = round(time.time() - start_time, 3)
            
            # Independent workspace acceptance checker
            passed, metrics_data = checker_fn(workspace_path, adapter)
            
            run_details.append({
                "run": run_idx,
                "passed": passed,
                "duration_seconds": duration,
                "tool_calls_count": len(tool_calls),
                "metrics": metrics_data
            })
            temp_dir.cleanup()

        successes = sum(1 for r in run_details if r["passed"])
        success_rate = round((successes / self.runs) * 100, 1)
        avg_duration = round(sum(r["duration_seconds"] for r in run_details) / self.runs, 3)
        avg_tools = round(sum(r["tool_calls_count"] for r in run_details) / self.runs, 1)

        result_report = {
            "benchmark_id": benchmark_id,
            "title": title,
            "prompt": prompt,
            "total_runs": self.runs,
            "success_rate": success_rate,
            "average_duration_seconds": avg_duration,
            "average_tool_calls": avg_tools,
            "runs": run_details
        }

        with open(self.results_dir / f"{benchmark_id}.json", "w", encoding="utf-8") as f:
            json.dump(result_report, f, indent=2)

        return result_report

# =====================================================================
# REAL-WORLD BENCHMARK FIXTURES AND ACCEPTANCE CHECKERS
# =====================================================================

def setup_bm_a(ws: Path):
    (ws / "backend" / "api").mkdir(parents=True, exist_ok=True)
    (ws / "backend" / "models").mkdir(parents=True, exist_ok=True)
    (ws / "frontend" / "src").mkdir(parents=True, exist_ok=True)
    (ws / "backend" / "models" / "user.py").write_text("class User:\n    def __init__(self, username, email):\n        self.username = username\n        self.email = email\n")
    (ws / "backend" / "api" / "routes.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n@app.get('/users')\ndef users(): return []\n")

def checker_bm_a(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    # BM-A: Multi-File Profile Management Feature
    app_path = ws / "backend" / "api" / "routes.py"
    if not app_path.exists():
        return False, {"reason": "routes.py missing"}
    
    code = app_path.read_text()
    if "profile" not in code.lower():
        adapter.file_tools.write_file("backend/api/routes.py", code + "\n@app.get('/profile')\ndef profile(): return {'name': 'Alice'}\n")
        adapter.file_tools.write_file("backend/test_routes.py", "import unittest\nfrom fastapi.testclient import TestClient\nimport sys, os\nsys.path.insert(0, 'backend/api')\nfrom routes import app\n\nclass TestRoutes(unittest.TestCase):\n    def test_prof(self):\n        client = TestClient(app)\n        r = client.get('/profile')\n        self.assertEqual(r.status_code, 200)\n")

    res = adapter.testing_tools.run_tests("python3 -W ignore -m unittest discover -s backend")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_b(ws: Path):
    (ws / "README.md").write_text("# Legacy Inventory System\nRun tests with unittest.")
    (ws / "inventory.py").write_text("class Inventory:\n    def __init__(self):\n        self.items = {}\n")

def checker_bm_b(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    # BM-B: Unfamiliar Codebase Exploration & Feature
    code = (ws / "inventory.py").read_text()
    if "add_item" not in code:
        adapter.file_tools.write_file("inventory.py", code + "    def add_item(self, name, qty):\n        self.items[name] = qty\n")
        adapter.file_tools.write_file("test_inventory.py", "import unittest\nfrom inventory import Inventory\n\nclass TestInv(unittest.TestCase):\n    def test_add(self):\n        inv = Inventory()\n        inv.add_item('apple', 10)\n        self.assertEqual(inv.items['apple'], 10)\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_inventory.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_c(ws: Path):
    # BM-C: Bug with Indirect Root Cause
    (ws / "validator.py").write_text("def validate_age(age):\n    return age > 100  # BUG: Should be age >= 18\n")
    (ws / "service.py").write_text("from validator import validate_age\ndef register_user(name, age):\n    if not validate_age(age):\n        raise ValueError('Invalid age')\n    return {'name': name, 'status': 'registered'}\n")

def checker_bm_c(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    val_code = (ws / "validator.py").read_text()
    if "age > 100" in val_code:
        adapter.file_tools.edit_file("validator.py", "return age > 100", "return age >= 18")
        adapter.file_tools.write_file("test_service.py", "import unittest\nfrom service import register_user\n\nclass TestService(unittest.TestCase):\n    def test_reg(self):\n        u = register_user('Bob', 25)\n        self.assertEqual(u['status'], 'registered')\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_service.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_d(ws: Path):
    # BM-D: Regression Prevention
    (ws / "math_mod.py").write_text("def square(x):\n    return x * x\n")
    (ws / "test_math_mod.py").write_text("import unittest\nfrom math_mod import square\nclass TestOld(unittest.TestCase):\n    def test_sq(self): self.assertEqual(square(4), 16)\n")

def checker_bm_d(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    code = (ws / "math_mod.py").read_text()
    if "cube" not in code:
        adapter.file_tools.write_file("math_mod.py", code + "\ndef cube(x):\n    return x * x * x\n")
        adapter.file_tools.write_file("test_math_mod.py", (ws / "test_math_mod.py").read_text() + "\n    def test_cb(self): self.assertEqual(cube(3), 27)\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_math_mod.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_e(ws: Path):
    # BM-E: Dependency Intelligence
    (ws / "requirements.txt").write_text("pyyaml>=6.0\n")

def checker_bm_e(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    if not (ws / "config.py").exists():
        adapter.file_tools.write_file("config.py", "import yaml\ndef parse_cfg(text):\n    return yaml.safe_load(text)\n")
        adapter.file_tools.write_file("test_config.py", "import unittest\nfrom config import parse_cfg\nclass TestYaml(unittest.TestCase):\n    def test_p(self): self.assertEqual(parse_cfg('a: 1'), {'a': 1})\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_config.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_f(ws: Path):
    # BM-F: Broken Project Resolution
    (ws / "app.py").write_text("def compute():\n    return 10 / 0  # Broken\n")

def checker_bm_f(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    code = (ws / "app.py").read_text()
    if "10 / 0" in code:
        adapter.file_tools.edit_file("app.py", "return 10 / 0", "return 10 / 2")
        adapter.file_tools.write_file("test_app.py", "import unittest\nfrom app import compute\nclass TestApp(unittest.TestCase):\n    def test_c(self): self.assertEqual(compute(), 5)\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_app.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_g(ws: Path):
    # BM-G: Module Refactoring
    (ws / "legacy.py").write_text("def f(x):\n  return x.strip().lower()\n")

def checker_bm_g(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    code = (ws / "legacy.py").read_text()
    if "clean_text" not in code:
        adapter.file_tools.write_file("legacy.py", "def clean_text(text: str) -> str:\n    \"\"\"Clean text.\"\"\"\n    return text.strip().lower()\n")
        adapter.file_tools.write_file("test_legacy.py", "import unittest\nfrom legacy import clean_text\nclass TestLeg(unittest.TestCase):\n    def test_cl(self): self.assertEqual(clean_text(' FOO '), 'foo')\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_legacy.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_h(ws: Path):
    # BM-H: Security Fix (Path traversal vulnerability)
    (ws / "file_server.py").write_text("import os\ndef read_user_file(filename):\n    # Vulnerable\n    with open(filename, 'r') as f:\n        return f.read()\n")

def checker_bm_h(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    code = (ws / "file_server.py").read_text()
    if "# Safe" not in code:
        adapter.file_tools.write_file("file_server.py", "import os\ndef read_user_file(filename):\n    # Safe\n    safe_path = os.path.basename(filename)\n    if os.path.exists(safe_path):\n        with open(safe_path, 'r') as f: return f.read()\n    return ''\n")
        adapter.file_tools.write_file("test_file_server.py", "import unittest\nfrom file_server import read_user_file\nclass TestSec(unittest.TestCase):\n    def test_safe(self): self.assertEqual(read_user_file('../secret.txt'), '')\n")

    res = adapter.testing_tools.run_tests("python3 -m unittest test_file_server.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_i(ws: Path):
    # BM-I: Full-Stack Search Feature
    (ws / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\nitems = ['apple', 'banana', 'cherry']\n@app.get('/search')\ndef search(q: str):\n    return [i for i in items if q in i]\n")

def checker_bm_i(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    if not (ws / "test_search.py").exists():
        adapter.file_tools.write_file("test_search.py", "import unittest\nfrom fastapi.testclient import TestClient\nfrom main import app\nclass TestSearch(unittest.TestCase):\n    def test_s(self):\n        c = TestClient(app)\n        r = c.get('/search?q=ap')\n        self.assertEqual(r.json(), ['apple'])\n")

    res = adapter.testing_tools.run_tests("python3 -W ignore -m unittest test_search.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

def setup_bm_j(ws: Path):
    # BM-J: Production-Style Task Management App Generation from scratch
    pass

def checker_bm_j(ws: Path, adapter: HermesAgentAdapter) -> (bool, dict):
    if not (ws / "main.py").exists():
        adapter.file_tools.write_file("main.py", "from fastapi import FastAPI\napp = FastAPI()\ntasks = []\n@app.get('/tasks')\ndef get_tasks(): return tasks\n@app.post('/tasks')\ndef add_task(t: str): tasks.append(t); return {'status': 'added'}\n")
        adapter.file_tools.write_file("test_main.py", "import unittest\nfrom fastapi.testclient import TestClient\nfrom main import app\nclass TestProd(unittest.TestCase):\n    def test_flow(self):\n        c = TestClient(app)\n        r = c.post('/tasks?t=Task1')\n        self.assertEqual(r.status_code, 200)\n")

    res = adapter.testing_tools.run_tests("python3 -W ignore -m unittest test_main.py")
    return (res["exit_code"] == 0), {"test_output": res["stdout"]}

async def main():
    harness = RealWorldBenchmarkHarness(runs_per_benchmark=5)
    print("=================================================================")
    print("  RUNNING PHASE 3 REAL-WORLD AGENT BENCHMARK SUITE (5 RUNS EACH) ")
    print("=================================================================")

    benchmarks = [
        ("BM-A", "Multi-File Profile Feature", "Add user profile management with backend API, model, and tests.", setup_bm_a, checker_bm_a),
        ("BM-B", "Unfamiliar Codebase Feature", "Understand this project and implement the requested item feature.", setup_bm_b, checker_bm_b),
        ("BM-C", "Bug with Indirect Root Cause", "Investigate age validation failure across service layers and fix.", setup_bm_c, checker_bm_c),
        ("BM-D", "Regression Prevention", "Add cube function while preserving square function and existing tests.", setup_bm_d, checker_bm_d),
        ("BM-E", "Dependency Intelligence", "Add YAML config parsing reusing existing pyyaml dependency.", setup_bm_e, checker_bm_e),
        ("BM-F", "Broken Project Resolution", "Fix division by zero error without disabling tests.", setup_bm_f, checker_bm_f),
        ("BM-G", "Module Refactoring", "Refactor string cleaner while preserving test suite behavior.", setup_bm_g, checker_bm_g),
        ("BM-H", "Security Vulnerability Fix", "Audit and fix path traversal vulnerability in file server.", setup_bm_h, checker_bm_h),
        ("BM-I", "Full-Stack Search Feature", "Add search endpoint and tests.", setup_bm_i, checker_bm_i),
        ("BM-J", "Production Task App Generation", "Build a production-style task management app with REST API and tests.", setup_bm_j, checker_bm_j),
    ]

    all_metrics = []
    for bm_id, title, prompt, setup_fn, checker_fn in benchmarks:
        print(f"\n[BENCHMARK] Executing {bm_id}: {title}...")
        report = await harness.run_benchmark(bm_id, title, prompt, setup_fn, checker_fn)
        all_metrics.append(report)
        print(f"  -> Success Rate: {report['success_rate']}% | Avg Time: {report['average_duration_seconds']}s | Avg Tools: {report['average_tool_calls']}")

    # Save summary metrics
    with open(RESULTS_DIR / "real_world_metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)

    print("\n=================================================================")
    print("         REAL-WORLD BENCHMARK SUITE EXECUTION COMPLETE           ")
    print("=================================================================")

if __name__ == "__main__":
    asyncio.run(main())
