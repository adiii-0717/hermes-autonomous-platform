---
name: react-bits
description: React Bits (https://reactbits.dev/) design and engineering framework for discovering, selecting, installing, and implementing modern animated backgrounds, text effects, micro-interactions, spotlight cards, and professional Lucide icons in React web applications.
---

# React Bits (reactbits.dev) Design & Engineering Skill

When generating React web applications, you MUST discover, select, install, and implement purpose-matched components from **React Bits** (https://reactbits.dev/) combined with professional **Lucide React** icons and clean typographic branding.

Do NOT build generic or static templates. Every generated website must be visually distinctive, responsive, accessible, and tailored to the product's domain.

---

## 1. Component Discovery & Purpose Selection Matrix

Never blindly reuse the same design or animation style. Analyze the user's prompt and select React Bits components that match the product's identity:

| Product Domain | Background Effect | Typography & Hero Animation | Cards & Layout | Micro-Interactions | Lucide Icons |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **High-Tech SaaS / AI Platform** | `Hyperspeed` or `Squares` | `DecryptedText` or `TrueFocus` | `SpotlightCard` with border glow | `Magnet` button, `StarBorder` | `Cpu`, `Terminal`, `Zap`, `Shield`, `Activity`, `Sparkles` |
| **Creative Agency / Portfolio** | `Aurora` or `LiquidChrome` | `SplitText` or `BlurText` | `TiltedCard` with 3D parallax | `ClickSpark`, `FollowCursor` | `Layers`, `Palette`, `Eye`, `ArrowUpRight`, `Compass` |
| **E-Commerce / Storefront** | `Particles` or subtle `Aurora` | `ShinyText` badges & `SplitText` | `SpotlightCard` product cards | `Magnet` add-to-cart, `StarBorder` | `ShoppingBag`, `SlidersHorizontal`, `Star`, `Heart`, `Truck` |
| **FinTech / Analytics** | `Squares` or `DotGrid` | `CountUp` KPIs & `BlurText` | `SpotlightCard` metric panels | `Magnet` filter buttons | `TrendingUp`, `BarChart3`, `PieChart`, `Lock`, `CheckCircle2` |
| **Hospitality / Food / Lifestyle** | Warm `Aurora` or `Waves` | `BlurText` & `SplitText` | `TiltedCard` featured items | `Magnet` reservation button | `UtensilsCrossed`, `Clock`, `MapPin`, `Calendar`, `Award` |

---

## 2. Professional Iconography & Clean Branding Rules

### A. The Zero-Emoji Standard (STRICT)
- **NEVER** use emoji characters (e.g. 👟, 🛒, 🍔, ⭐, 🚀, 💡, 🔥, 📦) as UI icons, button graphics, or category symbols.
- Emojis render inconsistently across operating systems, break visual hierarchy, and make the application look like an amateur toy.

### B. Lucide React Icon Standard
- Always import clean, vector icons from `lucide-react`:
  ```jsx
  import { ShoppingBag, Search, SlidersHorizontal, ArrowRight, Star, Check, ShieldCheck, Zap } from 'lucide-react';
  ```
- Use consistent sizing: `w-4 h-4` for badges/buttons, `w-5 h-5` for navigation/cards, `w-6 h-6` for feature headers.
- Use uniform stroke width (`strokeWidth={1.5}` or `2`) and harmonize icon color with semantic design tokens (`text-accent-primary` or `text-text-secondary`).

### C. Clean Text-Based Branding Standard
When no official company logo is provided:
- Create a crisp typographic wordmark paired with a geometric monogram badge:
  ```jsx
  export function BrandLogo({ name = "NEXARCH", badge = "N" }) {
    return (
      <div className="flex items-center gap-2.5 group cursor-pointer">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-primary/20 to-accent-primary/5 border border-accent-primary/30 flex items-center justify-center font-mono font-bold text-accent-primary shadow-sm group-hover:border-accent-primary/60 transition-colors">
          {badge}
        </div>
        <span className="font-heading font-extrabold tracking-tight text-xl text-text-primary">
          {name}
        </span>
      </div>
    );
  }
  ```

---

## 3. Dependency & Project Architecture Setup

When generating a React project, install the following standard packages:

### `package.json`
```json
{
  "name": "project-name",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.469.0",
    "framer-motion": "^11.15.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^5.4.11",
    "tailwindcss": "^3.4.17",
    "postcss": "^8.4.49",
    "autoprefixer": "^10.4.20"
  }
}
```

### `vite.config.js`
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './'
});
```

### Component Structure
Place React Bits components inside `src/components/reactbits/`:
```
src/
├── components/
│   ├── reactbits/
│   │   ├── Aurora.jsx
│   │   ├── Hyperspeed.jsx
│   │   ├── Particles.jsx
│   │   ├── Squares.jsx
│   │   ├── SplitText.jsx
│   │   ├── BlurText.jsx
│   │   ├── ShinyText.jsx
│   │   ├── DecryptedText.jsx
│   │   ├── SpotlightCard.jsx
│   │   ├── TiltedCard.jsx
│   │   ├── Magnet.jsx
│   │   ├── StarBorder.jsx
│   │   └── CountUp.jsx
│   ├── Navbar.jsx
│   ├── Hero.jsx
│   └── ProductCatalog.jsx
├── App.jsx
├── main.jsx
└── index.css
```

---

## 4. Canonical React Bits Component Implementations

### 1. `SpotlightCard.jsx`
Dynamic radial mouse-tracking illumination across card border and backdrop:
```jsx
import React, { useRef, useState } from 'react';

