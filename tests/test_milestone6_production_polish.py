import unittest
import json
from server.tools.component_discovery import ComponentDiscoveryCatalog
from server.tools.autonomous_art_director import AutonomousArtDirector

class TestMilestone6ProductionPolish(unittest.TestCase):
    def setUp(self):
        self.catalog = ComponentDiscoveryCatalog()
        self.art_director = AutonomousArtDirector()

    def test_catalog_has_production_polish_snippets(self):
        snippets = self.catalog.SNIPPETS
        self.assertIn('adaptive_motion_engine', snippets)
        self.assertIn('accessible_form_validator', snippets)
        self.assertIn('resilient_image_fallback', snippets)

    def test_search_production_polish_components(self):
        motion_res = self.catalog.search_components('adaptive motion')
        self.assertTrue(any(c['id'] == 'adaptive_motion_engine' for c in motion_res))

        form_res = self.catalog.search_components('form validation')
        self.assertTrue(any(c['id'] == 'accessible_form_validator' for c in form_res))

        img_res = self.catalog.search_components('image fallback')
        self.assertTrue(any(c['id'] == 'resilient_image_fallback' for c in img_res))

    def test_adaptive_motion_snippet_logic(self):
        snippet = self.catalog.SNIPPETS['adaptive_motion_engine']['js_vanilla']
        self.assertIn('class AdaptiveMotionEngine', snippet)
        self.assertIn('maxPixelRatio', snippet)
        self.assertIn('prefers-reduced-motion: reduce', snippet)
        self.assertIn('currentParticleCount', snippet)

    def test_accessible_form_validator_snippet_logic(self):
        snippet = self.catalog.SNIPPETS['accessible_form_validator']['js_vanilla']
        self.assertIn('initAccessibleFormValidator', snippet)
        self.assertIn('aria-invalid', snippet)
        self.assertIn('aria-describedby', snippet)
        self.assertIn('role', snippet)
        self.assertIn('alert', snippet)
        self.assertIn('emailRegex', snippet)
        self.assertIn('firstInvalid.focus()', snippet)

    def test_resilient_image_fallback_snippet_logic(self):
        snippet = self.catalog.SNIPPETS['resilient_image_fallback']['js_vanilla']
        self.assertIn('initResilientImageFallbacks', snippet)
        self.assertIn('svg', snippet)
        self.assertIn('data:image/svg+xml;charset=utf-8,', snippet)
        self.assertIn('preserveAspectRatio="xMidYMid slice"', snippet)
        self.assertIn('var(--bg-surface', snippet)

    def test_art_director_includes_production_polish_manifest(self):
        manifest = self.art_director.synthesize_art_direction('Interactive 3D Platform')
        self.assertIn('production_polish', manifest)
        polish = manifest['production_polish']
        self.assertTrue(polish['adaptive_motion']['framerate_scaling'])
        self.assertTrue(polish['form_validation']['accessible_errors'])
        self.assertTrue(polish['image_fallbacks']['resilient_svg_fallbacks'])

if __name__ == '__main__':
    unittest.main()
