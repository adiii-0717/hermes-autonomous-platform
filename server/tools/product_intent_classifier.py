"""
Product Intent Classifier Module for Hermes Dev Studio.
Analyzes user prompts to separate the PRIMARY PRODUCT (domain app with full functional features)
from VISUAL ENHANCEMENTS (3D graphics, animations, glassmorphism, cinematic themes).
Ensures generated applications remain fully functional domain products enhanced by visuals,
rather than abstract visual demos missing functional business logic.
"""

import re
from typing import Dict, List, Any, Tuple

class ProductIntentClassifier:
    """Classifies user prompt intent into primary product features vs visual enhancements."""

    DOMAIN_PATTERNS = {
        "RESTAURANT_FOOD": {
            "keywords": ["restaurant", "food", "dining", "bistro", "cafe", "kitchen", "crave", "dishes", "menu", "order food", "food ordering", "takeaway", "delivery", "culinary", "gourmet", "chef", "pizza", "burger", "pasta", "bakery", "sushi", "meal", "delicious", "recipes"],
            "primary_product": "Restaurant & Online Food Ordering Platform",
            "core_features": [
                "Hero section with brand storytelling, signature dish showcase, and order now / reserve table CTAs",
                "Interactive Food Menu with category filters (Chef's Specials, Wood-Fired Pizza, Gourmet Burgers, Handmade Pasta, Desserts)",
                "Individual dish cards with high-res food photography, pricing, dietary badges, and Quick Add",
                "Dish details modal with customization options (portion size, extra toppings, spice level, special cooking instructions)",
                "Live Food Bag drawer with delivery time estimate (25-35 mins), item modification, and promo code support",
                "Checkout modal with delivery address, tip selector, payment method, and live order confirmation",
                "Table reservation booking widget with date, time, and guest count selector"
            ]
        },
        "FOOTWEAR_SNEAKERS": {
            "keywords": ["sneaker", "sneakers", "shoe", "shoes", "footwear", "kicks", "boots", "jordans", "yeezy"],
            "primary_product": "High-Performance Sneaker Storefront & Footwear Experience",
            "core_features": [
                "Hero section with featured footwear collection and 3D silhouette inspection",
                "Sneaker catalog grid with filtering by category (Lifestyle, Running, Basketball, Trail)",
                "Individual sneaker cards with pricing, star rating, color swatches, and Quick Add",
                "Interactive product detail modal with US Men's size selector (US 7.5 - 12)",
                "Functional Shopping Bag drawer with item count badge, quantity modification, and subtotal calculation",
                "Checkout modal flow with shipping and payment steps",
                "Search bar and category navigation"
            ]
        },
        "STREAMING_ENTERTAINMENT": {
            "keywords": ["movie", "movies", "cinema", "series", "streaming", "video", "film", "watch", "theater", "showtime"],
            "primary_product": "Streaming Media & Entertainment Platform",
            "core_features": [
                "Hero billboard featuring trending blockbuster with backdrop and trailer play CTA",
                "Category carousels / rows (Trending Now, Action, Sci-Fi, Drama, Top Rated)",
                "Media cards with IMDb ratings, age classification, duration, and watchlist toggle",
                "Interactive media modal with video player preview, synopsis, cast, and episode guide",
                "Search bar with live title filtering"
            ]
        },
        "FASHION_APPAREL": {
            "keywords": ["clothing", "apparel", "fashion", "streetwear", "boutique", "dress", "wardrobe", "outfit"],
            "primary_product": "Fashion & Designer Apparel Storefront",
            "core_features": [
                "Hero section with seasonal lookbook and new arrivals showcase",
                "Catalog grid with category filters (Tops, Outerwear, Bottoms, Accessories)",
                "Apparel product cards with high-res editorial imagery, pricing, and size options",
                "Product detail modal with fabric details, care instructions, and fit guide",
                "Shopping bag slide-over drawer with item modification",
                "Checkout flow with express payment"
            ]
        },
        "E_COMMERCE": {
            "keywords": ["e-commerce", "ecommerce", "store", "shop", "storefront", "products", "cart", "buying", "checkout", "shopping"],
            "primary_product": "E-Commerce Storefront & Shopping Application",
            "core_features": [
                "Hero section with featured collection and CTA",
                "Product catalog grid with filtering by category, price, and status",
                "Individual product cards with high-res visuals, pricing, rating, and Quick Add",
                "Interactive product detail view / modal with variant selectors",
                "Functional Shopping Cart drawer with item count badge, quantity modification, and subtotal calculation",
                "Checkout modal flow with shipping and payment steps",
                "Search bar and category navigation"
            ]
        },
        "DASHBOARD": {
            "keywords": ["dashboard", "educational", "learning", "admin", "portal", "student", "teacher", "analytics dashboard", "control panel", "management", "kpi", "crm"],
            "primary_product": "Interactive Analytics & Management Dashboard",
            "core_features": [
                "Overview header with key performance indicator (KPI) metric cards",
                "Interactive charts and visualization widgets (progress, trends, activity)",
                "Data tables with status badges, pagination, and search/filter inputs",
                "Sidebar navigation with active state indicators",
                "User profile summary and notifications panel",
                "Actionable widgets (e.g. assignment submit, status toggles, quick actions)"
            ]
        },
        "PORTFOLIO": {
            "keywords": ["portfolio", "cinematic", "personal", "showcase", "creator", "designer", "developer", "resume", "work", "cv", "photographer"],
            "primary_product": "Professional Creative Portfolio & Project Showcase",
            "core_features": [
                "Hero intro section with headline, bio overview, and quick links",
                "Filterable Project Showcase gallery with tag filtering (Web, Mobile, 3D, Design)",
                "Detailed project modal / view showing client, timeline, tech stack, and highlights",
                "Interactive skills & technical proficiency grid/matrix",
                "Experience / Timeline section detailing background and achievements",
                "Contact section with working interactive form and social links"
            ]
        },
        "SAAS_ANALYTICS": {
            "keywords": ["saas", "analytics", "platform", "metrics", "mrr", "b2b", "subscription", "cloud", "reporting"],
            "primary_product": "SaaS Product Analytics & Performance Platform",
            "core_features": [
                "Real-time KPI metrics banner (MRR, ARR, Churn Rate, Active Users, LTV)",
                "Multi-dimensional interactive trend charts with timeframe toggles (7D, 30D, 1Y)",
                "User retention and funnel breakdown table with sorting and filtering",
                "Subscription / Pricing tier management component",
                "Export / Report generation trigger buttons",
                "Settings & team permissions navigation tab"
            ]
        }
    }

    VISUAL_ENHANCEMENT_PATTERNS = {
        "3D": ["3d", "three.js", "webgl", "canvas 3d", "interactive 3d", "spatial", "orthographic", "mesh", "model viewer"],
        "CINEMATIC": ["cinematic", "ambient", "lighting", "glow", "dramatic", "moody", "dark mode", "neon", "immersive"],
        "GLASSMORPHISM": ["glassmorphism", "frosted", "translucent", "glass", "backdrop blur", "modern overlay"],
        "ANIMATED": ["animated", "micro-interactions", "scroll animations", "parallax", "framer", "transitions", "motion"]
    }

    def classify_intent(self, user_prompt: str) -> Dict[str, Any]:
        """Parses prompt to separate primary product requirements from visual enhancements."""
        prompt_lower = user_prompt.lower()
        
        # 1. Identify Domain Type
        matched_domain = "GENERIC_WEB_APP"
        max_score = 0
        domain_info = None

        for domain_key, data in self.DOMAIN_PATTERNS.items():
            score = sum(1 for kw in data["keywords"] if kw in prompt_lower)
            if score > max_score:
                max_score = score
                matched_domain = domain_key
                domain_info = data

        if not domain_info:
            primary_product = "Custom Web Application"
            core_features = [
                "Navigation bar with branding and main section links",
                "Hero section explaining purpose and key call-to-action",
                "Primary interactive feature workspace / content area",
                "Data display / cards container with interactive controls",
                "Settings / Filter controls panel",
                "Footer with links and attribution"
            ]
        else:
            primary_product = domain_info["primary_product"]
            core_features = domain_info["core_features"]

        # 2. Identify Visual Enhancements
        detected_enhancements = []
        for enhancement_name, keywords in self.VISUAL_ENHANCEMENT_PATTERNS.items():
            if any(kw in prompt_lower for kw in keywords):
                detected_enhancements.append(enhancement_name)

        if not detected_enhancements:
            detected_enhancements.append("MODERN_CLEAN_UI")

        # 3. Construct Product Architecture Guidance
        guidelines = self._format_intent_guidelines(
            user_prompt=user_prompt,
            primary_product=primary_product,
            matched_domain=matched_domain,
            core_features=core_features,
            detected_enhancements=detected_enhancements
        )

        return {
            "matched_domain": matched_domain,
            "primary_product": primary_product,
            "core_features": core_features,
            "visual_enhancements": detected_enhancements,
            "guidelines": guidelines
        }

    def _format_intent_guidelines(
        self,
        user_prompt: str,
        primary_product: str,
        matched_domain: str,
        core_features: List[str],
        detected_enhancements: List[str]
    ) -> str:
        features_formatted = "\n".join([f"  - {f}" for f in core_features])
        enhancements_formatted = ", ".join(detected_enhancements)

        return f"""
[PRODUCT INTENT ARCHITECTURE & PLANNING INSTRUCTIONS]
User Request: "{user_prompt}"

PRIMARY PRODUCT IDENTIFICATION:
- Product Type: {primary_product} (Domain: {matched_domain})
- Visual Enhancements Requested: {enhancements_formatted}

CRITICAL ARCHITECTURAL RULE:
Visual enhancements (e.g. 3D elements, canvas graphics, ambient lighting) MUST ENHANCE the primary functional product, NEVER REPLACE IT.
Do NOT generate a blank canvas, a simple spinning 3D shape, or a minimal demo page when a complete application is requested.

MUST-HAVE DOMAIN PRODUCT FUNCTIONALITY:
{features_formatted}

INTEGRATION REQUIREMENT FOR VISUAL ENHANCEMENTS:
- Incorporate visual enhancements ({enhancements_formatted}) directly into the product components (e.g. interactive 3D canvas inside product detail hero/card, animated chart backgrounds in dashboard widgets, ambient particle effects in portfolio header).
- Ensure full UX interactivity: state management (e.g., shopping cart count/total updates, filter clicks, modal openings, tab switches) must be fully implemented and functional.
""".strip()

    def generate_domain_boilerplate(self, user_prompt: str, title: str) -> Tuple[str, str, str, str, str]:
        """Generates authentic domain-specific boilerplate (HTML, CSS, JS, SRS, README)."""
        intent = self.classify_intent(user_prompt)
        domain = intent["matched_domain"]

        if domain == "E_COMMERCE":
            return self._generate_ecommerce_boilerplate(title)
        elif domain == "DASHBOARD":
            return self._generate_dashboard_boilerplate(title)
        elif domain == "PORTFOLIO":
            return self._generate_portfolio_boilerplate(title)
        elif domain == "SAAS_ANALYTICS":
            return self._generate_saas_boilerplate(title)
        else:
            return self._generate_generic_boilerplate(title)

    def _generate_ecommerce_boilerplate(self, title: str) -> Tuple[str, str, str, str, str]:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - Performance Footwear & Apparel</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
  <header class="navbar">
    <div class="logo">
      <svg class="nav-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
      <span>{title}</span>
    </div>
    <nav class="categories">
      <button class="cat-btn active" data-cat="all">All Products</button>
      <button class="cat-btn" data-cat="running">Running</button>
      <button class="cat-btn" data-cat="lifestyle">Lifestyle</button>
      <button class="cat-btn" data-cat="basketball">Basketball</button>
    </nav>
    <div class="cart-trigger" id="cart-toggle">
      <svg class="cart-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
      Cart (<span id="cart-count">0</span>)
    </div>
  </header>

  <main>
    <section class="hero-3d">
      <div class="hero-info">
        <span class="tag">New 2026 Collection</span>
        <h1>Engineered for Peak Performance</h1>
        <p>Explore high-performance footwear with interactive 3D inspection and spatial cushioning technology.</p>
        <button class="btn-primary" onclick="scrollToProducts()">Shop Collection</button>
      </div>
      <div class="canvas-box" id="shoe-3d-canvas"></div>
    </section>

    <section class="products-section" id="products">
      <h2>Featured Footwear</h2>
      <div class="product-grid" id="product-grid">
        <!-- Injected dynamically by app.js -->
      </div>
    </section>
  </main>

  <div class="cart-drawer" id="cart-drawer">
    <div class="cart-header">
      <h3>Your Shopping Cart</h3>
      <button id="close-cart">✕</button>
    </div>
    <div class="cart-items" id="cart-items">
      <p class="empty-msg">Your cart is currently empty.</p>
    </div>
    <div class="cart-footer">
      <div class="total-row"><span>Total:</span> <span id="cart-total">$0.00</span></div>
      <button class="btn-checkout" id="checkout-btn" onclick="openCheckout()">Proceed to Checkout</button>
    </div>
  </div>

  <div class="modal" id="checkout-modal">
    <div class="modal-content">
      <h3>Complete Order</h3>
      <p>Enter payment details to confirm your order.</p>
      <input type="text" placeholder="Shipping Address" class="input-field" />
      <input type="text" placeholder="Card Number (0000 0000 0000 0000)" class="input-field" />
      <div class="modal-actions">
        <button class="btn-primary" onclick="confirmOrder()">Confirm & Pay</button>
        <button class="btn-secondary" onclick="closeCheckout()">Cancel</button>
      </div>
    </div>
  </div>

  <script src="app.js"></script>
