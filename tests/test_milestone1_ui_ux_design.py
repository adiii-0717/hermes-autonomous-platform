import unittest
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestMilestone1UIUXDesign(unittest.TestCase):
    def test_skill_files_exist(self):
        p1 = Path('.agents/skills/ui-ux-design-system/SKILL.md')
        p2 = Path('hermes-agent/skills/software-development/ui-ux-design-system/SKILL.md')
        self.assertTrue(p1.exists(), '.agents skill should exist')
        self.assertTrue(p2.exists(), 'hermes-agent skill should exist')
        
        content = p1.read_text(encoding='utf-8')
        self.assertIn('name: ui-ux-design-system', content)
        self.assertIn('Visual Identity Selection Matrix', content)
        self.assertIn('Design System Specification Workflow', content)

    def test_adapter_guidelines(self):
        adapter = HermesAgentAdapter('workspace')
        guidelines = adapter._get_ui_ux_design_guidelines()
        self.assertIn('DESIGN SYSTEM GUIDELINES', guidelines)
        self.assertIn('Selected Archetype', guidelines)
        self.assertIn('TYPOGRAPHY', guidelines)

if __name__ == '__main__':
    unittest.main()
