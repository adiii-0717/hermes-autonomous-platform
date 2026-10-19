import unittest
from server.tools.component_discovery import ComponentDiscoveryCatalog

class TestMilestone2ComponentDiscovery(unittest.TestCase):
    def setUp(self):
        self.catalog = ComponentDiscoveryCatalog()

    def test_search_components(self):
        res1 = self.catalog.search_components("shiny")
        self.assertTrue(len(res1) > 0)
        self.assertEqual(res1[0]['id'], 'shiny_text')

        res2 = self.catalog.search_components("card")
        self.assertTrue(len(res2) >= 2)

    def test_bundle_recommendation(self):
        rec = self.catalog.get_bundle_recommendation("3d particle background")
        self.assertIn('recommended_libraries', rec)
        self.assertTrue(rec['reduced_motion_supported'])

if __name__ == '__main__':
    unittest.main()
