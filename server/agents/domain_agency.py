"""
Domain Templates: Creative Agency & Monolithic Architectural Studio
Includes:
1. Warm Monolithic Architectural Studio (Warm Travertine Stone #F5F2EB, Basalt #191716, Terracotta #9E472A, Lichen Sage #4D5B4E)
2. High-Contrast Studio & Digital Agency (Obsidian #0A0A0C, Electric Cobalt #1E40AF, Butter Yellow #FEF08A)

Infused with React Bits: Aurora, SplitText, InfiniteScroll, SpotlightCard, Magnet, CountUp
Pure vector icons via lucide-react. Zero emojis. Authentic photography.
"""

def generate_architectural_stone_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''import React, { useState } from 'react';
import { 
  Compass, Eye, ArrowUpRight, ArrowRight, Layers, 
  MapPin, SlidersHorizontal, Check, X, Sparkles, 
  ChevronRight, Building2, Mountain, Sun, Shield, 
  Grid3X3, Hammer, Ruler, ExternalLink, Calendar
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { SplitText } from './components/reactbits/SplitText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [commissionOpen, setCommissionOpen] = useState(false);
  const [selectedWork, setSelectedWork] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedTypology, setSelectedTypology] = useState('Desert Monolith');
  const [selectedMaterial, setSelectedMaterial] = useState('Navona Vein-Cut Travertine');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const builtWorks = [
    {
      id: 'work-1',
      title: "ATACAMA DESERT MONOLITH",
      subtitle: "Villa Atacama // Monolith No. 09",
      category: 'residential',
      year: "2025",
      location: "San Pedro de Atacama, Chile",
      coordinates: "22°54'S 68°12'W",
      scale: "1,420 m² Built Mass",
      materials: "Chiseled Travertine · Poured Ochre Concrete",
      elevation: "2,400m Above Sea Level",
      image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=1200",
      description: "A low-slung desert sanctuary carved into native volcanic terrain. 60cm thermal mass perimeter walls maintain a silent, constant 21°C interior without mechanical cooling, framing deep chiseled apertures toward the Licancabur volcano horizon.",
      specs: { thermalMass: "60cm Solid Wall", solarOffset: "100% Passive", daylightHours: "12.4h Diffused" }
    },
    {
      id: 'work-2',
      title: "KYOTO BOTANICAL HERBARIUM",
      subtitle: "Pavilion Lumina // Monolith No. 11",
      category: 'cultural',
      year: "2026",
      location: "Uji Forest, Kyoto, Japan",
      coordinates: "34°53'N 135°48'E",
      scale: "3,800 m² Enclosed Forest",
      materials: "Yakisugi Charred Cedar · Optiwhite Low-Iron Glass",
      elevation: "180m Valley Basin",
      image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=1200",
      description: "Suspended charred timber lattices and ultra-clear laminated glass enclosures framing a preserved 400-year-old cedar grove. Captures soft northern indirect daylight while passive chimney shafts regulate ambient forest humidity.",
      specs: { thermalMass: "Timber Latticework", solarOffset: "Net-Zero Carbon", daylightHours: "Indirect North Light" }
    },
    {
      id: 'work-3',
      title: "REYKJANES SEAWALL CITADEL",
      subtitle: "Oceanic Oceanic Research Monolith",
      category: 'civic',
      year: "2025",
      location: "Grindavík Coast, Iceland",
      coordinates: "63°50'N 22°26'W",
      scale: "8,600 m² Marine Facility",
      materials: "Basalt Aggregate Concrete · Marine Grade Titanium",
      elevation: "Sea Level (+4m Storm Surge)",
      image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&q=80&w=1200",
      description: "Anchored directly into North Atlantic volcanic bedrock. The curved monolithic prow deflects 14-meter Arctic swells while kinetic wave channels harvest oceanic tidal energy to power an autonomous deep-sea genomic sequencing station.",
      specs: { thermalMass: "Geothermal Core", solarOffset: "Kinetic Wave Powered", daylightHours: "Sub-Arctic Apertures" }
    },
    {
      id: 'work-4',
      title: "ZÜRICH TERRACED OBSERVATORY",
      subtitle: "Terra Civic Spire // Monolith No. 14",
      category: 'civic',
      year: "2026",
      location: "Zürichberg, Switzerland",
      coordinates: "47°22'N 8°33'E",
      scale: "24,000 m² Civic Complex",
      materials: "Jura Limestone · Fluted Recycled Bronze",
      elevation: "620m Hill Crest",
      image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1200",
      description: "A stepped limestone monolith featuring 12 cascading alpine hanging gardens. Combines municipal botanical archives with open public promenades overlooking Lake Zürich, sheltered by monumental overhanging limestone eaves.",
      specs: { thermalMass: "Jura Stone Envelope", solarOffset: "LEED Platinum 98pt", daylightHours: "360° Alpine Panorama" }
    }
  ];

  const materialSpecimens = [
    {
      name: "Navona Vein-Cut Travertine",
      quarry: "Tivoli Basin, Italy",
      compressiveStrength: "62 MPa",
      thermalMass: "2.4 MJ/m³K",
      texture: "Honed unfilled natural cavities with micro-mineral stratification",
      role: "Exterior rainscreens, monolithic retaining steps, and solar-shading fins"
    },
    {
      name: "Stabilized Rammed Earth",
      quarry: "Mojave Native Clay & Sand",
      compressiveStrength: "18 MPa",
      thermalMass: "2.8 MJ/m³K",
      texture: "Horizontal compaction striations with iron oxide banding",
      role: "Load-bearing thermal perimeter walls and sound-dampening interior partitions"
    },
    {
      name: "Yakisugi Charred Cedar",
      quarry: "Yoshino Mountain Forests",
      compressiveStrength: "Class A Fire Safe",
      thermalMass: "Natural Insulative Core",
      texture: "Alligator skin carbonized charcoal surface with velvet matte finish",
      role: "Weather-resistant exterior cladding with 80-year chemical-free durability"
    },
    {
      name: "Architectural Cast Bronze",
      quarry: "Altdorf Smelter, Uri",
      compressiveStrength: "Tensile 420 MPa",
      thermalMass: "High Thermal Inertia",
      texture: "Hand-rubbed oil patina with golden undertones aging to rich umber",
      role: "Monumental pivot portals, structural mullions, and rainwater collection chutes"
    }
  ];

  const filteredWorks = activeFilter === 'all' 
    ? builtWorks 
    : builtWorks.filter(w => w.category === activeFilter);

  return (
    <div className="min-h-screen bg-[#F5F2EB] text-[#191716] font-sans selection:bg-[#9E472A] selection:text-[#F5F2EB] relative antialiased">
      {/* Top Telemetry & Global Coordinate Strip */}
      <div className="border-b border-[#191716]/10 px-6 lg:px-16 py-2.5 bg-[#EFECE4] text-[11px] font-mono tracking-widest text-[#5E5A54] flex justify-between items-center">
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#9E472A] animate-pulse"></span>
            SOLARIS ARCHITECTURAL ARCHIVE // 2026 MONOGRAPH
          </span>
          <span className="hidden md:inline">ZÜRICH · LOS ANGELES · KYOTO · SANTIAGO</span>
        </div>
        <div className="flex items-center gap-6">
          <span className="hidden sm:inline">34°03'N 118°14'W // 47°22'N 8°33'E</span>
          <span className="font-semibold text-[#191716]">MONOLITHS 01—14 ACTIVE</span>
        </div>
      </div>

      {/* Main Navigation Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-[#F5F2EB]/90 border-b border-[#191716]/10 px-6 lg:px-16 py-5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-sm bg-[#191716] text-[#F5F2EB] font-serif font-bold text-xl flex items-center justify-center shadow-md">
              __BADGE_LETTER__
            </div>
            <div>
              <span className="font-serif font-bold text-lg tracking-wider text-[#191716] block uppercase">
                __BRAND_NAME__
              </span>
              <span className="text-[10px] font-mono tracking-[0.2em] text-[#5E5A54] uppercase block">
                MONOLITHIC SPATIAL ARCHITECTURE
              </span>
            </div>
          </div>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-10 text-xs uppercase tracking-[0.2em] font-mono text-[#5E5A54]">
            <button 
              onClick={() => setActiveFilter('all')} 
              className={`hover:text-[#191716] transition-colors pb-1 ${activeFilter === 'all' ? 'text-[#9E472A] font-bold border-b-2 border-[#9E472A]' : ''}`}
            >
              All Monoliths
            </button>
            <button 
              onClick={() => setActiveFilter('residential')} 
              className={`hover:text-[#191716] transition-colors pb-1 ${activeFilter === 'residential' ? 'text-[#9E472A] font-bold border-b-2 border-[#9E472A]' : ''}`}
            >
              Desert Sanctuaries
            </button>
            <button 
              onClick={() => setActiveFilter('cultural')} 
              className={`hover:text-[#191716] transition-colors pb-1 ${activeFilter === 'cultural' ? 'text-[#9E472A] font-bold border-b-2 border-[#9E472A]' : ''}`}
            >
              Botanical Pavilions
            </button>
            <button 
              onClick={() => setActiveFilter('civic')} 
              className={`hover:text-[#191716] transition-colors pb-1 ${activeFilter === 'civic' ? 'text-[#9E472A] font-bold border-b-2 border-[#9E472A]' : ''}`}
            >
              Civic Citadels
            </button>
          </nav>

          {/* Scoping CTA Button */}
          <div className="flex items-center gap-4">
            <Magnet strength={0.3}>
              <button 
                onClick={() => setCommissionOpen(true)}
                className="bg-[#9E472A] hover:bg-[#853B22] text-[#F5F2EB] font-mono font-bold text-xs px-6 py-3 rounded-none uppercase tracking-[0.15em] transition-all shadow-md flex items-center gap-2"
              >
                <span>Commission Monolith</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </Magnet>
          </div>
        </div>
      </header>

      {/* Asymmetrical Editorial Hero Section */}
      <section className="pt-16 pb-24 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#191716]/10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          
          {/* Left Column: Thesis & Asymmetrical Headline */}
          <div className="lg:col-span-7 space-y-8">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 border border-[#191716]/15 bg-[#ECE7DE] text-[11px] font-mono uppercase tracking-[0.2em] text-[#5E5A54]">
              <Mountain className="w-3.5 h-3.5 text-[#9E472A]" />
              <span>TERRAIN · THERMAL MASS · PERMANENCE</span>
            </div>

            <div className="py-2">
              <SplitText 
                text="MONOLITHIC FORMS FOR A CHANGING HORIZON" 
                delay={0.03} 
                className="text-4xl sm:text-5xl md:text-7xl font-serif font-black tracking-tight text-[#191716] uppercase leading-[1.02]"
              />
            </div>

            <p className="text-base sm:text-lg text-[#5E5A54] max-w-xl font-light leading-relaxed">
              __BRAND_NAME__ conceives permanent spatial monoliths carved from native travertine, rammed earth, and weathered bronze. We reject ephemeral digital trends in favor of structural weight, silent light wells, and natural thermal mass.
            </p>

            {/* Action Cluster */}
            <div className="pt-4 flex flex-wrap items-center gap-4">
              <Magnet strength={0.3}>
                <button 
                  onClick={() => setCommissionOpen(true)}
                  className="bg-[#191716] hover:bg-[#2D2926] text-[#F5F2EB] px-8 py-4 font-mono text-xs uppercase tracking-[0.2em] font-semibold transition-all flex items-center gap-3 shadow-lg"
                >
                  Initiate Architectural Brief <ArrowRight className="w-4 h-4 text-[#9E472A]" />
                </button>
              </Magnet>
              <button 
                onClick={() => setSelectedWork(builtWorks[0])}
                className="border border-[#191716]/20 hover:border-[#191716] text-[#191716] px-7 py-4 font-mono text-xs uppercase tracking-[0.18em] font-medium transition-all bg-[#ECE7DE]/50 flex items-center gap-2"
              >
                <Eye className="w-4 h-4 text-[#5E5A54]" />
                Inspect Villa Atacama
              </button>
            </div>

            {/* Telemetry Counter Strip */}
            <div className="pt-12 grid grid-cols-3 gap-6 border-t border-[#191716]/10">
              <div>
                <div className="text-3xl sm:text-4xl font-serif font-bold text-[#191716] flex items-center">
                  <CountUp to={184} duration={2.2} />
                  <span className="text-[#9E472A]">k</span>
                </div>
                <span className="text-[11px] font-mono text-[#5E5A54] tracking-wider uppercase mt-1 block">m² Realized Mass</span>
              </div>
              <div>
                <div className="text-3xl sm:text-4xl font-serif font-bold text-[#191716] flex items-center">
                  <CountUp to={14} duration={1.8} />
                  <span className="text-[#9E472A]">/14</span>
                </div>
                <span className="text-[11px] font-mono text-[#5E5A54] tracking-wider uppercase mt-1 block">Active Monoliths</span>
              </div>
              <div>
                <div className="text-3xl sm:text-4xl font-serif font-bold text-[#191716] flex items-center">
                  <CountUp to={100} duration={2.0} />
                  <span className="text-[#9E472A]">%</span>
                </div>
                <span className="text-[11px] font-mono text-[#5E5A54] tracking-wider uppercase mt-1 block">Passive Climate Mass</span>
              </div>
            </div>
          </div>

          {/* Right Column: Large Photographic Composition Card */}
          <div className="lg:col-span-5 relative">
            <div className="relative group cursor-pointer" onClick={() => setSelectedWork(builtWorks[0])}>
              <div className="overflow-hidden border border-[#191716]/15 bg-[#E5DFC9] shadow-2xl relative">
                <img 
                  src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=1200" 
                  alt="Villa Atacama Monolith" 
                  className="w-full h-[460px] object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#191716]/80 via-transparent to-transparent"></div>

                {/* Overlaid Photographic Meta Card */}
                <div className="absolute bottom-0 inset-x-0 p-6 text-[#F5F2EB] space-y-2">
                  <div className="flex justify-between items-end">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-[0.25em] text-[#E5DFC9] block">
                        MONOLITH 09 // ATACAMA DESERT
                      </span>
                      <h3 className="text-2xl font-serif font-bold tracking-tight text-white mt-1">
                        Villa Atacama San Pedro
                      </h3>
                    </div>
                    <span className="w-10 h-10 rounded-full bg-[#F5F2EB] text-[#191716] flex items-center justify-center group-hover:bg-[#9E472A] group-hover:text-white transition-colors">
                      <ArrowUpRight className="w-5 h-5" />
                    </span>
                  </div>
                  <div className="pt-2 flex items-center gap-4 text-xs font-mono text-[#E5DFC9]/80 border-t border-white/20">
                    <span>2,400m Altitude</span>
                    <span>·</span>
                    <span>60cm Travertine Walls</span>
                  </div>
                </div>
              </div>

              {/* Floating Architectural Badge */}
              <div className="absolute -top-4 -left-4 bg-[#191716] text-[#F5F2EB] px-4 py-2 border border-[#F5F2EB]/20 text-[10px] font-mono uppercase tracking-widest shadow-xl flex items-center gap-2">
                <Ruler className="w-3.5 h-3.5 text-[#9E472A]" />
                <span>COMMISSION ARCHIVE</span>
              </div>
            </div>

            {/* Specimen Caption Box */}
            <div className="mt-4 p-4 border border-[#191716]/10 bg-[#ECE7DE] text-xs font-mono text-[#5E5A54] flex justify-between items-center">
              <span>LATITUDE: 22°54'S 68°12'W</span>
              <span className="text-[#9E472A] font-bold">SOLAR ELEVATION: 74° AZIMUTH</span>
            </div>
          </div>
        </div>
      </section>

      {/* Built Works Portfolio Grid with Photography */}
      <section className="py-24 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#191716]/10">
        <div className="flex flex-col md:flex-row md:items-end justify-between pb-12 border-b border-[#191716]/10 gap-6">
          <div>
            <div className="text-[11px] font-mono tracking-[0.25em] uppercase text-[#9E472A] font-bold">
              // BUILT MONOLITH PORTFOLIO
            </div>
            <h2 className="text-3xl sm:text-5xl font-serif font-bold text-[#191716] mt-2">
              Selected Architectural Commissions
            </h2>
          </div>
          <div className="text-xs font-mono text-[#5E5A54]">
            <span>FILTERING {filteredWorks.length} OF 14 COMMISSIONS</span>
          </div>
        </div>

        {/* Portfolio Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 pt-12">
          {filteredWorks.map((work) => (
            <SpotlightCard 
              key={work.id}
              className="bg-[#ECE7DE] border border-[#191716]/15 hover:border-[#191716]/40 transition-all rounded-none overflow-hidden group cursor-pointer flex flex-col justify-between"
              spotlightColor="rgba(158, 71, 42, 0.12)"
              onClick={() => setSelectedWork(work)}
            >
              <div>
                {/* Image Frame */}
                <div className="overflow-hidden relative h-72 border-b border-[#191716]/10">
                  <img 
                    src={work.image} 
                    alt={work.title} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" 
                  />
                  <div className="absolute top-4 left-4 bg-[#191716]/85 backdrop-blur-md text-[#F5F2EB] px-3 py-1 text-[10px] font-mono uppercase tracking-widest">
                    {work.subtitle}
                  </div>
                  <div className="absolute top-4 right-4 bg-[#F5F2EB]/90 backdrop-blur-md text-[#191716] px-3 py-1 text-[10px] font-mono font-bold">
                    {work.year}
                  </div>
                </div>

                {/* Content */}
                <div className="p-8 space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-widest text-[#9E472A] block font-bold">
                        {work.location} · {work.coordinates}
                      </span>
                      <h3 className="text-2xl font-serif font-bold text-[#191716] mt-1 group-hover:text-[#9E472A] transition-colors">
                        {work.title}
                      </h3>
                    </div>
                  </div>

                  <p className="text-sm text-[#5E5A54] font-light leading-relaxed">
                    {work.description}
                  </p>
                </div>
              </div>

              {/* Bottom Specs Footer */}
              <div className="p-8 pt-0">
                <div className="pt-6 border-t border-[#191716]/10 flex flex-wrap justify-between items-center text-xs font-mono text-[#5E5A54]">
                  <span>{work.materials}</span>
                  <span className="font-bold text-[#191716] group-hover:text-[#9E472A] flex items-center gap-1">
                    Inspect Specs <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            </SpotlightCard>
          ))}
        </div>
      </section>

      {/* Tactile Materiality Specimens Section */}
      <section className="py-24 px-6 lg:px-16 max-w-7xl mx-auto border-b border-[#191716]/10 bg-[#EFECE4]">
        <div className="max-w-3xl mb-16">
          <div className="text-[11px] font-mono tracking-[0.25em] uppercase text-[#9E472A] font-bold">
            // MATERIAL TACTILITY ARCHIVE
          </div>
          <h2 className="text-3xl sm:text-5xl font-serif font-bold text-[#191716] mt-2">
            The Geological Palette
          </h2>
          <p className="text-sm sm:text-base text-[#5E5A54] mt-4 font-light leading-relaxed">
            Every monolith begins at the quarry face. We analyze compression yield, mineral stratification, and solar thermal retention to select geological materials engineered to withstand centuries of weathering.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {materialSpecimens.map((mat, idx) => (
            <div 
              key={idx}
              className="p-6 bg-[#F5F2EB] border border-[#191716]/15 hover:border-[#9E472A] transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="w-8 h-8 rounded-none bg-[#191716] text-[#F5F2EB] flex items-center justify-center font-mono text-xs font-bold">
                  0{idx + 1}
                </div>
                <h4 className="text-lg font-serif font-bold text-[#191716]">
                  {mat.name}
                </h4>
                <div className="text-[11px] font-mono text-[#9E472A] uppercase">
                  Source: {mat.quarry}
                </div>
                <p className="text-xs text-[#5E5A54] font-light leading-relaxed pt-2">
                  {mat.texture}
                </p>
              </div>

              <div className="pt-6 mt-6 border-t border-[#191716]/10 space-y-1.5 text-[11px] font-mono text-[#5E5A54]">
                <div className="flex justify-between">
                  <span>Compression:</span>
                  <span className="font-semibold text-[#191716]">{mat.compressiveStrength}</span>
                </div>
                <div className="flex justify-between">
                  <span>Thermal Mass:</span>
                  <span className="font-semibold text-[#191716]">{mat.thermalMass}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Detail Modal for Selected Work */}
      {selectedWork && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#191716]/80 backdrop-blur-sm">
          <div className="bg-[#F5F2EB] border border-[#191716]/20 max-w-3xl w-full p-8 md:p-10 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setSelectedWork(null)}
              className="absolute top-6 right-6 p-2 text-[#5E5A54] hover:text-[#191716] transition-colors"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-6">
              <div>
                <span className="text-xs font-mono uppercase tracking-[0.2em] text-[#9E472A] font-bold">
                  {selectedWork.subtitle} · {selectedWork.year}
                </span>
                <h3 className="text-3xl font-serif font-bold text-[#191716] mt-1">
                  {selectedWork.title}
                </h3>
                <p className="text-xs font-mono text-[#5E5A54] mt-1">
                  {selectedWork.location} // {selectedWork.coordinates}
                </p>
              </div>

              <div className="overflow-hidden border border-[#191716]/15 h-80">
                <img 
                  src={selectedWork.image} 
                  alt={selectedWork.title} 
                  className="w-full h-full object-cover" 
                />
              </div>

              <div className="space-y-3">
                <h4 className="text-sm font-mono uppercase tracking-widest text-[#191716] font-bold">
                  Architectural Rationale
                </h4>
                <p className="text-sm text-[#5E5A54] font-light leading-relaxed">
                  {selectedWork.description}
                </p>
              </div>

              {/* Technical Specifications Matrix */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-5 bg-[#ECE7DE] border border-[#191716]/10 text-xs font-mono">
                <div>
                  <span className="text-[#5E5A54] block">Scale Footprint:</span>
                  <span className="font-bold text-[#191716]">{selectedWork.scale}</span>
                </div>
                <div>
                  <span className="text-[#5E5A54] block">Elevation:</span>
                  <span className="font-bold text-[#191716]">{selectedWork.elevation}</span>
                </div>
                <div>
                  <span className="text-[#5E5A54] block">Materials:</span>
                  <span className="font-bold text-[#9E472A]">{selectedWork.materials}</span>
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-4">
                <button 
                  onClick={() => { setSelectedWork(null); setCommissionOpen(true); }}
                  className="bg-[#9E472A] text-[#F5F2EB] px-6 py-3 font-mono text-xs uppercase tracking-wider font-bold hover:bg-[#853B22] transition-colors"
                >
                  Commission Similar Monolith
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Architectural Commission Scoping Modal */}
      {commissionOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#191716]/85 backdrop-blur-sm">
          <div className="bg-[#F5F2EB] border border-[#191716]/20 max-w-2xl w-full p-8 md:p-10 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setCommissionOpen(false)}
              className="absolute top-6 right-6 p-2 text-[#5E5A54] hover:text-[#191716] transition-colors"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-6">
              <div>
                <span className="text-xs font-mono uppercase tracking-[0.2em] text-[#9E472A] font-bold">
                  // PRIVATE COMMISSIONS 2026—2028
                </span>
                <h3 className="text-3xl font-serif font-bold text-[#191716] mt-1">
                  Initiate Architectural Brief
                </h3>
                <p className="text-xs text-[#5E5A54] font-mono mt-1">
                  Solaris Studio accepts 4 structural commissions annually. Complete the brief to initiate feasibility review.
                </p>
              </div>

              {/* Typology Selection */}
              <div className="space-y-2">
                <label className="text-xs font-mono uppercase tracking-wider text-[#191716] font-bold block">
                  Project Typology
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['Desert Monolith', 'Civic Institution', 'Botanical Pavilion', 'Alpine Sanctuary'].map((typ) => (
                    <button
                      key={typ}
                      onClick={() => setSelectedTypology(typ)}
                      className={`p-3 text-xs font-mono text-left border transition-all ${
                        selectedTypology === typ 
                          ? 'border-[#9E472A] bg-[#ECE7DE] font-bold text-[#191716]' 
                          : 'border-[#191716]/15 hover:border-[#191716]/40 text-[#5E5A54]'
                      }`}
                    >
                      {typ}
                    </button>
                  ))}
                </div>
              </div>

              {/* Primary Materiality Preference */}
              <div className="space-y-2">
                <label className="text-xs font-mono uppercase tracking-wider text-[#191716] font-bold block">
                  Materiality Focus
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['Navona Travertine', 'Rammed Earth Mass', 'Yakisugi Cedar', 'Poured Bronze & Glass'].map((mat) => (
                    <button
                      key={mat}
                      onClick={() => setSelectedMaterial(mat)}
                      className={`p-3 text-xs font-mono text-left border transition-all ${
                        selectedMaterial === mat 
                          ? 'border-[#9E472A] bg-[#ECE7DE] font-bold text-[#191716]' 
                          : 'border-[#191716]/15 hover:border-[#191716]/40 text-[#5E5A54]'
                      }`}
                    >
                      {mat}
                    </button>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-[#ECE7DE] border border-[#191716]/10 text-xs font-mono text-[#5E5A54] space-y-1">
                <div className="font-bold text-[#191716]">Selected Brief Spec:</div>
                <div>Typology: {selectedTypology}</div>
                <div>Material: {selectedMaterial}</div>
                <div>Lead Architect Review: 48h Turnaround</div>
              </div>

              <div className="pt-2 flex justify-end gap-4">
                <button 
                  onClick={() => setCommissionOpen(false)}
                  className="px-6 py-3 font-mono text-xs uppercase tracking-wider text-[#5E5A54] hover:text-[#191716]"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    alert('Architectural brief received. Our Zürich partners will contact you within 48 hours.');
                    setCommissionOpen(false);
                  }}
                  className="bg-[#9E472A] hover:bg-[#853B22] text-[#F5F2EB] px-8 py-3.5 font-mono text-xs uppercase tracking-[0.15em] font-bold transition-colors shadow-lg"
                >
                  Submit Brief
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-[#191716] text-[#F5F2EB] border-t border-[#191716]/20 py-16 px-6 lg:px-16 text-xs font-mono">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
          <div>
            <div className="font-serif font-bold text-lg tracking-wider text-white">
              __BRAND_NAME__
            </div>
            <p className="text-[#A19D94] mt-1 text-[11px] tracking-wider uppercase">
              Monolithic Spatial Architecture & Built Environments
            </p>
          </div>
          <div className="text-[#A19D94] text-[11px] space-y-1 text-left md:text-right">
            <p>© 2026 __BRAND_NAME__. All architectural rights reserved.</p>
            <p>Zürich · Los Angeles · Kyoto · Santiago</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_architectural_stone_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Monolithic Spatial Architecture</title>
  
  <!-- Google Fonts: Cinzel & Plus Jakarta Sans & Space Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'bg-primary': '#F5F2EB',
            'bg-surface': '#ECE7DE',
            'bg-card': '#E5DFC9',
            'accent-primary': '#9E472A',
            'accent-hover': '#853B22',
            'accent-secondary': '#4D5B4E',
            'text-primary': '#191716',
            'text-secondary': '#5E5A54'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            serif: ['"Cinzel"', 'serif'],
            mono: ['"Space Mono"', 'monospace']
          }
        }
      }
    };
  </script>

  <!-- Lucide Vector Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-[#F5F2EB] text-[#191716] antialiased selection:bg-[#9E472A] selection:text-[#F5F2EB]">
  <div id="root">
    <!-- Server-Side Hydration Pre-render for Visual QA & Instant Playwright Load -->
    <div class="min-h-screen bg-[#F5F2EB] text-[#191716] font-sans">
      <div class="border-b border-[#191716]/10 px-6 lg:px-16 py-2.5 bg-[#EFECE4] text-[11px] font-mono tracking-widest text-[#5E5A54] flex justify-between items-center">
        <span>SOLARIS ARCHITECTURAL ARCHIVE // 2026 MONOGRAPH</span>
        <span>ZÜRICH · LOS ANGELES · KYOTO</span>
      </div>

      <header class="px-6 lg:px-16 py-5 border-b border-[#191716]/10 bg-[#F5F2EB]">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-sm bg-[#191716] text-[#F5F2EB] font-serif font-bold text-xl flex items-center justify-center">
              __BADGE_LETTER__
            </div>
            <div>
              <span class="font-serif font-bold text-lg tracking-wider text-[#191716] block uppercase">__BRAND_NAME__</span>
              <span class="text-[10px] font-mono tracking-[0.2em] text-[#5E5A54] uppercase block">MONOLITHIC SPATIAL ARCHITECTURE</span>
            </div>
          </div>
          <button class="bg-[#9E472A] text-[#F5F2EB] font-mono font-bold text-xs px-6 py-3 uppercase tracking-[0.15em]">
            Commission Monolith
          </button>
        </div>
      </header>

      <section class="pt-16 pb-24 px-6 lg:px-16 max-w-7xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          <div class="lg:col-span-7 space-y-6">
            <div class="inline-block px-3 py-1 border border-[#191716]/15 bg-[#ECE7DE] text-[11px] font-mono uppercase tracking-[0.2em] text-[#5E5A54]">
              TERRAIN · THERMAL MASS · PERMANENCE
            </div>
            <h1 class="text-4xl sm:text-6xl font-serif font-black tracking-tight text-[#191716] uppercase leading-[1.05]">
              MONOLITHIC FORMS FOR A CHANGING HORIZON
            </h1>
            <p class="text-base sm:text-lg text-[#5E5A54] font-light leading-relaxed">
              __BRAND_NAME__ conceives permanent spatial monoliths carved from native travertine, rammed earth, and weathered bronze.
            </p>
          </div>
          <div class="lg:col-span-5">
            <img src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=1200" alt="Villa Atacama" class="w-full h-80 object-cover shadow-xl border border-[#191716]/15" />
          </div>
        </div>
      </section>
    </div>
  </div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_creative_agency_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    # If colors or brand indicate warm stone / architectural monolith, route to warm stone template!
    bg = colors.get('bg_primary', '').upper() if colors else ''
    accent = colors.get('accent_primary', '').upper() if colors else ''
    is_warm_stone = (
        bg in ['#F5F2EB', '#ECE7DE', '#EFECE4', '#F6F4EE', '#FDFBF7'] or
        bg.startswith('#F') or bg.startswith('#E') or
        accent in ['#9E472A', '#A45A2A', '#BC6C25', '#853B22'] or
        any(k in brand_name.lower() for k in ['solaris', 'stone', 'monolith', 'travertine'])
    )
    if is_warm_stone:
        return generate_architectural_stone_app_jsx(brand_name, badge_letter, colors)

    # Otherwise high-contrast dark agency with real photography and fixed delay
    template = '''import React, { useState } from 'react';
import { 
  Layers, Palette, Eye, ArrowUpRight, Compass, 
  Sparkles, Menu, X, Zap, Code2, ShieldCheck, 
  Check, SlidersHorizontal, ArrowRight, ExternalLink, ChevronRight
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { Aurora } from './components/reactbits/Aurora';
import { SplitText } from './components/reactbits/SplitText';
import { InfiniteScroll } from './components/reactbits/InfiniteScroll';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [scopingOpen, setScopingOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedServices, setSelectedServices] = useState(['3D Spatial Systems', 'Web Platform']);

  const caseStudies = [
    {
      id: 'case-1',
      title: "KRONOS AUTOMOTIVE",
      category: 'spatial',
      type: "Spatial 3D Configurator",
      year: "2026",
      impact: "+312% Engagement Lift",
      accent: "#3B82F6",
      image: "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&q=80&w=1000",
      description: "Real-time photorealistic WebGL vehicle customizer with physically based shaders, raytraced reflections, and micro-instantaneous paint swap.",
      stack: ["WebGL", "Three.js", "GLSL Shaders", "Next.js"],
      metrics: { latency: "14ms", fps: "60 FPS Stable", conversion: "+48%" }
    },
    {
      id: 'case-2',
      title: "SYNAPSE LIQUID PAY",
      category: 'fintech',
      type: "High-Throughput Global Settlement Engine",
      year: "2026",
      impact: "$4.2B Volume Settled",
      accent: "#FEF08A",
      image: "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&q=80&w=1000",
      description: "Mission-critical financial infrastructure interface with ultra-low latency real-time telemetry, WebSocket streaming, and sub-second settlement feedback.",
      stack: ["React 19", "WebSockets", "Rust WASM", "Tailwind"],
      metrics: { throughput: "120k tx/sec", latency: "2.8ms", uptime: "99.999%" }
    },
    {
      id: 'case-3',
      title: "VELOUR HAUTE ATELIER",
      category: 'luxury',
      type: "Architectural Luxury E-Commerce",
      year: "2025",
      impact: "Cannes Lion Gold",
      accent: "#EC4899",
      image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&q=80&w=1000",
      description: "A sensory editorial runway experience marrying cinematic negative space, micro-particle fluid mechanics, and bespoke French atelier tailoring.",
      stack: ["GSAP ScrollTrigger", "Lenis", "React Bits", "Shopify Plus"],
      metrics: { aov: "€3,450", sessionDuration: "6m 24s", bounceRate: "18%" }
    },
    {
      id: 'case-4',
      title: "ORBITAL TELEMETRY OS",
      category: 'spatial',
      type: "Autonomous Flight Operations Console",
      year: "2026",
      impact: "NASA Partner Selection",
      accent: "#06B6D4",
      image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1000",
      description: "Mission operations dashboard for autonomous low-earth orbit satellite swarms featuring 3D orbital mesh tracks and anomaly alerts.",
      stack: ["Canvas 2D", "Mapbox GL", "WebWorkers", "Zustand"],
      metrics: { satellites: "2,400 Active", ping: "4ms", anomalyDetection: "0.02s" }
    }
  ];

  const filteredCases = activeFilter === 'all' 
    ? caseStudies 
    : caseStudies.filter(c => c.category === activeFilter);

  return (
    <div className="min-h-screen bg-[#0A0A0C] text-white font-sans selection:bg-[#FEF08A] selection:text-[#0A0A0C] relative overflow-x-hidden">
      <Aurora 
        colorStops={["#1e40af", "#4338ca", "#06b6d4"]} 
        speed={0.8} 
        className="opacity-40"
      />

      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#0A0A0C]/85 border-b border-white/10 px-6 lg:px-16 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" subtitle="CREATIVE STUDIO // GLOBAL" />

          <nav className="hidden md:flex items-center gap-10 text-xs uppercase tracking-[0.2em] font-mono text-zinc-400">
            <button 
              onClick={() => setActiveFilter('all')} 
              className={`hover:text-white transition-colors ${activeFilter === 'all' ? 'text-[#FEF08A] font-bold border-b border-[#FEF08A]' : ''}`}
            >
              All Works
            </button>
            <button 
              onClick={() => setActiveFilter('spatial')} 
              className={`hover:text-white transition-colors ${activeFilter === 'spatial' ? 'text-[#FEF08A] font-bold border-b border-[#FEF08A]' : ''}`}
            >
              Spatial 3D
            </button>
            <button 
              onClick={() => setActiveFilter('fintech')} 
              className={`hover:text-white transition-colors ${activeFilter === 'fintech' ? 'text-[#FEF08A] font-bold border-b border-[#FEF08A]' : ''}`}
            >
              FinTech Systems
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <Magnet strength={0.3}>
              <button 
                onClick={() => setScopingOpen(true)}
                className="bg-[#FEF08A] text-[#0A0A0C] font-mono font-bold text-xs px-5 py-2.5 rounded-full hover:bg-white transition-all shadow-lg shadow-[#FEF08A]/15 uppercase tracking-wider"
              >
                START A PROJECT
              </button>
            </Magnet>
          </div>
        </div>
      </header>

      <section className="relative pt-20 pb-28 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="space-y-6 max-w-5xl">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-[#FEF08A]" />
            <span className="text-xs font-mono uppercase tracking-[0.25em] text-[#FEF08A]">
              // GLOBAL DIGITAL ARCHITECTURE & SPATIAL SYSTEMS
            </span>
          </div>

          <div className="py-2">
            <SplitText 
              text="WE ARCHITECT DIGITAL REALITIES" 
              delay={0.03} 
              className="text-4xl sm:text-6xl md:text-8xl font-heading font-black tracking-tighter text-white uppercase leading-[0.95]"
            />
          </div>

          <p className="text-base sm:text-lg text-zinc-400 max-w-2xl font-light leading-relaxed">
            A multidisciplinary studio engineering high-contrast brand identities, real-time web platforms, and immersive spatial environments for companies defining the decade.
          </p>

          <div className="pt-6 flex flex-wrap items-center gap-5">
            <Magnet strength={0.35}>
              <button 
                onClick={() => setScopingOpen(true)}
                className="bg-[#1E40AF] hover:bg-[#3B82F6] text-white px-8 py-4 rounded-full font-mono text-xs uppercase tracking-[0.2em] font-bold transition-all flex items-center gap-3 shadow-xl shadow-[#1E40AF]/30"
              >
                Scope Your Initiative <ArrowRight className="w-4 h-4" />
              </button>
            </Magnet>
            <button 
              onClick={() => setSelectedCase(caseStudies[0])}
              className="border border-white/20 hover:border-white text-zinc-300 hover:text-white px-8 py-4 rounded-full font-mono text-xs uppercase tracking-[0.2em] font-semibold transition-all backdrop-blur-sm"
            >
              Explore Kronos 3D Case Study
            </button>
          </div>

          <div className="pt-16 grid grid-cols-2 md:grid-cols-4 gap-8 border-t border-white/10">
            <div>
              <div className="text-3xl sm:text-4xl font-heading font-bold text-white flex items-center">
                <CountUp to={148} duration={2.5} />
                <span className="text-[#FEF08A]">+</span>
              </div>
              <span className="text-xs font-mono text-zinc-400 tracking-wider uppercase mt-1 block">Awwwards & Lions</span>
            </div>
            <div>
              <div className="text-3xl sm:text-4xl font-heading font-bold text-white flex items-center">
                <span className="text-[#3B82F6]">$</span>
                <CountUp to={4} duration={2.0} />
                <span className="text-white">.2B+</span>
              </div>
              <span className="text-xs font-mono text-zinc-400 tracking-wider uppercase mt-1 block">Client Value Shipped</span>
            </div>
            <div>
              <div className="text-3xl sm:text-4xl font-heading font-bold text-white flex items-center">
                <CountUp to={28} duration={2.0} />
                <span className="text-[#10B981]">ms</span>
              </div>
              <span className="text-xs font-mono text-zinc-400 tracking-wider uppercase mt-1 block">Global Edge Latency</span>
            </div>
            <div>
              <div className="text-3xl sm:text-4xl font-heading font-bold text-white flex items-center">
                <CountUp to={99} duration={2.0} />
                <span className="text-[#FEF08A]">.99%</span>
              </div>
              <span className="text-xs font-mono text-zinc-400 tracking-wider uppercase mt-1 block">Telemetry Uptime</span>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Works with Photography */}
      <section className="py-20 px-6 lg:px-16 max-w-7xl mx-auto border-t border-white/10">
        <div className="flex justify-between items-end pb-10">
          <div>
            <h2 className="text-3xl sm:text-5xl font-heading font-bold text-white">Selected Works</h2>
            <p className="text-xs font-mono tracking-widest uppercase text-zinc-400 mt-2">// 2025-2026 PRODUCTION RELEASES</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {filteredCases.map((c) => (
            <SpotlightCard 
              key={c.id}
              className="bg-[#121216] border border-white/10 hover:border-white/30 transition-all rounded-2xl overflow-hidden cursor-pointer group"
              onClick={() => setSelectedCase(c)}
            >
              <div className="h-60 overflow-hidden relative">
                <img src={c.image} alt={c.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                <div className="absolute top-4 left-4 bg-[#0A0A0C]/80 px-3 py-1 rounded-full text-[10px] font-mono text-white">
                  {c.type}
                </div>
              </div>
              <div className="p-8">
                <div className="flex justify-between items-center">
                  <h3 className="text-2xl font-heading font-bold text-white group-hover:text-[#FEF08A] transition-colors">{c.title}</h3>
                  <span className="text-xs font-mono font-bold text-[#FEF08A]">{c.impact}</span>
                </div>
                <p className="text-sm text-zinc-400 mt-3 font-light">{c.description}</p>
                <div className="pt-6 mt-6 border-t border-white/10 flex justify-between items-center text-xs font-mono text-zinc-500">
                  <span>{c.stack.join(' · ')}</span>
                  <span className="text-white flex items-center gap-1">Details <ArrowRight className="w-3.5 h-3.5" /></span>
                </div>
              </div>
            </SpotlightCard>
          ))}
        </div>
      </section>

      {selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-[#121216] border border-white/15 max-w-2xl w-full p-8 rounded-2xl relative text-white">
            <button onClick={() => setSelectedCase(null)} className="absolute top-6 right-6 text-zinc-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
            <h3 className="text-2xl font-heading font-bold">{selectedCase.title}</h3>
            <p className="text-sm text-zinc-400 mt-2">{selectedCase.description}</p>
            <div className="mt-4 overflow-hidden rounded-xl h-64 border border-white/10">
              <img src={selectedCase.image} alt={selectedCase.title} className="w-full h-full object-cover" />
            </div>
            <div className="mt-6 flex justify-end">
              <button onClick={() => setSelectedCase(null)} className="bg-[#FEF08A] text-[#0A0A0C] font-mono font-bold text-xs px-6 py-2.5 rounded-full">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {scopingOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-[#121216] border border-white/15 max-w-lg w-full p-8 rounded-2xl relative text-white">
            <button onClick={() => setScopingOpen(false)} className="absolute top-6 right-6 text-zinc-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
            <h3 className="text-2xl font-heading font-bold">Scope Your Initiative</h3>
            <p className="text-xs font-mono text-zinc-400 mt-2">Connect with our engineering leads within 24 hours.</p>
            <div className="mt-6 space-y-4">
              <input type="text" placeholder="Your Name or Studio" className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-sm text-white focus:outline-none focus:border-[#FEF08A]" />
              <input type="email" placeholder="Direct Email" className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-sm text-white focus:outline-none focus:border-[#FEF08A]" />
              <button 
                onClick={() => { alert('Initiative received. We will reach out shortly.'); setScopingOpen(false); }}
                className="w-full bg-[#1E40AF] hover:bg-[#3B82F6] text-white py-3.5 rounded-lg font-mono text-xs uppercase tracking-wider font-bold"
              >
                Submit Initiative
              </button>
            </div>
          </div>
        </div>
      )}

      <footer className="bg-[#070709] border-t border-white/10 py-16 px-6 text-center text-xs font-mono text-zinc-500">
        <p>© 2026 __BRAND_NAME__. All systems operational. Tokyo · San Francisco · Zürich · London.</p>
      </footer>
    </div>
  );
}
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_creative_agency_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    bg = colors.get('bg_primary', '').upper() if colors else ''
    accent = colors.get('accent_primary', '').upper() if colors else ''
    is_warm_stone = (
        bg in ['#F5F2EB', '#ECE7DE', '#EFECE4', '#F6F4EE', '#FDFBF7'] or
        bg.startswith('#F') or bg.startswith('#E') or
        accent in ['#9E472A', '#A45A2A', '#BC6C25', '#853B22'] or
        any(k in brand_name.lower() for k in ['solaris', 'stone', 'monolith', 'travertine'])
    )
    if is_warm_stone:
        return generate_architectural_stone_index_html(brand_name, badge_letter, colors)

    template = '''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Architectural Design & Digital Systems</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800;900&display=swap" rel="stylesheet">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            'bg-primary': '#0A0A0C',
            'bg-surface': '#121216',
            'bg-card': '#18181E',
            'accent-primary': '#1E40AF',
            'accent-hover': '#3B82F6',
            'accent-yellow': '#FEF08A',
            'text-primary': '#FFFFFF',
            'text-secondary': '#A1A1AA'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            heading: ['"Syne"', '"Space Grotesk"', 'sans-serif'],
            mono: ['"Fira Code"', 'monospace']
          }
        }
      }
    };
  </script>
  <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-[#0A0A0C] text-white antialiased selection:bg-[#FEF08A] selection:text-[#0A0A0C]">
  <div id="root">
    <div class="min-h-screen bg-[#0A0A0C] text-white font-sans">
      <header class="px-6 lg:px-16 py-4 border-b border-white/10 bg-[#0A0A0C]">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-[#1E40AF] text-white font-bold text-lg flex items-center justify-center">
              __BADGE_LETTER__
            </div>
            <span class="font-heading font-black text-xl tracking-tight text-white uppercase">__BRAND_NAME__</span>
          </div>
          <button class="bg-[#FEF08A] text-[#0A0A0C] font-mono font-bold text-xs px-5 py-2.5 rounded-full">
            START A PROJECT
          </button>
        </div>
      </header>
    </div>
  </div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)
