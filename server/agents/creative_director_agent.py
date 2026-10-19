import logging
from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.agents.schemas import AgentContext, CreativeDirectionSpec
from server.agents.llm_client import LLMClient
from server.tools.creative_direction_engine import CreativeDirectionEngine
from server.tools.component_discovery import ComponentDiscoveryCatalog
from server.tools.asset_discovery import AssetDiscoveryService

logger = logging.getLogger('agent.CreativeDirector')

class CreativeDirectorAgent(BaseAgent):
    BANNED_ANTI_PATTERNS = [
        'Banned Anti-Pattern 1: Repetitive centered hero sections with generic centered text',
        'Banned Anti-Pattern 2: Unnecessary purple-blue AI gradient backgrounds',
        'Banned Anti-Pattern 3: Excessive identical rounded card containers',
        'Banned Anti-Pattern 4: Generic floating decorative shapes without domain meaning',
        'Banned Anti-Pattern 5: Repeated 3-column feature grids on every section',
        'Banned Anti-Pattern 6: Unmotivated decorative animations that delay reading',
        'Banned Anti-Pattern 7: Placeholder 3D geometry presented as a finished product',
        'Banned Anti-Pattern 8: Non-functional buttons and broken navigation links',
        'Banned Anti-Pattern 9: Inconsistent typography sizes and haphazard margin spacing',
        'Banned Anti-Pattern 10: Emoji characters as UI icons (e.g. 👟, 🛒, 🍔, ⭐, 🚀). Must use Lucide React vector icons',
        'Banned Anti-Pattern 11: Mismatched clipart, awkward logos, or random symbols. Use clean typographic branding with geometric monogram when no logo exists',
        'Banned Anti-Pattern 12: Blindly reusing identical components across all websites. Purpose-match React Bits components to the specific site identity',
        'Banned Anti-Pattern 13: Anthropic AI Slop tells (warm cream #F4F1EA + terracotta #D97757 cliché, unmotivated dark-mode purple/neon gradients, single-word italic headline styling)',
        'Banned Anti-Pattern 14: Template chrome (tracked-out ALL-CAPS eyebrows on every heading, meta strings with middle dots A · B · C, and appending "→" to every button)',
        'Banned Anti-Pattern 15: Muddy heavy box shadows instead of UI.sh/Vercel hairline borders (ring-1 ring-inset ring-white/10)',
        'Banned Anti-Pattern 16: Poor accessibility & focus suppression (outline-none without focus-visible replacement, touch targets < 44px, contrast < 4.5:1)',
        'Banned Anti-Pattern 17: Non-tabular metrics jitter (numbers in metrics/telemetry must use tabular-nums)'
    ]


    def __init__(self):
        super().__init__(
            name='CreativeDirector',
            role_description='Synthesizes Anthropic, UI/UX Pro Max, Vercel, and UI.sh frameworks into bespoke CreativeDirectionSpec.'
        )
        self.llm = LLMClient()
        self.engine = CreativeDirectionEngine()
        self.catalog = ComponentDiscoveryCatalog()
        self.asset_service = AssetDiscoveryService()

    def run(self, context: AgentContext, **kwargs) -> Dict[str, Any]:
        prompt = context.target_project_brief or context.user_prompt
        ref_spec = kwargs.get('reference_spec', {})
        p_lower = prompt.lower()
        asset_data = self.asset_service.discover_assets(prompt)

        # Retrieve or classify target domain from clean brief
        from server.tools.prompt_reference_parser import PromptReferenceParser
        target_domain = context.target_domain or PromptReferenceParser._classify_domain(prompt)

        # 1. Attempt LLM-driven Creative Direction formulation synthesizing the 4 UI skills
        llm_spec = None
        if self.llm.is_configured():
            try:
                system_prompt = (
                    "You are an elite Creative Director at NEXARCH synthesizing four master UI design frameworks: "
                    "1. Anthropic Frontend Design (bespoke visual identity, anti-slop check, distinct typography, active voice copy, spend boldness in one place), "
                    "2. UI/UX Pro Max (10 design archetypes: Glassmorphism, Bento Grid, Minimalist Luxury, Dark Cyberpunk, Swiss International, Neo-Brutalist, Soft UI, Retro-Futuristic, Organic Editorial, High-Energy Studio; 8pt spatial grid; WCAG AA contrast), "
                    "3. Vercel Web Design & React Guidelines (Geist monochromatic sleekness, hairline borders, tabular-nums for metrics, balanced headings, visible focus rings, zero waterfalls), "
                    "4. UI.sh (visual hierarchy through weight/color rather than font size alone, generous whitespace, ring-1 borders over muddy shadows, tinted neutrals). "
                    f"Target Domain: {target_domain}. Analyze the user's project request and formulate a sophisticated creative direction tailored specifically to this product. "
                    "Output a JSON object with keys: "
                    "'archetype' (e.g. 'Dark Cyberpunk / Terminal', 'Bento Grid Architecture', 'Glassmorphism', 'Minimalist Luxury', 'Swiss International', 'High-Energy Footwear Studio', 'Artisanal Warm Culinary'), "
                    "'rationale' (1-sentence rationale explaining why this archetype fits the domain), "
                    "'concept' (1-sentence concept), "
                    "'color_tokens' (object with 4-6 named hex codes for bg_primary, bg_surface, bg_card, text_primary, text_muted, accent_primary, accent_secondary, border_color), "
                    "'fonts' (object with heading e.g. 'Space Grotesk' or 'Outfit' or 'Syne', body e.g. 'Plus Jakarta Sans'), "
                    "'spacing_scale' (e.g. '8pt grid: 16px cards, 24px container gaps, 64-96px section padding'), "
                    "'requires_3d' (boolean, true ONLY if explicitly requested or for 3D product showcase like shoes/chairs)."
                )
                llm_spec = self.llm.call_llm_json(system_prompt, f"Target Project Brief ({target_domain}): {prompt}", temperature=0.2)
            except Exception as e:
                logger.warning(f"CreativeDirector LLM call error: {e}")

        # Domain classification strictly governed by target_domain (never by reference links or attached images)
        is_food_domain = (target_domain in ["RESTAURANT_FOOD", "RESTAURANT_CULINARY"])
        is_fashion_domain = (target_domain in ["EDITORIAL_FASHION", "FASHION_APPAREL"])
        is_sculptural_furniture = (target_domain == "SCULPTURAL_FURNITURE")
        is_luxury_real_estate = (target_domain in ["ORGANIC_SANCTUARY", "REAL_ESTATE"])
        is_luxury_atelier = (target_domain == "LUXURY_ATELIER")
        is_architectural_stone = (target_domain == "EDITORIAL_ARCHITECTURAL")
        is_agency_domain = (target_domain == "CREATIVE_AGENCY")
        is_streaming_devtool = (target_domain == "STREAMING_DATA_DEVTOOL")
        is_footwear_domain = (target_domain == "FOOTWEAR_SNEAKERS")
        is_fintech_domain = (target_domain == "DASHBOARD" or "fintech" in p_lower)
        is_health_wellness = (target_domain == "FITNESS_WELLNESS" or "wellness" in p_lower)

        # Purpose-match React Bits components and Lucide vector icons
        react_bits_guidance = self.catalog.get_purpose_matched_reactbits(prompt, target_domain)

        if llm_spec and isinstance(llm_spec, dict) and llm_spec.get('archetype'):
            archetype = llm_spec.get('archetype')
            requires_3d = bool(llm_spec.get('requires_3d', False)) and not (is_food_domain or is_fashion_domain or is_architectural_stone or is_sculptural_furniture or is_luxury_real_estate or is_luxury_atelier)
            design_concept = llm_spec.get('concept', f"{context.project_name} — {archetype}")
            rationale = llm_spec.get('rationale', 'Bespoke design direction matching user request')
            llm_colors = llm_spec.get('color_tokens', {})
            llm_fonts = llm_spec.get('fonts', {})
        else:
            if is_food_domain:
                archetype = 'Artisanal Warm Culinary / Farm-to-Table Gastronomy'
                design_concept = f"{context.project_name} — Artisanal Dining & Organic Gastronomy"
                rationale = 'Linen oatmeal background with deep forest olive and warm terracotta accents reflecting authentic craft cuisine and rich dining experience'
            elif is_fashion_domain:
                archetype = 'Minimalist Luxury / Editorial High Fashion'
                design_concept = f"{context.project_name} — Editorial High Fashion Lookbook"
                rationale = 'Editorial cream and deep heritage burgundy palette with refined serif typography and subtle champagne particle ambience'
            elif is_sculptural_furniture:
                archetype = 'Sculptural Luxury Furniture & Interior Craft'
                design_concept = f"{context.project_name} — Sculptural Interior Attraction"
                rationale = 'Vibrant burnt terracotta and ochre with tactile cream linen and monumental seating silhouettes breaking container boundaries'
            elif is_luxury_real_estate:
                archetype = 'Futuristic Organic Sanctuary / Spatial Real Estate'
                design_concept = f"{context.project_name} — Organic Spatial Sanctuaries"
                rationale = 'Floating soft-pill canvas container over alpine mist landscape with sunset tungsten glow against desert twilight'
            elif is_luxury_atelier:
                archetype = 'Luxury Editorial Atelier / Royal Crimson & Rose Gold'
                design_concept = f"{context.project_name} — Luxury Brand Design Atelier"
                rationale = 'Deep royal crimson background with champagne rose gold accents, condensed serif typography, and layered botanical portraiture'
            elif is_architectural_stone:
                archetype = 'Editorial Architectural Studio / Warm Monolithic Stone'
                design_concept = f"{context.project_name} — Monolithic Spatial Architecture"
                rationale = 'Warm travertine limestone background with basalt iron typography, burnt terracotta accents, and structural photography celebrating monolithic built environments'
            elif is_agency_domain:
                archetype = 'High-Contrast Architectural Studio / Swiss International'
                design_concept = f"{context.project_name} — Creative Studio Portfolio"
                rationale = 'Obsidian backdrop with electric cobalt blue and butter yellow accents for dynamic agency punch'
            elif is_streaming_devtool:
                archetype = 'Deep Terminal Slate / Distributed Systems Engine'
                design_concept = f"{context.project_name} — Real-Time Streaming Telemetry"
                rationale = 'Deep slate console with cyan telemetry pulse and tabular metrics'
            elif is_footwear_domain:
                archetype = 'High-Energy Athletic Studio / Neo-Brutalist'
                design_concept = f"{context.project_name} — High-Performance Footwear Studio"
                rationale = 'Carbon backdrop with ember orange and crisp titanium highlights engineered for peak physical motion'
            elif is_fintech_domain:
                archetype = 'Monochromatic Precision / FinTech Intelligence'
                design_concept = f"{context.project_name} — Enterprise Financial Intelligence"
                rationale = 'Midnight graphite with emerald prosperity pulse and strict tabular-nums precision'
            elif is_health_wellness:
                archetype = 'Calm Botanical / Organic Wellness'
                design_concept = f"{context.project_name} — Holistic Wellness & Care"
                rationale = 'Off-white linen with muted sage teal and warm sand accents creating an open, calming atmosphere'
            else:
                archetype = 'Refined Monochromatic Studio'
                design_concept = f"{context.project_name} — {archetype}"
                rationale = 'Deep charcoal base with crisp white hierarchy and warm amber micro-interactions, avoiding clichéd gradients'
            llm_colors = {}
            llm_fonts = {}

            requires_3d = False
            if any(k in p_lower for k in ['3d', 'spatial', 'webgl', 'mesh', 'r3f', 'model']):
                requires_3d = True
            elif not (is_food_domain or is_fashion_domain) and any(k in p_lower for k in ['shoe', 'footwear', 'sneaker', 'chair', 'vehicle', 'car']):
                requires_3d = True

        three_d_spec = {}
        if requires_3d and asset_data.get('models_3d'):
            model_info = asset_data['models_3d'][0]
            three_d_spec = {
                'model_name': model_info['name'],
                'model_url': model_info['url'],
                'cameraZ': 4,
                'lighting': 'studio',
                'auto_rotate': True,
                'particle_bg': True,
                'particle_color': '#38bdf8'
            }

        if llm_colors:
            color_tokens = {
                'bg_primary': llm_colors.get('bg_primary', '#0c0a09'),
                'bg_surface': llm_colors.get('bg_surface', '#1c1917'),
                'bg_card': llm_colors.get('bg_card', '#292524'),
                'text_primary': llm_colors.get('text_primary', '#fafaf9'),
                'text_secondary': llm_colors.get('text_muted', '#a8a29e'),
                'accent_primary': llm_colors.get('accent_primary', '#f59e0b'),
                'accent_hover': llm_colors.get('accent_secondary', '#d97706'),
                'border_color': 'rgba(255, 255, 255, 0.12)'
            }
        elif is_sculptural_furniture:
            color_tokens = {
                'bg_primary': '#FFF8F0',
                'bg_surface': '#F4ECE1',
                'bg_card': '#FFFFFF',
                'text_primary': '#191716',
                'text_secondary': '#8C7E72',
                'accent_primary': '#E85A2A',
                'accent_hover': '#C84B20',
                'accent_secondary': '#D85224',
                'border_color': 'rgba(25, 23, 22, 0.12)'
            }
        elif is_luxury_real_estate:
            color_tokens = {
                'bg_primary': '#DDE4EB',
                'bg_surface': '#FFFFFF',
                'bg_card': '#F8FAFC',
                'text_primary': '#1E293B',
                'text_secondary': '#64748B',
                'accent_primary': '#3B82F6',
                'accent_hover': '#2563EB',
                'accent_secondary': '#F59E0B',
                'border_color': 'rgba(255, 255, 255, 0.8)'
            }
        elif is_luxury_atelier:
            color_tokens = {
                'bg_primary': '#140409',
                'bg_surface': '#280812',
                'bg_card': '#3D0C1C',
                'text_primary': '#FDFBF7',
                'text_secondary': '#D4D4D8',
                'accent_primary': '#E8B4A2',
                'accent_hover': '#D89F8B',
                'accent_secondary': '#C58F7C',
                'border_color': 'rgba(232, 180, 162, 0.2)'
            }
        elif is_architectural_stone:
            color_tokens = {
                'bg_primary': '#F5F2EB',
                'bg_surface': '#ECE7DE',
                'bg_card': '#E2DBD0',
                'text_primary': '#1C1917',
                'text_secondary': '#6B665E',
                'accent_primary': '#A45A2A',
                'accent_hover': '#85441E',
                'accent_secondary': '#4D5B4E',
                'border_color': 'rgba(28, 25, 23, 0.12)'
            }
        elif is_fashion_domain:
            color_tokens = {
                'bg_primary': '#FDFBF7',
                'bg_surface': '#FFFFFF',
                'bg_card': '#F7F5F0',
                'text_primary': '#1C1917',
                'text_secondary': '#78716C',
                'accent_primary': '#4A1525',
                'accent_hover': '#6B1D2F',
                'accent_secondary': '#C5A880',
                'border_color': 'rgba(74, 21, 37, 0.12)'
            }
        elif is_food_domain:
            color_tokens = {
                'bg_primary': '#F6F4EE',
                'bg_surface': '#FFFFFF',
                'bg_card': '#EFECE4',
                'text_primary': '#1C1917',
                'text_secondary': '#57534E',
                'accent_primary': '#283618',
                'accent_hover': '#3A4F23',
                'accent_secondary': '#BC6C25',
                'border_color': 'rgba(40, 54, 24, 0.15)'
            }
        elif is_agency_domain:
            color_tokens = {
                'bg_primary': '#0A0A0C',
                'bg_surface': '#121216',
                'bg_card': '#18181E',
                'text_primary': '#FFFFFF',
                'text_secondary': '#A1A1AA',
                'accent_primary': '#1E40AF',
                'accent_hover': '#3B82F6',
                'accent_secondary': '#FEF08A',
                'border_color': 'rgba(255, 255, 255, 0.12)'
            }
        elif is_streaming_devtool:
            color_tokens = {
                'bg_primary': '#07090e',
                'bg_surface': '#0d121f',
                'bg_card': '#141c2e',
                'text_primary': '#f8fafc',
                'text_secondary': '#94a3b8',
                'accent_primary': '#38bdf8',
                'accent_hover': '#0284c7',
                'accent_secondary': '#10b981',
                'border_color': 'rgba(56, 189, 248, 0.2)'
            }
        elif is_footwear_domain:
            color_tokens = {
                'bg_primary': '#0C0A09',
                'bg_surface': '#1C1917',
                'bg_card': '#292524',
                'text_primary': '#FAFAF9',
                'text_secondary': '#A8A29E',
                'accent_primary': '#F97316',
                'accent_hover': '#EA580C',
                'accent_secondary': '#E2E8F0',
                'border_color': 'rgba(255, 255, 255, 0.12)'
            }
        elif is_fintech_domain:
            color_tokens = {
                'bg_primary': '#090D16',
                'bg_surface': '#111827',
                'bg_card': '#1E293B',
                'text_primary': '#F8FAFC',
                'text_secondary': '#94A3B8',
                'accent_primary': '#10B981',
                'accent_hover': '#059669',
                'accent_secondary': '#38BDF8',
                'border_color': 'rgba(16, 185, 129, 0.2)'
            }
        elif is_health_wellness:
            color_tokens = {
                'bg_primary': '#FAF9F6',
                'bg_surface': '#FFFFFF',
                'bg_card': '#F0EFEA',
                'text_primary': '#1C1917',
                'text_secondary': '#57534E',
                'accent_primary': '#2D6A4F',
                'accent_hover': '#1B4332',
                'accent_secondary': '#D97706',
                'border_color': 'rgba(45, 106, 79, 0.15)'
            }
        else:
            color_tokens = {
                'bg_primary': '#121214',
                'bg_surface': '#1A1A1E',
                'bg_card': '#24242A',
                'text_primary': '#FAFAFA',
                'text_secondary': '#A1A1AA',
                'accent_primary': '#D97706',
                'accent_hover': '#B45309',
                'accent_secondary': '#F59E0B',
                'border_color': 'rgba(255, 255, 255, 0.1)'
            }

        domain_notes = f'Bespoke prompt-driven creative direction for {archetype}.'
        if ref_spec and isinstance(ref_spec, dict) and ref_spec.get('visual_identity'):
            ref_identity = ref_spec.get('visual_identity', 'Reference Design')
            ref_palette = ref_spec.get('color_palette', [])
            domain_notes = f"Adapted reference '{ref_identity}' aesthetic (color palette {ref_palette[:3]}, precision typography) into target product domain '{prompt}'."
            if ref_palette and len(ref_palette) >= 3:
                color_tokens['bg_primary'] = ref_palette[0]
                color_tokens['bg_surface'] = ref_palette[1] if len(ref_palette) > 1 else '#111827'
                color_tokens['accent_primary'] = ref_palette[2] if len(ref_palette) > 2 else '#38bdf8'

        if llm_fonts:
            heading_font = llm_fonts.get('heading', 'Outfit, sans-serif')
            body_font = llm_fonts.get('body', 'Plus Jakarta Sans, sans-serif')
        elif is_fashion_domain:
            heading_font = "'Cinzel', 'Playfair Display', serif"
            body_font = "'Plus Jakarta Sans', sans-serif"
        elif is_food_domain:
            heading_font = "'Playfair Display', serif"
            body_font = "'Plus Jakarta Sans', sans-serif"
        elif is_agency_domain:
            heading_font = "'Syne', 'Space Grotesk', sans-serif"
            body_font = "'Plus Jakarta Sans', sans-serif"
        elif is_streaming_devtool:
            heading_font = "'Outfit', sans-serif"
            body_font = "'Plus Jakarta Sans', sans-serif"
        else:
            heading_font = "'Outfit', sans-serif"
            body_font = "'Plus Jakarta Sans', sans-serif"

        # Domain-specific section sequences, signature interactions, and functional checklist
        if is_food_domain:
            section_sequence = [
                "Editorial Navigation with Live Food Bag Counter & Reservation CTA",
                "Asymmetrical Culinary Hero with Signature Dish Showcase & Provencal Provenance",
                "Live Dish Search & Course Category Filter Rail (Starters, Mains, Pasta, Dolci, Cocktails)",
                "Gourmet Dish Grid with Portion Customizer Trigger & Dietary Badges",
                "Chef's Tasting Philosophy & Farm-to-Table Artisanal Story",
                "Table Concierge & Reservation Booking Suite",
                "Guest Reviews & Culinary Accolades",
                "Footer with Operating Hours, Cellar Details & Allergen Information"
            ]
            signature_interaction = "Slide-over interactive Food Bag drawer with real-time bill breakdown, dish customizer modal, and express culinary checkout"
        elif is_fashion_domain:
            section_sequence = [
                "Atelier Monogram Header with Seasonal Curated Drop Indicator",
                "Full-bleed Editorial Hero with Haute Couture Imagery and Dynamic Lookbook Trigger",
                "Seasonal Runway Collection Filter and Garment Grid",
                "Fabric, Textile Craftsmanship & Heritage Provenance Deep Dive",
                "Lookbook Gallery with Quick Size/Variant Selector",
                "Private Client Consultation & Atelier Booking Suite",
                "Editorial Footer with Stockists and Care Instructions"
            ]
            signature_interaction = "Full-bleed interactive lookbook inspection with fabric texture zoom and size selector modal"
        elif is_sculptural_furniture:
            section_sequence = [
                "Architectural Header with Piece Portfolio Link",
                "Monumental Hero Chair Showcase with Asymmetrical Floating Silhouette",
                "Curated Pieces Catalog with Tactile Material Origin Badges",
                "Tactile Material Swatches and Woodcraft Provenance",
                "Piece Acquisition & Limited Edition Inquiry Modal",
                "Designer Statement and Studio Architectural Philosophy",
                "Footer with Atelier Address and Exhibition Schedule"
            ]
            signature_interaction = "Monumental 3D/silhouette rotation with tactile material swatches and bespoke commission drawer"
        elif is_luxury_real_estate:
            section_sequence = [
                "Organic Pill Navigation Header with Sanctuary Quick Actions",
                "Floating Soft-Pill Canvas Container over Scenic Mountain/Desert Mist Backdrop",
                "Spatial Telemetry & Sanctuary Specification Grid",
                "Curated Residence Showcase with High-Res Architectural Photography",
                "Private Walkthrough Scheduling and Sanctuary Acquisition Suite",
                "Architectural Masterplan and Sustainable Sanctuary Philosophy",
                "Sanctuary Footer with Global Concierge Contacts"
            ]
            signature_interaction = "Floating pill canvas viewport with ambient landscape transitions and private tour reservation modal"
        else:
            section_sequence = [
                "Precision Header with Domain Monogram",
                "Asymmetric Brand Identity Hero with Core Value Proposition",
                "Interactive Domain Content Grid with Search & Category Filters",
                "Detailed Feature / Product Inspection Showcase",
                "Technical / Brand Provenance Narrative",
                "Interactive Conversion Action / Booking Modal",
                "Comprehensive Domain Footer"
            ]
            signature_interaction = "Purpose-built interactive inspection modal and domain action workflow"

        functional_checklist = context.functional_checklist or PromptReferenceParser._extract_functional_requirements(prompt, target_domain)
        design_principles_borrowed = ref_spec.get('design_principles', [
            'Asymmetric visual balance',
            'Curated typography hierarchy',
            'Authentic photography integration',
            'Generous negative space'
        ])

        spec = CreativeDirectionSpec(
            design_concept=f"{archetype} — {rationale}",
            visual_identity=ref_spec.get('visual_identity', archetype),
            target_domain=target_domain,
            functional_checklist=functional_checklist,
            signature_interaction=signature_interaction,
            section_sequence=section_sequence,
            design_principles_borrowed=design_principles_borrowed,
            color_tokens=color_tokens,
            typography_system={
                'font_imports': asset_data.get('fonts', []),
                'heading_font': heading_font,
                'body_font': body_font,
                'scale': {'h1': '56px', 'h2': '36px', 'h3': '24px', 'body': '16px'}
            },
            layout_rules=[
                'Asymmetric hero section with 1280px max-width container',
                '12-column grid layout with 32px gutter spacing',
                'Vertical rhythm: 96px section padding desktop, 48px mobile'
            ],
            motion_philosophy='Staggered GSAP ScrollTrigger timeline entrance (0.7s power3.out, 0.15s stagger). Lenis momentum scroll.',
            requires_3d=requires_3d,
            three_d_spec=three_d_spec,
            domain_adaptation_notes=domain_notes,
            asset_spec={
                'topic': asset_data.get('topic', 'Creative Showcase'),
                'photos': asset_data.get('photos', []),
                'hdri_maps': asset_data.get('hdri_maps', []),
                'fallback_image': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1000&auto=format&fit=crop'
            },
            responsive_rules=[
                'Mobile drawer navigation menu for viewports < 768px',
                'Stack cards into single-column layout on mobile (< 640px)',
                'Scale hero font sizes down by 30% for mobile viewports'
            ],
            accessibility_rules=[
                'Check prefers-reduced-motion media query to pause GSAP ScrollTrigger timeline',
                'Ensure text contrast ratio >= 4.5:1 against surface background',
                'Attach explicit aria-label attributes on interactive controls'
            ],
            anti_patterns=self.BANNED_ANTI_PATTERNS,
            react_bits_spec=react_bits_guidance.get('selected_components', {}),
            icon_spec={
                'lucide_icons': react_bits_guidance.get('lucide_icons', []),
                'branding_badge': react_bits_guidance.get('branding_badge', 'NX'),
                'anti_patterns': react_bits_guidance.get('anti_patterns', [])
            }
        )
        return spec.model_dump()

    def get_fallback_output(self, context: AgentContext, error_msg: str, **kwargs) -> Dict[str, Any]:
        p_lower = context.user_prompt.lower()
        if any(k in p_lower for k in ["fashion", "velour", "couture", "apparel", "runway"]):
            colors = {
                'bg_primary': '#FDFBF7',
                'bg_surface': '#FFFFFF',
                'bg_card': '#F7F5F0',
                'text_primary': '#1C1917',
                'text_secondary': '#78716C',
                'accent_primary': '#4A1525',
                'accent_hover': '#6B1D2F',
                'border_color': 'rgba(74, 21, 37, 0.12)'
            }
            ident = "Velour Atelier High Fashion"
        elif any(k in p_lower for k in ["restaurant", "food", "dining", "kitchen", "osteria", "culinary"]):
            colors = {
                'bg_primary': '#F6F4EE',
                'bg_surface': '#FFFFFF',
                'bg_card': '#EFECE4',
                'text_primary': '#1C1917',
                'text_secondary': '#57534E',
                'accent_primary': '#283618',
                'accent_hover': '#3A4F23',
                'border_color': 'rgba(40, 54, 24, 0.15)'
            }
            ident = "Osteria Culinary Atelier"
        elif any(k in p_lower for k in ["solaris", "warm stone", "monolith", "travertine"]):
            colors = {
                'bg_primary': '#F5F2EB',
                'bg_surface': '#ECE7DE',
                'bg_card': '#E2DBD0',
                'text_primary': '#1C1917',
                'text_secondary': '#6B665E',
                'accent_primary': '#A45A2A',
                'accent_hover': '#85441E',
                'border_color': 'rgba(28, 25, 23, 0.12)'
            }
            ident = "Solaris Architectural Studio"
        elif any(k in p_lower for k in ["agency", "portfolio", "creative", "studio"]):
            colors = {
                'bg_primary': '#0A0A0C',
                'bg_surface': '#121216',
                'bg_card': '#18181E',
                'text_primary': '#FFFFFF',
                'text_secondary': '#A1A1AA',
                'accent_primary': '#1E40AF',
                'accent_hover': '#3B82F6',
                'border_color': 'rgba(255, 255, 255, 0.12)'
            }
            ident = "Nexus Creative Agency"
        else:
            colors = {
                'bg_primary': '#07090e',
                'bg_surface': '#0d121f',
                'bg_card': '#141c2e',
                'text_primary': '#f8fafc',
                'text_secondary': '#94a3b8',
                'accent_primary': '#38bdf8',
                'accent_hover': '#0284c7',
                'border_color': 'rgba(56, 189, 248, 0.2)'
            }
            ident = "Modern Minimal"

        spec = CreativeDirectionSpec(
            design_concept=f'{ident} Direction',
            visual_identity=ident,
            color_tokens=colors,
            motion_philosophy='CSS transition 0.3s ease-in-out',
            requires_3d=False,
            domain_adaptation_notes='Bespoke fallback direction',
            anti_patterns=self.BANNED_ANTI_PATTERNS,
            react_bits_spec={},
            icon_spec={
                'lucide_icons': ['Zap', 'ShieldCheck', 'ArrowRight'],
                'branding_badge': 'NX',
                'anti_patterns': self.BANNED_ANTI_PATTERNS
            }
        )
        return spec.model_dump()