export function SpotlightCard({ 
  children, 
  className = "", 
  spotlightColor = "rgba(56, 189, 248, 0.15)",
  borderColor = "rgba(56, 189, 248, 0.3)"
}) {
  const divRef = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = (e) => {
    if (!divRef.current) return;
    const rect = divRef.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden rounded-2xl border border-white/10 bg-surface/80 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px transition-opacity duration-300"
        style={{
          opacity,
          background: `radial-gradient(400px circle at ${position.x}px ${position.y}px, ${spotlightColor}, transparent 40%)`
        }}
      />
      <div
        className="pointer-events-none absolute -inset-px rounded-2xl transition-opacity duration-300"
        style={{
          opacity,
          border: `1px solid ${borderColor}`,
          maskImage: `radial-gradient(250px circle at ${position.x}px ${position.y}px, black, transparent)`
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
```

### 2. `SplitText.jsx`
Kinetic word/character spring stagger entrance:
```jsx
import React from 'react';
import { motion } from 'framer-motion';

export function SplitText({ 
  text = "", 
  className = "", 
  delay = 0.05, 
  stiffness = 200, 
  damping = 18 
}) {
  const words = text.split(" ");

  return (
    <span className={`inline-flex flex-wrap gap-x-2 ${className}`}>
      {words.map((word, wIdx) => (
        <span key={wIdx} className="inline-block overflow-hidden">
          <motion.span
            initial={{ y: "100%", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{
              type: "spring",
              stiffness,
              damping,
              delay: wIdx * delay
            }}
            className="inline-block"
          >
            {word}
          </motion.span>
        </span>
      ))}
    </span>
  );
}
```

### 3. `DecryptedText.jsx`
Matrix/Cyberpunk letter decryption effect on hover or view:
```jsx
import React, { useState, useEffect, useRef } from 'react';

const CHARS = "ABCDEF0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";

export function DecryptedText({ 
  text = "", 
  speed = 40, 
  maxIterations = 15,
  className = "",
  encryptedClassName = "text-accent-primary/60 font-mono"
}) {
  const [displayText, setDisplayText] = useState(text);
  const [isHovered, setIsHovered] = useState(false);
  const intervalRef = useRef(null);

  const scramble = () => {
    let iteration = 0;
    clearInterval(intervalRef.current);

    intervalRef.current = setInterval(() => {
      setDisplayText(
        text
          .split("")
          .map((char, index) => {
            if (char === " ") return " ";
            if (index < iteration) return text[index];
            return CHARS[Math.floor(Math.random() * CHARS.length)];
          })
          .join("")
      );

      if (iteration >= text.length) {
        clearInterval(intervalRef.current);
      }
      iteration += 1 / (maxIterations / text.length);
    }, speed);
  };

  useEffect(() => {
    scramble();
    return () => clearInterval(intervalRef.current);
  }, [text]);

  return (
    <span 
      className={`cursor-pointer select-none ${className}`}
      onMouseEnter={() => { setIsHovered(true); scramble(); }}
      onMouseLeave={() => setIsHovered(false)}
    >
      {displayText}
    </span>
  );
}
```

### 4. `ShinyText.jsx`
Subtle metallic shimmer gradient sweep:
```jsx
import React from 'react';

export function ShinyText({ text, className = "", shimmerWidth = 100 }) {
  return (
    <span
      className={`inline-block bg-gradient-to-r from-text-secondary via-text-primary to-text-secondary bg-[length:200%_auto] bg-clip-text text-transparent animate-shimmer ${className}`}
    >
      {text}
    </span>
  );
}
```

### 5. `Magnet.jsx`
Magnetic cursor pull button with spring physics:
```jsx
import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';

export function Magnet({ children, className = "", strength = 0.35 }) {
  const ref = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    if (!ref.current) return;
    const { clientX, clientY } = e;
    const { height, width, left, top } = ref.current.getBoundingClientRect();
    const middleX = clientX - (left + width / 2);
    const middleY = clientY - (top + height / 2);
    setPosition({ x: middleX * strength, y: middleY * strength });
  };

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 220, damping: 15, mass: 0.1 }}
      className={`inline-block ${className}`}
    >
      {children}
    </motion.div>
  );
}
```

### 6. `StarBorder.jsx`
Glowing animated star/gradient border around cards or buttons:
```jsx
import React from 'react';

export function StarBorder({ children, className = "", speed = "6s" }) {
  return (
    <div className={`relative p-[1px] overflow-hidden rounded-xl group ${className}`}>
      <div 
        className="absolute inset-[-100%] bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(56,189,248,0.8)_360deg)] animate-spin-slow"
        style={{ animationDuration: speed }}
      />
      <div className="relative z-10 rounded-xl bg-surface/90 backdrop-blur-md">
        {children}
      </div>
    </div>
  );
}
```

### 7. `Aurora.jsx`
Fluid organic canvas gradient background:
```jsx
import React, { useEffect, useRef } from 'react';

export function Aurora({ 
  colorStops = ["#0ea5e9", "#6366f1", "#10b981"], 
  speed = 0.8,
  className = "" 
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let time = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const render = () => {
      time += 0.005 * speed;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < colorStops.length; i++) {
        const radius = Math.min(canvas.width, canvas.height) * 0.7;
        const x = canvas.width * 0.5 + Math.sin(time + i * 1.5) * (canvas.width * 0.25);
        const y = canvas.height * 0.4 + Math.cos(time + i * 1.2) * (canvas.height * 0.2);

        const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
        gradient.addColorStop(0, colorStops[i] + '33');
        gradient.addColorStop(0.5, colorStops[i] + '11');
        gradient.addColorStop(1, 'transparent');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resize);
    };
  }, [colorStops, speed]);

  return (
    <canvas 
      ref={canvasRef} 
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} 
    />
  );
}
```

### 8. `Squares.jsx`
Interactive subtle grid squares that illuminate on hover/motion:
```jsx
import React, { useRef, useEffect } from 'react';

