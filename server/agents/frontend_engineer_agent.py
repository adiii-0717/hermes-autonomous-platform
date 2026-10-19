import logging
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.agents.schemas import AgentContext
from server.tools.product_intent_classifier import ProductIntentClassifier
from server.agents.llm_client import LLMClient
from server.agents.react_bits_generator import ReactBitsProjectGenerator
from server.tools.prompt_reference_parser import PromptReferenceParser

logger = logging.getLogger('agent.FrontendEngineer')

class FrontendEngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name='FrontendEngineer',
            role_description='Implements responsive HTML/JSX, CSS variables, interactive UI components, and navigation.'
        )
        self.intent_classifier = ProductIntentClassifier()
        self.llm = LLMClient()
        self.react_generator = ReactBitsProjectGenerator()


    def detect_domain(self, user_prompt: str) -> str:
        # Use PromptReferenceParser to ensure reference links do not hijack target domain
        return PromptReferenceParser._classify_domain(user_prompt)

    def extract_brand_name(self, user_prompt: str, domain: str) -> str:
        # 1. Match explicit quotes e.g. for 'Velour Atelier' or called “Osteria Terra” or named 'Nexus Creative'
        match = re.search(r'(?:for|called|named|brand|titled)\s+["“\']([^"”\']+)["”\']', user_prompt, re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip().rstrip('.,;:"\'')
        
        # 2. Match any capitalized quoted string e.g. 'Velour Atelier'
        match_any = re.search(r'["“\']([A-Z][^"”\']{2,40})["”\']', user_prompt)
        if match_any and match_any.group(1).strip():
            return match_any.group(1).strip().rstrip('.,;:"\'')

        # 3. Match capitalized words e.g. called Velour Atelier
        match2 = re.search(r'(?:called|named|brand|titled)\s+([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*)', user_prompt)
        if match2 and match2.group(1).strip():
            return match2.group(1).strip().rstrip('.,;:"\'')

        # 3b. Match 'for <Brand Name> in/with/using/as/...' e.g. for Solaris Studio in React
        match_for = re.search(r'\bfor\s+([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*)\s+(?:in|with|using|featuring|and|\.|$)', user_prompt)
        if match_for and match_for.group(1).strip():
            cand = match_for.group(1).strip().rstrip('.,;:"\'')
            if cand.lower() not in ["a", "an", "the", "react", "vite", "python", "html", "web", "vue", "nextjs", "javascript"]:
                return cand
            
        # 4. Match 'for a fashion store called Velour Atelier' without quotes
        match3 = re.search(r'(?:for\s+a\s+\w+\s+called\s+)([\w\s]+?)(?:\.|\s+Include|\s+with|\s*$)', user_prompt, re.IGNORECASE)
        if match3 and match3.group(1).strip():
            return match3.group(1).strip().title().rstrip('.,;:"\'')

        # 5. Extract from prompt if words like Solaris Studio appear
        match_studio = re.search(r'\b([A-Z][a-zA-Z0-9]+\s+(?:Studio|Atelier|Architecture|Lab|Design|Collective))\b', user_prompt)
        if match_studio and match_studio.group(1).strip():
            return match_studio.group(1).strip()

        fallbacks = {
            "EDITORIAL_FASHION": "VELOUR ATELIER",
            "RESTAURANT_CULINARY": "OSTERIA TERRA",
            "CREATIVE_AGENCY": "SOLARIS STUDIO",
            "STREAMING_DATA_DEVTOOL": "VORTEX FLOW",
            "AI_TECH_STUDIO": "AETHERIA AI STUDIO",
            "RESTAURANT_FOOD": "CRAVE KITCHEN",
            "FOOTWEAR_SNEAKERS": "AURA // KICKS",
            "STREAMING_ENTERTAINMENT": "CINEVERSE",
            "FASHION_APPAREL": "VELOUR ATELIER",
            "DASHBOARD": "NEXUS ANALYTICS",
            "PORTFOLIO": "ALEX MERCER // DESIGN",
            "FITNESS_WELLNESS": "APEX FITNESS",
            "REAL_ESTATE": "AURA PROPERTIES",
            "GENERIC_STORE": "LUMEN STORE"
        }
        return fallbacks.get(domain, "SOLARIS STUDIO")

    def run(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        spec = kwargs.get('creative_spec', {})
        prioritized_fixes = kwargs.get('prioritized_fixes', [])

        ws_p = Path(context.workspace_root)
        proj_dir = ws_p if ws_p.name == context.project_name else (ws_p / context.project_name)
        proj_dir.mkdir(parents=True, exist_ok=True)

        target_brief = context.target_project_brief or context.user_prompt
        domain = context.target_domain or spec.get('target_domain') or self.detect_domain(target_brief)
        brand_name = self.extract_brand_name(target_brief, domain)
        logger.info(f"FrontendEngineerAgent: detected domain='{domain}', brand='{brand_name}' for target brief: '{target_brief}'")

        # Check if the user requested a React / React Bits application
        p_lower = target_brief.lower()
        is_react = (
            any(k in p_lower for k in ["react", "react bits", "reactbits", "component", "vite", "jsx", "tsx", "website", "animated component"]) or
            "react" in str(context.project_name).lower() or
            domain in ["EDITORIAL_FASHION", "RESTAURANT_CULINARY", "RESTAURANT_FOOD", "CREATIVE_AGENCY", "STREAMING_DATA_DEVTOOL", "SCULPTURAL_FURNITURE", "ORGANIC_SANCTUARY", "LUXURY_ATELIER"]
        )
        if is_react:
            logger.info(f"FrontendEngineerAgent: detected React request, generating full Vite + React + React Bits project for '{brand_name}' ({domain})")
            return self.react_generator.generate_project(context, spec, brand_name, domain, prioritized_fixes)

        # 1. Attempt bespoke LLM generation strictly tailored to the user's prompt
        index_html_content = self._generate_with_llm(context, spec, brand_name, domain, prioritized_fixes)

        # 2. If LLM generation was unavailable or timed out, use high-fidelity domain fallback
        if not index_html_content:
            logger.info(f"FrontendEngineerAgent: using domain fallback generator for domain='{domain}'")
            if domain in ["RESTAURANT_FOOD", "RESTAURANT_CULINARY"]:
                from server.agents.domain_restaurant import generate_restaurant_culinary_index_html
                badge_letter = brand_name[0] if brand_name else "O"
                colors = spec.get('color_tokens', {})
                index_html_content = generate_restaurant_culinary_index_html(brand_name, badge_letter, colors)
            elif domain == "FOOTWEAR_SNEAKERS":
                index_html_content = self._generate_sneakers_html(context, spec, brand_name, prioritized_fixes)
            elif domain == "STREAMING_ENTERTAINMENT":
                index_html_content = self._generate_streaming_html(context, spec, brand_name, prioritized_fixes)
            elif domain == "DASHBOARD":
                index_html_content = self._generate_dashboard_html(context, spec, brand_name, prioritized_fixes)
            elif domain == "PORTFOLIO":
                index_html_content = self._generate_portfolio_html(context, spec, brand_name, prioritized_fixes)
            else:
                index_html_content = self._generate_generic_html(context, spec, brand_name, prioritized_fixes)

        index_html_path = proj_dir / 'index.html'
        index_html_path.write_text(index_html_content, encoding='utf-8')

        return {
            'files_written': ['index.html'],
            'project_dir': str(proj_dir),
            'concept': f"{brand_name} — {domain}"
        }

    def _generate_with_llm(self, context: AgentContext, spec: dict, brand_name: str, domain: str, prioritized_fixes: list) -> Optional[str]:
        if not self.llm.is_configured():
            return None

        system_prompt = """You are an elite Senior Staff Frontend Engineer and UI/UX Designer at NEXARCH Dev Studio.
Your mission is to generate a complete, standalone, production-grade, highly polished single-page web application based on the user's explicit request.

You MUST actively embody the principles of these four core UI design skills:
1. Anthropic Frontend Design:
   - Design Lead mindset: intentional design, purposeful layout, avoid AI clichés:
     - No purple-to-blue neon gradient backgrounds.
     - No single-word italic headline highlights.
     - No tracked-out ALL-CAPS eyebrows.
     - No appending `→` to every button.
     - Active voice copywriting tailored directly to the product domain.
2. UI/UX Pro Max:
   - Choose a distinctive design archetype matching domain (e.g. Dark Cyberpunk / Bento Grid for devtools, High-Energy Studio for sneakers, Organic Editorial for culinary, Minimalist Luxury for SaaS).
   - 8pt spatial grid (p-4, p-6, p-8, py-16, py-24).
   - 44px minimum touch targets.
   - 5 interactive states (default, hover, active, focus-visible, disabled).
   - Strict WCAG AA contrast (>= 4.5:1).
3. Vercel Web Design & React Guidelines:
   - Hairline borders (border border-white/10 or ring-1 ring-inset ring-white/10).
   - Tabular numbers (tabular-nums font-mono or font-variant-numeric: tabular-nums) on all numeric data, telemetry, prices, and metrics to prevent layout jitter.
   - Balanced headings (text-wrap: balance).
   - Visible focus rings (focus-visible:ring-2 focus-visible:ring-cyan-400).
   - Respect prefers-reduced-motion.
4. UI.sh:
   - Visual hierarchy driven by font-weight and color contrast rather than font-size alone.
   - Generous whitespace scale.
   - Avoid muddy shadows; use subtle hairline borders and dark tinted neutrals.
   - Realistic, authentic domain data (never lorem ipsum).

CRITICAL ARCHITECTURAL RULES:
1. OUTPUT FORMAT: Output ONLY pure HTML code starting with <!DOCTYPE html>. Do NOT output any markdown backticks, explanations, or preamble.
2. COMPLETENESS: The output must be 100% complete and self-contained with all HTML markup, embedded CSS in <style>, and interactive JavaScript in <script>. Never use placeholder text or truncate code.
3. VISUAL QUALITY & AESTHETICS (REACT BITS INSPIRATION):
   - Modern, ultra-premium design incorporating React Bits aesthetic paradigms:
     - Purpose-matched animated canvas or subtle grid background (Squares, Aurora, or Particles).
     - Kinetic hero typography (DecryptedText, SplitText, or BlurText).
     - Interactive Spotlight cards with mouse-tracking radial gradient glow across card surface and border.
     - Magnetic or StarBorder interactive CTA buttons.
   - Google Fonts (Outfit, Plus Jakarta Sans, Playfair Display, or Inter) loaded via <link>.
   - Smooth CSS transitions (0.2s - 0.3s cubic-bezier curves), clean card elevation, responsive padding.
4. PROFESSIONAL ICONOGRAPHY & CLEAN BRANDING:
   - ZERO-EMOJI RULE: NEVER use emoji characters (👟, 🛒, 🍔, ⭐, 🚀) as UI icons or graphics. Emojis look amateurish and break visual hierarchy.
   - Use clean, professional vector SVG icons modeled after Lucide React with consistent strokeWidth="1.5" or "2" and uniform sizing (w-4 h-4, w-5 h-5).
   - When no official logo exists, create clean text-based branding: a sleek typographic wordmark with a geometric monogram badge (e.g., a square/rounded icon with the first letter).
5. HIGH-FIDELITY CONTENT:
   - Provide realistic, rich, domain-specific content, titles, descriptions, badges, and high-quality Unsplash image URLs fitting the exact subject requested by the user.
6. COMPLETE INTERACTIVITY:
   - All buttons, navigation links, filters, category tabs, and search inputs MUST work with real JavaScript event listeners.
   - If e-commerce / food ordering / shopping: implement full cart/bag state (add to cart, quantity change, live total, checkout modal, order confirmation).
   - If streaming / data / devtool: implement interactive pipeline topology inspector, telemetry rate slider, filter toggles, test packet injector modal.
   - If dashboard: implement interactive charts, filter toggles, metrics cards, date selector.
   - If portfolio / corporate: implement interactive project filter, contact modal, testimonials slider, responsive hamburger menu.
7. RESPONSIVENESS:
   - Mobile-first or responsive desktop layout that looks flawless on both 1440px desktop and 375px mobile screens.
"""

        colors = spec.get('color_tokens', {})
        fonts = spec.get('typography_system', {})
        user_prompt = f"""Target Brand: {brand_name}
Target Domain: {domain}

User Prompt:
"{context.user_prompt}"

Design Tokens:
- Concept: {spec.get('design_concept', brand_name)}
- Visual Identity: {spec.get('visual_identity', 'Modern Studio')}
- Palette: {json.dumps(colors)}
- Typography: {json.dumps(fonts)}
- Requested Fixes from Visual QA: {', '.join(prioritized_fixes) if prioritized_fixes else 'None (Initial Generation)'}

Now, generate the complete, single-file <!DOCTYPE html> application fulfilling all user requirements above."""

        try:
            raw_html = self.llm.call_llm_text(system_prompt, user_prompt, temperature=0.3, timeout=50)
            if not raw_html:
                return None

            clean = raw_html.strip()
            if clean.startswith("```html"):
                clean = clean[7:]
            elif clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()

            if "<!DOCTYPE html" in clean or ("<html" in clean and "<body" in clean and "</html>" in clean):
                if len(clean) > 800:
                    logger.info(f"FrontendEngineerAgent: Successfully generated bespoke website via LLM ({len(clean)} bytes) for brand '{brand_name}'")
                    return clean
        except Exception as e:
            logger.warning(f"FrontendEngineerAgent: LLM generation error: {e}")

        return None

    def _generate_restaurant_html(self, context: AgentContext, spec: dict, brand_name: str, prioritized_fixes: list) -> str:
        refinement_notice = ''
        if prioritized_fixes:
            refinement_notice = f'<!-- Applied Refinements: {", ".join(prioritized_fixes[:2])} -->'

        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{brand_name} — Artisanal Culinary & Food Ordering</title>
  <!-- Google Fonts: Playfair Display, Outfit & Plus Jakarta Sans -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #0c0a09;
      --bg-surface: #1c1917;
      --bg-card: #292524;
      --bg-card-hover: #332e2c;
      --border-subtle: rgba(245, 158, 11, 0.15);
      --border-focus: rgba(245, 158, 11, 0.5);
      --accent: #f59e0b;
      --accent-warm: #ea580c;
      --accent-glow: rgba(245, 158, 11, 0.35);
      --text-main: #fafaf9;
      --text-muted: #d6d3d1;
      --text-dim: #a8a29e;
      --success: #10b981;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 22px;
      --radius-pill: 9999px;
      --shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
      --font-serif: 'Playfair Display', Georgia, serif;
      --font-heading: 'Outfit', sans-serif;
      --font-body: 'Plus Jakarta Sans', sans-serif;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-body);
      line-height: 1.5;
      overflow-x: hidden;
      min-height: 100vh;
    }}

    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-dark); }}
    ::-webkit-scrollbar-thumb {{ background: #44403c; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

    .container {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    /* Top Announcement Banner */
    .announcement-bar {{
      background: linear-gradient(90deg, #991b1b, #ea580c, #d97706);
      color: #fff;
      font-size: 0.825rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      padding: 9px 16px;
      text-align: center;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 12px;
    }}
    .announcement-bar span.pill {{
      background: rgba(0, 0, 0, 0.35);
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      font-size: 0.75rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* Header & Navigation */
    .navbar {{
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      background: rgba(12, 10, 9, 0.9);
      border-bottom: 1px solid var(--border-subtle);
      transition: all 0.3s ease;
    }}
    .nav-inner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 80px;
      gap: 24px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-main);
    }}
    .brand-icon {{
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, var(--accent), var(--accent-warm));
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.4rem;
      box-shadow: 0 4px 16px var(--accent-glow);
    }}
    .brand-text {{
      font-family: var(--font-serif);
      font-size: 1.65rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.1;
    }}
    .brand-text span {{ color: var(--accent); }}

    .nav-search {{
      flex: 1;
      max-width: 440px;
      position: relative;
    }}
    .nav-search input {{
      width: 100%;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-pill);
      padding: 11px 18px 11px 44px;
      color: var(--text-main);
      font-size: 0.9rem;
      outline: none;
      transition: all 0.25s ease;
    }}
    .nav-search input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--border-focus);
      background: #24201d;
    }}
    .nav-search .search-icon {{
      position: absolute;
      left: 16px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      font-size: 0.95rem;
    }}

    .nav-links {{
      display: flex;
      align-items: center;
      gap: 24px;
      list-style: none;
    }}
    .nav-links a {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 600;
      transition: color 0.2s ease;
    }}
    .nav-links a:hover, .nav-links a.active {{ color: var(--accent); }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .reserve-btn {{
      background: transparent;
      border: 1px solid var(--accent);
      color: var(--accent);
      padding: 10px 18px;
      border-radius: var(--radius-pill);
      font-weight: 700;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .reserve-btn:hover {{
      background: rgba(245, 158, 11, 0.15);
      transform: translateY(-1px);
    }}
    .cart-btn {{
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(234, 88, 12, 0.1));
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: var(--text-main);
      padding: 10px 20px;
      border-radius: var(--radius-pill);
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.25s ease;
    }}
    .cart-btn:hover {{
      background: var(--accent);
      color: #000;
      transform: translateY(-1px);
      box-shadow: 0 6px 20px var(--accent-glow);
    }}
    .cart-count {{
      background: var(--accent);
      color: #000;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: var(--radius-pill);
    }}
    .cart-btn:hover .cart-count {{
      background: #000;
      color: var(--accent);
    }}

    /* Hero Section */
    .hero-section {{
      padding: 64px 0 88px;
      position: relative;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 52px;
      align-items: center;
    }}
    .hero-content {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 16px;
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: var(--radius-pill);
      color: var(--accent);
      font-size: 0.825rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      width: fit-content;
    }}
    .hero-title {{
      font-family: var(--font-serif);
      font-size: 4rem;
      font-weight: 800;
      line-height: 1.08;
      letter-spacing: -0.02em;
    }}
    .hero-title .gradient-text {{
      background: linear-gradient(135deg, #fff 30%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero-desc {{
      font-size: 1.15rem;
      color: var(--text-muted);
      max-width: 540px;
      line-height: 1.6;
    }}
    .hero-cta-group {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-top: 12px;
      flex-wrap: wrap;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--accent), var(--accent-warm));
      color: #000;
      padding: 14px 34px;
      border-radius: var(--radius-pill);
      font-size: 1rem;
      font-weight: 800;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      border: none;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 8px 24px var(--accent-glow);
    }}
    .btn-primary:hover {{
      transform: translateY(-2px);
      box-shadow: 0 12px 30px rgba(245, 158, 11, 0.5);
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 14px 28px;
      border-radius: var(--radius-pill);
      font-size: 1rem;
      font-weight: 600;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.1);
      border-color: var(--accent);
    }}

    .hero-metrics {{
      display: flex;
      gap: 36px;
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid var(--border-subtle);
    }}
    .metric-item {{ display: flex; flex-direction: column; }}
    .metric-val {{
      font-family: var(--font-heading);
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--accent);
    }}
    .metric-lbl {{
      font-size: 0.8rem;
      color: var(--text-dim);
      font-weight: 500;
    }}

    .hero-food-card {{
      position: relative;
      border-radius: var(--radius-lg);
      background: radial-gradient(circle at 50% 40%, #292524 0%, #0c0a09 100%);
      border: 1px solid var(--border-subtle);
      overflow: hidden;
      min-height: 460px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: var(--shadow-card);
    }}
    .hero-food-img {{
      width: 100%;
      height: 100%;
      min-height: 460px;
      object-fit: cover;
      transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .hero-food-card:hover .hero-food-img {{
      transform: scale(1.05);
    }}
    .hero-floating-badge {{
      position: absolute;
      bottom: 24px;
      left: 24px;
      background: rgba(28, 25, 23, 0.85);
      backdrop-filter: blur(10px);
      padding: 10px 18px;
      border-radius: var(--radius-pill);
      border: 1px solid var(--border-subtle);
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }}
    .badge-dot {{
      width: 10px;
      height: 10px;
      background: var(--accent);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--accent);
    }}

    /* Pillars */
    .pillars-section {{
      padding: 24px 0 64px;
    }}
    .pillars-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
    }}
    .pillar-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 22px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      transition: all 0.25s ease;
    }}
    .pillar-card:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
    }}
    .pillar-icon {{
      font-size: 1.75rem;
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(245, 158, 11, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .pillar-info h4 {{
      font-size: 0.95rem;
      font-weight: 700;
      margin-bottom: 2px;
    }}
    .pillar-info p {{
      font-size: 0.8rem;
      color: var(--text-dim);
    }}

    /* Menu Catalog Section */
    .menu-section {{
      padding: 40px 0 100px;
    }}
    .menu-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 32px;
      flex-wrap: wrap;
      gap: 20px;
    }}
    .menu-title-group h2 {{
      font-family: var(--font-serif);
      font-size: 2.5rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .menu-title-group p {{
      color: var(--text-muted);
      font-size: 1rem;
      margin-top: 4px;
    }}

    /* Filters Bar */
    .filter-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-pill);
      padding: 8px 12px;
      margin-bottom: 36px;
      flex-wrap: wrap;
    }}
    .category-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .cat-pill {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 8px 18px;
      border-radius: var(--radius-pill);
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .cat-pill:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }}
    .cat-pill.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
      font-weight: 800;
      box-shadow: 0 4px 14px var(--accent-glow);
    }}

    .sort-control {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding-right: 8px;
    }}
    .sort-control label {{
      font-size: 0.85rem;
      color: var(--text-dim);
      font-weight: 600;
    }}
    .sort-select {{
      background: #292524;
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 6px 14px;
      border-radius: var(--radius-pill);
      font-size: 0.85rem;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }}

    /* Food Cards Grid */
    .food-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 28px;
    }}
    .food-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 18px;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
    }}
    .food-card:hover {{
      transform: translateY(-6px);
      border-color: var(--accent);
      box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.7);
      background: var(--bg-card-hover);
    }}
    .card-top {{
      position: relative;
      background: #14110f;
      border-radius: 14px;
      height: 220px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
    }}
    .food-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.5s ease;
    }}
    .food-card:hover .food-img {{
      transform: scale(1.08);
    }}
    .card-badge {{
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(6px);
      color: #fff;
      font-size: 0.7rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: var(--radius-pill);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .card-badge.bestseller {{ background: rgba(234, 88, 12, 0.9); }}
    .card-badge.signature {{ background: rgba(245, 158, 11, 0.9); color: #000; }}
    
    .dietary-tag {{
      position: absolute;
      bottom: 10px;
      left: 10px;
      background: rgba(28, 25, 23, 0.85);
      backdrop-filter: blur(6px);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--accent);
      border: 1px solid rgba(245, 158, 11, 0.2);
    }}

    .card-info {{
      display: flex;
      flex-direction: column;
      flex: 1;
    }}
    .card-cat {{
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 4px;
    }}
    .card-title {{
      font-family: var(--font-serif);
      font-size: 1.25rem;
      font-weight: 700;
      line-height: 1.25;
      margin-bottom: 8px;
      color: var(--text-main);
    }}
    .card-desc-snippet {{
      font-size: 0.85rem;
      color: var(--text-dim);
      line-height: 1.45;
      margin-bottom: 14px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .card-rating {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-bottom: 14px;
    }}
    .stars {{ color: var(--accent); }}

    .card-bottom {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: auto;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .current-price {{
      font-family: var(--font-heading);
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--text-main);
    }}
    .quick-add-btn {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 8px 16px;
      border-radius: var(--radius-pill);
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}
    .quick-add-btn:hover {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}

    /* Modals */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 200;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}
    .modal-overlay.active {{
      opacity: 1;
      pointer-events: auto;
    }}
    .detail-modal {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      max-width: 900px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      position: relative;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
      transform: translateY(20px) scale(0.98);
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .modal-overlay.active .detail-modal {{
      transform: translateY(0) scale(1);
    }}
    .close-modal {{
      position: absolute;
      top: 20px;
      right: 20px;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: var(--text-main);
      font-size: 1.1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10;
      transition: all 0.2s ease;
    }}
    .close-modal:hover {{
      background: var(--accent);
      color: #000;
    }}
    .detail-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 36px;
      padding: 36px;
    }}
    .detail-img-box {{
      background: #14110f;
      border-radius: var(--radius-md);
      overflow: hidden;
      height: 400px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .detail-img-box img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .detail-info {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .custom-group {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .custom-label {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-muted);
    }}
    .spice-grid {{
      display: flex;
      gap: 8px;
    }}
    .spice-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 8px 16px;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
    }}
    .spice-btn.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}

    /* Food Bag Slide-Over Drawer */
    .cart-drawer-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      z-index: 250;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}
    .cart-drawer-overlay.active {{
      opacity: 1;
      pointer-events: auto;
    }}
    .cart-drawer {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 460px;
      max-width: 90vw;
      background: var(--bg-surface);
      border-left: 1px solid var(--border-subtle);
      z-index: 260;
      display: flex;
      flex-direction: column;
      transform: translateX(100%);
      transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -15px 0 35px rgba(0, 0, 0, 0.7);
    }}
    .cart-drawer-overlay.active .cart-drawer {{
      transform: translateX(0);
    }}
    .cart-header {{
      padding: 24px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .cart-header h3 {{
      font-family: var(--font-serif);
      font-size: 1.45rem;
      font-weight: 700;
    }}
    .delivery-eta-pill {{
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #10b981;
      padding: 8px 16px;
      margin: 16px 24px 0;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .cart-items-list {{
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .cart-item {{
      display: flex;
      gap: 16px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 14px;
      align-items: center;
    }}
    .cart-item-img {{
      width: 72px;
      height: 72px;
      border-radius: 10px;
      object-fit: cover;
      background: #14110f;
      flex-shrink: 0;
    }}
    .cart-item-details {{
      flex: 1;
      min-width: 0;
    }}
    .cart-item-title {{
      font-size: 0.95rem;
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .cart-item-meta {{
      font-size: 0.8rem;
      color: var(--text-dim);
      margin: 2px 0 6px;
    }}
    .cart-item-price {{
      font-family: var(--font-heading);
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--accent);
    }}
    .qty-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-pill);
      padding: 2px 8px;
    }}
    .qty-btn {{
      background: transparent;
      border: none;
      color: var(--text-main);
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .qty-val {{
      font-size: 0.85rem;
      font-weight: 700;
      min-width: 16px;
      text-align: center;
    }}
    .cart-item-remove {{
      background: transparent;
      border: none;
      color: var(--text-dim);
      cursor: pointer;
      font-size: 1rem;
      padding: 4px;
      transition: color 0.2s ease;
    }}
    .cart-item-remove:hover {{ color: #ef4444; }}

    .cart-footer {{
      padding: 24px;
      border-top: 1px solid var(--border-subtle);
      background: #14110f;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .promo-box {{
      display: flex;
      gap: 8px;
    }}
    .promo-input {{
      flex: 1;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      color: var(--text-main);
      font-size: 0.85rem;
      outline: none;
    }}
    .promo-btn {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
    }}
    .cart-summary-row {{
      display: flex;
      justify-content: space-between;
      font-size: 0.9rem;
      color: var(--text-muted);
    }}
    .cart-total-row {{
      display: flex;
      justify-content: space-between;
      font-family: var(--font-heading);
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--text-main);
      padding-top: 10px;
      border-top: 1px solid var(--border-subtle);
    }}

    /* Checkout & Reservation Modal */
    .checkout-modal {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      max-width: 640px;
      width: 100%;
      padding: 32px;
      position: relative;
      max-height: 90vh;
      overflow-y: auto;
    }}
    .checkout-tabs {{
      display: flex;
      gap: 12px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }}
    .checkout-tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
    }}
    .checkout-tab-btn.active {{
      background: rgba(245, 158, 11, 0.15);
      color: var(--accent);
    }}
    .checkout-form {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .form-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .form-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .form-group label {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-muted);
    }}
    .form-group input, .form-group select, .form-group textarea {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      color: var(--text-main);
      font-size: 0.9rem;
      outline: none;
      font-family: inherit;
    }}
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {{
      border-color: var(--accent);
    }}

    /* Toast Notification */
    .toast-container {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 300;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }}
    .toast {{
      background: rgba(41, 37, 36, 0.95);
      backdrop-filter: blur(8px);
      border: 1px solid var(--border-subtle);
      border-left: 4px solid var(--accent);
      padding: 14px 20px;
      border-radius: var(--radius-md);
      color: var(--text-main);
      font-size: 0.9rem;
      font-weight: 600;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
      transform: translateX(120%);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .toast.show {{
      transform: translateX(0);
    }}

    /* Footer */
    footer {{
      background: #080605;
      border-top: 1px solid var(--border-subtle);
      padding: 64px 0 32px;
      color: var(--text-muted);
    }}
    .footer-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      gap: 48px;
      margin-bottom: 48px;
    }}
    .footer-col h5 {{
      font-family: var(--font-serif);
      color: var(--text-main);
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 16px;
    }}
    .footer-col ul {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
    .footer-col a {{ color: var(--text-muted); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }}
    .footer-col a:hover {{ color: var(--accent); }}
    .footer-bottom {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 0.85rem;
    }}

    @media (max-width: 1024px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .food-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .pillars-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .footer-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
    @media (max-width: 640px) {{
      .hero-title {{ font-size: 2.8rem; }}
      .food-grid {{ grid-template-columns: 1fr; }}
      .pillars-grid {{ grid-template-columns: 1fr; }}
      .nav-links {{ display: none; }}
      .detail-grid {{ grid-template-columns: 1fr; padding: 20px; }}
      .detail-img-box {{ height: 260px; }}
      .footer-grid {{ grid-template-columns: 1fr; }}
      .hero-metrics {{ flex-direction: column; gap: 16px; }}
    }}
  </style>
</head>
<body>
  {refinement_notice}
  
  <!-- Announcement Banner -->
  <div class="announcement-bar">
    <span>🔥 CRAVE SPECIAL: Use code <strong>CRAVE20</strong> for 20% OFF your first order</span>
    <span class="pill">Fast 30-Min Delivery Over $40</span>
  </div>

  <!-- Header Navigation -->
  <header class="navbar">
    <div class="container nav-inner">
      <a href="#" class="brand">
        <div class="brand-icon">🍴</div>
        <div class="brand-text">{brand_name.split()[0]}<span>{brand_name.split()[-1] if len(brand_name.split()) > 1 else ''}</span></div>
      </a>

      <div class="nav-search">
        <span class="search-icon">🔍</span>
        <input type="text" id="global-search" placeholder="Search truffle risotto, sourdough pizza, burgers..." oninput="handleSearch(this.value)" />
      </div>

      <nav>
        <ul class="nav-links">
          <li><a href="#menu" class="active" onclick="filterCategory('all')">Full Menu</a></li>
          <li><a href="#menu" onclick="filterCategory('specials')">Chef's Table</a></li>
          <li><a href="#menu" onclick="filterCategory('pizza')">Pizzas</a></li>
          <li><a href="#menu" onclick="filterCategory('burger')">Burgers</a></li>
          <li><a href="#menu" onclick="filterCategory('pasta')">Pastas</a></li>
        </ul>
      </nav>

      <div class="nav-actions">
        <button class="reserve-btn" onclick="openReservationModal()">📅 Reserve Table</button>
        <button class="cart-btn" onclick="openCart()">
          <span>🛍️</span>
          <span>Order</span>
          <span class="cart-count" id="cart-badge">0</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="hero-section">
    <div class="container hero-grid">
      <div class="hero-content">
        <div class="hero-badge">✦ ARTISANAL FARM-TO-FORK DINING</div>
        <h1 class="hero-title">FLAVORS CRAFTED TO <span class="gradient-text">PERFECTION.</span></h1>
        <p class="hero-desc">
          Wood-fired sourdough pizzas, 100% Wagyu smash burgers, and handmade ribbons of pasta prepared fresh from scratch daily. Delivered piping hot to your table or doorstep in 30 minutes.
        </p>
        <div class="hero-cta-group">
          <a href="#menu" class="btn-primary">Explore Menu 🍽️</a>
          <button class="btn-secondary" onclick="openReservationModal()">Book a Table 📅</button>
        </div>
        <div class="hero-metrics">
          <div class="metric-item">
            <span class="metric-val">30 Mins</span>
            <span class="metric-lbl">Average Express Delivery</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">★ 4.96 / 5</span>
            <span class="metric-lbl">1,850+ Verified Reviews</span>
          </div>
          <div class="metric-item">
            <span class="metric-val">100%</span>
            <span class="metric-lbl">Fresh Organic Ingredients</span>
          </div>
        </div>
      </div>

      <div class="hero-food-card">
        <img 
          src="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1000&auto=format&fit=crop" 
          alt="{brand_name} Signature Culinary Experience" 
          class="hero-food-img"
        />
        <div class="hero-floating-badge">
          <span class="badge-dot"></span>
          <span>Chef's Signature Table • Made Fresh Daily</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Trust Value Propositions -->
  <section class="pillars-section">
    <div class="container pillars-grid">
      <div class="pillar-card">
        <div class="pillar-icon">🌾</div>
        <div class="pillar-info">
          <h4>Farm-To-Table</h4>
          <p>Locally sourced organic produce & heritage meats.</p>
        </div>
      </div>
      <div class="pillar-card">
        <div class="pillar-icon">🔥</div>
        <div class="pillar-info">
          <h4>800° Wood-Fired</h4>
          <p>48-hour fermented sourdough crust baked on stone.</p>
        </div>
      </div>
      <div class="pillar-card">
        <div class="pillar-icon">⚡</div>
        <div class="pillar-info">
          <h4>30-Min Fast Delivery</h4>
          <p>Thermal insulated packaging delivered piping hot.</p>
        </div>
      </div>
      <div class="pillar-card">
        <div class="pillar-icon">👨‍🍳</div>
        <div class="pillar-info">
          <h4>Master Chef Recipes</h4>
          <p>Curated culinary dining by Executive Chef Antonio.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Menu Catalog Section -->
  <section class="menu-section" id="menu">
    <div class="container">
      <div class="menu-header">
        <div class="menu-title-group">
          <h2>EXPLORE OUR ARTISANAL MENU</h2>
          <p id="results-count">Showing 8 chef-crafted dishes</p>
        </div>
      </div>

      <!-- Filters & Sort Toolbar -->
      <div class="filter-bar">
        <div class="category-pills">
          <button class="cat-pill active" data-cat="all" onclick="filterCategory('all', this)">All Dishes</button>
          <button class="cat-pill" data-cat="specials" onclick="filterCategory('specials', this)">Chef's Specials</button>
          <button class="cat-pill" data-cat="pizza" onclick="filterCategory('pizza', this)">Wood-Fired Pizza</button>
          <button class="cat-pill" data-cat="burger" onclick="filterCategory('burger', this)">Gourmet Burgers</button>
          <button class="cat-pill" data-cat="pasta" onclick="filterCategory('pasta', this)">Handmade Pasta</button>
          <button class="cat-pill" data-cat="dessert" onclick="filterCategory('dessert', this)">Desserts</button>
        </div>
        <div class="sort-control">
          <label for="sort-by">Sort By:</label>
          <select id="sort-by" class="sort-select" onchange="handleSort(this.value)">
            <option value="featured">Chef's Recommendation</option>
            <option value="price-asc">Price: Low to High</option>
            <option value="price-desc">Price: High to Low</option>
            <option value="rating">Most Popular (Rating)</option>
          </select>
        </div>
      </div>

      <!-- Food Dishes Grid -->
      <div class="food-grid" id="food-grid">
        <!-- Rendered dynamically by script -->
      </div>
    </div>
  </section>

  <!-- Dish Detail Modal -->
  <div class="modal-overlay" id="dish-modal" onclick="if(event.target===this) closeModal()">
    <div class="detail-modal">
      <button class="close-modal" onclick="closeModal()">✕</button>
      <div class="detail-grid">
        <div class="detail-img-box">
          <img id="modal-img" src="" alt="Dish Detail" />
        </div>
        <div class="detail-info">
          <span class="card-cat" id="modal-cat">CHEF'S SPECIAL</span>
          <h2 id="modal-title" style="font-family: var(--font-serif); font-size: 1.85rem; font-weight:700;">Dish Title</h2>
          <div class="card-rating">
            <span class="stars">★★★★★</span>
            <span id="modal-rating">4.9</span>
            <span style="color:var(--text-dim);" id="modal-reviews">(312 reviews)</span>
          </div>
          <div class="current-price" id="modal-price" style="font-size:1.75rem; color:var(--accent);">$26.00</div>
          <p id="modal-desc" style="color:var(--text-muted); font-size: 0.95rem; line-height:1.6;">
            Dish description.
          </p>

          <div class="custom-group">
            <span class="custom-label">Select Spice Level:</span>
            <div class="spice-grid">
              <button class="spice-btn active" onclick="selectSpice('Mild', this)">Mild</button>
              <button class="spice-btn" onclick="selectSpice('Medium', this)">Medium 🔥</button>
              <button class="spice-btn" onclick="selectSpice('Hot', this)">Chef's Hot 🔥🔥</button>
            </div>
          </div>

          <div class="custom-group">
            <span class="custom-label">Chef Add-ons:</span>
            <div style="display:flex; flex-direction:column; gap:8px;">
              <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:var(--text-muted); cursor:pointer;">
                <input type="checkbox" id="addon-truffle" value="4" /> Shaved Black Truffle (+$4.00)
              </label>
              <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; color:var(--text-muted); cursor:pointer;">
                <input type="checkbox" id="addon-cheese" value="3" /> Extra Fior di Latte Mozzarella (+$3.00)
              </label>
            </div>
          </div>

          <div style="display:flex; gap:12px; margin-top:16px;">
            <button class="btn-primary" style="flex:1;" onclick="addModalItemToCart()">Add to Order 🛍️</button>
            <button class="btn-secondary" onclick="buyNowModal()">Express Checkout ⚡</button>
          </div>

          <div style="font-size:0.8rem; color:var(--text-dim); display:flex; gap:16px; margin-top:8px;">
            <span>✓ Prepared to Order</span>
            <span>✓ Thermal Packaged</span>
            <span>✓ 30-Min Delivery</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Food Bag Slide-Over Drawer -->
  <div class="cart-drawer-overlay" id="cart-overlay" onclick="if(event.target===this) closeCart()">
    <div class="cart-drawer">
      <div class="cart-header">
        <h3>Your Order Bag (<span id="drawer-count">0</span>)</h3>
        <button class="close-modal" style="position:static;" onclick="closeCart()">✕</button>
      </div>

      <div class="delivery-eta-pill">
        <span>⚡</span>
        <span>Estimated Delivery: 25 - 35 mins</span>
      </div>

      <div class="cart-items-list" id="cart-items-container">
        <!-- Injected by script -->
      </div>

      <div class="cart-footer">
        <div class="promo-box">
          <input type="text" id="promo-code" class="promo-input" placeholder="Promo code (try CRAVE20)" />
          <button class="promo-btn" onclick="applyPromo()">Apply</button>
        </div>
        <div class="cart-summary-row">
          <span>Subtotal</span>
          <span id="cart-subtotal">$0.00</span>
        </div>
        <div class="cart-summary-row" id="discount-row" style="display:none; color:#10b981;">
          <span>Promo Discount (20%)</span>
          <span id="cart-discount">-$0.00</span>
        </div>
        <div class="cart-summary-row">
          <span>Delivery Fee</span>
          <span id="cart-shipping">Free</span>
        </div>
        <div class="cart-summary-row">
          <span>Estimated Sales Tax (8.5%)</span>
          <span id="cart-tax">$0.00</span>
        </div>
        <div class="cart-total-row">
          <span>Total</span>
          <span id="cart-grand-total">$0.00</span>
        </div>
        <button class="btn-primary" style="width:100%; justify-content:center;" onclick="openCheckout()">
          Proceed to Checkout <span>→</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Checkout & Table Reservation Modal -->
  <div class="modal-overlay" id="checkout-modal" onclick="if(event.target===this) closeCheckout()">
    <div class="checkout-modal">
      <button class="close-modal" onclick="closeCheckout()">✕</button>
      
      <div class="checkout-tabs">
        <button class="checkout-tab-btn active" id="tab-delivery-btn" onclick="switchTab('delivery')">🚀 Delivery Checkout</button>
        <button class="checkout-tab-btn" id="tab-reserve-btn" onclick="switchTab('reserve')">📅 Reserve a Table</button>
      </div>

      <!-- Tab 1: Delivery Order -->
      <div id="tab-delivery-content">
        <h3 style="font-family: var(--font-serif); font-size:1.6rem; font-weight:700;">Delivery & Payment Details</h3>
        <p style="color:var(--text-muted); font-size:0.9rem; margin-top:4px;">Enter delivery address and payment to dispatch your order.</p>

        <form class="checkout-form" style="margin-top:20px;" onsubmit="handlePlaceOrder(event)">
          <div class="form-row">
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" required placeholder="Marcus Vance" value="Marcus Vance" />
            </div>
            <div class="form-group">
              <label>Phone Number for SMS Tracking</label>
              <input type="tel" required placeholder="(555) 234-5678" value="(555) 234-5678" />
            </div>
          </div>
          <div class="form-group">
            <label>Delivery Address</label>
            <input type="text" required placeholder="452 Lexington Avenue, Apt 4B" value="452 Lexington Avenue, Apt 4B" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>City</label>
              <input type="text" required placeholder="New York" value="New York" />
            </div>
            <div class="form-group">
              <label>Postal Code</label>
              <input type="text" required placeholder="10017" value="10017" />
            </div>
          </div>
          <div class="form-group">
            <label>Chef & Delivery Instructions (Optional)</label>
            <input type="text" placeholder="e.g. Ring apartment buzzer #4B, leave at door" value="Ring buzzer #4B" />
          </div>
          <div class="form-group">
            <label>Card Payment (256-Bit SSL Encrypted)</label>
            <input type="text" required placeholder="4242 •••• •••• 4242" value="4242 9821 7364 4242" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Expiry (MM/YY)</label>
              <input type="text" required placeholder="08/28" value="08/28" />
            </div>
            <div class="form-group">
              <label>CVV</label>
              <input type="text" required placeholder="931" value="931" />
            </div>
          </div>
          <div style="background:rgba(245,158,11,0.06); padding:16px; border-radius:var(--radius-sm); border:1px solid var(--border-subtle); margin-top:4px;">
            <div style="display:flex; justify-content:space-between; font-weight:700;">
              <span>Total Payable Amount:</span>
              <span id="checkout-total-val" style="color:var(--accent); font-size:1.25rem;">$0.00</span>
            </div>
          </div>
          <button type="submit" class="btn-primary" id="place-order-btn" style="width:100%; justify-content:center; margin-top:8px;">
            Authorize & Dispatch Order 🚀
          </button>
        </form>
      </div>

      <!-- Tab 2: Table Reservation -->
      <div id="tab-reserve-content" style="display:none;">
        <h3 style="font-family: var(--font-serif); font-size:1.6rem; font-weight:700;">Reserve Your Table at {brand_name}</h3>
        <p style="color:var(--text-muted); font-size:0.9rem; margin-top:4px;">Select your preferred dining date, seating, and guest count.</p>

        <form class="checkout-form" style="margin-top:20px;" onsubmit="handleReserveTable(event)">
          <div class="form-row">
            <div class="form-group">
              <label>Guest Name</label>
              <input type="text" required placeholder="Marcus Vance" value="Marcus Vance" />
            </div>
            <div class="form-group">
              <label>Contact Phone</label>
              <input type="tel" required placeholder="(555) 234-5678" value="(555) 234-5678" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Reservation Date</label>
              <input type="date" required value="2026-10-20" />
            </div>
            <div class="form-group">
              <label>Preferred Time</label>
              <select required>
                <option value="6:00 PM">6:00 PM (Dinner)</option>
                <option value="7:00 PM" selected>7:00 PM (Prime Dinner)</option>
                <option value="8:00 PM">8:00 PM (Chef's Tasting)</option>
                <option value="9:00 PM">9:00 PM (Late Night)</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Party Size</label>
              <select required>
                <option value="2">2 Guests (Table for Two)</option>
                <option value="4" selected>4 Guests (Booths)</option>
                <option value="6">6 Guests (Chef's Table)</option>
                <option value="8">8+ Guests (Private Dining)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Seating Preference</label>
              <select required>
                <option value="Main Dining Room">Main Dining Room</option>
                <option value="Patio Terrace">Outdoor Heated Patio</option>
                <option value="Chef Counter">Chef's Tasting Counter</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Special Requests or Dietary Requirements</label>
            <input type="text" placeholder="e.g. Birthday celebration, gluten allergies" value="Anniversary dinner" />
          </div>
          <button type="submit" class="btn-primary" style="width:100%; justify-content:center; margin-top:8px;">
            Confirm Table Reservation 📅
          </button>
        </form>
      </div>
    </div>
  </div>

  <!-- Toast Notification Container -->
  <div class="toast-container" id="toast-container"></div>

  <!-- Footer -->
  <footer>
    <div class="container footer-grid">
      <div class="footer-col">
        <div class="brand" style="margin-bottom: 16px;">
          <div class="brand-icon">🍴</div>
          <div class="brand-text">{brand_name.split()[0]}<span>{brand_name.split()[-1] if len(brand_name.split()) > 1 else ''}</span></div>
        </div>
        <p style="font-size: 0.9rem; max-width: 340px; line-height: 1.6;">
          Artisanal dining meets seamless delivery. Handcrafted wood-fired pizzas, Wagyu smash burgers, and fresh pasta prepared by Executive Chef Antonio.
        </p>
      </div>
      <div class="footer-col">
        <h5>Culinary Menu</h5>
        <ul>
          <li><a href="#menu" onclick="filterCategory('specials')">Chef's Table Selection</a></li>
          <li><a href="#menu" onclick="filterCategory('pizza')">Wood-Fired Sourdough Pizza</a></li>
          <li><a href="#menu" onclick="filterCategory('burger')">Gourmet Wagyu Burgers</a></li>
          <li><a href="#menu" onclick="filterCategory('pasta')">Handmade Silk Pasta</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5>Dining & Service</h5>
        <ul>
          <li><a href="#" onclick="openReservationModal()">Book a Table</a></li>
          <li><a href="#">30-Minute Delivery Guarantee</a></li>
          <li><a href="#">Farm-To-Table Sourcing</a></li>
          <li><a href="#">Private Event Inquiries</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5>Hours & Location</h5>
        <ul style="font-size:0.875rem; color:var(--text-dim);">
          <li>Monday – Thursday: 11:30 AM – 10:30 PM</li>
          <li>Friday – Sunday: 11:00 AM – 11:30 PM</li>
          <li>452 Lexington Avenue, New York, NY</li>
          <li>Direct Line: (555) 234-CRAVE</li>
        </ul>
      </div>
    </div>
    <div class="container footer-bottom">
      <p>© 2026 {brand_name} — Powered by NEXARCH Multi-Agent Intelligence. All rights reserved.</p>
      <p style="color:var(--text-dim);">Freshly Prepared Daily with Passion & Craft.</p>
    </div>
  </footer>

  <!-- Application Logic -->
  <script>
    // Authentic Gourmet Food Dishes
    const DISHES = [
      {{
        id: "dish-1",
        title: "Truffle Forest Mushroom Risotto",
        category: "specials",
        price: 26,
        rating: 4.9,
        reviews: 312,
        badge: "CHEF'S SPECIAL",
        badgeClass: "signature",
        dietary: "Vegetarian • Gluten-Free",
        image: "https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?q=80&w=1000&auto=format&fit=crop",
        desc: "Creamy Carnaroli rice simmered in slow-simmered vegetable broth, wild chanterelle & porcini forest mushrooms, black summer truffle carpaccio, aged 24-month Parmigiano Reggiano, and white truffle herb oil."
      }},
      {{
        id: "dish-2",
        title: "Wood-Fired Margherita D.O.P.",
        category: "pizza",
        price: 22,
        rating: 4.9,
        reviews: 528,
        badge: "BESTSELLER",
        badgeClass: "bestseller",
        dietary: "Vegetarian • Sourdough",
        image: "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?q=80&w=1000&auto=format&fit=crop",
        desc: "48-hour fermented slow sourdough crust baked in our 800° stone oven, San Marzano D.O.P. tomato reduction, fresh Fior di Latte mozzarella, sweet Genovese basil, and Sicilian extra virgin olive oil."
      }},
      {{
        id: "dish-3",
        title: "The Crave Wagyu Smash Burger",
        category: "burger",
        price: 24,
        rating: 4.8,
        reviews: 415,
        badge: "BESTSELLER",
        badgeClass: "bestseller",
        dietary: "100% American Wagyu",
        image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=1000&auto=format&fit=crop",
        desc: "Double 100% American Wagyu beef patties smashed crisp, melted aged smoked cheddar, caramelized shallots, crispy pancetta, and secret Crave umami aioli on a toasted buttered brioche bun."
      }},
      {{
        id: "dish-4",
        title: "Handmade Pappardelle Bolognese",
        category: "pasta",
        price: 25,
        rating: 4.9,
        reviews: 284,
        badge: "SIGNATURE",
        badgeClass: "signature",
        dietary: "Handcrafted Daily",
        image: "https://images.unsplash.com/photo-1621996346565-e3d5d6281699?q=80&w=1000&auto=format&fit=crop",
        desc: "Silky egg pasta ribbons hand-cut daily, tossed in an 8-hour slow-braised beef short rib and heritage pork shoulder ragù, finished with whipped mascarpone and pecorino romano."
      }},
      {{
        id: "dish-5",
        title: "Pan-Seared Chilean Sea Bass",
        category: "specials",
        price: 34,
        rating: 5.0,
        reviews: 195,
        badge: "WILD CAUGHT",
        badgeClass: "",
        dietary: "Gluten-Free • Omega-3",
        image: "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1000&auto=format&fit=crop",
        desc: "Crispy skin Chilean sea bass fillet pan-seared to perfection over velvety saffron cauliflower purée, roasted baby heirloom carrots, and caper lemon brown butter reduction."
      }},
      {{
        id: "dish-6",
        title: "Pugliese Burrata Caprese",
        category: "specials",
        price: 19,
        rating: 4.8,
        reviews: 162,
        badge: "POPULAR",
        badgeClass: "",
        dietary: "Vegetarian Option",
        image: "https://images.unsplash.com/photo-1592417817098-8f3d69102353?q=80&w=1000&auto=format&fit=crop",
        desc: "Creamy 250g Pugliese burrata cheese, 24-month aged Prosciutto di Parma, blistered heirloom cherry tomatoes, cold-pressed basil pesto emulsion, and grilled rosemary focaccia."
      }},
      {{
        id: "dish-7",
        title: "Truffle Pecorino Hand-Cut Fries",
        category: "burger",
        price: 12,
        rating: 4.7,
        reviews: 340,
        badge: "SIDE DISH",
        badgeClass: "",
        dietary: "Vegetarian",
        image: "https://images.unsplash.com/photo-1576107232684-1279f3908594?q=80&w=1000&auto=format&fit=crop",
        desc: "Triple-cooked Kennebec potatoes tossed in white Alba truffle oil, finely grated aged pecorino cheese, fresh parsley, served with house-made black garlic aioli."
      }},
      {{
        id: "dish-8",
        title: "Traditional Espresso Tiramisu",
        category: "dessert",
        price: 14,
        rating: 4.9,
        reviews: 420,
        badge: "HOMEMADE",
        badgeClass: "",
        dietary: "Artisanal Dessert",
        image: "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?q=80&w=1000&auto=format&fit=crop",
        desc: "Savoiardi ladyfingers soaked in dark Illy espresso and dark aged rum, layered with whipped Zabaione mascarpone mousse and dusted with Valrhona Dutch cocoa."
      }}
    ];

    // State
    let cart = [];
    let currentCategory = 'all';
    let currentSearch = '';
    let currentSort = 'featured';
    let selectedModalDish = null;
    let selectedSpice = 'Mild';
    let discountApplied = false;

    // Render Menu Grid
    function renderDishes() {{
      const grid = document.getElementById('food-grid');
      let filtered = DISHES.filter(d => {{
        const matchesCat = currentCategory === 'all' || d.category === currentCategory;
        const matchesSearch = !currentSearch || 
          d.title.toLowerCase().includes(currentSearch.toLowerCase()) ||
          d.category.toLowerCase().includes(currentSearch.toLowerCase()) ||
          d.desc.toLowerCase().includes(currentSearch.toLowerCase());
        return matchesCat && matchesSearch;
      }});

      if (currentSort === 'price-asc') {{
        filtered.sort((a, b) => a.price - b.price);
      }} else if (currentSort === 'price-desc') {{
        filtered.sort((a, b) => b.price - a.price);
      }} else if (currentSort === 'rating') {{
        filtered.sort((a, b) => b.rating - a.rating);
      }}

      document.getElementById('results-count').innerText = `Showing ${{filtered.length}} of ${{DISHES.length}} chef-crafted dishes`;

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; padding: 64px 24px; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-subtle);">
            <h3 style="font-family: var(--font-serif); font-size:1.6rem; margin-bottom:8px;">No matching dishes found</h3>
            <p style="color:var(--text-muted); margin-bottom:16px;">Try searching for pizza, risotto, burger, or pasta.</p>
            <button class="btn-primary" onclick="resetFilters()">View Full Menu</button>
          </div>
        `;
        return;
      }}

      grid.innerHTML = filtered.map(d => `
        <div class="food-card" onclick="openDishModal('${{d.id}}')">
          <div class="card-top">
            <span class="card-badge ${{d.badgeClass}}">${{d.badge}}</span>
            <span class="dietary-tag">${{d.dietary}}</span>
            <img src="${{d.image}}" alt="${{d.title}}" class="food-img" loading="lazy" />
          </div>
          <div class="card-info">
            <span class="card-cat">${{d.category}}</span>
            <h3 class="card-title">${{d.title}}</h3>
            <p class="card-desc-snippet">${{d.desc}}</p>
            <div class="card-rating">
              <span class="stars">★★★★★</span>
              <span>${{d.rating}}</span>
              <span style="color:var(--text-dim);">(${{d.reviews}} reviews)</span>
            </div>
            <div class="card-bottom">
              <span class="current-price">$${{d.price}}.00</span>
              <button class="quick-add-btn" onclick="event.stopPropagation(); quickAddToCart('${{d.id}}')">
                <span>+</span> Add
              </button>
            </div>
          </div>
        </div>
      `).join('');
    }}

    // Filtering & Sorting
    function filterCategory(cat, btn) {{
      currentCategory = cat;
      document.querySelectorAll('.cat-pill').forEach(el => {{
        if (el.getAttribute('data-cat') === cat) el.classList.add('active');
        else el.classList.remove('active');
      }});
      renderDishes();
    }}

    function handleSearch(val) {{
      currentSearch = val.trim();
      renderDishes();
    }}

    function handleSort(val) {{
      currentSort = val;
      renderDishes();
    }}

    function resetFilters() {{
      currentCategory = 'all';
      currentSearch = '';
      document.getElementById('global-search').value = '';
      document.querySelectorAll('.cat-pill').forEach(el => {{
        if (el.getAttribute('data-cat') === 'all') el.classList.add('active');
        else el.classList.remove('active');
      }});
      renderDishes();
    }}

    // Dish Modal
    function openDishModal(dishId) {{
      const dish = DISHES.find(d => d.id === dishId);
      if (!dish) return;
      selectedModalDish = dish;
      selectedSpice = 'Mild';

      document.getElementById('modal-img').src = dish.image;
      document.getElementById('modal-cat').innerText = dish.dietary.toUpperCase();
      document.getElementById('modal-title').innerText = dish.title;
      document.getElementById('modal-rating').innerText = dish.rating;
      document.getElementById('modal-reviews').innerText = `(${{dish.reviews}} reviews)`;
      document.getElementById('modal-price').innerText = `$${{dish.price}}.00`;
      document.getElementById('modal-desc').innerText = dish.desc;

      document.getElementById('dish-modal').classList.add('active');
    }}

    function selectSpice(spice, btn) {{
      selectedSpice = spice;
      document.querySelectorAll('.spice-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }}

    function closeModal() {{
      document.getElementById('dish-modal').classList.remove('active');
    }}

    function addModalItemToCart() {{
      if (!selectedModalDish) return;
      let extra = 0;
      let notes = [];
      if (document.getElementById('addon-truffle') && document.getElementById('addon-truffle').checked) {{
        extra += 4;
        notes.push('Truffle (+$4)');
      }}
      if (document.getElementById('addon-cheese') && document.getElementById('addon-cheese').checked) {{
        extra += 3;
        notes.push('Extra Cheese (+$3)');
      }}
      addToCart(selectedModalDish, selectedSpice, extra, notes.join(', '));
      closeModal();
      openCart();
    }}

    function buyNowModal() {{
      if (!selectedModalDish) return;
      addToCart(selectedModalDish, selectedSpice, 0, '');
      closeModal();
      openCheckout();
    }}

    // Order Cart Management
    function quickAddToCart(dishId) {{
      const dish = DISHES.find(d => d.id === dishId);
      if (!dish) return;
      addToCart(dish, 'Standard', 0, '');
      showToast(`Added ${{dish.title}} to Order Bag!`);
    }}

    function addToCart(dish, spice, extra, customization) {{
      const existing = cart.find(item => item.id === dish.id && item.customization === customization);
      if (existing) {{
        existing.qty += 1;
      }} else {{
        cart.push({{
          id: dish.id,
          title: dish.title,
          category: dish.category,
          price: dish.price + extra,
          image: dish.image,
          customization: customization || `Spice: ${{spice}}`,
          qty: 1
        }});
      }}
      updateCartUI();
    }}

    function updateCartUI() {{
      const totalCount = cart.reduce((sum, item) => sum + item.qty, 0);
      document.getElementById('cart-badge').innerText = totalCount;
      document.getElementById('drawer-count').innerText = totalCount;

      const container = document.getElementById('cart-items-container');
      if (cart.length === 0) {{
        container.innerHTML = `
          <div style="text-align:center; padding: 48px 0; color:var(--text-dim);">
            <div style="font-size:3rem; margin-bottom:12px;">🍽️</div>
            <h4 style="font-family: var(--font-serif); color:var(--text-main); font-size:1.25rem; margin-bottom:4px;">Your Bag is empty</h4>
            <p style="font-size:0.85rem; margin-bottom:20px;">Explore our culinary creations and order your favorite dishes.</p>
            <button class="btn-secondary" onclick="closeCart(); document.getElementById('menu').scrollIntoView();">
              Explore Menu
            </button>
          </div>
        `;
      }} else {{
        container.innerHTML = cart.map((item, idx) => `
          <div class="cart-item">
            <img src="${{item.image}}" alt="${{item.title}}" class="cart-item-img" />
            <div class="cart-item-details">
              <div class="cart-item-title">${{item.title}}</div>
              <div class="cart-item-meta">${{item.customization}}</div>
              <div class="cart-item-price">$${{item.price * item.qty}}.00</div>
            </div>
            <div class="qty-controls">
              <button class="qty-btn" onclick="changeQty(${{idx}}, -1)">-</button>
              <span class="qty-val">${{item.qty}}</span>
              <button class="qty-btn" onclick="changeQty(${{idx}}, 1)">+</button>
            </div>
            <button class="cart-item-remove" onclick="removeCartItem(${{idx}})" title="Remove dish">✕</button>
          </div>
        `).join('');
      }}

      let subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
      let discount = discountApplied ? subtotal * 0.20 : 0;
      let delivery = (subtotal > 40 || subtotal === 0) ? 0 : 4.99;
      let tax = (subtotal - discount) * 0.085;
      let grandTotal = (subtotal - discount) + delivery + tax;

      document.getElementById('cart-subtotal').innerText = `$${{subtotal.toFixed(2)}}`;
      if (discountApplied) {{
        document.getElementById('discount-row').style.display = 'flex';
        document.getElementById('cart-discount').innerText = `-$${{discount.toFixed(2)}}`;
      }} else {{
        document.getElementById('discount-row').style.display = 'none';
      }}
      document.getElementById('cart-shipping').innerText = delivery === 0 ? 'Free' : `$${{delivery.toFixed(2)}}`;
      document.getElementById('cart-tax').innerText = `$${{tax.toFixed(2)}}`;
      document.getElementById('cart-grand-total').innerText = `$${{grandTotal.toFixed(2)}}`;
      document.getElementById('checkout-total-val').innerText = `$${{grandTotal.toFixed(2)}}`;
    }}

    function changeQty(idx, delta) {{
      if (!cart[idx]) return;
      cart[idx].qty += delta;
      if (cart[idx].qty <= 0) {{
        cart.splice(idx, 1);
        showToast('Dish removed from Order');
      }}
      updateCartUI();
    }}

    function removeCartItem(idx) {{
      cart.splice(idx, 1);
      showToast('Dish removed from Order');
      updateCartUI();
    }}

    function applyPromo() {{
      const code = document.getElementById('promo-code').value.trim().toUpperCase();
      if (code === 'CRAVE20') {{
        discountApplied = true;
        updateCartUI();
        showToast('Promo code CRAVE20 applied! 20% discount granted.');
      }} else {{
        showToast('Invalid promo code. Use code "CRAVE20" for 20% off.');
      }}
    }}

    function openCart() {{
      document.getElementById('cart-overlay').classList.add('active');
    }}
    function closeCart() {{
      document.getElementById('cart-overlay').classList.remove('active');
    }}

    // Checkout & Reservation Modal
    function openCheckout() {{
      if (cart.length === 0) {{
        showToast('Your bag is empty! Add a delicious dish first.');
        return;
      }}
      closeCart();
      switchTab('delivery');
      document.getElementById('checkout-modal').classList.add('active');
    }}
    function openReservationModal() {{
      switchTab('reserve');
      document.getElementById('checkout-modal').classList.add('active');
    }}
    function closeCheckout() {{
      document.getElementById('checkout-modal').classList.remove('active');
    }}

    function switchTab(tab) {{
      if (tab === 'delivery') {{
        document.getElementById('tab-delivery-content').style.display = 'block';
        document.getElementById('tab-reserve-content').style.display = 'none';
        document.getElementById('tab-delivery-btn').classList.add('active');
        document.getElementById('tab-reserve-btn').classList.remove('active');
      }} else {{
        document.getElementById('tab-delivery-content').style.display = 'none';
        document.getElementById('tab-reserve-content').style.display = 'block';
        document.getElementById('tab-reserve-btn').classList.add('active');
        document.getElementById('tab-delivery-btn').classList.remove('active');
      }}
    }}

    function handlePlaceOrder(e) {{
      e.preventDefault();
      const btn = document.getElementById('place-order-btn');
      btn.innerHTML = 'Connecting to Kitchen 👨‍🍳...';
      btn.disabled = true;

      setTimeout(() => {{
        const orderId = 'CRV-' + Math.floor(10000 + Math.random() * 90000);
        const modal = document.querySelector('.checkout-modal');
        modal.innerHTML = `
          <div style="text-align:center; padding: 28px 0;">
            <div style="width:72px; height:72px; background:rgba(16,185,129,0.15); border:2px solid #10b981; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px; font-size:2rem; color:#10b981;">
              ✓
            </div>
            <h3 style="font-family: var(--font-serif); font-size: 2rem; font-weight:800; margin-bottom:8px;">
              Order Confirmed & Fired!
            </h3>
            <p style="color:var(--accent); font-weight:700; font-size:1.15rem; margin-bottom:12px;">Order #${{orderId}}</p>
            <p style="color:var(--text-muted); font-size:0.95rem; max-width:440px; margin:0 auto 20px; line-height:1.6;">
              Thank you for ordering with {brand_name}! Executive Chef Antonio has received your ticket. Estimated arrival time is <strong>28 minutes</strong>.
            </p>
            <button class="btn-primary" onclick="resetAfterOrder()" style="margin: 0 auto;">
              Order More Delicious Food 🍽️
            </button>
          </div>
        `;
        cart = [];
        discountApplied = false;
        updateCartUI();
        showToast(`Order #${{orderId}} successfully sent to kitchen!`);
      }}, 1200);
    }}

    function handleReserveTable(e) {{
      e.preventDefault();
      const modal = document.querySelector('.checkout-modal');
      const confCode = 'RES-' + Math.floor(1000 + Math.random() * 9000);
      modal.innerHTML = `
        <div style="text-align:center; padding: 28px 0;">
          <div style="width:72px; height:72px; background:rgba(245,158,11,0.15); border:2px solid var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px; font-size:2rem; color:var(--accent);">
            📅
          </div>
          <h3 style="font-family: var(--font-serif); font-size: 2rem; font-weight:800; margin-bottom:8px;">
            Table Confirmed!
          </h3>
          <p style="color:var(--accent); font-weight:700; font-size:1.15rem; margin-bottom:12px;">Confirmation Code: ${{confCode}}</p>
          <p style="color:var(--text-muted); font-size:0.95rem; max-width:440px; margin:0 auto 20px; line-height:1.6;">
            We look forward to welcoming you to {brand_name}. An SMS confirmation has been sent to your mobile phone.
          </p>
          <button class="btn-primary" onclick="resetAfterOrder()" style="margin: 0 auto;">
            Return to Menu
          </button>
        </div>
      `;
      showToast(`Table successfully reserved! Code: ${{confCode}}`);
    }}

    function resetAfterOrder() {{
      closeCheckout();
      location.reload();
    }}

    function showToast(msg) {{
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      toast.className = 'toast';
      toast.innerHTML = `<span>🍴</span> <span>${{msg}}</span>`;
      container.appendChild(toast);

      setTimeout(() => toast.classList.add('show'), 10);
      setTimeout(() => {{
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 350);
      }}, 3200);
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      renderDishes();
      updateCartUI();
    }});
  </script>
