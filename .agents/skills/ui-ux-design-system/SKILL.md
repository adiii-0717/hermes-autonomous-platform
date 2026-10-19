---
name: ui-ux-design-system
description: Reusable UI/UX design framework for engineering project-specific visual identity, design system specifications, professional typography, color harmony, responsive layouts, and polished components.
---

# UI/UX Design System & Visual Craftsmanship Framework

When building web interfaces, applications, or user-facing components, you MUST establish a project-specific visual identity and design system before implementing frontend code.

Do NOT enforce a single default style (such as mandatory glassmorphism or generic gradients) across all projects. Instead, select a visual direction tailored to the product purpose, target audience, and use case.

---

## 1. Visual Identity Selection Matrix

Analyze the user's project requirements and select one of the following visual directions (or synthesize a custom direction appropriate for the product):

### A. Minimalist Enterprise / Professional SaaS
- **Target Products**: Admin dashboards, developer tools, B2B SaaS, productivity suites.
- **Palette**: Slate/zinc backdrops, crisp borders, subtle elevation shadows, focused primary accent (indigo, cobalt, or emerald).
- **Typography**: Clean sans-serif (e.g., Inter, Plus Jakarta Sans) paired with a precise monospace font (Fira Code, JetBrains Mono).
- **Aesthetic**: Sharp precision, 1px subtle borders, high contrast, clean data presentation.

### B. Modern Dark Developer Studio
- **Target Products**: AI dev tools, terminal interfaces, code editors, high-tech platforms.
- **Palette**: Obsidian or deep charcoal background (`#07090e`, `#0f172a`), subtle glowing neon status indicators, muted surface panels.
- **Typography**: Outfit or Space Grotesk headings, Fira Code / JetBrains Mono for data & code.
- **Aesthetic**: High contrast, subtle glow accents, rounded panel containers, crisp micro-badges.

### C. Consumer / Humanist Product
- **Target Products**: Personal finance trackers, health/wellness, education, lifestyle apps.
- **Palette**: Warm organic surfaces, soft pastel card backgrounds, vibrant primary accent (amber, violet, teal).
- **Typography**: Friendly rounded typography (Plus Jakarta Sans, Outfit, Rubik).
- **Aesthetic**: Soft card geometry, generous padding, friendly empty states, clear visual feedback.

### D. Editorial & Content-Rich Workspace
- **Target Products**: Knowledge bases, documentation portals, blogs, news feeds.
- **Palette**: High-contrast light slate or deep dark mode, minimal accent clutter, high contrast body text.
- **Typography**: Distinctive serif or geometric sans headings (Playfair Display, Syne, Instrument Serif) paired with readable body text (Source Sans 3, Inter).
- **Aesthetic**: Generous whitespace, elegant type scale, clear heading hierarchy.

---

## 2. Design System Specification Workflow

Before writing component markup, establish the project's CSS Design System variables in `index.css` or root styles:

```css
:root {
  /* 1. Color Palette (Semantic Tokens) */
  --bg-primary: #f8fafc;
  --bg-surface: #ffffff;
  --bg-card: #ffffff;
  --bg-input: #f1f5f9;
  --bg-hover: #e2e8f0;

  --border-color: #cbd5e1;
  --border-hover: #4f46e5;

  --accent-primary: #4f46e5;
  --accent-hover: #4338ca;
  --accent-surface: rgba(79, 70, 229, 0.08);

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;

  --status-success: #059669;
  --status-warning: #d97706;
  --status-danger: #dc2626;

  /* 2. Typography Tokens */
  --font-sans: "Plus Jakarta Sans", system-ui, -apple-system, sans-serif;
  --font-heading: "Outfit", sans-serif;
  --font-mono: "Fira Code", monospace;

  /* 3. Spacing & Radius Tokens */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --shadow-md: 0 10px 25px -5px rgba(15, 23, 42, 0.08);
}
```

---

## 3. Responsive Layout & Component Craftsmanship

1. **Responsive Breakpoints**:
   - Desktop: `1440px` baseline.
   - Tablet: `@media (max-width: 1024px)` -> Stack sidebars, adjust grid columns.
   - Mobile: `@media (max-width: 640px)` -> Full-width cards, touch-friendly tap targets (minimum 44px height).

2. **Interactive States**:
   - Every interactive element (button, link, input, tab) MUST feature explicit `:hover`, `:active`, `:focus-visible`, and `:disabled` styles.
   - Include subtle CSS transitions (`transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1)`).

3. **Accessibility & Contrast**:
   - Maintain minimum WCAG AA contrast ratio (>= 4.5:1) for all body text.
   - Ensure clear visual focus rings (`outline: 2px solid var(--accent-primary)`).

---

## 7. Advanced 3D (React Three Fiber) & Motion (GSAP / Lenis) Guidelines

When building immersive or interactive digital experiences:

1. **React Three Fiber (R3F) Infrastructure**:
   - Always wrap 3D Viewports (`<Canvas>`) inside a `Suspense` fallback and an `R3FErrorBoundary`.
   - Use `PerspectiveCamera` with tuned FOV (35-45deg) and responsive camera positioning (`cameraZ`).
   - Include realistic environment lighting (`<Environment preset="city" />` or HDRI) + directional key/fill lights.
   - Use `useFrame` for continuous smooth rotations or particle displacement.
   - Handle 3D asset load errors gracefully: fallback to a 2D high-res card or Canvas SVG if WebGL fails.

2. **GSAP & Motion Choreography**:
   - Use `gsap.context()` inside `useEffect` / `useGSAP` to guarantee clean unmounting and prevent memory leaks.
   - Respect user motion preferences: check `window.matchMedia('(prefers-reduced-motion: reduce)').matches`.
   - Build staggered entrances (`stagger: 0.15`) for hero headings, subtitle text, and grid cards.
   - For smooth scrolling experiences, integrate Lenis (`@studio-freight/lenis`) and sync its ticker with `ScrollTrigger.update`.
