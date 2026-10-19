---
name: advanced-motion-design
description: Teaches magnetic micro-interactions, spring physics, text character splitting, page transitions, and cursor followers with motion accessibility compliance.
---

# Advanced Motion Design Guidelines

## 1. Magnetic Hover Micro-Interactions
- Pull buttons toward pointer coordinates when hovering within `40px` radius.
```js
button.addEventListener("mousemove", (e) => {
  const rect = button.getBoundingClientRect();
  const x = e.clientX - rect.left - rect.width / 2;
  const y = e.clientY - rect.top - rect.height / 2;
  button.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
});
button.addEventListener("mouseleave", () => {
  button.style.transform = "translate(0px, 0px)";
});
```

## 2. Text Character Reveal Sweeps
- Split headings into individual characters/words and animate stagger on scroll.

## 3. Motion Accessibility Compliance (`prefers-reduced-motion`)
- Wrap all animations in reduced motion checks:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
