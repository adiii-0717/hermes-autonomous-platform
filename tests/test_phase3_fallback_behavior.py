"""
Phase 3 Verification Tests: Fallback Behavior & Boilerplate Overhaul.
Verifies that generic Torus Knot static template fallback is eliminated,
workspace mutation during project discovery is removed, and domain-appropriate
fallbacks are generated only when entry points are missing.
"""

import unittest
import sys
import shutil
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.hermes_adapter import HermesAgentAdapter

class TestPhase3FallbackBehavior(unittest.TestCase):

    def setUp(self):
        self.test_workspace = PROJECT_ROOT / "workspace" / "test_phase3_workspace"
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)
        self.test_workspace.mkdir(parents=True, exist_ok=True)
        self.adapter = HermesAgentAdapter(str(self.test_workspace))

    def tearDown(self):
        if self.test_workspace.exists():
            shutil.rmtree(self.test_workspace)

    def test_ecommerce_fallback_is_domain_appropriate(self):
        prompt = "Create a premium 3D footwear e-commerce website."
        self.adapter._ensure_web_app_boilerplate(prompt)

        html_file = self.test_workspace / "index.html"
        self.assertTrue(html_file.exists())
        
        html_content = html_file.read_text(encoding="utf-8")
        # Ensure domain components are present
        self.assertIn("Cart", html_content)
        self.assertIn("Footwear", html_content)
        self.assertIn("checkout-modal", html_content)
        # Ensure old generic torus knot title/structure is gone
        self.assertNotIn("TorusKnotGeometry", html_content)

    def test_dashboard_fallback_is_domain_appropriate(self):
        prompt = "Modern educational dashboard."
        self.adapter._ensure_web_app_boilerplate(prompt)

        html_file = self.test_workspace / "index.html"
        self.assertTrue(html_file.exists())
        
        html_content = html_file.read_text(encoding="utf-8")
        self.assertIn("Dashboard", html_content)
        self.assertIn("KPI", html_content.upper() or "STUDENT" in html_content.upper())

    def test_existing_files_are_preserved(self):
        # Create a valid generated index.html
        custom_html = "<html><body><h1>Custom LLM Output</h1></body></html>"
        (self.test_workspace / "index.html").write_text(custom_html, encoding="utf-8")

        prompt = "Create a premium 3D footwear e-commerce website."
        self.adapter._ensure_web_app_boilerplate(prompt)

        # Content must remain unchanged
        html_content = (self.test_workspace / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html_content, custom_html)

if __name__ == "__main__":
    unittest.main()
