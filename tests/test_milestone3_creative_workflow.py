import unittest
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestMilestone3CreativeWorkflow(unittest.TestCase):
    def test_adapter_has_creative_engine_and_catalog(self):
        adapter = HermesAgentAdapter('workspace/test_m3_creative')
        self.assertTrue(hasattr(adapter, 'creative_engine'))
        self.assertTrue(hasattr(adapter, 'component_catalog'))

    def test_get_ui_ux_design_guidelines_returns_creative_direction(self):
        adapter = HermesAgentAdapter('workspace/test_m3_creative')
        guidelines = adapter._get_ui_ux_design_guidelines('Create a neo-brutalist landing page')
        self.assertIn('CREATIVE DIRECTION & DESIGN SYSTEM GUIDELINES', guidelines)
        self.assertIn('Neo-Brutalist', guidelines)
        self.assertIn('STRICT RULES', guidelines)

if __name__ == '__main__':
    unittest.main()