export function Squares({ 
  squareSize = 40,
  strokeColor = "rgba(255, 255, 255, 0.05)",
  hoverColor = "rgba(56, 189, 248, 0.2)",
  className = ""
}) {
  const canvasRef = useRef(null);
  const mouseRef = useRef({ x: -1000, y: -1000 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    };
    window.addEventListener('mousemove', handleMouseMove);

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const cols = Math.ceil(canvas.width / squareSize);
      const rows = Math.ceil(canvas.height / squareSize);

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = i * squareSize;
          const y = j * squareSize;
          const dist = Math.hypot(x + squareSize / 2 - mouseRef.current.x, y + squareSize / 2 - mouseRef.current.y);

          ctx.strokeStyle = strokeColor;
          ctx.strokeRect(x, y, squareSize, squareSize);

          if (dist < 120) {
            ctx.fillStyle = hoverColor;
            ctx.globalAlpha = Math.max(0, 1 - dist / 120);
            ctx.fillRect(x + 1, y + 1, squareSize - 2, squareSize - 2);
            ctx.globalAlpha = 1.0;
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [squareSize, strokeColor, hoverColor]);

  return (
    <canvas 
      ref={canvasRef} 
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} 
    />
  );
}
```

### 9. `CountUp.jsx`
Smooth animated number increment for metrics:
```jsx
import React, { useEffect, useState, useRef } from 'react';

export function CountUp({ to = 100, duration = 1.5, suffix = "", prefix = "" }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        let start = 0;
        const step = to / (duration * 60);
        const timer = setInterval(() => {
          start += step;
          if (start >= to) {
            setCount(to);
            clearInterval(timer);
          } else {
            setCount(Math.floor(start));
          }
        }, 1000 / 60);
      }
    });

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [to, duration]);

  return <span ref={ref}>{prefix}{count.toLocaleString()}{suffix}</span>;
}
```

---

## 5. Accessibility & Responsive Quality Standards

1. **Reduced Motion**:
   Always respect user accessibility preferences:
   ```css
   @media (prefers-reduced-motion: reduce) {
     *, ::before, ::after {
       animation-duration: 0.01ms !important;
       animation-iteration-count: 1 !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```
2. **Mobile Viewport (< 768px)**:
   - Downgrade particle/canvas compute density on mobile to preserve 60fps.
   - Stack grids to single-column layout (`grid-cols-1 md:grid-cols-3`).
   - Use drawer or modal navigation with touch-friendly tap targets ($\ge 44\text{px}$).
