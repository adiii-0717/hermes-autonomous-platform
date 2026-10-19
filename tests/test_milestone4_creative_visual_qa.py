import unittest
from pathlib import Path
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_visual_qa_tools import DevVisualQATools

class TestMilestone4CreativeVisualQA(unittest.TestCase):
    def setUp(self):
        self.guard = WorkspaceGuard(Path.cwd())
        self.tools = DevVisualQATools(self.guard)

    def test_technical_qa_includes_distinctiveness_and_motion(self):
        v_qa = self.tools.run_full_visual_qa('saas_project_management')
        tech_qa = v_qa.get('technical_qa', {})
        self.assertIn('distinctiveness_score', tech_qa)
        self.assertIn('motion_audit', tech_qa)
        self.assertTrue(tech_qa['distinctiveness_score'] >= 90)
        self.assertTrue(tech_qa['motion_audit']['reduced_motion_ready'])

if __name__ == '__main__':
    unittest.main()
