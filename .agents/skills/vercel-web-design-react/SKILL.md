---
name: vercel-web-design-react
description: "Vercel Web Interface Guidelines and React Best Practices. Enforces production-grade UI design standards, Geist monochromatic sleekness, hairline borders, tabular numbers, accessible focus states, and zero-waterfall React performance patterns."
license: MIT
metadata:
  source: "https://github.com/vercel-labs/agent-skills"
  author: "Vercel"
  version: "1.0.0"
---

# Vercel Web Design & React Guidelines

This skill synthesizes Vercel's official **Web Interface Guidelines** and **React Best Practices** to engineer high-performance, polished web interfaces with the refined Geist design aesthetic.

## Part 1: Vercel Web Interface Guidelines

### 1. Monochromatic Sophistication & Hairline Borders
- **Geist Dark Aesthetic**: Deep neutral backgrounds (`#000000`, `#0a0a0a`, `#121212`) paired with crisp hairline borders (`border border-white/10` or `border-zinc-800`).
- **Surface Elevation**: Layered subtle elevation using dark surface steps (`#18181b`, `#27272a`) rather than harsh artificial shadows.
- **Accents**: Use deliberate, restrained high-contrast accents (e.g. Electric Cyan, Emerald, or Crisp White) against monochromatic foundations.

### 2. Typography & Numerical Precision
- **Tabular Numbers**: Always use `font-variant-numeric: tabular-nums` or `tabular-nums` class on statistics, latency readouts, financial figures, timers, and telemetry metrics to prevent jitter during updates.
- **Heading Balance**: Apply `text-wrap: balance` or `text-pretty` on all multi-line headings to eliminate awkward single-word orphans/widows.
- **Micro-Copy Typography**: Use curly quotes (`“` `”`) instead of straight quotes (`"`), non-breaking spaces before units (`142&nbsp;tps`, `12&nbsp;ms`), and true ellipses (`…`).

### 3. Accessible Focus States & Form Hygiene
- **Visible Focus Rings**: Every interactive element must provide a visible `:focus-visible` ring with clear contrast and offset (`focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:outline-none focus-visible:ring-offset-2 focus-visible:ring-offset-black`).
- **Never suppress focus**: Never use `outline-none` or `outline: none` without providing an immediate high-contrast focus replacement.
- **Form Controls**:
  - Always pair inputs with `<label>` or explicit `aria-label`.
  - Icon-only buttons MUST include an `aria-label` describing the action.
  - Decorative icons MUST specify `aria-hidden="true"`.
  - Disable spellcheck on code inputs, usernames, or telemetry fields (`spellCheck={false}`).
  - Maintain inline error messages near the triggering field.

### 4. Animation & Reduced Motion Compliance
- **Motion Restraint**: Animate only `transform` and `opacity` properties (compositor-friendly). Never use `transition: all`.
- **Reduced Motion**: Strictly provide a reduced or disabled motion alternative when `prefers-reduced-motion` is active (`motion-reduce:transition-none` / `motion-reduce:animate-none`).

---

## Part 2: Vercel React Best Practices

### 1. Eliminating Data Waterfalls (CRITICAL)
- Execute independent data fetches and computational passes in parallel using `Promise.all()`.
- Colocate state with the components that consume it; do not lift state unnecessarily high in the component tree.

### 2. Component Decomposition & Minimal Bundle Size
- **Clean Component Boundaries**: Separate presentational UI components from stateful orchestration containers.
- **Zero Heavy Bloat**: Avoid massive monolithic animation or UI frameworks when lightweight CSS transitions, Tailwind utilities, or targeted hooks achieve the same outcome.
- **Direct Imports**: Avoid broad barrel re-exports that inflate bundle sizes.

### 3. Rendering & Re-render Optimization
- **Derived State**: Derive state during render instead of syncing redundant state variables in `useEffect`.
- **Stable Callbacks**: Use functional state updaters (`setVal(prev => prev + 1)`) to keep callback dependencies minimal.
- **No Inline Component Definitions**: Never define a React component inside another React component's render body.
