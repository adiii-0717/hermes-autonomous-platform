"""
Domain Template: Luxury Editorial Atelier & Avant-Garde Studio
Inspired by Mariana & Zenrixa Benchmarks.
Features:
- Deep Royal Crimson (#1A050B) & Rose Gold (#E8B4A2) Atelier with dramatic condensed typography
- Editorial portraiture layered with botanical motifs and luxury seals
- 5-Step Strategic Methodology & Translucent Value Metric Cards
- High-Fashion Client Case Studies & Conversion Footers
- Pure vector Lucide icons, zero emojis.
"""

def generate_luxury_atelier_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''import React, { useState } from 'react';
import { 
  Sparkles, ArrowRight, ArrowUpRight, Compass, 
  Layers, SlidersHorizontal, Check, X, Eye, 
  Heart, Share2, Award, Star, Flower2, Shield,
  ChevronRight, Calendar, Mail, Instagram, MapPin
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { SplitText } from './components/reactbits/SplitText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [selectedCase, setSelectedCase] = useState(null);
  const [bookingOpen, setBookingOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all');

  const caseStudies = [
    {
      id: 'case-1',
      title: "NOIRÉ COSMETICS",
      category: "Branding · Packaging",
      year: "2025",
      impact: "+240% Direct Sales",
      image: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&q=80&w=900",
      description: "A bold luxury beauty brand with timeless Parisian elegance, obsidian glass packaging, and gold-foiled typography.",
      deliverables: ["Visual Identity", "Custom Glass Bottles", "E-Commerce Experience", "Packaging Guidelines"]
    },
    {
      id: 'case-2',
      title: "ELYSIUM STUDIO",
      category: "Branding · Web Design",
      year: "2026",
      impact: "Awwwards Site of the Day",
      image: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&q=80&w=900",
      description: "Minimalist floral atelier branding marrying warm nude paper stocks, debossed monogram seals, and editorial typography.",
      deliverables: ["Creative Direction", "Editorial Lookbook", "Interactive Catalog"]
    },
    {
      id: 'case-3',
      title: "VELLORA JEWELRY",
      category: "Branding · E-Commerce",
      year: "2025",
      impact: "€1.8M Launch Volume",
      image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&q=80&w=900",
      description: "Heritage high jewelry identity with deep burgundy velvet boxes, filigree gold seals, and an intimate digital boutique.",
      deliverables: ["Full Brand System", "Custom Monogram", "E-Commerce Storefront"]
    },
    {
      id: 'case-4',
      title: "AUREA WELLNESS",
      category: "Branding · Web Design",
      year: "2026",
      impact: "+380% Membership Growth",
      image: "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&q=80&w=900",
      description: "A sanctuary wellness brand promoting balance, holistic beauty, and organic botanical self-care.",
      deliverables: ["Sensory Identity", "Spatial Signage", "Member Web App"]
    }
  ];

  const processSteps = [
    { num: "01", name: "DISCOVER", desc: "I learn about your brand, goals, and audience to establish creative conviction." },
    { num: "02", name: "STRATEGIZE", desc: "I create a clear aesthetic and market positioning plan tailored to your domain." },
    { num: "03", name: "DESIGN", desc: "I bring your brand to life with intentional, impactful typography and art direction." },
    { num: "04", name: "REFINE", desc: "We collaborate closely to polish every texture, transition, and detail until perfect." },
    { num: "05", name: "DELIVER", desc: "You receive comprehensive assets, guidelines, and an unforgettable digital presence." }
  ];

  const filteredCases = activeFilter === 'all' 
    ? caseStudies 
    : caseStudies.filter(c => c.category.includes(activeFilter));

  return (
    <div className="min-h-screen bg-[#140409] text-[#FDFBF7] font-sans selection:bg-[#E8B4A2] selection:text-[#140409] relative overflow-x-hidden antialiased">
      
      {/* Top Header */}
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-[#140409]/90 border-b border-[#E8B4A2]/15 px-6 lg:px-16 py-5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full border border-[#E8B4A2]/40 bg-[#280812] flex items-center justify-center text-[#E8B4A2] font-serif font-bold text-base shadow-lg">
              __BADGE_LETTER__
            </div>
            <div>
              <span className="font-serif font-bold text-lg tracking-widest text-[#FDFBF7] block uppercase">
                __BRAND_NAME__
              </span>
              <span className="text-[9px] font-mono tracking-[0.25em] text-[#E8B4A2] uppercase block">
                LUXURY BRAND DESIGN ATELIER
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-xs font-mono tracking-widest uppercase text-zinc-400">
            <a href="#about" className="hover:text-[#E8B4A2] transition-colors">About</a>
            <a href="#work" className="hover:text-[#E8B4A2] transition-colors">Featured Work</a>
            <a href="#process" className="hover:text-[#E8B4A2] transition-colors">Methodology</a>
            <a href="#contact" className="hover:text-[#E8B4A2] transition-colors">Contact</a>
          </nav>

          <Magnet strength={0.3}>
            <button 
              onClick={() => setBookingOpen(true)}
              className="bg-[#280812] hover:bg-[#E8B4A2] text-[#E8B4A2] hover:text-[#140409] border border-[#E8B4A2]/40 px-6 py-2.5 rounded-full font-mono text-xs uppercase tracking-widest font-semibold transition-all shadow-md flex items-center gap-2"
            >
              <span>Let's Talk</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </Magnet>
        </div>
      </header>

      {/* Hero Section: Mariana Benchmark Composition */}
      <section className="relative pt-12 pb-24 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#E8B4A2]/15">
        
        {/* Ambient Crimson Glow */}
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#4A0D1E]/40 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          
          {/* Left Hero Column: Monumental Condensed Serif Display */}
          <div className="lg:col-span-7 space-y-6 z-10">
            <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E8B4A2] font-semibold flex items-center gap-2">
              <Flower2 className="w-4 h-4 text-[#E8B4A2]" />
              BRANDING · WEB DESIGN · DIGITAL EXPERIENCES
            </span>

            <div className="py-2">
              <h1 className="text-4xl sm:text-6xl lg:text-7xl font-serif font-black tracking-tight text-[#FDFBF7] uppercase leading-[1.02]">
                I Design <br />
                <span className="text-[#E8B4A2] italic font-serif">Brands</span> <br />
                That Stand Out.
              </h1>
            </div>

            <p className="text-base sm:text-lg text-zinc-300 font-light max-w-lg leading-relaxed">
              I help ambitious founders and visionary creators turn ideas into magnetic brand identities that elevate perception, command respect, and convert.
            </p>

            <div className="pt-4 flex flex-wrap items-center gap-5">
              <Magnet strength={0.3}>
                <button 
                  onClick={() => setBookingOpen(true)}
                  className="bg-[#E8B4A2] hover:bg-[#D89F8B] text-[#140409] px-8 py-4 rounded-full font-mono text-xs uppercase tracking-[0.2em] font-bold transition-all shadow-xl shadow-[#E8B4A2]/20 flex items-center gap-3"
                >
                  View Work <ArrowRight className="w-4 h-4" />
                </button>
              </Magnet>
              <button 
                onClick={() => setBookingOpen(true)}
                className="border border-[#E8B4A2]/30 hover:border-[#E8B4A2] text-zinc-200 hover:text-white px-7 py-4 rounded-full font-mono text-xs uppercase tracking-widest transition-all"
              >
                Inquire For 2026
              </button>
            </div>
          </div>

          {/* Right Hero Column: Editorial Portraiture & Luxury Seal Layering */}
          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md">
              
              {/* Circular Luxury Brand Seal Stamp (Mariana Signature) */}
              <div className="absolute -top-6 -right-6 z-20 w-24 h-24 rounded-full border border-[#E8B4A2]/40 bg-[#280812]/90 backdrop-blur-md flex flex-col items-center justify-center p-2 text-center shadow-xl animate-spin-slow">
                <Sparkles className="w-4 h-4 text-[#E8B4A2] mb-0.5" />
                <span className="text-[8px] font-mono uppercase tracking-widest text-[#E8B4A2] font-bold leading-tight">
                  DESIGN WITH PURPOSE
                </span>
              </div>

              {/* Main Portrait Frame with Dark Wine Vignette */}
              <div className="relative rounded-3xl overflow-hidden border border-[#E8B4A2]/25 shadow-2xl bg-[#280812]">
                <img 
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=900" 
                  alt="Creative Director" 
                  className="w-full h-[500px] object-cover" 
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#140409] via-transparent to-transparent"></div>

                <div className="absolute bottom-6 left-6 right-6 text-center">
                  <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E8B4A2] block">
                    MARÍANA STUDIO // WARSAW & PARIS
                  </span>
                  <p className="text-sm font-serif italic text-white/90 mt-1">
                    "Strategy meets artistic intention."
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About & Value Props Section: 3 Translucent Wine Cards */}
      <section id="about" className="py-20 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#E8B4A2]/15">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-5 space-y-4">
            <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E8B4A2] font-semibold">
              // ABOUT THE ATELIER
            </span>
            <h2 className="text-3xl sm:text-5xl font-serif font-bold text-[#FDFBF7] leading-tight">
              Strategy Meets <br />
              <span className="italic text-[#E8B4A2]">Creativity.</span>
            </h2>
            <p className="text-sm text-zinc-300 font-light leading-relaxed pt-2">
              I'm Mariana, a brand designer passionate about creating meaningful, visually captivating identities. I help businesses turn vision into assets that resonate deeply and convert.
            </p>
            <div className="pt-2">
              <button 
                onClick={() => setBookingOpen(true)}
                className="inline-flex items-center gap-2 text-xs font-mono text-[#E8B4A2] uppercase tracking-wider font-bold hover:underline"
              >
                <span>Read Full Philosophy</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="p-8 rounded-2xl bg-[#280812]/70 border border-[#E8B4A2]/20 shadow-xl space-y-3">
              <Sparkles className="w-6 h-6 text-[#E8B4A2]" />
              <div className="text-3xl font-serif font-bold text-white flex items-center">
                <CountUp to={5} duration={1.8} />+
              </div>
              <h4 className="text-xs font-mono uppercase tracking-widest text-[#E8B4A2] font-bold">Years Experience</h4>
              <p className="text-xs text-zinc-300 font-light">
                Crafting bespoke brands and digital experiences that make an impact.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-[#280812]/70 border border-[#E8B4A2]/20 shadow-xl space-y-3">
              <Award className="w-6 h-6 text-[#E8B4A2]" />
              <div className="text-3xl font-serif font-bold text-white flex items-center">
                <CountUp to={100} duration={2.2} />+
              </div>
              <h4 className="text-xs font-mono uppercase tracking-widest text-[#E8B4A2] font-bold">Projects Delivered</h4>
              <p className="text-xs text-zinc-300 font-light">
                From luxury startups to established global brands that scale.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-[#280812]/70 border border-[#E8B4A2]/20 shadow-xl space-y-3">
              <Heart className="w-6 h-6 text-[#E8B4A2]" />
              <div className="text-3xl font-serif font-bold text-white flex items-center">
                <CountUp to={98} duration={2.0} />%
              </div>
              <h4 className="text-xs font-mono uppercase tracking-widest text-[#E8B4A2] font-bold">Retention Rate</h4>
              <p className="text-xs text-zinc-300 font-light">
                Ongoing creative partnerships and global design advisory.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Works 4-Column Showcase */}
      <section id="work" className="py-20 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#E8B4A2]/15">
        <div className="flex justify-between items-end pb-12 border-b border-[#E8B4A2]/15">
          <div>
            <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E8B4A2] font-bold">
              // FEATURED COMMISSIONS
            </span>
            <h2 className="text-3xl sm:text-5xl font-serif font-bold text-white mt-2">
              Selected Atelier Works
            </h2>
          </div>
          <span className="text-xs font-mono text-zinc-400">
            SHOWCASING 4 MASTERPIECES
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-12">
          {caseStudies.map((work) => (
            <SpotlightCard 
              key={work.id}
              className="bg-[#280812]/60 border border-[#E8B4A2]/20 hover:border-[#E8B4A2]/60 transition-all rounded-2xl overflow-hidden group cursor-pointer flex flex-col justify-between shadow-lg"
              spotlightColor="rgba(232, 180, 162, 0.12)"
              onClick={() => setSelectedCase(work)}
            >
              <div>
                <div className="overflow-hidden relative h-64 border-b border-[#E8B4A2]/15">
                  <img 
                    src={work.image} 
                    alt={work.title} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" 
                  />
                  <div className="absolute top-3 right-3 bg-[#140409]/80 backdrop-blur-md px-2.5 py-0.5 rounded-full text-[10px] font-mono text-[#E8B4A2]">
                    {work.year}
                  </div>
                </div>

                <div className="p-6 space-y-2">
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#E8B4A2]">
                    {work.category}
                  </span>
                  <h3 className="text-xl font-serif font-bold text-white group-hover:text-[#E8B4A2] transition-colors">
                    {work.title}
                  </h3>
                  <p className="text-xs text-zinc-300 font-light line-clamp-2">
                    {work.description}
                  </p>
                </div>
              </div>

              <div className="p-6 pt-0">
                <div className="pt-4 border-t border-[#E8B4A2]/15 flex justify-between items-center text-xs font-mono text-zinc-400">
                  <span className="text-[#E8B4A2] font-semibold">{work.impact}</span>
                  <span className="text-white flex items-center gap-1 group-hover:text-[#E8B4A2]">
                    View <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            </SpotlightCard>
          ))}
        </div>
      </section>

      {/* 5-Step Methodology Timeline (Mariana Benchmark) */}
      <section id="process" className="py-20 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#E8B4A2]/15">
        <div className="max-w-2xl mb-16">
          <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E8B4A2] font-bold">
            // DESIGN METHODOLOGY
          </span>
          <h2 className="text-3xl sm:text-5xl font-serif font-bold text-white mt-2">
            The 5-Step Strategic Journey
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          {processSteps.map((step) => (
            <div key={step.num} className="p-6 bg-[#280812]/50 border border-[#E8B4A2]/15 rounded-2xl space-y-3">
              <span className="text-2xl font-serif font-bold text-[#E8B4A2] block">
                {step.num}
              </span>
              <h4 className="text-sm font-mono uppercase tracking-widest text-white font-bold">
                {step.name}
              </h4>
              <p className="text-xs text-zinc-300 font-light leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* High-Converting Footer Banner: Mariana Signature */}
      <section id="contact" className="py-20 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="rounded-3xl bg-gradient-to-r from-[#280812] via-[#3D0C1C] to-[#280812] border border-[#E8B4A2]/25 p-10 lg:p-16 shadow-2xl relative overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-7 space-y-4">
              <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E8B4A2] font-bold">
                // INITIATE COMMISSION
              </span>
              <h2 className="text-3xl sm:text-5xl font-serif font-bold text-white">
                Ready to elevate <br />
                <span className="italic text-[#E8B4A2]">your brand?</span>
              </h2>
              <p className="text-sm text-zinc-300 font-light max-w-md">
                Let's create something beautiful, strategic, and unforgettable for the decade ahead.
              </p>
              <div className="pt-2">
                <Magnet strength={0.3}>
                  <button 
                    onClick={() => setBookingOpen(true)}
                    className="bg-[#E8B4A2] hover:bg-[#D89F8B] text-[#140409] px-8 py-4 rounded-full font-mono text-xs uppercase tracking-widest font-bold transition-all shadow-xl shadow-[#E8B4A2]/20 flex items-center gap-3"
                  >
                    Let's Work Together <ArrowRight className="w-4 h-4" />
                  </button>
                </Magnet>
              </div>
            </div>

            <div className="lg:col-span-5 space-y-3 font-mono text-xs text-zinc-300 border-t lg:border-t-0 lg:border-l border-[#E8B4A2]/20 pt-6 lg:pt-0 lg:pl-10">
              <div className="flex items-center gap-3">
                <Mail className="w-4 h-4 text-[#E8B4A2]" />
                <span>hello@marianaatelier.studio</span>
              </div>
              <div className="flex items-center gap-3">
                <Instagram className="w-4 h-4 text-[#E8B4A2]" />
                <span>@mariana.designstudio</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-4 h-4 text-[#E8B4A2]" />
                <span>Warsaw · Paris · Zurich</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Case Study Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
          <div className="bg-[#140409] border border-[#E8B4A2]/30 max-w-2xl w-full p-8 rounded-3xl shadow-2xl relative text-white max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setSelectedCase(null)} 
              className="absolute top-6 right-6 p-2 text-zinc-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-6">
              <div>
                <span className="text-xs font-mono uppercase tracking-widest text-[#E8B4A2]">
                  {selectedCase.category} · {selectedCase.year}
                </span>
                <h3 className="text-3xl font-serif font-bold mt-1">{selectedCase.title}</h3>
                <div className="text-xs font-mono text-[#E8B4A2] mt-1 font-bold">{selectedCase.impact}</div>
              </div>

              <div className="overflow-hidden rounded-2xl h-80 border border-[#E8B4A2]/20">
                <img src={selectedCase.image} alt={selectedCase.title} className="w-full h-full object-cover" />
              </div>

              <p className="text-sm text-zinc-300 leading-relaxed font-light">
                {selectedCase.description}
              </p>

              <div className="p-4 bg-[#280812] rounded-xl border border-[#E8B4A2]/20 text-xs font-mono space-y-1">
                <div className="text-[#E8B4A2] font-bold">Deliverables:</div>
                <div className="text-zinc-300">{selectedCase.deliverables.join(" · ")}</div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button 
                  onClick={() => setSelectedCase(null)} 
                  className="px-5 py-2.5 font-mono text-xs uppercase text-zinc-400"
                >
                  Close
                </button>
                <button 
                  onClick={() => { setSelectedCase(null); setBookingOpen(true); }}
                  className="bg-[#E8B4A2] text-[#140409] px-7 py-3 rounded-full font-mono text-xs uppercase tracking-widest font-bold"
                >
                  Request Similar Project
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {bookingOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
          <div className="bg-[#140409] border border-[#E8B4A2]/30 max-w-lg w-full p-8 rounded-3xl shadow-2xl relative text-white">
            <button 
              onClick={() => setBookingOpen(false)} 
              className="absolute top-6 right-6 p-2 text-zinc-400 hover:text-white"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-4">
              <span className="text-xs font-mono uppercase tracking-widest text-[#E8B4A2] font-bold">
                // PROJECT INQUIRY 2026
              </span>
              <h3 className="text-2xl font-serif font-bold">Let's Work Together</h3>
              <p className="text-xs text-zinc-400 font-mono">
                Currently booking brand identity and digital experience commissions.
              </p>

              <div className="space-y-3 pt-2">
                <input 
                  type="text" 
                  placeholder="Your Name & Brand" 
                  className="w-full px-4 py-3 rounded-xl bg-[#280812] border border-[#E8B4A2]/20 text-sm text-white focus:outline-none focus:border-[#E8B4A2]" 
                />
                <input 
                  type="email" 
                  placeholder="Direct Email Address" 
                  className="w-full px-4 py-3 rounded-xl bg-[#280812] border border-[#E8B4A2]/20 text-sm text-white focus:outline-none focus:border-[#E8B4A2]" 
                />
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button onClick={() => setBookingOpen(false)} className="px-5 py-2.5 font-mono text-xs uppercase text-zinc-400">
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    alert('Inquiry received. Mariana will contact you within 24 hours.');
                    setBookingOpen(false);
                  }}
                  className="bg-[#E8B4A2] text-[#140409] px-7 py-3 rounded-full font-mono text-xs uppercase tracking-widest font-bold"
                >
                  Send Inquiry
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="py-12 px-6 text-center text-xs font-mono text-zinc-500 border-t border-[#E8B4A2]/15">
        <p>© 2026 __BRAND_NAME__. All branding rights reserved. Warsaw · Paris · Zurich.</p>
      </footer>
    </div>
  );
}
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_luxury_atelier_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Luxury Brand Design Atelier</title>
  
  <!-- Google Fonts: Playfair Display & Plus Jakarta Sans & Space Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;0,900;1,600;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'bg-crimson': '#140409',
            'accent-rose': '#E8B4A2',
            'wine-surface': '#280812'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            serif: ['"Playfair Display"', 'serif'],
            mono: ['"Space Mono"', 'monospace']
          }
        }
      }
    };
  </script>

  <!-- Lucide Vector Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-[#140409] text-[#FDFBF7] antialiased">
  <div id="root">
    <div class="min-h-screen bg-[#140409] p-8 text-white">
      <header class="max-w-7xl mx-auto flex justify-between items-center py-4 border-b border-[#E8B4A2]/20">
        <span class="font-serif font-bold text-xl tracking-wider text-[#E8B4A2]">__BRAND_NAME__</span>
        <button class="bg-[#E8B4A2] text-[#140409] font-mono text-xs px-6 py-2.5 rounded-full uppercase tracking-widest font-bold">
          Let's Talk
        </button>
      </header>
      <section class="max-w-7xl mx-auto mt-12">
        <h1 class="text-4xl sm:text-6xl font-serif font-black uppercase text-white leading-tight">
          I Design Brands That Stand Out.
        </h1>
        <p class="text-base text-zinc-300 mt-4 max-w-lg">
          I help businesses turn vision into magnetic assets that convert.
        </p>
      </section>
    </div>
  </div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)
