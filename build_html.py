import json

with open("data.json", "r") as f:
    discounts_json = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#F05023">
    <title>Vaquero Discounts</title>
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

        .card-body {{
            padding: 0 16px 16px 16px;
            display: none; /* Hidden by default */
            border-top: 1px solid #f0f0f0;
            margin-top: 8px;
            padding-top: 12px;
            font-size: 0.9rem;
        }}
        .card.expanded .card-body {{ display: block; }}

        .detail-row {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .detail-icon {{
            width: 18px;
            height: 18px;
            color: var(--secondary);
            flex-shrink: 0;
            margin-top: 2px;
        }}
        .detail-text {{ color: var(--text-main); word-break: break-word; }}
        .detail-text a {{ color: var(--primary); text-decoration: none; }}
        .detail-text a:hover {{ text-decoration: underline; }}

        .card-actions {{
            padding: 12px 16px;
            background: #fafafa;
            border-top: 1px solid #eee;
            margin-top: auto;
            text-align: center;
        }}
        .expand-btn {{
            background: none;
            border: none;
            color: var(--secondary);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .expand-btn svg {{ transition: transform 0.2s; }}
        .card.expanded .expand-btn svg {{ transform: rotate(180deg); }}

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
        <svg id="icon-chevron-down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
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
            eligibility: new Set()
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
            emptyState: document.getElementById('emptyState')
        }};

        // --- ICONS ---
        const icons = {{
            map: document.getElementById('icon-map').innerHTML,
            phone: document.getElementById('icon-phone').innerHTML,
            globe: document.getElementById('icon-globe').innerHTML,
            info: document.getElementById('icon-info').innerHTML,
            chevron: document.getElementById('icon-chevron-down').innerHTML
        }};

        // --- INIT ---
        function init() {{
            loadState();
            renderFilters();
            renderAll();
            setupListeners();
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
                    renderCategoryChips(); // Re-render chips to show active state
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
            // Categories
            renderCategoryChips();
            // Eligibility is static HTML but needs active class update
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

            // Show clear button if any filter active
            const hasFilters = state.search || state.category || state.eligibility.size > 0;
            els.clearBtn.style.display = hasFilters ? 'block' : 'none';
        }}

        // --- CORE LOGIC ---
        function getFilteredDiscounts() {{
            return DISCOUNTS.filter(d => {{
                // Search
                if (state.search) {{
                    const q = state.search.toLowerCase();
                    const text = (d.businessName + " " + d.description + " " + d.tags.join(" ")).toLowerCase();
                    if (!text.includes(q)) return false;
                }}

                // Category
                if (state.category && d.category !== state.category) {{
                    return false;
                }}

                // Eligibility
                if (state.eligibility.size > 0) {{
                    // Intersection: Item must support ALL selected? Or ANY?
                    // Requirement: "intersect with the selected eligibility set"
                    // Usually means: If I select "Students", show me things Students can redeem.
                    // If I select "Students" AND "Staff", show me things that are for Students OR Staff?
                    // "A discount matches if its whoCanRedeem array intersects with the selected eligibility set."
                    // This implies OR logic between the selected filters for matching (if I am a Student and Staff, show me deals for either).
                    // BUT Requirement says: "All filters should be applied with AND logic" (between search, category, eligibility).

                    const selected = Array.from(state.eligibility);
                    const hasIntersection = selected.some(role => d.whoCanRedeem.includes(role));
                    if (!hasIntersection) return false;
                }}

                return true;
            }}).sort((a, b) => a.businessName.localeCompare(b.businessName));
        }}

        function renderAll() {{
            const filtered = getFilteredDiscounts();

            // Update counts
            els.resultCount.textContent = `Showing ${{filtered.length}} discount${{filtered.length !== 1 ? 's' : ''}}`;

            // Featured
            const featured = filtered.filter(d => d.isFeatured);
            // Sort featured: Featured items at top, but if we are filtering, we just show relevant featured ones.
            // Requirement: "A small Featured Discounts area at the top of the results... showing a small subset".
            // If we have filters, maybe we shouldn't show the separate section?
            // Usually featured sections disappear when searching/filtering to avoid duplication.
            // Let's hide Featured if searching or categorizing, OR just show featured subset of results.
            // Let's hide Featured section if user has active filters to keep results clean,
            // OR keep it but ensure no dupes.
            // Requirement says "If no entries are featured, hide this section."

            const isFiltering = state.search || state.category || state.eligibility.size > 0;

            if (featured.length > 0 && !isFiltering) {{
                els.featuredSection.style.display = 'block';
                els.featuredGrid.innerHTML = featured.slice(0, 3).map(renderCard).join(''); // Show top 3 featured
            }} else {{
                els.featuredSection.style.display = 'none';
            }}

            // Main Results
            if (filtered.length === 0) {{
                els.resultsGrid.innerHTML = '';
                els.emptyState.style.display = 'block';
            }} else {{
                els.emptyState.style.display = 'none';
                els.resultsGrid.innerHTML = filtered.map(renderCard).join('');
            }}

            renderEligibilityToggles(); // Update clear button visibility
        }}

        function renderCard(item) {{
            // Format eligibility
            const who = item.whoCanRedeem.join(", ");

            // Icons
            const mapIcon = `<svg class="detail-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>`;

            return `
            <article class="card" id="card-${{item.id}}">
                <div class="card-header">
                    <div class="card-badge-row">
                        <span class="category-badge">${{item.category}}</span>
                        <span class="discount-badge">${{item.discountAmount}}</span>
                    </div>
                    <h3 class="card-title">${{item.businessName}}</h3>
                    <div class="card-eligibility">For: ${{who}}</div>
                </div>

                <div class="card-body">
                    <div class="detail-row">
                        <span class="detail-icon">${{icons.info}}</span>
                        <span class="detail-text"><strong>Redeem:</strong> ${{item.howToRedeem}}</span>
                    </div>

                    ${{item.description ? `
                    <p style="margin: 0 0 8px 0; color: var(--text-muted); font-size: 0.9em;">${{item.description}}</p>
                    ` : ''}}

                    ${{item.address ? `
                    <div class="detail-row">
                        ${{icons.map}}
                        <span class="detail-text">
                            <a href="https://maps.google.com/?q=${{encodeURIComponent(item.address)}}" target="_blank">${{item.address}}</a>
                            ${{item.campusProximity ? `<br><small style="color:var(--text-muted)">(${{item.campusProximity}})</small>` : ''}}
                        </span>
                    </div>
                    ` : ''}}

                    ${{item.phone ? `
                    <div class="detail-row">
                        ${{icons.phone}}
                        <span class="detail-text"><a href="tel:${{item.phone}}">${{item.phone}}</a></span>
                    </div>
                    ` : ''}}

                    ${{item.website ? `
                    <div class="detail-row">
                        ${{icons.globe}}
                        <span class="detail-text"><a href="${{item.website}}" target="_blank">Visit Website</a></span>
                    </div>
                    ` : ''}}
                </div>

                <div class="card-actions">
                    <button class="expand-btn" onclick="toggleCard('${{item.id}}')">
                        Details <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    </button>
                </div>
            </article>
            `;
        }}

        // Global scope for onclick
        window.toggleCard = function(id) {{
            const card = document.getElementById(`card-${{id}}`);
            if (card) {{
                card.classList.toggle('expanded');
                // Optional: Update button text? No, kept simple "Details" with chevron rotation
            }}
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

with open("vaquero-discounts.html", "w") as f:
    f.write(html_content)

print("File created successfully.")
