import tempfile
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_review_tools import DevReviewTools
from server.tools.dev_health_tools import DevHealthTools

class TestHealthAndReview(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.root_path))
        self.review_tools = DevReviewTools(self.guard)
        self.health_tools = DevHealthTools(self.guard)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_review_changes(self):
        res = self.review_tools.review_changes()
        self.assertIn("has_changes", res)

    def test_check_project_health(self):
        (self.root_path / "main.py").write_text("print('health check')\n")
        health_res = self.health_tools.check_project_health()
        
        self.assertIn("project_name", health_res)
        self.assertIn("build_healthy", health_res)
        self.assertIn("tests_healthy", health_res)

if __name__ == "__main__":
    unittest.main()