</body>
</html>"""

        css = """:root {
  --bg-primary: #090d16;
  --bg-surface: #111827;
  --bg-card: #141c2e;
  --accent: #f97316;
  --accent-hover: #ea580c;
  --text-primary: #f8fafc;
  --text-muted: #94a3b8;
  --border-subtle: rgba(255, 255, 255, 0.1);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; background: var(--bg-primary); color: var(--text-primary); }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1.2rem 3rem; background: rgba(9,13,22,0.85); backdrop-filter: blur(16px); position: sticky; top: 0; z-index: 100; border-bottom: 1px solid var(--border-subtle); }
.logo { display: flex; align-items: center; gap: 0.6rem; font-size: 1.3rem; font-weight: 800; color: var(--text-primary); }
.logo svg { color: var(--accent); }
.categories { display: flex; gap: 0.8rem; }
.cat-btn { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-muted); padding: 0.5rem 1.2rem; border-radius: 20px; cursor: pointer; transition: 0.2s; font-family: inherit; font-size: 0.9rem; }
.cat-btn.active, .cat-btn:hover { background: var(--accent); color: #fff; border-color: var(--accent); }
.cart-trigger { display: flex; align-items: center; gap: 0.5rem; background: var(--bg-card); padding: 0.6rem 1.2rem; border-radius: 20px; cursor: pointer; border: 1px solid var(--border-subtle); font-weight: 700; }
.hero-3d { display: grid; grid-template-columns: 1fr 1fr; padding: 4rem 3rem; max-width: 1300px; margin: 0 auto; align-items: center; gap: 2rem; }
.hero-info h1 { font-size: 3.2rem; margin: 1rem 0; line-height: 1.1; }
.hero-info p { color: var(--text-muted); margin-bottom: 2rem; font-size: 1.1rem; }
.canvas-box { height: 380px; background: var(--bg-card); border-radius: 20px; border: 1px solid var(--border-subtle); overflow: hidden; }
.products-section { padding: 3rem; max-width: 1300px; margin: 0 auto; }
.product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; margin-top: 2rem; }
.product-card { background: var(--bg-card); border-radius: 16px; padding: 1.5rem; border: 1px solid var(--border-subtle); position: relative; }
.product-card .img-placeholder { height: 160px; background: rgba(255,255,255,0.03); border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 1rem; color: var(--accent); border: 1px solid rgba(255,255,255,0.05); }
.product-card .badge { display: inline-block; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); background: rgba(249, 115, 22, 0.1); padding: 0.2rem 0.6rem; border-radius: 6px; margin-bottom: 0.5rem; }
.product-card h3 { font-size: 1.2rem; margin-bottom: 0.5rem; }
.product-card .price { font-size: 1.3rem; font-weight: 800; color: var(--accent); margin-bottom: 1rem; font-variant-numeric: tabular-nums; }
.btn-primary { background: var(--accent); color: white; border: none; padding: 0.8rem 1.6rem; border-radius: 10px; font-weight: 700; cursor: pointer; width: 100%; transition: 0.2s; font-family: inherit; }
.btn-primary:hover { background: var(--accent-hover); }
.cart-drawer { position: fixed; right: -400px; top: 0; width: 380px; height: 100vh; background: var(--bg-card); z-index: 1000; transition: 0.3s; padding: 2rem; border-left: 1px solid var(--border-subtle); display: flex; flex-direction: column; }
.cart-drawer.open { right: 0; }
.cart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.cart-items { flex: 1; overflow-y: auto; }
.modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 2000; align-items: center; justify-content: center; }
.modal.open { display: flex; }
.modal-content { background: var(--bg-card); padding: 2.5rem; border-radius: 20px; width: 90%; max-width: 420px; border: 1px solid var(--border-subtle); }
.input-field { width: 100%; padding: 0.8rem; margin: 0.8rem 0; background: rgba(0,0,0,0.3); border: 1px solid var(--border-subtle); border-radius: 8px; color: white; }
.modal-actions { display: flex; gap: 1rem; margin-top: 1.5rem; }
.btn-secondary { background: transparent; color: white; border: 1px solid var(--border-subtle); padding: 0.8rem; border-radius: 8px; width: 100%; cursor: pointer; }
"""

        js = """const products = [
  { id: 1, name: 'AeroGlide Ultra 3D', category: 'running', price: 189.99, badge: 'Speed Track' },
  { id: 2, name: 'PulseX Quantum', category: 'lifestyle', price: 149.99, badge: 'Urban Cushion' },
  { id: 3, name: 'HyperCourt Pro', category: 'basketball', price: 210.00, badge: 'High Support' },
  { id: 4, name: 'VaporRun Speed', category: 'running', price: 165.50, badge: 'Carbon Plate' }
];

