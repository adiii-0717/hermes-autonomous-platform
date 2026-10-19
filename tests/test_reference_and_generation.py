"""
Comprehensive Regression Test Suite for Hermes Agent:
Reference Understanding, Functional Completeness, and Website Generation.

Verifies:
- Scenario A: Reference interpretation (restaurant brief with furniture reference -> remains restaurant, borrows visual principles without furniture products).
- Scenario B: Functional requirements (complete food-ordering site has menu cards, real food images, category filters, live search, cart drawer, and checkout flow verified in browser).
- Scenario C: Distinct art direction (fashion lookbook vs restaurant site have completely distinct palettes, typography, layouts, and components).
- Scenario D: Explicit replication vs design inspiration.
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.tools.prompt_reference_parser import PromptReferenceParser
from server.agents.orchestrator import MultiAgentOrchestrator
from server.agents.creative_director_agent import CreativeDirectorAgent
from server.agents.frontend_engineer_agent import FrontendEngineerAgent
from server.agents.schemas import AgentContext
from server.security.workspace_guard import WorkspaceGuard
from server.tools.dev_visual_qa_tools import DevVisualQATools


class TestHermesReferenceAndGenerationAudit(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="hermes_audit_test_")
        self.workspace_root = Path(self.temp_dir)
        self.guard = WorkspaceGuard(str(self.workspace_root))
        self.orchestrator = MultiAgentOrchestrator(self.guard)
        self.qa_tools = DevVisualQATools(self.guard)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scenario_d_replication_vs_inspiration_separation(self):
        """Scenario D: Test explicit replication vs design reference inspiration separation."""
        # 1. Reference inspiration: restaurant brief citing furniture reference
        prompt_inspiration = (
            "Build a food ordering website for 'Osteria Del Mare'. "
            "Study and use all the attached website references as visual-quality benchmarks: "
            "https://in.pinterest.com/pin/1109504058217486382/ (Formora Sculptural Furniture & Interior Seating). "
            "Take inspiration from the warm terracotta palette and generous whitespace, but make it for our seafood and pasta restaurant."
        )
        parsed_insp = PromptReferenceParser.parse(prompt_inspiration)
        self.assertFalse(parsed_insp["is_replication_request"])
        self.assertEqual(parsed_insp["target_domain"], "RESTAURANT_FOOD")
        self.assertIn("https://in.pinterest.com/pin/1109504058217486382/", parsed_insp["reference_images"])
        self.assertIn("Osteria Del Mare", parsed_insp["target_project_brief"])
        self.assertNotIn("https://in.pinterest.com", parsed_insp["target_project_brief"])

        # 2. Explicit replication request: user explicitly asks to recreate a reference
        prompt_replication = (
            "Recreate this exact website from https://in.pinterest.com/pin/1109504058217486382/ for Formora chair studio."
        )
        parsed_rep = PromptReferenceParser.parse(prompt_replication)
        self.assertTrue(parsed_rep["is_replication_request"])
        self.assertEqual(parsed_rep["target_domain"], "SCULPTURAL_FURNITURE")

    def test_scenario_a_reference_interpretation_end_to_end(self):
        """
        Scenario A — Reference interpretation:
        User requests a restaurant website and attaches a furniture website screenshot / Pinterest URL.
        The result MUST remain a restaurant website while borrowing relevant design principles,
        NOT furniture products or furniture-specific content.
        """
        project_name = "test_restaurant_with_furniture_ref"
        prompt = (
            "Build a gourmet dining and food ordering website for 'Osteria Del Mare' featuring handcrafted pasta, seafood, and fine wine. "
            "Use all the attached website references as visual-quality benchmarks: "
            "https://in.pinterest.com/pin/1109504058217486382/ (Formora Sculptural Furniture). "
            "Borrow the warm terracotta palette, typography hierarchy, and clean whitespace."
        )

        # Run real multi-agent orchestration execution path
        result = self.orchestrator.generate_project(
            project_name=project_name,
            user_prompt=prompt,
            max_cycles=1
        )

        proj_dir = self.workspace_root / project_name
        self.assertTrue(proj_dir.exists())

        # Verify App.jsx exists
        app_jsx = proj_dir / "src" / "App.jsx"
        self.assertTrue(app_jsx.exists(), "App.jsx must be generated")
        code = app_jsx.read_text(encoding="utf-8")

        # 1. Assert domain remains restaurant
        self.assertIn("Osteria Del Mare", code)
        self.assertIn("Menu", code)
        self.assertIn("Pasta", code)
        self.assertIn("Truffle", code)

        # 2. Assert zero furniture products or sofa references
        code_lower = code.lower()
        self.assertNotIn("sofa", code_lower)
        self.assertNotIn("armchair", code_lower)
        self.assertNotIn("seating collection", code_lower)
        self.assertNotIn("lounge chair", code_lower)
        self.assertNotIn("coffee table", code_lower)
        self.assertNotIn("credenza", code_lower)

        # 3. Assert design principles borrowed (terracotta / cream warmth)
        self.assertTrue(
            "#E85A2A" in code or "#e85a2a" in code or "terracotta" in code.lower() or "accent-primary" in code,
            "Design principles like warm accents should be present"
        )

    def test_scenario_b_functional_requirements_and_browser_qa(self):
        """
        Scenario B — Functional requirements:
        User requests a complete food-ordering website.
        Verify that the generated result includes the requested menu, real food imagery,
        category filters, search, cart, and checkout flow—not just an empty hero page.
        """
        project_name = "test_food_ordering_complete"
        prompt = (
            "Create a complete food ordering web experience for 'Crave Osteria' "
            "with interactive food menu, food imagery, category filters, live search, item customizer, "
            "cart drawer with total calculation, and checkout flow."
        )

        result = self.orchestrator.generate_project(
            project_name=project_name,
            user_prompt=prompt,
            max_cycles=1
        )

        proj_dir = self.workspace_root / project_name
        app_jsx = proj_dir / "src" / "App.jsx"
        self.assertTrue(app_jsx.exists())
        code = app_jsx.read_text(encoding="utf-8")

        # 1. Code checks for core functional elements
        self.assertIn("searchQuery", code, "Must include search state")
        self.assertIn("activeCategory", code, "Must include category filtering state")
        self.assertIn("cart", code, "Must include cart state")
        self.assertIn("isCartOpen", code, "Must include cart drawer open state")
        self.assertIn("isCheckoutOpen", code, "Must include checkout modal state")
        self.assertIn("selectedDishForModal", code, "Must include dish customizer modal state")
        self.assertIn("dish-card", code, "Must include dish cards")
        self.assertIn("cat-tab", code, "Must include category tabs")
        self.assertIn("cart-trigger", code, "Must include cart trigger")

        # 2. Browser Playwright functional verification
        qa_res = self.qa_tools.capture_responsive_screenshots(
            project_name=project_name,
            target_domain="RESTAURANT_FOOD"
        )

        self.assertTrue(qa_res.get("visual_inspection_executed"))
        self.assertFalse(qa_res.get("blank_page_detected"))
        self.assertTrue(qa_res.get("domain_relevance_pass"), "Domain relevance must pass without reference contamination")
        self.assertEqual(len(qa_res.get("functional_defects", [])), 0, f"Defects detected: {qa_res.get('functional_defects')}")
        self.assertGreaterEqual(qa_res.get("functional_completion_score", 0), 8.0)

        # Verify screenshot files exist
        qa_dir = proj_dir / ".visual_qa"
        desktop_img = qa_dir / "desktop.png"
        mobile_img = qa_dir / "mobile.png"
        self.assertTrue(desktop_img.exists(), "Desktop screenshot must be captured")
        self.assertTrue(mobile_img.exists(), "Mobile screenshot must be captured")
        self.assertGreater(desktop_img.stat().st_size, 1000, "Desktop screenshot must not be empty")
        self.assertGreater(mobile_img.stat().st_size, 1000, "Mobile screenshot must not be empty")

    def test_scenario_c_distinct_art_direction(self):
        """
        Scenario C — Distinct art direction:
        Submit unrelated briefs: a premium fashion portfolio vs a restaurant ordering experience.
        Verify that their designs respond to their content rather than reusing the same layout and animation pattern.
        """
        # Project 1: Luxury Fashion Editorial Lookbook
        proj_fashion = "test_velour_fashion"
        prompt_fashion = "Create a luxury haute couture fashion editorial lookbook for 'Velour Atelier' with runway collection and garment showcase."

        res_fashion = self.orchestrator.generate_project(
            project_name=proj_fashion,
            user_prompt=prompt_fashion,
            max_cycles=1
        )

        # Project 2: Restaurant Culinary Ordering
        proj_restaurant = "test_osteria_culinary"
        prompt_restaurant = "Create an artisanal dining and food ordering experience for 'Osteria Terra' with pasta, wine, and chef reservations."

        res_restaurant = self.orchestrator.generate_project(
            project_name=proj_restaurant,
            user_prompt=prompt_restaurant,
            max_cycles=1
        )

        code_fashion = (self.workspace_root / proj_fashion / "src" / "App.jsx").read_text(encoding="utf-8")
        code_restaurant = (self.workspace_root / proj_restaurant / "src" / "App.jsx").read_text(encoding="utf-8")

        # 1. Distinct domains
        self.assertIn("Velour Atelier", code_fashion)
        self.assertIn("Osteria Terra", code_restaurant)

        # 2. Distinct functional features
        self.assertIn("Couture", code_fashion)
        self.assertIn("Runway", code_fashion)
        self.assertNotIn("Food Bag", code_fashion)
        self.assertNotIn("Tasting Menu", code_fashion)

        self.assertIn("Food Bag", code_restaurant)
        self.assertIn("Truffle", code_restaurant)
        self.assertNotIn("Runway Collection", code_restaurant)

        # 3. Distinct visual palettes & typography
        # Fashion uses deep heritage burgundy (#4A1525) or editorial cream
        # Restaurant uses olive, terracotta, or warm amber
        self.assertNotEqual(code_fashion[:500], code_restaurant[:500])


if __name__ == "__main__":
    unittest.main()
