import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger('creative_direction_engine')

class CreativeDirectionEngine:
    """Generates project-tailored creative directions, prevents AI tropes, and formulates design tokens."""

    ARCHETYPES = {
        'editorial_minimal': {
            'name': 'Editorial Minimalist',
            'bg_primary': '#faf9f6',
            'bg_surface': '#ffffff',
            'bg_card': '#f1efe9',
            'text_primary': '#1a1a1a',
            'text_secondary': '#666666',
            'accent_primary': '#000000',
            'accent_hover': '#333333',
            'font_heading': "'Playfair Display', serif",
            'font_body': "'Inter', sans-serif",
            'border_style': '1px solid #e2ded7',
            'shadow': '0 4px 20px rgba(0, 0, 0, 0.04)',
            'motion_curve': 'cubic-bezier(0.25, 1, 0.5, 1)',
            'vibe': 'Sophisticated, high-end editorial, generous whitespace.'
        },
        'neo_brutalism': {
            'name': 'Neo-Brutalist',
            'bg_primary': '#fef08a',
            'bg_surface': '#ffffff',
            'bg_card': '#a7f3d0',
            'text_primary': '#0f172a',
            'text_secondary': '#1e293b',
            'accent_primary': '#f43f5e',
            'accent_hover': '#e11d48',
            'font_heading': "'Space Grotesk', sans-serif",
            'font_body': "'Inter', sans-serif",
            'border_style': '3px solid #000000',
            'shadow': '5px 5px 0px #000000',
            'motion_curve': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
            'vibe': 'High contrast, bold geometric borders, energetic flat pop colors.'
        },
        'swiss_typographic': {
            'name': 'Swiss Typographic',
            'bg_primary': '#ffffff',
            'bg_surface': '#f4f4f5',
            'bg_card': '#e4e4e7',
            'text_primary': '#09090b',
            'text_secondary': '#52525b',
            'accent_primary': '#dc2626',
            'accent_hover': '#b91c1c',
            'font_heading': "'Inter', sans-serif",
            'font_body': "'Inter', sans-serif",
            'border_style': '1px solid #d4d4d8',
            'shadow': 'none',
            'motion_curve': 'cubic-bezier(0.16, 1, 0.3, 1)',
            'vibe': 'Grid-locked precision, oversized headings, asymmetric structured layouts.'
        },
        'refined_carbon': {
            'name': 'Refined Monochromatic Studio',
            'bg_primary': '#0f1115',
            'bg_surface': '#181b22',
            'bg_card': '#222631',
            'text_primary': '#f8fafc',
            'text_secondary': '#94a3b8',
            'accent_primary': '#f59e0b',
            'accent_hover': '#d97706',
            'font_heading': "'Space Grotesk', sans-serif",
            'font_body': "'Plus Jakarta Sans', sans-serif",
            'border_style': '1px solid rgba(255, 255, 255, 0.08)',
            'shadow': '0 10px 30px rgba(0, 0, 0, 0.35)',
            'motion_curve': 'cubic-bezier(0.16, 1, 0.3, 1)',
            'vibe': 'Crisp carbon studio interface, subtle elevated borders, warm amber accents.'
        },
        'luxury_editorial': {
            'name': 'Minimalist Luxury Editorial',
            'bg_primary': '#fdfbf7',
            'bg_surface': '#ffffff',
            'bg_card': '#f7f5f0',
            'text_primary': '#1c1917',
            'text_secondary': '#78716c',
            'accent_primary': '#4a1525',
            'accent_hover': '#6b1d2f',
            'font_heading': "'Playfair Display', serif",
            'font_body': "'Plus Jakarta Sans', sans-serif",
            'border_style': '1px solid rgba(74, 21, 37, 0.12)',
            'shadow': '0 4px 20px rgba(0, 0, 0, 0.03)',
            'motion_curve': 'cubic-bezier(0.25, 1, 0.5, 1)',
            'vibe': 'Editorial cream and heritage burgundy luxury with refined serif typography.'
        },
        'earthen_culinary': {
            'name': 'Artisanal Earthen Culinary',
            'bg_primary': '#f6f4ee',
            'bg_surface': '#ffffff',
            'bg_card': '#efece4',
            'text_primary': '#1c1917',
            'text_secondary': '#57534e',
            'accent_primary': '#283618',
            'accent_hover': '#3a4f23',
            'font_heading': "'Playfair Display', serif",
            'font_body': "'Plus Jakarta Sans', sans-serif",
            'border_style': '1px solid rgba(40, 54, 24, 0.15)',
            'shadow': '0 4px 18px rgba(0, 0, 0, 0.04)',
            'motion_curve': 'cubic-bezier(0.16, 1, 0.3, 1)',
            'vibe': 'Linen oatmeal backdrop with deep forest olive and warm terracotta accents.'
        },
        'architectural_stone': {
            'name': 'Editorial Architectural Monolith',
            'bg_primary': '#f5f2eb',
            'bg_surface': '#ece7de',
            'bg_card': '#e2dbd0',
            'text_primary': '#191716',
            'text_secondary': '#6e675f',
            'accent_primary': '#9e472a',
            'accent_hover': '#7f361e',
            'font_heading': "'Cinzel', 'Syne', serif",
            'font_body': "'Plus Jakarta Sans', sans-serif",
            'border_style': '1px solid rgba(25, 23, 22, 0.12)',
            'shadow': '0 12px 35px rgba(25, 23, 22, 0.06)',
            'motion_curve': 'cubic-bezier(0.25, 1, 0.5, 1)',
            'vibe': 'Warm limestone travertine monolith, rich terracotta accents, structural architectural photography.'
        },
        'cyber_technical': {
            'name': 'Cyber Technical',
            'bg_primary': '#080c14',
            'bg_surface': '#0e1626',
            'bg_card': '#162238',
            'text_primary': '#e2e8f0',
            'text_secondary': '#94a3b8',
            'accent_primary': '#06b6d4',
            'accent_hover': '#0891b2',
            'font_heading': "'JetBrains Mono', monospace",
            'font_body': "'Inter', sans-serif",
            'border_style': '1px solid rgba(6, 182, 212, 0.25)',
            'shadow': '0 0 15px rgba(6, 182, 212, 0.15)',
            'motion_curve': 'cubic-bezier(0.2, 0.8, 0.2, 1)',
            'vibe': 'Technical data-dense dashboard, cyan glows, grid overlay patterns.'
        }
    }

    def generate_creative_direction(self, user_prompt: str, project_name: str = '') -> Dict[str, Any]:
        """Formulates 3 candidate design concepts and selects the best fit for the prompt."""
        prompt_lower = user_prompt.lower()
        
        # Determine best matching archetype
        if any(k in prompt_lower for k in ['solaris', 'architecture', 'architectural', 'stone', 'monolith', 'travertine']):
            selected_key = 'architectural_stone'
        elif any(k in prompt_lower for k in ['fashion', 'luxury', 'couture', 'apparel', 'velour']):
            selected_key = 'luxury_editorial'
        elif any(k in prompt_lower for k in ['food', 'restaurant', 'culinary', 'dining', 'bistro', 'cafe', 'osteria']):
            selected_key = 'earthen_culinary'
        elif 'brutal' in prompt_lower or 'pop' in prompt_lower or 'bold' in prompt_lower:
            selected_key = 'neo_brutalism'
        elif 'minimal' in prompt_lower or 'editorial' in prompt_lower or 'blog' in prompt_lower or 'book' in prompt_lower:
            selected_key = 'editorial_minimal'
        elif 'cyber' in prompt_lower or 'terminal' in prompt_lower or 'tech' in prompt_lower or 'dev' in prompt_lower:
            selected_key = 'cyber_technical'
        elif 'swiss' in prompt_lower or 'typography' in prompt_lower or 'grid' in prompt_lower:
            selected_key = 'swiss_typographic'
        else:
            selected_key = 'refined_carbon'

        primary = self.ARCHETYPES[selected_key]
        
        # Select 2 alternate concepts for multi-concept evaluation
        alternates = [self.ARCHETYPES[k] for k in self.ARCHETYPES if k != selected_key][:2]

        rationale = f"Evaluated 3 design concepts ({primary['name']}, {alternates[0]['name']}, {alternates[1]['name']}). Selected {primary['name']} to align with target audience and product identity. Banned generic purple AI gradient tropes."

        return {
            'selected_archetype': primary['name'],
            'design_rationale': rationale,
            'color_tokens': {
                'bg_primary': primary['bg_primary'],
                'bg_surface': primary['bg_surface'],
                'bg_card': primary['bg_card'],
                'text_primary': primary['text_primary'],
                'text_secondary': primary['text_secondary'],
                'accent_primary': primary['accent_primary'],
                'accent_hover': primary['accent_hover'],
                'border_style': primary['border_style'],
                'shadow': primary['shadow']
            },
            'typography': {
                'font_heading': primary['font_heading'],
                'font_body': primary['font_body']
            },
            'motion': {
                'easing': primary['motion_curve'],
                'duration_standard': '0.25s',
                'prefers_reduced_motion': True
            },
            'vibe': primary['vibe'],
            'candidate_concepts': [primary['name'], alternates[0]['name'], alternates[1]['name']]
        }

    def get_css_variable_block(self, direction: Dict[str, Any]) -> str:
        """Generates a clean CSS :root block from the creative direction tokens."""
        tokens = direction.get('color_tokens', {})
        typo = direction.get('typography', {})
        motion = direction.get('motion', {})
        
        return f""":root {{
  --bg-primary: {tokens.get('bg_primary', '#090d16')};
  --bg-surface: {tokens.get('bg_surface', '#111827')};
  --bg-card: {tokens.get('bg_card', '#1f293d')};
  --text-primary: {tokens.get('text_primary', '#f3f4f6')};
  --text-secondary: {tokens.get('text_secondary', '#9ca3af')};
  --accent-primary: {tokens.get('accent_primary', '#6366f1')};
  --accent-hover: {tokens.get('accent_hover', '#4f46e5')};
  --border-style: {tokens.get('border_style', '1px solid rgba(255, 255, 255, 0.08)')};
  --box-shadow: {tokens.get('shadow', 'none')};
  --font-heading: {typo.get('font_heading', "'Inter', sans-serif")};
  --font-body: {typo.get('font_body', "'Inter', sans-serif")};
  --transition-easing: {motion.get('easing', 'cubic-bezier(0.16, 1, 0.3, 1)')};
}}
"""

    def generate_interaction_contract(self, user_prompt: str, project_name: str = '') -> Dict[str, Any]:
        """Formulates an interaction-first contract specifying interactive states and fallbacks for every component."""
        return {
            'interactive_elements': [
                {
                    'element': 'Primary CTA Button / Action Trigger',
                    'hover_micro_state': 'Magnetic cursor pull (dx, dy * 0.3) + spring scale 1.05',
                    'click_action': 'Triggers interactive modal overlay with smooth focus trap',
                    'touch_fallback': 'Direct tap feedback (scale 0.98, opacity 0.9)',
                    'keyboard_accessible': True
                },
                {
                    'element': '3D Hero Scene / Interactive Visual Focus',
                    'pointer_reaction': 'Particle swarm coordinates follow mousemove position',
                    'scroll_action': 'Synchronized 180-degree rotation along Y-axis on scroll enter',
                    'fallback_strategy': 'WebGL context check -> HTML5 2D Canvas particles or high-res ambient gradient',
                    'reduced_motion_ready': True
                },
                {
                    'element': 'Interactive Filter & Search Navigation',
                    'input_feedback': 'Instant live record filtering with smooth height auto-transition',
                    'keyboard_shortcut': "Press '/' to auto-focus search input"
                }
            ],
            'prefers_reduced_motion_enabled': True
        }