let cart = [];

function renderProducts(items) {
  const grid = document.getElementById('product-grid');
  if (!grid) return;
  grid.innerHTML = items.map(p => `
    <div class="product-card">
      <div class="img-placeholder">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/><path d="M4 19h16"/></svg>
      </div>
      <span class="badge">${p.badge}</span>
      <h3>${p.name}</h3>
      <p class="price">$${p.price.toFixed(2)}</p>
      <button class="btn-primary" onclick="addToCart(${p.id})">Add to Cart</button>
    </div>
  `).join('');
}

function addToCart(id) {
  const item = products.find(p => p.id === id);
  if (item) {
    cart.push(item);
    updateCartUI();
  }
}

function updateCartUI() {
  document.getElementById('cart-count').innerText = cart.length;
  const container = document.getElementById('cart-items');
  if (cart.length === 0) {
    container.innerHTML = '<p class="empty-msg">Your cart is currently empty.</p>';
  } else {
    container.innerHTML = cart.map(item => `
      <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
        <span>${item.name}</span>
        <strong>$${item.price.toFixed(2)}</strong>
      </div>
    `).join('');
  }
  const total = cart.reduce((sum, i) => sum + i.price, 0);
  document.getElementById('cart-total').innerText = `$${total.toFixed(2)}`;
}

