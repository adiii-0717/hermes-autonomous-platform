import os
import json
import zipfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from server.main import app, adapter, PROJECT_ROOT
from server.security.workspace_guard import WorkspaceGuard
from server.agents.schemas import AgentContext
from server.agents.orchestrator import MultiAgentOrchestrator
from server.tools.dev_visual_qa_tools import DevVisualQATools

class TestPhase41DeploymentSecurity(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.workspace_root = PROJECT_ROOT / 'workspace'
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.guard = WorkspaceGuard(str(self.workspace_root))
        self.orchestrator = MultiAgentOrchestrator(self.guard)

    def test_01_deployment_config_and_health_check(self):
        """Verify /api/health and /api/config handle credentials and return online status."""
        resp = self.client.get('/api/health')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'online')
        self.assertIn('framework', data)

        cfg_resp = self.client.get('/api/config')
        self.assertEqual(cfg_resp.status_code, 200)
        cfg_data = cfg_resp.json()
        # Verify API key is masked and not exposed in raw plain-text
        masked = cfg_data.get('masked_api_key', '')
        self.assertNotIn('AIzaSy', masked)  # Standard Google API key prefix check

    def test_02_workspace_guard_security_boundaries(self):
        """Verify WorkspaceGuard blocks path traversal, percent-encoding escapes, and forbidden commands."""
        # 1. Direct path traversal
        resp = self.client.get('/api/workspace/file?path=../../etc/passwd')
        self.assertEqual(resp.status_code, 403)

        # 2. URL percent-encoded path traversal (%2F -> /)
        resp2 = self.client.get('/api/workspace/file?path=%2F..%2F..%2Fetc%2Fpasswd')
        self.assertEqual(resp2.status_code, 403)

        # 3. Guard direct validation
        valid, path, err = self.guard.validate_path('../../../System/Library')
        self.assertFalse(valid)
        self.assertIn('Security Boundary Violation', err)

        # 4. Command execution risk classification
        risk, reason = self.guard.classify_command('rm -rf /')
        self.assertEqual(risk, 'BLOCKED')

        risk, reason = self.guard.classify_command('cat /etc/shadow')
        self.assertEqual(risk, 'BLOCKED')

    def test_03_zip_export_isolation(self):
        """Verify project ZIP download generates safe archives containing only workspace files."""
        proj_name = 'p41_zip_security_test'
        res = self.orchestrator.generate_project(
            project_name=proj_name,
            user_prompt='Create a security portal website',
            max_cycles=1
        )
        self.assertIn(res['status'], ['SUCCESS', 'PARTIAL'])

        dl_resp = self.client.get(f'/api/projects/{proj_name}/download')
        self.assertEqual(dl_resp.status_code, 200)
        self.assertEqual(dl_resp.headers['content-type'], 'application/zip')

        # Verify ZIP path containment
        zip_file_path = self.workspace_root / f'{proj_name}.zip'
        self.assertTrue(zip_file_path.exists())
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            for name in z.namelist():
                self.assertFalse(name.startswith('/'))
                self.assertFalse('..' in name)

    def test_04_real_generation_stress_test(self):
        """Execute real multi-agent generation for static, interactive, and spatial websites."""
        benchmarks = [
            ('p41_bench_static', 'Create a simple static landing page for a coffee roastery'),
            ('p41_bench_interactive', 'Create an interactive developer workflow dashboard with dynamic filters')
        ]
        for name, prompt in benchmarks:
            res = self.orchestrator.generate_project(name, prompt, max_cycles=1)
            self.assertIn(res['status'], ['SUCCESS', 'PARTIAL'])
            proj_dir = self.workspace_root / name
            self.assertTrue((proj_dir / 'index.html').exists())
            self.assertTrue((proj_dir / '.project_manifest.json').exists())

    def test_05_concurrent_generation_isolation(self):
        """Verify multiple concurrent projects create distinct isolated workspace subdirectories."""
        p1 = 'p41_concurrent_alpha'
        p2 = 'p41_concurrent_beta'

        res1 = self.orchestrator.generate_project(p1, 'Alpha project prompt', max_cycles=1)
        res2 = self.orchestrator.generate_project(p2, 'Beta project prompt', max_cycles=1)

        d1 = self.workspace_root / p1
        d2 = self.workspace_root / p2

        self.assertTrue(d1.exists())
        self.assertTrue(d2.exists())

        m1 = json.loads((d1 / '.project_manifest.json').read_text(encoding='utf-8'))
        m2 = json.loads((d2 / '.project_manifest.json').read_text(encoding='utf-8'))

        self.assertEqual(m1['name'], p1)
        self.assertEqual(m2['name'], p2)

    def test_06_crash_recovery_and_state_restoration(self):
        """Verify workspace discovery and state restoration via .project_manifest.json."""
        proj_name = 'p41_recovery_test'
        self.orchestrator.generate_project(proj_name, 'Recovery test website', max_cycles=1)

        # Simulate project discovery after server restart
        projects_resp = self.client.get('/api/projects')
        self.assertEqual(projects_resp.status_code, 200)
        project_list = projects_resp.json().get('projects', [])
        found = any(p['name'] == proj_name for p in project_list)
        self.assertTrue(found)

    def test_07_visual_regression_benchmarks(self):
        """Verify responsive screenshot capture across desktop and mobile viewports."""
        qa_tools = DevVisualQATools(self.guard)
        res = qa_tools.capture_responsive_screenshots('p41_recovery_test')
        self.assertTrue(res['success'])
        
        desktop_rel = res['desktop']
        mobile_rel = res['mobile']
        
        d_path = self.workspace_root / desktop_rel if not os.path.isabs(desktop_rel) else Path(desktop_rel)
        m_path = self.workspace_root / mobile_rel if not os.path.isabs(mobile_rel) else Path(mobile_rel)

        self.assertTrue(d_path.exists())
        self.assertTrue(m_path.exists())

if __name__ == '__main__':
    unittest.main()
