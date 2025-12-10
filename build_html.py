import json
import csv
import os

CSV_FILE = "categorized_discounts.csv"
OUTPUT_HTML = "vaquero-discounts.html"
OUTPUT_MANIFEST = "manifest.json"
OUTPUT_SW = "sw.js"

def load_data_from_csv():
    discounts = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Transform fields back to what JS expects

                # whoCanRedeem: "A;B" -> ["A", "B"]
                who = row.get("whoCanRedeem", "").split(";")
                who = [x.strip() for x in who if x.strip()]

                # tags: "tag" -> ["tag"]
                tags = [row.get("tags", "")]

                # isFeatured: "True" -> True
                is_featured = row.get("isFeatured", "False") == "True"

                # Construct object
                item = {
                    "id": row["id"],
                    "businessName": row["businessName"],
                    "category": row["category"],
                    "discountAmount": row["discountAmount"],
                    "whoCanRedeem": who,
                    "howToRedeem": row["howToRedeem"],
                    "description": row["description"],
                    "address": row["address"],
                    "phone": row["phone"],
                    "email": row["email"],
                    "website": row["website"],
                    "social": "", # Not in CSV currently
                    "campusProximity": row["campusProximity"],
                    "isFeatured": is_featured,
                    "tags": tags
                }
                discounts.append(item)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found. Please run fetch_and_process.py first.")
        return []
    return discounts

discounts_data = load_data_from_csv()
discounts_json = json.dumps(discounts_data, indent=2)

# --- MANIFEST.JSON ---
manifest_content = """{
  "name": "Vaquero Discounts",
  "short_name": "VaqueroDiscounts",
  "start_url": "./vaquero-discounts.html",
  "display": "standalone",
  "background_color": "#F5F5F7",
  "theme_color": "#F05023",
  "icons": [
    {
      "src": "icon.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}"""

# --- SW.JS ---
sw_content = """const CACHE_NAME = 'vaquero-v1';
const ASSETS = [
  './',
  './vaquero-discounts.html',
  './manifest.json',
  './icon.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => response || fetch(e.request))
  );
});
"""

