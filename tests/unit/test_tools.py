import os
import tempfile
import unittest
import asyncio
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.security.approval_controller import ApprovalController
from server.tools.dev_file_tools import DevFileTools
from server.tools.dev_terminal_tools import DevTerminalTools
from server.tools.dev_testing_tools import DevTestingTools
from server.tools.dev_git_tools import DevGitTools

class TestDevTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.root_path))
        self.approval = ApprovalController()
        
        self.file_tools = DevFileTools(self.guard)
        self.term_tools = DevTerminalTools(self.guard, self.approval)
        self.test_tools = DevTestingTools(self.guard)
        self.git_tools = DevGitTools(self.guard)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_file_operations(self):
        # 1. Write file
        w_res = self.file_tools.write_file("hello.txt", "Hello World\nLine 2")
        self.assertIn("Successfully wrote", w_res)

        # 2. Read file
        content = self.file_tools.read_file("hello.txt")
        self.assertIn("Hello World", content)

        # 3. Edit file
        e_res = self.file_tools.edit_file("hello.txt", "World", "Hermes")
        self.assertIn("Successfully updated", e_res)
        self.assertIn("Hello Hermes", self.file_tools.read_file("hello.txt"))

        # 4. Search files
        s_res = self.file_tools.search_files("Hermes")
        self.assertIn("hello.txt", s_res)

        # 5. List directory
        dirs = self.file_tools.list_directory(".")
        self.assertIn("hello.txt", dirs)

    def test_terminal_command_execution(self):
        res = asyncio.run(self.term_tools.execute_command("echo 'Hermes Test'"))
        self.assertTrue(res["success"])
        self.assertIn("Hermes Test", res["stdout"])

    def test_testing_tools(self):
        self.file_tools.write_file("dummy.py", "x = 1\n")
        res = self.test_tools.run_build("python3 -m py_compile dummy.py")
        self.assertTrue(res["success"])

if __name__ == "__main__":
    unittest.main()
