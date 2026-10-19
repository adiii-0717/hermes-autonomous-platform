import unittest
import shutil
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_visual_qa_tools import DevVisualQATools
from server.hermes_adapter import HermesAgentAdapter

class TestMilestone3RefinementLoop(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("workspace/test_m3_project")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.guard = WorkspaceGuard(Path.cwd())
        self.tools = DevVisualQATools(self.guard)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_bounded_refinement_fixes_issues(self):
        html_file = self.test_dir / "index.html"
        css_file = self.test_dir / "style.css"

        # Intentionally missing viewport & css tokens
        html_file.write_text("<!DOCTYPE html><html><head></head><body><h1>Test M3</h1></body></html>")
        css_file.write_text("button { color: red; }")

        # Run 1: Should fail
        res1 = self.tools.run_technical_visual_qa("test_m3_project")
        self.assertFalse(res1["passed"])

        # Simulate refinement step 1 (adds viewport & CSS tokens)
        html_content = html_file.read_text()
        html_file.write_text(html_content.replace("<head>", "<head>\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"))
        css_file.write_text(":root { --bg-primary: #fff; }\nbutton { color: red; }:hover { opacity:0.8; }\n@import url(\"https://fonts.googleapis.com\");")

        # Run 2: Should pass
        res2 = self.tools.run_technical_visual_qa("test_m3_project")
        self.assertTrue(res2["passed"])

    def test_compile_results_includes_visual_qa(self):
        adapter = HermesAgentAdapter(str(self.test_dir))
        results = adapter.compile_project_results()
        self.assertIn("visual_qa", results)
        self.assertIn("is_web_project", results["visual_qa"])

if __name__ == "__main__":
    unittest.main()
