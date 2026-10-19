import os
import tempfile
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard

class TestWorkspaceSecurityBoundary(unittest.TestCase):

    def setUp(self):
        self.base_dir = tempfile.TemporaryDirectory()
        self.outside_dir = tempfile.TemporaryDirectory()
        
        self.workspace_path = Path(self.base_dir.name).resolve()
        self.outside_path = Path(self.outside_dir.name).resolve()

        self.guard = WorkspaceGuard(str(self.workspace_path))

    def tearDown(self):
        self.base_dir.cleanup()
        self.outside_dir.cleanup()

    def test_valid_workspace_file_access(self):
        valid, resolved, err = self.guard.validate_path("app.py")
        self.assertTrue(valid)
        self.assertEqual(resolved, (self.workspace_path / "app.py").resolve())
        self.assertFalse(bool(err))

    def test_relative_path_traversal_blocked(self):
        valid, resolved, err = self.guard.validate_path("../../outside.txt")
        self.assertFalse(valid)
        self.assertIn("Security Boundary Violation", err)

    def test_symlink_escape_protection(self):
        outside_file = self.outside_path / "secret.txt"
        outside_file.write_text("TOP SECRET")

        link_path = self.workspace_path / "malicious_link"
        try:
            os.symlink(str(outside_file), str(link_path))
        except OSError:
            self.skipTest("Symlink creation failed due to platform OS restrictions.")

        valid, resolved, err = self.guard.validate_path("malicious_link")
        self.assertFalse(valid)
        self.assertIn("Security Boundary Violation", err)

    def test_command_risk_classification(self):
        safe_level, _ = self.guard.classify_command("python3 -m unittest")
        self.assertEqual(safe_level, "ALLOWED")

        appr_level, _ = self.guard.classify_command("rm -rf build/")
        self.assertEqual(appr_level, "REQUIRE_APPROVAL")

        block_level, _ = self.guard.classify_command("rm -rf /")
        self.assertEqual(block_level, "BLOCKED")

if __name__ == "__main__":
    unittest.main()
