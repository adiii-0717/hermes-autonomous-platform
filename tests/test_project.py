import os
import tempfile
import unittest
from pathlib import Path
from server.project import ProjectDetector, ProjectAnalyzer, DependencyAnalyzer, StructureAnalyzer

class TestProjectIntelligence(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name).resolve()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_python_fastapi_project_detection(self):
        (self.root_path / "requirements.txt").write_text("fastapi>=0.100.0\nuvicorn\npsycopg2\npytest\n")
        (self.root_path / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
        (self.root_path / "test_main.py").write_text("def test_dummy(): pass\n")

        detector = ProjectDetector(self.root_path)
        self.assertIn("Python", detector.detect_languages())
        self.assertIn("FastAPI", detector.detect_frameworks())
        self.assertIn("pip", detector.detect_package_managers())
        self.assertIn("PostgreSQL", detector.detect_databases())
        self.assertIn("pytest", detector.detect_test_frameworks())

    def test_javascript_react_project_detection(self):
        pkg_data = """{
            "name": "react-app",
            "dependencies": { "react": "^18.0.0", "express": "^4.18.0" },
            "devDependencies": { "vitest": "^1.0.0" }
        }"""
        (self.root_path / "package.json").write_text(pkg_data)
        (self.root_path / "src").mkdir()
        (self.root_path / "src" / "App.jsx").write_text("export default function App() { return <div>App</div>; }")

        detector = ProjectDetector(self.root_path)
        self.assertIn("JavaScript", detector.detect_languages())
        self.assertIn("React", detector.detect_frameworks())
        self.assertIn("Express", detector.detect_frameworks())
        self.assertIn("npm", detector.detect_package_managers())
        self.assertIn("Vitest", detector.detect_test_frameworks())

    def test_project_manifest_generation(self):
        (self.root_path / "pyproject.toml").write_text("[tool.poetry]\nname = 'demo'\n")
        (self.root_path / "app.py").write_text("print('hello')\n")

        analyzer = ProjectAnalyzer(self.root_path)
        manifest = analyzer.generate_manifest()

        self.assertEqual(manifest["name"], self.root_path.name)
        self.assertIn("Python", manifest["languages"])
        self.assertIn("app.py", manifest["entry_points"])
        self.assertTrue((self.root_path / ".project_manifest.json").exists())

    def test_dependency_analyzer(self):
        (self.root_path / "requirements.txt").write_text("requests==2.31.0\npytest\n")
        dep_analyzer = DependencyAnalyzer(self.root_path)

        self.assertTrue(dep_analyzer.is_dependency_installed("requests", "python"))
        self.assertTrue(dep_analyzer.is_dependency_installed("pytest", "python"))
        self.assertFalse(dep_analyzer.is_dependency_installed("nonexistent_pkg", "python"))

    def test_structure_analyzer(self):
        (self.root_path / "src").mkdir()
        (self.root_path / "src" / "index.js").write_text("// entry")
        (self.root_path / "node_modules").mkdir()
        (self.root_path / "node_modules" / "secret.js").write_text("// hidden")

        struct_analyzer = StructureAnalyzer(self.root_path)
        tree = struct_analyzer.get_project_structure()

        self.assertIn("src/", tree)
        self.assertIn("index.js", tree)
        self.assertNotIn("node_modules/", tree)

if __name__ == "__main__":
    unittest.main()
