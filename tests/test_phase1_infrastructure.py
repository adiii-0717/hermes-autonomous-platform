import os
import unittest
from pathlib import Path
from server.tools.component_discovery import ComponentDiscoveryCatalog
from server.tools.asset_discovery import AssetDiscoveryService
from server.tools.dev_visual_qa_tools import DevVisualQATools
from server.hermes_adapter import HermesAgentAdapter

class DummyGuard:
    workspace_root = Path(__file__).parent.parent / 'workspace'

class TestPhase1Infrastructure(unittest.TestCase):

    def setUp(self):
        self.catalog = ComponentDiscoveryCatalog()
        self.asset_service = AssetDiscoveryService()
        self.guard = DummyGuard()
        self.guard.workspace_root.mkdir(parents=True, exist_ok=True)
        self.qa = DevVisualQATools(self.guard)

    def test_01_component_discovery_3d_and_motion_recipes(self):
        """Verify ComponentDiscoveryCatalog matches and formats R3F and GSAP recipes."""
        res_3d = self.catalog.search_components('Create a 3d footwear shoe model')
        self.assertTrue(len(res_3d) > 0)
        self.assertTrue(any(c['type'].startswith('3d') for c in res_3d))
        
        # Verify code sample presence
        top_recipe = res_3d[0]
        self.assertIn('code_sample', top_recipe)
        self.assertIn('React Three Fiber', top_recipe['name'])

        formatted = self.catalog.format_component_prompt(res_3d[:2])
        self.assertIn('[MATCHED 3D & MOTION IMPLEMENTATION RECIPES]', formatted)
        self.assertIn('Code Example:', formatted)

    def test_02_asset_discovery_service(self):
        """Verify AssetDiscoveryService returns verified URLs, 3D GLBs, HDR maps, and fonts."""
        assets = self.asset_service.discover_assets('Create a 3d footwear e-commerce shop')
        self.assertEqual(assets['topic'], 'Footwear & E-Commerce')
        self.assertTrue(len(assets['photos']) >= 3)
        self.assertTrue(len(assets['models_3d']) >= 1)
        self.assertTrue(len(assets['hdri_maps']) >= 1)

        # Verify Unsplash image URL format
        self.assertTrue(assets['photos'][0]['url'].startswith('https://images.unsplash.com/'))

        formatted = self.asset_service.format_asset_prompt_guidelines(assets)
        self.assertIn('[VERIFIED ASSET DISCOVERY & RESILIENT FALLBACKS', formatted)
        self.assertIn('High-Quality Photography Assets', formatted)

    def test_03_adapter_design_guidelines_enrichment(self):
        """Verify HermesAgentAdapter enriches generation prompt with 3D recipes and assets."""
        adapter = HermesAgentAdapter(workspace_path=str(self.guard.workspace_root))
        guidelines = adapter._get_ui_ux_design_guidelines('Create a cinematic portfolio website with scroll storytelling')
        self.assertIn('[MATCHED 3D & MOTION IMPLEMENTATION RECIPES]', guidelines)
        self.assertIn('[VERIFIED ASSET DISCOVERY & RESILIENT FALLBACKS', guidelines)

    def test_04_playwright_responsive_screenshot_capture(self):
        """Verify Playwright captures genuine PNG screenshots and console errors."""
        test_proj = self.guard.workspace_root / 'test_infra_proj'
        test_proj.mkdir(parents=True, exist_ok=True)
        index_file = test_proj / 'index.html'
        index_file.write_text("""<!DOCTYPE html>
<html>
<head><title>Infra QA Test</title></head>
<body style="background:#0f172a; color:#f8fafc; font-family:sans-serif; padding:40px;">
  <h1 style="color:#38bdf8;">Playwright Infra Verification</h1>
  <p>Verifying responsive desktop and mobile screenshot capture.</p>
  <script>console.error('Infra test error event');</script>
</body>
</html>""", encoding='utf-8')

        res = self.qa.capture_responsive_screenshots('test_infra_proj')
        self.assertTrue(res['success'])
        self.assertTrue(res['visual_inspection_executed'])
        self.assertIsNotNone(res['desktop'])
        self.assertIsNotNone(res['mobile'])
        self.assertIn('Infra test error event', res['console_errors'])

        # Verify PNG files exist on disk
        desktop_p = self.guard.workspace_root / res['desktop']
        mobile_p = self.guard.workspace_root / res['mobile']
        self.assertTrue(desktop_p.exists())
        self.assertTrue(mobile_p.exists())
        self.assertTrue(desktop_p.stat().st_size > 1000)
        self.assertTrue(mobile_p.stat().st_size > 1000)

    def test_05_baseline_benchmark_prompts_evaluation(self):
        """Verify visual quality baseline evaluation framework across 4 benchmark prompts."""
        benchmark_prompts = [
            ("3d_footwear_shop", "Create a premium 3D footwear e-commerce website with an interactive product presentation."),
            ("cinematic_portfolio", "Create a cinematic creative developer portfolio with scroll-driven storytelling."),
            ("architecture_studio", "Create an immersive architecture studio website with sophisticated visual transitions."),
            ("saas_landing_page", "Create a premium SaaS landing page with distinctive art direction and meaningful interactions.")
        ]

        results = {}
        for proj_name, prompt in benchmark_prompts:
            proj_dir = self.guard.workspace_root / proj_name
            proj_dir.mkdir(parents=True, exist_ok=True)
            
            # Asset & recipe retrieval for prompt
            discovered_assets = self.asset_service.discover_assets(prompt)
            matched_recipes = self.catalog.search_components(prompt)
            
            # Create baseline HTML
            index_file = proj_dir / 'index.html'
            photo_url = discovered_assets['photos'][0]['url']
            top_recipe_name = matched_recipes[0]['name'] if matched_recipes else 'Modern Layout'
            
            index_file.write_text(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{proj_name.replace('_', ' ').title()}</title>
  <style>
    body {{ margin: 0; background: #090d16; color: #f3f4f6; font-family: system-ui, sans-serif; }}
    .hero {{ height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }}
    h1 {{ font-size: 3rem; margin-bottom: 1rem; color: #38bdf8; }}
    p {{ max-width: 600px; color: #9ca3af; font-size: 1.25rem; }}
    img {{ max-width: 400px; border-radius: 16px; margin-top: 2rem; border: 1px solid #1e293b; }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>{proj_name.replace('_', ' ').title()}</h1>
    <p>Baseline experience powered by {top_recipe_name}</p>
    <img src="{photo_url}" alt="Product Showcase" onerror="this.src='https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1000&auto=format&fit=crop'" />
  </div>
</body>
</html>""", encoding='utf-8')

            # Run Playwright visual QA
            qa_res = self.qa.capture_responsive_screenshots(proj_name)
            results[proj_name] = {
                'prompt': prompt,
                'recipe': top_recipe_name,
                'topic': discovered_assets['topic'],
                'qa_success': qa_res['success'],
                'desktop_png': qa_res.get('desktop'),
                'mobile_png': qa_res.get('mobile'),
                'console_errors': qa_res.get('console_errors', [])
            }

        self.assertEqual(len(results), 4)
        for name, r in results.items():
            self.assertTrue(r['qa_success'], f"QA screenshot capture failed for {name}")
            self.assertIsNotNone(r['desktop_png'])
            self.assertIsNotNone(r['mobile_png'])

if __name__ == '__main__':
    unittest.main()
