import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from server.agents.schemas import AgentContext
from server.tools.component_discovery import ComponentDiscoveryCatalog
from server.agents.domain_fashion import generate_fashion_editorial_app_jsx, generate_fashion_editorial_index_html
from server.agents.domain_restaurant import generate_restaurant_culinary_app_jsx, generate_restaurant_culinary_index_html
from server.agents.domain_agency import generate_creative_agency_app_jsx, generate_creative_agency_index_html
from server.agents.domain_furniture import generate_sculptural_furniture_app_jsx, generate_sculptural_furniture_index_html
from server.agents.domain_real_estate import generate_sanctuary_real_estate_app_jsx, generate_sanctuary_real_estate_index_html
from server.agents.domain_luxury_atelier import generate_luxury_atelier_app_jsx, generate_luxury_atelier_index_html

logger = logging.getLogger("agent.ReactBitsGenerator")

class ReactBitsProjectGenerator:
    """Generates complete, production-grade Vite + React applications infused with React Bits components, Lucide React icons, and clean text branding."""

    def __init__(self):
        self.catalog = ComponentDiscoveryCatalog()

    def generate_project(
        self,
        context: AgentContext,
        spec: dict,
        brand_name: str,
        domain: str,
        prioritized_fixes: list
    ) -> Dict[str, Any]:
        ws_p = Path(context.workspace_root)
        proj_dir = ws_p if ws_p.name == context.project_name else (ws_p / context.project_name)
        proj_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"ReactBitsProjectGenerator: scaffolding React Bits project at {proj_dir} for '{brand_name}' ({domain})")

        # 1. Fetch purpose-matched React Bits recommendations
        rb_plan = self.catalog.get_purpose_matched_reactbits(context.user_prompt, domain)
        colors = spec.get('color_tokens', {})
        fonts = spec.get('typography_system', {})

        if not colors:
            domain_upper = domain.upper()
            if "FASHION" in domain_upper:
                colors = {
                    'bg_primary': '#FDFBF7',
                    'bg_surface': '#F4EFEA',
                    'bg_card': '#EAE3DC',
                    'accent_primary': '#4A1525',
                    'accent_hover': '#6B1D36',
                    'text_primary': '#1A1A1A',
                    'text_secondary': '#666666'
                }
            elif "RESTAURANT" in domain_upper or "CULINARY" in domain_upper or "FOOD" in domain_upper:
                colors = {
                    'bg_primary': '#F6F4EE',
                    'bg_surface': '#EFECE4',
                    'bg_card': '#E5E0D5',
                    'accent_primary': '#283618',
                    'accent_hover': '#BC6C25',
                    'text_primary': '#1C1917',
                    'text_secondary': '#57534E'
                }
            elif "AGENCY" in domain_upper or "ARCHITECT" in domain_upper:
                colors = {
                    'bg_primary': '#0A0A0C',
                    'bg_surface': '#121216',
                    'bg_card': '#18181E',
                    'accent_primary': '#1E40AF',
                    'accent_hover': '#FEF08A',
                    'text_primary': '#FFFFFF',
                    'text_secondary': '#9CA3AF'
                }
            elif "STREAMING" in domain_upper or "DEVTOOL" in domain_upper or "INFRA" in domain_upper:
                colors = {
                    'bg_primary': '#07090e',
                    'bg_surface': '#0e121a',
                    'bg_card': '#151b26',
                    'accent_primary': '#6366f1',
                    'accent_hover': '#818cf8',
                    'text_primary': '#f1f5f9',
                    'text_secondary': '#94a3b8'
                }

        bg_primary = colors.get('bg_primary', '#090d16')
        bg_surface = colors.get('bg_surface', '#111827')
        bg_card = colors.get('bg_card', '#1f293d')
        accent_primary = colors.get('accent_primary', '#38bdf8')
        accent_hover = colors.get('accent_hover', '#0284c7')
        text_primary = colors.get('text_primary', '#f8fafc')
        text_secondary = colors.get('text_secondary', '#94a3b8')

        badge_letter = brand_name[0] if brand_name else "N"

        # 2. Directory structure
        src_dir = proj_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        components_dir = src_dir / "components"
        components_dir.mkdir(parents=True, exist_ok=True)
        reactbits_dir = components_dir / "reactbits"
        reactbits_dir.mkdir(parents=True, exist_ok=True)

        files_written = []

        # 3. Write package.json
        pkg_json = {
            "name": context.project_name.lower().replace(" ", "-"),
            "private": True,
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
        (proj_dir / "package.json").write_text(json.dumps(pkg_json, indent=2), encoding="utf-8")
        files_written.append("package.json")

        # 4. Write vite.config.js
        vite_config = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './'
});
"""
        (proj_dir / "vite.config.js").write_text(vite_config, encoding="utf-8")
        files_written.append("vite.config.js")

        # 5. Write tailwind.config.js
        tailwind_config = f"""/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "./src/**/*.{'{js,ts,jsx,tsx}'}",
  ],
  darkMode: 'class',
  theme: {{
    extend: {{
      colors: {{
        'bg-primary': '{bg_primary}',
        'bg-surface': '{bg_surface}',
        'bg-card': '{bg_card}',
        'accent-primary': '{accent_primary}',
        'accent-hover': '{accent_hover}',
        'text-primary': '{text_primary}',
        'text-secondary': '{text_secondary}',
      }},
      fontFamily: {{
        sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
        heading: ['Outfit', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace'],
      }},
      animation: {{
        'spin-slow': 'spin 8s linear infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
        'marquee': 'marquee 25s linear infinite',
      }},
      keyframes: {{
        shimmer: {{
          '0%': {{ backgroundPosition: '200% 0' }},
          '100%': {{ backgroundPosition: '-200% 0' }}
        }},
        marquee: {{
          '0%': {{ transform: 'translateX(0%)' }},
          '100%': {{ transform: 'translateX(-50%)' }}
        }}
      }}
    }},
  }},
  plugins: [],
}}
"""
        (proj_dir / "tailwind.config.js").write_text(tailwind_config, encoding="utf-8")
        files_written.append("tailwind.config.js")

        # 6. Write postcss.config.js
        postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
        (proj_dir / "postcss.config.js").write_text(postcss_config, encoding="utf-8")
        files_written.append("postcss.config.js")

        # 7. Write src/index.css
        index_css = f"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --bg-primary: {bg_primary};
  --bg-surface: {bg_surface};
  --bg-card: {bg_card};
  --accent-primary: {accent_primary};
  --accent-hover: {accent_hover};
  --text-primary: {text_primary};
  --text-secondary: {text_secondary};
}}

body {{
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  overflow-x: hidden;
  margin: 0;
}}

@media (prefers-reduced-motion: reduce) {{
  *, ::before, ::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}
"""
        (src_dir / "index.css").write_text(index_css, encoding="utf-8")
        files_written.append("src/index.css")

        # 8. Write React Bits Components
        rb_files = {
            "Squares.jsx": self._get_squares_component(),
            "Aurora.jsx": self._get_aurora_component(),
            "Particles.jsx": self._get_particles_component(),
            "Hyperspeed.jsx": self._get_hyperspeed_component(),
            "DecryptedText.jsx": self._get_decrypted_text_component(),
            "SplitText.jsx": self._get_split_text_component(),
            "BlurText.jsx": self._get_blur_text_component(),
            "ShinyText.jsx": self._get_shiny_text_component(),
            "SpotlightCard.jsx": self._get_spotlight_card_component(),
            "TiltedCard.jsx": self._get_tilted_card_component(),
            "Magnet.jsx": self._get_magnet_component(),
            "StarBorder.jsx": self._get_star_border_component(),
            "CountUp.jsx": self._get_count_up_component(),
            "InfiniteScroll.jsx": self._get_infinite_scroll_component()
        }

        for fname, code in rb_files.items():
            (reactbits_dir / fname).write_text(code, encoding="utf-8")
            files_written.append(f"src/components/reactbits/{fname}")

        # 9. Write BrandLogo.jsx
        default_sub = (
            "ATELIER COUTURE" if "fashion" in domain.lower() 
            else ("ARTISANAL DINING" if "restaurant" in domain.lower() 
            else ("CREATIVE STUDIO" if "agency" in domain.lower() 
            else "SYSTEMS LAB"))
        )
        brand_logo_code = f"""import React from 'react';

export function BrandLogo({{ name = "{brand_name}", badge = "{badge_letter}", subtitle = "{default_sub}" }}) {{
  return (
    <div className="flex items-center gap-3 group cursor-pointer select-none">
      <div 
        className="w-10 h-10 rounded-xl flex items-center justify-center font-bold shadow-md transition-all duration-300 group-hover:scale-105"
        style={{{{
          backgroundColor: '{accent_primary}18',
          borderColor: '{accent_primary}40',
          borderWidth: '1px',
          color: '{accent_primary}'
        }}}}
      >
        <span className="text-base tracking-wider">{{badge}}</span>
      </div>
      <div className="flex flex-col">
        <span 
          className="font-heading font-extrabold tracking-tight text-xl transition-colors"
          style={{{{ color: '{text_primary}' }}}}
        >
          {{name}}
        </span>
        {{subtitle && (
          <span 
            className="text-[10px] tracking-widest uppercase font-mono"
            style={{{{ color: '{text_secondary}' }}}}
          >
            {{subtitle}}
          </span>
        )}}
      </div>
    </div>
  );
}}
"""
        (components_dir / "BrandLogo.jsx").write_text(brand_logo_code, encoding="utf-8")
        files_written.append("src/components/BrandLogo.jsx")

        # 10. Write main.jsx
        main_jsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        (src_dir / "main.jsx").write_text(main_jsx, encoding="utf-8")
        files_written.append("src/main.jsx")

        # 11. Write App.jsx tailored to domain
        app_jsx_content = self._generate_domain_app_jsx(brand_name, domain, badge_letter, colors)
        (src_dir / "App.jsx").write_text(app_jsx_content, encoding="utf-8")
        files_written.append("src/App.jsx")

        # 12. Write dual-mode index.html (Vite root + immediate inline React 18 browser execution)
        index_html_content = self._generate_dual_mode_index_html(brand_name, domain, badge_letter, colors)
        (proj_dir / "index.html").write_text(index_html_content, encoding="utf-8")
        files_written.append("index.html")

        # 13. Write SRS.md and README.md
        (proj_dir / "README.md").write_text(f"""# {brand_name} — React Bits Application

Generated by NEXARCH Multi-Agent Architecture with **React Bits** design skill integration.

## Features
- **React Bits Animated Background**: Interactive canvas background tailored to product domain.
- **React Bits Typography**: Kinetic text reveal and shimmer badges.
- **React Bits Spotlight Cards**: Dynamic radial glow tracking cursor across cards and borders.
- **Lucide React Vector Icons**: 100% clean vector icons (zero emojis).
- **Clean Typographic Branding**: Geometric monogram badge with responsive navigation.
- **Interactive State**: Real-time filtering, parameter tuning modal, and responsive mobile drawer.

## Quick Start
```bash
npm install
npm run dev
```
""", encoding="utf-8")
        files_written.append("README.md")

        return {
            "files_written": files_written,
            "project_dir": str(proj_dir),
            "concept": f"{brand_name} — React Bits {domain}",
            "react_bits_integrated": True,
            "components_installed": list(rb_files.keys())
        }

    def _get_squares_component(self) -> str:
        return """import React, { useRef, useEffect } from 'react';

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

          if (dist < 130) {
            ctx.fillStyle = hoverColor;
            ctx.globalAlpha = Math.max(0, 1 - dist / 130);
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

  return <canvas ref={canvasRef} className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} />;
}
"""

    def _get_aurora_component(self) -> str:
        return """import React, { useEffect, useRef } from 'react';

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

  return <canvas ref={canvasRef} className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} />;
}
"""

    def _get_particles_component(self) -> str:
        return """import React, { useRef, useEffect } from 'react';

export function Particles({ count = 60, color = "#38bdf8", className = "" }) {
  const canvasRef = useRef(null);

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

    const particles = Array.from({ length: count }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.6,
      vy: (Math.random() - 0.5) * 0.6,
      radius: Math.random() * 2 + 1,
      alpha: Math.random() * 0.5 + 0.2
    }));

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.fillStyle = color;
        ctx.globalAlpha = p.alpha;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resize);
    };
  }, [count, color]);

  return <canvas ref={canvasRef} className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} />;
}
"""

    def _get_hyperspeed_component(self) -> str:
        return """import React, { useRef, useEffect } from 'react';

export function Hyperspeed({ streakColor = "#00f0ff", count = 50, className = "" }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const streaks = Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * canvas.width * 2,
      y: (Math.random() - 0.5) * canvas.height * 2,
      z: Math.random() * 1000 + 200,
      length: Math.random() * 20 + 10
    }));

    const render = () => {
      ctx.fillStyle = 'rgba(5, 5, 8, 0.25)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const cx = canvas.width / 2;
      const cy = canvas.height / 2;

      streaks.forEach((s) => {
        s.z -= 12;
        if (s.z <= 10) {
          s.z = 1000;
          s.x = (Math.random() - 0.5) * canvas.width * 2;
          s.y = (Math.random() - 0.5) * canvas.height * 2;
        }

        const k = 300 / s.z;
        const px = s.x * k + cx;
        const py = s.y * k + cy;

        const k2 = 300 / (s.z + s.length);
        const px2 = s.x * k2 + cx;
        const py2 = s.y * k2 + cy;

        ctx.strokeStyle = streakColor;
        ctx.lineWidth = Math.max(0.5, (1 - s.z / 1000) * 2.5);
        ctx.globalAlpha = Math.max(0.1, 1 - s.z / 1000);
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(px2, py2);
        ctx.stroke();
      });

      animationId = requestAnimationFrame(render);
    };

    render();
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
    };
  }, [streakColor, count]);

  return <canvas ref={canvasRef} className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} />;
}
"""

    def _get_decrypted_text_component(self) -> str:
        return """import React, { useState, useEffect, useRef } from 'react';

const GLYPHS = "ABCDEF0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";

export function DecryptedText({ text = "", speed = 40, maxIterations = 14, className = "" }) {
  const [displayText, setDisplayText] = useState(text);
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
            return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
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
    <span className={`cursor-pointer select-none font-mono ${className}`} onMouseEnter={scramble}>
      {displayText}
    </span>
  );
}
"""

    def _get_split_text_component(self) -> str:
        return """import React from 'react';
import { motion } from 'framer-motion';

export function SplitText({ text = "", className = "", delay = 0.04, stiffness = 240, damping = 20 }) {
  const words = text.split(" ");
  // Normalize delay: if passed in milliseconds (>1), convert to seconds; cap total stagger to 0.4s max
  const stepDelay = delay > 1 ? delay / 1000 : delay;
  return (
    <span className={`inline-flex flex-wrap gap-x-3 gap-y-1 ${className}`}>
      {words.map((word, i) => (
        <span key={i} className="inline-block overflow-hidden py-0.5">
          <motion.span
            initial={{ y: "100%", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ 
              type: "spring", 
              stiffness, 
              damping, 
              delay: Math.min(i * stepDelay, 0.4) 
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
"""

    def _get_blur_text_component(self) -> str:
        return """import React from 'react';
import { motion } from 'framer-motion';

export function BlurText({ text = "", className = "", delay = 0.05 }) {
  const words = text.split(" ");
  return (
    <span className={`inline-flex flex-wrap gap-x-2 ${className}`}>
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, filter: "blur(10px)", y: 15 }}
          animate={{ opacity: 1, filter: "blur(0px)", y: 0 }}
          transition={{ duration: 0.6, delay: i * delay, ease: [0.16, 1, 0.3, 1] }}
          className="inline-block"
        >
          {word}
        </motion.span>
      ))}
    </span>
  );
}
"""

    def _get_shiny_text_component(self) -> str:
        return """import React from 'react';

export function ShinyText({ text, className = "" }) {
  return (
    <span className={`inline-block bg-gradient-to-r from-slate-400 via-white to-slate-400 bg-[length:200%_auto] bg-clip-text text-transparent animate-shimmer ${className}`}>
      {text}
    </span>
  );
}
"""

    def _get_spotlight_card_component(self) -> str:
        return """import React, { useRef, useState } from 'react';

export function SpotlightCard({ 
  children, 
  className = "", 
  spotlightColor = "rgba(56, 189, 248, 0.15)",
  borderColor = "rgba(56, 189, 248, 0.4)"
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
      className={`relative overflow-hidden rounded-2xl border border-white/10 bg-slate-900/80 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl ${className}`}
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
"""

    def _get_tilted_card_component(self) -> str:
        return """import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

export function TiltedCard({ children, className = "", maxTilt = 12 }) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseX = useSpring(x, { stiffness: 250, damping: 20 });
  const mouseY = useSpring(y, { stiffness: 250, damping: 20 });

  const rotateX = useTransform(mouseY, [-0.5, 0.5], [maxTilt, -maxTilt]);
  const rotateY = useTransform(mouseX, [-0.5, 0.5], [-maxTilt, maxTilt]);

  const handleMouseMove = (e) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseXPos = (e.clientX - rect.left) / width - 0.5;
    const mouseYPos = (e.clientY - rect.top) / height - 0.5;
    x.set(mouseXPos);
    y.set(mouseYPos);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      className={`relative perspective-1000 ${className}`}
    >
      <div style={{ transform: "translateZ(20px)" }}>{children}</div>
    </motion.div>
  );
}
"""

    def _get_magnet_component(self) -> str:
        return """import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';

export function Magnet({ children, className = "", strength = 0.35 }) {
  const ref = useRef(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });

  const handleMove = (e) => {
    if (!ref.current) return;
    const { clientX, clientY } = e;
    const { left, top, width, height } = ref.current.getBoundingClientRect();
    const x = (clientX - (left + width / 2)) * strength;
    const y = (clientY - (top + height / 2)) * strength;
    setPos({ x, y });
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={() => setPos({ x: 0, y: 0 })}
      animate={{ x: pos.x, y: pos.y }}
      transition={{ type: "spring", stiffness: 220, damping: 14, mass: 0.1 }}
      className={`inline-block ${className}`}
    >
      {children}
    </motion.div>
  );
}
"""

    def _get_star_border_component(self) -> str:
        return """import React from 'react';

export function StarBorder({ 
  as: Component = 'div',
  children, 
  className = "", 
  innerClassName = "",
  color = "#BC6C25", 
  speed = "5s",
  onClick,
  ...props 
}) {
  return (
    <Component 
      onClick={onClick}
      className={`relative inline-block p-[1.5px] overflow-hidden rounded-full group cursor-pointer ${className}`}
      {...props}
    >
      <div 
        className="absolute inset-[-100%] animate-spin-slow pointer-events-none"
        style={{ 
          animationDuration: speed,
          background: `conic-gradient(from 0deg, transparent 0 320deg, ${color} 360deg)`
        }}
      />
      <div className={`relative z-10 rounded-full px-5 py-2 transition-colors ${innerClassName || 'bg-white/80 dark:bg-slate-900/90 backdrop-blur-md'}`}>
        {children}
      </div>
    </Component>
  );
}
"""

    def _get_count_up_component(self) -> str:
        return """import React, { useEffect, useState, useRef } from 'react';

export function CountUp({ to = 100, duration = 1.6, prefix = "", suffix = "" }) {
  const [val, setVal] = useState(to);
  const ref = useRef(null);
  const triggered = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !triggered.current) {
        triggered.current = true;
        let start = 0;
        setVal(0);
        const totalFrames = Math.max(duration * 60, 1);
        const step = to / totalFrames;
        const interval = setInterval(() => {
          start += step;
          if (start >= to) {
            setVal(to);
            clearInterval(interval);
          } else {
            setVal(Math.floor(start));
          }
        }, 1000 / 60);
      }
    });

    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [to, duration]);

  return <span ref={ref}>{prefix}{val.toLocaleString()}{suffix}</span>;
}
"""

    def _get_infinite_scroll_component(self) -> str:
        return """import React from 'react';

export function InfiniteScroll({ items = [], speed = "25s", className = "" }) {
  return (
    <div className={`overflow-hidden whitespace-nowrap relative ${className}`}>
      <div className="inline-flex gap-8 animate-marquee hover:[animation-play-state:paused]" style={{ animationDuration: speed }}>
        {items.concat(items).map((item, idx) => (
          <div key={idx} className="flex-shrink-0 flex items-center gap-3 px-6 py-3 rounded-full bg-slate-900/60 border border-white/5">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}
"""

    def _generate_domain_app_jsx(self, brand_name: str, domain: str, badge_letter: str, colors: dict) -> str:
        d_upper = domain.upper()
        if d_upper in ["RESTAURANT_CULINARY", "RESTAURANT_FOOD"]:
            return generate_restaurant_culinary_app_jsx(brand_name, badge_letter, colors)
        elif d_upper in ["EDITORIAL_FASHION", "FASHION_APPAREL"]:
            return generate_fashion_editorial_app_jsx(brand_name, badge_letter, colors)
        elif d_upper in ["SCULPTURAL_FURNITURE"]:
            return generate_sculptural_furniture_app_jsx(brand_name, badge_letter, colors)
        elif d_upper in ["ORGANIC_SANCTUARY", "REAL_ESTATE"]:
            return generate_sanctuary_real_estate_app_jsx(brand_name, badge_letter, colors)
        elif d_upper in ["LUXURY_ATELIER"]:
            return generate_luxury_atelier_app_jsx(brand_name, badge_letter, colors)
        elif d_upper in ["EDITORIAL_ARCHITECTURAL", "CREATIVE_AGENCY", "PORTFOLIO"]:
            return generate_creative_agency_app_jsx(brand_name, badge_letter, colors)
        elif d_upper in ["STREAMING_DATA_DEVTOOL"]:
            return self._generate_streaming_devtool_app_jsx(brand_name, badge_letter, colors)

        prompt_domain = f"{brand_name} {domain}".lower()
        if any(k in prompt_domain for k in ["restaurant", "food", "dining", "kitchen", "bistro", "cafe", "osteria", "culinary"]):
            return generate_restaurant_culinary_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["fashion", "velour", "couture", "apparel", "runway", "atelier"]):
            return generate_fashion_editorial_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["furniture", "chair", "sofa", "armchair", "interior", "formora", "simply", "seating"]):
            return generate_sculptural_furniture_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["real estate", "villa", "property", "sanctuary", "orizon", "oasis", "cantilever"]):
            return generate_sanctuary_real_estate_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["mariana", "brand studio", "branding studio", "rose gold", "crimson"]):
            return generate_luxury_atelier_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["solaris", "stone", "monolith", "travertine", "limestone", "architectural"]):
            return generate_creative_agency_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["agency", "portfolio", "creative", "studio", "nexus"]):
            return generate_creative_agency_app_jsx(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["vortex", "pipeline", "streaming", "event stream", "telemetry", "distributed"]):
            return self._generate_streaming_devtool_app_jsx(brand_name, badge_letter, colors)
        return self._generate_ai_studio_app_jsx(brand_name, badge_letter, colors)

    def _generate_ai_studio_app_jsx(self, brand_name: str, badge_letter: str, colors: dict) -> str:
        template = '''import React, { useState } from 'react';
import { 
  Cpu, Terminal, Zap, ShieldCheck, Activity, Sparkles, 
  ArrowRight, Layers, Code2, SlidersHorizontal, Check, X,
  ExternalLink, ChevronRight, BarChart2, Database
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { Squares } from './components/reactbits/Squares';
import { DecryptedText } from './components/reactbits/DecryptedText';
import { ShinyText } from './components/reactbits/ShinyText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { StarBorder } from './components/reactbits/StarBorder';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [playgroundOpen, setPlaygroundOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('Aetheria-Omni 70B');
  const [temperature, setTemperature] = useState(0.7);
  const [contextWindow, setContextWindow] = useState('128k');
  const [activeTab, setActiveTab] = useState('models');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const models = [
    {
      id: 'omni-70b',
      name: 'Aetheria-Omni 70B',
      type: 'Multimodal Foundation',
      context: '128k Tokens',
      throughput: '142 tps',
      latency: '12ms',
      description: 'SOTA frontier reasoning engine trained on multi-token prediction with native vision-audio synthesis.'
    },
    {
      id: 'synapse-diff',
      name: 'Synapse-Diffusion v3',
      type: 'Latent Generative',
      context: '64k Tokens',
      throughput: '88 tps',
      latency: '18ms',
      description: 'Continuous latent flow matching model engineered for sub-second spatial and code generation.'
    },
    {
      id: 'nexus-quant',
      name: 'Nexus-Quant 1.58b',
      type: 'Ternary Edge Runtime',
      context: '32k Tokens',
      throughput: '410 tps',
      latency: '3ms',
      description: 'Ultra-low footprint 1.58-bit quantized kernel designed for real-time edge robotics and embedded devices.'
    }
  ];

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black relative overflow-x-hidden">
      {/* React Bits Animated Background */}
      <Squares 
        squareSize={48} 
        strokeColor="rgba(255, 255, 255, 0.04)" 
        hoverColor="rgba(14, 165, 233, 0.22)" 
      />

      {/* Navigation Header */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#07090e]/80 border-b border-white/5 py-4 px-6 md:px-12">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" />

          {/* Desktop Nav Items */}
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <button 
              onClick={() => setActiveTab('models')}
              className={`hover:text-cyan-400 transition-colors ${activeTab === 'models' ? 'text-cyan-400 font-semibold' : ''}`}
            >
              Architectures
            </button>
            <button 
              onClick={() => setActiveTab('benchmarks')}
              className={`hover:text-cyan-400 transition-colors ${activeTab === 'benchmarks' ? 'text-cyan-400 font-semibold' : ''}`}
            >
              Benchmarks
            </button>
            <button 
              onClick={() => setActiveTab('specs')}
              className={`hover:text-cyan-400 transition-colors ${activeTab === 'specs' ? 'text-cyan-400 font-semibold' : ''}`}
            >
              Runtime Specs
            </button>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <ShinyText text="RUNTIME v4.2 LIVE" />
            </div>

            <Magnet>
              <button 
                onClick={() => setPlaygroundOpen(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black font-semibold text-sm hover:bg-cyan-300 transition-all shadow-lg shadow-white/10"
              >
                <Terminal className="w-4 h-4" />
                Playground
              </button>
            </Magnet>
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg bg-slate-900 border border-white/10 text-slate-300"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <SlidersHorizontal className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-white/10 pt-4 flex flex-col gap-3">
            <button onClick={() => { setActiveTab('models'); setMobileMenuOpen(false); }} className="text-left py-2 text-slate-300">Architectures</button>
            <button onClick={() => { setActiveTab('benchmarks'); setMobileMenuOpen(false); }} className="text-left py-2 text-slate-300">Benchmarks</button>
            <button onClick={() => { setPlaygroundOpen(true); setMobileMenuOpen(false); }} className="flex items-center gap-2 py-2 text-cyan-400 font-semibold">
              <Terminal className="w-4 h-4" /> Launch Playground
            </button>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <header className="relative z-10 pt-20 pb-16 px-6 md:px-12 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300">
          <Sparkles className="w-3.5 h-3.5" />
          <span>NEURAL ARCHITECTURE SYNTHESIS</span>
        </div>

        {/* React Bits DecryptedText Hero Typography */}
        <h1 className="text-4xl md:text-7xl font-extrabold tracking-tight mb-6 max-w-5xl mx-auto leading-tight text-white">
          <DecryptedText text="INTELLIGENCE ARCHITECTED AT SCALE" speed={35} maxIterations={16} />
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
          __BRAND_NAME__ pioneers self-evolving foundation architectures with sub-millisecond inference, dynamic mixture-of-agents routing, and verified zero-loss quantization.
        </p>

        {/* Hero CTA Row */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <StarBorder speed="4s">
            <button 
              onClick={() => setPlaygroundOpen(true)}
              className="flex items-center gap-3 px-8 py-4 text-white font-semibold rounded-xl text-base group"
            >
              <Zap className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
              <span>Deploy Architecture</span>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </button>
          </StarBorder>

          <Magnet>
            <button 
              onClick={() => setActiveTab('benchmarks')}
              className="flex items-center gap-2 px-7 py-4 rounded-xl bg-slate-900/90 border border-white/10 hover:border-cyan-500/40 text-slate-200 font-medium text-base transition-colors"
            >
              <Code2 className="w-4 h-4 text-slate-400" />
              <span>Inspect Benchmarks</span>
            </button>
          </Magnet>
        </div>
      </header>

      {/* KPI Metrics Row */}
      <section className="relative z-10 py-8 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 rounded-2xl bg-slate-950/60 border border-white/5 backdrop-blur-xl">
          <div className="flex flex-col items-center md:items-start p-4">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
              <Zap className="w-4 h-4" />
              <span>INFERENCE SPEED</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              <CountUp to={142} duration={1.5} suffix=" tps" />
            </div>
            <span className="text-xs text-slate-500 mt-1">Per GPU streaming throughput</span>
          </div>

          <div className="flex flex-col items-center md:items-start p-4 border-l border-white/5">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span>SLA RELIABILITY</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              <CountUp to={99} duration={1.2} suffix=".98%" />
            </div>
            <span className="text-xs text-slate-500 mt-1">Multi-region active cluster</span>
          </div>

          <div className="flex flex-col items-center md:items-start p-4 border-l border-white/5">
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 mb-1">
              <Activity className="w-4 h-4" />
              <span>FIRST TOKEN TIME</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              <CountUp to={12} duration={1.0} suffix=" ms" />
            </div>
            <span className="text-xs text-slate-500 mt-1">Direct kernel optimization</span>
          </div>

          <div className="flex flex-col items-center md:items-start p-4 border-l border-white/5">
            <div className="flex items-center gap-2 text-xs font-mono text-purple-400 mb-1">
              <Cpu className="w-4 h-4" />
              <span>ACTIVE WEIGHTS</span>
            </div>
            <div className="text-3xl font-extrabold text-white">
              <CountUp to={70} duration={1.8} suffix=" B" />
            </div>
            <span className="text-xs text-slate-500 mt-1">FP8 native tensor cores</span>
          </div>
        </div>
      </section>

      {/* Model Architectures Showcase */}
      <section className="relative z-10 py-16 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-end justify-between mb-12">
          <div>
            <span className="text-xs font-mono text-cyan-400 tracking-widest uppercase">FOUNDATION PIPELINE</span>
            <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white mt-2">
              Frontier Model Matrix
            </h2>
          </div>
          <p className="text-slate-400 text-sm max-w-md mt-4 md:mt-0 font-light">
            Engineered with React Bits micro-interactions, vector Lucide icons, and clean text branding.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {models.map((m) => (
            <SpotlightCard 
              key={m.id}
              className="flex flex-col justify-between h-full bg-[#0d121f]/90 border-slate-800"
              spotlightColor="rgba(14, 165, 233, 0.18)"
              borderColor="rgba(14, 165, 233, 0.4)"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                    {m.type}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400">
                    <Activity className="w-3.5 h-3.5 text-cyan-400" />
                    {m.latency}
                  </div>
                </div>

                <h3 className="text-2xl font-bold text-white mb-2 tracking-tight group-hover:text-cyan-300 transition-colors">
                  {m.name}
                </h3>

                <p className="text-slate-400 text-sm leading-relaxed mb-6 font-light">
                  {m.description}
                </p>

                <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs font-mono text-slate-400 mb-6">
                  <div>
                    <span className="text-slate-500 block text-[10px]">CONTEXT</span>
                    <span className="text-white font-medium">{m.context}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">THROUGHPUT</span>
                    <span className="text-cyan-400 font-medium">{m.throughput}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                <button 
                  onClick={() => { setSelectedModel(m.name); setPlaygroundOpen(true); }}
                  className="flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Test in Playground</span>
                </button>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
            </SpotlightCard>
          ))}
        </div>
      </section>

      {/* Interactive Playground Drawer / Modal */}
      {playgroundOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-[#0b0f19] border border-cyan-500/30 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Terminal className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">Model Playground & Neural Inspector</h3>
                  <p className="text-xs text-slate-400">Target Architecture: {selectedModel}</p>
                </div>
              </div>
              <button 
                onClick={() => setPlaygroundOpen(false)}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <label className="text-xs font-mono text-slate-400 block mb-1">SELECT ACTIVE MODEL</label>
                <select 
                  value={selectedModel} 
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-cyan-500 outline-none"
                >
                  <option value="Aetheria-Omni 70B">Aetheria-Omni 70B (Frontier Reasoning)</option>
                  <option value="Synapse-Diffusion v3">Synapse-Diffusion v3 (Generative)</option>
                  <option value="Nexus-Quant 1.58b">Nexus-Quant 1.58b (Ultra Edge)</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono text-slate-400 mb-1">
                  <span>TEMPERATURE: {temperature}</span>
                  <span>{temperature < 0.4 ? 'Deterministic' : 'Creative Exploration'}</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.05"
                  value={temperature} 
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-white/5 font-mono text-xs text-slate-300">
                <div className="flex items-center justify-between text-[10px] text-cyan-400 mb-2">
                  <span>LIVE RUNTIME TELEMETRY</span>
                  <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" /> READY</span>
                </div>
                <p className="text-slate-400">
                  Prompt: "Synthesize unified agent routing policy across edge inference nodes."
                </p>
                <p className="mt-2 text-cyan-300">
                  Output: "Generated 3 routing matrices with 0.84ms dispatch overhead. Quantization verified clean at FP8."
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
              <button 
                onClick={() => setPlaygroundOpen(false)}
                className="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-sm font-medium"
              >
                Close
              </button>
              <button 
                onClick={() => alert(`Inference deployed to ${selectedModel} at temperature ${temperature}!`)}
                className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm shadow-lg shadow-cyan-500/20 transition-all"
              >
                Execute Test Pass
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="relative z-10 py-12 px-6 md:px-12 border-t border-white/5 mt-20 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" />
        <p className="text-xs text-slate-500 font-mono text-center md:text-left">
          © 2026 __BRAND_NAME__. Engineered with React Bits (reactbits.dev) & Lucide React.
        </p>
        <div className="flex items-center gap-6 text-xs text-slate-400">
          <a href="#" className="hover:text-cyan-400 transition-colors">Documentation</a>
          <a href="#" className="hover:text-cyan-400 transition-colors">Weights</a>
          <a href="#" className="hover:text-cyan-400 transition-colors">Security</a>
        </div>
      </footer>
    </div>
  );
}'''
        return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

    def _generate_dual_mode_index_html(self, brand_name: str, domain: str, badge_letter: str, colors: dict) -> str:
        d_upper = domain.upper()
        if d_upper in ["RESTAURANT_CULINARY", "RESTAURANT_FOOD"]:
            return generate_restaurant_culinary_index_html(brand_name, badge_letter, colors)
        elif d_upper in ["EDITORIAL_FASHION", "FASHION_APPAREL"]:
            return generate_fashion_editorial_index_html(brand_name, badge_letter, colors)
        elif d_upper in ["SCULPTURAL_FURNITURE"]:
            return generate_sculptural_furniture_index_html(brand_name, badge_letter, colors)
        elif d_upper in ["ORGANIC_SANCTUARY", "REAL_ESTATE"]:
            return generate_sanctuary_real_estate_index_html(brand_name, badge_letter, colors)
        elif d_upper in ["LUXURY_ATELIER"]:
            return generate_luxury_atelier_index_html(brand_name, badge_letter, colors)
        elif d_upper in ["EDITORIAL_ARCHITECTURAL", "CREATIVE_AGENCY", "PORTFOLIO"]:
            return generate_creative_agency_index_html(brand_name, badge_letter, colors)
        elif d_upper in ["STREAMING_DATA_DEVTOOL"]:
            return self._generate_streaming_devtool_index_html(brand_name, badge_letter, colors)

        prompt_domain = f"{brand_name} {domain}".lower()
        if any(k in prompt_domain for k in ["restaurant", "food", "dining", "kitchen", "bistro", "cafe", "osteria", "culinary"]):
            return generate_restaurant_culinary_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["fashion", "velour", "couture", "apparel", "runway", "atelier"]):
            return generate_fashion_editorial_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["furniture", "chair", "sofa", "armchair", "interior", "formora", "simply", "seating"]):
            return generate_sculptural_furniture_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["real estate", "villa", "property", "sanctuary", "orizon", "oasis", "cantilever"]):
            return generate_sanctuary_real_estate_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["mariana", "brand studio", "branding studio", "rose gold", "crimson"]):
            return generate_luxury_atelier_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["solaris", "stone", "monolith", "travertine", "limestone", "architectural"]):
            return generate_creative_agency_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["agency", "portfolio", "creative", "studio", "nexus"]):
            return generate_creative_agency_index_html(brand_name, badge_letter, colors)
        elif any(k in prompt_domain for k in ["vortex", "pipeline", "streaming", "event stream", "telemetry", "distributed"]):
            return self._generate_streaming_devtool_index_html(brand_name, badge_letter, colors)
        return self._generate_ai_studio_index_html(brand_name, badge_letter, colors)

    def _generate_ai_studio_index_html(self, brand_name: str, badge_letter: str, colors: dict) -> str:
        """Dual-mode index.html that supports Vite module loading AND instant standalone browser rendering."""
        template = '''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — React Bits Architecture</title>
  
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN for immediate standalone preview -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            'bg-primary': '#07090e',
            'bg-surface': '#0d121f',
            'bg-card': '#141c2e',
            'accent-primary': '#38bdf8',
            'accent-hover': '#0284c7'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            heading: ['Outfit', 'sans-serif'],
            mono: ['"Fira Code"', 'monospace']
          }
        }
      }
    };
  </script>

  <!-- Lucide Vector Icons Library -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <style>
    body {
      background: #07090e;
      color: #f8fafc;
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      margin: 0;
      overflow-x: hidden;
    }
    .animate-shimmer {
      background-size: 200% auto;
      animation: shimmer 2.5s linear infinite;
    }
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }
    .animate-spin-slow {
      animation: spin 8s linear infinite;
    }
  </style>
</head>
<body class="bg-[#07090e] text-slate-100">
  <div id="root">
    <!-- Standalone Pre-Render Fallback (guarantees immediate instant render in preview and playwright before npm build) -->
    <div class="min-h-screen relative overflow-hidden">
      <!-- React Bits Canvas Background -->
      <canvas id="squares-canvas" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>

      <!-- Navigation Bar -->
      <nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#07090e]/80 border-b border-white/5 py-4 px-6 md:px-12">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-3 cursor-pointer">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 via-sky-500/10 to-indigo-500/20 border border-cyan-500/30 flex items-center justify-center font-mono font-bold text-cyan-400 shadow-lg shadow-cyan-500/10">
              __BADGE_LETTER__
            </div>
            <div class="flex flex-col">
              <span class="font-heading font-extrabold tracking-tight text-xl text-white">__BRAND_NAME__</span>
              <span class="text-[10px] font-mono tracking-widest text-zinc-400 uppercase">INTELLIGENCE LAB</span>
            </div>
          </div>

          <div class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
            <a href="#architectures" class="text-cyan-400 font-semibold">Architectures</a>
            <a href="#benchmarks" class="hover:text-cyan-400 transition-colors">Benchmarks</a>
            <a href="#specs" class="hover:text-cyan-400 transition-colors">Runtime Specs</a>
          </div>

          <div class="flex items-center gap-4">
            <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-400">
              <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
              <span class="bg-gradient-to-r from-slate-300 via-white to-slate-300 bg-clip-text text-transparent animate-shimmer">REACT BITS v4.2 LIVE</span>
            </div>
            <button onclick="toggleModal(true)" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black font-semibold text-sm hover:bg-cyan-300 transition-all shadow-lg shadow-white/10">
              <i data-lucide="terminal" class="w-4 h-4"></i>
              <span>Playground</span>
            </button>
          </div>
        </div>
      </nav>

      <!-- Hero Section with DecryptedText -->
      <header class="relative z-10 pt-20 pb-16 px-6 md:px-12 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
          <span>NEURAL ARCHITECTURE SYNTHESIS</span>
        </div>

        <h1 class="text-4xl md:text-7xl font-extrabold tracking-tight mb-6 max-w-5xl mx-auto leading-tight text-white font-mono" id="hero-title">
          INTELLIGENCE ARCHITECTED AT SCALE
        </h1>

        <p class="text-lg md:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
          __BRAND_NAME__ pioneers self-evolving foundation architectures with sub-millisecond inference, dynamic mixture-of-agents routing, and verified zero-loss quantization.
        </p>

        <div class="flex flex-wrap items-center justify-center gap-4">
          <div class="relative p-[1px] overflow-hidden rounded-xl">
            <div class="absolute inset-[-100%] bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(56,189,248,0.9)_360deg)] animate-spin-slow"></div>
            <div class="relative z-10 rounded-xl bg-slate-900/90 backdrop-blur-md">
              <button onclick="toggleModal(true)" class="flex items-center gap-3 px-8 py-4 text-white font-semibold rounded-xl text-base group">
                <i data-lucide="zap" class="w-5 h-5 text-cyan-400"></i>
                <span>Deploy Architecture</span>
                <i data-lucide="arrow-right" class="w-4 h-4 text-slate-400"></i>
              </button>
            </div>
          </div>

          <button onclick="document.getElementById('architectures').scrollIntoView({behavior:'smooth'})" class="flex items-center gap-2 px-7 py-4 rounded-xl bg-slate-900/90 border border-white/10 hover:border-cyan-500/40 text-slate-200 font-medium text-base transition-colors">
            <i data-lucide="code-2" class="w-4 h-4 text-slate-400"></i>
            <span>Inspect Benchmarks</span>
          </button>
        </div>
      </header>

      <!-- KPI Metrics -->
      <section class="relative z-10 py-8 px-6 md:px-12 max-w-7xl mx-auto">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 rounded-2xl bg-slate-950/60 border border-white/5 backdrop-blur-xl">
          <div class="flex flex-col items-center md:items-start p-4">
            <div class="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
              <i data-lucide="zap" class="w-4 h-4"></i>
              <span>INFERENCE SPEED</span>
            </div>
            <div class="text-3xl font-extrabold text-white" id="count-tps">142 tps</div>
            <span class="text-xs text-slate-500 mt-1">Per GPU streaming throughput</span>
          </div>

          <div class="flex flex-col items-center md:items-start p-4 border-l border-white/5">
            <div class="flex items-center gap-2 text-xs font-mono text-emerald-400 mb-1">
              <i data-lucide="shield-check" class="w-4 h-4"></i>
              <span>SLA RELIABILITY</span>
            </div>
            <div class="text-3xl font-extrabold text-white">99.98%</div>
            <span class="text-xs text-slate-500 mt-1">Multi-region active cluster</span>
          </div>

          <div class="flex flex-col items-center md:items-start p-4 border-l border-white/5">
            <div class="flex items-center gap-2 text-xs font-mono text-indigo-400 mb-1">
              <i data-lucide="activity" class="w-4 h-4"></i>
              <span>FIRST TOKEN TIME</span>
            </div>
            <div class="text-3xl font-extrabold text-white">12 ms</div>
            <span class="text-xs text-slate-500 mt-1">Direct kernel optimization</span>
          </div>

          <div class="flex flex-col items-center md:items-start p-4 border-l border-white/5">
            <div class="flex items-center gap-2 text-xs font-mono text-purple-400 mb-1">
              <i data-lucide="cpu" class="w-4 h-4"></i>
              <span>ACTIVE WEIGHTS</span>
            </div>
            <div class="text-3xl font-extrabold text-white">70 B</div>
            <span class="text-xs text-slate-500 mt-1">FP8 native tensor cores</span>
          </div>
        </div>
      </section>

      <!-- React Bits Spotlight Cards Grid -->
      <section id="architectures" class="relative z-10 py-16 px-6 md:px-12 max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row items-start md:items-end justify-between mb-12">
          <div>
            <span class="text-xs font-mono text-cyan-400 tracking-widest uppercase">FOUNDATION PIPELINE</span>
            <h2 class="text-3xl md:text-5xl font-bold tracking-tight text-white mt-2">
              Frontier Model Matrix
            </h2>
          </div>
          <p class="text-slate-400 text-sm max-w-md mt-4 md:mt-0 font-light">
            Engineered with React Bits micro-interactions, vector Lucide icons, and clean text branding.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Card 1 -->
          <div class="spotlight-card relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d121f]/90 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between">
            <div class="spotlight-glow pointer-events-none absolute -inset-px transition-opacity duration-300 opacity-0"></div>
            <div class="relative z-10">
              <div class="flex items-center justify-between mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                  Multimodal Foundation
                </span>
                <span class="flex items-center gap-1.5 text-xs font-mono text-slate-400">
                  <i data-lucide="activity" class="w-3.5 h-3.5 text-cyan-400"></i> 12ms
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2 tracking-tight">Aetheria-Omni 70B</h3>
              <p class="text-slate-400 text-sm leading-relaxed mb-6 font-light">
                SOTA frontier reasoning engine trained on multi-token prediction with native vision-audio synthesis.
              </p>
              <div class="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs font-mono text-slate-400 mb-6">
                <div>
                  <span class="text-slate-500 block text-[10px]">CONTEXT</span>
                  <span class="text-white font-medium">128k Tokens</span>
                </div>
                <div>
                  <span class="text-slate-500 block text-[10px]">THROUGHPUT</span>
                  <span class="text-cyan-400 font-medium">142 tps</span>
                </div>
              </div>
            </div>
            <div class="pt-4 border-t border-white/5 flex items-center justify-between relative z-10">
              <button onclick="toggleModal(true, 'Aetheria-Omni 70B')" class="flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300">
                <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
                <span>Test in Playground</span>
              </button>
              <i data-lucide="chevron-right" class="w-4 h-4 text-slate-500"></i>
            </div>
          </div>

          <!-- Card 2 -->
          <div class="spotlight-card relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d121f]/90 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between">
            <div class="spotlight-glow pointer-events-none absolute -inset-px transition-opacity duration-300 opacity-0"></div>
            <div class="relative z-10">
              <div class="flex items-center justify-between mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                  Latent Generative
                </span>
                <span class="flex items-center gap-1.5 text-xs font-mono text-slate-400">
                  <i data-lucide="activity" class="w-3.5 h-3.5 text-cyan-400"></i> 18ms
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2 tracking-tight">Synapse-Diffusion v3</h3>
              <p class="text-slate-400 text-sm leading-relaxed mb-6 font-light">
                Continuous latent flow matching model engineered for sub-second spatial and code generation.
              </p>
              <div class="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs font-mono text-slate-400 mb-6">
                <div>
                  <span class="text-slate-500 block text-[10px]">CONTEXT</span>
                  <span class="text-white font-medium">64k Tokens</span>
                </div>
                <div>
                  <span class="text-slate-500 block text-[10px]">THROUGHPUT</span>
                  <span class="text-cyan-400 font-medium">88 tps</span>
                </div>
              </div>
            </div>
            <div class="pt-4 border-t border-white/5 flex items-center justify-between relative z-10">
              <button onclick="toggleModal(true, 'Synapse-Diffusion v3')" class="flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300">
                <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
                <span>Test in Playground</span>
              </button>
              <i data-lucide="chevron-right" class="w-4 h-4 text-slate-500"></i>
            </div>
          </div>

          <!-- Card 3 -->
          <div class="spotlight-card relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d121f]/90 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between">
            <div class="spotlight-glow pointer-events-none absolute -inset-px transition-opacity duration-300 opacity-0"></div>
            <div class="relative z-10">
              <div class="flex items-center justify-between mb-4">
                <span class="px-3 py-1 rounded-full text-xs font-mono bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                  Ternary Edge Runtime
                </span>
                <span class="flex items-center gap-1.5 text-xs font-mono text-slate-400">
                  <i data-lucide="activity" class="w-3.5 h-3.5 text-cyan-400"></i> 3ms
                </span>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2 tracking-tight">Nexus-Quant 1.58b</h3>
              <p class="text-slate-400 text-sm leading-relaxed mb-6 font-light">
                Ultra-low footprint 1.58-bit quantized kernel designed for real-time edge robotics and embedded devices.
              </p>
              <div class="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-950/60 border border-white/5 text-xs font-mono text-slate-400 mb-6">
                <div>
                  <span class="text-slate-500 block text-[10px]">CONTEXT</span>
                  <span class="text-white font-medium">32k Tokens</span>
                </div>
                <div>
                  <span class="text-slate-500 block text-[10px]">THROUGHPUT</span>
                  <span class="text-cyan-400 font-medium">410 tps</span>
                </div>
              </div>
            </div>
            <div class="pt-4 border-t border-white/5 flex items-center justify-between relative z-10">
              <button onclick="toggleModal(true, 'Nexus-Quant 1.58b')" class="flex items-center gap-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300">
                <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
                <span>Test in Playground</span>
              </button>
              <i data-lucide="chevron-right" class="w-4 h-4 text-slate-500"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- Playground Modal -->
      <div id="modal-container" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="bg-[#0b0f19] border border-cyan-500/30 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative">
          <div class="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <i data-lucide="terminal" class="w-4 h-4"></i>
              </div>
              <div>
                <h3 class="font-bold text-white text-lg">Model Playground & Neural Inspector</h3>
                <p class="text-xs text-slate-400" id="modal-subtitle">Target Architecture: Aetheria-Omni 70B</p>
              </div>
            </div>
            <button onclick="toggleModal(false)" class="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white">
              <i data-lucide="x" class="w-5 h-5"></i>
            </button>
          </div>

          <div class="space-y-4 mb-6">
            <div>
              <label class="text-xs font-mono text-slate-400 block mb-1">SELECT ACTIVE MODEL</label>
              <select id="modal-select" class="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-cyan-500 outline-none">
                <option value="Aetheria-Omni 70B">Aetheria-Omni 70B (Frontier Reasoning)</option>
                <option value="Synapse-Diffusion v3">Synapse-Diffusion v3 (Generative)</option>
                <option value="Nexus-Quant 1.58b">Nexus-Quant 1.58b (Ultra Edge)</option>
              </select>
            </div>

            <div class="p-4 rounded-xl bg-slate-950 border border-white/5 font-mono text-xs text-slate-300">
              <div class="flex items-center justify-between text-[10px] text-cyan-400 mb-2">
                <span>LIVE RUNTIME TELEMETRY</span>
                <span class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> READY</span>
              </div>
              <p class="text-slate-400">Prompt: "Synthesize unified agent routing policy across edge inference nodes."</p>
              <p class="mt-2 text-cyan-300">Output: "Generated 3 routing matrices with 0.84ms dispatch overhead. Quantization verified clean at FP8."</p>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
            <button onclick="toggleModal(false)" class="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-sm font-medium">Close</button>
            <button onclick="alert('Inference pass executed successfully!')" class="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm shadow-lg shadow-cyan-500/20">
              Execute Test Pass
            </button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="relative z-10 py-12 px-6 md:px-12 border-t border-white/5 mt-20 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center font-mono font-bold text-cyan-400 text-sm">
            __BADGE_LETTER__
          </div>
          <span class="font-heading font-bold text-white text-base">__BRAND_NAME__</span>
        </div>
        <p class="text-xs text-slate-500 font-mono text-center md:text-left">
          © 2026 __BRAND_NAME__. Engineered with React Bits (reactbits.dev) & Lucide React.
        </p>
        <div class="flex items-center gap-6 text-xs text-slate-400">
          <a href="#" class="hover:text-cyan-400">Documentation</a>
          <a href="#" class="hover:text-cyan-400">Weights</a>
          <a href="#" class="hover:text-cyan-400">Security</a>
        </div>
      </footer>
    </div>
  </div>

  <!-- Vite module entry -->
  <script type="module" src="/src/main.jsx"></script>

  <!-- Interactive Scripts for React Bits canvas, DecryptedText, and SpotlightCards -->
  <script>
    // 1. Initialize Lucide Icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }

    // 2. React Bits Squares Canvas Background
    (function initSquares() {
      const canvas = document.getElementById('squares-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      let mouseX = -1000, mouseY = -1000;

      function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }
      resize();
      window.addEventListener('resize', resize);

      window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
      });

      function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const squareSize = 48;
        const cols = Math.ceil(canvas.width / squareSize);
        const rows = Math.ceil(canvas.height / squareSize);

        for (let i = 0; i < cols; i++) {
          for (let j = 0; j < rows; j++) {
            const x = i * squareSize;
            const y = j * squareSize;
            const dist = Math.hypot(x + squareSize/2 - mouseX, y + squareSize/2 - mouseY);

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
            ctx.strokeRect(x, y, squareSize, squareSize);

            if (dist < 130) {
              ctx.fillStyle = 'rgba(14, 165, 233, 0.18)';
              ctx.globalAlpha = Math.max(0, 1 - dist / 130);
              ctx.fillRect(x + 1, y + 1, squareSize - 2, squareSize - 2);
              ctx.globalAlpha = 1.0;
            }
          }
        }
        requestAnimationFrame(draw);
      }
      draw();
    })();

    // 3. React Bits DecryptedText Animation on Hero Title
    (function initDecryptedText() {
      const title = document.getElementById('hero-title');
      if (!title) return;
      const originalText = title.textContent.trim();
      const glyphs = "ABCDEF0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";
      let iteration = 0;

      function scramble() {
        iteration = 0;
        const interval = setInterval(() => {
          title.textContent = originalText.split("").map((char, index) => {
            if (char === " ") return " ";
            if (index < iteration) return originalText[index];
            return glyphs[Math.floor(Math.random() * glyphs.length)];
          }).join("");

          if (iteration >= originalText.length) {
            clearInterval(interval);
          }
          iteration += 1 / (14 / originalText.length);
        }, 35);
      }

      scramble();
      title.addEventListener('mouseenter', scramble);
    })();

    // 4. React Bits Spotlight Cards mouse tracking
    document.querySelectorAll('.spotlight-card').forEach((card) => {
      const glow = card.querySelector('.spotlight-glow');
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        if (glow) {
          glow.style.opacity = '1';
          glow.style.background = `radial-gradient(400px circle at ${x}px ${y}px, rgba(14, 165, 233, 0.18), transparent 40%)`;
        }
      });
      card.addEventListener('mouseleave', () => {
        if (glow) glow.style.opacity = '0';
      });
    });

    // 5. Modal Controller
    function toggleModal(open, modelName) {
      const modal = document.getElementById('modal-container');
      const sub = document.getElementById('modal-subtitle');
      if (modelName && sub) {
        sub.textContent = 'Target Architecture: ' + modelName;
        const sel = document.getElementById('modal-select');
        if (sel) sel.value = modelName;
      }
      if (modal) {
        if (open) {
          modal.classList.remove('hidden');
        } else {
          modal.classList.add('hidden');
        }
      }
      if (typeof lucide !== 'undefined') {
        lucide.createIcons();
      }
    }
  </script>
</body>
</html>'''
        return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

    def _generate_streaming_devtool_app_jsx(self, brand_name: str, badge_letter: str, colors: dict) -> str:
        template = '''import React, { useState } from 'react';
import { 
  GitBranch, Activity, Cpu, Layers, Database, Server, 
  Terminal, SlidersHorizontal, Check, X, ArrowRight, Zap,
  ShieldCheck, Radio, HardDrive, RefreshCw, ChevronRight,
  Filter, Play, AlertCircle
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { Squares } from './components/reactbits/Squares';
import { DecryptedText } from './components/reactbits/DecryptedText';
import { ShinyText } from './components/reactbits/ShinyText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { StarBorder } from './components/reactbits/StarBorder';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [playgroundOpen, setPlaygroundOpen] = useState(false);
  const [activeNode, setActiveNode] = useState('processor');
  const [shards, setShards] = useState(1024);
  const [bufferMB, setBufferMB] = useState(512);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [burstLogs, setBurstLogs] = useState([
    '[SYSTEM] Cluster initialized with 1,024 active partitions.',
    '[QUORUM] Raft leader elected on node-04 (latency 0.12ms).',
    '[INGEST] Listening for telemetry streams on port 9092.'
  ]);
  const [burstActive, setBurstActive] = useState(false);

  const calculatedThroughput = ((shards * 2.34) + (bufferMB * 0.95)).toFixed(1);

  const handleInjectBurst = () => {
    setBurstActive(true);
    const time = new Date().toISOString().substring(11, 23);
    const newLogs = [
      `[${time}] INGEST: Burst of 50,000 telemetry events received on port 9092.`,
      `[${time}] SHARDING: Dispatched across ${shards} partition rings in 0.38ms (0 dropped).`,
      `[${time}] PROCESSOR: Window aggregation computed. Sink replication ACK received.`,
      ...burstLogs.slice(0, 5)
    ];
    setBurstLogs(newLogs);
    setTimeout(() => setBurstActive(false), 800);
  };

  const nodes = {
    ingest: {
      title: 'Ingestion Gateway',
      protocol: 'gRPC / Kafka / WebSockets',
      rate: '2.4M msg/s',
      buffer: '128 MB ring',
      status: 'OPTIMAL',
      desc: 'Zero-copy kernel bypass ingesting multi-tenant telemetry bursts directly into userland ring buffers.'
    },
    processor: {
      title: 'Stream Processor',
      protocol: 'Vectorized Map/Reduce & Windowing',
      rate: '2.1M msg/s',
      buffer: '512 MB working set',
      status: 'OPTIMAL',
      desc: 'Stateful tumbling and sliding window processors evaluating real-time stream topologies at sub-millisecond p99.'
    },
    ring: {
      title: 'Partition Sharding Ring',
      protocol: 'Consistent Hash Ring (1,024 Shards)',
      rate: '1,024 Partitions',
      buffer: 'Zero-loss rebalance',
      status: 'HEALTHY',
      desc: 'Deterministic partition allocation with automatic peer heartbeat detection and sub-10ms partition failover.'
    },
    sink: {
      title: 'Durable Sink Connectors',
      protocol: 'ClickHouse / S3 Parquet / Redis',
      rate: '1.8M msg/s persisted',
      buffer: '99.999% SLA commit',
      status: 'SYNCED',
      desc: 'High-throughput columnar write-ahead log flush committing exactly-once state to downstream analytical sinks.'
    }
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black relative overflow-x-hidden">
      {/* React Bits Animated Background */}
      <Squares 
        squareSize={48} 
        strokeColor="rgba(255, 255, 255, 0.04)" 
        hoverColor="rgba(14, 165, 233, 0.22)" 
      />

      {/* Navigation Header */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-[#07090e]/85 border-b border-white/10 py-4 px-6 md:px-12">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" subtitle="DISTRIBUTED PIPELINE ENGINE" />

          {/* Desktop Nav Items */}
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#topology" className="hover:text-cyan-400 transition-colors">Topology</a>
            <a href="#benchmarks" className="hover:text-cyan-400 transition-colors">Benchmarks</a>
            <a href="#architecture" className="hover:text-cyan-400 transition-colors">Architecture</a>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <ShinyText text="CLUSTER ACTIVE — 100% QUORUM" />
            </div>

            <Magnet>
              <button 
                onClick={() => setPlaygroundOpen(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black font-semibold text-sm hover:bg-cyan-300 focus-visible:ring-2 focus-visible:ring-cyan-400 transition-all shadow-lg shadow-white/10"
              >
                <SlidersHorizontal className="w-4 h-4" />
                Cluster Console
              </button>
            </Magnet>
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2.5 rounded-lg bg-slate-900 border border-white/10 text-slate-300 focus-visible:ring-2 focus-visible:ring-cyan-400"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <SlidersHorizontal className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-white/10 pt-4 flex flex-col gap-3">
            <a href="#topology" onClick={() => setMobileMenuOpen(false)} className="text-left py-2 text-slate-300 hover:text-cyan-400">Topology</a>
            <a href="#benchmarks" onClick={() => setMobileMenuOpen(false)} className="text-left py-2 text-slate-300 hover:text-cyan-400">Benchmarks</a>
            <a href="#architecture" onClick={() => setMobileMenuOpen(false)} className="text-left py-2 text-slate-300 hover:text-cyan-400">Architecture</a>
            <button onClick={() => { setPlaygroundOpen(true); setMobileMenuOpen(false); }} className="flex items-center gap-2 py-2 text-cyan-400 font-semibold">
              <SlidersHorizontal className="w-4 h-4" /> Launch Cluster Console
            </button>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <header className="relative z-10 pt-20 pb-16 px-6 md:px-12 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full bg-gradient-to-r from-cyan-500/10 via-sky-500/10 to-indigo-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span>REAL-TIME STREAMING & PIPELINE ENGINE</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 max-w-5xl mx-auto leading-tight text-white font-mono">
          <DecryptedText text="REAL-TIME STREAM PROCESSING AT WIRE SPEED" speed={30} maxIterations={14} />
        </h1>

        <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
          __BRAND_NAME__ is a high-performance distributed event streaming engine engineered for sub-millisecond p99 latency, deterministic partition sharding, and zero-drop exactly-once semantics.
        </p>

        {/* Hero CTA Row */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          <StarBorder speed="4s">
            <button 
              onClick={() => setPlaygroundOpen(true)}
              className="flex items-center gap-3 px-8 py-4 text-white font-semibold rounded-xl text-base group focus-visible:ring-2 focus-visible:ring-cyan-400"
            >
              <Zap className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
              <span>Configure Cluster</span>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </button>
          </StarBorder>

          <Magnet>
            <button 
              onClick={() => { const el = document.getElementById('topology'); if (el) el.scrollIntoView({ behavior: 'smooth' }); }}
              className="flex items-center gap-2 px-7 py-4 rounded-xl bg-slate-900/90 border border-white/10 hover:border-cyan-500/40 text-slate-200 font-medium text-base transition-colors focus-visible:ring-2 focus-visible:ring-cyan-400"
            >
              <GitBranch className="w-4 h-4 text-slate-400" />
              <span>Inspect Topology</span>
            </button>
          </Magnet>
        </div>
      </header>

      {/* KPI Telemetry Metrics Row - Tabular Nums */}
      <section id="benchmarks" className="relative z-10 py-8 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 rounded-2xl bg-slate-950/70 border border-white/10 backdrop-blur-xl">
          <div className="flex flex-col items-center md:items-start p-4">
            <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
              <Zap className="w-4 h-4" />
              <span>THROUGHPUT</span>
            </div>
            <div className="text-3xl font-extrabold text-white font-mono tabular-nums">
              <CountUp to={2400000} duration={1.5} suffix=" msg/s" />
            </div>
            <span className="text-xs text-slate-400 mt-1">Per node streaming throughput</span>
          </div>

          <div className="flex flex-col items-center md:items-start p-4 border-l border-white/10">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 mb-1">
              <Activity className="w-4 h-4" />
              <span>p99 LATENCY</span>
            </div>
            <div className="text-3xl font-extrabold text-white font-mono tabular-nums">
              0.42 ms
            </div>
            <span className="text-xs text-slate-400 mt-1">Direct kernel bypass dispatch</span>
          </div>

          <div className="flex flex-col items-center md:items-start p-4 border-l border-white/10">
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 mb-1">
              <GitBranch className="w-4 h-4" />
              <span>ACTIVE PARTITIONS</span>
            </div>
            <div className="text-3xl font-extrabold text-white font-mono tabular-nums">
              {shards.toLocaleString()}
            </div>
            <span className="text-xs text-slate-400 mt-1">Consistent partition ring</span>
          </div>

          <div className="flex flex-col items-center md:items-start p-4 border-l border-white/10">
            <div className="flex items-center gap-2 text-xs font-mono text-amber-400 mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span>ZERO-DROP SLA</span>
            </div>
            <div className="text-3xl font-extrabold text-white font-mono tabular-nums">
              99.999%
            </div>
            <span className="text-xs text-slate-400 mt-1">Strict exactly-once guarantee</span>
          </div>
        </div>
      </section>

      {/* Interactive Pipeline Topology Visualizer */}
      <section id="topology" className="relative z-10 py-16 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-end justify-between mb-8">
          <div>
            <span className="text-xs font-mono text-cyan-400 tracking-widest uppercase">STREAM ARCHITECTURE</span>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-white mt-1">
              Interactive Pipeline Topology
            </h2>
          </div>
          <p className="text-slate-400 text-sm max-w-md mt-2 md:mt-0 font-light">
            Select any stage in the live distributed pipeline to inspect buffer depth and telemetry.
          </p>
        </div>

        {/* Pipeline Nodes Flow */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[
            { id: 'ingest', name: '1. Ingest Gateway', icon: Radio, metric: '2.4M msg/s' },
            { id: 'processor', name: '2. Stream Processor', icon: Cpu, metric: '0.18ms win' },
            { id: 'ring', name: '3. Partition Ring', icon: GitBranch, metric: `${shards} shards` },
            { id: 'sink', name: '4. Storage Sinks', icon: Database, metric: 'Durable ACK' }
          ].map((item) => {
            const Icon = item.icon;
            const isSelected = activeNode === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveNode(item.id)}
                className={`p-5 rounded-2xl border text-left transition-all duration-300 focus-visible:ring-2 focus-visible:ring-cyan-400 ${
                  isSelected 
                    ? 'bg-slate-900 border-cyan-400/80 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-400/40' 
                    : 'bg-slate-950/60 border-white/10 hover:border-white/20 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${isSelected ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                    {item.metric}
                  </span>
                </div>
                <h3 className="font-semibold text-white text-base mb-1">{item.name}</h3>
                <p className="text-xs text-slate-400 font-mono">Click to inspect status</p>
              </button>
            );
          })}
        </div>

        {/* Selected Node Details Inspector */}
        <div className="p-6 rounded-2xl bg-slate-950/80 border border-white/10 backdrop-blur-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-white/10 gap-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold font-mono">
                {activeNode === 'ingest' ? 'IN' : activeNode === 'processor' ? 'PR' : activeNode === 'ring' ? 'RG' : 'SK'}
              </div>
              <div>
                <h4 className="text-lg font-bold text-white">{nodes[activeNode].title}</h4>
                <p className="text-xs font-mono text-cyan-400">{nodes[activeNode].protocol}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                {nodes[activeNode].status}
              </span>
              <button 
                onClick={handleInjectBurst} 
                disabled={burstActive}
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 text-cyan-300 text-xs font-semibold focus-visible:ring-2 focus-visible:ring-cyan-400 transition-colors"
              >
                <Play className="w-3.5 h-3.5" />
                {burstActive ? 'Injecting...' : 'Inject Test Event'}
              </button>
            </div>
          </div>

          <p className="text-sm text-slate-300 leading-relaxed mb-6 font-light">
            {nodes[activeNode].desc}
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-900/60 border border-white/5 font-mono text-xs">
            <div>
              <span className="text-slate-400 block text-[10px]">CURRENT RATE</span>
              <span className="text-white font-semibold text-sm tabular-nums">{nodes[activeNode].rate}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">RING BUFFER</span>
              <span className="text-cyan-400 font-semibold text-sm tabular-nums">{nodes[activeNode].buffer}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">DROPPED PACKETS</span>
              <span className="text-emerald-400 font-semibold text-sm tabular-nums">0 (0.000%)</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">REPLICATION QUORUM</span>
              <span className="text-white font-semibold text-sm tabular-nums">3 / 3 Nodes</span>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Bento Grid / SpotlightCards */}
      <section id="architecture" className="relative z-10 py-16 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="mb-12">
          <span className="text-xs font-mono text-cyan-400 tracking-widest uppercase">CORE SPECIFICATIONS</span>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white mt-1">
            Engineered for Extreme Workloads
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SpotlightCard 
            className="flex flex-col justify-between h-full bg-[#0d121f]/90 border-slate-800 p-6"
            spotlightColor="rgba(14, 165, 233, 0.18)"
            borderColor="rgba(14, 165, 233, 0.4)"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
                <Cpu className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">Zero-Copy Ring Buffer</h3>
              <p className="text-slate-300 text-sm leading-relaxed mb-6 font-light">
                Utilizes io_uring and circular ring buffers to eliminate context switches between kernel and user space, achieving wire-speed throughput.
              </p>
            </div>
            <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-cyan-400">
              <span>LATENCY: &lt; 0.42ms</span>
              <ChevronRight className="w-4 h-4 text-slate-500" />
            </div>
          </SpotlightCard>

          <SpotlightCard 
            className="flex flex-col justify-between h-full bg-[#0d121f]/90 border-slate-800 p-6"
            spotlightColor="rgba(14, 165, 233, 0.18)"
            borderColor="rgba(14, 165, 233, 0.4)"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mb-4">
                <GitBranch className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">Deterministic Sharding</h3>
              <p className="text-slate-300 text-sm leading-relaxed mb-6 font-light">
                Consistent hash ring topology routes event keys deterministically across 1,024 partitions with automatic peer heartbeat failover in &lt; 10ms.
              </p>
            </div>
            <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-sky-400">
              <span>FAILOVER: &lt; 10ms</span>
              <ChevronRight className="w-4 h-4 text-slate-500" />
            </div>
          </SpotlightCard>

          <SpotlightCard 
            className="flex flex-col justify-between h-full bg-[#0d121f]/90 border-slate-800 p-6"
            spotlightColor="rgba(14, 165, 233, 0.18)"
            borderColor="rgba(14, 165, 233, 0.4)"
          >
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2 tracking-tight">Adaptive Backpressure</h3>
              <p className="text-slate-300 text-sm leading-relaxed mb-6 font-light">
                Credit-based flow regulation dynamically pauses upstream producers when downstream consumer queues reach threshold, preventing memory saturation.
              </p>
            </div>
            <div className="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-emerald-400">
              <span>SLA: 99.999% ZERO-DROP</span>
              <ChevronRight className="w-4 h-4 text-slate-500" />
            </div>
          </SpotlightCard>
        </div>
      </section>

      {/* Interactive Cluster & Pipeline Control Drawer / Modal */}
      {playgroundOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-[#0b0f19] border border-cyan-500/30 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <SlidersHorizontal className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">Cluster Topology & Shard Console</h3>
                  <p className="text-xs text-slate-400">Engine: __BRAND_NAME__ Runtime v4.2</p>
                </div>
              </div>
              <button 
                onClick={() => setPlaygroundOpen(false)}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white focus-visible:ring-2 focus-visible:ring-cyan-400"
                aria-label="Close Modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <div className="flex justify-between text-xs font-mono text-slate-400 mb-1">
                  <span>PARTITION SHARDS: <strong className="text-cyan-400 font-bold tabular-nums">{shards}</strong></span>
                  <span>Max Scale: 4,096 Shards</span>
                </div>
                <input 
                  type="range" 
                  min="64" 
                  max="4096" 
                  step="64"
                  value={shards} 
                  onChange={(e) => setShards(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono text-slate-400 mb-1">
                  <span>INGESTION RING BUFFER: <strong className="text-cyan-400 font-bold tabular-nums">{bufferMB} MB</strong></span>
                  <span>Cluster Throughput: <strong className="text-emerald-400 tabular-nums font-mono">{calculatedThroughput}k msg/s</strong></span>
                </div>
                <input 
                  type="range" 
                  min="64" 
                  max="2048" 
                  step="64"
                  value={bufferMB} 
                  onChange={(e) => setBufferMB(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-white/5 font-mono text-xs">
                <div className="flex items-center justify-between text-[10px] text-cyan-400 mb-2">
                  <span>LIVE REPLICATION TELEMETRY LOG</span>
                  <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" /> ACTIVE</span>
                </div>
                <div className="space-y-1 text-slate-300 max-h-32 overflow-y-auto">
                  {burstLogs.map((log, idx) => (
                    <p key={idx} className={idx === 0 ? "text-cyan-300" : "text-slate-400"}>{log}</p>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <button 
                onClick={handleInjectBurst} 
                disabled={burstActive}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold focus-visible:ring-2 focus-visible:ring-cyan-400 transition-colors"
              >
                <Play className="w-3.5 h-3.5 text-cyan-400" />
                <span>{burstActive ? 'Injecting...' : 'Inject 50k Event Burst'}</span>
              </button>

              <div className="flex items-center gap-3">
                <button 
                  onClick={() => setPlaygroundOpen(false)}
                  className="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-sm font-medium focus-visible:ring-2 focus-visible:ring-cyan-400"
                >
                  Close
                </button>
                <button 
                  onClick={() => { alert(`Cluster configuration committed with ${shards} shards and ${bufferMB}MB buffer!`); setPlaygroundOpen(false); }}
                  className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm shadow-lg shadow-cyan-500/20 focus-visible:ring-2 focus-visible:ring-cyan-400 transition-all"
                >
                  Apply Configuration
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="relative z-10 py-12 px-6 md:px-12 border-t border-white/10 mt-20 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" subtitle="DISTRIBUTED PIPELINE ENGINE" />
        <p className="text-xs text-slate-400 font-mono text-center md:text-left">
          © 2026 __BRAND_NAME__. Engineered with React Bits, Lucide React, and Vercel Web Standards.
        </p>
        <div className="flex items-center gap-6 text-xs text-slate-400">
          <a href="#" className="hover:text-cyan-400 transition-colors">Documentation</a>
          <a href="#" className="hover:text-cyan-400 transition-colors">Topology API</a>
          <a href="#" className="hover:text-cyan-400 transition-colors">Security</a>
        </div>
      </footer>
    </div>
  );
}'''
        return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

    def _generate_streaming_devtool_index_html(self, brand_name: str, badge_letter: str, colors: dict) -> str:
        template = '''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Distributed Streaming Engine</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            'bg-primary': '#07090e',
            'bg-surface': '#0d121f',
            'bg-card': '#141c2e',
            'accent-primary': '#38bdf8',
            'accent-hover': '#0284c7'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            heading: ['Outfit', 'sans-serif'],
            mono: ['"Fira Code"', 'monospace']
          }
        }
      }
    };
  </script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body {
      background: #07090e;
      color: #f8fafc;
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      margin: 0;
      overflow-x: hidden;
    }
    .animate-spin-slow {
      animation: spin 8s linear infinite;
    }
  </style>
</head>
<body class="bg-[#07090e] text-slate-100">
  <div id="root">
    <div class="min-h-screen relative overflow-hidden">
      <canvas id="squares-canvas" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>

      <nav class="sticky top-0 z-50 backdrop-blur-xl bg-[#07090e]/85 border-b border-white/10 py-4 px-6 md:px-12">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-3 cursor-pointer">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 via-sky-500/10 to-indigo-500/20 border border-cyan-500/30 flex items-center justify-center font-mono font-bold text-cyan-400 shadow-lg shadow-cyan-500/10">
              __BADGE_LETTER__
            </div>
            <div class="flex flex-col">
              <span class="font-heading font-extrabold tracking-tight text-xl text-white">__BRAND_NAME__</span>
              <span class="text-[10px] font-mono tracking-widest text-zinc-400 uppercase">DISTRIBUTED PIPELINE ENGINE</span>
            </div>
          </div>

          <div class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#topology" class="hover:text-cyan-400 transition-colors">Topology</a>
            <a href="#benchmarks" class="hover:text-cyan-400 transition-colors">Benchmarks</a>
            <a href="#architecture" class="hover:text-cyan-400 transition-colors">Architecture</a>
          </div>

          <div class="flex items-center gap-4">
            <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span>CLUSTER ACTIVE — 100% QUORUM</span>
            </div>
            <button onclick="toggleModal(true)" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black font-semibold text-sm hover:bg-cyan-300 transition-all shadow-lg shadow-white/10">
              <i data-lucide="sliders-horizontal" class="w-4 h-4"></i>
              <span>Cluster Console</span>
            </button>
          </div>
        </div>
      </nav>

      <header class="relative z-10 pt-20 pb-16 px-6 md:px-12 max-w-7xl mx-auto text-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 mb-8 rounded-full bg-gradient-to-r from-cyan-500/10 via-sky-500/10 to-indigo-500/10 border border-cyan-500/20 text-xs font-mono text-cyan-300">
          <i data-lucide="activity" class="w-3.5 h-3.5 text-cyan-400"></i>
          <span>REAL-TIME STREAMING & PIPELINE ENGINE</span>
        </div>

        <h1 class="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 max-w-5xl mx-auto leading-tight text-white font-mono" id="hero-title">
          REAL-TIME STREAM PROCESSING AT WIRE SPEED
        </h1>

        <p class="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
          __BRAND_NAME__ is a high-performance distributed event streaming engine engineered for sub-millisecond p99 latency, deterministic partition sharding, and zero-drop exactly-once semantics.
        </p>

        <div class="flex flex-wrap items-center justify-center gap-4">
          <div class="relative p-[1px] overflow-hidden rounded-xl">
            <div class="absolute inset-[-100%] bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(56,189,248,0.9)_360deg)] animate-spin-slow"></div>
            <div class="relative z-10 rounded-xl bg-slate-900/90 backdrop-blur-md">
              <button onclick="toggleModal(true)" class="flex items-center gap-3 px-8 py-4 text-white font-semibold rounded-xl text-base group">
                <i data-lucide="zap" class="w-5 h-5 text-cyan-400"></i>
                <span>Configure Cluster</span>
                <i data-lucide="arrow-right" class="w-4 h-4 text-slate-400"></i>
              </button>
            </div>
          </div>

          <button onclick="document.getElementById('topology').scrollIntoView({behavior:'smooth'})" class="flex items-center gap-2 px-7 py-4 rounded-xl bg-slate-900/90 border border-white/10 hover:border-cyan-500/40 text-slate-200 font-medium text-base transition-colors">
            <i data-lucide="git-branch" class="w-4 h-4 text-slate-400"></i>
            <span>Inspect Topology</span>
          </button>
        </div>
      </header>

      <section id="benchmarks" class="relative z-10 py-8 px-6 md:px-12 max-w-7xl mx-auto">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 rounded-2xl bg-slate-950/70 border border-white/10 backdrop-blur-xl">
          <div class="flex flex-col items-center md:items-start p-4">
            <div class="flex items-center gap-2 text-xs font-mono text-cyan-400 mb-1">
              <i data-lucide="zap" class="w-4 h-4"></i>
              <span>THROUGHPUT</span>
            </div>
            <div class="text-3xl font-extrabold text-white font-mono tabular-nums">2,400,000 msg/s</div>
            <span class="text-xs text-slate-400 mt-1">Per node streaming throughput</span>
          </div>

          <div class="flex flex-col items-center md:items-start p-4 border-l border-white/10">
            <div class="flex items-center gap-2 text-xs font-mono text-emerald-400 mb-1">
              <i data-lucide="activity" class="w-4 h-4"></i>
              <span>p99 LATENCY</span>
            </div>
            <div class="text-3xl font-extrabold text-white font-mono tabular-nums">0.42 ms</div>
            <span class="text-xs text-slate-400 mt-1">Direct kernel bypass dispatch</span>
          </div>

          <div class="flex flex-col items-center md:items-start p-4 border-l border-white/10">
            <div class="flex items-center gap-2 text-xs font-mono text-indigo-400 mb-1">
              <i data-lucide="git-branch" class="w-4 h-4"></i>
              <span>ACTIVE PARTITIONS</span>
            </div>
            <div class="text-3xl font-extrabold text-white font-mono tabular-nums" id="stat-shards">1,024</div>
            <span class="text-xs text-slate-400 mt-1">Consistent partition ring</span>
          </div>

          <div class="flex flex-col items-center md:items-start p-4 border-l border-white/10">
            <div class="flex items-center gap-2 text-xs font-mono text-amber-400 mb-1">
              <i data-lucide="shield-check" class="w-4 h-4"></i>
              <span>ZERO-DROP SLA</span>
            </div>
            <div class="text-3xl font-extrabold text-white font-mono tabular-nums">99.999%</div>
            <span class="text-xs text-slate-400 mt-1">Strict exactly-once guarantee</span>
          </div>
        </div>
      </section>

      <section id="topology" class="relative z-10 py-16 px-6 md:px-12 max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row items-start md:items-end justify-between mb-8">
          <div>
            <span class="text-xs font-mono text-cyan-400 tracking-widest uppercase">STREAM ARCHITECTURE</span>
            <h2 class="text-3xl md:text-4xl font-bold tracking-tight text-white mt-1">
              Interactive Pipeline Topology
            </h2>
          </div>
          <p class="text-slate-400 text-sm max-w-md mt-2 md:mt-0 font-light">
            Select any stage in the live distributed pipeline to inspect buffer depth and telemetry.
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <button onclick="selectTopologyNode('ingest')" id="btn-node-ingest" class="p-5 rounded-2xl border text-left transition-all duration-300 bg-slate-950/60 border-white/10 hover:border-white/20">
            <div class="flex items-center justify-between mb-3">
              <div class="w-9 h-9 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center">
                <i data-lucide="radio" class="w-5 h-5"></i>
              </div>
              <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">2.4M msg/s</span>
            </div>
            <h3 class="font-semibold text-white text-base mb-1">1. Ingest Gateway</h3>
            <p class="text-xs text-slate-400 font-mono">Click to inspect status</p>
          </button>

          <button onclick="selectTopologyNode('processor')" id="btn-node-processor" class="p-5 rounded-2xl border text-left transition-all duration-300 bg-slate-900 border-cyan-400/80 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-400/40">
            <div class="flex items-center justify-between mb-3">
              <div class="w-9 h-9 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
                <i data-lucide="cpu" class="w-5 h-5"></i>
              </div>
              <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">0.18ms win</span>
            </div>
            <h3 class="font-semibold text-white text-base mb-1">2. Stream Processor</h3>
            <p class="text-xs text-slate-400 font-mono">Click to inspect status</p>
          </button>

          <button onclick="selectTopologyNode('ring')" id="btn-node-ring" class="p-5 rounded-2xl border text-left transition-all duration-300 bg-slate-950/60 border-white/10 hover:border-white/20">
            <div class="flex items-center justify-between mb-3">
              <div class="w-9 h-9 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center">
                <i data-lucide="git-branch" class="w-5 h-5"></i>
              </div>
              <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20" id="badge-shards">1,024 shards</span>
            </div>
            <h3 class="font-semibold text-white text-base mb-1">3. Partition Ring</h3>
            <p class="text-xs text-slate-400 font-mono">Click to inspect status</p>
          </button>

          <button onclick="selectTopologyNode('sink')" id="btn-node-sink" class="p-5 rounded-2xl border text-left transition-all duration-300 bg-slate-950/60 border-white/10 hover:border-white/20">
            <div class="flex items-center justify-between mb-3">
              <div class="w-9 h-9 rounded-xl bg-slate-800 text-slate-400 flex items-center justify-center">
                <i data-lucide="database" class="w-5 h-5"></i>
              </div>
              <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">Durable ACK</span>
            </div>
            <h3 class="font-semibold text-white text-base mb-1">4. Storage Sinks</h3>
            <p class="text-xs text-slate-400 font-mono">Click to inspect status</p>
          </button>
        </div>

        <div class="p-6 rounded-2xl bg-slate-950/80 border border-white/10 backdrop-blur-xl">
          <div class="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-white/10 gap-4 mb-4">
            <div class="flex items-center gap-3">
              <div id="inspector-badge" class="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-bold font-mono">
                PR
              </div>
              <div>
                <h4 id="inspector-title" class="text-lg font-bold text-white">Stream Processor</h4>
                <p id="inspector-proto" class="text-xs font-mono text-cyan-400">Vectorized Map/Reduce & Windowing</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                OPTIMAL
              </span>
              <button onclick="injectTestEvent()" id="btn-inject-event" class="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/30 text-cyan-300 text-xs font-semibold transition-colors">
                <i data-lucide="play" class="w-3.5 h-3.5"></i>
                <span>Inject Test Event</span>
              </button>
            </div>
          </div>

          <p id="inspector-desc" class="text-sm text-slate-300 leading-relaxed mb-6 font-light">
            Stateful tumbling and sliding window processors evaluating real-time stream topologies at sub-millisecond p99.
          </p>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-900/60 border border-white/5 font-mono text-xs">
            <div>
              <span class="text-slate-400 block text-[10px]">CURRENT RATE</span>
              <span id="inspector-rate" class="text-white font-semibold text-sm tabular-nums">2.1M msg/s</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[10px]">RING BUFFER</span>
              <span id="inspector-buffer" class="text-cyan-400 font-semibold text-sm tabular-nums">512 MB working set</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[10px]">DROPPED PACKETS</span>
              <span class="text-emerald-400 font-semibold text-sm tabular-nums">0 (0.000%)</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[10px]">REPLICATION QUORUM</span>
              <span class="text-white font-semibold text-sm tabular-nums">3 / 3 Nodes</span>
            </div>
          </div>
        </div>
      </section>

      <section id="architecture" class="relative z-10 py-16 px-6 md:px-12 max-w-7xl mx-auto">
        <div class="mb-12">
          <span class="text-xs font-mono text-cyan-400 tracking-widest uppercase">CORE SPECIFICATIONS</span>
          <h2 class="text-3xl md:text-5xl font-bold tracking-tight text-white mt-1">
            Engineered for Extreme Workloads
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="spotlight-card relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d121f]/90 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between">
            <div class="spotlight-glow pointer-events-none absolute -inset-px transition-opacity duration-300 opacity-0"></div>
            <div class="relative z-10">
              <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-4">
                <i data-lucide="cpu" class="w-5 h-5"></i>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2 tracking-tight">Zero-Copy Ring Buffer</h3>
              <p class="text-slate-300 text-sm leading-relaxed mb-6 font-light">
                Utilizes io_uring and circular ring buffers to eliminate context switches between kernel and user space, achieving wire-speed throughput.
              </p>
            </div>
            <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-cyan-400 relative z-10">
              <span>LATENCY: &lt; 0.42ms</span>
              <i data-lucide="chevron-right" class="w-4 h-4 text-slate-500"></i>
            </div>
          </div>

          <div class="spotlight-card relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d121f]/90 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between">
            <div class="spotlight-glow pointer-events-none absolute -inset-px transition-opacity duration-300 opacity-0"></div>
            <div class="relative z-10">
              <div class="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 mb-4">
                <i data-lucide="git-branch" class="w-5 h-5"></i>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2 tracking-tight">Deterministic Sharding</h3>
              <p class="text-slate-300 text-sm leading-relaxed mb-6 font-light">
                Consistent hash ring topology routes event keys deterministically across 1,024 partitions with automatic peer heartbeat failover in &lt; 10ms.
              </p>
            </div>
            <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-sky-400 relative z-10">
              <span>FAILOVER: &lt; 10ms</span>
              <i data-lucide="chevron-right" class="w-4 h-4 text-slate-500"></i>
            </div>
          </div>

          <div class="spotlight-card relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d121f]/90 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 shadow-xl flex flex-col justify-between">
            <div class="spotlight-glow pointer-events-none absolute -inset-px transition-opacity duration-300 opacity-0"></div>
            <div class="relative z-10">
              <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
                <i data-lucide="shield-check" class="w-5 h-5"></i>
              </div>
              <h3 class="text-2xl font-bold text-white mb-2 tracking-tight">Adaptive Backpressure</h3>
              <p class="text-slate-300 text-sm leading-relaxed mb-6 font-light">
                Credit-based flow regulation dynamically pauses upstream producers when downstream consumer queues reach threshold, preventing memory saturation.
              </p>
            </div>
            <div class="pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-emerald-400 relative z-10">
              <span>SLA: 99.999% ZERO-DROP</span>
              <i data-lucide="chevron-right" class="w-4 h-4 text-slate-500"></i>
            </div>
          </div>
        </div>
      </section>

      <div id="modal-container" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <div class="bg-[#0b0f19] border border-cyan-500/30 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative">
          <div class="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <i data-lucide="sliders-horizontal" class="w-4 h-4"></i>
              </div>
              <div>
                <h3 class="font-bold text-white text-lg">Cluster Topology & Shard Console</h3>
                <p class="text-xs text-slate-400">Engine: __BRAND_NAME__ Runtime v4.2</p>
              </div>
            </div>
            <button onclick="toggleModal(false)" class="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white">
              <i data-lucide="x" class="w-5 h-5"></i>
            </button>
          </div>

          <div class="space-y-4 mb-6">
            <div>
              <div class="flex justify-between text-xs font-mono text-slate-400 mb-1">
                <span>PARTITION SHARDS: <strong id="val-shards" class="text-cyan-400 font-bold tabular-nums">1024</strong></span>
                <span>Max Scale: 4,096 Shards</span>
              </div>
              <input id="slider-shards" type="range" min="64" max="4096" step="64" value="1024" oninput="updateShards(this.value)" class="w-full accent-cyan-400">
            </div>

            <div>
              <div class="flex justify-between text-xs font-mono text-slate-400 mb-1">
                <span>INGESTION RING BUFFER: <strong id="val-buffer" class="text-cyan-400 font-bold tabular-nums">512 MB</strong></span>
                <span>Cluster Throughput: <strong id="val-throughput" class="text-emerald-400 tabular-nums font-mono">2,882.6k msg/s</strong></span>
              </div>
              <input id="slider-buffer" type="range" min="64" max="2048" step="64" value="512" oninput="updateBuffer(this.value)" class="w-full accent-cyan-400">
            </div>

            <div class="p-4 rounded-xl bg-slate-950 border border-white/5 font-mono text-xs">
              <div class="flex items-center justify-between text-[10px] text-cyan-400 mb-2">
                <span>LIVE REPLICATION TELEMETRY LOG</span>
                <span class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> ACTIVE</span>
              </div>
              <div id="modal-log-box" class="space-y-1 text-slate-300 max-h-32 overflow-y-auto">
                <p class="text-cyan-300">[SYSTEM] Cluster initialized with 1,024 active partitions.</p>
                <p class="text-slate-400">[QUORUM] Raft leader elected on node-04 (latency 0.12ms).</p>
                <p class="text-slate-400">[INGEST] Listening for telemetry streams on port 9092.</p>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-between pt-4 border-t border-white/10">
            <button onclick="injectTestEvent()" class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors">
              <i data-lucide="play" class="w-3.5 h-3.5 text-cyan-400"></i>
              <span>Inject 50k Event Burst</span>
            </button>

            <div class="flex items-center gap-3">
              <button onclick="toggleModal(false)" class="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-sm font-medium">Close</button>
              <button onclick="toggleModal(false); alert('Cluster configuration committed!');" class="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-sm shadow-lg shadow-cyan-500/20">
                Apply Configuration
              </button>
            </div>
          </div>
        </div>
      </div>

      <footer class="relative z-10 py-12 px-6 md:px-12 border-t border-white/10 mt-20 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center font-mono font-bold text-cyan-400 text-sm">
            __BADGE_LETTER__
          </div>
          <span class="font-heading font-bold text-white text-base">__BRAND_NAME__</span>
        </div>
        <p class="text-xs text-slate-400 font-mono text-center md:text-left">
          © 2026 __BRAND_NAME__. Engineered with React Bits, Lucide React, and Vercel Web Standards.
        </p>
        <div class="flex items-center gap-6 text-xs text-slate-400">
          <a href="#" class="hover:text-cyan-400">Documentation</a>
          <a href="#" class="hover:text-cyan-400">Topology API</a>
          <a href="#" class="hover:text-cyan-400">Security</a>
        </div>
      </footer>
    </div>
  </div>

  <script type="module" src="/src/main.jsx"></script>

  <script>
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }

    (function initSquares() {
      const canvas = document.getElementById('squares-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      let mouseX = -1000, mouseY = -1000;

      function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }
      resize();
      window.addEventListener('resize', resize);

      window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
      });

      function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const squareSize = 48;
        const cols = Math.ceil(canvas.width / squareSize);
        const rows = Math.ceil(canvas.height / squareSize);

        for (let i = 0; i < cols; i++) {
          for (let j = 0; j < rows; j++) {
            const x = i * squareSize;
            const y = j * squareSize;
            const dist = Math.hypot(x + squareSize/2 - mouseX, y + squareSize/2 - mouseY);

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
            ctx.strokeRect(x, y, squareSize, squareSize);

            if (dist < 130) {
              ctx.fillStyle = 'rgba(14, 165, 233, 0.18)';
              ctx.globalAlpha = Math.max(0, 1 - dist / 130);
              ctx.fillRect(x + 1, y + 1, squareSize - 2, squareSize - 2);
              ctx.globalAlpha = 1.0;
            }
          }
        }
        requestAnimationFrame(draw);
      }
      draw();
    })();

    (function initDecryptedText() {
      const title = document.getElementById('hero-title');
      if (!title) return;
      const originalText = title.textContent.trim();
      const glyphs = "ABCDEF0123456789!@#$%^&*()_+-=[]{}|;:,.<>?";
      let iteration = 0;

      function scramble() {
        iteration = 0;
        const interval = setInterval(() => {
          title.textContent = originalText.split("").map((char, index) => {
            if (char === " ") return " ";
            if (index < iteration) return originalText[index];
            return glyphs[Math.floor(Math.random() * glyphs.length)];
          }).join("");

          if (iteration >= originalText.length) {
            clearInterval(interval);
          }
          iteration += 1 / (14 / originalText.length);
        }, 30);
      }

      scramble();
      title.addEventListener('mouseenter', scramble);
    })();

    document.querySelectorAll('.spotlight-card').forEach((card) => {
      const glow = card.querySelector('.spotlight-glow');
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        if (glow) {
          glow.style.opacity = '1';
          glow.style.background = `radial-gradient(400px circle at ${x}px ${y}px, rgba(14, 165, 233, 0.18), transparent 40%)`;
        }
      });
      card.addEventListener('mouseleave', () => {
        if (glow) glow.style.opacity = '0';
      });
    });

    const nodeData = {
      ingest: { badge: 'IN', title: 'Ingestion Gateway', proto: 'gRPC / Kafka / WebSockets', rate: '2.4M msg/s', buffer: '128 MB ring', desc: 'Zero-copy kernel bypass ingesting multi-tenant telemetry bursts directly into userland ring buffers.' },
      processor: { badge: 'PR', title: 'Stream Processor', proto: 'Vectorized Map/Reduce & Windowing', rate: '2.1M msg/s', buffer: '512 MB working set', desc: 'Stateful tumbling and sliding window processors evaluating real-time stream topologies at sub-millisecond p99.' },
      ring: { badge: 'RG', title: 'Partition Sharding Ring', proto: 'Consistent Hash Ring (1,024 Shards)', rate: '1,024 Partitions', buffer: 'Zero-loss rebalance', desc: 'Deterministic partition allocation with automatic peer heartbeat detection and sub-10ms partition failover.' },
      sink: { badge: 'SK', title: 'Durable Sink Connectors', proto: 'ClickHouse / S3 Parquet / Redis', rate: '1.8M msg/s persisted', buffer: '99.999% SLA commit', desc: 'High-throughput columnar write-ahead log flush committing exactly-once state to downstream analytical sinks.' }
    };

    function selectTopologyNode(nodeKey) {
      ['ingest', 'processor', 'ring', 'sink'].forEach((k) => {
        const btn = document.getElementById('btn-node-' + k);
        if (btn) {
          if (k === nodeKey) {
            btn.className = 'p-5 rounded-2xl border text-left transition-all duration-300 bg-slate-900 border-cyan-400/80 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-400/40';
          } else {
            btn.className = 'p-5 rounded-2xl border text-left transition-all duration-300 bg-slate-950/60 border-white/10 hover:border-white/20';
          }
        }
      });
      const d = nodeData[nodeKey];
      if (d) {
        document.getElementById('inspector-badge').textContent = d.badge;
        document.getElementById('inspector-title').textContent = d.title;
        document.getElementById('inspector-proto').textContent = d.proto;
        document.getElementById('inspector-rate').textContent = d.rate;
        document.getElementById('inspector-buffer').textContent = d.buffer;
        document.getElementById('inspector-desc').textContent = d.desc;
      }
    }

    function updateShards(val) {
      document.getElementById('val-shards').textContent = val;
      const elStat = document.getElementById('stat-shards');
      if (elStat) elStat.textContent = parseInt(val).toLocaleString();
      const elBadge = document.getElementById('badge-shards');
      if (elBadge) elBadge.textContent = parseInt(val).toLocaleString() + ' shards';
      recalcThroughput();
    }

    function updateBuffer(val) {
      document.getElementById('val-buffer').textContent = val + ' MB';
      recalcThroughput();
    }

    function recalcThroughput() {
      const s = parseInt(document.getElementById('slider-shards').value) || 1024;
      const b = parseInt(document.getElementById('slider-buffer').value) || 512;
      const tp = ((s * 2.34) + (b * 0.95)).toFixed(1);
      document.getElementById('val-throughput').textContent = parseFloat(tp).toLocaleString() + 'k msg/s';
    }

    function injectTestEvent() {
      const logBox = document.getElementById('modal-log-box');
      const time = new Date().toISOString().substring(11, 23);
      if (logBox) {
        const p1 = document.createElement('p');
        p1.className = 'text-cyan-300 font-semibold';
        p1.textContent = `[${time}] INGEST: Burst of 50,000 telemetry events received on port 9092.`;
        logBox.insertBefore(p1, logBox.firstChild);
        const p2 = document.createElement('p');
        p2.className = 'text-emerald-400';
        p2.textContent = `[${time}] COMMIT: Sharded and replicated across cluster with 0 dropped packets.`;
        logBox.insertBefore(p2, logBox.children[1]);
      }
      alert('Event burst of 50,000 packets successfully injected into pipeline!');
    }

    function toggleModal(open) {
      const modal = document.getElementById('modal-container');
      if (modal) {
        if (open) {
          modal.classList.remove('hidden');
        } else {
          modal.classList.add('hidden');
        }
      }
      if (typeof lucide !== 'undefined') {
        lucide.createIcons();
      }
    }
  </script>
</body>
</html>'''
        return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)


