import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger('autonomous_art_director')

class AutonomousArtDirector:
    """Autonomous Creative Art Direction Engine for Hermes Agent.
    Independently synthesizes unconventional design visual identities, semantic 3D relevance, and unified motion palettes.
    """

    UNCONVENTIONAL_ARCHETYPES = {
        'kinetic_brutalism': {
            'name': 'Kinetic Brutalism',
            'bg_primary': '#facc15',
            'bg_surface': '#ffffff',
            'bg_card': '#f43f5e',
            'text_primary': '#09090b',
            'text_secondary': '#18181b',
            'accent_primary': '#000000',
            'accent_hover': '#27272a',
            'border_style': '3px solid #000000',
            'shadow': '6px 6px 0px #000000',
            'font_heading': "'Syne', sans-serif",
            'font_body': "'Space Grotesk', sans-serif",
            'easing': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
            'vibe': 'High contrast, thick 3px black borders, energetic flat pop yellow/coral colors, hard drop-shadows.'
        },
        'swiss_monochrome': {
            'name': 'Swiss Grid Monochrome',
            'bg_primary': '#ffffff',
            'bg_surface': '#f4f4f5',
            'bg_card': '#e4e4e7',
            'text_primary': '#09090b',
            'text_secondary': '#52525b',
            'accent_primary': '#ef4444',
            'accent_hover': '#dc2626',
            'border_style': '1px solid #d4d4d8',
            'shadow': 'none',
            'font_heading': "'Inter', sans-serif",
            'font_body': "'Inter', sans-serif",
            'easing': 'cubic-bezier(0.16, 1, 0.3, 1)',
            'vibe': 'Strict grid precision, oversized Swiss Helvetica typography, asymmetric structured layouts, zero gradients.'
        },
        'neo_japanese_studio': {
            'name': 'Neo-Japanese Studio',
            'bg_primary': '#07090e',
            'bg_surface': '#0e121c',
            'bg_card': '#161c2b',
            'text_primary': '#f8fafc',
            'text_secondary': '#94a3b8',
            'accent_primary': '#06b6d4',
            'accent_hover': '#0891b2',
            'border_style': '1px solid rgba(6, 182, 212, 0.25)',
            'shadow': '0 0 20px rgba(6, 182, 212, 0.12)',
            'font_heading': "'Syne', sans-serif",
            'font_body': "'Plus Jakarta Sans', sans-serif",
            'font_mono': "'JetBrains Mono', monospace",
            'easing': 'cubic-bezier(0.16, 1, 0.3, 1)',
            'vibe': 'Dark Tokyo studio aesthetic, cyan glows, monospace data accents, magnetic button transforms.'
        },
        'editorial_spatial': {
            'name': 'Editorial Spatial Minimal',
            'bg_primary': '#fbf9f5',
            'bg_surface': '#ffffff',
            'bg_card': '#f2eee7',
            'text_primary': '#1c1917',
            'text_secondary': '#57534e',
            'accent_primary': '#292524',
            'accent_hover': '#44403c',
            'border_style': '1px solid #e7e5e4',
            'shadow': '0 4px 20px rgba(0, 0, 0, 0.03)',
            'font_heading': "'Playfair Display', serif",
            'font_body': "'Plus Jakarta Sans', sans-serif",
            'easing': 'cubic-bezier(0.25, 1, 0.5, 1)',
            'vibe': 'Luxurious editorial magazine layout, warm cream/stone palette, generous negative space, serif headlines.'
        }
    }

    def evaluate_3d_relevance(self, prompt: str) -> Dict[str, Any]:
        """Determines whether 3D WebGL scenes are semantically relevant or if 2D canvas/editorial typography is preferred."""
        p = prompt.lower()
        if any(k in p for k in ['3d', 'spatial', 'webgl', 'particle', 'audio', 'game', 'xr', 'metaverse', 'interactive canvas', 'studio']):
            return {
                'use_3d': True,
                'type': 'Interactive WebGL Canvas Particles with 2D Fallback',
                'reasoning': '3D WebGL particle environment directly reinforces spatial creative direction.'
            }
        return {
            'use_3d': False,
            'type': 'High-Contrast Editorial Grid & Motion Micro-Interactions',
            'reasoning': '3D WebGL is unnecessary for this product domain. Prioritizing crisp typography and motion.'
        }

    def synthesize_art_direction(self, user_prompt: str, project_name: str = '') -> Dict[str, Any]:
        """Synthesizes a complete autonomous art direction specification."""
        p = user_prompt.lower()
        
        if 'brutal' in p or 'pop' in p or 'yellow' in p or 'bold' in p:
            arch_key = 'kinetic_brutalism'
        elif 'swiss' in p or 'grid' in p or 'monochrome' in p:
            arch_key = 'swiss_monochrome'
        elif 'editorial' in p or 'luxur' in p or 'magazine' in p or 'serif' in p:
            arch_key = 'editorial_spatial'
        else:
            arch_key = 'neo_japanese_studio'

        archetype = self.UNCONVENTIONAL_ARCHETYPES[arch_key]
        three_d_decision = self.evaluate_3d_relevance(user_prompt)

        return {
            'archetype_key': arch_key,
            'archetype_name': archetype['name'],
            'design_vibe': archetype['vibe'],
            'color_tokens': {
                'bg_primary': archetype['bg_primary'],
                'bg_surface': archetype['bg_surface'],
                'bg_card': archetype['bg_card'],
                'text_primary': archetype['text_primary'],
                'text_secondary': archetype['text_secondary'],
                'accent_primary': archetype['accent_primary'],
                'accent_hover': archetype['accent_hover'],
                'border_style': archetype['border_style'],
                'shadow': archetype['shadow']
            },
            'typography': {
                'font_heading': archetype['font_heading'],
                'font_body': archetype['font_body']
            },
            'motion_palette': {
                'easing': archetype['easing'],
                'duration': '0.25s',
                'prefers_reduced_motion': True
            },
            'semantic_3d_decision': three_d_decision,
            'production_polish': {
                'adaptive_motion': {'device_pixel_ratio_cap': 1.5, 'target_fps': 60, 'framerate_scaling': True, 'reduced_motion': True},
                'form_validation': {'html5_validation': True, 'accessible_errors': True, 'aria_describedby': True, 'prevent_duplicate_submit': True},
                'image_fallbacks': {'resilient_svg_fallbacks': True, 'aspect_ratio_preservation': True, 'zero_layout_shift': True}
            }
        }
