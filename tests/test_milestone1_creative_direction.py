import unittest
from pathlib import Path
from server.tools.creative_direction_engine import CreativeDirectionEngine

class TestMilestone1CreativeDirection(unittest.TestCase):
    def setUp(self):
        self.engine = CreativeDirectionEngine()

    def test_skill_files_exist(self):
        p1 = Path('.agents/skills/creative-design-research/SKILL.md')
        p2 = Path('hermes-agent/skills/software-development/creative-design-research/SKILL.md')
        self.assertTrue(p1.exists(), '.agents skill should exist')
        self.assertTrue(p2.exists(), 'hermes-agent skill should exist')

    def test_generate_creative_direction(self):
        res = self.engine.generate_creative_direction('Build a bold neo-brutalist pop landing page')
        self.assertEqual(res['selected_archetype'], 'Neo-Brutalist')
        self.assertEqual(len(res['candidate_concepts']), 3)
        self.assertIn('color_tokens', res)
        self.assertIn('typography', res)

    def test_css_variable_block_generation(self):
        res = self.engine.generate_creative_direction('Minimalist editorial blog')
        css_block = self.engine.get_css_variable_block(res)
        self.assertIn(':root', css_block)
        self.assertIn('--bg-primary:', css_block)
        self.assertIn('--font-heading:', css_block)

if __name__ == '__main__':
    unittest.main()
