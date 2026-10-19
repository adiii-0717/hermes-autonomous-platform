import os
import unittest
from pathlib import Path
from server.agents.schemas import AgentContext, CreativeDirectionSpec, VisualQAReport
from server.agents.creative_director_agent import CreativeDirectorAgent
from server.agents.frontend_engineer_agent import FrontendEngineerAgent
from server.agents.motion_3d_engineer_agent import Motion3DEngineerAgent
from server.agents.visual_qa_inspector_agent import VisualQAInspectorAgent
from server.agents.orchestrator import MultiAgentOrchestrator
from server.hermes_adapter import HermesAgentAdapter

class DummyGuard:
    workspace_root = Path(__file__).parent.parent / 'workspace'

class TestPhase2Orchestration(unittest.TestCase):

    def setUp(self):
        self.guard = DummyGuard()
        self.guard.workspace_root.mkdir(parents=True, exist_ok=True)
        self.orchestrator = MultiAgentOrchestrator(self.guard)

    def test_01_creative_director_spec_schema(self):
        """Verify Agent A (Creative Director) produces valid CreativeDirectionSpec."""
        agent = CreativeDirectorAgent()
        ctx = AgentContext(project_name='cd_test', user_prompt='Create a 3d footwear shoe shop', workspace_root=str(self.guard.workspace_root))
        res = agent.execute(ctx)
        self.assertEqual(res.status, 'SUCCESS')
        spec = res.data
        self.assertIn('design_concept', spec)
        self.assertIn('visual_identity', spec)
        self.assertIn('color_tokens', spec)
        self.assertTrue(spec['requires_3d'])
        self.assertIn('model_url', spec['three_d_spec'])

    def test_02_frontend_engineer_handoff(self):
        """Verify Agent B (Frontend Engineer) receives CreativeDirectionSpec and builds UI HTML."""
        cd_agent = CreativeDirectorAgent()
        fe_agent = FrontendEngineerAgent()
        ctx = AgentContext(project_name='fe_test', user_prompt='Minimalist portfolio website', workspace_root=str(self.guard.workspace_root))
        
        spec_res = cd_agent.execute(ctx)
        fe_res = fe_agent.execute(ctx, creative_spec=spec_res.data)
        
        self.assertEqual(fe_res.status, 'SUCCESS')
        proj_dir = self.guard.workspace_root / 'fe_test'
        index_html = proj_dir / 'index.html'
        self.assertTrue(index_html.exists())
        content = index_html.read_text(encoding='utf-8')
        self.assertIn('<!DOCTYPE html>', content)

    def test_03_motion_3d_engineer_conditional_delegation(self):
        """Verify Agent C (3D Engineer) embeds WebGL canvas and Three.js scene when 3D is requested."""
        fe_agent = FrontendEngineerAgent()
        m3d_agent = Motion3DEngineerAgent()
        ctx = AgentContext(project_name='m3d_test', user_prompt='3D interactive shoe showcase', workspace_root=str(self.guard.workspace_root))
        
        fe_agent.execute(ctx, creative_spec={'color_tokens': {}, 'asset_spec': {}})
        m3d_res = m3d_agent.execute(ctx, creative_spec={'requires_3d': True})
        
        self.assertEqual(m3d_res.status, 'SUCCESS')
        self.assertEqual(m3d_res.data.get('status'), 'ENHANCED')
        
        index_html = self.guard.workspace_root / 'm3d_test' / 'index.html'
        content = index_html.read_text(encoding='utf-8')
        self.assertIn('THREE.WebGLRenderer', content)
        self.assertIn('THREE.GLTFLoader', content)

    def test_04_visual_qa_inspector_report_schema(self):
        """Verify Agent D (Visual QA Inspector) evaluates screenshots and produces VisualQAReport."""
        qa_agent = VisualQAInspectorAgent(self.guard)
        ctx = AgentContext(project_name='qa_test', user_prompt='SaaS Landing Page', workspace_root=str(self.guard.workspace_root))
        
        mock_screenshot_res = {
            'success': True,
            'visual_inspection_executed': True,
            'desktop': 'qa_test/.visual_qa/desktop.png',
            'mobile': 'qa_test/.visual_qa/mobile.png',
            'console_errors': []
        }
        
        res = qa_agent.execute(ctx, creative_spec={}, screenshot_result=mock_screenshot_res)
        self.assertEqual(res.status, 'SUCCESS')
        report = res.data
        self.assertEqual(report['decision'], 'PASS')
        self.assertGreaterEqual(report['overall_score'], 8.0)

    def test_05_bounded_refinement_loop_termination(self):
        """Verify MultiAgentOrchestrator respects max_refinement_cycles limit."""
        res = self.orchestrator.generate_project('bounded_loop_test', 'Test SaaS page', max_cycles=2)
        self.assertIn(res['status'], ['SUCCESS', 'PARTIAL', 'BLOCKED'])
        self.assertLessEqual(res['refinement_cycles_executed'], 2)
        self.assertIn('creative_spec', res)
        self.assertIn('qa_report', res)

    def test_06_phase2_benchmark_prompts(self):
        """Execute Phase 2 Multi-Agent Orchestration benchmark across 4 prompts."""
        benchmarks = [
            ("p2_bench_3d_footwear", "Create a premium 3D footwear e-commerce website with an interactive product presentation."),
            ("p2_bench_cinematic_portfolio", "Create a cinematic creative developer portfolio with scroll-driven storytelling."),
            ("p2_bench_architecture_studio", "Create an immersive architecture studio website with sophisticated visual transitions."),
            ("p2_bench_saas_landing", "Create a premium SaaS landing page with distinctive art direction and meaningful interactions.")
        ]

        benchmark_results = {}
        for proj_name, prompt in benchmarks:
            orchestrator_res = self.orchestrator.generate_project(proj_name, prompt, max_cycles=2)
            
            status_classification = orchestrator_res.get('status', 'FAIL')
            qa_decision = orchestrator_res.get('qa_report', {}).get('decision', 'BLOCKED')
            
            desktop_png = orchestrator_res.get('screenshot_result', {}).get('desktop')
            mobile_png = orchestrator_res.get('screenshot_result', {}).get('mobile')
            
            if status_classification == 'SUCCESS' and qa_decision == 'PASS' and desktop_png and mobile_png:
                classification = 'PASS'
            elif status_classification == 'SUCCESS':
                classification = 'PARTIAL'
            else:
                classification = 'FAIL'

            benchmark_results[proj_name] = {
                'prompt': prompt,
                'classification': classification,
                'qa_decision': qa_decision,
                'cycles': orchestrator_res.get('refinement_cycles_executed', 1),
                'desktop_png': desktop_png,
                'mobile_png': mobile_png,
                'agents_run': [l['agent_name'] for l in orchestrator_res.get('agent_execution_logs', [])]
            }

        self.assertEqual(len(benchmark_results), 4)
        for name, r in benchmark_results.items():
            self.assertIn(r['classification'], ['PASS', 'PARTIAL', 'FAIL'])
            self.assertIsNotNone(r['desktop_png'])
            self.assertIsNotNone(r['mobile_png'])

if __name__ == '__main__':
    unittest.main()
