"""
Domain Template: Futuristic Organic Sanctuary & Spatial Real Estate
Inspired by Orizon Design Benchmark.
Features:
- Floating pill-shaped canvas container over alpine mist landscape
- Frosted glass search pill bar (Buy, Location, Property Type, Max Price, Rent)
- Floating circular left icon dock
- Asymmetrical overlapping floating cards (Find The Perfect Place, Lunar Oasis Villa telemetry)
- Sunset tungsten interior glow against desert twilight photography
- Pure vector Lucide icons, zero emojis.
"""

def generate_sanctuary_real_estate_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''import React, { useState } from 'react';
import { 
  Home, Search, Grid, MessageSquare, Bell, Settings, 
  Moon, Sun, Compass, Heart, Share2, ArrowUpRight, 
  ArrowRight, MapPin, Maximize2, Bed, Bath, Sparkles, 
  ChevronDown, X, SlidersHorizontal, Check, ShieldCheck
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { SplitText } from './components/reactbits/SplitText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { Magnet } from './components/reactbits/Magnet';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const [selectedVilla, setSelectedVilla] = useState(null);
  const [inquiryModalOpen, setInquiryModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('buy');
  const [activeNav, setActiveNav] = useState('home');
  const [savedVillas, setSavedVillas] = useState(['villa-1']);
  const [priceRange, setPriceRange] = useState('$300,000');
  const [locationFilter, setLocationFilter] = useState('Arizona');

  const featuredVilla = {
    id: 'villa-1',
    name: "Lunar Oasis Villa",
    address: "1874 Forest Haven Rd, Sedona, Arizona",
    coordinates: "34°52'N 111°45'W",
    price: "$4,250,000",
    sqm: "695m²",
    yard: "1,260m² Private Desert",
    beds: 3,
    baths: 2,
    image: "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&q=80&w=1200",
    description: "This futuristic organic villa seamlessly blends into the red rock desert environment, offering a modern flowing space with panoramic desert views. Its innovative double-curved cantilever design makes it a serene luxury getaway with zero passive thermal loss.",
    specs: { energy: "100% Geothermal Solar", privacy: "Private Canyon Ridge", pool: "Heated Infinity Mineral Pool" }
  };

  const sanctuaryList = [
    {
      id: 'villa-2',
      name: "Solarium Canyon Ridge",
      location: "Moab, Utah",
      price: "$3,800,000",
      sqm: "580m²",
      beds: 4,
      baths: 3,
      image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=900",
      highlight: "Carved Sandstone Mass"
    },
    {
      id: 'villa-3',
      name: "Alpine Monolith Sanctuary",
      location: "Aspen, Colorado",
      price: "$6,100,000",
      sqm: "820m²",
      beds: 5,
      baths: 4,
      image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=900",
      highlight: "Triple-Glazed Snow Vista"
    },
    {
      id: 'villa-4',
      name: "Cascade Timber Horizon",
      location: "Bend, Oregon",
      price: "$2,950,000",
      sqm: "490m²",
      beds: 3,
      baths: 2,
      image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=900",
      highlight: "Cedar Forest Canopy"
    }
  ];

  const toggleSave = (id) => {
    setSavedVillas(prev => 
      prev.includes(id) ? prev.filter(v => v !== id) : [...prev, id]
    );
  };

  return (
    <div className="min-h-screen bg-[#DDE4EB] text-[#1E293B] font-sans relative overflow-x-hidden selection:bg-[#3B82F6] selection:text-white">
      
      {/* Outer Misty Landscape Canvas Layer */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-40 bg-cover bg-center mix-blend-multiply"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&q=80&w=1600')`
        }}
      ></div>

      {/* Main Responsive Floating Container (Orizon Benchmark) */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        
        {/* Outer Brand & Meta Bar */}
        <div className="flex justify-between items-center mb-6 text-xs font-mono tracking-widest text-[#64748B] uppercase">
          <div className="flex items-center gap-3">
            <span className="font-bold text-[#1E293B] tracking-wider text-sm">__BRAND_NAME__</span>
            <span>// ORGANIC SPATIAL SANCTUARIES</span>
          </div>
          <div className="hidden sm:flex items-center gap-6">
            <span>ARIZONA · COLORADO · UTAH · OREGON</span>
            <span className="text-[#3B82F6] font-semibold">BEST SHOTS ARCHIVE</span>
          </div>
        </div>

        {/* Central Rounded Sanctuary Card (Orizon Design Signature) */}
        <div className="relative rounded-[36px] sm:rounded-[44px] overflow-hidden bg-white/70 backdrop-blur-2xl border border-white/60 shadow-[0_32px_64px_rgba(30,41,59,0.12)] p-4 sm:p-6 lg:p-8">
          
          {/* Top Pill Filter & Search Navigation Bar */}
          <div className="flex flex-col lg:flex-row items-center justify-between gap-4 bg-white/80 backdrop-blur-md rounded-full px-4 sm:px-6 py-3 border border-white/80 shadow-sm mb-6">
            
            {/* Buy / Rent Switch Pills */}
            <div className="flex items-center gap-2 bg-[#F1F5F9] p-1.5 rounded-full">
              <button 
                onClick={() => setActiveTab('buy')}
                className={`px-6 py-2 rounded-full text-xs font-mono uppercase tracking-wider font-bold transition-all ${
                  activeTab === 'buy' ? 'bg-white text-[#1E293B] shadow-sm' : 'text-[#64748B] hover:text-[#1E293B]'
                }`}
              >
                Buy
              </button>
              <button 
                onClick={() => setActiveTab('rent')}
                className={`px-6 py-2 rounded-full text-xs font-mono uppercase tracking-wider font-bold transition-all ${
                  activeTab === 'rent' ? 'bg-white text-[#1E293B] shadow-sm' : 'text-[#64748B] hover:text-[#1E293B]'
                }`}
              >
                Rent
              </button>
            </div>

            {/* Filter Dropdowns */}
            <div className="hidden md:flex items-center gap-8 text-xs font-mono text-[#64748B]">
              <div className="flex flex-col">
                <span className="text-[10px] text-[#94A3B8] uppercase">Location</span>
                <span className="font-bold text-[#1E293B] flex items-center gap-1 cursor-pointer">
                  {locationFilter} <ChevronDown className="w-3.5 h-3.5" />
                </span>
              </div>
              <div className="h-6 w-px bg-slate-200"></div>
              <div className="flex flex-col">
                <span className="text-[10px] text-[#94A3B8] uppercase">Property Type</span>
                <span className="font-bold text-[#1E293B] flex items-center gap-1 cursor-pointer">
                  Organic Villa <ChevronDown className="w-3.5 h-3.5" />
                </span>
              </div>
              <div className="h-6 w-px bg-slate-200"></div>
              <div className="flex flex-col">
                <span className="text-[10px] text-[#94A3B8] uppercase">Max Price</span>
                <span className="font-bold text-[#1E293B] flex items-center gap-1 cursor-pointer">
                  $4.5M <ChevronDown className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>

            {/* Primary Action Button */}
            <Magnet strength={0.3}>
              <button 
                onClick={() => setInquiryModalOpen(true)}
                className="bg-[#1E293B] hover:bg-[#3B82F6] text-white px-7 py-2.5 rounded-full text-xs font-mono uppercase tracking-widest font-bold transition-all shadow-md flex items-center gap-2"
              >
                <span>Acquire Sanctuary</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </Magnet>
          </div>

          {/* Main Layout Grid: Floating Icon Sidebar + Hero Visual */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            
            {/* Left Vertical Glass Dock (Orizon Benchmark) */}
            <div className="hidden lg:flex lg:col-span-1 flex-col items-center justify-between py-6 px-2 bg-white/70 backdrop-blur-md rounded-full border border-white/80 shadow-sm">
              <div className="space-y-4">
                <button onClick={() => setActiveNav('home')} className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${activeNav === 'home' ? 'bg-[#1E293B] text-white shadow-md' : 'text-[#64748B] hover:bg-white'}`}>
                  <Home className="w-4 h-4" />
                </button>
                <button onClick={() => setActiveNav('search')} className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${activeNav === 'search' ? 'bg-[#1E293B] text-white shadow-md' : 'text-[#64748B] hover:bg-white'}`}>
                  <Search className="w-4 h-4" />
                </button>
                <button onClick={() => setActiveNav('grid')} className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${activeNav === 'grid' ? 'bg-[#1E293B] text-white shadow-md' : 'text-[#64748B] hover:bg-white'}`}>
                  <Grid className="w-4 h-4" />
                </button>
                <button onClick={() => setActiveNav('chat')} className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${activeNav === 'chat' ? 'bg-[#1E293B] text-white shadow-md' : 'text-[#64748B] hover:bg-white'}`}>
                  <MessageSquare className="w-4 h-4" />
                </button>
                <button onClick={() => setActiveNav('bell')} className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${activeNav === 'bell' ? 'bg-[#1E293B] text-white shadow-md' : 'text-[#64748B] hover:bg-white'}`}>
                  <Bell className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3 pt-6 border-t border-slate-200">
                <button onClick={() => setActiveNav('settings')} className="w-10 h-10 rounded-full flex items-center justify-center text-[#64748B] hover:bg-white transition-all">
                  <Settings className="w-4 h-4" />
                </button>
                <button onClick={() => setActiveNav('sun')} className="w-10 h-10 rounded-full flex items-center justify-center text-[#64748B] hover:bg-white transition-all">
                  <Sun className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Main Hero Visual Card with Overlapping Asymmetric Cards */}
            <div className="lg:col-span-11 relative rounded-[32px] overflow-hidden border border-white/60 shadow-xl min-h-[580px] flex flex-col justify-between p-6 sm:p-10 bg-slate-900">
              
              {/* Background Architectural Photo with Ambient Sunset Lighting */}
              <img 
                src={featuredVilla.image} 
                alt={featuredVilla.name} 
                className="absolute inset-0 w-full h-full object-cover opacity-90 transition-transform duration-1000 hover:scale-105" 
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-slate-950/40"></div>

              {/* Central Floating Typography (New Way Of Living) */}
              <div className="relative z-10 max-w-2xl pt-4">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/20 backdrop-blur-md border border-white/30 text-white text-[11px] font-mono uppercase tracking-widest mb-4">
                  <Sparkles className="w-3.5 h-3.5 text-[#F59E0B]" />
                  <span>ORGANIC CANTILEVER ARCHITECTURE</span>
                </div>
                <SplitText 
                  text="New Way Of Living" 
                  delay={0.03} 
                  className="text-4xl sm:text-6xl lg:text-7xl font-sans font-bold text-white tracking-tight leading-[1.05]"
                />
                <p className="text-sm sm:text-base text-slate-200 mt-3 font-light max-w-lg leading-relaxed">
                  Discover extraordinary organic properties available for purchase. Curved thermal envelopes seamlessly opening to sweeping panoramic desert canyons.
                </p>
              </div>

              {/* Bottom Overlapping Cards Row (Orizon Benchmark Layout) */}
              <div className="relative z-10 pt-12 grid grid-cols-1 md:grid-cols-12 gap-6 items-end">
                
                {/* Floating Bottom-Left Card: "Find The Perfect Place" */}
                <div className="md:col-span-5 bg-white/95 backdrop-blur-xl rounded-[28px] p-6 shadow-2xl border border-white/80 space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-lg font-bold text-[#1E293B]">
                        Find The Perfect Place
                      </h4>
                      <p className="text-xs text-[#64748B] mt-1 font-light leading-relaxed">
                        Our platform connects you with extraordinary homes in the most sought-after locations.
                      </p>
                    </div>
                  </div>

                  <div className="pt-2 flex items-center justify-between border-t border-slate-100">
                    <div>
                      <div className="text-2xl font-bold text-[#1E293B] flex items-center">
                        <CountUp to={10} duration={1.8} />k+
                      </div>
                      <span className="text-[10px] font-mono text-[#94A3B8] uppercase">Curated Sanctuaries</span>
                    </div>

                    <div className="flex items-center -space-x-2">
                      <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=120" alt="Client" className="w-8 h-8 rounded-full border-2 border-white object-cover" />
                      <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=120" alt="Client" className="w-8 h-8 rounded-full border-2 border-white object-cover" />
                      <div className="w-8 h-8 rounded-full bg-[#3B82F6] text-white text-[10px] font-bold flex items-center justify-center border-2 border-white">
                        +14
                      </div>
                    </div>

                    <button 
                      onClick={() => setInquiryModalOpen(true)}
                      className="w-10 h-10 rounded-full bg-[#1E293B] hover:bg-[#3B82F6] text-white flex items-center justify-center transition-colors shadow-md"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Floating Bottom-Right Frosted Glass Card: "Lunar Oasis Villa" */}
                <div className="md:col-span-7 bg-slate-900/80 backdrop-blur-2xl rounded-[28px] p-6 text-white border border-white/20 shadow-2xl space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 text-[#38BDF8] text-[11px] font-mono uppercase tracking-widest">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>Sedona Canyon, Arizona</span>
                      </div>
                      <h3 className="text-2xl font-bold tracking-tight text-white mt-1">
                        {featuredVilla.name}
                      </h3>
                      <div className="text-sm font-mono text-[#F59E0B] font-bold mt-0.5">
                        {featuredVilla.price}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button 
                        onClick={() => toggleSave(featuredVilla.id)}
                        className={`w-9 h-9 rounded-full flex items-center justify-center border border-white/20 transition-colors ${
                          savedVillas.includes(featuredVilla.id) ? 'bg-[#EF4444] text-white border-[#EF4444]' : 'bg-white/10 text-white hover:bg-white/20'
                        }`}
                      >
                        <Heart className="w-4 h-4 fill-current" />
                      </button>
                      <button 
                        onClick={() => setSelectedVilla(featuredVilla)}
                        className="w-9 h-9 rounded-full bg-white text-[#1E293B] flex items-center justify-center hover:bg-[#38BDF8] hover:text-white transition-colors"
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 font-light leading-relaxed line-clamp-2">
                    {featuredVilla.description}
                  </p>

                  <div className="pt-3 border-t border-white/15 flex flex-wrap items-center justify-between text-xs font-mono text-slate-300">
                    <span className="flex items-center gap-1.5">
                      <Maximize2 className="w-3.5 h-3.5 text-[#38BDF8]" /> {featuredVilla.sqm}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Bed className="w-3.5 h-3.5 text-[#38BDF8]" /> {featuredVilla.beds} Bedrooms
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Bath className="w-3.5 h-3.5 text-[#38BDF8]" /> {featuredVilla.baths} Baths
                    </span>
                    <span className="text-[#38BDF8] font-bold">
                      {featuredVilla.yard}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Selected Additional Sanctuaries Grid */}
        <div className="mt-12 space-y-6">
          <div className="flex justify-between items-end px-2">
            <div>
              <span className="text-xs font-mono uppercase tracking-[0.2em] text-[#3B82F6] font-bold">
                // CURATED RESIDENCES
              </span>
              <h3 className="text-2xl sm:text-3xl font-bold text-[#1E293B] mt-1">
                Other Architectural Sanctuaries
              </h3>
            </div>
            <span className="text-xs font-mono text-[#64748B]">
              4 AVAILABLE FOR ACQUISITION
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {sanctuaryList.map((villa) => (
              <SpotlightCard 
                key={villa.id}
                className="bg-white/80 backdrop-blur-xl rounded-[28px] overflow-hidden border border-white/80 p-0 shadow-md hover:shadow-xl transition-all cursor-pointer group flex flex-col justify-between"
                spotlightColor="rgba(59, 130, 246, 0.1)"
                onClick={() => setSelectedVilla(villa)}
              >
                <div>
                  <div className="h-56 overflow-hidden relative">
                    <img 
                      src={villa.image} 
                      alt={villa.name} 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" 
                    />
                    <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-mono text-[#1E293B] font-bold">
                      {villa.location}
                    </div>
                    <div className="absolute top-4 right-4 bg-[#1E293B]/85 text-white px-3 py-1 rounded-full text-xs font-mono font-bold">
                      {villa.price}
                    </div>
                  </div>

                  <div className="p-6 space-y-2">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-[#3B82F6] font-bold">
                      {villa.highlight}
                    </span>
                    <h4 className="text-lg font-bold text-[#1E293B] group-hover:text-[#3B82F6] transition-colors">
                      {villa.name}
                    </h4>
                  </div>
                </div>

                <div className="p-6 pt-0">
                  <div className="pt-4 border-t border-slate-100 flex justify-between items-center text-xs font-mono text-[#64748B]">
                    <span>{villa.sqm} · {villa.beds} Beds</span>
                    <span className="font-bold text-[#1E293B] flex items-center gap-1 group-hover:text-[#3B82F6]">
                      View Spec <ArrowRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>
              </SpotlightCard>
            ))}
          </div>
        </div>
      </div>

      {/* Detail Villa Modal */}
      {selectedVilla && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="bg-white rounded-[32px] border border-white/60 max-w-2xl w-full p-8 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setSelectedVilla(null)} 
              className="absolute top-6 right-6 p-2 text-[#64748B] hover:text-[#1E293B]"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-6">
              <div>
                <span className="text-xs font-mono uppercase tracking-widest text-[#3B82F6] font-bold">
                  {selectedVilla.location || selectedVilla.address}
                </span>
                <h3 className="text-2xl sm:text-3xl font-bold text-[#1E293B] mt-1">
                  {selectedVilla.name}
                </h3>
                <div className="text-lg font-mono font-bold text-[#F59E0B] mt-1">
                  {selectedVilla.price}
                </div>
              </div>

              <div className="overflow-hidden rounded-2xl h-72">
                <img 
                  src={selectedVilla.image} 
                  alt={selectedVilla.name} 
                  className="w-full h-full object-cover" 
                />
              </div>

              <p className="text-sm text-[#64748B] leading-relaxed">
                {selectedVilla.description || "A masterfully engineered organic sanctuary featuring seamless thermal cantilever glass walls and private desert garden access."}
              </p>

              <div className="p-4 bg-[#F8FAFC] rounded-2xl border border-slate-200 text-xs font-mono text-[#64748B] space-y-1.5">
                <div className="font-bold text-[#1E293B]">Acquisition Services:</div>
                <div>Private Flight Landing Feasibility Included</div>
                <div>Title Escrow via Zürich Global Escrow Partners</div>
                <div>Full Interior Fixtures by Master Craftsmen</div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button 
                  onClick={() => setSelectedVilla(null)} 
                  className="px-5 py-2.5 font-mono text-xs uppercase text-[#64748B]"
                >
                  Close
                </button>
                <button 
                  onClick={() => { setSelectedVilla(null); setInquiryModalOpen(true); }}
                  className="bg-[#1E293B] hover:bg-[#3B82F6] text-white px-8 py-3 rounded-full font-mono text-xs uppercase tracking-widest font-bold shadow-lg"
                >
                  Request Private Tour
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inquiry Drawer Modal */}
      {inquiryModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
          <div className="bg-white rounded-[32px] border border-white/60 max-w-lg w-full p-8 shadow-2xl relative">
            <button 
              onClick={() => setInquiryModalOpen(false)} 
              className="absolute top-6 right-6 p-2 text-[#64748B] hover:text-[#1E293B]"
            >
              <X className="w-6 h-6" />
            </button>

            <div className="space-y-4">
              <span className="text-xs font-mono uppercase tracking-widest text-[#3B82F6] font-bold">
                // SANCTUARY ACQUISITION
              </span>
              <h3 className="text-2xl font-bold text-[#1E293B]">
                Initiate Private Dossier
              </h3>
              <p className="text-xs text-[#64748B] font-mono">
                Access full architectural blueprints, environmental studies, and confidential pricing.
              </p>

              <div className="space-y-3 pt-2">
                <input 
                  type="text" 
                  placeholder="Principal Investor or Family Office Name" 
                  className="w-full px-4 py-3 rounded-2xl bg-[#F8FAFC] border border-slate-200 text-sm text-[#1E293B] focus:outline-none focus:border-[#3B82F6]" 
                />
                <input 
                  type="email" 
                  placeholder="Confidential Communication Email" 
                  className="w-full px-4 py-3 rounded-2xl bg-[#F8FAFC] border border-slate-200 text-sm text-[#1E293B] focus:outline-none focus:border-[#3B82F6]" 
                />
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button 
                  onClick={() => setInquiryModalOpen(false)} 
                  className="px-5 py-2.5 font-mono text-xs uppercase text-[#64748B]"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    alert('Sanctuary dossier request received. Our managing partner will contact you directly.');
                    setInquiryModalOpen(false);
                  }}
                  className="bg-[#1E293B] hover:bg-[#3B82F6] text-white px-8 py-3 rounded-full font-mono text-xs uppercase tracking-widest font-bold shadow-lg"
                >
                  Send Dossier Request
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-20 py-12 px-6 text-center text-xs font-mono text-[#64748B] border-t border-slate-200">
        <p>© 2026 __BRAND_NAME__. All architectural sanctuaries patented and protected.</p>
      </footer>
    </div>
  );
}
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_sanctuary_real_estate_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Organic Spatial Sanctuaries</title>
  
  <!-- Google Fonts: Plus Jakarta Sans & Space Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'bg-canvas': '#DDE4EB',
            'accent-blue': '#3B82F6',
            'text-dark': '#1E293B'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            mono: ['"Space Mono"', 'monospace']
          }
        }
      }
    };
  </script>

  <!-- Lucide Vector Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-[#DDE4EB] text-[#1E293B] antialiased">
  <div id="root">
    <div class="min-h-screen bg-[#DDE4EB] p-8">
      <header class="max-w-7xl mx-auto flex justify-between items-center py-4">
        <span class="font-bold text-xl uppercase tracking-wider text-[#1E293B]">__BRAND_NAME__</span>
        <button class="bg-[#1E293B] text-white font-mono text-xs px-6 py-2.5 rounded-full uppercase tracking-widest font-bold">
          Acquire Sanctuary
        </button>
      </header>
      <section class="max-w-7xl mx-auto mt-6 bg-white/70 backdrop-blur-xl rounded-[36px] p-8 border border-white/60">
        <h1 class="text-4xl sm:text-6xl font-bold text-[#1E293B] tracking-tight">
          New Way Of Living
        </h1>
        <p class="text-base text-slate-600 mt-2 font-light">
          Discover extraordinary organic properties available for purchase.
        </p>
      </section>
    </div>
  </div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)