document.addEventListener('DOMContentLoaded', () => {
  renderProducts(products);

  const cartToggle = document.getElementById('cart-toggle');
  const cartDrawer = document.getElementById('cart-drawer');
  const closeCart = document.getElementById('close-cart');

  if (cartToggle && cartDrawer) {
    cartToggle.addEventListener('click', () => cartDrawer.classList.add('open'));
  }
  if (closeCart && cartDrawer) {
    closeCart.addEventListener('click', () => cartDrawer.classList.remove('open'));
  }

  // Init 3D Canvas
  const container = document.getElementById('shoe-3d-canvas');
  if (container && typeof THREE !== 'undefined') {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const geo = new THREE.BoxGeometry(2, 0.8, 1);
    const mat = new THREE.MeshStandardMaterial({ color: 0xf97316, roughness: 0.3 });
    const mesh = new THREE.Mesh(geo, mat);
    scene.add(mesh);

    const light = new THREE.DirectionalLight(0xffffff, 1.5);
    light.position.set(5, 5, 5);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));

    camera.position.z = 4;
    function animate() {
      requestAnimationFrame(animate);
      mesh.rotation.y += 0.01;
      renderer.render(scene, camera);
    }
    animate();
  }
});

function openCheckout() {
  if (cart.length === 0) return alert('Add items to cart first.');
  document.getElementById('checkout-modal').classList.add('open');
}
function closeCheckout() {
  document.getElementById('checkout-modal').classList.remove('open');
}
function confirmOrder() {
  alert('Order placed successfully! Thank you for shopping with ' + document.title);
  cart = [];
  updateCartUI();
  closeCheckout();
}
"""

        srs = f"""# SRS: {title}

