import unittest
from pathlib import Path
from server.hermes_adapter import HermesAgentAdapter

class TestPhase1Verification(unittest.TestCase):
    def test_task_prompt_includes_design_intelligence_and_skills(self):
        adapter = HermesAgentAdapter('workspace/test_phase1_verification')
        guidelines = adapter._get_ui_ux_design_guidelines('Build a luxury ecommerce footwear store')
        
        self.assertIn('CREATIVE DIRECTION & DESIGN SYSTEM GUIDELINES', guidelines)
        self.assertIn('Recommended CSS Variable Tokens', guidelines)
        self.assertIn('RECOMMENDED UI COMPONENT RECIPES', guidelines)
        self.assertIn('STRICT RULES', guidelines)
        self.assertTrue(any(arch in guidelines for arch in ['Luxury Minimalist', 'Modern Minimal', 'Cyberpunk / Dark Neon', 'Neo-Brutalist', 'Glassmorphism Flow']))

if __name__ == '__main__':
    unittest.main()
