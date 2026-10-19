"""
Domain Template: Sculptural Luxury Furniture & Tactile Interior Objects
Inspired by Formora & Simply Benchmarks.
Features:
- Vibrant Terracotta & Ochre Sculptural Craft OR Deep Burgundy Velvet & Oatmeal Comfort
- Monumental hero products breaking out of container boundaries
- Floating vertical product selector cards & tactile material specimens
- Multi-tier editorial arguments & telemetry stats
- Authentic interior photography, Lucide vector icons, zero emojis.
"""

def generate_sculptural_furniture_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''import React, { useState } from 'react';
import { 
  Sparkles, ArrowRight, ArrowUpRight, Compass, 
  Layers, SlidersHorizontal, Check, X, Eye, 
  Heart, Share2, Ruler, Shield, Plus, ChevronRight,
  Maximize2, Award, CircleDot, Info
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { SplitText } from './components/reactbits/SplitText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [orderModalOpen, setOrderModalOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedFinish, setSelectedFinish] = useState('Burnt Ochre Velvet');
  const [customizerOpen, setCustomizerOpen] = useState(false);

  const heroPiece = {
    id: 'hero-1',
    name: "AUREA HONEYCOMB COCOON",
    tagline: "Attraction points for spaces that are memorable",
    category: "Lounge Chairs",
    year: "2026 Collection",
    price: "$4,850",
    dimensions: "112cm × 98cm × 84cm",
    weight: "34 kg",
    leadTime: "4 Weeks Made-to-Order",
    materials: "Cellular Quilted Velvet · Solid Walnut Plinth",
    image: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&q=80&w=1200",
    description: "A monumental sculptural lounge chair engineered with ergonomic cellular honeycomb quilting. Conceived to act as the undeniable gravitational anchor in high-volume public lobbies and private executive residences."
  };

  const catalog = [
    {
      id: 'furn-1',
      name: "VERTA MONOLITH ARMCHAIR",
      series: "Series 01 // Terracotta",
      category: "Armchairs",
      price: "$3,620",
      finish: "Burnt Ochre Velvet",
      image: "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&q=80&w=1000",
      description: "Low-center curved cocoon chair wrapped in Italian brushed wool, cradled by hand-turned smoked oak legs.",
      specs: { foam: "High-Resilience Bio-Latex", frame: "FSC Smoked Oak", rubCount: "100,000 Martindale" }
    },
    {
      id: 'furn-2',
      name: "DIANA SCULPTURAL WAVE",
      series: "Series 02 // Burgundy",
      category: "Lounge Chairs",
      price: "$4,150",
      finish: "Deep Plum Velvet",
      image: "https://images.unsplash.com/photo-1592078615290-033ee584e267?auto=format&fit=crop&q=80&w=1000",
      description: "Continuous serpentine silhouette offering continuous lumbar relief and tactile, light-absorbing velvet upholstery.",
      specs: { foam: "Dual-Density Polycore", frame: "Reinforced Steel Webbing", rubCount: "120,000 Martindale" }
    },
    {
      id: 'furn-3',
      name: "CRESTA CONTOUR DINING CHAIR",
      series: "Series 03 // Smoked Sand",
      category: "Chairs",
      price: "$1,890",
      finish: "Oatmeal Bouclé",
      image: "https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&q=80&w=1000",
      description: "Ergonomic dining chair featuring a cradling half-moon backrest and micro-stitched linen welt detailing.",
      specs: { foam: "Molded Memory Foam", frame: "Matte Black Steel", rubCount: "80,000 Martindale" }
    },
    {
      id: 'furn-4',
      name: "ORBITA SECTIONAL CURVE",
      series: "Series 04 // Natural Ochre",
      category: "Sofas",
      price: "$8,900",
      finish: "Cognac Full-Grain Leather",
      image: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&q=80&w=1000",
      description: "A sweeping 3.8-meter radial sofa designed for conversation in open architectural spaces.",
      specs: { foam: "Down-Layered Core", frame: "Kiln-Dried European Beech", rubCount: "Natural Patina" }
    }
  ];

  const materialSwatches = [
    { name: "Burnt Ochre Velvet", origin: "Como, Italy", texture: "Heavy-pile cotton velvet with deep amber refractions" },
    { name: "Deep Plum Bouclé", origin: "Lyon, France", texture: "Looped wool and mohair blend with three-dimensional grain" },
    { name: "Smoked Native Oak", origin: "Black Forest, Germany", texture: "Fumed matte wood with open-pore wax seal" },
    { name: "Navona Travertine", origin: "Tivoli, Italy", texture: "Honed vein-cut limestone with unfilled natural voids" }
  ];

  const filteredCatalog = activeCategory === 'all' 
    ? catalog 
    : catalog.filter(c => c.category === activeCategory);

  return (
    <div className="min-h-screen bg-[#FFF8F0] text-[#191716] font-sans selection:bg-[#E85A2A] selection:text-[#FFF8F0] relative overflow-x-hidden antialiased">
      
      {/* Top Banner Ticker */}
      <div className="bg-[#191716] text-[#FFF8F0] px-6 lg:px-16 py-2.5 text-xs font-mono tracking-widest flex justify-between items-center border-b border-white/10">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#E85A2A] animate-pulse"></span>
          __BRAND_NAME__ // BESPOKE SCULPTURAL FURNITURE 2026
        </span>
        <span className="hidden md:inline">ZÜRICH · MILAN · COPENHAGEN · NEW YORK</span>
        <span className="font-semibold text-[#E85A2A]">LIMITED EDITION PIECES</span>
      </div>

      {/* Main Header */}
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-[#FFF8F0]/90 border-b border-[#191716]/10 px-6 lg:px-16 py-5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-sm bg-[#E85A2A] text-white font-serif font-black text-xl flex items-center justify-center shadow-lg">
              __BADGE_LETTER__
            </div>
            <div>
              <span className="font-serif font-black text-xl tracking-tight text-[#191716] block uppercase">
                __BRAND_NAME__
              </span>
              <span className="text-[10px] font-mono tracking-[0.2em] text-[#8C7E72] uppercase block">
                SCULPTURAL INTERIOR ATELIER
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-xs font-mono tracking-widest uppercase text-[#8C7E72]">
            <button onClick={() => setActiveCategory('all')} className={`hover:text-[#191716] transition-colors pb-1 ${activeCategory === 'all' ? 'text-[#E85A2A] font-bold border-b-2 border-[#E85A2A]' : ''}`}>
              All Pieces
            </button>
            <button onClick={() => setActiveCategory('Armchairs')} className={`hover:text-[#191716] transition-colors pb-1 ${activeCategory === 'Armchairs' ? 'text-[#E85A2A] font-bold border-b-2 border-[#E85A2A]' : ''}`}>
              Armchairs
            </button>
            <button onClick={() => setActiveCategory('Chairs')} className={`hover:text-[#191716] transition-colors pb-1 ${activeCategory === 'Chairs' ? 'text-[#E85A2A] font-bold border-b-2 border-[#E85A2A]' : ''}`}>
              Dining Chairs
            </button>
            <button onClick={() => setActiveCategory('Sofas')} className={`hover:text-[#191716] transition-colors pb-1 ${activeCategory === 'Sofas' ? 'text-[#E85A2A] font-bold border-b-2 border-[#E85A2A]' : ''}`}>
              Sectionals
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <Magnet strength={0.3}>
              <button 
                onClick={() => setOrderModalOpen(true)}
                className="bg-[#191716] hover:bg-[#E85A2A] text-white px-6 py-3 font-mono text-xs uppercase tracking-widest font-bold transition-all shadow-md flex items-center gap-2"
              >
                <span>Acquire Piece</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </Magnet>
          </div>
        </div>
      </header>

      {/* Hero Section: Monumental Formora-Style Sculptural Hero */}
      <section className="pt-8 sm:pt-12 pb-24 px-4 sm:px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="relative rounded-[24px] sm:rounded-[32px] bg-gradient-to-br from-[#F4ECE1] via-[#EFE5D8] to-[#E5D7C3] border border-[#191716]/10 p-6 sm:p-12 lg:p-16 overflow-hidden shadow-2xl">
          
          {/* Top Decorative Subheader */}
          <div className="flex flex-wrap justify-between items-center pb-6 sm:pb-8 border-b border-[#191716]/10 text-xs font-mono uppercase tracking-[0.2em] text-[#8C7E72] gap-4">
            <span>CUSTOM-MADE FOR THE PROJECT</span>
            <span className="text-[#E85A2A] font-bold">★ WOW EFFECT WITHOUT LOSS OF FUNCTION ★</span>
            <span>FROM IDEA TO INSTALLATION</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center pt-8">
            
            {/* Left Content Column */}
            <div className="lg:col-span-6 space-y-6 z-10">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#E85A2A]/10 border border-[#E85A2A]/20 text-[11px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>SIGNATURE SCULPTURAL ATTRACTION</span>
              </div>

              <div className="py-2">
                <SplitText 
                  text="ATTRACTION POINTS FOR SPACES THAT ARE MEMORABLE" 
                  delay={0.03} 
                  className="text-lg sm:text-3xl md:text-5xl lg:text-6xl font-serif font-black tracking-normal sm:tracking-tight text-[#191716] uppercase leading-snug break-words"
                />
              </div>

              <p className="text-base sm:text-lg text-[#5E5A54] max-w-md font-light leading-relaxed">
                In the premium segment, invisibility costs more than boldness. We forge tactile seating monoliths designed to provoke contemplation, tactile interaction, and permanent aesthetic delight.
              </p>

              <div className="pt-4 flex flex-wrap items-center gap-4">
                <Magnet strength={0.3}>
                  <button 
                    onClick={() => { setSelectedPiece(heroPiece); setOrderModalOpen(true); }}
                    className="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-8 py-4 font-mono text-xs uppercase tracking-[0.2em] font-bold transition-all shadow-xl shadow-[#E85A2A]/25 flex items-center gap-3"
                  >
                    Reserve Honeycomb Cocoon <ArrowRight className="w-4 h-4" />
                  </button>
                </Magnet>
                <button 
                  onClick={() => setSelectedPiece(heroPiece)}
                  className="border border-[#191716]/20 hover:border-[#191716] text-[#191716] px-6 py-4 font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/50"
                >
                  Inspect Specifications
                </button>
              </div>

              <div className="pt-8 grid grid-cols-3 gap-6 border-t border-[#191716]/10 text-xs font-mono">
                <div>
                  <span className="text-[#8C7E72] block">Pricing:</span>
                  <span className="font-bold text-lg text-[#191716]">{heroPiece.price}</span>
                </div>
                <div>
                  <span className="text-[#8C7E72] block">Handcrafting:</span>
                  <span className="font-bold text-lg text-[#E85A2A]">4 Weeks</span>
                </div>
                <div>
                  <span className="text-[#8C7E72] block">Provenance:</span>
                  <span className="font-bold text-lg text-[#191716]">Italy</span>
                </div>
              </div>
            </div>

            {/* Right Overlapping Visual Column */}
            <div className="lg:col-span-6 relative">
              <div className="relative group cursor-pointer" onClick={() => setSelectedPiece(heroPiece)}>
                
                {/* Floating Decorative Blur Aura */}
                <div className="absolute -inset-4 bg-gradient-to-r from-[#E85A2A]/30 to-[#F59E0B]/20 rounded-full blur-3xl opacity-60 group-hover:opacity-100 transition-opacity"></div>

                {/* Overlapping Hero Image Card */}
                <div className="relative rounded-2xl overflow-hidden border border-[#191716]/10 bg-white shadow-2xl">
                  <img 
                    src={heroPiece.image} 
                    alt={heroPiece.name} 
                    className="w-full h-[480px] object-cover group-hover:scale-105 transition-transform duration-700" 
                  />
                  <div className="absolute top-4 left-4 bg-[#191716]/90 backdrop-blur-md text-white px-3.5 py-1 text-[11px] font-mono tracking-widest uppercase">
                    MONOLITH COCOON // 2026
                  </div>
                  <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-md text-[#191716] px-4 py-2 text-xs font-mono font-bold shadow-lg flex items-center gap-2">
                    <Maximize2 className="w-3.5 h-3.5 text-[#E85A2A]" />
                    <span>360° INSPECTION</span>
                  </div>
                </div>

                {/* Overlapping Specimen Pill */}
                <div className="absolute -bottom-6 -left-6 bg-[#191716] text-white p-5 rounded-xl border border-white/10 shadow-2xl max-w-xs hidden sm:block">
                  <div className="flex items-center gap-2 text-[#E85A2A] text-xs font-mono font-bold uppercase">
                    <Award className="w-4 h-4" />
                    <span>Salone Del Mobile Award</span>
                  </div>
                  <p className="text-[11px] font-mono text-zinc-300 mt-1">
                    Selected as Best Sculptural Seating Solution for High-End Hospitality.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Middle Editorial Banner: Formora Principle */}
      <section className="py-20 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="rounded-3xl bg-gradient-to-r from-[#C84B20] via-[#E85A2A] to-[#D85224] text-white p-10 lg:p-16 shadow-2xl relative overflow-hidden">
          <div className="max-w-4xl space-y-6">
            <span className="text-xs font-mono tracking-[0.25em] uppercase text-white/80 block">
              // EDITORIAL CONVICTION & INTERIOR TELEMETRY
            </span>
            <h2 className="text-3xl sm:text-5xl lg:text-6xl font-serif font-black tracking-tight uppercase leading-tight">
              The Most Expensive Mistake In A Premium Interior Is To Look Like Everyone Else
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-white/20 text-sm font-light leading-relaxed text-white/90">
              <div>
                <strong className="block font-mono text-xs uppercase tracking-wider text-white mb-2">First Impressions Anchor Value</strong>
                Guests form an unshakeable opinion about a space in a matter of seconds. Standard catalog furniture nullifies the financial investment in prime architecture and lighting.
              </div>
              <div>
                <strong className="block font-mono text-xs uppercase tracking-wider text-white mb-2">Invisibility Costs More Than Boldness</strong>
                In the luxury hospitality and residential segment, generic comfort is forgotten. Sculptural boldness turns spatial square-footage into an iconic, memorable destination.
              </div>
            </div>

            {/* Telemetry Metrics Bar */}
            <div className="pt-10 grid grid-cols-2 md:grid-cols-4 gap-6 border-t border-white/20 text-center">
              <div className="p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-4xl font-serif font-bold text-white">
                  <CountUp to={75} duration={2.0} />%
                </div>
                <span className="text-[11px] font-mono uppercase text-white/80 mt-1 block">Form opinion in 38s</span>
              </div>
              <div className="p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-4xl font-serif font-bold text-white">
                  +<CountUp to={25} duration={1.8} />%
                </div>
                <span className="text-[11px] font-mono uppercase text-white/80 mt-1 block">Higher dwell investment</span>
              </div>
              <div className="p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-4xl font-serif font-bold text-white">
                  <CountUp to={90} duration={2.2} /> min
                </div>
                <span className="text-[11px] font-mono uppercase text-white/80 mt-1 block">Avg comfort session</span>
              </div>
              <div className="p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-4xl font-serif font-bold text-white">
                  0<CountUp to={7} duration={1.5} /> sec
                </div>
                <span className="text-[11px] font-mono uppercase text-white/80 mt-1 block">First visceral impression</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Pieces Catalog Grid */}
      <section className="py-20 px-6 lg:px-16 max-w-7xl mx-auto border-t border-[#191716]/10">
        <div className="flex flex-col md:flex-row md:items-end justify-between pb-12 border-b border-[#191716]/10 gap-6">
          <div>
            <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E85A2A] font-bold">
              // PERMANENT COLLECTION 2026
            </span>
            <h2 className="text-3xl sm:text-5xl font-serif font-bold text-[#191716] mt-2">
              Sculptural Seating Monoliths
            </h2>
          </div>
          <div className="text-xs font-mono text-[#8C7E72]">
            <span>EXPLORING {filteredCatalog.length} OF 18 SPECIMENS</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 pt-12">
          {filteredCatalog.map((piece) => (
            <SpotlightCard 
              key={piece.id}
              className="bg-white border border-[#191716]/10 hover:border-[#E85A2A]/50 transition-all rounded-3xl overflow-hidden group cursor-pointer flex flex-col justify-between shadow-sm hover:shadow-xl"
              spotlightColor="rgba(232, 90, 42, 0.12)"
              onClick={() => setSelectedPiece(piece)}
            >
              <div>
                <div className="overflow-hidden relative h-72 border-b border-[#191716]/10">
                  <img 
                    src={piece.image} 
                    alt={piece.name} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" 
                  />
                  <div className="absolute top-4 left-4 bg-[#191716]/85 text-white px-3 py-1 rounded-full text-[10px] font-mono uppercase tracking-widest">
                    {piece.series}
                  </div>
                  <div className="absolute top-4 right-4 bg-white/95 text-[#191716] px-3.5 py-1 rounded-full text-xs font-mono font-bold shadow-md">
                    {piece.price}
                  </div>
                </div>

                <div className="p-8 space-y-3">
                  <div className="flex justify-between items-start">
                    <h3 className="text-2xl font-serif font-bold text-[#191716] group-hover:text-[#E85A2A] transition-colors">
                      {piece.name}
                    </h3>
                  </div>
                  <p className="text-sm text-[#5E5A54] font-light leading-relaxed">
                    {piece.description}
                  </p>
                </div>
              </div>

              <div className="p-8 pt-0">
                <div className="pt-6 border-t border-[#191716]/10 flex justify-between items-center text-xs font-mono text-[#8C7E72]">
                  <span>{piece.finish}</span>
                  <span className="font-bold text-[#191716] group-hover:text-[#E85A2A] flex items-center gap-1">
                    Examine Specs <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            </SpotlightCard>
          ))}
        </div>
      </section>

      {/* Tactile Material Library */}
      <section className="py-20 px-6 lg:px-16 max-w-7xl mx-auto border-t border-[#191716]/10 bg-[#F4ECE1]/60 rounded-3xl mb-24">
        <div className="max-w-2xl mb-12">
          <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#E85A2A] font-bold">
            // MATERIAL TACTILITY SWATCHES
          </span>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-[#191716] mt-2">
            Textile & Timber Provenance
          </h2>
          <p className="text-sm text-[#5E5A54] mt-2 font-light">
            Every piece is calibrated for tactile sensation. We combine high-density bio-latex cores with heritage Italian velvets and fumed German timber.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {materialSwatches.map((mat, idx) => (
            <div key={idx} className="p-6 bg-white rounded-2xl border border-[#191716]/10 shadow-sm space-y-3">
              <span className="text-[10px] font-mono text-[#E85A2A] font-bold tracking-widest block uppercase">
                SPECIMEN 0{idx + 1} // {mat.origin}
              </span>
              <h4 className="text-lg font-serif font-bold text-[#191716]">
                {mat.name}
              </h4>
              <p className="text-xs text-[#5E5A54] font-light leading-relaxed">
                {mat.texture}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Detail Modal */}
      {selectedPiece && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="bg-[#FFF8F0] border border-[#191716]/20 max-w-2xl w-full p-8 md:p-10 rounded-3xl shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setSelectedPiece(null)} 
              className="absolute top-6 right-6 p-2 text-[#8C7E72] hover:text-[#191716]"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-6">
              <div>
                <span className="text-xs font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
                  {selectedPiece.category} · {selectedPiece.price}
                </span>
                <h3 className="text-3xl font-serif font-bold text-[#191716] mt-1">
                  {selectedPiece.name}
                </h3>
              </div>

              <div className="overflow-hidden rounded-2xl h-80 border border-[#191716]/10">
                <img 
                  src={selectedPiece.image} 
                  alt={selectedPiece.name} 
                  className="w-full h-full object-cover" 
                />
              </div>

              <p className="text-sm text-[#5E5A54] leading-relaxed">
                {selectedPiece.description}
              </p>

              <div className="p-4 bg-[#F4ECE1] rounded-2xl border border-[#191716]/10 text-xs font-mono space-y-1">
                <div className="font-bold text-[#191716]">Crafting Specifications:</div>
                <div>Standard Lead Time: 4-6 Weeks Custom Build</div>
                <div>Warranty: 15-Year Structural Integrity Guarantee</div>
                <div>Delivery: White-Glove Architectural Freight</div>
              </div>

              <div className="flex justify-end gap-4 pt-2">
                <button 
                  onClick={() => setSelectedPiece(null)} 
                  className="px-6 py-3 font-mono text-xs uppercase tracking-wider text-[#8C7E72] hover:text-[#191716]"
                >
                  Close
                </button>
                <button 
                  onClick={() => { setSelectedPiece(null); setOrderModalOpen(true); }}
                  className="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-8 py-3.5 rounded-full font-mono text-xs uppercase tracking-widest font-bold shadow-lg"
                >
                  Commission This Piece
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Commission Inquiry Modal */}
      {orderModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="bg-[#FFF8F0] border border-[#191716]/20 max-w-lg w-full p-8 rounded-3xl shadow-2xl relative">
            <button 
              onClick={() => setOrderModalOpen(false)} 
              className="absolute top-6 right-6 p-2 text-[#8C7E72] hover:text-[#191716]"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-4">
              <span className="text-xs font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
                // COMMISSION INQUIRY
              </span>
              <h3 className="text-2xl font-serif font-bold text-[#191716]">
                Acquire Sculptural Furniture
              </h3>
              <p className="text-xs text-[#5E5A54] font-mono">
                Each piece is tailored to client spatial dimensions and fabric requirements.
              </p>

              <div className="space-y-3 pt-2">
                <input 
                  type="text" 
                  placeholder="Your Full Name or Interior Design Studio" 
                  className="w-full px-4 py-3 rounded-xl bg-white border border-[#191716]/15 text-sm text-[#191716] focus:outline-none focus:border-[#E85A2A]" 
                />
                <input 
                  type="email" 
                  placeholder="Direct Contact Email" 
                  className="w-full px-4 py-3 rounded-xl bg-white border border-[#191716]/15 text-sm text-[#191716] focus:outline-none focus:border-[#E85A2A]" 
                />
                <select className="w-full px-4 py-3 rounded-xl bg-white border border-[#191716]/15 text-sm text-[#191716] focus:outline-none focus:border-[#E85A2A]">
                  <option>Select Preferred Finish: Burnt Ochre Velvet</option>
                  <option>Deep Plum Bouclé</option>
                  <option>Smoked Native Oak</option>
                  <option>Cognac Full-Grain Leather</option>
                </select>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button 
                  onClick={() => setOrderModalOpen(false)} 
                  className="px-5 py-3 font-mono text-xs uppercase text-[#8C7E72]"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    alert('Acquisition brief received. Our studio director will contact you with fabric swatches.');
                    setOrderModalOpen(false);
                  }}
                  className="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-8 py-3.5 rounded-full font-mono text-xs uppercase tracking-widest font-bold shadow-lg"
                >
                  Submit Inquiry
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-[#191716] text-[#FFF8F0] py-16 px-6 lg:px-16 text-xs font-mono border-t border-[#191716]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
          <div>
            <div className="font-serif font-black text-xl tracking-tight text-white uppercase">
              __BRAND_NAME__
            </div>
            <p className="text-[#8C7E72] mt-1 text-[11px] uppercase tracking-widest">
              Sculptural Interior Furniture & Architectural Monoliths
            </p>
          </div>
          <div className="text-[#8C7E72] text-[11px] space-y-1 text-left md:text-right">
            <p>© 2026 __BRAND_NAME__. All rights reserved.</p>
            <p>Zürich · Milan · Copenhagen · New York</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_sculptural_furniture_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Sculptural Interior Furniture</title>
  
  <!-- Google Fonts: Syne & Plus Jakarta Sans & Space Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Syne:wght@700;800;900&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'bg-primary': '#FFF8F0',
            'bg-surface': '#F4ECE1',
            'accent-primary': '#E85A2A',
            'accent-hover': '#C84B20',
            'text-primary': '#191716',
            'text-secondary': '#8C7E72'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            serif: ['"Syne"', 'sans-serif'],
            mono: ['"Space Mono"', 'monospace']
          }
        }
      }
    };
  </script>

  <!-- Lucide Vector Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-[#FFF8F0] text-[#191716] antialiased selection:bg-[#E85A2A] selection:text-[#FFF8F0]">
  <div id="root">
    <div class="min-h-screen bg-[#FFF8F0] text-[#191716]">
      <header class="px-6 lg:px-16 py-5 border-b border-[#191716]/10 bg-[#FFF8F0]">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span class="font-serif font-black text-2xl tracking-tight text-[#191716]">__BRAND_NAME__</span>
          </div>
          <button class="bg-[#E85A2A] text-white font-mono font-bold text-xs px-6 py-3 uppercase tracking-widest">
            Acquire Piece
          </button>
        </div>
      </header>

      <section class="pt-12 pb-24 px-6 lg:px-16 max-w-7xl mx-auto">
        <div class="rounded-3xl bg-[#F4ECE1] p-12 border border-[#191716]/10">
          <h1 class="text-4xl sm:text-6xl font-serif font-black uppercase tracking-tight text-[#191716]">
            ATTRACTION POINTS FOR SPACES THAT ARE MEMORABLE
          </h1>
          <p class="text-lg text-[#5E5A54] mt-4 font-light">
            In the premium segment, invisibility costs more than boldness.
          </p>
        </div>
      </section>
    </div>
  </div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)
