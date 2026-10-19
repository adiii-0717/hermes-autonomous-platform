import unittest
import tempfile
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.security.approval_controller import ApprovalController
from server.tools.dev_testing_tools import DevTestingTools
from server.tools.dev_ast_tools import DevASTTools
from server.debug.error_memory import ErrorMemory
from tools.daemon_pool import DaemonThreadPoolExecutor

class TestSystemRegressionSuite(unittest.TestCase):
    """Regression test suite covering security, AST, test classification, error memory, and daemon pool."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name).resolve()
        self.guard = WorkspaceGuard(str(self.workspace))
        self.approval = ApprovalController()
        self.ast_tools = DevASTTools(self.guard)
        self.testing_tools = DevTestingTools(self.guard)
        self.error_memory = ErrorMemory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_workspace_guard_path_traversal(self):
        # 1. Path traversal attempt outside workspace
        outside_path = "../outside.txt"
        is_safe, _, _ = self.guard.validate_path(outside_path)
        self.assertFalse(is_safe)

        # 2. Safe inside workspace
        inside_path = "inside.txt"
        is_safe, _, _ = self.guard.validate_path(inside_path)
        self.assertTrue(is_safe)

    def test_approval_controller_pending_approvals(self):
        # Verify approval controller pending approvals state initialization
        self.assertEqual(len(self.approval.pending_approvals), 0)

    def test_classify_test_failure(self):
        # 1. Test assertion failure classification
        test_err = self.testing_tools.classify_test_failure("AssertionError: 1 != 2", "")
        self.assertEqual(test_err, "TEST_ERROR")

        # 2. Dependency error classification
        dep_err = self.testing_tools.classify_test_failure("ModuleNotFoundError: No module named 'foo'", "")
        self.assertEqual(dep_err, "DEPENDENCY_ERROR")

        # 3. Code syntax error classification
        code_err = self.testing_tools.classify_test_failure("SyntaxError: invalid syntax", "")
        self.assertEqual(code_err, "CODE_ERROR")

    def test_find_related_tests(self):
        # Create source and corresponding test file
        src_file = self.workspace / "book_service.py"
        src_file.write_text("def service(): pass")
        
        test_file = self.workspace / "test_book_service.py"
        test_file.write_text("def test_service(): pass")

        related = self.testing_tools.find_related_tests("book_service.py")
        self.assertTrue(isinstance(related, list))
        self.assertTrue(len(related) > 0)
        self.assertIn("test_book_service.py", related)

    def test_error_memory_recording_and_formatting(self):
        # Record error and check formatted history
        session_id = "test_session_123"
        self.error_memory.record_error(
            session_id=session_id,
            error_text="SyntaxError: invalid syntax",
            root_cause="Missing colon in def statement",
            attempted_fix="Added colon",
            result="Fixed"
        )
        history = self.error_memory.get_error_history(session_id)
        self.assertEqual(len(history), 1)
        formatted = self.error_memory.format_history_for_context(session_id)
        self.assertIn("SyntaxError", formatted)
        self.assertIn("Missing colon", formatted)

    def test_daemon_pool_executor_python314(self):
        # Verify DaemonThreadPoolExecutor initializes and submits tasks without exception
        executor = DaemonThreadPoolExecutor(max_workers=2)
        future = executor.submit(lambda x: x * 2, 21)
        result = future.result(timeout=2.0)
        executor.shutdown(wait=True)
        self.assertEqual(result, 42)

if __name__ == "__main__":
    unittest.main()