</body>
</html>"""

    def _generate_sneakers_html(self, context: AgentContext, spec: dict, brand_name: str, prioritized_fixes: list) -> str:
        color_tokens = spec.get('color_tokens', {})
        accent = color_tokens.get('accent_primary', '#ff4d00')
        refinement_notice = ''
        if prioritized_fixes:
            refinement_notice = f'<!-- Applied Refinements: {", ".join(prioritized_fixes[:2])} -->'

        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{brand_name} — High-Performance Sneaker Storefront</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #07090e;
      --bg-surface: #0e1320;
      --bg-card: #141c2e;
      --bg-card-hover: #1b263e;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 77, 0, 0.4);
      --accent: {accent if accent != '#38bdf8' else '#ff4d00'};
      --accent-glow: rgba(255, 77, 0, 0.35);
      --accent-secondary: #00f2fe;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --success: #10b981;
      --gold: #fbbf24;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 22px;
      --radius-pill: 9999px;
      --shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
      --font-heading: 'Outfit', sans-serif;
      --font-body: 'Plus Jakarta Sans', sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background-color: var(--bg-dark); color: var(--text-main); font-family: var(--font-body); line-height: 1.5; overflow-x: hidden; min-height: 100vh; }}
    .container {{ max-width: 1320px; margin: 0 auto; padding: 0 24px; }}
    .announcement-bar {{ background: linear-gradient(90deg, #b91c1c, #ea580c, #f59e0b); color: #fff; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; padding: 8px 16px; text-align: center; display: flex; justify-content: center; align-items: center; gap: 12px; }}
    .navbar {{ position: sticky; top: 0; z-index: 100; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); background: rgba(7, 9, 14, 0.85); border-bottom: 1px solid var(--border-subtle); }}
    .nav-inner {{ display: flex; align-items: center; justify-content: space-between; height: 76px; gap: 24px; }}
    .brand {{ display: flex; align-items: center; gap: 10px; text-decoration: none; color: var(--text-main); }}
    .brand-icon {{ width: 40px; height: 40px; background: linear-gradient(135deg, var(--accent), #ff8c00); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; box-shadow: 0 4px 16px var(--accent-glow); }}
    .brand-text {{ font-family: var(--font-heading); font-size: 1.5rem; font-weight: 800; letter-spacing: -0.03em; }}
    .brand-text span {{ color: var(--accent); }}
    .nav-search {{ flex: 1; max-width: 440px; position: relative; }}
    .nav-search input {{ width: 100%; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-pill); padding: 10px 18px 10px 42px; color: var(--text-main); font-size: 0.9rem; outline: none; }}
    .nav-search .search-icon {{ position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--text-dim); }}
    .nav-links {{ display: flex; align-items: center; gap: 28px; list-style: none; }}
    .nav-links a {{ color: var(--text-muted); text-decoration: none; font-size: 0.95rem; font-weight: 600; }}
    .nav-links a:hover, .nav-links a.active {{ color: var(--text-main); }}
    .cart-btn {{ background: linear-gradient(135deg, rgba(255, 77, 0, 0.15), rgba(255, 77, 0, 0.05)); border: 1px solid rgba(255, 77, 0, 0.3); color: var(--text-main); padding: 10px 20px; border-radius: var(--radius-pill); display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 0.9rem; cursor: pointer; }}
    .cart-count {{ background: var(--accent); color: #fff; font-size: 0.75rem; font-weight: 800; padding: 2px 7px; border-radius: var(--radius-pill); }}
    .hero-section {{ padding: 64px 0 80px; position: relative; }}
    .hero-grid {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 48px; align-items: center; }}
    .hero-content {{ display: flex; flex-direction: column; gap: 20px; }}
    .hero-badge {{ display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; background: rgba(255, 77, 0, 0.1); border: 1px solid rgba(255, 77, 0, 0.25); border-radius: var(--radius-pill); color: #ff6a00; font-size: 0.8rem; font-weight: 700; width: fit-content; }}
    .hero-title {{ font-family: var(--font-heading); font-size: 3.75rem; font-weight: 900; line-height: 1.05; letter-spacing: -0.04em; }}
    .hero-title .gradient-text {{ background: linear-gradient(135deg, #fff 30%, #ff8c00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .btn-primary {{ background: linear-gradient(135deg, var(--accent), #ff6a00); color: #fff; padding: 14px 34px; border-radius: var(--radius-pill); font-size: 1rem; font-weight: 700; text-decoration: none; display: inline-flex; align-items: center; gap: 10px; cursor: pointer; border: none; }}
    .btn-secondary {{ background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-subtle); color: var(--text-main); padding: 14px 28px; border-radius: var(--radius-pill); font-size: 1rem; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; cursor: pointer; }}
    .hero-viewport {{ position: relative; border-radius: var(--radius-lg); background: radial-gradient(circle at 50% 40%, #1e293b 0%, #090d16 100%); border: 1px solid var(--border-subtle); overflow: hidden; min-height: 440px; display: flex; align-items: center; justify-content: center; }}
    #viewport-3d-container {{ width: 100%; height: 440px; position: relative; }}
    .hero-img-fallback {{ width: 100%; height: 100%; object-fit: cover; transform: scale(1.05) rotate(-6deg); }}
    .product-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 28px; }}
    .product-card {{ background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 18px; display: flex; flex-direction: column; cursor: pointer; }}
    .card-top {{ position: relative; background: #0b0f19; border-radius: 14px; height: 220px; overflow: hidden; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }}
    .product-img {{ width: 100%; height: 100%; object-fit: cover; }}
    .modal-overlay {{ position: fixed; inset: 0; background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(12px); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 24px; opacity: 0; pointer-events: none; transition: opacity 0.3s ease; }}
    .modal-overlay.active {{ opacity: 1; pointer-events: auto; }}
    .detail-modal {{ background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 36px; position: relative; }}
    .cart-drawer-overlay {{ position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6); z-index: 250; opacity: 0; pointer-events: none; transition: opacity 0.3s ease; }}
    .cart-drawer-overlay.active {{ opacity: 1; pointer-events: auto; }}
    .cart-drawer {{ position: fixed; top: 0; right: 0; bottom: 0; width: 440px; max-width: 90vw; background: var(--bg-surface); border-left: 1px solid var(--border-subtle); z-index: 260; display: flex; flex-direction: column; transform: translateX(100%); transition: transform 0.35s ease; }}
    .cart-drawer-overlay.active .cart-drawer {{ transform: translateX(0); }}
    .checkout-modal {{ background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); max-width: 600px; width: 100%; padding: 32px; position: relative; }}
  </style>
</head>
<body>
  {refinement_notice}
  <div class="announcement-bar">
    <span>🔥 DROP ALERT: Use code <strong>NEXARCH10</strong> for 10% OFF</span>
  </div>
  <header class="navbar">
    <div class="container nav-inner">
      <a href="#" class="brand">
        <div class="brand-icon">👟</div>
        <div class="brand-text">{brand_name}</div>
      </a>
      <div class="nav-search">
        <span class="search-icon">🔍</span>
        <input type="text" id="global-search" placeholder="Search silhouettes..." />
      </div>
      <div class="nav-actions">
        <button class="cart-btn" onclick="openCart()">
          <span>🛒</span>
          <span>Bag</span>
          <span class="cart-count" id="cart-badge">0</span>
        </button>
      </div>
    </div>
  </header>
  <section class="hero-section">
    <div class="container hero-grid">
      <div class="hero-content">
        <div class="hero-badge">✦ LIMITED RELEASE</div>
        <h1 class="hero-title">ENGINEERED FOR <span class="gradient-text">SUPREMACY.</span></h1>
        <p style="color:var(--text-muted); font-size:1.1rem;">High-performance footwear crafted with adaptive spatial cushioning and verified authenticity.</p>
        <div style="display:flex; gap:16px; margin-top:12px;">
          <a href="#catalog" class="btn-primary">Shop Latest Drops →</a>
        </div>
      </div>
      <div class="hero-viewport" id="hero-3d-box">
        <div id="viewport-3d-container">
          <img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1000&auto=format&fit=crop" class="hero-img-fallback" alt="Hero Sneaker" />
        </div>
      </div>
    </div>
  </section>
  <section class="container" id="catalog" style="padding: 40px 0 100px;">
    <h2 style="font-family:var(--font-heading); font-size:2.2rem; margin-bottom:24px;">LATEST SNEAKER DROPS</h2>
    <div class="product-grid" id="product-grid">
      <div class="product-card" onclick="alert('Viewing Air Jordan 1')">
        <div class="card-top">
          <img src="https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1000&auto=format&fit=crop" class="product-img" alt="Shoe 1" />
        </div>
        <h3>Air Jordan 1 Retro High</h3>
        <p style="color:var(--accent); font-weight:800; font-size:1.3rem; margin-top:8px;">$180.00</p>
      </div>
      <div class="product-card" onclick="alert('Viewing Yeezy Boost')">
        <div class="card-top">
          <img src="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=1000&auto=format&fit=crop" class="product-img" alt="Shoe 2" />
        </div>
        <h3>Yeezy Boost 350 V2</h3>
        <p style="color:var(--accent); font-weight:800; font-size:1.3rem; margin-top:8px;">$230.00</p>
      </div>
      <div class="product-card" onclick="alert('Viewing New Balance')">
        <div class="card-top">
          <img src="https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=1000&auto=format&fit=crop" class="product-img" alt="Shoe 3" />
        </div>
        <h3>New Balance 9060</h3>
        <p style="color:var(--accent); font-weight:800; font-size:1.3rem; margin-top:8px;">$150.00</p>
      </div>
      <div class="product-card" onclick="alert('Viewing Nike Dunk')">
        <div class="card-top">
          <img src="https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?q=80&w=1000&auto=format&fit=crop" class="product-img" alt="Shoe 4" />
        </div>
        <h3>Nike Dunk Low Retro</h3>
        <p style="color:var(--accent); font-weight:800; font-size:1.3rem; margin-top:8px;">$115.00</p>
      </div>
    </div>
  </section>
</body>
</html>"""

    def _generate_streaming_html(self, context: AgentContext, spec: dict, brand_name: str, prioritized_fixes: list) -> str:
        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{brand_name} — Streaming Media & Entertainment</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --bg-dark: #07090e; --bg-surface: #10141f; --bg-card: #182030; --accent: #f43f5e; --text-main: #f8fafc; --text-muted: #94a3b8; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg-dark); color: var(--text-main); font-family: 'Plus Jakarta Sans', sans-serif; }}
    .container {{ max-width: 1320px; margin: 0 auto; padding: 0 24px; }}
    .nav {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.08); }}
    .hero {{ padding: 64px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <header class="nav">
      <h2 style="font-family:'Outfit'; color:var(--accent);">{brand_name}</h2>
      <nav><a href="#movies" style="color:#fff; text-decoration:none;">Movies</a></nav>
    </header>
    <section class="hero">
      <h1 style="font-size:3.5rem; font-family:'Outfit';">Unlimited Blockbusters & Series.</h1>
      <p style="color:var(--text-muted); font-size:1.2rem; margin:16px 0 24px;">Stream high-definition cinema anytime, anywhere.</p>
    </section>
  </div>
</body>
</html>"""

    def _generate_dashboard_html(self, context: AgentContext, spec: dict, brand_name: str, prioritized_fixes: list) -> str:
        return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{brand_name} — Operations & Analytics Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --bg-dark: #0a0e17; --bg-surface: #111827; --bg-card: #1f2937; --accent: #38bdf8; --text-main: #f9fafb; --text-muted: #9ca3af; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg-dark); color: var(--text-main); font-family: 'Plus Jakarta Sans', sans-serif; }}
    .container {{ max-width: 1320px; margin: 0 auto; padding: 24px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 32px 0; }}
    .kpi-card {{ background: var(--bg-card); padding: 24px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); }}
  </style>
</head>
<body>
  <div class="container">
    <header style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:16px;">
      <h2 style="font-family:'Outfit'; color:var(--accent);">{brand_name}</h2>
      <span>Live Operational Status: Optimal</span>
    </header>
    <div class="kpi-grid">
      <div class="kpi-card"><h4>Active Users</h4><h2 style="color:var(--accent); font-size:2rem; margin-top:8px;">84,290</h2></div>
      <div class="kpi-card"><h4>Monthly Revenue</h4><h2 style="color:#10b981; font-size:2rem; margin-top:8px;">$124,500</h2></div>
      <div class="kpi-card"><h4>Average Latency</h4><h2 style="color:var(--text-main); font-size:2rem; margin-top:8px;">18ms</h2></div>
      <div class="kpi-card"><h4>Satisfaction Score</h4><h2 style="color:#fbbf24; font-size:2rem; margin-top:8px;">99.4%</h2></div>
    </div>
  </div>
</body>
</html>"""

    def _generate_portfolio_html(self, context: AgentContext, spec: dict, brand_name: str, prioritized_fixes: list) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{brand_name} — Creative Portfolio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{ --bg-dark: #090d16; --bg-surface: #111827; --bg-card: #1f293d; --accent: #8b5cf6; --text-main: #f3f4f6; --text-muted: #9ca3af; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg-dark); color: var(--text-main); font-family: 'Plus Jakarta Sans', sans-serif; }}
    .container {{ max-width: 1280px; margin: 0 auto; padding: 0 24px; }}
    .hero {{ padding: 80px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <header style="display:flex; justify-content:space-between; padding:24px 0; border-bottom:1px solid rgba(255,255,255,0.08);">
      <h2 style="font-family:'Outfit';">{brand_name}</h2>
    </header>
    <section class="hero">
      <h1 style="font-size:3.5rem; font-family:'Outfit';">Design & Engineering Showcase.</h1>
      <p style="color:var(--text-muted); font-size:1.2rem; margin-top:16px;">Curated works spanning spatial UI, interactive web apps, and design systems.</p>
    </section>
  </div>
</body>
</html>"""

    def _generate_generic_html(self, context: AgentContext, spec: dict, brand_name: str, prioritized_fixes: list) -> str:
        color_tokens = spec.get('color_tokens', {})
        bg_primary = color_tokens.get('bg_primary', '#090d16')
        bg_surface = color_tokens.get('bg_surface', '#111827')
        bg_card = color_tokens.get('bg_card', '#1f293d')
        text_primary = color_tokens.get('text_primary', '#f3f4f6')
        text_secondary = color_tokens.get('text_secondary', '#9ca3af')
        accent = color_tokens.get('accent_primary', '#6366f1')

        asset_spec = spec.get('asset_spec', {})
        photos = asset_spec.get('photos', [])
        hero_photo = photos[0]['url'] if photos else 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1000&auto=format&fit=crop'
        secondary_photo = photos[1]['url'] if len(photos) > 1 else hero_photo

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{brand_name} — High-Performance Experience</title>
  <style>
    :root {{
      --bg-primary: {bg_primary};
      --bg-surface: {bg_surface};
      --bg-card: {bg_card};
      --text-primary: {text_primary};
      --text-secondary: {text_secondary};
      --accent-primary: {accent};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg-primary); color: var(--text-primary); font-family: system-ui, sans-serif; }}
    .container {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
  </style>
</head>
<body>
  <div class="container">
    <header style="display:flex; justify-content:space-between; padding:24px 0; border-bottom:1px solid rgba(255,255,255,0.08);">
      <h2>{brand_name}</h2>
    </header>
    <main style="padding:64px 0;">
      <h1 style="font-size:3rem;">{brand_name}</h1>
      <p style="color:var(--text-secondary); margin-top:12px;">Crafted with autonomous multi-agent intelligence and precision specifications.</p>
    </main>
  </div>
</body>
</html>"""

    def get_fallback_output(self, context: AgentContext, error_msg: str, **kwargs) -> Dict[str, Any]:
        proj_dir = Path(context.workspace_root) / context.project_name
        proj_dir.mkdir(parents=True, exist_ok=True)
        index_path = proj_dir / 'index.html'
        if not index_path.exists():
            index_path.write_text(f'<!DOCTYPE html><html><body><h1>{context.project_name}</h1></body></html>', encoding='utf-8')
        return {'files_written': ['index.html'], 'fallback_used': True}
