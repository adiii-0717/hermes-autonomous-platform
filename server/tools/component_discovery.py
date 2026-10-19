import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger('component_discovery')

class ComponentDiscoveryCatalog:
    """Catalog for discovering, matching, and injecting production-ready React Bits, 3D (R3F), and Motion (GSAP/Framer Motion) recipes."""

    SNIPPETS = {
        # --- React Bits: Animated Backgrounds ---
        'reactbits_aurora': {
            'id': 'reactbits_aurora',
            'name': 'React Bits Aurora Background',
            'library': 'react & canvas / tailwind',
            'type': 'animated_background',
            'category': 'background',
            'keywords': ['aurora', 'background', 'glow', 'fluid', 'gradient', 'canvas', 'organic', 'ambient', 'creative', 'lifestyle'],
            'install': 'Tailwind CSS (Vanilla Canvas)',
            'guidance': 'Organic radial gradient fluid wave animation rendered on responsive 2D canvas with customizable color stops and reduced-motion guard.',
            'failure_modes': 'Canvas requires resize event listener to adapt dynamically without distortion.',
            'code_sample': '''import React, { useEffect, useRef } from 'react';

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
}'''
        },
        'reactbits_squares': {
            'id': 'reactbits_squares',
            'name': 'React Bits Squares Background',
            'library': 'react & canvas / tailwind',
            'type': 'animated_background',
            'category': 'background',
            'keywords': ['squares', 'grid', 'background', 'interactive', 'hover', 'saas', 'tech', 'dashboard', 'fintech'],
            'install': 'Tailwind CSS (Vanilla Canvas)',
            'guidance': 'Interactive grid of subtle squares that illuminate smoothly in proximity to the mouse pointer.',
            'failure_modes': 'Ensure mouse coordinate calculations subtract container bounding rect offsets.',
            'code_sample': '''import React, { useRef, useEffect } from 'react';

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

  return <canvas ref={canvasRef} className={`absolute inset-0 w-full h-full pointer-events-none ${className}`} />;
}'''
        },
        'reactbits_particles': {
            'id': 'reactbits_particles',
            'name': 'React Bits Floating Particles',
            'library': 'react & canvas / tailwind',
            'type': 'animated_background',
            'category': 'background',
            'keywords': ['particles', 'stars', 'cloud', 'background', 'space', 'dots', 'store', 'ecommerce', 'luxury'],
            'install': 'Tailwind CSS (Vanilla Canvas)',
            'guidance': 'Floating particle constellation that drifts with gentle sine-wave motion and connects neighboring nodes.',
            'failure_modes': 'Cap particle count at 80 for optimal 60fps mobile execution.',
            'code_sample': '''import React, { useRef, useEffect } from 'react';

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
}'''
        },
        'reactbits_hyperspeed': {
            'id': 'reactbits_hyperspeed',
            'name': 'React Bits Hyperspeed Light Trails',
            'library': 'react & canvas / tailwind',
            'type': 'animated_background',
            'category': 'background',
            'keywords': ['hyperspeed', 'warp', 'light', 'trails', 'tunnel', 'speed', 'cyber', 'tech', 'ai', 'futuristic'],
            'install': 'Tailwind CSS (Vanilla Canvas)',
            'guidance': 'High-velocity 3D perspective warp light streaks, ideal for AI labs, performance tools, and gaming.',
            'failure_modes': 'Set z-index to negative or place behind backdrop filter so content remains perfectly readable.',
            'code_sample': '''import React, { useRef, useEffect } from 'react';

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
}'''
        },

        # --- React Bits: Text Animations ---
        'reactbits_split_text': {
            'id': 'reactbits_split_text',
            'name': 'React Bits SplitText Stagger Animation',
            'library': 'react & framer-motion',
            'type': 'text_animation',
            'category': 'typography',
            'keywords': ['split', 'text', 'stagger', 'motion', 'spring', 'headline', 'hero', 'entrance', 'kinetic'],
            'install': 'npm install framer-motion',
            'guidance': 'Spring-based kinetic typography that reveals text word-by-word with stagger delay and reduced-motion compliance.',
            'failure_modes': 'Wrap words in inline-flex to prevent awkward mid-word layout wrapping.',
            'code_sample': '''import React from 'react';
import { motion } from 'framer-motion';

export function SplitText({ text = "", className = "", delay = 0.04, stiffness = 220, damping = 18 }) {
  const words = text.split(" ");
  return (
    <span className={`inline-flex flex-wrap gap-x-2 ${className}`}>
      {words.map((word, i) => (
        <span key={i} className="inline-block overflow-hidden">
          <motion.span
            initial={{ y: "100%", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ type: "spring", stiffness, damping, delay: i * delay }}
            className="inline-block"
          >
            {word}
          </motion.span>
        </span>
      ))}
    </span>
  );
}'''
        },
        'reactbits_decrypted_text': {
            'id': 'reactbits_decrypted_text',
            'name': 'React Bits DecryptedText Cyber Scrambler',
            'library': 'react & vanilla_js',
            'type': 'text_animation',
            'category': 'typography',
            'keywords': ['decrypted', 'scramble', 'matrix', 'cyber', 'code', 'hacker', 'text', 'ai', 'tech', 'reveal'],
            'install': 'Tailwind CSS (Vanilla JS)',
            'guidance': 'Matrix/cyber character decryption animation that reveals headline text on load or mouse hover.',
            'failure_modes': 'Always clear intervals inside cleanup hooks to prevent memory leaks.',
            'code_sample': '''import React, { useState, useEffect, useRef } from 'react';

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
}'''
        },
        'reactbits_blur_text': {
            'id': 'reactbits_blur_text',
            'name': 'React Bits BlurText Focus Reveal',
            'library': 'react & framer-motion',
            'type': 'text_animation',
            'category': 'typography',
            'keywords': ['blur', 'text', 'focus', 'reveal', 'editorial', 'luxury', 'hero', 'motion'],
            'install': 'npm install framer-motion',
            'guidance': 'Animates text from a subtle blur filter and opacity into crisp, high-contrast typography.',
            'failure_modes': 'Use will-change-filter for GPU rasterization.',
            'code_sample': '''import React from 'react';
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
}'''
        },
        'reactbits_shiny_text': {
            'id': 'reactbits_shiny_text',
            'name': 'React Bits ShinyText Shimmer Gradient',
            'library': 'react & tailwind_css',
            'type': 'text_animation',
            'category': 'typography',
            'keywords': ['shiny', 'text', 'shimmer', 'metallic', 'gradient', 'badge', 'gold', 'silver', 'premium'],
            'install': 'Tailwind CSS',
            'guidance': 'CSS background-clip text with animated gradient sweep. Perfect for category badges and premium pills.',
            'failure_modes': 'Must provide fallback text color if background-clip is unsupported.',
            'code_sample': '''import React from 'react';

export function ShinyText({ text, className = "" }) {
  return (
    <span className={`inline-block bg-gradient-to-r from-slate-400 via-white to-slate-400 bg-[length:200%_auto] bg-clip-text text-transparent animate-shimmer ${className}`}>
      {text}
    </span>
  );
}'''
        },
        'reactbits_count_up': {
            'id': 'reactbits_count_up',
            'name': 'React Bits CountUp KPI Counter',
            'library': 'react & vanilla_js',
            'type': 'text_animation',
            'category': 'typography',
            'keywords': ['count', 'counter', 'kpi', 'metric', 'number', 'stats', 'dashboard', 'analytics'],
            'install': 'Vanilla React',
            'guidance': 'Intersection-observer triggered smooth numeric increment counter for stats, metrics, and ratings.',
            'failure_modes': 'Ensure formatted thousand separators do not flicker during step increment.',
            'code_sample': '''import React, { useEffect, useState, useRef } from 'react';

export function CountUp({ to = 100, duration = 1.6, prefix = "", suffix = "" }) {
  const [val, setVal] = useState(0);
  const ref = useRef(null);
  const triggered = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !triggered.current) {
        triggered.current = true;
        let start = 0;
        const totalFrames = duration * 60;
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
}'''
        },

        # --- React Bits: UI Cards & Layouts ---
        'reactbits_spotlight_card': {
            'id': 'reactbits_spotlight_card',
            'name': 'React Bits SpotlightCard Glow Border',
            'library': 'react & tailwind_css',
            'type': 'ui_card',
            'category': 'cards',
            'keywords': ['spotlight', 'card', 'glow', 'gradient', 'hover', 'border', 'saas', 'ecommerce', 'tech'],
            'install': 'Tailwind CSS',
            'guidance': 'Mouse-tracking radial glow across the card surface and dynamic illuminated perimeter border.',
            'failure_modes': 'Set pointer-events: none on radial gradient masks to ensure nested buttons and links stay clickable.',
            'code_sample': '''import React, { useRef, useState } from 'react';

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
}'''
        },
        'reactbits_tilted_card': {
            'id': 'reactbits_tilted_card',
            'name': 'React Bits TiltedCard 3D Parallax',
            'library': 'react & framer-motion',
            'type': 'ui_card',
            'category': 'cards',
            'keywords': ['tilt', 'card', '3d', 'perspective', 'parallax', 'portfolio', 'agency', 'product'],
            'install': 'npm install framer-motion',
            'guidance': 'Calculates mouse tilt coordinates with spring physics and perspective transform for physical card depth.',
            'failure_modes': 'Disable 3D tilt on mobile touch viewports to prevent scroll capture lag.',
            'code_sample': '''import React, { useRef } from 'react';
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
}'''
        },

        # --- React Bits: Micro-Interactions & Buttons ---
        'reactbits_magnet_button': {
            'id': 'reactbits_magnet_button',
            'name': 'React Bits Magnet Button',
            'library': 'react & framer-motion',
            'type': 'micro_interaction',
            'category': 'buttons',
            'keywords': ['magnet', 'button', 'cursor', 'spring', 'cta', 'interactive', 'hover'],
            'install': 'npm install framer-motion',
            'guidance': 'Tracks cursor bounds and pulls button smoothly toward cursor with responsive spring dampening.',
            'failure_modes': 'Disable on mobile touch screens with pointer-events query.',
            'code_sample': '''import React, { useRef, useState } from 'react';
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
}'''
        },
        'reactbits_star_border': {
            'id': 'reactbits_star_border',
            'name': 'React Bits StarBorder Glow Contour',
            'library': 'react & tailwind_css',
            'type': 'micro_interaction',
            'category': 'buttons',
            'keywords': ['star', 'border', 'glow', 'contour', 'cta', 'button', 'gradient', 'highlight'],
            'install': 'Tailwind CSS',
            'guidance': 'Conic gradient that rotates continuously along card or button edge, creating an ambient neon border sweep.',
            'failure_modes': 'Ensure inner container background matches parent background to prevent edge bleed.',
            'code_sample': '''import React from 'react';

export function StarBorder({ children, className = "", speed = "5s" }) {
  return (
    <div className={`relative p-[1px] overflow-hidden rounded-xl group ${className}`}>
      <div 
        className="absolute inset-[-100%] bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(56,189,248,0.9)_360deg)] animate-spin-slow"
        style={{ animationDuration: speed }}
      />
      <div className="relative z-10 rounded-xl bg-surface/90 backdrop-blur-md">
        {children}
      </div>
    </div>
  );
}'''
        },
        'reactbits_infinite_scroll': {
            'id': 'reactbits_infinite_scroll',
            'name': 'React Bits InfiniteScroll Marquee',
            'library': 'react & tailwind_css',
            'type': 'ui_layout',
            'category': 'layout',
            'keywords': ['marquee', 'scroll', 'infinite', 'logos', 'ribbon', 'partners', 'awards', 'ticker'],
            'install': 'Tailwind CSS',
            'guidance': 'Smooth continuous horizontal ribbon for client logos, partner badges, and testimonials.',
            'failure_modes': 'Pause animation on hover so users can easily read moving text or click badges.',
            'code_sample': '''import React from 'react';

export function InfiniteScroll({ items = [], speed = "25s", className = "" }) {
  return (
    <div className={`overflow-hidden whitespace-nowrap relative mask-radial ${className}`}>
      <div className="inline-flex gap-8 animate-marquee hover:[animation-play-state:paused]" style={{ animationDuration: speed }}>
        {items.concat(items).map((item, idx) => (
          <div key={idx} className="flex-shrink-0 flex items-center gap-3 px-6 py-3 rounded-full bg-surface/60 border border-white/5">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}'''
        },

        # --- Professional Iconography & Clean Branding Suites ---
        'lucide_icons_suite': {
            'id': 'lucide_icons_suite',
            'name': 'Lucide React Vector Icon Standards',
            'library': 'lucide-react',
            'type': 'ui_iconography',
            'category': 'icons',
            'keywords': ['icons', 'lucide', 'vector', 'clean', 'svg', 'professional', 'standard'],
            'install': 'npm install lucide-react',
            'guidance': 'Strict vector iconography standards banning emojis and clipart. Use consistent strokeWidth={1.5} and semantic sizes.',
            'failure_modes': 'Never use emojis as icons (no 👟, 🛒, ⭐). Always use vector Lucide React components.',
            'code_sample': '''import { ShoppingBag, Search, SlidersHorizontal, ArrowRight, Star, Check, ShieldCheck, Zap, Layers, Activity } from 'lucide-react';

export const IconSizes = {
  badge: "w-3.5 h-3.5",
  button: "w-4 h-4",
  nav: "w-5 h-5",
  card: "w-6 h-6",
  hero: "w-8 h-8"
};'''
        },
        'clean_text_branding': {
            'id': 'clean_text_branding',
            'name': 'Clean Typographic Brand Identity & Monogram',
            'library': 'react & tailwind_css',
            'type': 'branding',
            'category': 'branding',
            'keywords': ['branding', 'logo', 'wordmark', 'monogram', 'identity', 'typography'],
            'install': 'Tailwind CSS',
            'guidance': 'Generates modern geometric monogram badge and clean tracking sans-serif wordmark when no official logo exists.',
            'failure_modes': 'Avoid random awkward clipart; geometric letter monogram always looks high-end.',
            'code_sample': '''import React from 'react';

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
}'''
        }
    }

    def search_components(self, query: str) -> List[Dict[str, Any]]:
        """Relevance-based Component Retrieval matching query keywords against SNIPPETS keywords & type."""
        q_lower = query.lower()
        results = []
        
        for key, snippet in self.SNIPPETS.items():
            score = 0
            lib = snippet.get('library', '').lower()
            snip_type = snippet.get('type', '').lower()
            name = snippet.get('name', '').lower()
            keywords = snippet.get('keywords', [key]) + [name, lib, snip_type]
            
            for kw in keywords:
                if kw and kw in q_lower:
                    score += 2
            
            if any(k in q_lower for k in ['react', 'reactbits', 'react bits', 'bits']) and 'reactbits' in key:
                score += 4
            if any(k in q_lower for k in ['card', 'spotlight', 'grid']) and 'card' in key:
                score += 3
            if any(k in q_lower for k in ['text', 'headline', 'typography', 'font']) and 'text' in snip_type:
                score += 3
            if any(k in q_lower for k in ['background', 'aurora', 'particles', 'squares']) and 'background' in snip_type:
                score += 3
            if any(k in q_lower for k in ['icon', 'lucide', 'logo', 'branding']) and ('icon' in key or 'brand' in key):
                score += 3
                
            if score > 0:
                item = snippet.copy()
                item['id'] = key
                item['score'] = score
                results.append(item)
                
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return results if results else [dict(v, id=k) for k, v in list(self.SNIPPETS.items())[:4]]

    def search_react_bits(self, query: str) -> List[Dict[str, Any]]:
        """Specialized retrieval specifically for React Bits and Lucide components."""
        matches = self.search_components(query)
        return [m for m in matches if 'reactbits' in m.get('id', '') or 'lucide' in m.get('id', '')]

    def get_purpose_matched_reactbits(self, prompt: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Returns purposefully chosen React Bits components, Lucide icons, and brand direction for the requested website."""
        p_lower = prompt.lower()
        
        # Domain Detection
        if domain:
            dom = domain.upper()
        elif any(k in p_lower for k in ['fashion', 'couture', 'velour', 'apparel', 'runway', 'atelier', 'luxury fashion', 'wardrobe']):
            dom = "EDITORIAL_FASHION"
        elif any(k in p_lower for k in ['restaurant', 'food', 'dining', 'kitchen', 'cafe', 'bistro', 'dish', 'menu', 'bakery', 'sushi', 'osteria', 'culinary', 'tasting']):
            dom = "RESTAURANT_CULINARY"
        elif any(k in p_lower for k in ['portfolio', 'agency', 'studio', 'creative', 'design agency', 'nexus creative', 'photographer', 'architect']):
            dom = "CREATIVE_AGENCY"
        elif any(k in p_lower for k in ['distributed', 'pipeline', 'streaming engine', 'telemetry', 'event stream', 'vortex', 'kafka', 'message queue', 'devtool']):
            dom = "STREAMING_DATA_DEVTOOL"
        elif any(k in p_lower for k in ['shoe', 'footwear', 'sneaker', 'kicks']):
            dom = "FOOTWEAR_SNEAKERS"
        elif any(k in p_lower for k in ['finance', 'fintech', 'crypto', 'dashboard', 'analytics', 'portfolio tracker', 'metrics']):
            dom = "FINTECH_DASHBOARD"
        elif any(k in p_lower for k in ['ai', 'tech', 'neural', 'saas', 'cloud', 'cyber', 'developer', 'terminal', 'platform', 'api']):
            dom = "AI_TECH"
        elif any(k in p_lower for k in ['shop', 'ecommerce', 'store']):
            dom = "ECOMMERCE"
        else:
            dom = "CREATIVE_AGENCY"

        matrix = {
            "EDITORIAL_FASHION": {
                "domain_name": "Editorial Fashion & Haute Couture Store",
                "background": self.SNIPPETS['reactbits_particles'],
                "background_alt": self.SNIPPETS['reactbits_aurora'],
                "hero_text": self.SNIPPETS['reactbits_blur_text'],
                "badge_text": self.SNIPPETS['reactbits_shiny_text'],
                "card": self.SNIPPETS['reactbits_tilted_card'],
                "micro_interaction": self.SNIPPETS['reactbits_shiny_text'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["ShoppingBag", "Sparkles", "SlidersHorizontal", "ArrowRight", "Eye", "Heart", "Search", "X", "Check"],
                "branding_badge": "VA"
            },
            "RESTAURANT_CULINARY": {
                "domain_name": "Artisanal Culinary & Fine Dining",
                "background": self.SNIPPETS['reactbits_aurora'],
                "background_alt": self.SNIPPETS['reactbits_particles'],
                "hero_text": self.SNIPPETS['reactbits_split_text'],
                "card": self.SNIPPETS['reactbits_tilted_card'],
                "micro_interaction": self.SNIPPETS['reactbits_star_border'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["UtensilsCrossed", "Clock", "MapPin", "Calendar", "Award", "Check", "ArrowRight", "Star", "Sparkles"],
                "branding_badge": "OT"
            },
            "CREATIVE_AGENCY": {
                "domain_name": "Creative Agency & Immersive Studio",
                "background": self.SNIPPETS['reactbits_aurora'],
                "background_alt": self.SNIPPETS['reactbits_particles'],
                "hero_text": self.SNIPPETS['reactbits_split_text'],
                "card": self.SNIPPETS['reactbits_spotlight_card'],
                "ticker": self.SNIPPETS['reactbits_infinite_scroll'],
                "micro_interaction": self.SNIPPETS['reactbits_magnet_button'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["Layers", "Palette", "Eye", "ArrowUpRight", "Compass", "Sparkles", "Menu", "X", "Zap", "Code2"],
                "branding_badge": "NX"
            },
            "STREAMING_DATA_DEVTOOL": {
                "domain_name": "High-Performance Distributed Streaming Engine",
                "background": self.SNIPPETS['reactbits_squares'],
                "background_alt": self.SNIPPETS['reactbits_hyperspeed'],
                "hero_text": self.SNIPPETS['reactbits_decrypted_text'],
                "card": self.SNIPPETS['reactbits_spotlight_card'],
                "micro_interaction": self.SNIPPETS['reactbits_star_border'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["Cpu", "Terminal", "Zap", "ShieldCheck", "Activity", "Sparkles", "ArrowRight", "Layers", "Code2", "BarChart2", "Database"],
                "branding_badge": "VF"
            },
            "AI_TECH": {
                "domain_name": "High-Tech SaaS & AI Platform",
                "background": self.SNIPPETS['reactbits_squares'],
                "background_alt": self.SNIPPETS['reactbits_hyperspeed'],
                "hero_text": self.SNIPPETS['reactbits_decrypted_text'],
                "card": self.SNIPPETS['reactbits_spotlight_card'],
                "micro_interaction": self.SNIPPETS['reactbits_star_border'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["Cpu", "Terminal", "Zap", "ShieldCheck", "Activity", "Sparkles", "ArrowRight", "Layers", "Code2"],
                "branding_badge": "AI"
            },
            "ECOMMERCE": {
                "domain_name": "High-Performance E-Commerce & Retail",
                "background": self.SNIPPETS['reactbits_particles'],
                "background_alt": self.SNIPPETS['reactbits_aurora'],
                "hero_text": self.SNIPPETS['reactbits_split_text'],
                "badge_text": self.SNIPPETS['reactbits_shiny_text'],
                "card": self.SNIPPETS['reactbits_spotlight_card'],
                "micro_interaction": self.SNIPPETS['reactbits_star_border'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["ShoppingBag", "SlidersHorizontal", "Star", "Heart", "Truck", "ArrowRight", "Search", "Check", "ShieldCheck"],
                "branding_badge": "NX"
            },
            "FOOTWEAR_SNEAKERS": {
                "domain_name": "High-Performance Footwear Studio",
                "background": self.SNIPPETS['reactbits_particles'],
                "background_alt": self.SNIPPETS['reactbits_aurora'],
                "hero_text": self.SNIPPETS['reactbits_split_text'],
                "badge_text": self.SNIPPETS['reactbits_shiny_text'],
                "card": self.SNIPPETS['reactbits_spotlight_card'],
                "micro_interaction": self.SNIPPETS['reactbits_star_border'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["ShoppingBag", "SlidersHorizontal", "Star", "Heart", "Truck", "ArrowRight", "Search", "Check", "ShieldCheck"],
                "branding_badge": "AK"
            },
            "FINTECH_DASHBOARD": {
                "domain_name": "FinTech & Enterprise Analytics",
                "background": self.SNIPPETS['reactbits_squares'],
                "background_alt": self.SNIPPETS['reactbits_aurora'],
                "hero_text": self.SNIPPETS['reactbits_blur_text'],
                "card": self.SNIPPETS['reactbits_spotlight_card'],
                "micro_interaction": self.SNIPPETS['reactbits_magnet_button'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["TrendingUp", "BarChart3", "PieChart", "Lock", "CheckCircle2", "ArrowUpRight", "SlidersHorizontal"],
                "branding_badge": "FX"
            },
            "FOOD_HOSPITALITY": {
                "domain_name": "Artisanal Hospitality & Dining",
                "background": self.SNIPPETS['reactbits_aurora'],
                "background_alt": self.SNIPPETS['reactbits_particles'],
                "hero_text": self.SNIPPETS['reactbits_split_text'],
                "card": self.SNIPPETS['reactbits_tilted_card'],
                "micro_interaction": self.SNIPPETS['reactbits_star_border'],
                "button": self.SNIPPETS['reactbits_magnet_button'],
                "stats": self.SNIPPETS['reactbits_count_up'],
                "lucide_icons": ["UtensilsCrossed", "Clock", "MapPin", "Calendar", "Award", "Check", "ArrowRight", "Star"],
                "branding_badge": "OT"
            }
        }

        selected_plan = matrix.get(dom, matrix["CREATIVE_AGENCY"])
        return {
            "domain": dom,
            "domain_name": selected_plan["domain_name"],
            "selected_components": {
                "background": selected_plan["background"]["name"],
                "background_code": selected_plan["background"]["code_sample"],
                "hero_text": selected_plan["hero_text"]["name"],
                "hero_text_code": selected_plan["hero_text"]["code_sample"],
                "card": selected_plan["card"]["name"],
                "card_code": selected_plan["card"]["code_sample"],
                "button": selected_plan["button"]["name"],
                "button_code": selected_plan["button"]["code_sample"],
                "micro_interaction": selected_plan["micro_interaction"]["name"],
                "micro_interaction_code": selected_plan["micro_interaction"]["code_sample"],
                "stats": selected_plan["stats"]["name"],
                "stats_code": selected_plan["stats"]["code_sample"]
            },
            "lucide_icons": selected_plan["lucide_icons"],
            "branding_badge": selected_plan["branding_badge"],
            "anti_patterns": [
                "NEVER use emojis (👟, 🛒, 🍔, ⭐, 🚀) as UI icons or graphics",
                "NEVER use mismatched random SVG stickers or awkward third-party logos",
                "Always use Lucide React icons with consistent sizing (w-4 h-4, w-5 h-5)",
                "Always generate a clean text-based brand mark with geometric monogram when no logo exists",
                "Match animations to the product purpose (do not reuse the same layout for every site)"
            ]
        }

    def format_component_prompt(self, components: List[Dict[str, Any]]) -> str:
        """Formats retrieved component snippets into complete, actionable prompt instructions for the LLM."""
        lines = ["[MATCHED REACT BITS & MOTION IMPLEMENTATION RECIPES]"]
        for c in components:
            lines.append(f"### Recipe: {c['name']} ({c['library']})")
            lines.append(f"Install: {c.get('install', 'N/A')}")
            lines.append(f"Guidance: {c.get('guidance', 'N/A')}")
            lines.append(f"Failure Mode Handling: {c.get('failure_modes', 'N/A')}")
            lines.append("Code Example:")
            lines.append("```jsx")
            lines.append(c.get('code_sample', ''))
            lines.append("```\n")
        return "\n".join(lines)

    def get_targeted_component_specs(self, user_prompt: str) -> str:
        """Retrieves authentic, un-truncated documentation, exact props, dependencies, and implementation examples for purpose-matched React Bits components."""
        rb_plan = self.get_purpose_matched_reactbits(user_prompt)
        selected_comps = rb_plan.get("selected_components", {})
        dom_name = rb_plan.get("domain_name", "Web Application")
        badge = rb_plan.get("branding_badge", "NX")
        lucide_list = ", ".join(rb_plan.get("lucide_icons", ["ShoppingBag", "ArrowRight", "Search", "Star"]))

        lines = [
            f"[AUTHENTIC REACT BITS ARCHITECTURE SPECIFICATION: {dom_name.upper()}]",
            f"Selected Domain Archetype: {dom_name}",
            f"Recommended Monogram Badge: '{badge}'",
            f"Harmonized Lucide Icons: {lucide_list}",
            "",
            "### Standard Package Dependencies (package.json):",
            "```json",
            "\"dependencies\": {",
            "  \"react\": \"^18.3.1\",",
            "  \"react-dom\": \"^18.3.1\",",
            "  \"lucide-react\": \"^0.469.0\",",
            "  \"framer-motion\": \"^11.15.0\",",
            "  \"clsx\": \"^2.1.1\",",
            "  \"tailwind-merge\": \"^2.6.0\"",
            "}",
            "```",
            "",
            "### Strict Implementation Guidelines:",
            "1. NEVER invent component APIs or props. Use only the exact props documented below.",
            "2. ZERO-EMOJI RULE: NEVER use emoji characters (👟, 🛒, 🍔, ⭐, 🚀) as UI icons or graphics. Use vector Lucide React SVGs.",
            "3. Clean Text Branding: When no official logo exists, generate a typographic wordmark with a geometric monogram badge.",
            "4. Component Directory: Place React Bits component implementations in `src/components/reactbits/`.",
            "",
            "### Selected Purpose-Matched Components & Verified APIs:"
        ]

        # Gather snippets for the selected components
        comp_keys = []
        p_lower = user_prompt.lower()
        if "spotlight" in selected_comps.get("card", "").lower():
            comp_keys.append("reactbits_spotlight_card")
        elif "tilted" in selected_comps.get("card", "").lower():
            comp_keys.append("reactbits_tilted_card")
        else:
            comp_keys.append("reactbits_spotlight_card")

        if "aurora" in selected_comps.get("background", "").lower():
            comp_keys.append("reactbits_aurora")
        elif "squares" in selected_comps.get("background", "").lower():
            comp_keys.append("reactbits_squares")
        elif "particles" in selected_comps.get("background", "").lower():
            comp_keys.append("reactbits_particles")
        elif "hyperspeed" in selected_comps.get("background", "").lower():
            comp_keys.append("reactbits_hyperspeed")
        else:
            comp_keys.append("reactbits_aurora")

        if "decrypted" in selected_comps.get("hero_text", "").lower():
            comp_keys.append("reactbits_decrypted_text")
        elif "split" in selected_comps.get("hero_text", "").lower():
            comp_keys.append("reactbits_split_text")
        elif "blur" in selected_comps.get("hero_text", "").lower():
            comp_keys.append("reactbits_blur_text")
        else:
            comp_keys.append("reactbits_split_text")

        comp_keys.append("reactbits_magnet_button")
        comp_keys.append("reactbits_count_up")

        # Deduplicate while preserving order
        seen = set()
        unique_keys = []
        for k in comp_keys:
            if k not in seen and k in self.SNIPPETS:
                seen.add(k)
                unique_keys.append(k)

        for k in unique_keys:
            snip = self.SNIPPETS[k]
            lines.append(f"\n#### Component: `{snip['name']}` ({snip['category']})")
            lines.append(f"- **Import Location**: `src/components/reactbits/{snip['id'].replace('reactbits_', '').title().replace('_', '')}.jsx`")
            lines.append(f"- **Requirements / Install**: {snip.get('install', 'Tailwind CSS')}")
            lines.append(f"- **Guidance**: {snip.get('guidance', 'N/A')}")
            lines.append(f"- **Failure Mode Caution**: {snip.get('failure_modes', 'N/A')}")
            lines.append("- **Canonical Verified Source Code**:")
            lines.append("```jsx")
            lines.append(snip.get('code_sample', ''))
            lines.append("```")

        return "\n".join(lines)

