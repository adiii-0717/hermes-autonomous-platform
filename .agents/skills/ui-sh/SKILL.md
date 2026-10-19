---
name: ui-sh
description: "Design-engineering principles and Refactoring UI laws by Adam Wathan & Steve Schoger (Tailwind CSS). Enforces visual hierarchy through weight/contrast, generous whitespace, hairline borders, asymmetric rhythm, and clean componentization."
license: MIT
metadata:
  source: "https://ui.sh"
  author: "Adam Wathan & Steve Schoger"
  version: "1.0.0"
---

# UI.sh — Design Engineering & Refactoring UI Principles

Created by the team behind Tailwind CSS and *Refactoring UI*, **UI.sh** bridges the gap between raw functionality and professional, human-crafted interface design. It provides design-engineering laws to eradicate the "generic AI look".

## 1. Hierarchy with Weight & Color Contrast (Not Just Font Size)

- **Avoid the "Make Everything Bigger" Trap**: When trying to make an element feel secondary, developers often shrink the font size until it becomes unreadable. Instead, keep the font size legible (14–15px) and de-emphasize using color contrast (`text-zinc-400` or `text-slate-500`) and font weight (`font-normal` vs `font-semibold`).
- **Two font sizes are often enough**: A single section can look sophisticated using only two well-paired font sizes if weight (`font-bold`, `font-medium`, `font-normal`) and color value are used intentionally.

## 2. Start with Too Much Whitespace and Pull Back

- **Generous Spatial Scales**: Cramped layouts make interfaces feel amateurish and claustrophobic. Start sections with generous padding (`py-20 md:py-28`), cards with ample breathing room (`p-6 md:p-8`), and clean line gaps (`gap-6 md:gap-8`).
- **Whitespace is a design element**: Do not fill every empty pixel with decorative borders, dividers, or badges. Allow negative space to frame high-priority elements.

## 3. Hairline Borders & Rings Over Muddy Box Shadows

- **Crisp Edge Definition**: Heavy, blurry drop shadows (`shadow-2xl` with default black opacity) muddy the UI and feel dated.
- **Tailwind Rings**: Use hairline inset rings (`ring-1 ring-inset ring-white/10` or `ring-white/5`) paired with a dark backdrop (`bg-zinc-900/60 backdrop-blur-md`). This creates razor-sharp edge contrast that looks sleek on high-DPI displays.

## 4. Tint Neutrals with the Background Hue

- **No Dead Grays**: In dark themes, pure desaturated grays look chalky and lifeless. If the background has a cool blue-slate undertone (`#07090e`), tint your borders and secondary text with cool slate (`text-slate-400`, `border-slate-800`). If the background is warm charcoal (`#121110`), tint neutrals with warm zinc/stone (`text-stone-400`, `border-stone-800`).

## 5. Break the Monotonous Card Grid

- **Asymmetric Layout Rhythm**: Resist placing 3 identical square cards side-by-side in every section.
- **Visual Variation**:
  - Use asymmetric columns (e.g., 7 columns for a featured architecture demo + 5 columns for telemetry metrics).
  - Use horizontal feature rows with alternating visual anchors.
  - Stagger cards or use full-width telemetry panels to create rhythmic contrast across the scroll experience.

## 6. Clean Componentization

- **Small, Composable Molecules**: Break monolithic files into clean, single-responsibility components (`BrandLogo`, `TelemetryCard`, `ArchitectureMatrix`, `PlaygroundDrawer`).
- **Explicit Prop Contracts**: Each component should accept clear props with defaults, avoiding hidden coupling or fragile global selectors.
- **Zero Lorem Ipsum**: All copy, labels, metrics, timestamps, and badges must reflect realistic domain data.
