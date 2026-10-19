"""
Prompt and Reference Parser for Hermes Software Engineering Agent.
Explicitly separates:
1. Target Project Brief (what the user wants built: domain, industry, features, interactions).
2. Design References (visual examples for composition, art direction, palette, typography, motion).
3. Explicit Replication Requests (user explicitly asking to clone/reproduce the reference subject).

Ensures that design references NEVER hijack the target project's functional domain or subject.
"""

import re
from typing import Dict, List, Any, Optional, Tuple

class PromptReferenceParser:
    """Parses user prompts to separate the target project specification from design references."""

    # Keywords indicating the user explicitly wants to replicate / clone the reference website
    REPLICATION_PATTERNS = [
        r'\b(?:recreate|reproduce|clone|copy|duplicate)\s+(?:this|the|exact)\b',
        r'\b(?:build|make)\s+(?:the\s+same|an\s+exact\s+copy|a\s+clone)\b',
        r'\b(?:replicate|exact\s+replica)\b',
        r'\brecreate\s+this\s+website\b'
    ]

    # Reference indicator phrases where the user is citing visual benchmarks / references
    REFERENCE_PATTERNS = [
        r'(?:use|using|refer\s+to|look\s+at|benchmarks?|inspired\s+by|visual\s+reference|reference\s+screenshot|attached\s+reference)[^.\n]*',
        r'https?://(?:in\.)?pinterest\.com/pin/\S+',
        r'https?://(?:www\.)?dribbble\.com/\S+',
        r'https?://(?:www\.)?behance\.net/\S+',
        r'https?://(?:www\.)?awwwards\.com/\S+',
        r'\[https?://[^\]]+\]\([^)]+\)',
        r'\[https?://[^\]]+\]',
        r'file:///\S+\.(?:png|jpg|jpeg|webp)',
        r'/\S+\.(?:png|jpg|jpeg|webp)'
    ]

    # Domain vocabulary for intent classification
    DOMAIN_VOCABULARY = {
        "RESTAURANT_FOOD": [
            "restaurant", "food", "dining", "bistro", "cafe", "kitchen", "crave",
            "dish", "dishes", "menu", "order food", "food ordering", "delivery",
            "culinary", "gourmet", "chef", "pizza", "burger", "pasta", "bakery",
            "sushi", "meal", "cook", "eats", "osteria", "tasting", "takeaway"
        ],
        "EDITORIAL_FASHION": [
            "fashion", "velour", "couture", "apparel", "runway", "lookbook",
            "luxury fashion", "clothing", "dress", "wardrobe", "collection", "outfit"
        ],
        "SCULPTURAL_FURNITURE": [
            "furniture", "chair", "armchair", "sofa", "seating", "table", "homeware",
            "interior decor", "formora", "simply furniture"
        ],
        "ORGANIC_SANCTUARY": [
            "real estate", "villa", "property", "sanctuary", "orizon", "penthouse",
            "oasis", "residence", "habitation", "cantilever", "realty"
        ],
        "LUXURY_ATELIER": [
            "mariana", "brand studio", "branding studio", "atelier", "luxury brand",
            "personal brand", "brand designer", "creative direction studio"
        ],
        "EDITORIAL_ARCHITECTURAL": [
            "solaris", "warm stone", "monolith", "travertine", "limestone",
            "architectural studio", "spatial architecture"
        ],
        "FOOTWEAR_SNEAKERS": [
            "sneaker", "sneakers", "shoe", "shoes", "footwear", "kicks", "boots"
        ],
        "STREAMING_DATA_DEVTOOL": [
            "distributed", "pipeline", "streaming engine", "event stream", "telemetry",
            "kafka", "flink", "vortex", "devtool", "message queue"
        ],
        "STREAMING_ENTERTAINMENT": [
            "movie", "movies", "cinema", "series", "streaming", "video", "film"
        ],
        "DASHBOARD": [
            "dashboard", "analytics", "metrics", "kpi", "admin portal", "crm"
        ],
        "CREATIVE_AGENCY": [
            "agency", "creative agency", "nexus creative", "design studio", "portfolio"
        ]
    }

    @classmethod
    def parse(cls, user_message: str, attached_images: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Parses user prompt into:
        - is_replication_request: bool
        - target_project_brief: str (clean user requirements without reference contamination)
        - design_reference_instructions: str (visual instructions for styling only)
        - reference_images: List[str] (all detected URLs and file paths)
        - target_domain: str (clean domain classification)
        - functional_requirements: List[str] (verifiable acceptance criteria)
        """
        text = user_message.strip()
        attached_images = attached_images or []

        # 1. Detect explicit replication request
        is_replication = any(re.search(pat, text, re.IGNORECASE) for pat in cls.REPLICATION_PATTERNS)

        # 2. Extract reference URLs and image paths
        found_urls = re.findall(r'https?://[^\s)\]]+', text)
        image_paths = list(attached_images)
        for url in found_urls:
            if any(k in url.lower() for k in ["pinterest", "dribbble", "behance", "awwwards", ".png", ".jpg", ".jpeg", ".webp"]):
                if url not in image_paths:
                    image_paths.append(url)

        local_img_matches = re.findall(r'(?:file:///|[/\w.-]+/)[^\s)\]]+\.(?:png|jpg|jpeg|webp)', text, re.IGNORECASE)
        for p in local_img_matches:
            clean_p = p.replace("file://", "")
            if clean_p not in image_paths:
                image_paths.append(clean_p)

        # 3. Separate target project brief from reference instructions
        # If user explicitly asks to replicate, the target brief is the reference
        if is_replication and not any(k in text.lower() for k in ["restaurant", "food", "shoe", "fashion", "devtool"]):
            target_brief = text
            ref_instructions = "Replicate visual layout, composition, and domain from supplied reference."
        else:
            # Split out reference clauses to prevent domain cross-contamination
            cleaned_target_brief = text
            ref_instruction_snippets = []

            # Patterns that introduce references
            ref_intro_patterns = [
                r'(?:Use\s+all\s+the\s+attached\s+website\s+references|Study\s+the\s+references|Refer\s+to\s+this|Using\s+this\s+reference|Based\s+on\s+this\s+reference|Inspired\s+by\s+this|Take\s+inspiration\s+from)[^.\n]*\.?',
                r'https?://[^\s)\]]+',
                r'\[https?://[^\]]+\]\([^)]+\)',
                r'\[https?://[^\]]+\]'
            ]

            for pat in ref_intro_patterns:
                matches = re.findall(pat, cleaned_target_brief, re.IGNORECASE)
                for m in matches:
                    ref_instruction_snippets.append(m)
                    cleaned_target_brief = cleaned_target_brief.replace(m, " ")

            cleaned_target_brief = re.sub(r'\s+', ' ', cleaned_target_brief).strip()

            # If the brief was emptied by stripping (user ONLY provided reference links),
            # infer target brief from explicit keywords or mark as reference replication
            if len(cleaned_target_brief) < 15 and image_paths:
                target_brief = text
                ref_instructions = "Apply visual benchmarks directly to the specified project."
            else:
                target_brief = cleaned_target_brief if cleaned_target_brief else text
                ref_instructions = " ".join(ref_instruction_snippets) if ref_instruction_snippets else "Apply high-contrast editorial hierarchy, authentic photography, and balanced typography."

        # 4. Classify Target Domain STRICTLY using target_brief (never reference text!)
        target_domain = cls._classify_domain(target_brief, is_replication=is_replication, fallback_text=text)

        # 5. Extract Functional Requirements Checklist for the Target Domain
        functional_reqs = cls._extract_functional_requirements(target_brief, target_domain)

        return {
            "is_replication_request": is_replication,
            "target_project_brief": target_brief,
            "design_reference_instructions": ref_instructions,
            "reference_images": image_paths,
            "target_domain": target_domain,
            "functional_requirements": functional_reqs
        }

    @classmethod
    def _classify_domain(cls, brief_text: str, is_replication: bool = False, fallback_text: str = "") -> str:
        """Classifies the domain using target brief text to prevent reference contamination."""
        b_lower = brief_text.lower()

        # Score matches in target brief
        scores = {}
        for domain, keywords in cls.DOMAIN_VOCABULARY.items():
            score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', b_lower))
            if score > 0:
                scores[domain] = score

        if scores:
            # Return domain with highest keyword density in the target brief
            sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return sorted_domains[0][0]

        # If target brief had no domain keywords but user requested replication, test full text
        if is_replication and fallback_text:
            fb_lower = fallback_text.lower()
            for domain, keywords in cls.DOMAIN_VOCABULARY.items():
                if any(re.search(r'\b' + re.escape(kw) + r'\b', fb_lower) for kw in keywords):
                    return domain

        # Default fallback if unspecified
        return "CREATIVE_AGENCY"

    @classmethod
    def _extract_functional_requirements(cls, brief_text: str, domain: str) -> List[Dict[str, Any]]:
        """Generates concrete, testable functional acceptance criteria based on domain and brief."""
        b_lower = brief_text.lower()
        reqs = []

        if domain == "RESTAURANT_FOOD":
            reqs = [
                {"id": "hero_story", "name": "Brand Storytelling & Dining Hero", "description": "Hero section with culinary philosophy, signature dish showcase, and order/reserve CTAs"},
                {"id": "menu_grid", "name": "Interactive Food Menu", "description": "Curated dishes with high-res food photography, pricing, course labels, and provenance details"},
                {"id": "category_filter", "name": "Menu Category Tabs", "description": "Filtering by tasting course, primi, secondi, pizza, dolci, and signature dishes"},
                {"id": "live_search", "name": "Live Dish Search", "description": "Search input filtering menu items in real time by dish name or ingredients"},
                {"id": "item_details_modal", "name": "Dish Customization Modal", "description": "Interactive modal with portion size, dietary notes, and gourmet add-ons"},
                {"id": "cart_drawer", "name": "Shopping Food Bag Drawer", "description": "Slide-over drawer showing selected items, item quantities, subtotal, delivery fee, and tax"},
                {"id": "quantity_controls", "name": "Cart Quantity Modification", "description": "Working plus, minus, and remove buttons updating cart total in real time"},
                {"id": "checkout_flow", "name": "Checkout Flow Modal", "description": "Complete ordering modal with customer details, tip selector, delivery estimate, and live order confirmation"},
                {"id": "reservation_widget", "name": "Table Reservation Booking", "description": "Interactive booking widget with date, time, and guest count selector"}
            ]
        elif domain == "EDITORIAL_FASHION":
            reqs = [
                {"id": "lookbook_hero", "name": "Editorial Lookbook Hero", "description": "Full-bleed or asymmetric hero with seasonal campaign imagery"},
                {"id": "collection_catalog", "name": "Curated Garment Catalog", "description": "High-fashion product cards with fabric composition and pricing"},
                {"id": "size_variant_selector", "name": "Size & Variant Selector", "description": "Interactive clothing size picker (XS, S, M, L, XL)"},
                {"id": "bag_drawer", "name": "Shopping Bag Drawer", "description": "Cart slide-over with total calculation and checkout CTA"}
            ]
        elif domain == "SCULPTURAL_FURNITURE":
            reqs = [
                {"id": "sculptural_hero", "name": "Monumental Hero Chair Showcase", "description": "Large-scale sculptural furniture piece with architectural typography"},
                {"id": "collection_grid", "name": "Curated Pieces Catalog", "description": "Detailed cards with price, series, finish, and specifications"},
                {"id": "tactile_materials", "name": "Tactile Material Swatches", "description": "Swatches showing textile/timber origin and tactile descriptions"},
                {"id": "piece_acquisition", "name": "Piece Acquisition Drawer", "description": "Order inquiry and reserve flow for limited edition pieces"}
            ]
        elif domain == "ORGANIC_SANCTUARY":
            reqs = [
                {"id": "floating_canvas", "name": "Organic Pill Canvas & Scenic Backdrop", "description": "Floating pill container over alpine/desert mist landscape"},
                {"id": "dock_navigation", "name": "Vertical Dock Rail", "description": "Docked vertical sidebar navigation with tooltips and quick actions"},
                {"id": "property_specs", "name": "Spatial Telemetry & Specifications", "description": "Square footage, bedrooms, bathrooms, and private land specifications"},
                {"id": "tour_booking", "name": "Sanctuary Tour Acquisition", "description": "Private walkthrough scheduling and architectural inquiry modal"}
            ]
        elif domain == "LUXURY_ATELIER":
            reqs = [
                {"id": "condensed_hero", "name": "Dramatic Condensed Typography Hero", "description": "High-contrast serif headline with editorial portraiture"},
                {"id": "case_studies", "name": "Selected Atelier Works", "description": "4-column case studies with client metrics, category, and deliverables"},
                {"id": "methodology", "name": "5-Step Strategic Methodology", "description": "Sequential process cards detailing discovery to delivery"},
                {"id": "commission_cta", "name": "Initiate Commission Flow", "description": "Project scoping inquiry and studio contact details"}
            ]
        else:
            reqs = [
                {"id": "signature_hero", "name": "Signature Identity Hero", "description": "Hero section with clear value proposition and visual storytelling"},
                {"id": "interactive_catalog", "name": "Domain Content Grid", "description": "Structured grid of products, projects, or features with interactive details"},
                {"id": "interactive_modal", "name": "Interactive Detail / Action Modal", "description": "Modal dialog providing deep inspection or booking/checkout action"}
            ]

        # Check for explicit feature mentions in user brief
        if any(k in b_lower for k in ["cart", "bag", "basket", "ordering", "buy"]):
            if not any(r["id"] == "cart_drawer" for r in reqs):
                reqs.append({"id": "cart_drawer", "name": "Interactive Shopping Cart", "description": "Slide-over drawer managing items, quantities, and totals"})

        if any(k in b_lower for k in ["checkout", "payment", "place order"]):
            if not any(r["id"] == "checkout_flow" for r in reqs):
                reqs.append({"id": "checkout_flow", "name": "Checkout Flow Modal", "description": "Modal with order summary, shipping/delivery, and payment"})

        if any(k in b_lower for k in ["search", "filter", "find"]):
            if not any(r["id"] == "live_search" for r in reqs):
                reqs.append({"id": "live_search", "name": "Live Search & Filter", "description": "Real-time query filtering across items"})

        return reqs
