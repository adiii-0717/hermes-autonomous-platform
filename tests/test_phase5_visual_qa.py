"""
Phase 5 Verification Tests: Visual QA & Bounded Refinement Cycle.
Verifies visual QA inspection, technical layout auditing, deficiency detection,
bounded refinement cycle execution, and final status verification.
"""

import unittest
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_visual_qa_tools import DevVisualQATools

class TestPhase5VisualQA(unittest.TestCase):

    def setUp(self):
        self.test_dir = PROJECT_ROOT / "workspace" / "test_phase5_workspace"
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.guard = WorkspaceGuard(str(self.test_dir))
        self.visual_qa = DevVisualQATools(self.guard)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_visual_qa_detects_missing_viewport_and_refines(self):
        # Create un-refined HTML file missing viewport meta tag
        unrefined_html = "<html><head><title>Unrefined Page</title></head><body><h1>Hello World</h1></body></html>"
        (self.test_dir / "index.html").write_text(unrefined_html, encoding="utf-8")

        # Run initial technical QA -> Should fail due to missing viewport
        initial_tech_qa = self.visual_qa.run_technical_visual_qa(".")
        self.assertFalse(initial_tech_qa["passed"])

        # Run bounded refinement cycle
        refine_result = self.visual_qa.perform_bounded_refinement_cycle(".")
        
        self.assertTrue(refine_result["refinement_performed"])
        self.assertGreater(len(refine_result["fixes_applied"]), 0)
        
        # Verify the HTML file now has viewport meta tag
        updated_content = (self.test_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("viewport", updated_content.lower())
        
        # Final QA must now pass
        self.assertTrue(refine_result["final_qa"]["passed"])

    def test_non_web_project_handled_honestly(self):
        # No HTML files
        (self.test_dir / "script.py").write_text("print('hello')", encoding="utf-8")
        
        qa_result = self.visual_qa.run_full_visual_qa(".", auto_refine=False)
        self.assertFalse(qa_result["is_web_project"])
        self.assertEqual(qa_result["technical_qa"]["issues"], [])

if __name__ == "__main__":
    unittest.main()
