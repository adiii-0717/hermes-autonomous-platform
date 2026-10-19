import os
import sys
import unittest
import asyncio
from pathlib import Path

from server.security.workspace_guard import WorkspaceGuard
from server.security.container_runner import ContainerRunner
from server.tools.dev_terminal_tools import DevTerminalTools

class TestPhase51FailClosedSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('/tmp/hermes_p51_test_workspace').resolve()
        os.makedirs(self.test_dir, exist_ok=True)
        self.guard = WorkspaceGuard(str(self.test_dir))

    def test_docker_unavailable_production_mode_fails_closed(self):
        os.environ['HERMES_ENV'] = 'production'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'false'
        os.environ['HERMES_ENABLE_DOCKER'] = 'false'
        
        runner = ContainerRunner(workspace_guard=self.guard)
        res = asyncio.run(runner.execute_command('echo hello'))
        
        self.assertFalse(res['success'])
        self.assertEqual(res['isolation_mode'], 'sandbox_unavailable_failed_closed')
        self.assertIn('Security Error', res['stderr'])

    def test_production_mode_host_fallback_impossible(self):
        # Even if allow_host_fallback is true, production mode enforces fail-closed
        os.environ['HERMES_ENV'] = 'production'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'true'
        os.environ['HERMES_ENABLE_DOCKER'] = 'false'
        
        runner = ContainerRunner(workspace_guard=self.guard)
        res = asyncio.run(runner.execute_command('echo hello'))
        
        self.assertFalse(res['success'])
        self.assertEqual(res['isolation_mode'], 'sandbox_unavailable_failed_closed')

    def test_explicit_development_mode_permitted(self):
        os.environ['HERMES_ENV'] = 'development'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'true'
        os.environ['HERMES_ENABLE_DOCKER'] = 'false'
        
        runner = ContainerRunner(workspace_guard=self.guard)
        res = asyncio.run(runner.execute_command('echo dev_fallback_ok'))
        
        self.assertTrue(res['success'])
        self.assertEqual(res['isolation_mode'], 'host_bounded_development')
        self.assertIn('dev_fallback_ok', res['stdout'])

    def test_container_creation_failure_fails_closed(self):
        os.environ['HERMES_ENV'] = 'production'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'false'
        os.environ['HERMES_ENABLE_DOCKER'] = 'true'
        os.environ['HERMES_DOCKER_IMAGE'] = 'nonexistent_invalid_image_12345'
        
        runner = ContainerRunner(workspace_guard=self.guard)
        res = asyncio.run(runner.execute_command('echo hello'))
        
        self.assertFalse(res['success'])
        self.assertIn(res['isolation_mode'], ['docker_container_failed', 'sandbox_unavailable_failed_closed', 'container_creation_failed_closed'])

    def test_sandbox_runtime_failure_fails_closed(self):
        os.environ['HERMES_ENV'] = 'production'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'false'
        os.environ['HERMES_ENABLE_DOCKER'] = 'true'
        os.environ['HERMES_SANDBOX_RUNTIME'] = 'invalid_sandbox_runtime'
        
        runner = ContainerRunner(workspace_guard=self.guard)
        res = asyncio.run(runner.execute_command('echo hello'))
        
        self.assertFalse(res['success'])
        self.assertIn(res['isolation_mode'], ['docker_container_failed', 'sandbox_unavailable_failed_closed', 'container_creation_failed_closed'])

    def test_existing_workflow_preservation(self):
        os.environ['HERMES_ENV'] = 'development'
        os.environ['HERMES_ALLOW_HOST_FALLBACK'] = 'true'
        os.environ['HERMES_ENABLE_DOCKER'] = 'false'
        
        terminal = DevTerminalTools(workspace_guard=self.guard, approval_controller=None)
        res = asyncio.run(terminal.execute_command('echo workflow_ok'))
        
        self.assertTrue(res['success'])
        self.assertIn('workflow_ok', res['stdout'])

if __name__ == '__main__':
    unittest.main()