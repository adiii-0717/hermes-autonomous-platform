---
name: anthropic-frontend-design
description: "Guidance for distinctive, intentional visual design when building new web applications or reshaping existing ones. Enforces design director leadership, anti-slop checks against AI clichés, bespoke typography, intentional color systems, and purposeful motion."
license: MIT
metadata:
  source: "https://github.com/anthropics/skills/tree/main/skills/frontend-design"
  author: "Anthropic"
  version: "1.0.0"
---

# Anthropic Frontend Design

Approach every frontend task as the **design lead** at an elite design studio known for giving every client a distinct, authentic visual identity that cannot be mistaken for anyone else's. Reject generic or templated designs: make deliberate, opinionated choices about palette, typography, layout, and composition specific to the user's brief.

## 1. Ground Designs in the Subject Matter

- **Identity comes from the subject**: Extract the product's industry, materials, audience, and vernacular. A high-performance developer tool looks radically different from an artisanal bakery, a luxury fashion house, or a pediatric clinic.
- **Never design in a vacuum**: Use real, authentic domain content throughout. Never use generic placeholder lorem ipsum or ungrounded dummy data.
- **Hero section craftsmanship**: The hero must showcase the most characteristic artifact in the subject's world: an interactive live demo, a topological canvas, an architectural model matrix, or a kinetic typography statement. Avoid default formulaic treatments (e.g., a big generic number with a gradient accent).

## 2. The Anti-Slop Check (Banned Clichés)

AI-generated interfaces repeatedly cluster around predictable tells. **Actively audit against and ban these AI slop traits**:
1. **The Claude Cliché**: A warm cream background (`#F4F1EA`) with high-contrast serif display and terracotta/clay accent (`#D97757`).
2. **The Dark Mode Cliché**: Near-black background with unmotivated purple/violet gradients or neon acid-green accents.
3. **The Broadsheet Cliché**: Over-stylized newspaper column layout with hairline rules and zero border-radius regardless of domain.
4. **The SaaS-Card Kit**: Content chopped into identical rounded cards with identical border-radii, same soft gray shadow (`rgba(0,0,0,0.1)`), and decorative gradient washes.
5. **The Template Chrome**:
   - Tracked-out ALL-CAPS eyebrow labels above every single heading.
   - Meta strings joined with middle dots (`A · B · C`).
   - Labels constructed as `WORD — fragment` with spaced em dashes.
   - A monospace font used arbitrarily for ordinary non-code labels.
   - Appending `→` or `->` to every single button and link.
   - Highlighting a single random word in a headline with italic, bold, or accent color.

## 3. Typography & Composition

- **Typography carries personality**: Choose typefaces deliberately (e.g., Space Grotesk, Syne, Outfit, Plus Jakarta Sans, Cabinet Grotesk, Playfair Display) rather than default Inter/Roboto on every project.
- **Type scale**: Follow intentional weights, optical line heights (1.4–1.6), and keep line lengths under 80 characters for optimal readability.
- **Visual structure as information**: Use structural elements (borders, dividers, numbered markers) only when they encode real information (e.g., sequential processes or data boundaries), never as decorative fluff.

## 4. Purposeful Motion & Restraint

- **Spend boldness in one place**: Let one element be the memorable visual highlight (e.g., an interactive canvas, animated model topology, or kinetic reveal), and keep the surrounding interface quiet, disciplined, and functional.
- **Single orchestrated reveal**: A single well-choreographed page-load or reveal sequence lands with authority. Avoid scattered fade-and-slide-up triggers on every card.
- **Respect accessibility**: Honor `prefers-reduced-motion` unconditionally.

## 5. Intentional Copywriting

- **Active voice & clarity**: CTAs must state exactly what happens ("Deploy Pipeline", "Configure Node", "Save Changes", not "Submit" or "Click Here").
- **Sentence case**: Use sentence case for button labels and navigation; avoid shouty all-caps.
- **Action continuity**: Actions keep the same name throughout the user flow (e.g., button "Deploy" produces a toast "Deployed").
