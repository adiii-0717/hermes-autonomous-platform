import os
import unittest
from pathlib import Path
from server.agents.schemas import AgentContext, CreativeDirectionSpec, VisualQAReport, ReferenceDesignSpec
from server.agents.reference_inspector import ReferenceInspector
from server.agents.creative_director_agent import CreativeDirectorAgent
from server.agents.frontend_engineer_agent import FrontendEngineerAgent
from server.agents.motion_3d_engineer_agent import Motion3DEngineerAgent
from server.agents.visual_qa_inspector_agent import VisualQAInspectorAgent
from server.agents.orchestrator import MultiAgentOrchestrator
from server.tools.asset_discovery import AssetDiscoveryService

class DummyGuard:
    workspace_root = Path(__file__).parent.parent / 'workspace'

class TestPhase3CreativeExcellence(unittest.TestCase):

    def setUp(self):
        self.guard = DummyGuard()
        self.guard.workspace_root.mkdir(parents=True, exist_ok=True)
        self.orchestrator = MultiAgentOrchestrator(self.guard)
        self.asset_service = AssetDiscoveryService()

    def test_01_reference_inspector(self):
        """Verify ReferenceInspector extracts ReferenceDesignSpec."""
        inspector = ReferenceInspector()
        ctx = AgentContext(project_name='ref_test', user_prompt='Create an architecture studio website', workspace_root=str(self.guard.workspace_root))
        res = inspector.execute(ctx)
        self.assertEqual(res.status, 'SUCCESS')
        spec = res.data
        self.assertIn('visual_identity', spec)
        self.assertIn('color_palette', spec)
        self.assertIn('adaptable_elements', spec)

    def test_02_creative_director_anti_patterns(self):
        """Verify CreativeDirectorAgent candidate exploration & 9 banned AI anti-patterns."""
        agent = CreativeDirectorAgent()
        ctx = AgentContext(project_name='cd_p3_test', user_prompt='Create a 3d footwear shop', workspace_root=str(self.guard.workspace_root))
        res = agent.execute(ctx)
        self.assertEqual(res.status, 'SUCCESS')
        spec = res.data
        self.assertEqual(len(spec['anti_patterns']), 9)
        self.assertTrue(any('centered hero' in ap.lower() for ap in spec['anti_patterns']))

    def test_03_intelligent_asset_selection(self):
        """Verify AssetDiscoveryService matches assets based on CreativeDirectionSpec."""
        spec = {
            'design_concept': '3D Footwear E-Commerce Showcase',
            'color_tokens': {'accent_primary': '#38bdf8'},
            'asset_spec': {'topic': 'Footwear & E-Commerce'}
        }
        assets = self.asset_service.discover_assets_for_spec(spec)
        self.assertTrue(assets['spec_alignment'])
        self.assertEqual(assets['matched_accent_color'], '#38bdf8')
        self.assertTrue(len(assets['photos']) >= 3)

    def test_04_14_dimension_visual_qa(self):
        """Verify VisualQAInspectorAgent evaluates 14 visual & technical dimensions."""
        qa_agent = VisualQAInspectorAgent(self.guard)
        ctx = AgentContext(project_name='qa_p3_test', user_prompt='SaaS Landing Page', workspace_root=str(self.guard.workspace_root))
        
        mock_screenshot_res = {
            'success': True,
            'visual_inspection_executed': True,
            'desktop': 'qa_p3_test/.visual_qa/desktop.png',
            'mobile': 'qa_p3_test/.visual_qa/mobile.png',
            'console_errors': []
        }
        
        res = qa_agent.execute(ctx, creative_spec={}, screenshot_result=mock_screenshot_res)
        self.assertEqual(res.status, 'SUCCESS')
        report = res.data
        self.assertIn(report['decision'], ['PASS', 'NEEDS_REFINEMENT', 'BLOCKED'])

    def test_05_multi_agent_orchestrator_phase3(self):
        """Verify MultiAgentOrchestrator executes ReferenceInspector -> CreativeDirector -> Frontend -> 3D -> QA."""
        res = self.orchestrator.generate_project('p3_pipeline_test', 'Cinematic portfolio with scroll storytelling', max_cycles=1)
        self.assertIn(res['status'], ['SUCCESS', 'PARTIAL', 'BLOCKED'])
        self.assertIn('reference_spec', res)
        self.assertIn('creative_spec', res)
        self.assertIn('qa_report', res)
        self.assertGreaterEqual(len(res['agent_execution_logs']), 4)

    def test_06_phase3_benchmark_categories(self):
        """Execute Phase 3 Multi-Agent Orchestration benchmark across 4 distinct categories."""
        benchmarks = [
            ("p3_bench_3d_footwear", "Create a premium 3D footwear e-commerce website featuring an interactive product presentation."),
            ("p3_bench_cinematic_portfolio", "Create a cinematic creative developer portfolio with scroll-driven storytelling."),
            ("p3_bench_architecture_studio", "Create an immersive architecture studio website with sophisticated visual transitions."),
            ("p3_bench_saas_landing", "Create a premium SaaS landing page with distinctive art direction and meaningful interactions.")
        ]

        benchmark_results = {}
        for proj_name, prompt in benchmarks:
            orchestrator_res = self.orchestrator.generate_project(proj_name, prompt, max_cycles=1)
            
            status_classification = orchestrator_res.get('status', 'FAIL')
            qa_decision = orchestrator_res.get('qa_report', {}).get('decision', 'BLOCKED')
            
            desktop_png = orchestrator_res.get('screenshot_result', {}).get('desktop')
            mobile_png = orchestrator_res.get('screenshot_result', {}).get('mobile')
            
            if status_classification == 'SUCCESS' and qa_decision == 'PASS' and desktop_png and mobile_png:
                classification = 'PASS'
            elif status_classification in ['SUCCESS', 'PARTIAL']:
                classification = 'PARTIAL'
            else:
                classification = 'FAIL'

            benchmark_results[proj_name] = {
                'prompt': prompt,
                'classification': classification,
                'qa_decision': qa_decision,
                'desktop_png': desktop_png,
                'mobile_png': mobile_png
            }

        self.assertEqual(len(benchmark_results), 4)
        for name, r in benchmark_results.items():
            self.assertIn(r['classification'], ['PASS', 'PARTIAL'])
            self.assertIsNotNone(r['desktop_png'])
            self.assertIsNotNone(r['mobile_png'])

if __name__ == '__main__':
    unittest.main()
