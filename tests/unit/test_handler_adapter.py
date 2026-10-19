import os
import tempfile
import unittest
import asyncio
import json
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter
from tools.registry import registry

class TestHandlerAdapter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_path = Path(self.temp_dir.name).resolve()
        # Instantiating the adapter registers the wrapped custom tools into registry
        self.adapter = HermesAgentAdapter(str(self.workspace_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_write_file_adapted_signature(self):
        # Dispatch write_file with Hermes convention: handler(args, **metadata)
        args = {
            "path": "hello.txt",
            "content": "Hello World!"
        }
        res = registry.dispatch(
            "write_file",
            args,
            task_id="test-task-123",
            session_id="test-session-456",
            user_task="Write a greetings file"
        )
        self.assertIn("Successfully wrote", res)

        # Check if the file was actually written to the workspace
        file_path = self.workspace_path / "hello.txt"
        self.assertTrue(file_path.is_file())
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "Hello World!")

    def test_read_file_adapted_signature(self):
        # First write the file directly
        file_path = self.workspace_path / "hello.txt"
        with open(file_path, "w") as f:
            f.write("Hello from test!")

        # Dispatch read_file with Hermes convention: handler(args, **metadata)
        args = {
            "path": "hello.txt"
        }
        res = registry.dispatch(
            "read_file",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        self.assertIn("Hello from test!", res)

    def test_search_files_adapted_signature(self):
        # Write some files
        (self.workspace_path / "file1.txt").write_text("UniqueKeyword here")
        (self.workspace_path / "file2.txt").write_text("Regular file")

        # Dispatch search_files with Hermes convention: handler(args, **metadata)
        args = {
            "query": "UniqueKeyword",
            "relative_path": "."
        }
        res = registry.dispatch(
            "search_files",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        self.assertIn("file1.txt", res)

    def test_async_execute_command_adapted_signature(self):
        # Dispatch execute_command (async) with Hermes convention
        args = {
            "command": "echo 'Async Command Success'",
            "timeout": 10
        }
        # Note: registry.dispatch automatically runs async handlers via _run_async
        # so dispatch() returns the resolved value directly.
        res = registry.dispatch(
            "execute_command",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        # Parse the JSON normalized output
        res_dict = json.loads(res)
        self.assertTrue(res_dict["success"])
        self.assertIn("Async Command Success", res_dict["stdout"])

    def test_write_file_missing_argument(self):
        # Missing 'content'
        args = {"path": "hello.txt"}
        res = registry.dispatch(
            "write_file",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        self.assertIn("Missing required argument 'content'", res)

        # Missing 'path'
        args = {"content": "some content"}
        res2 = registry.dispatch(
            "write_file",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        self.assertIn("Missing required argument 'path'", res2)

    def test_read_file_missing_argument(self):
        # Missing 'path'
        args = {}
        res = registry.dispatch(
            "read_file",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        self.assertIn("Missing required argument 'path'", res)

    def test_async_execute_command_missing_argument(self):
        # Missing 'command'
        args = {"timeout": 10}
        res = registry.dispatch(
            "execute_command",
            args,
            task_id="test-task-123",
            session_id="test-session-456"
        )
        self.assertIn("Missing required argument 'command'", res)

if __name__ == "__main__":
    unittest.main()
