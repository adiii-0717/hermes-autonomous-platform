"""
Phase 2 Verification Tests: Product Intent Understanding and Planning Stage.
Verifies that user prompts are properly classified into primary domain products
and visual enhancements, ensuring generated applications maintain full functional logic.
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server.tools.product_intent_classifier import ProductIntentClassifier
from server.hermes_adapter import HermesAgentAdapter

class TestPhase2ProductIntentClassification(unittest.TestCase):
    
    def setUp(self):
        self.classifier = ProductIntentClassifier()
        self.adapter = HermesAgentAdapter(str(PROJECT_ROOT / "workspace"))

    def test_footwear_3d_ecommerce_intent(self):
        prompt = "Create a premium 3D footwear e-commerce website."
        result = self.classifier.classify_intent(prompt)
        
        self.assertEqual(result["matched_domain"], "E_COMMERCE")
        self.assertIn("E-Commerce", result["primary_product"])
        self.assertIn("3D", result["visual_enhancements"])
        
        # Verify core features include shopping & cart requirements
        features_text = " ".join(result["core_features"]).lower()
        self.assertIn("cart", features_text)
        self.assertIn("checkout", features_text)
        self.assertIn("product", features_text)

    def test_educational_dashboard_intent(self):
        prompt = "Modern educational dashboard."
        result = self.classifier.classify_intent(prompt)
        
        self.assertEqual(result["matched_domain"], "DASHBOARD")
        self.assertIn("Dashboard", result["primary_product"])
        
        features_text = " ".join(result["core_features"]).lower()
        self.assertIn("chart", features_text)
        self.assertIn("metric", features_text)

    def test_cinematic_portfolio_intent(self):
        prompt = "Cinematic portfolio website."
        result = self.classifier.classify_intent(prompt)
        
        self.assertEqual(result["matched_domain"], "PORTFOLIO")
        self.assertIn("Portfolio", result["primary_product"])
        self.assertIn("CINEMATIC", result["visual_enhancements"])
        
        features_text = " ".join(result["core_features"]).lower()
        self.assertIn("showcase", features_text)
        self.assertIn("contact", features_text)

    def test_saas_analytics_intent(self):
        prompt = "SaaS analytics platform."
        result = self.classifier.classify_intent(prompt)
        
        self.assertEqual(result["matched_domain"], "SAAS_ANALYTICS")
        self.assertIn("SaaS", result["primary_product"])
        
        features_text = " ".join(result["core_features"]).lower()
        self.assertIn("metric", features_text)
        self.assertIn("chart", features_text)

    def test_adapter_guidelines_injection(self):
        prompt = "Create a premium 3D footwear e-commerce website."
        guidelines = self.adapter._get_ui_ux_design_guidelines(prompt)
        
        self.assertIn("[PRODUCT INTENT ARCHITECTURE & PLANNING INSTRUCTIONS]", guidelines)
        self.assertIn("PRIMARY PRODUCT IDENTIFICATION:", guidelines)
        self.assertIn("CRITICAL ARCHITECTURAL RULE:", guidelines)
        self.assertIn("MUST-HAVE DOMAIN PRODUCT FUNCTIONALITY:", guidelines)
        self.assertIn("E-Commerce", guidelines)

    def test_analyze_prompt_for_project_includes_intent(self):
        prompt = "Create a premium 3D footwear e-commerce website."
        import asyncio
        analysis = asyncio.run(self.adapter.analyze_prompt_for_project(prompt))
        
        self.assertIn("product_intent", analysis)
        self.assertEqual(analysis["product_intent"]["matched_domain"], "E_COMMERCE")

if __name__ == "__main__":
    unittest.main()
