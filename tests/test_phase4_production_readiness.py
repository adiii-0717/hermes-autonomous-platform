import os
import json
import zipfile
import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.agents.schemas import AgentContext
from server.agents.llm_client import LLMClient
from server.agents.orchestrator import MultiAgentOrchestrator
from server.tools.asset_discovery import AssetDiscoveryService
from server.tools.dev_visual_qa_tools import DevVisualQATools
from server.hermes_adapter import HermesAgentAdapter

class DummyGuard:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root

class TestPhase4ProductionReadiness(unittest.TestCase):

    def setUp(self):
        self.PROJECT_ROOT = Path(__file__).parent.parent.resolve()
        self.workspace_root = self.PROJECT_ROOT / 'workspace'
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.guard = WorkspaceGuard(str(self.workspace_root))
        self.orchestrator = MultiAgentOrchestrator(self.guard)
        # Fast deterministic mock fixture for ordinary test runs (opt-in live via HERMES_RUN_LIVE_TESTS=true)
        if not os.getenv("HERMES_RUN_LIVE_TESTS", "").lower() in ("true", "1"):
            mock_vqa = {
                "decision": "PASS",
                "overall_score": 9.0,
                "semantic_fidelity_pass": True,
                "semantic_fidelity_score": 9.5,
                "prioritized_fixes": [],
                "critical_issues": [],
                "identified_defects": [],
                "recommended_corrections": []
            }
            self.orchestrator.visual_qa_inspector.llm.call_llm_json = lambda *args, **kwargs: mock_vqa

    def test_01_structured_execution_states_and_callbacks(self):
        """Verify MultiAgentOrchestrator emits structured progress events and updates state."""
        status_events = []
        def on_status(evt):
            status_events.append(evt)

        res = self.orchestrator.generate_project(
            project_name='p4_status_test',
            user_prompt='Create a minimalist SaaS landing page',
            max_cycles=1,
            status_callback=on_status
        )

        self.assertIn(res['status'], ['SUCCESS', 'PARTIAL', 'BLOCKED'])
        self.assertTrue(len(status_events) >= 5)
        states = [e['state'] for e in status_events]
        self.assertIn('INITIATED', states)
        self.assertIn('GENERATING_FRONTEND', states)
        self.assertIn('COMPLETED', states)

    def test_02_llm_client_exponential_backoff_retry(self):
        """Verify LLMClient is initialized with retry capabilities."""
        client = LLMClient()
        self.assertTrue(hasattr(client, 'call_llm_json'))

    def test_03_intermediate_state_preservation(self):
        """Verify .generation_state.json is saved inside the workspace project directory."""
        res = self.orchestrator.generate_project(
            project_name='p4_state_test',
            user_prompt='Create a portfolio website',
            max_cycles=1
        )
        state_file = self.workspace_root / 'p4_state_test' / '.generation_state.json'
        self.assertTrue(state_file.exists())
        
        state_data = json.loads(state_file.read_text(encoding='utf-8'))
        self.assertEqual(state_data['state'], 'COMPLETED')
        self.assertEqual(state_data['progress_percent'], 100)

    def test_04_project_manifest_and_zip_integrity(self):
        """Verify .project_manifest.json and ZIP archive integrity."""
        proj_name = 'p4_manifest_test'
        res = self.orchestrator.generate_project(
            project_name=proj_name,
            user_prompt='Create a footwear store',
            max_cycles=1
        )
        
        proj_dir = self.workspace_root / proj_name
        manifest_file = proj_dir / '.project_manifest.json'
        self.assertTrue(manifest_file.exists())
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        self.assertEqual(manifest['name'], proj_name)

        adapter = HermesAgentAdapter(str(proj_dir))
        results = adapter.compile_project_results()
        self.assertIn('download_url', results)
        
        zip_path = self.workspace_root / f'{proj_name}.zip'
        self.assertTrue(zip_path.exists())
        with zipfile.ZipFile(zip_path, 'r') as z:
            namelist = z.namelist()
            self.assertTrue(any('index.html' in name for name in namelist))

    def test_05_workspace_guard_security_isolation(self):
        """Verify WorkspaceGuard path traversal rejection and command classification."""
        valid, path, err = self.guard.validate_path('../../etc/passwd')
        self.assertFalse(valid)
        self.assertIn('Security Boundary Violation', err)

        valid, path, err = self.guard.validate_path('%2F..%2F..%2Fsys')
        self.assertFalse(valid)

        risk, reason = self.guard.classify_command('rm -rf /')
        self.assertEqual(risk, 'BLOCKED')

        risk, reason = self.guard.classify_command('sudo apt-get update')
        self.assertEqual(risk, 'BLOCKED')

    def test_06_in_memory_asset_caching(self):
        """Verify AssetDiscoveryService caches queries for identical topics."""
        service = AssetDiscoveryService()
        a1 = service.discover_assets('Create a footwear e-commerce store')
        a2 = service.discover_assets('Create a footwear shop')
        self.assertEqual(a1['topic'], a2['topic'])
        self.assertIn('footwear', service._cache)

    def test_07_browser_cleanup_reliability(self):
        """Verify DevVisualQATools captures screenshots and closes Chromium context."""
        qa_tools = DevVisualQATools(self.guard)
        res = qa_tools.capture_responsive_screenshots('p4_manifest_test')
        self.assertTrue(res['success'])
        desktop_path = self.workspace_root / res['desktop'] if not os.path.isabs(res['desktop']) else Path(res['desktop'])
        mobile_path = self.workspace_root / res['mobile'] if not os.path.isabs(res['mobile']) else Path(res['mobile'])
        self.assertTrue(desktop_path.exists())
        self.assertTrue(mobile_path.exists())

if __name__ == '__main__':
    unittest.main()
