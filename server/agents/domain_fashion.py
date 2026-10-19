"""
Domain Template: Editorial Fashion & Haute Couture Storefront
Infused with React Bits: Particles, BlurText, ShinyText, TiltedCard, Magnet
Palette: Editorial Cream (#FDFBF7), Deep Heritage Burgundy (#4A1525), Champagne (#C5A880), Charcoal (#1C1917)
Typography: Cinzel / Playfair Display & Plus Jakarta Sans
"""

def generate_fashion_editorial_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''import React, { useState } from 'react';
import { 
  ShoppingBag, Sparkles, SlidersHorizontal, ArrowRight, Eye, 
  Heart, Search, X, Check, Globe, ChevronDown, Plus, Minus
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { Particles } from './components/reactbits/Particles';
import { BlurText } from './components/reactbits/BlurText';
import { ShinyText } from './components/reactbits/ShinyText';
import { TiltedCard } from './components/reactbits/TiltedCard';
import { Magnet } from './components/reactbits/Magnet';

export default function App() {
  const [cartOpen, setCartOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedSize, setSelectedSize] = useState('FR 38');
  const [currency, setCurrency] = useState('EUR');
  const [activeCategory, setActiveCategory] = useState('all');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [bagItems, setBagItems] = useState([
    {
      id: 'item-1',
      name: "L'Ombre Silk Trench",
      priceEUR: 2850,
      priceUSD: 3100,
      size: 'FR 38',
      quantity: 1,
      image: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=900'
    }
  ]);

  const currencySymbol = currency === 'EUR' ? '€' : '$';
  const getPrice = (item) => currency === 'EUR' ? item.priceEUR : item.priceUSD;

  const catalog = [
    {
      id: 'item-1',
      name: "L'Ombre Silk Trench",
      category: 'coats',
      priceEUR: 2850,
      priceUSD: 3100,
      tag: "EDITION LIMITÉE // 40 PIÈCES",
      fabric: "100% Mulberry Heavyweight Silk (40 Momme)",
      provenance: "Hand-finished in Atelier 7ème, Paris",
      description: "A monumental study in structural fluid draping. Features our signature architectural storm lapel, horn-carved closures, and double-stitched storm flap.",
      image: "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'item-2',
      name: "Velour Sculpted Cape",
      category: 'coats',
      priceEUR: 3400,
      priceUSD: 3700,
      tag: "RUNWAY PIECE 04",
      fabric: "Double-Faced Cashmere & Heritage Bordeaux Wool",
      provenance: "Spun in Biella, Tailored in Paris",
      description: "Monumental drape cut from raw-edge double-faced cashmere. Unstructured silhouette engineered to respond dynamically to human motion.",
      image: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'item-3',
      name: "Aura Pleated Column Gown",
      category: 'dresses',
      priceEUR: 4100,
      priceUSD: 4450,
      tag: "HAUTE ATELIER",
      fabric: "Hand-Pleated Micro-Organza & Liquid Silk",
      provenance: "78 Hours of Hand-Pleating",
      description: "Precision sunburst accordion pleats radiating from a sculpted boned bodice. A masterwork of structural elegance and nocturnal drape.",
      image: "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'item-4',
      name: "Le Ciel Structured Tote",
      category: 'leather',
      priceEUR: 1650,
      priceUSD: 1800,
      tag: "PERMANENT ARCHIVE",
      fabric: "Box Calfskin & Palladium Hardware",
      provenance: "Tanned in Tuscany, Hand-Assembled",
      description: "Monolithic geometric tote structured with internal cedar reinforcement. Designed with architectural proportion and mirror-finish palladium hardware.",
      image: "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&q=80&w=900"
    }
  ];

  const filteredItems = activeCategory === 'all' 
    ? catalog 
    : catalog.filter(item => item.category === activeCategory);

  const subtotal = bagItems.reduce((acc, item) => acc + (getPrice(item) * item.quantity), 0);

  const addToBag = (product, size) => {
    const existing = bagItems.find(i => i.id === product.id && i.size === size);
    if (existing) {
      setBagItems(bagItems.map(i => i.id === product.id && i.size === size ? { ...i, quantity: i.quantity + 1 } : i));
    } else {
      setBagItems([...bagItems, { ...product, size: size || 'FR 38', quantity: 1 }]);
    }
    setCartOpen(true);
  };

  const updateQuantity = (id, size, delta) => {
    setBagItems(bagItems.map(i => {
      if (i.id === id && i.size === size) {
        const newQ = i.quantity + delta;
        return newQ > 0 ? { ...i, quantity: newQ } : null;
      }
      return i;
    }).filter(Boolean));
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-[#1C1917] font-sans selection:bg-[#4A1525] selection:text-[#FDFBF7] relative overflow-x-hidden">
      {/* React Bits Particles Ambient Luxury Dust Background */}
      <Particles 
        color="#C5A880" 
        count={45} 
        speed={0.4} 
        className="opacity-70"
      />

      {/* Luxury Navigation Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#FDFBF7]/90 border-b border-[#4A1525]/10 px-6 lg:px-16 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" subtitle="ATELIER COUTURE // PARIS" />

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-10 text-xs uppercase tracking-[0.2em] font-serif font-medium text-[#78716C]">
            <button 
              onClick={() => setActiveCategory('all')} 
              className={`hover:text-[#4A1525] transition-colors ${activeCategory === 'all' ? 'text-[#4A1525] font-bold border-b border-[#4A1525]' : ''}`}
            >
              Collections
            </button>
            <button 
              onClick={() => setActiveCategory('coats')} 
              className={`hover:text-[#4A1525] transition-colors ${activeCategory === 'coats' ? 'text-[#4A1525] font-bold border-b border-[#4A1525]' : ''}`}
            >
              Manteaux & Capes
            </button>
            <button 
              onClick={() => setActiveCategory('dresses')} 
              className={`hover:text-[#4A1525] transition-colors ${activeCategory === 'dresses' ? 'text-[#4A1525] font-bold border-b border-[#4A1525]' : ''}`}
            >
              Robes & Soie
            </button>
            <button 
              onClick={() => setActiveCategory('leather')} 
              className={`hover:text-[#4A1525] transition-colors ${activeCategory === 'leather' ? 'text-[#4A1525] font-bold border-b border-[#4A1525]' : ''}`}
            >
              Maroquinerie
            </button>
          </nav>

          {/* Header Actions */}
          <div className="flex items-center gap-5">
            <button 
              onClick={() => setCurrency(currency === 'EUR' ? 'USD' : 'EUR')} 
              className="text-xs font-mono font-medium tracking-wider px-2.5 py-1 rounded border border-[#4A1525]/20 text-[#4A1525] hover:bg-[#4A1525]/5 transition-all"
            >
              {currency} {currencySymbol}
            </button>

            {/* Shopping Bag Trigger */}
            <button 
              onClick={() => setCartOpen(true)}
              className="relative p-2 text-[#1C1917] hover:text-[#4A1525] transition-colors"
              aria-label="View Shopping Bag"
            >
              <ShoppingBag className="w-5 h-5" />
              {bagItems.length > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-[#4A1525] text-[#FDFBF7] text-[10px] font-mono font-bold rounded-full flex items-center justify-center">
                  {bagItems.reduce((acc, i) => acc + i.quantity, 0)}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-24 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="text-center max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#4A1525]/20 bg-[#F7F5F0]">
            <Sparkles className="w-3.5 h-3.5 text-[#C5A880]" />
            <ShinyText 
              text="EXCLUSIVITÉ ATELIER // AUTOMNE-HIVER 2026" 
              speed={3} 
              className="text-xs uppercase tracking-[0.25em] text-[#4A1525] font-serif font-semibold"
            />
          </div>

          <div className="py-2">
            <BlurText 
              text="HAUTE COUTURE ÉDITION LIMITÉE" 
              delay={70} 
              animateBy="words" 
              direction="top" 
              className="text-4xl sm:text-6xl md:text-7xl font-serif tracking-tight text-[#1C1917] font-normal leading-tight"
            />
          </div>

          <p className="text-sm sm:text-base text-[#78716C] max-w-2xl mx-auto font-light leading-relaxed">
            A sensory dialogue between architectural silhouette and ethereal drape. 
            Meticulously tailored in our 7th Arrondissement atelier using certified biological Mulberry silk and double-faced Biellese wool.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <Magnet strength={0.3}>
              <button 
                onClick={() => setCartOpen(true)}
                className="bg-[#4A1525] text-[#FDFBF7] px-8 py-3.5 tracking-[0.2em] uppercase font-serif text-xs font-semibold hover:bg-[#6B1D2F] transition-all flex items-center gap-2 shadow-lg shadow-[#4A1525]/20"
              >
                Acquire Collection <ArrowRight className="w-4 h-4" />
              </button>
            </Magnet>
            <button 
              onClick={() => setSelectedItem(catalog[0])}
              className="border border-[#4A1525]/30 text-[#4A1525] px-8 py-3.5 tracking-[0.2em] uppercase font-serif text-xs font-semibold hover:bg-[#4A1525]/5 transition-all"
            >
              Inspect Lookbook No. 01
            </button>
          </div>
        </div>
      </section>

      {/* Lookbook Gallery Grid */}
      <section className="py-12 px-6 lg:px-16 max-w-7xl mx-auto">
        <div className="flex items-center justify-between pb-8 border-b border-[#4A1525]/10">
          <div>
            <h2 className="text-2xl sm:text-3xl font-serif text-[#1C1917] tracking-tight">The 2026 Runway Lookbook</h2>
            <p className="text-xs tracking-widest uppercase font-serif text-[#78716C] mt-1">Direct from Paris Fashion Week</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-[#78716C]">{filteredItems.length} Pieces Curated</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 pt-8">
          {filteredItems.map((item) => (
            <div key={item.id} className="flex flex-col group">
              <div 
                onClick={() => setSelectedItem(item)}
                className="cursor-pointer overflow-hidden rounded-xl border border-[#4A1525]/15 bg-[#F7F5F0] relative"
              >
                <TiltedCard 
                  imageSrc={item.image}
                  alt={item.name}
                  captionText={item.tag}
                  containerHeight="400px"
                  imageHeight="400px"
                  maxAngle={10}
                  scale={1.02}
                />
              </div>

              <div className="pt-4 flex flex-col space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase tracking-widest text-[#C5A880] font-mono font-medium">{item.tag}</span>
                  <span className="text-sm font-serif font-bold text-[#4A1525]">{currencySymbol}{getPrice(item).toLocaleString()}</span>
                </div>
                <h3 className="text-base font-serif font-medium text-[#1C1917] group-hover:text-[#4A1525] transition-colors">{item.name}</h3>
                <p className="text-xs text-[#78716C] line-clamp-1">{item.fabric}</p>
                
                <div className="pt-2 flex items-center gap-2">
                  <button 
                    onClick={() => addToBag(item, 'FR 38')}
                    className="flex-1 bg-[#4A1525]/10 hover:bg-[#4A1525] text-[#4A1525] hover:text-[#FDFBF7] py-2 text-xs uppercase tracking-widest font-serif font-semibold transition-all rounded"
                  >
                    Add to Bag
                  </button>
                  <button 
                    onClick={() => setSelectedItem(item)}
                    className="p-2 border border-[#4A1525]/20 text-[#4A1525] hover:bg-[#4A1525]/5 rounded"
                    aria-label="Inspect piece details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Atelier Craftsmanship Showcase */}
      <section className="py-20 bg-[#F7F5F0] border-y border-[#4A1525]/10 mt-16 px-6 lg:px-16">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-12 text-center lg:text-left">
          <div className="space-y-3">
            <span className="text-xs font-mono text-[#4A1525] tracking-widest uppercase font-bold">01 // PROVENANCE</span>
            <h4 className="text-xl font-serif text-[#1C1917]">Single-Origin Natural Fibers</h4>
            <p className="text-xs text-[#78716C] leading-relaxed">
              Every yard of Mulberry silk and un-dyed virgin wool is sourced from heritage Italian and French family mills with complete chemical-free traceability.
            </p>
          </div>
          <div className="space-y-3">
            <span className="text-xs font-mono text-[#4A1525] tracking-widest uppercase font-bold">02 // ARCHITECTURE</span>
            <h4 className="text-xl font-serif text-[#1C1917]">Sculptural Pattern Drafting</h4>
            <p className="text-xs text-[#78716C] leading-relaxed">
              Tailoring patterns are drafted with asymmetrical internal boning to retain architectural volume while providing unrestricted kinetic freedom.
            </p>
          </div>
          <div className="space-y-3">
            <span className="text-xs font-mono text-[#4A1525] tracking-widest uppercase font-bold">03 // PERMANENCE</span>
            <h4 className="text-xl font-serif text-[#1C1917]">Lifetime Atelier Warranty</h4>
            <p className="text-xs text-[#78716C] leading-relaxed">
              Each garment includes complimentary lifetime hand-mending and seasonal pressing at any of our private Parisian and Milanese salon archives.
            </p>
          </div>
        </div>
      </section>

      {/* Slide-over Luxury Shopping Bag Drawer */}
      {cartOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-black/40 backdrop-blur-sm flex justify-end">
          <div className="w-full max-w-md bg-[#FDFBF7] h-full shadow-2xl flex flex-col p-6 animate-slide-left border-l border-[#4A1525]/20">
            <div className="flex items-center justify-between pb-4 border-b border-[#4A1525]/10">
              <div className="flex items-center gap-2">
                <ShoppingBag className="w-5 h-5 text-[#4A1525]" />
                <h3 className="font-serif text-lg font-bold text-[#1C1917]">Your Private Bag</h3>
              </div>
              <button 
                onClick={() => setCartOpen(false)}
                className="p-1 text-[#78716C] hover:text-[#1C1917]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-6 space-y-4">
              {bagItems.length === 0 ? (
                <div className="text-center py-16 text-[#78716C] font-serif">
                  Your luxury bag is currently empty.
                </div>
              ) : (
                bagItems.map((item) => (
                  <div key={`${item.id}-${item.size}`} className="flex gap-4 p-3 bg-[#F7F5F0] rounded-lg border border-[#4A1525]/10">
                    <img src={item.image} alt={item.name} className="w-16 h-20 object-cover rounded" />
                    <div className="flex-1 flex flex-col justify-between">
                      <div>
                        <h4 className="font-serif text-sm font-medium text-[#1C1917]">{item.name}</h4>
                        <span className="text-xs text-[#78716C] font-mono">Size: {item.size}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="font-serif font-bold text-xs text-[#4A1525]">{currencySymbol}{getPrice(item).toLocaleString()}</span>
                        <div className="flex items-center gap-2 border border-[#4A1525]/20 rounded px-1.5 bg-[#FDFBF7]">
                          <button onClick={() => updateQuantity(item.id, item.size, -1)} className="text-[#78716C] hover:text-[#4A1525] p-0.5"><Minus className="w-3 h-3" /></button>
                          <span className="text-xs font-mono font-bold px-1">{item.quantity}</span>
                          <button onClick={() => updateQuantity(item.id, item.size, 1)} className="text-[#78716C] hover:text-[#4A1525] p-0.5"><Plus className="w-3 h-3" /></button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="pt-4 border-t border-[#4A1525]/10 space-y-3">
              <div className="flex justify-between text-sm font-serif">
                <span className="text-[#78716C]">Estimated Atelier Shipping</span>
                <span className="font-mono text-emerald-800 font-medium">Complimentary Courier</span>
              </div>
              <div className="flex justify-between text-base font-serif font-bold text-[#1C1917]">
                <span>Total Acquisition</span>
                <span className="text-[#4A1525]">{currencySymbol}{subtotal.toLocaleString()}</span>
              </div>
              <button 
                onClick={() => alert(`Acquisition confirmed for ${currencySymbol}${subtotal.toLocaleString()}! Our client concierge will contact you for bespoke fitting.`)}
                className="w-full bg-[#4A1525] text-[#FDFBF7] py-3.5 tracking-[0.2em] uppercase font-serif text-xs font-semibold hover:bg-[#6B1D2F] transition-all rounded shadow-md"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Lookbook Inspection Modal */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#FDFBF7] max-w-2xl w-full rounded-2xl overflow-hidden shadow-2xl border border-[#4A1525]/20 flex flex-col md:flex-row">
            <img src={selectedItem.image} alt={selectedItem.name} className="w-full md:w-1/2 h-80 md:h-auto object-cover" />
            <div className="p-6 flex flex-col justify-between space-y-4 flex-1">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono uppercase text-[#C5A880] tracking-widest">{selectedItem.tag}</span>
                  <button onClick={() => setSelectedItem(null)} className="text-[#78716C] hover:text-[#1C1917]"><X className="w-5 h-5" /></button>
                </div>
                <h3 className="text-2xl font-serif text-[#1C1917] mt-1">{selectedItem.name}</h3>
                <span className="text-xl font-serif font-bold text-[#4A1525] block mt-1">{currencySymbol}{getPrice(selectedItem).toLocaleString()}</span>
                
                <p className="text-xs text-[#78716C] mt-3 leading-relaxed">{selectedItem.description}</p>
                <div className="mt-3 p-2.5 bg-[#F7F5F0] rounded border border-[#4A1525]/10 text-[11px] text-[#78716C]">
                  <strong>Provenance:</strong> {selectedItem.provenance}
                </div>
              </div>

              <div>
                <span className="text-xs font-serif uppercase tracking-wider text-[#1C1917] block mb-2 font-medium">Select French Sizing:</span>
                <div className="grid grid-cols-4 gap-2">
                  {['FR 34', 'FR 36', 'FR 38', 'FR 40'].map(sz => (
                    <button
                      key={sz}
                      onClick={() => setSelectedSize(sz)}
                      className={`py-1.5 text-xs font-mono rounded border transition-all ${selectedSize === sz ? 'bg-[#4A1525] text-[#FDFBF7] border-[#4A1525]' : 'border-[#4A1525]/20 text-[#78716C] hover:border-[#4A1525]'}`}
                    >
                      {sz}
                    </button>
                  ))}
                </div>
              </div>

              <button 
                onClick={() => { addToBag(selectedItem, selectedSize); setSelectedItem(null); }}
                className="w-full bg-[#4A1525] text-[#FDFBF7] py-3 tracking-[0.2em] uppercase font-serif text-xs font-semibold hover:bg-[#6B1D2F] transition-all rounded shadow-md"
              >
                Acquire Piece ({selectedSize})
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Atelier Footer */}
      <footer className="bg-[#F7F5F0] border-t border-[#4A1525]/15 py-12 px-6 lg:px-16 text-center text-xs text-[#78716C] space-y-4">
        <BrandLogo name="__BRAND_NAME__" badge="__BADGE_LETTER__" subtitle="SALONS: PARIS · MILANO · TOKYO · NEW YORK" />
        <p className="font-serif">© 2026 __BRAND_NAME__ Haute Couture. All Rights Reserved. Private Appointments Only.</p>
      </footer>
    </div>
  );
}'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)


def generate_fashion_editorial_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''<!DOCTYPE html>
<html lang="en" class="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Haute Couture & Editorial Collection</title>
  
  <!-- Google Fonts: Cinzel & Playfair Display & Plus Jakarta Sans -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Playfair+Display:ital,wght@0,500;0,700;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            'bg-primary': '#FDFBF7',
            'bg-surface': '#FFFFFF',
            'bg-card': '#F7F5F0',
            'accent-primary': '#4A1525',
            'accent-hover': '#6B1D2F',
            'accent-gold': '#C5A880',
            'text-primary': '#1C1917',
            'text-secondary': '#78716C'
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
            serif: ['"Playfair Display"', 'serif'],
            heading: ['"Cinzel"', 'serif'],
            mono: ['"Fira Code"', 'monospace']
          }
        }
      }
    };
  </script>

  <!-- Lucide Vector Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <style>
    body {
      background: #FDFBF7;
      color: #1C1917;
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      margin: 0;
      overflow-x: hidden;
    }
  </style>
</head>
<body class="bg-[#FDFBF7] text-[#1C1917]">
  <div id="root">
    <div class="min-h-screen relative overflow-hidden bg-[#FDFBF7] text-[#1C1917]">
      <canvas id="particles-canvas" class="absolute inset-0 w-full h-full pointer-events-none opacity-70"></canvas>
      
      <!-- Nav -->
      <header class="sticky top-0 z-50 backdrop-blur-xl bg-[#FDFBF7]/90 border-b border-[#4A1525]/10 px-6 lg:px-16 py-4">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center font-serif font-bold text-[#4A1525] bg-[#4A1525]/10 border border-[#4A1525]/30">
              __BADGE_LETTER__
            </div>
            <div class="flex flex-col">
              <span class="font-heading font-extrabold tracking-tight text-xl text-[#1C1917]">__BRAND_NAME__</span>
              <span class="text-[10px] tracking-widest uppercase font-mono text-[#78716C]">ATELIER COUTURE // PARIS</span>
            </div>
          </div>
          <nav class="hidden md:flex items-center gap-10 text-xs uppercase tracking-[0.2em] font-serif text-[#78716C]">
            <span class="text-[#4A1525] font-bold border-b border-[#4A1525]">Collections</span>
            <span class="hover:text-[#4A1525]">Manteaux & Capes</span>
            <span class="hover:text-[#4A1525]">Robes & Soie</span>
            <span class="hover:text-[#4A1525]">Maroquinerie</span>
          </nav>
          <div class="flex items-center gap-4">
            <button class="bg-[#4A1525] text-[#FDFBF7] px-6 py-2.5 text-xs uppercase tracking-widest font-serif font-semibold rounded shadow-md">Acquire</button>
          </div>
        </div>
      </header>

      <!-- Hero -->
      <section class="relative pt-16 pb-20 px-6 lg:px-16 max-w-7xl mx-auto text-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#4A1525]/20 bg-[#F7F5F0] mb-6">
          <span class="text-xs uppercase tracking-[0.25em] text-[#4A1525] font-serif font-semibold">EXCLUSIVITÉ ATELIER // AUTOMNE-HIVER 2026</span>
        </div>
        <h1 class="text-5xl sm:text-7xl font-serif tracking-tight text-[#1C1917] font-normal leading-tight max-w-4xl mx-auto">
          HAUTE COUTURE ÉDITION LIMITÉE
        </h1>
        <p class="text-sm sm:text-base text-[#78716C] max-w-2xl mx-auto font-light mt-4 leading-relaxed">
          A sensory dialogue between architectural silhouette and ethereal drape. Meticulously tailored in Paris using biological Mulberry silk and double-faced Biellese wool.
        </p>
        <div class="pt-8 flex justify-center gap-4">
          <button class="bg-[#4A1525] text-[#FDFBF7] px-8 py-3.5 tracking-[0.2em] uppercase font-serif text-xs font-semibold rounded shadow-lg shadow-[#4A1525]/20">Acquire Collection</button>
          <button class="border border-[#4A1525]/30 text-[#4A1525] px-8 py-3.5 tracking-[0.2em] uppercase font-serif text-xs font-semibold rounded">Inspect Lookbook</button>
        </div>
      </section>

      <!-- Lookbook Grid -->
      <section class="py-12 px-6 lg:px-16 max-w-7xl mx-auto">
        <div class="flex justify-between items-center pb-8 border-b border-[#4A1525]/10">
          <div>
            <h2 class="text-2xl sm:text-3xl font-serif text-[#1C1917]">The 2026 Runway Lookbook</h2>
            <p class="text-xs tracking-widest uppercase font-serif text-[#78716C] mt-1">Direct from Paris Fashion Week</p>
          </div>
          <span class="text-xs font-mono text-[#78716C]">4 PIECES CURATED</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 pt-8">
          <div class="rounded-xl overflow-hidden border border-[#4A1525]/15 bg-[#F7F5F0] p-4 shadow-sm hover:shadow-md transition-shadow">
            <img src="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=900" class="w-full h-80 object-cover rounded-lg" alt="Silk Trench" />
            <div class="pt-3">
              <span class="text-[10px] font-mono text-[#C5A880] uppercase tracking-wider block">EDITION LIMITÉE</span>
              <h3 class="font-serif text-base font-bold text-[#1C1917] mt-1">L'Ombre Silk Trench</h3>
              <span class="font-serif text-sm text-[#4A1525] font-bold">€2,850</span>
            </div>
          </div>
          <div class="rounded-xl overflow-hidden border border-[#4A1525]/15 bg-[#F7F5F0] p-4 shadow-sm hover:shadow-md transition-shadow">
            <img src="https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&q=80&w=900" class="w-full h-80 object-cover rounded-lg" alt="Sculpted Cape" />
            <div class="pt-3">
              <span class="text-[10px] font-mono text-[#C5A880] uppercase tracking-wider block">RUNWAY PIECE 04</span>
              <h3 class="font-serif text-base font-bold text-[#1C1917] mt-1">Velour Sculpted Cape</h3>
              <span class="font-serif text-sm text-[#4A1525] font-bold">€3,400</span>
            </div>
          </div>
          <div class="rounded-xl overflow-hidden border border-[#4A1525]/15 bg-[#F7F5F0] p-4 shadow-sm hover:shadow-md transition-shadow">
            <img src="https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&q=80&w=900" class="w-full h-80 object-cover rounded-lg" alt="Pleated Gown" />
            <div class="pt-3">
              <span class="text-[10px] font-mono text-[#C5A880] uppercase tracking-wider block">HAUTE ATELIER</span>
              <h3 class="font-serif text-base font-bold text-[#1C1917] mt-1">Aura Pleated Gown</h3>
              <span class="font-serif text-sm text-[#4A1525] font-bold">€4,100</span>
            </div>
          </div>
          <div class="rounded-xl overflow-hidden border border-[#4A1525]/15 bg-[#F7F5F0] p-4 shadow-sm hover:shadow-md transition-shadow">
            <img src="https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&q=80&w=900" class="w-full h-80 object-cover rounded-lg" alt="Structured Tote" />
            <div class="pt-3">
              <span class="text-[10px] font-mono text-[#C5A880] uppercase tracking-wider block">PERMANENT ARCHIVE</span>
              <h3 class="font-serif text-base font-bold text-[#1C1917] mt-1">Le Ciel Structured Tote</h3>
              <span class="font-serif text-sm text-[#4A1525] font-bold">€1,650</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Craftsmanship -->
      <section class="py-16 bg-[#F7F5F0] border-y border-[#4A1525]/10 px-6 lg:px-16 mt-12">
        <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <span class="text-xs font-mono text-[#4A1525] font-bold">01 // PROVENANCE</span>
            <h4 class="font-serif text-lg font-bold text-[#1C1917] mt-1">Single-Origin Silk</h4>
            <p class="text-xs text-[#78716C] mt-1">Certified biological Mulberry silk from Italian family mills.</p>
          </div>
          <div>
            <span class="text-xs font-mono text-[#4A1525] font-bold">02 // ARCHITECTURE</span>
            <h4 class="font-serif text-lg font-bold text-[#1C1917] mt-1">Sculptural Drafting</h4>
            <p class="text-xs text-[#78716C] mt-1">Architectural boning retaining volume with fluid motion.</p>
          </div>
          <div>
            <span class="text-xs font-mono text-[#4A1525] font-bold">03 // PERMANENCE</span>
            <h4 class="font-serif text-lg font-bold text-[#1C1917] mt-1">Atelier Warranty</h4>
            <p class="text-xs text-[#78716C] mt-1">Lifetime hand-mending and seasonal pressing at all salons.</p>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="bg-[#F7F5F0] border-t border-[#4A1525]/15 py-12 px-6 text-center text-xs text-[#78716C]">
        <p class="font-serif">© 2026 __BRAND_NAME__ Haute Couture. Paris · Milano · Tokyo · New York.</p>
      </footer>
    </div>
  </div>
  <script type="module" src="/src/main.jsx"></script>
  <script>
    window.addEventListener('DOMContentLoaded', () => {
      const cvs = document.getElementById('particles-canvas');
      if (cvs) {
        const ctx = cvs.getContext('2d');
        const resize = () => { cvs.width = window.innerWidth; cvs.height = window.innerHeight; };
        resize();
        window.addEventListener('resize', resize);
        const pts = Array.from({length: 45}, () => ({
          x: Math.random() * cvs.width,
          y: Math.random() * cvs.height,
          r: Math.random() * 2 + 0.8,
          dx: (Math.random() - 0.5) * 0.4,
          dy: (Math.random() - 0.5) * 0.4
        }));
        const render = () => {
          ctx.clearRect(0, 0, cvs.width, cvs.height);
          ctx.fillStyle = '#C5A880';
          pts.forEach(p => {
            p.x += p.dx; p.y += p.dy;
            if (p.x < 0) p.x = cvs.width;
            if (p.x > cvs.width) p.x = 0;
            if (p.y < 0) p.y = cvs.height;
            if (p.y > cvs.height) p.y = 0;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
          });
          requestAnimationFrame(render);
        };
        render();
      }
      if (typeof lucide !== 'undefined') {
        lucide.createIcons();
      }
    });
  </script>
</body>
</html>'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)
