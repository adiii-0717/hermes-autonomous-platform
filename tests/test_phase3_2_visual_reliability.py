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

class DummyGuard:
    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent / 'workspace'

class TestPhase32VisualReliability(unittest.TestCase):

    def setUp(self):
        self.guard = DummyGuard()
        self.guard.workspace_root.mkdir(parents=True, exist_ok=True)
        self.orchestrator = MultiAgentOrchestrator(self.guard)

    def test_01_progressive_webgl_rendering(self):
        """Verify Motion3DEngineerAgent injects intentional SVG hero fallback, 3000ms timeout guard, and WebGL context loss handling."""
        fe_agent = FrontendEngineerAgent()
        m3d_agent = Motion3DEngineerAgent()
        
        ctx = AgentContext(project_name='p32_webgl_test', user_prompt='Create a 3d audiophile headphones showcase', workspace_root=str(self.guard.workspace_root))
        fe_agent.execute(ctx, creative_spec={'requires_3d': True, 'design_concept': '3D Headphones Showcase'})
        
        m3d_res = m3d_agent.execute(ctx, creative_spec={'requires_3d': True})
        self.assertEqual(m3d_res.status, 'SUCCESS')
        
        index_html = self.guard.workspace_root / 'p32_webgl_test' / 'index.html'
        html_content = index_html.read_text(encoding='utf-8')
        
        self.assertIn('webgl-fallback-hero', html_content)
        self.assertIn('setTimeout', html_content)
        self.assertIn('webglcontextlost', html_content)
        self.assertIn('prefers-reduced-motion', html_content)

    def test_02_responsive_art_direction(self):
        """Verify FrontendEngineerAgent incorporates mobile font wrapping, touch targets, and horizontal overflow bounds."""
        fe_agent = FrontendEngineerAgent()
        ctx = AgentContext(project_name='p32_responsive_test', user_prompt='Create a luxury architecture studio website', workspace_root=str(self.guard.workspace_root))
        fe_res = fe_agent.execute(ctx, creative_spec={'design_concept': 'Studio Dark Architecture'})
        self.assertEqual(fe_res.status, 'SUCCESS')

        index_html = self.guard.workspace_root / 'p32_responsive_test' / 'index.html'
        html_content = index_html.read_text(encoding='utf-8')
        
        self.assertIn('white-space: nowrap', html_content)
        self.assertIn('min-height: 44px', html_content)
        self.assertIn('overflow-x: hidden', html_content)

    def test_03_domain_aware_reference_adaptation(self):
        """Verify ReferenceInspector and CreativeDirector execute explicit domain adaptation."""
        cd_agent = CreativeDirectorAgent()
        ctx = AgentContext(project_name='p32_domain_test', user_prompt='Create a luxury watch horology website', workspace_root=str(self.guard.workspace_root))
        
        ref_spec = {
            'visual_identity': 'Dark Mode Developer Dashboard',
            'color_palette': ['#0b0f19', '#111827', '#38bdf8'],
            'typography_hierarchy': 'Monospace data headers with clean sans'
        }
        
        cd_res = cd_agent.execute(ctx, reference_spec=ref_spec)
        self.assertEqual(cd_res.status, 'SUCCESS')
        spec = cd_res.data
        
        self.assertIn('domain_adaptation_notes', spec)
        self.assertIn('Adapted reference', spec['domain_adaptation_notes'])
        self.assertEqual(spec['color_tokens']['bg_primary'], '#0b0f19')

    def test_04_detailed_visual_qa_dimension_tracking(self):
        """Verify VisualQAInspectorAgent tracks separate visual, functional, responsive, and rendering scores."""
        qa_agent = VisualQAInspectorAgent(self.guard)
        ctx = AgentContext(project_name='p32_qa_test', user_prompt='SaaS Landing Page', workspace_root=str(self.guard.workspace_root))
        
        mock_screenshot_res = {
            'success': True,
            'visual_inspection_executed': True,
            'desktop': 'p32_qa_test/.visual_qa/desktop.png',
            'mobile': 'p32_qa_test/.visual_qa/mobile.png',
            'console_errors': []
        }
        
        res = qa_agent.execute(ctx, creative_spec={}, screenshot_result=mock_screenshot_res)
        self.assertEqual(res.status, 'SUCCESS')
        report = res.data
        
        self.assertIn('visual_quality_score', report)
        self.assertIn('responsive_quality_score', report)
        self.assertIn('rendering_reliability_score', report)

if __name__ == '__main__':
    unittest.main()
