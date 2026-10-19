---
name: advanced-3d-interface-design
description: Teaches Three.js, React Three Fiber, Drei, environment lighting, shader backgrounds, interactive 3D hero objects, and automatic 2D Canvas fallbacks.
---

# Advanced 3D Interface Design Guidelines

## 1. Selective 3D Placement
- Use 3D hero objects, particle grids, or spatial product showcases to reinforce identity.
- Never add unoptimized 3D scenes to basic utility pages.

## 2. Interactive Three.js / Canvas Starters
- Particle swarm canvas responding to pointer coordinates.
- Orbit controls or subtle camera spring movement on mousemove.

## 3. Graceful 2D Fallback Strategy
- Always detect WebGL support before rendering 3D context:
```js
function isWebGLAvailable() {
  try {
    const canvas = document.createElement("canvas");
    return !!(window.WebGLRenderingContext && (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")));
  } catch (e) { return false; }
}
```
- If WebGL is unavailable or user has low-power device, automatically render HTML5 2D Canvas particles or high-resolution ambient CSS backdrop.
