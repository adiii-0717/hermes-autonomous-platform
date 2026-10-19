import unittest
from pathlib import Path
from server.tools.autonomous_art_director import AutonomousArtDirector
from server.hermes_adapter import HermesAgentAdapter

class TestMilestone5AutonomousArtDirection(unittest.TestCase):
    def setUp(self):
        self.art_director = AutonomousArtDirector()

    def test_synthesize_art_direction_kinetic_brutalism(self):
        res = self.art_director.synthesize_art_direction('Build a bold yellow kinetic brutalist pop app')
        self.assertEqual(res['archetype_name'], 'Kinetic Brutalism')
        self.assertIn('border_style', res['color_tokens'])
        self.assertEqual(res['color_tokens']['bg_primary'], '#facc15')

    def test_synthesize_art_direction_editorial(self):
        res = self.art_director.synthesize_art_direction('Editorial magazine blog layout')
        self.assertEqual(res['archetype_name'], 'Editorial Spatial Minimal')

    def test_3d_relevance_evaluation(self):
        three_d_res = self.art_director.evaluate_3d_relevance('Build an interactive 3D WebGL particle showcase')
        self.assertTrue(three_d_res['use_3d'])

        non_3d_res = self.art_director.evaluate_3d_relevance('Simple markdown documentation site')
        self.assertFalse(non_3d_res['use_3d'])

    def test_adapter_has_autonomous_art_director(self):
        adapter = HermesAgentAdapter('workspace/test_art_dir')
        self.assertTrue(hasattr(adapter, 'autonomous_art_director'))

if __name__ == '__main__':
    unittest.main()
