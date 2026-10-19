import os
import tempfile
import asyncio
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.security.approval_controller import ApprovalController
from server.tools.dev_file_tools import DevFileTools
from server.tools.dev_terminal_tools import DevTerminalTools
from server.tools.dev_testing_tools import DevTestingTools
from server.tools.dev_git_tools import DevGitTools

class TestDevelopmentTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.workspace_path))
        self.approval = ApprovalController()
        
        self.file_tools = DevFileTools(self.guard)
        self.terminal_tools = DevTerminalTools(self.guard, self.approval)
        self.testing_tools = DevTestingTools(self.guard)
        self.git_tools = DevGitTools(self.guard)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_file_operations(self):
        # 1. Write file
        write_res = self.file_tools.write_file("test.py", "def main():\n    print('Hello World')\n")
        self.assertIn("Successfully wrote", write_res)

        # 2. Read file
        read_res = self.file_tools.read_file("test.py")
        self.assertIn("Hello World", read_res)

        # 3. Edit file
        edit_res = self.file_tools.edit_file("test.py", "Hello World", "Hermes Agent")
        self.assertIn("Successfully updated", edit_res)
        read_res_2 = self.file_tools.read_file("test.py")
        self.assertIn("Hermes Agent", read_res_2)

        # 4. Search files
        search_res = self.file_tools.search_files("Hermes")
        self.assertIn("test.py", search_res)

        # 5. List directory
        list_res = self.file_tools.list_directory(".")
        self.assertIn("FILE  test.py", list_res)

    def test_terminal_execution(self):
        async def run_exec():
            res = await self.terminal_tools.execute_command("echo 'Testing Terminal Execution'")
            self.assertTrue(res["success"])
            self.assertEqual(res["exit_code"], 0)
            self.assertIn("Testing Terminal Execution", res["stdout"])

        asyncio.run(run_exec())

    def test_background_process_lifecycle(self):
        start_res = self.terminal_tools.start_background_process("echo 'Background Job Done'")
        self.assertTrue(start_res["success"])
        proc_id = start_res["process_id"]
        
        output_res = self.terminal_tools.get_process_output(proc_id)
        self.assertTrue(output_res["success"])

    def test_testing_and_build_tools(self):
        # Write dummy python test
        self.file_tools.write_file("test_sample.py", "def test_pass(): assert True\n")
        
        test_res = self.testing_tools.run_tests("python3 -m unittest discover -s .")
        self.assertIn("exit_code", test_res)
        
        build_res = self.testing_tools.run_build("echo 'Build completed'")
        self.assertTrue(build_res["success"])
        self.assertIn("Build completed", build_res["stdout"])

    def test_git_tools(self):
        status_res = self.git_tools.git_status()
        self.assertIsNotNone(status_res)

if __name__ == "__main__":
    unittest.main()
