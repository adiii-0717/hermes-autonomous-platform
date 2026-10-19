---
name: cinematic-scroll-experience
description: Guides implementation of pinned scroll sections, horizontal scroll triggers, parallax depth, and image/video scroll scrubbing using GSAP ScrollTrigger.
---

# Cinematic Scroll Experience Guidelines

When designing scroll-driven storytelling, follow these implementation rules:

## 1. GSAP ScrollTrigger Architecture
- Import GSAP & ScrollTrigger via script tag or npm (`import { gsap } from "gsap"; import { ScrollTrigger } from "gsap/ScrollTrigger";`).
- Always register plugin: `gsap.registerPlugin(ScrollTrigger);`.

## 2. Pinned Scene Sequences
- Pin container elements during scroll:
```js
gsap.to(".pinned-container", {
  scrollTrigger: {
    trigger: ".pinned-container",
    pin: true,
    start: "top top",
    end: "+=1000",
    scrub: 1
  }
});
```

## 3. Horizontal Scroll Sections
- Translate inner track along X-axis as vertical scroll progresses:
```js
gsap.to(".horizontal-track", {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-wrapper",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".horizontal-track").offsetWidth
  }
});
```

## 4. Parallax Depth & Motion Continuity
- Apply differential scroll speeds (`data-speed="0.5"`, `data-speed="1.2"`).
- Maintain visual continuity between adjacent sections using gradient masking and overlapping elements.
