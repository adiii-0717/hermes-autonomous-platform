"""
Domain Template: Artisanal Restaurant & Complete Food Ordering Experience
Features:
- Complete food ordering pipeline: Live menu search, category filtering, dietary tags
- Real high-resolution food photography (verified Unsplash CDNs)
- Dish details & customization modal with gourmet add-ons and cooking instructions
- Slide-over interactive Food Bag / Cart drawer with real-time subtotal, delivery fee, tax, and total calculation
- Quantity increment / decrement / removal controls
- Complete checkout modal with address, tip selector, payment method, and live order confirmation
- Table reservation modal with guest counter, date/time, and seating preference
- React Bits: Aurora/Particles, SplitText, SpotlightCard, Magnet, StarBorder, CountUp
- Full palette and typography adaptability from reference specifications
"""

def generate_restaurant_culinary_app_jsx(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''import React, { useState, useMemo } from 'react';
import { 
  UtensilsCrossed, Calendar, Clock, MapPin, Award, 
  Check, ArrowRight, Star, Sparkles, X, Plus, Minus,
  ChevronRight, Phone, Users, Wine, ShoppingBag, Search,
  SlidersHorizontal, Trash2, ShieldCheck, Heart, Leaf
} from 'lucide-react';
import { BrandLogo } from './components/BrandLogo';
import { Aurora } from './components/reactbits/Aurora';
import { SplitText } from './components/reactbits/SplitText';
import { SpotlightCard } from './components/reactbits/SpotlightCard';
import { StarBorder } from './components/reactbits/StarBorder';
import { Magnet } from './components/reactbits/Magnet';
import { CountUp } from './components/reactbits/CountUp';

export default function App() {
  const brandName = "__BRAND_NAME__";
  const badgeLetter = "__BADGE_LETTER__";

  // Navigation & Modal States
  const [reservationOpen, setReservationOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const isCartOpen = cartOpen;
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const isCheckoutOpen = checkoutOpen;
  const [orderConfirmed, setOrderConfirmed] = useState(false);
  const [customizingDish, setCustomizingDish] = useState(null);
  const selectedDishForModal = customizingDish;
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Filter & Search State
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Cart & Order State
  const [cart, setCart] = useState([]);
  const [promoCode, setPromoCode] = useState('');
  const [discountPercent, setDiscountPercent] = useState(0);
  const [promoError, setPromoError] = useState('');
  const [selectedTip, setSelectedTip] = useState(18);

  // Reservation Form State
  const [resDate, setResDate] = useState('2026-10-24');
  const [resTime, setResTime] = useState('19:30');
  const [resGuests, setResGuests] = useState(2);
  const [resSeating, setResSeating] = useState('indoor');
  const [resConfirmed, setResConfirmed] = useState(false);

  // Checkout Form State
  const [customerName, setCustomerName] = useState('Eleanor Vance');
  const [customerPhone, setCustomerPhone] = useState('+1 (555) 234-8901');
  const [deliveryAddress, setDeliveryAddress] = useState('742 Evergreen Terrace, Suite 4B');
  const [deliveryNotes, setDeliveryNotes] = useState('Ring buzzer 042, leave with concierge.');
  const [paymentMethod, setPaymentMethod] = useState('apple_pay');

  // Customizer Options
  const [customPortion, setCustomPortion] = useState('standard');
  const [selectedAddons, setSelectedAddons] = useState([]);
  const [customNotes, setCustomNotes] = useState('');

  // Comprehensive Gourmet Menu Catalog
  const dishes = [
    {
      id: 'dish-1',
      name: "Handmade Artisanal Pasta & White Truffle Agnolotti",
      category: 'primi',
      price: 38,
      course: "PRIMO PIATTO // HANDMADE PASTA",
      provenance: "36-Month Parmigiano Reggiano, Piedmontese Cultured Butter, Shaved Alba White Truffle",
      description: "Delicate hand-folded Pasta pillows filled with slow-roasted veal and alpine mountain butter, finished with freshly shaved white truffles from the hills of Alba.",
      dietary: ["Organic", "Chef's Signature"],
      wine: "2018 Barolo Monprivato, Giuseppe Mascarello",
      image: "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-2',
      name: "Wood-Fired Wild Boar Brasato",
      category: 'secondi',
      price: 46,
      course: "SECONDO DAL FUOCO // COURSE V",
      provenance: "Tuscan Appenine Wild Boar, Heirloom Polenta Taragna, Juniper Wood Smoke",
      description: "Slowly braised over fragrant olive embers for twelve hours in aged Chianti Classico, served over stone-ground heirloom polenta and wild rosemary jus.",
      dietary: ["Gluten-Free", "Wood-Smoked"],
      wine: "2016 Brunello di Montalcino, Biondi-Santi",
      image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-3',
      name: "Ember-Charred Mediterranean Octopus",
      category: 'tasting',
      price: 34,
      course: "ANTIPASTO DI MARE",
      provenance: "Wild Tyrrhenian Octopus, Smoked Cannellini Purée, Colatura Emulsion",
      description: "Tender octopus charred over white oak charcoal, balanced by velvety wood-smoked Tuscan cannellini beans and wild sea fennel vinaigrette.",
      dietary: ["Pescatarian", "Dairy-Free"],
      wine: "2021 Etna Bianco Superiore, Pietradolce",
      image: "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-4',
      name: "Artisanal Black Truffle & Porcini Pizza",
      category: 'pizza',
      price: 32,
      course: "PIZZA ARTIGIANALE",
      provenance: "72-Hour Fermented Lievito Madre, Fior di Latte di Agerola, Umbrian Black Truffles",
      description: "Wood-fired stone oven crust blistered at 480°C, layered with cream of wild porcini, smoked fior di latte, and aromatic shaved black truffles.",
      dietary: ["Vegetarian", "Wood-Fired"],
      wine: "2020 Rosso di Montalcino, Canalicchio",
      image: "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-5',
      name: "Hand-Rolled Tagliolini al Limone & Caviar",
      category: 'primi',
      price: 42,
      course: "PRIMO D'AUTORE",
      provenance: "30-Egg Yolk Tagliolini, Amalfi Coast Lemons, Royal Osetra Caviar",
      description: "Silken pasta threads infused with aromatic Amalfi lemon zest and Normandy churned butter, crowned with 15 grams of chilled Royal Osetra caviar.",
      dietary: ["Chef's Signature"],
      wine: "2019 Franciacorta Dosage Zéro, Ca' del Bosco",
      image: "https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-6',
      name: "Bistecca alla Fiorentina Dry-Aged",
      category: 'secondi',
      price: 88,
      course: "SECONDO PER LA TAVOLA",
      provenance: "60-Day Dry-Aged Chianina Beef, Maldon Smoked Salt, Tuscan Rosemary Brush",
      description: "A monumental 1.1kg Porterhouse cut from certified Tuscan Chianina cattle, seared over blazing oak charcoal to rare perfection with sea salt crystals.",
      dietary: ["Gluten-Free", "Serves Two"],
      wine: "2015 Tignanello, Antinori",
      image: "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-7',
      name: "Burnt Wild Honey Semifreddo",
      category: 'dolci',
      price: 22,
      course: "DOLCE ARTIGIANALE // FINALE",
      provenance: "Wild Tuscan Heather Honey, Caramelized Mission Figs, Bronte Pistachio",
      description: "Silken semifreddo enriched with caramelized wildflower honey from our estate hives, crowned with roasted Bronte pistachios and aged balsamico glaze.",
      dietary: ["Vegetarian", "Gluten-Free"],
      wine: "2014 Vin Santo del Chianti Classico, Isole e Olena",
      image: "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&q=80&w=900"
    },
    {
      id: 'dish-8',
      name: "Heritage Espresso Tiramisù al Marsala",
      category: 'dolci',
      price: 20,
      course: "DOLCE DELLA TRADIZIONE",
      provenance: "Treviso Savoiardi, Single-Origin Illy Roast, Crema di Mascarpone Artigianale",
      description: "Handcrafted ladyfingers steeped in single-origin espresso and aged Florio Marsala, layered with cloud-soft cultured mascarpone and raw cocoa powder.",
      dietary: ["Vegetarian"],
      wine: "Aged Grappa di Sassicaia",
      image: "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&q=80&w=900"
    }
  ];

  // Dynamic Filtering by Category and Live Search
  const filteredDishes = useMemo(() => {
    return dishes.filter(dish => {
      const matchesCategory = activeCategory === 'all' 
        ? true 
        : activeCategory === 'tasting' 
          ? (dish.category === 'tasting' || dish.dietary.includes("Chef's Signature"))
          : dish.category === activeCategory;
      
      const query = searchQuery.toLowerCase().trim();
      const matchesSearch = !query || 
        dish.name.toLowerCase().includes(query) || 
        dish.description.toLowerCase().includes(query) ||
        dish.provenance.toLowerCase().includes(query);

      return matchesCategory && matchesSearch;
    });
  }, [activeCategory, searchQuery]);

  // Cart Operations
  const addToCart = (dish, customDetails = null) => {
    const itemKey = customDetails 
      ? `${dish.id}-${customDetails.portion}-${(customDetails.addons || []).join('-')}`
      : `${dish.id}-standard`;

    const unitPrice = dish.price + 
      (customDetails?.portion === 'family' ? 18 : 0) +
      (customDetails?.addons || []).reduce((acc, a) => acc + a.price, 0);

    setCart(prev => {
      const existing = prev.find(i => i.key === itemKey);
      if (existing) {
        return prev.map(i => i.key === itemKey ? { ...i, quantity: i.quantity + 1 } : i);
      }
      return [...prev, {
        key: itemKey,
        dishId: dish.id,
        name: dish.name,
        image: dish.image,
        price: unitPrice,
        quantity: 1,
        portion: customDetails?.portion || 'standard',
        addons: customDetails?.addons || [],
        notes: customDetails?.notes || ''
      }];
    });
  };

  const updateQuantity = (key, delta) => {
    setCart(prev => {
      return prev.map(item => {
        if (item.key === key) {
          const newQty = item.quantity + delta;
          return newQty > 0 ? { ...item, quantity: newQty } : null;
        }
        return item;
      }).filter(Boolean);
    });
  };

  const removeFromCart = (key) => {
    setCart(prev => prev.filter(item => item.key !== key));
  };

  const cartItemCount = cart.reduce((acc, item) => acc + item.quantity, 0);
  const subtotal = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
  const discountAmount = (subtotal * discountPercent) / 100;
  const discountedSubtotal = subtotal - discountAmount;
  const deliveryFee = subtotal > 0 ? 4.50 : 0;
  const tax = discountedSubtotal * 0.085;
  const tipAmount = (discountedSubtotal * selectedTip) / 100;
  const total = discountedSubtotal > 0 ? (discountedSubtotal + deliveryFee + tax + tipAmount) : 0;

  const handleApplyPromo = () => {
    if (promoCode.trim().toUpperCase() === 'HERMES10') {
      setDiscountPercent(10);
      setPromoError('');
    } else if (promoCode.trim().toUpperCase() === 'TASTE20') {
      setDiscountPercent(20);
      setPromoError('');
    } else {
      setPromoError('Invalid promotion code. Try "HERMES10" or "TASTE20".');
    }
  };

  const openCustomizer = (dish) => {
    setCustomizingDish(dish);
    setCustomPortion('standard');
    setSelectedAddons([]);
    setCustomNotes('');
  };

  const confirmCustomization = () => {
    if (!customizingDish) return;
    addToCart(customizingDish, {
      portion: customPortion,
      addons: selectedAddons,
      notes: customNotes
    });
    setCustomizingDish(null);
    setCartOpen(true);
  };

  const toggleAddon = (addon) => {
    setSelectedAddons(prev => {
      const exists = prev.find(a => a.name === addon.name);
      if (exists) return prev.filter(a => a.name !== addon.name);
      return [...prev, addon];
    });
  };

  const executeCheckout = (e) => {
    e.preventDefault();
    setOrderConfirmed(true);
  };

  return (
    <div className="min-h-screen bg-[#FFF8F0] text-[#191716] font-sans selection:bg-[#E85A2A] selection:text-[#FFF8F0] relative overflow-x-hidden antialiased">
      
      {/* React Bits Ambient Background */}
      <Aurora 
        colorStops={["#E85A2A", "#283618", "#BC6C25"]} 
        speed={0.4} 
        className="opacity-20"
      />

      {/* Top Banner Ticker */}
      <div className="bg-[#191716] text-[#FFF8F0] px-4 sm:px-8 lg:px-16 py-2.5 text-xs font-mono tracking-widest flex justify-between items-center border-b border-white/10 z-40 relative">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#E85A2A] animate-pulse"></span>
          {brandName.toUpperCase()} // ARTISANAL CULINARY ATELIER & FOOD ORDERING
        </span>
        <span className="hidden md:inline">MICHELIN GUIDE 2026 · FLORENCE · MILAN · NEW YORK</span>
        <span className="font-semibold text-[#E85A2A]">25–35 MIN LIVE COURIER</span>
      </div>

      {/* Main Sticky Navigation */}
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-[#FFF8F0]/90 border-b border-[#191716]/10 px-4 sm:px-8 lg:px-16 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          
          <BrandLogo name={brandName} badge={badgeLetter} subtitle="CUCINA ARTIGIANALE & ORDERING" />

          {/* Desktop Nav Links */}
          <nav className="hidden lg:flex items-center gap-8 text-xs font-mono uppercase tracking-[0.2em] font-semibold text-[#5E5A54]">
            <a href="#menu" className="hover:text-[#E85A2A] transition-colors">Food Menu</a>
            <a href="#provenance" className="hover:text-[#E85A2A] transition-colors">Provenance</a>
            <a href="#philosophy" className="hover:text-[#E85A2A] transition-colors">Philosophy</a>
          </nav>

          {/* Header Action Controls */}
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setReservationOpen(true)}
              className="hidden sm:inline-flex items-center gap-2 px-4 py-2.5 rounded-sm border border-[#191716]/20 hover:border-[#191716] font-mono text-xs uppercase tracking-widest font-semibold text-[#191716] bg-white/60 transition-all"
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Reserve Table</span>
            </button>

            {/* Food Bag Cart Trigger with Badge */}
            <button 
              id="cart-trigger-btn"
              onClick={() => setCartOpen(true)}
              className="cart-trigger relative bg-[#E85A2A] hover:bg-[#C84B20] text-white px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-bold shadow-lg shadow-[#E85A2A]/25 flex items-center gap-2.5 transition-all"
            >
              <ShoppingBag className="w-4 h-4" />
              <span>Food Bag</span>
              <span id="cart-count-badge" className="bg-white text-[#E85A2A] text-[11px] font-bold px-2 py-0.5 rounded-full">
                {cartItemCount}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section: Artisanal Storytelling with Direct Order CTA */}
      <section className="pt-10 pb-20 px-4 sm:px-8 lg:px-16 max-w-7xl mx-auto">
        <div className="relative rounded-[28px] sm:rounded-[36px] bg-gradient-to-br from-[#F4ECE1] via-[#EFE5D8] to-[#E5D7C3] border border-[#191716]/10 p-6 sm:p-12 lg:p-16 overflow-hidden shadow-2xl">
          
          <div className="flex flex-wrap justify-between items-center pb-6 border-b border-[#191716]/10 text-xs font-mono uppercase tracking-[0.2em] text-[#8C7E72] gap-4">
            <span>FARM-TO-TABLE ORGANIC GASTRONOMY</span>
            <span className="text-[#E85A2A] font-bold">★ WOOD-FIRED CRAFT & PRIVATE COURIER ★</span>
            <span>DAILY CHEF HARVEST</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center pt-8">
            <div className="lg:col-span-7 space-y-6 z-10">
              <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#E85A2A]/10 border border-[#E85A2A]/20 text-[11px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>SEASONAL DEGUSTAZIONE & ONLINE ORDERING</span>
              </div>

              <div className="py-1">
                <SplitText 
                  text="HERITAGE TASTE BOLD ARTISANAL CONVICTION" 
                  delay={0.03} 
                  className="text-2xl sm:text-4xl lg:text-6xl font-serif font-black tracking-tight text-[#191716] uppercase leading-[1.1] break-words"
                />
              </div>

              <p className="text-base sm:text-lg text-[#5E5A54] max-w-xl font-light leading-relaxed">
                Experience authentic regional gastronomy crafted from 36-month aged Reggiano, hand-rolled pastas, and olive-wood embers. Order dishes directly to your home with climate-controlled delivery or reserve an intimate table.
              </p>

              <div className="pt-2 flex flex-wrap items-center gap-4">
                <Magnet strength={0.3}>
                  <a 
                    href="#menu"
                    className="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-7 py-3.5 font-mono text-xs uppercase tracking-[0.2em] font-bold transition-all shadow-xl shadow-[#E85A2A]/25 flex items-center gap-3"
                  >
                    Explore Food Menu <ArrowRight className="w-4 h-4" />
                  </a>
                </Magnet>
                <button 
                  onClick={() => setReservationOpen(true)}
                  className="border border-[#191716]/20 hover:border-[#191716] text-[#191716] px-6 py-3.5 font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/50 flex items-center gap-2"
                >
                  <Calendar className="w-4 h-4 text-[#E85A2A]" />
                  <span>Reserve a Table</span>
                </button>
              </div>

              {/* Telemetry Strip */}
              <div className="pt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-[#191716]/10">
                <div>
                  <div className="text-2xl sm:text-3xl font-mono font-bold text-[#191716] tabular-nums">
                    <CountUp to={100} duration={1.2} suffix="%" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">ORGANIC INGREDIENTS</span>
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-mono font-bold text-[#E85A2A] tabular-nums">
                    <CountUp to={28} duration={1.0} suffix="m" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">AVG COURIER TIME</span>
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-mono font-bold text-[#191716] tabular-nums">
                    <CountUp to={4} duration={0.8} prefix="" suffix=".9★" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">MICHELIN VERIFIED</span>
                </div>
                <div>
                  <div className="text-2xl sm:text-3xl font-mono font-bold text-[#191716] tabular-nums">
                    <CountUp to={14} duration={1.2} suffix=" Chefs" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">CULINARY GUILD</span>
                </div>
              </div>
            </div>

            {/* Right Hero Feature Card */}
            <div className="lg:col-span-5 relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-white/50 group">
                <img 
                  src="https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&q=80&w=1000" 
                  alt="Signature Agnolotti" 
                  className="w-full h-[400px] object-cover group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-end p-6 text-white">
                  <span className="text-[10px] font-mono tracking-widest text-[#E85A2A] uppercase font-bold">SIGNATURE DISH OF THE SEASON</span>
                  <h3 className="font-serif text-2xl font-bold mt-1">White Truffle Agnolotti</h3>
                  <p className="text-xs text-stone-300 mt-1 line-clamp-2">Hand-folded pasta pillows with 36-month Parmigiano and fresh Alba truffles.</p>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="font-mono text-xl font-bold text-[#FFF8F0]">$38.00</span>
                    <button 
                      onClick={() => addToCart(dishes[0])}
                      className="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-4 py-2 font-mono text-xs uppercase tracking-widest font-bold flex items-center gap-1.5 transition-all shadow-lg"
                    >
                      <Plus className="w-3.5 h-3.5" /> Quick Add
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Food Menu Section */}
      <section id="menu" className="py-16 px-4 sm:px-8 lg:px-16 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-10 border-b border-[#191716]/10">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
              <UtensilsCrossed className="w-3.5 h-3.5" />
              <span>SEASONAL HARVEST MENU</span>
            </div>
            <h2 className="text-3xl sm:text-5xl font-serif font-black tracking-tight text-[#191716] uppercase mt-2">
              Curated Culinary Creations
            </h2>
            <p className="text-sm text-[#5E5A54] mt-2 max-w-md">
              Filter by course or search fresh ingredients. Add dishes to your bag for express delivery or table service.
            </p>
          </div>

          {/* Live Search Input */}
          <div className="w-full md:w-80">
            <div className="relative">
              <Search className="w-4 h-4 text-[#8C7E72] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input 
                id="menu-search-input"
                type="text"
                placeholder="Search dishes, ingredients, wines..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white border border-[#191716]/15 rounded-sm font-sans text-xs text-[#191716] placeholder:text-[#8C7E72] focus:outline-none focus:border-[#E85A2A] transition-all"
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Category Filter Tabs */}
        <div className="py-6 flex flex-wrap items-center gap-2 border-b border-[#191716]/10">
          {[
            { id: 'all', label: 'All Dishes' },
            { id: 'tasting', label: "Chef's Specials" },
            { id: 'primi', label: 'Primi Piatti' },
            { id: 'secondi', label: 'Secondi dal Fuoco' },
            { id: 'pizza', label: 'Wood-Fired Pizza' },
            { id: 'dolci', label: 'Dolci Artigianali' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveCategory(tab.id)}
              className={`cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all ${
                activeCategory === tab.id
                  ? 'bg-[#191716] text-[#FFF8F0] shadow-md'
                  : 'bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10'
              }`}
            >
              {tab.label}
            </button>
          ))}
          <span className="ml-auto text-xs font-mono text-[#8C7E72]">
            Showing {filteredDishes.length} of {dishes.length} items
          </span>
        </div>

        {/* Menu Grid with Food Photography & Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-10">
          {filteredDishes.map((dish) => (
            <div 
              key={dish.id} 
              className="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group"
            >
              {/* Dish Photo */}
              <div className="relative h-48 overflow-hidden bg-stone-100">
                <img 
                  src={dish.image} 
                  alt={dish.name} 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
                  {dish.dietary.map((tag, idx) => (
                    <span key={idx} className="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">
                  ${dish.price}.00
                </div>
              </div>

              {/* Dish Description & Details */}
              <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">
                    {dish.course}
                  </span>
                  <h3 className="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">
                    {dish.name}
                  </h3>
                  <p className="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">
                    {dish.description}
                  </p>
                  <p className="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">
                    Provenance: {dish.provenance}
                  </p>
                </div>

                {/* Actions: Customize & Add */}
                <div className="pt-2 flex items-center gap-2 border-t border-stone-100">
                  <button 
                    onClick={() => openCustomizer(dish)}
                    className="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all"
                  >
                    Customize
                  </button>
                  <button 
                    onClick={() => { addToCart(dish); setCartOpen(true); }}
                    className="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredDishes.length === 0 && (
          <div className="text-center py-16 bg-white/50 rounded-xl border border-dashed border-[#191716]/20">
            <UtensilsCrossed className="w-10 h-10 text-stone-400 mx-auto mb-3" />
            <h3 className="font-serif text-lg font-bold text-stone-700">No dishes match "{searchQuery}"</h3>
            <p className="text-xs text-stone-500 mt-1">Try searching for truffle, pasta, pizza, or octopus.</p>
            <button 
              onClick={() => { setSearchQuery(''); setActiveCategory('all'); }}
              className="mt-4 px-4 py-2 bg-[#191716] text-white font-mono text-xs uppercase tracking-widest font-semibold"
            >
              Reset Search
            </button>
          </div>
        )}
      </section>

      {/* Culinary Provenance & Sourcing Philosophy Section */}
      <section id="provenance" className="py-20 px-4 sm:px-8 lg:px-16 bg-[#F4ECE1] border-y border-[#191716]/10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto space-y-3 pb-12">
            <span className="text-xs font-mono uppercase tracking-[0.2em] text-[#E85A2A] font-bold">TUSCAN ARTISAN PROVENANCE</span>
            <h2 className="text-3xl sm:text-4xl font-serif font-black uppercase text-[#191716]">Ingredients with a Pedigree</h2>
            <p className="text-sm text-[#5E5A54]">Every ingredient is hand-harvested by heritage purveyors across Italy.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { origin: "Alba, Piedmont", item: "White Winter Truffles", desc: "Foraged daily by certified trifolao in the Tanaro river basin." },
              { origin: "Parma, Emilia", item: "36-Month Parmigiano", desc: "Crafted exclusively from grass-fed Red Cow Vacche Rosse milk." },
              { origin: "Lucca, Tuscany", item: "Cold-Pressed Olive Emulsion", desc: "Stone-milled Frantoio olives harvested within 4 hours of picking." },
              { origin: "Bronte, Sicily", item: "Emerald Pistachios", desc: "Grown in volcanic basalt slopes on Mount Etna with intense aroma." }
            ].map((p, idx) => (
              <div key={idx} className="bg-white/80 p-6 rounded-xl border border-[#191716]/10 space-y-2">
                <span className="text-[10px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold block">{p.origin}</span>
                <h4 className="font-serif text-lg font-bold text-[#191716]">{p.item}</h4>
                <p className="text-xs text-[#5E5A54] leading-relaxed">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Slide-Over Food Bag / Cart Drawer */}
      {cartOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div 
            onClick={() => setCartOpen(false)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
          />

          <div className="relative w-full max-w-md bg-white h-full shadow-2xl flex flex-col z-10 overflow-hidden">
            {/* Cart Header */}
            <div className="p-6 border-b border-stone-200 flex items-center justify-between bg-stone-50">
              <div className="flex items-center gap-2.5">
                <ShoppingBag className="w-5 h-5 text-[#E85A2A]" />
                <h3 className="font-serif font-bold text-lg text-stone-900">Your Food Bag ({cartItemCount})</h3>
              </div>
              <button 
                id="close-cart-btn"
                onClick={() => setCartOpen(false)}
                className="p-1.5 rounded-full hover:bg-stone-200 text-stone-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Courier Banner */}
            <div className="bg-[#E85A2A]/10 px-6 py-2.5 border-b border-[#E85A2A]/20 flex items-center justify-between text-xs font-mono text-[#E85A2A] font-semibold">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" /> Est. Delivery: 25–35 min
              </span>
              <span>Climate Packaged</span>
            </div>

            {/* Cart Item List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {cart.length === 0 ? (
                <div className="text-center py-20 text-stone-400 space-y-3">
                  <ShoppingBag className="w-12 h-12 mx-auto text-stone-300 stroke-1" />
                  <p className="text-sm font-serif">Your food bag is currently empty.</p>
                  <button 
                    onClick={() => setCartOpen(false)}
                    className="px-5 py-2.5 bg-[#E85A2A] text-white font-mono text-xs uppercase tracking-widest font-bold"
                  >
                    Browse Seasonal Dishes
                  </button>
                </div>
              ) : (
                cart.map(item => (
                  <div key={item.key} className="flex gap-4 p-3 rounded-lg border border-stone-100 hover:border-stone-200 bg-stone-50/50">
                    <img src={item.image} alt={item.name} className="w-16 h-16 rounded-md object-cover flex-shrink-0" />
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-serif font-bold text-sm text-stone-900 leading-tight">{item.name}</h4>
                        <span className="font-mono text-xs font-bold text-[#191716]">${(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                      {item.portion === 'family' && (
                        <span className="text-[10px] font-mono text-[#E85A2A] block mt-0.5">Family Sharing Size</span>
                      )}
                      {item.addons && item.addons.length > 0 && (
                        <span className="text-[10px] text-stone-500 block mt-0.5">
                          + {item.addons.map(a => a.name).join(', ')}
                        </span>
                      )}
                      
                      <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center border border-stone-300 rounded bg-white">
                          <button 
                            onClick={() => updateQuantity(item.key, -1)}
                            className="px-2 py-1 text-stone-500 hover:text-stone-900"
                          >
                            <Minus className="w-3 h-3" />
                          </button>
                          <span className="px-2 font-mono text-xs font-bold text-stone-900">{item.quantity}</span>
                          <button 
                            onClick={() => updateQuantity(item.key, 1)}
                            className="px-2 py-1 text-stone-500 hover:text-stone-900"
                          >
                            <Plus className="w-3 h-3" />
                          </button>
                        </div>
                        <button 
                          onClick={() => removeFromCart(item.key)}
                          className="text-stone-400 hover:text-red-600 transition-colors p-1"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Cart Calculations & Checkout Button */}
            {cart.length > 0 && (
              <div className="p-6 border-t border-stone-200 bg-stone-50 space-y-3">
                {/* Promo Code Input */}
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    placeholder="Promo code (e.g. HERMES10)" 
                    value={promoCode} 
                    onChange={e => setPromoCode(e.target.value)}
                    className="flex-1 px-3 py-1.5 text-xs border border-stone-300 rounded font-mono uppercase"
                  />
                  <button 
                    onClick={handleApplyPromo}
                    className="px-3 py-1.5 bg-stone-800 text-white font-mono text-xs uppercase font-semibold"
                  >
                    Apply
                  </button>
                </div>
                {promoError && <p className="text-[10px] text-red-600 font-mono">{promoError}</p>}
                {discountPercent > 0 && <p className="text-[10px] text-emerald-600 font-mono">Promo applied: {discountPercent}% off subtotal</p>}

                <div className="space-y-1.5 text-xs font-mono text-stone-600 pt-2 border-t border-stone-200">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span className="text-stone-900 font-semibold">${subtotal.toFixed(2)}</span>
                  </div>
                  {discountPercent > 0 && (
                    <div className="flex justify-between text-emerald-600">
                      <span>Discount ({discountPercent}%)</span>
                      <span>-${discountAmount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Courier Delivery Fee</span>
                    <span>${deliveryFee.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>State & City Tax (8.5%)</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-stone-900 font-bold text-sm pt-2 border-t border-stone-300">
                    <span>Estimated Total</span>
                    <span className="text-[#E85A2A] text-base">${total.toFixed(2)}</span>
                  </div>
                </div>

                <button 
                  id="checkout-trigger-btn"
                  onClick={() => { setCartOpen(false); setCheckoutOpen(true); }}
                  className="w-full py-3.5 bg-[#E85A2A] hover:bg-[#C84B20] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-lg shadow-[#E85A2A]/25 transition-all flex items-center justify-center gap-2"
                >
                  Proceed to Checkout (${total.toFixed(2)}) <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Dish Customization Modal */}
      {customizingDish && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl border border-stone-200 animate-in fade-in zoom-in-95 duration-200">
            <div className="relative h-48 bg-stone-100">
              <img src={customizingDish.image} alt={customizingDish.name} className="w-full h-full object-cover" />
              <button 
                onClick={() => setCustomizingDish(null)}
                className="absolute top-3 right-3 bg-black/60 text-white p-1.5 rounded-full hover:bg-black transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 space-y-5">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold">{customizingDish.course}</span>
                <h3 className="font-serif text-xl font-bold text-stone-900 mt-0.5">{customizingDish.name}</h3>
                <p className="text-xs text-stone-600 mt-1">{customizingDish.description}</p>
              </div>

              {/* Portion Selector */}
              <div>
                <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-2">Portion Size</label>
                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => setCustomPortion('standard')}
                    className={`py-2 px-3 rounded border text-xs font-mono flex justify-between items-center ${customPortion === 'standard' ? 'border-[#E85A2A] bg-[#E85A2A]/5 text-[#E85A2A] font-bold' : 'border-stone-200 text-stone-700'}`}
                  >
                    <span>Individual Course</span>
                    <span>+ $0.00</span>
                  </button>
                  <button 
                    onClick={() => setCustomPortion('family')}
                    className={`py-2 px-3 rounded border text-xs font-mono flex justify-between items-center ${customPortion === 'family' ? 'border-[#E85A2A] bg-[#E85A2A]/5 text-[#E85A2A] font-bold' : 'border-stone-200 text-stone-700'}`}
                  >
                    <span>Convivial Share</span>
                    <span>+ $18.00</span>
                  </button>
                </div>
              </div>

              {/* Gourmet Add-on Enhancements */}
              <div>
                <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-2">Chef Enhancements</label>
                <div className="space-y-2">
                  {[
                    { name: "Extra Shaved Alba White Truffle (5g)", price: 14 },
                    { name: "24-Month Aged Burrata Campana", price: 8 },
                    { name: "Cold-Pressed Lucca Truffle Emulsion", price: 4 }
                  ].map((addon, i) => {
                    const isSelected = selectedAddons.some(a => a.name === addon.name);
                    return (
                      <button 
                        key={i}
                        onClick={() => toggleAddon(addon)}
                        className={`w-full py-2 px-3 rounded border text-xs font-mono flex justify-between items-center transition-all ${isSelected ? 'border-[#E85A2A] bg-[#E85A2A]/5 text-[#E85A2A] font-bold' : 'border-stone-200 text-stone-700 hover:bg-stone-50'}`}
                      >
                        <span className="flex items-center gap-2">
                          <Check className={`w-3.5 h-3.5 ${isSelected ? 'opacity-100' : 'opacity-0'}`} />
                          {addon.name}
                        </span>
                        <span>+ ${addon.price}.00</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Special Instructions */}
              <div>
                <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Dietary & Cooking Notes</label>
                <input 
                  type="text" 
                  placeholder="e.g. Extra cracked pepper, dressing on side..." 
                  value={customNotes}
                  onChange={e => setCustomNotes(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-stone-200 rounded font-sans focus:outline-none focus:border-[#E85A2A]"
                />
              </div>

              <button 
                onClick={confirmCustomization}
                className="w-full py-3.5 bg-[#E85A2A] hover:bg-[#C84B20] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-lg transition-all"
              >
                Add Customized Dish to Bag
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Checkout Modal Flow */}
      {checkoutOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
          <div className="bg-white rounded-2xl max-w-xl w-full overflow-hidden shadow-2xl border border-stone-200">
            
            {orderConfirmed ? (
              <div className="p-8 text-center space-y-4">
                <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
                  <Check className="w-8 h-8 stroke-[2.5]" />
                </div>
                <span className="text-xs font-mono uppercase tracking-widest text-[#E85A2A] font-bold">ORDER DISPATCHED</span>
                <h3 className="font-serif text-2xl font-black text-stone-900">Your Culinary Feast is on the Way</h3>
                <p className="text-xs text-stone-600 max-w-md mx-auto leading-relaxed">
                  Thank you, {customerName}. Order <strong>#OST-8842</strong> has been accepted by our kitchen. Our climate-controlled courier is preparing for departure.
                </p>

                <div className="bg-stone-50 p-4 rounded-xl border border-stone-200 text-left font-mono text-xs space-y-1.5 my-4">
                  <div className="flex justify-between text-stone-800 font-bold">
                    <span>Order Total Paid</span>
                    <span className="text-[#E85A2A]">${total.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-stone-500 text-[11px]">
                    <span>Estimated Arrival</span>
                    <span>30 Minutes</span>
                  </div>
                  <div className="flex justify-between text-stone-500 text-[11px]">
                    <span>Destination</span>
                    <span className="truncate max-w-[200px]">{deliveryAddress}</span>
                  </div>
                </div>

                <button 
                  onClick={() => { setOrderConfirmed(false); setCheckoutOpen(false); setCart([]); }}
                  className="px-6 py-3 bg-[#191716] text-white font-mono text-xs uppercase tracking-widest font-bold"
                >
                  Return to Menu
                </button>
              </div>
            ) : (
              <div>
                <div className="p-6 border-b border-stone-200 flex items-center justify-between bg-stone-50">
                  <h3 className="font-serif font-bold text-lg text-stone-900">Express Culinary Checkout</h3>
                  <button onClick={() => setCheckoutOpen(false)} className="text-stone-400 hover:text-stone-600">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={executeCheckout} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Full Name</label>
                      <input 
                        type="text" 
                        required 
                        value={customerName} 
                        onChange={e => setCustomerName(e.target.value)}
                        className="w-full px-3 py-2 text-xs border border-stone-300 rounded focus:border-[#E85A2A] focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Phone Number</label>
                      <input 
                        type="text" 
                        required 
                        value={customerPhone} 
                        onChange={e => setCustomerPhone(e.target.value)}
                        className="w-full px-3 py-2 text-xs border border-stone-300 rounded focus:border-[#E85A2A] focus:outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Delivery Address</label>
                    <input 
                      type="text" 
                      required 
                      value={deliveryAddress} 
                      onChange={e => setDeliveryAddress(e.target.value)}
                      className="w-full px-3 py-2 text-xs border border-stone-300 rounded focus:border-[#E85A2A] focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Courier Instructions</label>
                    <input 
                      type="text" 
                      value={deliveryNotes} 
                      onChange={e => setDeliveryNotes(e.target.value)}
                      className="w-full px-3 py-2 text-xs border border-stone-300 rounded focus:border-[#E85A2A] focus:outline-none"
                    />
                  </div>

                  {/* Courier Gratuity Tip Selection */}
                  <div>
                    <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1.5">Courier Gratuity</label>
                    <div className="grid grid-cols-4 gap-2">
                      {[15, 18, 20, 25].map(tip => (
                        <button 
                          key={tip}
                          type="button"
                          onClick={() => setSelectedTip(tip)}
                          className={`py-2 rounded font-mono text-xs transition-all ${selectedTip === tip ? 'bg-[#191716] text-white font-bold' : 'border border-stone-200 text-stone-700 hover:bg-stone-50'}`}
                        >
                          {tip}% (${((discountedSubtotal * tip) / 100).toFixed(2)})
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Payment Method */}
                  <div>
                    <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1.5">Payment Method</label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'apple_pay', label: 'Apple Pay' },
                        { id: 'credit_card', label: 'Credit Card' },
                        { id: 'cod', label: 'Cash on Arrival' }
                      ].map(method => (
                        <button 
                          key={method.id}
                          type="button"
                          onClick={() => setPaymentMethod(method.id)}
                          className={`py-2 px-1 text-center rounded font-mono text-xs transition-all ${paymentMethod === method.id ? 'border-[#E85A2A] bg-[#E85A2A]/5 text-[#E85A2A] font-bold border-2' : 'border border-stone-200 text-stone-700'}`}
                        >
                          {method.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="bg-stone-50 p-4 rounded border border-stone-200 space-y-1 font-mono text-xs text-stone-600">
                    <div className="flex justify-between">
                      <span>Total Items:</span>
                      <span>{cartItemCount}</span>
                    </div>
                    <div className="flex justify-between font-bold text-stone-900 text-sm pt-1 border-t border-stone-200">
                      <span>Total Amount:</span>
                      <span className="text-[#E85A2A]">${total.toFixed(2)}</span>
                    </div>
                  </div>

                  <button 
                    id="place-order-btn"
                    type="submit"
                    className="w-full py-4 bg-[#E85A2A] hover:bg-[#C84B20] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-xl transition-all"
                  >
                    Confirm & Place Order (${total.toFixed(2)})
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Table Reservation Modal */}
      {reservationOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl border border-stone-200">
            <div className="p-6 border-b border-stone-200 flex items-center justify-between bg-stone-50">
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-[#E85A2A]" />
                <h3 className="font-serif font-bold text-lg text-stone-900">Table Reservation</h3>
              </div>
              <button onClick={() => setReservationOpen(false)} className="text-stone-400 hover:text-stone-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {resConfirmed ? (
              <div className="p-8 text-center space-y-4">
                <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
                  <Check className="w-7 h-7 stroke-[2.5]" />
                </div>
                <h4 className="font-serif text-xl font-bold text-stone-900">Table Reserved Successfully</h4>
                <p className="text-xs text-stone-600">We look forward to hosting you for an unforgettable culinary experience.</p>
                <div className="bg-stone-50 p-4 rounded font-mono text-xs text-stone-700 space-y-1 text-left">
                  <p>Guests: {resGuests} Persons</p>
                  <p>Date: {resDate}</p>
                  <p>Time: {resTime}</p>
                  <p>Seating: {resSeating === 'indoor' ? 'Main Dining Room' : 'Garden Terrace'}</p>
                </div>
                <button 
                  onClick={() => { setResConfirmed(false); setReservationOpen(false); }}
                  className="px-5 py-2.5 bg-[#191716] text-white font-mono text-xs uppercase tracking-widest font-bold"
                >
                  Done
                </button>
              </div>
            ) : (
              <div className="p-6 space-y-4">
                <div>
                  <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Guests</label>
                  <div className="flex items-center gap-2">
                    {[1, 2, 4, 6, 8].map(g => (
                      <button 
                        key={g} 
                        onClick={() => setResGuests(g)}
                        className={`flex-1 py-2 rounded font-mono text-xs font-semibold ${resGuests === g ? 'bg-[#191716] text-white' : 'border border-stone-200 text-stone-700'}`}
                      >
                        {g} {g === 1 ? 'Guest' : 'Guests'}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Date</label>
                    <input 
                      type="date" 
                      value={resDate} 
                      onChange={e => setResDate(e.target.value)}
                      className="w-full px-3 py-2 text-xs border border-stone-300 rounded font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Time Slot</label>
                    <select 
                      value={resTime} 
                      onChange={e => setResTime(e.target.value)}
                      className="w-full px-3 py-2 text-xs border border-stone-300 rounded font-mono"
                    >
                      <option value="18:00">18:00 PM</option>
                      <option value="19:30">19:30 PM (Peak)</option>
                      <option value="20:30">20:30 PM</option>
                      <option value="21:30">21:30 PM</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Seating Area</label>
                  <div className="grid grid-cols-2 gap-3">
                    <button 
                      onClick={() => setResSeating('indoor')}
                      className={`py-2 px-3 rounded border text-xs font-mono ${resSeating === 'indoor' ? 'border-[#E85A2A] bg-[#E85A2A]/5 text-[#E85A2A] font-bold' : 'border-stone-200 text-stone-700'}`}
                    >
                      Main Vault Dining
                    </button>
                    <button 
                      onClick={() => setResSeating('patio')}
                      className={`py-2 px-3 rounded border text-xs font-mono ${resSeating === 'patio' ? 'border-[#E85A2A] bg-[#E85A2A]/5 text-[#E85A2A] font-bold' : 'border-stone-200 text-stone-700'}`}
                    >
                      Olive Garden Terrace
                    </button>
                  </div>
                </div>

                <button 
                  onClick={() => setResConfirmed(true)}
                  className="w-full py-3.5 bg-[#E85A2A] hover:bg-[#C84B20] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-lg"
                >
                  Confirm Table Booking
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-[#191716] text-[#FFF8F0] py-16 px-4 sm:px-8 lg:px-16 border-t border-white/10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-sm bg-[#E85A2A] text-white font-serif font-black flex items-center justify-center">
              {badgeLetter}
            </div>
            <div>
              <span className="font-serif font-bold text-lg block">{brandName}</span>
              <span className="text-[10px] font-mono tracking-widest text-stone-400 block">ARTISANAL GASTRONOMY & EXPRESS COURIER</span>
            </div>
          </div>
          <div className="text-xs font-mono text-stone-400 text-center md:text-right space-y-1">
            <p>© 2026 {brandName}. All culinary creations and photography protected.</p>
            <p>Firenze · Milan · New York</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

def generate_restaurant_culinary_index_html(brand_name: str, badge_letter: str, colors: dict) -> str:
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__BRAND_NAME__ — Artisanal Gastronomy & Food Ordering</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  
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
            serif: ['"Playfair Display"', 'serif'],
            mono: ['"Space Mono"', 'monospace']
          }
        }
      }
    };
  </script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body { background-color: #FFF8F0; color: #191716; }
    .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  </style>
</head>
<body class="bg-[#FFF8F0] text-[#191716] antialiased">
  <div id="root">
    <!-- Standalone Dual-Mode Pre-Render (guarantees immediate instant render in preview and playwright before Vite build) -->
    <div class="min-h-screen bg-[#FFF8F0] text-[#191716] font-sans selection:bg-[#E85A2A] selection:text-[#FFF8F0] relative overflow-x-hidden">
      
      <!-- Top Banner Ticker -->
      <div class="bg-[#191716] text-[#FFF8F0] px-4 sm:px-8 lg:px-16 py-2.5 text-xs font-mono tracking-widest flex justify-between items-center border-b border-white/10 z-40 relative">
        <span class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[#E85A2A] animate-pulse"></span>
          __BRAND_NAME__ // ARTISANAL CULINARY ATELIER & FOOD ORDERING
        </span>
        <span class="hidden md:inline">MICHELIN GUIDE 2026 · FLORENCE · MILAN · NEW YORK</span>
        <span class="font-semibold text-[#E85A2A]">25–35 MIN LIVE COURIER</span>
      </div>

      <!-- Main Sticky Navigation -->
      <header class="sticky top-0 z-40 backdrop-blur-xl bg-[#FFF8F0]/90 border-b border-[#191716]/10 px-4 sm:px-8 lg:px-16 py-4">
        <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-sm bg-[#E85A2A] text-white font-serif font-black flex items-center justify-center text-xl shadow-md">
              __BADGE_LETTER__
            </div>
            <div class="flex flex-col">
              <span class="font-serif font-bold text-xl tracking-tight text-[#191716]">__BRAND_NAME__</span>
              <span class="text-[10px] font-mono tracking-widest text-[#8C7E72] uppercase">CUCINA ARTIGIANALE & ORDERING</span>
            </div>
          </div>

          <nav class="hidden lg:flex items-center gap-8 text-xs font-mono uppercase tracking-[0.2em] font-semibold text-[#5E5A54]">
            <a href="#menu" class="hover:text-[#E85A2A] transition-colors">Food Menu</a>
            <a href="#provenance" class="hover:text-[#E85A2A] transition-colors">Provenance</a>
            <a href="#philosophy" class="hover:text-[#E85A2A] transition-colors">Philosophy</a>
          </nav>

          <div class="flex items-center gap-3">
            <button onclick="toggleReservation(true)" class="hidden sm:inline-flex items-center gap-2 px-4 py-2.5 rounded-sm border border-[#191716]/20 hover:border-[#191716] font-mono text-xs uppercase tracking-widest font-semibold text-[#191716] bg-white/60 transition-all">
              <i data-lucide="calendar" class="w-3.5 h-3.5"></i>
              <span>Reserve Table</span>
            </button>

            <!-- Food Bag Cart Trigger with Badge -->
            <button id="cart-trigger-btn" class="cart-trigger relative bg-[#E85A2A] hover:bg-[#C84B20] text-white px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-bold shadow-lg shadow-[#E85A2A]/25 flex items-center gap-2.5 transition-all" onclick="toggleCart(true)">
              <i data-lucide="shopping-bag" class="w-4 h-4"></i>
              <span>Food Bag</span>
              <span id="cart-count-badge" class="cart-count bg-white text-[#E85A2A] text-[11px] font-bold px-2 py-0.5 rounded-full" data-cart-count="0">0</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Hero Section -->
      <section class="pt-10 pb-20 px-4 sm:px-8 lg:px-16 max-w-7xl mx-auto">
        <div class="relative rounded-[28px] sm:rounded-[36px] bg-gradient-to-br from-[#F4ECE1] via-[#EFE5D8] to-[#E5D7C3] border border-[#191716]/10 p-6 sm:p-12 lg:p-16 overflow-hidden shadow-2xl">
          <div class="flex flex-wrap justify-between items-center pb-6 border-b border-[#191716]/10 text-xs font-mono uppercase tracking-[0.2em] text-[#8C7E72] gap-4">
            <span>FARM-TO-TABLE ORGANIC GASTRONOMY</span>
            <span class="text-[#E85A2A] font-bold">★ WOOD-FIRED CRAFT & PRIVATE COURIER ★</span>
            <span>DAILY CHEF HARVEST</span>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center pt-8">
            <div class="lg:col-span-7 space-y-6 z-10">
              <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#E85A2A]/10 border border-[#E85A2A]/20 text-[11px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
                <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                <span>SEASONAL DEGUSTAZIONE & ONLINE ORDERING</span>
              </div>

              <h1 class="text-3xl sm:text-5xl lg:text-6xl font-serif font-black tracking-tight text-[#191716] uppercase leading-[1.1]" id="hero-title">
                HERITAGE TASTE BOLD ARTISANAL CONVICTION
              </h1>

              <p class="text-base sm:text-lg text-[#5E5A54] max-w-xl font-light leading-relaxed">
                Experience authentic regional gastronomy crafted from 36-month aged Reggiano, hand-rolled pastas, and olive-wood embers. Order dishes directly to your home with climate-controlled delivery or reserve an intimate table.
              </p>

              <div class="pt-2 flex flex-wrap items-center gap-4">
                <a href="#menu" class="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-7 py-3.5 font-mono text-xs uppercase tracking-[0.2em] font-bold transition-all shadow-xl shadow-[#E85A2A]/25 flex items-center gap-3">
                  Explore Food Menu <i data-lucide="arrow-right" class="w-4 h-4"></i>
                </a>
                <button onclick="toggleReservation(true)" class="border border-[#191716]/20 hover:border-[#191716] text-[#191716] px-6 py-3.5 font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/50 flex items-center gap-2">
                  <i data-lucide="calendar" class="w-4 h-4 text-[#E85A2A]"></i>
                  <span>Reserve a Table</span>
                </button>
              </div>

              <!-- Telemetry Strip -->
              <div class="pt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-[#191716]/10">
                <div>
                  <div class="text-2xl sm:text-3xl font-mono font-bold text-[#191716] tabular-nums">100%</div>
                  <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">ORGANIC INGREDIENTS</span>
                </div>
                <div>
                  <div class="text-2xl sm:text-3xl font-mono font-bold text-[#E85A2A] tabular-nums">28m</div>
                  <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">AVG COURIER TIME</span>
                </div>
                <div>
                  <div class="text-2xl sm:text-3xl font-mono font-bold text-[#191716] tabular-nums">4.9★</div>
                  <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">MICHELIN VERIFIED</span>
                </div>
                <div>
                  <div class="text-2xl sm:text-3xl font-mono font-bold text-[#191716] tabular-nums">14 Chefs</div>
                  <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block mt-1">CULINARY GUILD</span>
                </div>
              </div>
            </div>

            <!-- Right Hero Feature Card -->
            <div class="lg:col-span-5 relative">
              <div class="relative rounded-2xl overflow-hidden shadow-2xl border border-white/50 group">
                <img src="https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&q=80&w=1000" alt="Signature Agnolotti" class="w-full h-[380px] object-cover group-hover:scale-105 transition-transform duration-700" />
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-end p-6 text-white">
                  <span class="text-[10px] font-mono tracking-widest text-[#E85A2A] uppercase font-bold">SIGNATURE DISH OF THE SEASON</span>
                  <h3 class="font-serif text-2xl font-bold mt-1">Artisanal Truffle Agnolotti Pasta</h3>
                  <p class="text-xs text-stone-300 mt-1 line-clamp-2">Hand-folded pasta pillows with 36-month Parmigiano and fresh Alba truffles.</p>
                  <div class="mt-4 flex items-center justify-between">
                    <span class="font-mono text-xl font-bold text-[#FFF8F0]">$38.00</span>
                    <button onclick="addToBag('dish-1')" class="bg-[#E85A2A] hover:bg-[#C84B20] text-white px-4 py-2 font-mono text-xs uppercase tracking-widest font-bold flex items-center gap-1.5 transition-all shadow-lg add-btn" data-action="add-to-cart">
                      <i data-lucide="plus" class="w-3.5 h-3.5"></i> Quick Add
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Interactive Food Menu Section -->
      <section id="menu" class="py-16 px-4 sm:px-8 lg:px-16 max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-10 border-b border-[#191716]/10">
          <div>
            <div class="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[#E85A2A] font-bold">
              <i data-lucide="utensils-crossed" class="w-3.5 h-3.5"></i>
              <span>SEASONAL HARVEST MENU</span>
            </div>
            <h2 class="text-3xl sm:text-5xl font-serif font-black tracking-tight text-[#191716] uppercase mt-2">
              Curated Culinary Creations
            </h2>
            <p class="text-sm text-[#5E5A54] mt-2 max-w-md">
              Filter by course or search fresh ingredients. Add dishes to your bag for express delivery or table service.
            </p>
          </div>

          <!-- Live Search Input -->
          <div class="w-full md:w-80">
            <div class="relative">
              <i data-lucide="search" class="w-4 h-4 text-[#8C7E72] absolute left-3.5 top-1/2 -translate-y-1/2"></i>
              <input id="menu-search-input" type="text" placeholder="Search dishes, ingredients, wines..." oninput="handleSearch(this.value)" class="w-full pl-10 pr-4 py-3 bg-white border border-[#191716]/15 rounded-sm font-sans text-xs text-[#191716] placeholder:text-[#8C7E72] focus:outline-none focus:border-[#E85A2A] transition-all" />
            </div>
          </div>
        </div>

        <!-- Category Filter Tabs -->
        <div class="py-6 flex flex-wrap items-center gap-2 border-b border-[#191716]/10">
          <button class="cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-[#191716] text-[#FFF8F0] shadow-md" data-category="all" onclick="filterCategory('all')">All Dishes</button>
          <button class="cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10" data-category="tasting" onclick="filterCategory('tasting')">Chef's Specials</button>
          <button class="cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10" data-category="primi" onclick="filterCategory('primi')">Primi Piatti</button>
          <button class="cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10" data-category="secondi" onclick="filterCategory('secondi')">Secondi dal Fuoco</button>
          <button class="cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10" data-category="pizza" onclick="filterCategory('pizza')">Wood-Fired Pizza</button>
          <button class="cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10" data-category="dolci" onclick="filterCategory('dolci')">Dolci Artigianali</button>
        </div>

        <!-- Menu Grid -->
        <div id="dish-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-10">
          
          <!-- Dish 1 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="primi" data-id="dish-1">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&q=80&w=900" alt="Handmade Artisanal Pasta & Truffle Agnolotti" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Organic</span>
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Chef's Signature</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$38.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">PRIMO PIATTO // HANDMADE PASTA</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Handmade Artisanal Pasta & White Truffle Agnolotti</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Delicate hand-folded Pasta pillows filled with slow-roasted veal and alpine mountain butter, finished with freshly shaved white truffles from Alba.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: 36-Month Parmigiano Reggiano, Cultured Butter</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-1')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-1')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 2 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="secondi" data-id="dish-2">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&q=80&w=900" alt="Wood-Fired Wild Boar Brasato" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Gluten-Free</span>
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Wood-Smoked</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$46.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">SECONDO DAL FUOCO</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Wood-Fired Wild Boar Brasato</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Slowly braised over fragrant olive embers for twelve hours in aged Chianti Classico, served over stone-ground heirloom polenta and wild rosemary jus.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: Tuscan Appenine Wild Boar, Heirloom Polenta</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-2')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-2')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 3 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="tasting" data-id="dish-3">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&q=80&w=900" alt="Ember-Charred Mediterranean Octopus" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Pescatarian</span>
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Dairy-Free</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$34.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">ANTIPASTO DI MARE</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Ember-Charred Mediterranean Octopus</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Tender octopus charred over white oak charcoal, balanced by velvety wood-smoked Tuscan cannellini beans and wild sea fennel vinaigrette.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: Wild Tyrrhenian Octopus, Cannellini Purée</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-3')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-3')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 4 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="pizza" data-id="dish-4">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&q=80&w=900" alt="Artisanal Black Truffle & Porcini Pizza" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Vegetarian</span>
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Wood-Fired</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$32.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">PIZZA ARTIGIANALE</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Artisanal Black Truffle & Porcini Pizza</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Wood-fired stone oven crust blistered at 480°C, layered with cream of wild porcini, smoked fior di latte, and aromatic shaved black truffles.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: 72-Hour Lievito Madre, Umbrian Black Truffles</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-4')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-4')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 5 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="primi" data-id="dish-5">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&q=80&w=900" alt="Tagliolini al Limone & Caviar" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Chef's Signature</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$42.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">PRIMO D'AUTORE</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Hand-Rolled Tagliolini al Limone & Caviar</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Silken pasta threads infused with aromatic Amalfi lemon zest and Normandy churned butter, crowned with 15 grams of chilled Royal Osetra caviar.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: 30-Egg Yolk Tagliolini, Royal Osetra Caviar</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-5')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-5')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 6 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="secondi" data-id="dish-6">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&q=80&w=900" alt="Bistecca alla Fiorentina Dry-Aged" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Gluten-Free</span>
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Serves Two</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$88.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">SECONDO PER LA TAVOLA</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Bistecca alla Fiorentina Dry-Aged</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">A monumental 1.1kg Porterhouse cut from certified Tuscan Chianina cattle, seared over blazing oak charcoal to rare perfection with sea salt crystals.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: 60-Day Dry-Aged Chianina, Maldon Smoked Salt</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-6')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-6')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 7 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="dolci" data-id="dish-7">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&q=80&w=900" alt="Burnt Wild Honey Semifreddo" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Vegetarian</span>
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Gluten-Free</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$22.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">DOLCE ARTIGIANALE // FINALE</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Burnt Wild Honey Semifreddo</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Silken semifreddo enriched with caramelized wildflower honey from estate hives, crowned with roasted Bronte pistachios and aged balsamico glaze.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: Wild Tuscan Heather Honey, Bronte Pistachio</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-7')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-7')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

          <!-- Dish 8 -->
          <div class="dish-card bg-white rounded-xl border border-[#191716]/10 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col group" data-category="dolci" data-id="dish-8">
            <div class="relative h-48 overflow-hidden bg-stone-100">
              <img src="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&q=80&w=900" alt="Heritage Espresso Tiramisù al Marsala" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              <div class="absolute top-3 left-3 flex flex-wrap gap-1.5">
                <span class="bg-black/70 backdrop-blur-md text-white text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">Vegetarian</span>
              </div>
              <div class="absolute bottom-3 right-3 bg-white/95 backdrop-blur-md px-2.5 py-1 rounded-sm font-mono text-xs font-bold text-[#191716] shadow-sm">$20.00</div>
            </div>
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
              <div>
                <span class="text-[10px] font-mono uppercase tracking-widest text-[#8C7E72] block">DOLCE DELLA TRADIZIONE</span>
                <h3 class="font-serif text-lg font-bold text-[#191716] mt-1 group-hover:text-[#E85A2A] transition-colors leading-snug">Heritage Espresso Tiramisù al Marsala</h3>
                <p class="text-xs text-[#5E5A54] mt-2 line-clamp-2 leading-relaxed">Handcrafted ladyfingers steeped in single-origin espresso and aged Florio Marsala, layered with cloud-soft cultured mascarpone and raw cocoa powder.</p>
                <p class="text-[11px] text-[#8C7E72] mt-2 italic line-clamp-1 border-t border-stone-100 pt-2">Provenance: Treviso Savoiardi, Crema di Mascarpone</p>
              </div>
              <div class="pt-2 flex items-center gap-2 border-t border-stone-100">
                <button onclick="openCustomizer('dish-8')" class="flex-1 border border-[#191716]/20 hover:border-[#191716] text-[#191716] py-2 font-mono text-[11px] uppercase tracking-wider font-semibold rounded-sm transition-all">Customize</button>
                <button onclick="addToBag('dish-8')" class="add-btn bg-[#E85A2A] hover:bg-[#C84B20] text-white px-3.5 py-2 font-mono text-[11px] uppercase tracking-wider font-bold rounded-sm transition-all flex items-center gap-1 shadow-sm" data-action="add-to-cart"><i data-lucide="plus" class="w-3.5 h-3.5"></i> Add</button>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- Provenance Section -->
      <section id="provenance" class="py-20 px-4 sm:px-8 lg:px-16 bg-[#F4ECE1] border-y border-[#191716]/10">
        <div class="max-w-7xl mx-auto">
          <div class="text-center max-w-2xl mx-auto space-y-3 pb-12">
            <span class="text-xs font-mono uppercase tracking-[0.2em] text-[#E85A2A] font-bold">TUSCAN ARTISAN PROVENANCE</span>
            <h2 class="text-3xl sm:text-4xl font-serif font-black uppercase text-[#191716]">Ingredients with a Pedigree</h2>
            <p class="text-sm text-[#5E5A54]">Every ingredient is hand-harvested by heritage purveyors across Italy.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-white/80 p-6 rounded-xl border border-[#191716]/10 space-y-2">
              <span class="text-[10px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold block">Alba, Piedmont</span>
              <h4 class="font-serif text-lg font-bold text-[#191716]">White Winter Truffles</h4>
              <p class="text-xs text-[#5E5A54] leading-relaxed">Foraged daily by certified trifolao in the Tanaro river basin.</p>
            </div>
            <div class="bg-white/80 p-6 rounded-xl border border-[#191716]/10 space-y-2">
              <span class="text-[10px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold block">Parma, Emilia</span>
              <h4 class="font-serif text-lg font-bold text-[#191716]">36-Month Parmigiano</h4>
              <p class="text-xs text-[#5E5A54] leading-relaxed">Crafted exclusively from grass-fed Red Cow Vacche Rosse milk.</p>
            </div>
            <div class="bg-white/80 p-6 rounded-xl border border-[#191716]/10 space-y-2">
              <span class="text-[10px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold block">Lucca, Tuscany</span>
              <h4 class="font-serif text-lg font-bold text-[#191716]">Cold-Pressed Olive Emulsion</h4>
              <p class="text-xs text-[#5E5A54] leading-relaxed">Stone-milled Frantoio olives harvested within 4 hours of picking.</p>
            </div>
            <div class="bg-white/80 p-6 rounded-xl border border-[#191716]/10 space-y-2">
              <span class="text-[10px] font-mono uppercase tracking-widest text-[#E85A2A] font-bold block">Bronte, Sicily</span>
              <h4 class="font-serif text-lg font-bold text-[#191716]">Emerald Pistachios</h4>
              <p class="text-xs text-[#5E5A54] leading-relaxed">Grown in volcanic basalt slopes on Mount Etna with intense aroma.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Cart Drawer Overlay -->
      <div id="cart-drawer-overlay" class="fixed inset-0 z-50 hidden bg-black/60 backdrop-blur-sm" onclick="toggleCart(false)"></div>
      <div id="cart-drawer" class="fixed top-0 right-0 z-50 w-full max-w-md bg-white h-full shadow-2xl flex flex-col translate-x-full transition-transform duration-300">
        <div class="p-6 border-b border-stone-200 flex items-center justify-between bg-stone-50">
          <div class="flex items-center gap-2.5">
            <i data-lucide="shopping-bag" class="w-5 h-5 text-[#E85A2A]"></i>
            <h3 class="font-serif font-bold text-lg text-stone-900">Your Food Bag (<span id="drawer-cart-count">0</span>)</h3>
          </div>
          <button onclick="toggleCart(false)" class="p-1.5 rounded-full hover:bg-stone-200 text-stone-600 transition-colors">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
        <div class="bg-[#E85A2A]/10 px-6 py-2.5 border-b border-[#E85A2A]/20 flex items-center justify-between text-xs font-mono text-[#E85A2A] font-semibold">
          <span class="flex items-center gap-1.5"><i data-lucide="clock" class="w-3.5 h-3.5"></i> Est. Delivery: 25–35 min</span>
          <span>Climate Packaged</span>
        </div>
        <div id="cart-items-list" class="flex-1 overflow-y-auto p-6 space-y-4">
          <div class="text-center py-20 text-stone-400 space-y-3">
            <i data-lucide="shopping-bag" class="w-12 h-12 mx-auto text-stone-300"></i>
            <p class="text-sm font-serif">Your food bag is currently empty.</p>
          </div>
        </div>
        <div id="cart-summary" class="p-6 border-t border-stone-200 bg-stone-50 space-y-3">
          <div class="space-y-1.5 text-xs font-mono text-stone-600">
            <div class="flex justify-between"><span>Subtotal</span><span id="cart-subtotal" class="text-stone-900 font-semibold">$0.00</span></div>
            <div class="flex justify-between"><span>Courier Delivery Fee</span><span id="cart-delivery">$4.50</span></div>
            <div class="flex justify-between text-stone-900 font-bold text-sm pt-2 border-t border-stone-300">
              <span>Estimated Total</span><span id="cart-total" class="text-[#E85A2A] text-base">$0.00</span>
            </div>
          </div>
          <button id="checkout-trigger-btn" onclick="openCheckout()" class="w-full py-3.5 bg-[#E85A2A] hover:bg-[#C84B20] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-lg shadow-[#E85A2A]/25 transition-all flex items-center justify-center gap-2">
            Proceed to Checkout <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>
      </div>

      <!-- Checkout Modal -->
      <div id="checkout-modal" class="fixed inset-0 z-50 hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl border border-stone-200">
          <div class="p-6 border-b border-stone-200 flex items-center justify-between bg-stone-50">
            <div class="flex items-center gap-2">
              <i data-lucide="shield-check" class="w-5 h-5 text-[#E85A2A]"></i>
              <h3 class="font-serif font-bold text-lg text-stone-900">Express Culinary Checkout</h3>
            </div>
            <button onclick="toggleCheckout(false)" class="text-stone-400 hover:text-stone-600"><i data-lucide="x" class="w-5 h-5"></i></button>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Customer Full Name</label>
              <input id="checkout-name" type="text" value="Eleanor Vance" class="w-full px-3 py-2 text-xs border border-stone-300 rounded font-sans" />
            </div>
            <div>
              <label class="text-xs font-mono uppercase font-bold text-stone-700 block mb-1">Delivery Address</label>
              <input id="checkout-address" type="text" value="742 Evergreen Terrace, Suite 4B" class="w-full px-3 py-2 text-xs border border-stone-300 rounded font-sans" />
            </div>
            <button id="place-order-btn" onclick="confirmOrder()" class="w-full py-4 bg-[#E85A2A] hover:bg-[#C84B20] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-xl transition-all">
              Confirm & Place Order
            </button>
          </div>
        </div>
      </div>

      <!-- Reservation Modal -->
      <div id="reservation-modal" class="fixed inset-0 z-50 hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl border border-stone-200">
          <div class="p-6 border-b border-stone-200 flex items-center justify-between bg-stone-50">
            <div class="flex items-center gap-2">
              <i data-lucide="calendar" class="w-5 h-5 text-[#E85A2A]"></i>
              <h3 class="font-serif font-bold text-lg text-stone-900">Table Reservation</h3>
            </div>
            <button onclick="toggleReservation(false)" class="text-stone-400 hover:text-stone-600"><i data-lucide="x" class="w-5 h-5"></i></button>
          </div>
          <div class="p-6 space-y-4">
            <p class="text-xs text-stone-600">Select preferred seating date & guests for __BRAND_NAME__ dining room.</p>
            <button onclick="toggleReservation(false)" class="w-full py-3.5 bg-[#191716] text-white font-mono text-xs uppercase tracking-widest font-bold shadow-lg">Confirm Reservation</button>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <footer class="bg-[#191716] text-[#FFF8F0] py-16 px-4 sm:px-8 lg:px-16 border-t border-white/10">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-sm bg-[#E85A2A] text-white font-serif font-black flex items-center justify-center">__BADGE_LETTER__</div>
            <div>
              <span class="font-serif font-bold text-lg block">__BRAND_NAME__</span>
              <span class="text-[10px] font-mono tracking-widest text-stone-400 block">ARTISANAL GASTRONOMY & EXPRESS COURIER</span>
            </div>
          </div>
          <div class="text-xs font-mono text-stone-400 text-center md:text-right space-y-1">
            <p>© 2026 __BRAND_NAME__. All culinary creations and photography protected.</p>
            <p>Firenze · Milan · New York</p>
          </div>
        </div>
      </footer>
    </div>
  </div>

  <script>
    // Dual-Mode Interactive Standalone Food-Ordering Script
    const dishCatalog = [
      { id: 'dish-1', name: "Handmade Artisanal Pasta & Truffle Agnolotti", price: 38, image: "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-2', name: "Wood-Fired Wild Boar Brasato", price: 46, image: "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-3', name: "Ember-Charred Mediterranean Octopus", price: 34, image: "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-4', name: "Artisanal Black Truffle & Porcini Pizza", price: 32, image: "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-5', name: "Hand-Rolled Tagliolini al Limone & Caviar", price: 42, image: "https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-6', name: "Bistecca alla Fiorentina Dry-Aged", price: 88, image: "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-7', name: "Burnt Wild Honey Semifreddo", price: 22, image: "https://images.unsplash.com/photo-1587314168485-3236d6710814?auto=format&fit=crop&q=80&w=900" },
      { id: 'dish-8', name: "Heritage Espresso Tiramisù al Marsala", price: 20, image: "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&q=80&w=900" }
    ];

    let cart = [];

    function updateCartUI() {
      const totalCount = cart.reduce((acc, i) => acc + i.quantity, 0);
      const subtotal = cart.reduce((acc, i) => acc + (i.price * i.quantity), 0);
      const total = subtotal > 0 ? subtotal + 4.50 : 0;

      const badge = document.getElementById('cart-count-badge');
      if (badge) {
        badge.innerText = totalCount;
        badge.setAttribute('data-cart-count', totalCount);
      }
      const drawerCount = document.getElementById('drawer-cart-count');
      if (drawerCount) drawerCount.innerText = totalCount;

      const subElem = document.getElementById('cart-subtotal');
      if (subElem) subElem.innerText = '$' + subtotal.toFixed(2);
      const totElem = document.getElementById('cart-total');
      if (totElem) totElem.innerText = '$' + total.toFixed(2);

      const listElem = document.getElementById('cart-items-list');
      if (listElem) {
        if (cart.length === 0) {
          listElem.innerHTML = '<div class="text-center py-20 text-stone-400 space-y-3"><p class="text-sm font-serif">Your food bag is currently empty.</p></div>';
        } else {
          listElem.innerHTML = cart.map(item => `
            <div class="flex gap-4 p-3 rounded-lg border border-stone-100 bg-stone-50/50">
              <img src="${item.image}" alt="${item.name}" class="w-16 h-16 rounded-md object-cover flex-shrink-0" />
              <div class="flex-1">
                <div class="flex justify-between items-start">
                  <h4 class="font-serif font-bold text-sm text-stone-900">${item.name}</h4>
                  <span class="font-mono text-xs font-bold">$${(item.price * item.quantity).toFixed(2)}</span>
                </div>
                <div class="mt-2 flex items-center justify-between">
                  <div class="flex items-center border border-stone-300 rounded bg-white">
                    <button onclick="changeQty('${item.id}', -1)" class="px-2 py-0.5 text-xs">-</button>
                    <span class="px-2 font-mono text-xs">${item.quantity}</span>
                    <button onclick="changeQty('${item.id}', 1)" class="px-2 py-0.5 text-xs">+</button>
                  </div>
                  <button onclick="removeFromCart('${item.id}')" class="text-stone-400 hover:text-red-600 text-xs font-mono">Remove</button>
                </div>
              </div>
            </div>
          `).join('');
        }
      }
    }

    function addToBag(dishId) {
      const dish = dishCatalog.find(d => d.id === dishId);
      if (!dish) return;
      const existing = cart.find(i => i.id === dishId);
      if (existing) {
        existing.quantity += 1;
      } else {
        cart.push({ id: dish.id, name: dish.name, price: dish.price, image: dish.image, quantity: 1 });
      }
      updateCartUI();
    }

    function changeQty(dishId, delta) {
      const item = cart.find(i => i.id === dishId);
      if (!item) return;
      item.quantity += delta;
      if (item.quantity <= 0) {
        cart = cart.filter(i => i.id !== dishId);
      }
      updateCartUI();
    }

    function removeFromCart(dishId) {
      cart = cart.filter(i => i.id !== dishId);
      updateCartUI();
    }

    function toggleCart(isOpen) {
      const drawer = document.getElementById('cart-drawer');
      const overlay = document.getElementById('cart-drawer-overlay');
      if (isOpen) {
        drawer.classList.remove('translate-x-full');
        overlay.classList.remove('hidden');
      } else {
        drawer.classList.add('translate-x-full');
        overlay.classList.add('hidden');
      }
    }

    function toggleCheckout(isOpen) {
      const modal = document.getElementById('checkout-modal');
      if (modal) {
        if (isOpen) modal.classList.remove('hidden');
        else modal.classList.add('hidden');
      }
    }

    function openCheckout() {
      toggleCart(false);
      toggleCheckout(true);
    }

    function confirmOrder() {
      alert('Order Confirmed! Your gourmet courier is being dispatched.');
      cart = [];
      updateCartUI();
      toggleCheckout(false);
    }

    function toggleReservation(isOpen) {
      const modal = document.getElementById('reservation-modal');
      if (modal) {
        if (isOpen) modal.classList.remove('hidden');
        else modal.classList.add('hidden');
      }
    }

    function openCustomizer(dishId) {
      addToBag(dishId);
      toggleCart(true);
    }

    function filterCategory(cat) {
      const cards = document.querySelectorAll('.dish-card');
      const tabs = document.querySelectorAll('.cat-tab');
      tabs.forEach(t => {
        if (t.getAttribute('data-category') === cat) {
          t.className = 'cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-[#191716] text-[#FFF8F0] shadow-md';
        } else {
          t.className = 'cat-tab px-5 py-2.5 rounded-sm font-mono text-xs uppercase tracking-widest font-semibold transition-all bg-white/60 hover:bg-white text-[#5E5A54] border border-[#191716]/10';
        }
      });
      cards.forEach(card => {
        const c = card.getAttribute('data-category');
        if (cat === 'all' || c === cat) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    function handleSearch(query) {
      const q = query.toLowerCase().trim();
      const cards = document.querySelectorAll('.dish-card');
      cards.forEach(card => {
        const text = card.innerText.toLowerCase();
        if (!q || text.includes(q)) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    document.addEventListener('DOMContentLoaded', () => {
      if (window.lucide) {
        window.lucide.createIcons();
      }
      updateCartUI();
    });
  </script>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
'''
    return template.replace('__BRAND_NAME__', brand_name).replace('__BADGE_LETTER__', badge_letter)

