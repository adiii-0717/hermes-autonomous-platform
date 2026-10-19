import os
import sys
import unittest
import asyncio
from pathlib import Path
import httpx

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.project.project_server_manager import ProjectServerManager, project_server_manager
from server.main import app

class TestProjectServerManager(unittest.TestCase):
    def setUp(self):
        self.psm = ProjectServerManager()

    def test_find_free_port(self):
        port = self.psm.find_free_port()
        self.assertGreaterEqual(port, 8090)
        self.assertLessEqual(port, 8190)

    def test_detect_server_cmd_static_dist(self):
        project_dir = PROJECT_ROOT / 'workspace' / 'grocery_store_website'
        cmd, server_type = self.psm.detect_server_cmd(project_dir, 8095)
        self.assertIn('8095', cmd)
        self.assertTrue(server_type in ['static_dist', 'vite', 'static_html'])

    def test_ensure_project_server_grocery_website(self):
        server_info = self.psm.ensure_project_server('grocery_store_website')
        self.assertEqual(server_info.get('status'), 'READY')
        self.assertIsNotNone(server_info.get('port'))
        self.assertTrue(self.psm.is_server_alive('grocery_store_website'))
        self.psm.stop_project_server('grocery_store_website')

    def test_fastapi_preview_proxy_endpoint(self):
        async def run_test():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
                resp = await client.get('/preview/grocery_store_website/')
                self.assertEqual(resp.status_code, 200)
                self.assertIn('text/html', resp.headers.get('content-type', ''))
                has_base = ('base href=' in resp.text)
                self.assertTrue(has_base)
        asyncio.run(run_test())

    def test_hermes_adapter_includes_preview_url(self):
        from server.hermes_adapter import HermesAgentAdapter
        adapter = HermesAgentAdapter(PROJECT_ROOT / 'workspace' / 'grocery_store_website')
        results = adapter.compile_project_results()
        self.assertIn('preview_url', results)
        self.assertEqual(results['preview_url'], f'/preview/{adapter.workspace_path.name}/')
        self.assertIn('server_status', results)

if __name__ == '__main__':
    unittest.main()
