import unittest
import json
import tempfile
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestProjectContinuation(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.test_dir.name)
        self.workspace_dir = self.project_root / "workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Create a Python simple calculator project
        self.calc_dir = self.workspace_dir / "simple_calculator"
        self.calc_dir.mkdir(parents=True, exist_ok=True)
        self.calc_manifest = {
            "project_id": "simple_calculator",
            "name": "simple_calculator",
            "languages": ["Python"]
        }
        with open(self.calc_dir / ".project_manifest.json", "w") as f:
            json.dump(self.calc_manifest, f)
            
        # 2. Create a TypeScript scientific calculator project
        self.sci_calc_dir = self.workspace_dir / "scientific_calculator"
        self.sci_calc_dir.mkdir(parents=True, exist_ok=True)
        self.sci_manifest = {
            "project_id": "scientific_calculator",
            "name": "scientific_calculator",
            "languages": ["TypeScript"]
        }
        with open(self.sci_calc_dir / ".project_manifest.json", "w") as f:
            json.dump(self.sci_manifest, f)

        # Instantiate adapter pointing to our mock project root
        self.adapter = HermesAgentAdapter(str(self.project_root))
        
    def tearDown(self):
        self.test_dir.cleanup()

    def test_discover_projects(self):
        projects = self.adapter.discover_projects()
        self.assertEqual(len(projects), 2)
        names = {p["name"] for p in projects}
        self.assertEqual(names, {"simple_calculator", "scientific_calculator"})

    def test_single_match(self):
        matches = self.adapter.find_matching_projects("add square root to the Python calculator")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "simple_calculator")
        self.assertEqual(matches[0]["language"], "Python")

    def test_ambiguous_matches(self):
        matches = self.adapter.find_matching_projects("Add advanced features to my calculator project")
        self.assertEqual(len(matches), 2)
        names = {p["name"] for p in matches}
        self.assertEqual(names, {"simple_calculator", "scientific_calculator"})

    def test_no_matches_fallback(self):
        matches = self.adapter.find_matching_projects("Build an email validator app from scratch")
        self.assertEqual(len(matches), 0)

    def test_isolation_boundary_check(self):
        guard = self.adapter.workspace_guard
        valid, real_path, err = guard.validate_path("calculator.py")
        self.assertTrue(valid)
        
        valid, real_path, err = guard.validate_path("../../../etc/passwd")
        self.assertFalse(valid)
        self.assertIn("Security Boundary Violation", err)