## Primary Intent: E-Commerce Storefront
- Product showcase & interactive 3D viewer
- Cart drawer management & checkout flow
"""
        readme = f"""# {title}

E-Commerce storefront application with 3D elements.
Run `index.html` in browser.
"""
        return html, css, js, srs, readme

    def _generate_dashboard_boilerplate(self, title: str) -> Tuple[str, str, str, str, str]:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title} - Learning & Analytics Dashboard</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <h2>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>
        <span>{title}</span>
      </h2>
      <nav>
        <a href="#" class="active">Overview</a>
        <a href="#">Courses</a>
        <a href="#">Analytics</a>
        <a href="#">Settings</a>
      </nav>
    </aside>
    <main class="content">
      <header class="topbar">
        <h1>Dashboard Overview</h1>
        <input type="text" placeholder="Search records..." class="search-input" />
      </header>
      <section class="kpi-grid">
        <div class="kpi-card"><h3>Active Students</h3><p class="num">1,248</p></div>
        <div class="kpi-card"><h3>Course Completion</h3><p class="num">88.4%</p></div>
        <div class="kpi-card"><h3>Avg Test Score</h3><p class="num">92/100</p></div>
      </section>
      <section class="chart-section">
        <h2>Weekly Learning Progress</h2>
        <canvas id="chart-canvas" height="200"></canvas>
      </section>
    </main>
  </div>
  <script src="app.js"></script>
</body>
</html>"""
        css = "* { box-sizing: border-box; margin: 0; padding: 0; } body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; } .dashboard-layout { display: flex; min-height: 100vh; } .sidebar { width: 250px; background: #1e293b; padding: 2rem; border-right: 1px solid rgba(255,255,255,0.1); } .sidebar nav a { display: block; color: #94a3b8; padding: 0.8rem 0; text-decoration: none; } .sidebar nav a.active { color: #38bdf8; font-weight: 700; } .content { flex: 1; padding: 2.5rem; } .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 2rem 0; } .kpi-card { background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); } .kpi-card .num { font-size: 2rem; font-weight: 800; color: #38bdf8; margin-top: 0.5rem; } .chart-section { background: #1e293b; padding: 2rem; border-radius: 12px; } .search-input { padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: #0f172a; color: white; }"
        js = "document.addEventListener('DOMContentLoaded', () => { const canvas = document.getElementById('chart-canvas'); if (canvas) { const ctx = canvas.getContext('2d'); ctx.fillStyle = '#38bdf8'; const heights = [40, 80, 60, 120, 100, 150, 130]; heights.forEach((h, i) => ctx.fillRect(i * 60 + 20, 200 - h, 40, h)); } });"
        srs = f"""# SRS: {title}

Educational Learning Dashboard with KPI Analytics.
"""
        readme = f"""# {title}

Dashboard Application.
Open `index.html`.
"""
        return html, css, js, srs, readme

    def _generate_portfolio_boilerplate(self, title: str) -> Tuple[str, str, str, str, str]:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title} - Cinematic Portfolio</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="hero">
    <h1>{title}</h1>
    <p>Cinematic Showcase & Creative Art Direction</p>
  </header>
  <section class="gallery">
    <div class="item"><h3>Project Alpha</h3><p>Interactive WebGL Design</p></div>
    <div class="item"><h3>Project Beta</h3><p>3D Product Experience</p></div>
  </section>
  <script src="app.js"></script>
