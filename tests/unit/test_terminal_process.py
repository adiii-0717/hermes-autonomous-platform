import tempfile
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.security.approval_controller import ApprovalController
from server.tools.dev_terminal_tools import DevTerminalTools

class TestTerminalProcess(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.root_path))
        self.approval = ApprovalController()
        self.term_tools = DevTerminalTools(self.guard, self.approval)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_background_process_lifecycle(self):
        start_res = self.term_tools.start_background_process("python3 -c 'import time; time.sleep(1)'")
        self.assertTrue(start_res["success"])
        proc_id = start_res["process_id"]
        self.assertIsNotNone(start_res["pid"])

        status_res = self.term_tools.get_process_status(proc_id)
        self.assertTrue(status_res["success"])
        self.assertEqual(status_res["process_id"], proc_id)

        all_status = self.term_tools.get_process_status()
        self.assertTrue(all_status["success"])
        self.assertGreaterEqual(all_status["total_processes"], 1)

        kill_res = self.term_tools.kill_process(proc_id)
        self.assertTrue(kill_res["success"])

if __name__ == "__main__":
    unittest.main()
