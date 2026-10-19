import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_visual_qa_tools import DevVisualQATools

class TestMilestone3ImmersiveVisualQA(unittest.TestCase):
    def setUp(self):
        self.guard = WorkspaceGuard(Path.cwd())
        self.tools = DevVisualQATools(self.guard)

    def test_immersive_quality_gate_audit(self):
        v_qa = self.tools.run_full_visual_qa('saas_project_management')
        tech_qa = v_qa.get('technical_qa', {})
        self.assertIn('immersive_quality_gate', tech_qa)
        gate = tech_qa['immersive_quality_gate']
        self.assertTrue(gate['passed'])
        self.assertTrue(gate['score'] >= 90)
        self.assertIn('WebGL 3D', gate['webgl_status'])

if __name__ == '__main__':
    unittest.main()
