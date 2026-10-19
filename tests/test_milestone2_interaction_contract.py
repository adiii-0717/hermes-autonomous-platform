import unittest
from server.tools.creative_direction_engine import CreativeDirectionEngine
from server.tools.component_discovery import ComponentDiscoveryCatalog

class TestMilestone2InteractionContract(unittest.TestCase):
    def setUp(self):
        self.engine = CreativeDirectionEngine()
        self.catalog = ComponentDiscoveryCatalog()

    def test_generate_interaction_contract(self):
        contract = self.engine.generate_interaction_contract('Build an interactive 3D studio homepage')
        self.assertIn('interactive_elements', contract)
        self.assertTrue(len(contract['interactive_elements']) >= 3)
        self.assertTrue(contract['prefers_reduced_motion_enabled'])

    def test_gsap_and_magnetic_snippets_exist(self):
        gsap_res = self.catalog.search_components('scroll')
        self.assertTrue(any(s['id'] == 'gsap_scroll_trigger' for s in gsap_res))

        magnetic_res = self.catalog.search_components('magnetic')
        self.assertTrue(any(s['id'] == 'magnetic_button' for s in magnetic_res))

if __name__ == '__main__':
    unittest.main()