# --- HTML ---
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#F05023">
    <title>Vaquero Discounts</title>

    <!-- PWA -->
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="icon.png">

    <!-- PDF Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>

    <style>
        :root {{
            --primary: #F05023;
            --secondary: #646469;
            --bg-body: #F5F5F7;
            --bg-card: #FFFFFF;
            --text-main: #1D1D1F;
            --text-muted: #86868B;
            --border-color: #D2D2D7;
            --radius: 12px;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            --transition: 0.2s ease-in-out;
        }}

        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
        }}

        /* --- Header --- */
        header {{
            background: #fff;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid var(--border-color);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        .brand {{
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--secondary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .brand span {{ color: var(--primary); }}
        .header-subtitle {{ font-size: 0.75rem; color: var(--text-muted); display: none; }}
        @media (min-width: 600px) {{ .header-subtitle {{ display: block; }} }}

        /* --- Main Layout --- */
        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 16px;
        }}

        /* --- Search & Filters --- */
        .controls-section {{
            margin-bottom: 24px;
        }}

        .search-container {{
            position: relative;
            margin-bottom: 16px;
        }}
        .search-input {{
            width: 100%;
            padding: 14px 44px 14px 16px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            font-size: 16px; /* Prevents zoom on iOS */
            background: #fff;
            transition: border-color var(--transition);
        }}
        .search-input:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(240, 80, 35, 0.1);
        }}
        .search-icon {{
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
        }}

        /* Filter Groups */
        .filter-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--secondary);
            margin-bottom: 8px;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Chips */
        .chips-container {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 8px; /* Space for scrollbar */
            scrollbar-width: none; /* Firefox */
            -ms-overflow-style: none;  /* IE 10+ */
            margin-bottom: 16px;
        }}
        .chips-container::-webkit-scrollbar {{ display: none; }}

        .chip {{
            background: #fff;
            border: 1px solid var(--border-color);
            border-radius: 999px;
            padding: 8px 16px;
            font-size: 0.9rem;
            color: var(--text-main);
            white-space: nowrap;
            cursor: pointer;
            transition: all var(--transition);
            user-select: none;
        }}
        .chip:hover {{ background: #f0f0f0; }}
        .chip.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            font-weight: 500;
        }}

        /* Eligibility Toggles */
        .eligibility-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }}
        .toggle-btn {{
            background: #fff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 0.85rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all var(--transition);
        }}
        .toggle-btn.active {{
            background: rgba(240, 80, 35, 0.1);
            border-color: var(--primary);
            color: var(--primary);
            font-weight: 600;
        }}

        .clear-filters {{
            font-size: 0.9rem;
            color: var(--text-muted);
            text-decoration: underline;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0;
            margin-top: 8px;
        }}
        .clear-filters:hover {{ color: var(--primary); }}

        /* --- Sections --- */
        .section-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--secondary);
            margin: 24px 0 12px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .result-count {{
            font-size: 0.85rem;
            font-weight: 400;
            color: var(--text-muted);
        }}

        /* --- Cards --- */
        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }}
        @media (min-width: 600px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (min-width: 900px) {{ .grid {{ grid-template-columns: repeat(3, 1fr); }} }}

        .card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            overflow: hidden;
            border: 1px solid transparent;
            transition: transform var(--transition), box-shadow var(--transition);
            display: flex;
            flex-direction: column;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow);
            border-color: rgba(240, 80, 35, 0.3);
        }}

        .card-header {{
            padding: 16px;
            padding-bottom: 8px;
        }}

        .card-badge-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }}
        .category-badge {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--secondary);
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .discount-badge {{
            background: rgba(240, 80, 35, 0.1);
            color: var(--primary);
            font-weight: 700;
            font-size: 0.8rem;
            padding: 4px 8px;
            border-radius: 4px;
            text-align: right;
            max-width: 60%;
        }}

        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            margin: 0 0 4px 0;
            color: var(--text-main);
        }}

        .card-eligibility {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .card-actions {{
            padding: 12px 16px;
            background: #fafafa;
            border-top: 1px solid #eee;
            margin-top: auto;
            text-align: center;
        }}
        .details-btn {{
            background: none;
            border: none;
            color: var(--primary);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .details-btn:hover {{
            text-decoration: underline;
        }}

        /* --- Modal --- */
        .modal-backdrop {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        .modal-backdrop.active {{
            display: flex;
            opacity: 1;
        }}
        .modal-content {{
            background: #fff;
            border-radius: var(--radius);
            width: 100%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            padding: 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transform: translateY(20px);
            transition: transform 0.3s ease;
        }}
        .modal-backdrop.active .modal-content {{
            transform: translateY(0);
        }}
        .modal-header {{
            padding: 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            background: #fff;
            z-index: 10;
        }}
        .modal-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-main);
        }}
        .close-modal-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
        }}
        .close-modal-btn:hover {{ color: var(--primary); }}

        .modal-body {{
            padding: 20px;
        }}

        .modal-detail-row {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 16px;
        }}
        .modal-detail-icon {{
            color: var(--primary);
            width: 20px;
            height: 20px;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .modal-label {{
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
            font-weight: 600;
        }}
        .modal-value {{
            font-size: 1rem;
            color: var(--text-main);
            line-height: 1.5;
        }}

        .modal-footer {{
            padding: 16px 20px;
            border-top: 1px solid #eee;
            background: #fafafa;
            display: flex;
            justify-content: flex-end;
        }}
        .pdf-btn {{
            background: var(--primary);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s;
        }}
        .pdf-btn:hover {{
            background: #d64015;
        }}


        /* --- Footer --- */
        footer {{
            text-align: center;
            padding: 32px 16px;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border-color);
            margin-top: 32px;
            background: #fff;
        }}
        .footer-link {{ color: var(--secondary); font-weight: 500; }}

        /* --- Empty State --- */
        .empty-state {{
            text-align: center;
            padding: 48px;
            color: var(--text-muted);
        }}
        .empty-icon {{ width: 48px; height: 48px; opacity: 0.3; margin-bottom: 16px; }}

    </style>
</head>
<body>

    <header>
        <a href="#" class="brand" onclick="window.scrollTo(0,0); return false;">
            UTRGV <span>Vaquero Discounts</span>
        </a>
        <span class="header-subtitle">Exclusive offers for Students, Faculty, Staff & Alumni</span>
    </header>

    <main>

        <!-- Search & Filters -->
        <section class="controls-section">
            <div class="search-container">
                <input type="text" id="searchInput" class="search-input" placeholder="Search businesses, categories, or keywords..." aria-label="Search discounts">
                <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </div>

            <span class="filter-label">Categories</span>
            <div class="chips-container" id="categoryContainer">
                <!-- Injected via JS -->
            </div>

            <span class="filter-label">Who can redeem</span>
            <div class="eligibility-container" id="eligibilityContainer">
                <button class="toggle-btn" data-value="Students">Students</button>
                <button class="toggle-btn" data-value="Faculty">Faculty</button>
                <button class="toggle-btn" data-value="Staff">Staff</button>
                <button class="toggle-btn" data-value="Alumni">Alumni</button>
            </div>

            <button id="clearFilters" class="clear-filters" style="display: none;">Clear all filters</button>
        </section>

        <!-- Featured -->
        <section id="featuredSection" style="display: none;">
            <div class="section-title">
                Featured Discounts
            </div>
            <div class="grid" id="featuredGrid">
                <!-- JS Injected -->
            </div>
        </section>

        <!-- Results -->
        <section>
            <div class="section-title">
                All Discounts
                <span class="result-count" id="resultCount">Showing 0 discounts</span>
            </div>
            <div class="grid" id="resultsGrid">
                <!-- JS Injected -->
            </div>
            <div id="emptyState" class="empty-state" style="display: none;">
                <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                <p>No results found for your filters.</p>
                <button class="toggle-btn" style="display:inline-block; margin-top:8px;" onclick="clearAllFilters()">Clear Filters</button>
            </div>
        </section>

    </main>

    <!-- Modal -->
    <div id="modalBackdrop" class="modal-backdrop">
        <div class="modal-content" id="modalContent">
            <div class="modal-header">
                <h2 id="modalTitle" class="modal-title">Business Name</h2>
                <button class="close-modal-btn" onclick="closeModal()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Dynamic Content -->
            </div>
            <div class="modal-footer">
                <button class="pdf-btn" onclick="saveCurrentAsPDF()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                    Save as PDF
                </button>
            </div>
        </div>
    </div>

    <footer>
        <p><strong>Disclaimer:</strong> Vendors and offers are subject to change without notice.</p>
        <p>Please visit the <a href="https://www.utrgv.edu/hr/benefits/index.htm" target="_blank" class="footer-link">official UTRGV Human Resources website</a> for the most up-to-date policy and participation details.</p>
        <p>&copy; 2024 UTRGV Vaquero Discounts</p>
    </footer>

    <!-- ICONS (Embedded for reuse in JS) -->
    <div style="display: none;">
        <svg id="icon-map" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
        <svg id="icon-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
        <svg id="icon-globe" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
        <svg id="icon-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        <svg id="icon-chevron-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
    </div>

    <script>
        // --- DATA ---
        const DISCOUNTS = {discounts_json};

        // --- CONFIG ---
        const CATEGORIES = [
            "Eat & Drink (Food & Dining)",
            "Shop (Retail)",
            "Health & Beauty",
            "Fun & Events (Entertainment)",
            "Auto & Tech",
            "Services & Travel"
        ];

        // --- STATE ---
        let state = {{
            search: "",
            category: null,
            eligibility: new Set(),
            currentModalItem: null
        }};

        // --- DOM ELEMENTS ---
        const els = {{
            search: document.getElementById('searchInput'),
            categories: document.getElementById('categoryContainer'),
            eligibility: document.getElementById('eligibilityContainer'),
            clearBtn: document.getElementById('clearFilters'),
            featuredSection: document.getElementById('featuredSection'),
            featuredGrid: document.getElementById('featuredGrid'),
            resultsGrid: document.getElementById('resultsGrid'),
            resultCount: document.getElementById('resultCount'),
            emptyState: document.getElementById('emptyState'),
            modalBackdrop: document.getElementById('modalBackdrop'),
            modalTitle: document.getElementById('modalTitle'),
            modalBody: document.getElementById('modalBody')
        }};

        // --- ICONS ---
        const icons = {{
            map: document.getElementById('icon-map').innerHTML,
            phone: document.getElementById('icon-phone').innerHTML,
            globe: document.getElementById('icon-globe').innerHTML,
            info: document.getElementById('icon-info').innerHTML,
            chevron: document.getElementById('icon-chevron-right').innerHTML
        }};

        // --- INIT ---
        function init() {{
            loadState();
            renderFilters();
            renderAll();
            setupListeners();
            registerSW();
        }}

        function registerSW() {{
            if ('serviceWorker' in navigator) {{
                navigator.serviceWorker.register('sw.js')
                .then(() => console.log('Service Worker Registered'))
                .catch(err => console.log('SW Registration Failed', err));
            }}
        }}

        function setupListeners() {{
            // Search
            els.search.addEventListener('input', (e) => {{
                state.search = e.target.value;
                saveState();
                renderAll();
            }});

            // Categories
            els.categories.addEventListener('click', (e) => {{
                if (e.target.classList.contains('chip')) {{
                    const cat = e.target.dataset.cat;
                    if (state.category === cat) {{
                        state.category = null; // Toggle off
                    }} else {{
                        state.category = cat;
                    }}
                    renderCategoryChips();
                    saveState();
                    renderAll();
                }}
            }});

            // Eligibility
            els.eligibility.addEventListener('click', (e) => {{
                const btn = e.target.closest('.toggle-btn');
                if (btn) {{
                    const val = btn.dataset.value;
                    if (state.eligibility.has(val)) {{
                        state.eligibility.delete(val);
                    }} else {{
                        state.eligibility.add(val);
                    }}
                    renderEligibilityToggles();
                    saveState();
                    renderAll();
                }}
            }});

            // Clear
            els.clearBtn.addEventListener('click', clearAllFilters);

            // Modal Backdrop Click
            els.modalBackdrop.addEventListener('click', (e) => {{
                if (e.target === els.modalBackdrop) {{
                    closeModal();
                }}
            }});
        }}

        function clearAllFilters() {{
            state.search = "";
            state.category = null;
            state.eligibility.clear();
            els.search.value = "";
            renderCategoryChips();
            renderEligibilityToggles();
            saveState();
            renderAll();
        }}

        // --- RENDER FILTERS ---
        function renderFilters() {{
            renderCategoryChips();
            renderEligibilityToggles();
            els.search.value = state.search;
        }}

        function renderCategoryChips() {{
            els.categories.innerHTML = CATEGORIES.map(cat => {{
                const isActive = state.category === cat;
                return `<button class="chip ${{isActive ? 'active' : ''}}" data-cat="${{cat}}">${{cat}}</button>`;
            }}).join('');
        }}

        function renderEligibilityToggles() {{
            Array.from(els.eligibility.children).forEach(btn => {{
                const val = btn.dataset.value;
                if (state.eligibility.has(val)) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});

            const hasFilters = state.search || state.category || state.eligibility.size > 0;
            els.clearBtn.style.display = hasFilters ? 'block' : 'none';
        }}

        // --- CORE LOGIC ---
        function getFilteredDiscounts() {{
            return DISCOUNTS.filter(d => {{
                if (state.search) {{
                    const q = state.search.toLowerCase();
                    const text = (d.businessName + " " + d.description + " " + d.tags.join(" ")).toLowerCase();
                    if (!text.includes(q)) return false;
                }}
                if (state.category && d.category !== state.category) {{
                    return false;
                }}
                if (state.eligibility.size > 0) {{
                    const selected = Array.from(state.eligibility);
                    const hasIntersection = selected.some(role => d.whoCanRedeem.includes(role));
                    if (!hasIntersection) return false;
                }}
                return true;
            }}).sort((a, b) => a.businessName.localeCompare(b.businessName));
        }}

        function renderAll() {{
            const filtered = getFilteredDiscounts();
            els.resultCount.textContent = `Showing ${{filtered.length}} discount${{filtered.length !== 1 ? 's' : ''}}`;

            const featured = filtered.filter(d => d.isFeatured);
            const isFiltering = state.search || state.category || state.eligibility.size > 0;

            if (featured.length > 0 && !isFiltering) {{
                els.featuredSection.style.display = 'block';
                els.featuredGrid.innerHTML = featured.slice(0, 3).map(renderCard).join('');
            }} else {{
                els.featuredSection.style.display = 'none';
            }}

            if (filtered.length === 0) {{
                els.resultsGrid.innerHTML = '';
                els.emptyState.style.display = 'block';
            }} else {{
                els.emptyState.style.display = 'none';
                els.resultsGrid.innerHTML = filtered.map(renderCard).join('');
            }}
            renderEligibilityToggles();
        }}

        function truncateText(text, limit) {{
            if (text.length <= limit) return text;
            return text.substring(0, limit) + "...";
        }}

        function renderCard(item) {{
            const who = item.whoCanRedeem.join(", ");
            // Truncate discount amount
            const discountDisplay = truncateText(item.discountAmount, 25);

            return `
            <article class="card">
                <div class="card-header">
                    <div class="card-badge-row">
                        <span class="category-badge">${{item.category}}</span>
                        <span class="discount-badge" title="${{item.discountAmount}}">${{discountDisplay}}</span>
                    </div>
                    <h3 class="card-title">${{item.businessName}}</h3>
                    <div class="card-eligibility">For: ${{who}}</div>
                </div>

                <div class="card-actions">
                    <button class="details-btn" onclick="openModal('${{item.id}}')">
                        View Details <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </button>
                </div>
            </article>
            `;
        }}

        // --- MODAL & PDF ---
        window.openModal = function(id) {{
            const item = DISCOUNTS.find(d => d.id == id);
            if (!item) return;
            state.currentModalItem = item;

            els.modalTitle.textContent = item.businessName;

            const who = item.whoCanRedeem.join(", ");

            els.modalBody.innerHTML = `
                <div style="background:rgba(240, 80, 35, 0.1); padding:12px; border-radius:8px; margin-bottom:20px;">
                    <span class="modal-label" style="color:var(--primary);">Discount Offer</span>
                    <strong style="font-size:1.2rem; color:var(--primary);">${{item.discountAmount}}</strong>
                </div>

                <div class="modal-detail-row">
                    <div class="modal-detail-icon">${{icons.info}}</div>
                    <div>
                        <span class="modal-label">How to Redeem</span>
                        <div class="modal-value">${{item.howToRedeem}}</div>
                    </div>
                </div>

                <div class="modal-detail-row">
                    <div class="modal-detail-icon" style="color:var(--secondary);">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    </div>
                    <div>
                        <span class="modal-label">Eligibility</span>
                        <div class="modal-value">${{who}}</div>
                    </div>
                </div>

                ${{item.description ? `
                <div class="modal-detail-row">
                     <div class="modal-detail-icon" style="color:var(--secondary);opacity:0;"></div>
                    <div style="font-style:italic; color:var(--text-muted);">${{item.description}}</div>
                </div>
                ` : ''}}

                ${{item.address ? `
                <div class="modal-detail-row">
                    <div class="modal-detail-icon">${{icons.map}}</div>
                    <div>
                        <span class="modal-label">Location</span>
                        <div class="modal-value">
                            <a href="https://maps.google.com/?q=${{encodeURIComponent(item.address)}}" target="_blank" style="color:var(--text-main); text-decoration:underline;">${{item.address}}</a>
                            ${{item.campusProximity ? `<div style="font-size:0.85em; color:var(--text-muted); margin-top:2px;">(${{item.campusProximity}})</div>` : ''}}
                        </div>
                    </div>
                </div>
                ` : ''}}

                ${{item.phone ? `
                <div class="modal-detail-row">
                    <div class="modal-detail-icon">${{icons.phone}}</div>
                    <div>
                        <span class="modal-label">Phone</span>
                        <div class="modal-value"><a href="tel:${{item.phone}}" style="color:var(--text-main); text-decoration:none;">${{item.phone}}</a></div>
                    </div>
                </div>
                ` : ''}}

                ${{item.website ? `
                <div class="modal-detail-row">
                    <div class="modal-detail-icon">${{icons.globe}}</div>
                    <div>
                        <span class="modal-label">Website</span>
                        <div class="modal-value"><a href="${{item.website}}" target="_blank" style="color:var(--primary);">Visit Website</a></div>
                    </div>
                </div>
                ` : ''}}
            `;

            els.modalBackdrop.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }};

        window.closeModal = function() {{
            els.modalBackdrop.classList.remove('active');
            document.body.style.overflow = '';
            state.currentModalItem = null;
        }};

        window.saveCurrentAsPDF = function() {{
            if (!state.currentModalItem) return;
            const item = state.currentModalItem;

            if (!window.jspdf) {{
                alert("PDF library not loaded. Please check internet connection.");
                return;
            }}

            const {{ jsPDF }} = window.jspdf;
            const doc = new jsPDF();

            // Layout constants
            const margin = 20;
            const pageWidth = doc.internal.pageSize.getWidth();
            const contentWidth = pageWidth - (margin * 2);

            // Branding Header
            doc.setFillColor(240, 80, 35); // UTRGV Orange
            doc.rect(0, 0, pageWidth, 40, 'F');

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(24);
            doc.setFont("helvetica", "bold");
            doc.text("UTRGV Vaquero Discounts", margin, 25);

            let y = 60;

            // Business Name
            doc.setTextColor(29, 29, 31); // Dark Gray
            doc.setFontSize(22);
            doc.setFont("helvetica", "bold");
            const titleSplit = doc.splitTextToSize(item.businessName, contentWidth);
            doc.text(titleSplit, margin, y);
            y += (titleSplit.length * 10) + 10;

            // Discount Box
            doc.setFillColor(250, 250, 250);
            doc.setDrawColor(220, 220, 220);
            doc.roundedRect(margin, y, contentWidth, 30, 3, 3, 'FD');

            doc.setTextColor(240, 80, 35);
            doc.setFontSize(16);
            doc.text("Discount Offer:", margin + 5, y + 10);

            doc.setFontSize(14);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(50, 50, 50);
            const discountSplit = doc.splitTextToSize(item.discountAmount, contentWidth - 10);
            doc.text(discountSplit, margin + 5, y + 20);

            y += 45;

            // Details
            function addDetail(label, value) {{
                if (!value) return;
                doc.setFontSize(10);
                doc.setTextColor(134, 134, 139); // Muted
                doc.text(label.toUpperCase(), margin, y);
                y += 5;

                doc.setFontSize(12);
                doc.setTextColor(0, 0, 0);
                const valSplit = doc.splitTextToSize(value, contentWidth);
                doc.text(valSplit, margin, y);
                y += (valSplit.length * 6) + 10;
            }}

            addDetail("How to Redeem", item.howToRedeem);
            addDetail("Eligibility", item.whoCanRedeem.join(", "));
            addDetail("Location", item.address);
            if (item.phone) addDetail("Phone", item.phone);

            // Disclaimer Message
            y = Math.max(y, 250); // Push to bottom if space allows, or just margin
            if (y > 250) y += 10;
            else y = 250;

            doc.setDrawColor(240, 80, 35);
            doc.setLineWidth(0.5);
            doc.line(margin, y - 10, pageWidth - margin, y - 10);

            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            const msg = "Presented by UTRGV Human Resources. This discount is for UTRGV Students, Faculty, Staff, and Alumni. Please present your UTRGV ID to redeem.";
            const msgSplit = doc.splitTextToSize(msg, contentWidth);
            doc.text(msgSplit, margin, y);

            doc.save(`${{item.businessName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}}_discount.pdf`);
        }};

        window.clearAllFilters = clearAllFilters;

        // --- STORAGE ---
        function saveState() {{
            const s = {{
                search: state.search,
                category: state.category,
                eligibility: Array.from(state.eligibility)
            }};
            localStorage.setItem('vaquero_state', JSON.stringify(s));
        }}

        function loadState() {{
            try {{
                const s = JSON.parse(localStorage.getItem('vaquero_state'));
                if (s) {{
                    if (s.search) state.search = s.search;
                    if (s.category) state.category = s.category;
                    if (s.eligibility) state.eligibility = new Set(s.eligibility);
                }}
            }} catch (e) {{
                console.log("No saved state");
            }}
        }}

        // Run
        init();
    </script>
</body>
</html>
"""

# Write HTML
with open(OUTPUT_HTML, "w", encoding='utf-8') as f:
    f.write(html_content)
print(f"File {OUTPUT_HTML} created successfully.")

# Write Manifest
with open(OUTPUT_MANIFEST, "w", encoding='utf-8') as f:
    f.write(manifest_content)
print(f"File {OUTPUT_MANIFEST} created successfully.")

# Write SW
with open(OUTPUT_SW, "w", encoding='utf-8') as f:
    f.write(sw_content)
print(f"File {OUTPUT_SW} created successfully.")
