import os
import sys
import unittest
import asyncio
from pathlib import Path

from server.security.workspace_guard import WorkspaceGuard
from server.security.container_runner import ContainerRunner
from server.tools.dev_terminal_tools import DevTerminalTools

class TestPhase5ContainerSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('/tmp/hermes_p5_test_workspace').resolve()
        os.makedirs(self.test_dir, exist_ok=True)
        # Enable development mode for container runner unit testing host fallback logic
        os.environ['HERMES_ENV'] = 'development'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'true'
        self.guard = WorkspaceGuard(str(self.test_dir))
        self.runner = ContainerRunner(workspace_guard=self.guard)
        self.terminal = DevTerminalTools(workspace_guard=self.guard, approval_controller=None)

    def test_docker_command_building_security_flags(self):
        cmd_list = self.runner.build_docker_command('echo hello', str(self.test_dir))
        cmd_str = ' '.join(cmd_list)
        
        self.assertIn('--cpus 1.0', cmd_str)
        self.assertIn('--memory 512m', cmd_str)
        self.assertIn('--pids-limit 64', cmd_str)
        self.assertIn('--cap-drop ALL', cmd_str)
        self.assertIn('--security-opt no-new-privileges:true', cmd_str)
        self.assertIn('--read-only', cmd_str)
        self.assertIn(f'-v {os.path.realpath(str(self.test_dir))}:/workspace:rw', cmd_str)

    def test_forbidden_command_blocking(self):
        res = asyncio.run(self.runner.execute_command('rm -rf /'))
        self.assertFalse(res['success'])
        self.assertEqual(res['isolation_mode'], 'blocked_by_guard')
        self.assertIn('Security Policy Error', res['stderr'])

    def test_bounded_execution_environment_sanitization(self):
        os.environ['GEMINI_API_KEY'] = 'secret_gemini_key_12345'
        res = asyncio.run(self.runner.execute_command("python3 -c 'import os; print(os.getenv(\"GEMINI_API_KEY\"))'" ))
        self.assertTrue(res['success'], msg=f"Error: {res.get('stderr')}")
        self.assertIn('None', res['stdout'])
        self.assertNotIn('secret_gemini_key_12345', res['stdout'])

    def test_timeout_enforcement(self):
        res = asyncio.run(self.runner.execute_command('sleep 5', timeout=1))
        self.assertFalse(res['success'])
        self.assertIn('timed out', res['stderr'])

    def test_dev_terminal_tools_integration(self):
        res = asyncio.run(self.terminal.execute_command('echo hermes_p5_ok'))
        self.assertTrue(res['success'])
        self.assertIn('hermes_p5_ok', res['stdout'])
        self.assertIn(res['isolation_mode'], ['docker_container', 'host_bounded_development', 'host_bounded_fallback'])

if __name__ == '__main__':
    unittest.main()