</body>
</html>"""
        css = "body { background: #050505; color: #fff; font-family: sans-serif; padding: 3rem; } .hero { text-align: center; margin-bottom: 4rem; } .hero h1 { font-size: 3rem; color: #e2e8f0; } .gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; } .item { background: #111; padding: 2rem; border-radius: 12px; border: 1px solid #222; }"
        js = "console.log('Cinematic Portfolio Loaded.');"
        srs = f"""# SRS: {title}

Cinematic Portfolio Website.
"""
        readme = f"""# {title}

Portfolio Showcase.
"""
        return html, css, js, srs, readme

    def _generate_saas_boilerplate(self, title: str) -> Tuple[str, str, str, str, str]:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title} - SaaS Analytics</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="container">
    <h1>{title} Platform</h1>
    <div class="stats">
      <div class="stat"><span>MRR</span><strong>$42,500</strong></div>
      <div class="stat"><span>Active Users</span><strong>14,200</strong></div>
    </div>
  </main>
  <script src="app.js"></script>
</body>
</html>"""
        css = "body { background: #090d16; color: white; font-family: sans-serif; padding: 4rem; } .stats { display: flex; gap: 2rem; margin-top: 2rem; } .stat { background: #131b2e; padding: 1.5rem 2.5rem; border-radius: 12px; display: flex; flex-direction: column; }"
        js = "console.log('SaaS Analytics initialized.');"
        srs = f"""# SRS: {title}

SaaS Analytics Platform.
"""
        readme = f"""# {title}

SaaS Metrics App.
"""
        return html, css, js, srs, readme

    def _generate_generic_boilerplate(self, title: str) -> Tuple[str, str, str, str, str]:
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header><h1>{title}</h1></header>
  <main><p>Application initialized successfully.</p></main>
  <script src="app.js"></script>
</body>
</html>"""
        css = "body { background: #0f172a; color: white; font-family: sans-serif; padding: 2rem; }"
        js = "console.log('App ready.');"
        srs = f"# SRS: {title}\n"
        readme = f"# {title}\n"
        return html, css, js, srs, readme
