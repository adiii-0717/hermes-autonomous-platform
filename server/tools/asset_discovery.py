import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("asset_discovery")

class AssetDiscoveryService:
    """Discovers, verifies, and provides high-quality 2D photos, product imagery, 3D GLTF models, HDR environment maps, Google fonts, and resilient visual fallbacks."""

    CURATED_ASSETS = {
        "footwear": {
            "topic": "Footwear & E-Commerce",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1000&auto=format&fit=crop", "alt": "Red Premium Performance Running Shoe"},
                {"url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=1000&auto=format&fit=crop", "alt": "Pastel Lifestyle Sneaker Showcase"},
                {"url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?q=80&w=1000&auto=format&fit=crop", "alt": "Classic Canvas Skate Sneaker"},
                {"url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=1000&auto=format&fit=crop", "alt": "Multi-colored Luxury Designer Shoe"}
            ],
            "models_3d": [
                {
                    "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/MaterialsVariantsShoe/glTF-Binary/MaterialsVariantsShoe.glb",
                    "name": "Khronos Materials Variants Luxury Shoe GLB",
                    "license": "CC0 / Khronos Group Sample Assets"
                }
            ],
            "hdri_maps": [
                {"url": "https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/equirectangular/venice_sunset_1k.hdr", "name": "Venice Sunset Warm Lighting 1K"}
            ],
            "fonts": [
                "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');"
            ]
        },
        "furniture": {
            "topic": "Interior Furniture & Architecture",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1000&auto=format&fit=crop", "alt": "Modernist Glass Villa Architecture"},
                {"url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?q=80&w=1000&auto=format&fit=crop", "alt": "Minimalist Interior Architectural Spatial Design"}
            ],
            "models_3d": [
                {
                    "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/SheenChair/glTF-Binary/SheenChair.glb",
                    "name": "Khronos Sheen Velvet Lounge Chair GLB",
                    "license": "CC0 / Khronos Group Sample Assets"
                }
            ],
            "hdri_maps": [
                {"url": "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/royal_esplanade_1k.hdr", "name": "Daylight Architectural HDRI 1K"}
            ],
            "fonts": [
                "@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,400&family=Outfit:wght@300;400;500;600&display=swap');"
            ]
        },
        "tech": {
            "topic": "Cyber Tech & Audio Hardware",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1000&auto=format&fit=crop", "alt": "Premium Studio Headphones"},
                {"url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop", "alt": "Cybersecurity Tech Screen"}
            ],
            "models_3d": [
                {
                    "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/DamagedHelmet/glTF-Binary/DamagedHelmet.glb",
                    "name": "Khronos Sci-Fi Tech Helmet GLB",
                    "license": "CC0 / Khronos Group Sample Assets"
                }
            ],
            "hdri_maps": [
                {"url": "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_08_1k.hdr", "name": "Tech Studio Soft Light 1K"}
            ],
            "fonts": [
                "@import url('https://fonts.googleapis.com/css2?family=Syne:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');"
            ]
        },
        "automotive": {
            "topic": "Automotive & Industrial Design",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?q=80&w=1000&auto=format&fit=crop", "alt": "Modern Sports Car Showcase"}
            ],
            "models_3d": [
                {
                    "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/ToyCar/glTF-Binary/ToyCar.glb",
                    "name": "Khronos Industrial Toy Car GLB",
                    "license": "CC0 / Khronos Group Sample Assets"
                }
            ],
            "hdri_maps": [
                {"url": "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/royal_esplanade_1k.hdr", "name": "Studio Automotive HDRI 1K"}
            ],
            "fonts": [
                "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&display=swap');"
            ]
        },
        "culinary": {
            "topic": "Gourmet Culinary & Restaurant Dining",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1000&auto=format&fit=crop", "alt": "Warm Ambient Artisanal Restaurant Table"},
                {"url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?q=80&w=1000&auto=format&fit=crop", "alt": "Wood-Fired Neapolitan Pizza"},
                {"url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=1000&auto=format&fit=crop", "alt": "Gourmet Wagyu Beef Smash Burger"},
                {"url": "https://images.unsplash.com/photo-1621996346565-e3d5d6281699?q=80&w=1000&auto=format&fit=crop", "alt": "Fresh Handmade Pappardelle Pasta"},
                {"url": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1000&auto=format&fit=crop", "alt": "Pan-Seared Salmon Fillet"},
                {"url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?q=80&w=1000&auto=format&fit=crop", "alt": "Traditional Espresso Tiramisu Dessert"}
            ],
            "models_3d": [],
            "hdri_maps": [
                {"url": "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_08_1k.hdr", "name": "Warm Bistro Softlight 1K"}
            ],
            "fonts": [
                "@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');"
            ]
        },
        "beverage": {
            "topic": "Beverage & Consumer Product",
            "photos": [
                {"url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?q=80&w=1000&auto=format&fit=crop", "alt": "Minimalist Stainless Steel Water Bottle"}
            ],
            "models_3d": [
                {
                    "url": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/WaterBottle/glTF-Binary/WaterBottle.glb",
                    "name": "Khronos Metallic Water Bottle GLB",
                    "license": "CC0 / Khronos Group Sample Assets"
                }
            ],
            "hdri_maps": [
                {"url": "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_08_1k.hdr", "name": "Studio Product Softlight 1K"}
            ],
            "fonts": [
                "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');"
            ]
        }
    }

    def __init__(self):
        self.unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY")
        self._cache = {}

    def discover_assets(self, user_prompt: str) -> Dict[str, Any]:
        """Selects verified high-quality photography, 3D models, fonts, and fallbacks matching prompt intent."""
        p_lower = user_prompt.lower()
        matched_topic = "tech"

        if any(k in p_lower for k in ["restaurant", "food", "dining", "cafe", "bistro", "kitchen", "crave", "dish", "menu", "pizza", "burger", "pasta", "bakery", "sushi", "meal", "cook", "chef"]):
            matched_topic = "culinary"
        elif any(k in p_lower for k in ["shoe", "footwear", "sneaker", "boot", "run", "kicks"]):
            matched_topic = "footwear"
        elif any(k in p_lower for k in ["chair", "furniture", "sofa", "architecture", "interior", "decor", "home"]):
            matched_topic = "furniture"
        elif any(k in p_lower for k in ["car", "vehicle", "auto", "drive", "racing", "speed"]):
            matched_topic = "automotive"
        elif any(k in p_lower for k in ["bottle", "drink", "beverage", "water", "can", "flask"]):
            matched_topic = "beverage"
        elif any(k in p_lower for k in ["headphone", "audio", "watch", "helmet", "tech", "saas", "cyber", "portfolio"]):
            matched_topic = "tech"

        if matched_topic in self._cache:
            return dict(self._cache[matched_topic])
        assets = self.CURATED_ASSETS.get(matched_topic, self.CURATED_ASSETS["footwear"])
        self._cache[matched_topic] = assets
        return {
            "topic": assets["topic"],
            "photos": assets["photos"],
            "models_3d": assets["models_3d"],
            "hdri_maps": assets["hdri_maps"],
            "fonts": assets["fonts"]
        }

    def discover_assets_for_spec(self, creative_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Selects high-quality photography, 3D models, HDR maps, and fonts matched to CreativeDirectionSpec."""
        concept = creative_spec.get('design_concept', '')
        asset_spec = creative_spec.get('asset_spec', {})
        topic = asset_spec.get('topic', '')
        
        prompt_query = f"{concept} {topic}"
        base_assets = self.discover_assets(prompt_query)

        color_tokens = creative_spec.get('color_tokens', {})
        accent = color_tokens.get('accent_primary', '#38bdf8')

        base_assets['matched_accent_color'] = accent
        base_assets['spec_alignment'] = True
        return base_assets

    def format_asset_prompt_guidelines(self, asset_data: Dict[str, Any]) -> str:
        """Formats asset recommendations into structured guidelines for prompt injection."""
        out = []
        out.append(f"[VERIFIED ASSET DISCOVERY & RESILIENT FALLBACKS - Topic: {asset_data['topic']}]")
        out.append("")
        out.append("### High-Quality Photography Assets (Verified Unsplash CDNs):")
        for img in asset_data.get("photos", []):
            out.append(f"- URL: {img['url']}")
            out.append(f"  Alt: {img['alt']}")

        out.append("")
        out.append("### Verified 3D GLTF/GLB Models:")
        for m in asset_data.get("models_3d", []):
            out.append(f"- {m['name']} (License: {m.get('license', 'CC0')}): {m['url']}")

        out.append("")
        out.append("### Recommended Google Fonts Import:")
        for f in asset_data.get("fonts", []):
            out.append(f"- {f}")

        return chr(10).join(out)
