import os
import tempfile
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard

class TestWorkspaceSecurity(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.workspace_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_file_path(self):
        valid, resolved, err = self.guard.validate_path("src/index.js")
        self.assertTrue(valid)
        self.assertTrue(str(resolved).startswith(str(self.workspace_path)))

    def test_path_traversal_attack(self):
        traversal_paths = [
            "../outside.txt",
            "../../etc/passwd",
            "../../../secret",
            "/etc/passwd",
            "src/../../outside.txt"
        ]
        for path in traversal_paths:
            valid, resolved, err = self.guard.validate_path(path)
            self.assertFalse(valid, f"Path traversal attempt '{path}' should be blocked!")
            self.assertIn("Security Boundary Violation", err)

    def test_symlink_escape_attack(self):
        # Create a directory outside workspace
        outside_dir = tempfile.TemporaryDirectory()
        outside_path = Path(outside_dir.name).resolve()
        outside_file = outside_path / "sensitive.txt"
        outside_file.write_text("secret_data")

        # Create a symlink inside workspace pointing outside
        symlink_path = self.workspace_path / "malicious_link"
        os.symlink(str(outside_file), str(symlink_path))

        # Test validation on symlink
        valid, resolved, err = self.guard.validate_path("malicious_link")
        self.assertFalse(valid, "Symlink escaping workspace must be blocked by WorkspaceGuard!")
        self.assertIn("Security Boundary Violation", err)
        outside_dir.cleanup()

    def test_forbidden_commands(self):
        forbidden_cmds = [
            "rm -rf /",
            "mkfs /dev/sda1",
            "dd if=/dev/zero of=/dev/sda",
            "chmod -R 777 /",
            "cat /etc/passwd",
            "sudo rm -rf /var"
        ]
        for cmd in forbidden_cmds:
            risk_level, err = self.guard.classify_command(cmd)
            self.assertEqual(risk_level, "BLOCKED", f"Dangerous command '{cmd}' must be BLOCKED!")

    def test_approval_requiring_commands(self):
        approval_cmds = [
            "rm -rf build/",
            "mv file1.txt file2.txt",
            "git commit -m 'feat: update'",
            "npm install express"
        ]
        for cmd in approval_cmds:
            risk_level, err = self.guard.classify_command(cmd)
            self.assertEqual(risk_level, "REQUIRE_APPROVAL", f"High-risk command '{cmd}' must REQUIRE_APPROVAL!")

if __name__ == "__main__":
    unittest.main()
