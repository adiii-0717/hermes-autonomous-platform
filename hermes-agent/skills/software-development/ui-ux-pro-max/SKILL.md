---
name: ui-ux-pro-max
description: "UI/UX design intelligence framework featuring 10 curated design archetypes, product-specific color systems, font pairings, 8pt spatial grid standards, and strict WCAG AA/AAA accessibility gates."
license: MIT
metadata:
  source: "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"
  author: "Next Level Builder"
  version: "2.0.0"
---

# UI/UX Pro Max — Design Intelligence Framework

UI/UX Pro Max provides structured design intelligence to eliminate amateurish or generic UI generation. It enforces product-specific archetype matching, 8pt spatial grid rhythm, rigorous accessibility contrast ratios, and touch-target hygiene.

## 1. Curated Design Archetypes

Every product must be classified into a distinct visual archetype matching its functional purpose:

| Archetype | Best For | Visual Signatures | Key CSS Tokens |
| :--- | :--- | :--- | :--- |
| **Glassmorphism / Frosted Glass** | Modern SaaS, Crypto, Creative Portfolios | Translucent layers (`backdrop-blur-md`), subtle borders (`border-white/10`), multi-layered depth | `bg-white/5 border border-white/10 backdrop-blur-xl` |
| **Bento Grid Architecture** | Feature showcases, Analytics, Apple-like landing pages | Modular asymmetrical cells (`col-span-12 md:col-span-8`), high information density, subtle borders | `grid grid-cols-12 gap-4 rounded-2xl` |
| **Minimalist Luxury / Editorial** | High-end retail, Architecture, Fine dining, Art | Generous whitespace, refined serif/sans pairing, quiet monochromatic tones with warm accents | `bg-[#0a0a0c] text-stone-100 font-serif` |
| **Dark Cyberpunk / Terminal** | DevOps, AI Infrastructure, Security, Compilers | Deep obsidian (`#07090e`), electric cyan/emerald accents, monospace telemetry readouts, hairline grids | `bg-[#07090e] text-cyan-400 font-mono ring-1 ring-cyan-500/20` |
| **Swiss / International Style** | Data dashboards, Financial reports, Governance | Strict grid alignment, asymmetric white space, high legibility sans-serif, bold hierarchical weight | `font-sans tracking-tight border-b border-black/10` |
| **Brutalism / Neo-Brutalist** | Youth culture, Streetwear, Indie tools, Web3 | High-contrast borders (`border-2 border-black`), hard box-shadows (`shadow-[4px_4px_0px_0px_#000]`), raw typography | `border-2 border-white shadow-[4px_4px_0_0_#38bdf8]` |
| **Soft UI / Clean Precision** | Healthcare, Enterprise Cloud, Productivity | Muted slate surfaces (`#0f172a`), crisp radius (8-16px), soft elevation, high-clarity typography | `bg-slate-900/60 border border-slate-800` |

## 2. Product-Specific Color Systems & Reasoning

Never pick arbitrary hex colors. Select deliberate, harmonic color systems based on domain psychology:

- **AI Infrastructure & Cloud**: Deep Obsidian (`#07090e`), Slate (`#0f172a`), Electric Cyan (`#06b6d4`), Ice Blue (`#38bdf8`), Neutral Text (`#f8fafc`).
- **FinTech & Wealth**: Midnight Navy (`#030712`), Steel (`#1e293b`), Emerald Mint (`#10b981`), Platinum (`#f1f5f9`).
- **E-Commerce & High-Energy**: Carbon Black (`#09090b`), Pure White (`#ffffff`), Vibrant Crimson / Volt Orange (`#f97316` / `#ef4444`).
- **Culinary & Artisanal**: Warm Dark Charcoal (`#121110`), Rich Amber / Gold (`#d97706`), Cream Text (`#fafaf9`).

## 3. The 8pt Spatial Spacing System

All padding, margins, gaps, and component heights must adhere strictly to the 8pt spatial grid:
- **Micro Spacing**: 4px (`p-1`), 8px (`p-2`), 12px (`p-3`) for badges, icons, and button paddings.
- **Component Spacing**: 16px (`p-4`), 24px (`p-6`), 32px (`p-8`) for card bodies, form fields, and modal containers.
- **Section Spacing**: 48px (`py-12`), 64px (`py-16`), 96px (`py-24`), 128px (`py-32`) for hero containers and major section breaks.

## 4. Accessibility Quality Gates (WCAG AA/AAA)

1. **Color Contrast**: Body text must maintain at least **4.5:1** contrast against backgrounds (7:1 for AAA). Small captions must maintain at least **3:1**.
2. **Touch Targets**: All interactive elements (buttons, nav links, tabs, close icons) must have a minimum touch target area of **44 × 44px**.
3. **State Completeness**: Every interactive element must define all 5 states:
   - **Default (Rest)**
   - **Hover** (`hover:border-cyan-400 hover:bg-white/5`)
   - **Active (Pressed)** (`active:scale-98`)
   - **Focus-Visible** (`focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:outline-none`)
   - **Disabled** (`disabled:opacity-40 disabled:cursor-not-allowed`)
4. **Zero Layout Shifts (CLS < 0.1)**: Always declare explicit aspect ratios or height reservations on images, charts, and asynchronous containers.
