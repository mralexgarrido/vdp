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
                    "social": "",
                    "campusProximity": row["campusProximity"],
                    "isFeatured": is_featured,
                    "tags": tags,
                    # New internal fields
                    "joinDate": row.get("joinDate", ""),
                    "authorizedBy": row.get("authorizedBy", ""),
                    "contactTitle": row.get("contactTitle", "")
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
sw_content = """const CACHE_NAME = 'vaquero-v2';
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

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">

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
            --radius: 8px; /* Slightly sharper for official look */
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            --transition: 0.2s ease-in-out;
            --header-orange: #F05023;
            --header-gray: #575757;
        }}

        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        body {{
            margin: 0;
            font-family: "Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
        }}

        /* --- Global UTRGV Header --- */
        .utrgv-header {{
            display: flex;
            flex-direction: column;
            width: 100%;
        }}

        /* Top Orange Bar */
        .header-top {{
            background-color: var(--header-orange);
            color: white;
            padding: 0;
            height: 55px; /* Fixed height for consistency */
            display: flex;
            align-items: center;
            justify-content: flex-start;
            position: relative;
        }}

        .header-logo-container {{
            padding-left: 15px;
            display: flex;
            align-items: center;
            height: 100%;
            background: var(--header-orange);
            z-index: 2;
        }}

        /* SVG Logo approximation */
        .utrgv-logo-svg {{
            height: 32px;
            width: auto;
            fill: white;
            margin-right: 15px;
        }}

        .header-10years {{
             height: 38px;
             margin-left: 5px;
             border-left: 1px solid rgba(255,255,255,0.3);
             padding-left: 10px;
        }}

        /* Slanted Divider */
        .header-divider {{
            height: 55px;
            width: 40px;
            background: var(--header-orange);
            clip-path: polygon(0 0, 100% 0, 0 100%);
            margin-left: -1px; /* Overlap slightly */
            z-index: 1;
        }}

        /* Gray Bar (Desktop: To the right of orange; Mobile: Below?)
           Actually UTRGV site keeps them on same line for desktop, but mobile is stacked.
           We will try to mimic the image provided which shows a continuous bar.
        */
        .header-main-bar {{
            flex-grow: 1;
            background-color: var(--header-gray);
            height: 55px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-left: 20px; /* Offset for slanted cut if using absolute positioning, but we are using flex */
            margin-left: -20px; /* Pull back to tuck under slant */
            padding-right: 20px;
            z-index: 0;
        }}

        .university-name {{
            font-family: "Open Sans", sans-serif;
            font-weight: 700;
            font-size: 1.1rem;
            color: white;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            padding-left: 20px;
            text-transform: uppercase; /* Often uppercase in branding headers */
            letter-spacing: 0.5px;
        }}

        .header-nav {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-left: auto;
        }}

        .header-link {{
            color: white;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            display: none; /* Hidden on mobile */
        }}

        .header-search-icon {{
            color: white;
            width: 24px;
            height: 24px;
            cursor: pointer;
        }}

        @media (min-width: 900px) {{
            .header-link {{ display: block; }}
        }}

        @media (max-width: 600px) {{
            .university-name {{ display: none; }} /* Hide full name on small screens */
            .header-top {{ justify-content: space-between; }}
        }}

        /* --- Local Header (Vaquero Discounts Title) --- */
        .app-header {{
            background: white;
            padding: 24px 16px;
            border-bottom: 1px solid var(--border-color);
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .app-title {{
            margin: 0;
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--primary);
            text-transform: uppercase;
            letter-spacing: -0.5px;
        }}
        .app-subtitle {{
            margin: 8px 0 0;
            color: var(--text-muted);
            font-size: 1rem;
        }}

        /* --- Main Layout --- */
        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px 16px;
        }}

        /* --- Search & Filters --- */
        .controls-section {{
            margin-bottom: 32px;
        }}

        .search-container {{
            position: relative;
            margin-bottom: 24px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        .search-input {{
            width: 100%;
            padding: 16px 48px 16px 20px;
            border: 1px solid var(--border-color);
            border-radius: 50px; /* Pill shape */
            font-size: 16px;
            background: #fff;
            transition: all var(--transition);
            box-shadow: 0 2px 6px rgba(0,0,0,0.02);
            font-family: inherit;
        }}
        .search-input:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 4px 12px rgba(240, 80, 35, 0.15);
        }}
        .search-icon {{
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
        }}

        /* Filter Groups */
        .filter-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--secondary);
            margin-bottom: 12px;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Chips */
        .chips-container {{
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding-bottom: 12px;
            scrollbar-width: none;
            margin-bottom: 24px;
        }}
        .chips-container::-webkit-scrollbar {{ display: none; }}

        .chip {{
            background: #fff;
            border: 1px solid var(--border-color);
            border-radius: 6px; /* Square with slight radius */
            padding: 8px 16px;
            font-size: 0.9rem;
            color: var(--text-main);
            white-space: nowrap;
            cursor: pointer;
            transition: all var(--transition);
            user-select: none;
            font-family: inherit;
            font-weight: 600;
        }}
        .chip:hover {{ background: #f9f9f9; border-color: #bbb; }}
        .chip.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(240, 80, 35, 0.3);
        }}

        /* Eligibility Toggles */
        .eligibility-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 16px;
        }}
        .toggle-btn {{
            background: #fff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all var(--transition);
            font-family: inherit;
            color: var(--text-main);
        }}
        .toggle-btn:hover {{ background: #f9f9f9; }}
        .toggle-btn.active {{
            background: #fff3f0; /* Light orange tint */
            border-color: var(--primary);
            color: var(--primary);
            font-weight: 700;
        }}

        .clear-filters {{
            font-size: 0.9rem;
            color: var(--text-muted);
            text-decoration: underline;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0;
            margin-top: 12px;
            font-family: inherit;
        }}
        .clear-filters:hover {{ color: var(--primary); }}

        /* --- Sections --- */
        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #333;
            margin: 40px 0 20px 0;
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            border-bottom: 2px solid #eee;
            padding-bottom: 8px;
        }}
        .result-count {{
            font-size: 0.9rem;
            font-weight: 400;
            color: var(--text-muted);
        }}

        /* --- Cards --- */
        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 24px;
        }}
        @media (min-width: 600px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (min-width: 900px) {{ .grid {{ grid-template-columns: repeat(3, 1fr); }} }}

        .card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            overflow: hidden;
            border: 1px solid #E5E5E5;
            transition: transform var(--transition), box-shadow var(--transition);
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.08);
            border-color: rgba(240, 80, 35, 0.3);
        }}

        /* Orange Top Strip on Card */
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: var(--primary);
            opacity: 0;
            transition: opacity 0.2s;
        }}
        .card:hover::before {{ opacity: 1; }}

        .card-header {{
            padding: 20px;
            padding-bottom: 12px;
            flex-grow: 1;
        }}

        .card-badge-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        .category-badge {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #555;
            background: #f0f0f0;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .discount-badge {{
            background: #fff3f0;
            color: var(--primary);
            font-weight: 800;
            font-size: 0.85rem;
            padding: 4px 8px;
            border-radius: 4px;
            text-align: right;
            max-width: 60%;
        }}

        .card-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0 0 8px 0;
            color: var(--text-main);
            line-height: 1.3;
        }}

        .card-eligibility {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: auto;
        }}

        .card-actions {{
            padding: 16px 20px;
            background: #FAFAFA;
            border-top: 1px solid #eee;
            text-align: right;
        }}
        .details-btn {{
            background: var(--primary);
            border: none;
            color: white;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            padding: 8px 16px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
            font-family: inherit;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .details-btn:hover {{
            background: #d64015;
            text-decoration: none;
        }}

        /* --- Modal --- */
        .modal-backdrop {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
            opacity: 0;
            transition: opacity 0.3s ease;
            backdrop-filter: blur(4px);
        }}
        .modal-backdrop.active {{
            display: flex;
            opacity: 1;
        }}
        .modal-content {{
            background: #fff;
            border-radius: var(--radius);
            width: 100%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 20px 40px rgba(0,0,0,0.25);
            transform: translateY(20px);
            transition: transform 0.3s ease;
            display: flex;
            flex-direction: column;
        }}
        .modal-backdrop.active .modal-content {{
            transform: translateY(0);
        }}
        .modal-header {{
            padding: 24px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            background: #fff;
            z-index: 10;
        }}
        .modal-title {{
            font-size: 1.5rem;
            font-weight: 800;
            margin: 0;
            color: var(--text-main);
            padding-right: 20px;
        }}
        .close-modal-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
            transition: color 0.2s;
        }}
        .close-modal-btn:hover {{ color: var(--primary); }}

        .modal-body {{
            padding: 24px;
            overflow-y: auto;
        }}

        .modal-offer-box {{
            background: #fff3f0;
            border-left: 4px solid var(--primary);
            padding: 16px;
            border-radius: 4px;
            margin-bottom: 24px;
        }}

        .modal-detail-row {{
            display: flex;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 20px;
        }}
        .modal-detail-icon {{
            color: var(--primary);
            width: 24px;
            height: 24px;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .modal-label {{
            display: block;
            font-size: 0.75rem;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
            font-weight: 700;
        }}
        .modal-value {{
            font-size: 1rem;
            color: var(--text-main);
            line-height: 1.6;
        }}

        .modal-footer {{
            padding: 20px 24px;
            border-top: 1px solid #eee;
            background: #fafafa;
            display: flex;
            justify-content: flex-end;
        }}
        .pdf-btn {{
            background: var(--text-main);
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-size: 0.95rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background 0.2s;
            font-family: inherit;
        }}
        .pdf-btn:hover {{
            background: #000;
        }}


        /* --- Footer --- */
        footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
            margin-top: 48px;
            background: #fff;
        }}
        .footer-link {{ color: var(--primary); font-weight: 600; text-decoration: none; }}
        .footer-link:hover {{ text-decoration: underline; }}

        /* --- Empty State --- */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
            background: #fff;
            border-radius: var(--radius);
            border: 1px dashed var(--border-color);
        }}
        .empty-icon {{ width: 64px; height: 64px; opacity: 0.2; margin-bottom: 20px; color: var(--secondary); }}

    </style>
</head>
<body>

    <!-- Header Structure -->
    <div class="utrgv-header">
        <div class="header-top">
            <div class="header-logo-container">
                <!-- UTRGV Logo SVG Placeholder -->
                <svg class="utrgv-logo-svg" viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15.8,12.5h8.9l-5.6,22.4c-0.6,2.3-2,3.5-4.3,3.5h-3.6c-2.3,0-3.7-1.2-4.3-3.5L1.3,12.5h8.9l2.8,13.7L15.8,12.5z M34.6,19.3h-5.9v19.1h-8.2V19.3h-5.9v-6.8h20V19.3z M52.5,23.3h-4.6v15.1h-8.2V12.5h13.9c2.7,0,4.8,0.5,6.3,1.4 c1.5,0.9,2.6,2.3,3.3,4.1c0.6,1.8,0.7,3.6,0.2,5.5c-0.6,2.1-2.1,3.7-4.4,4.7l6.1,10.2h-9.5L52.5,23.3z M47.9,18.5h3.6 c0.9,0,1.5-0.1,1.9-0.4c0.4-0.3,0.6-0.7,0.6-1.3c0-0.6-0.2-1.1-0.6-1.4c-0.4-0.3-1-0.4-1.9-0.4h-3.6V18.5z M85.2,34.4 c-2,1.7-4.6,2.5-7.9,2.5c-3.7,0-6.6-1.3-8.6-3.8c-2-2.5-3.1-6.1-3.1-10.8c0-4.8,1-8.5,3.1-11c2.1-2.5,4.9-3.8,8.5-3.8 c3,0,5.4,0.7,7.3,2.2l-3,5.6c-1.3-1-2.8-1.5-4.4-1.5c-1.4,0-2.5,0.6-3.3,1.7c-0.8,1.2-1.2,2.9-1.2,5.1s0.4,3.7,1.1,4.8 c0.7,1.1,1.8,1.6,3.1,1.6c0.8,0,1.5-0.1,2.1-0.4v-4h-3.1v-6h11.1v17.4C86.5,34.1,86,34.3,85.2,34.4z M99.1,12.5l-6.8,25.9h-8.4 l-6.8-25.9h8.5l2.4,13l2.6-13H99.1z" />
                </svg>
                <div style="color:white; font-weight:800; font-size:24px; line-height:1;">|</div>
                <!-- 10 Years Placeholder -->
                 <div style="font-weight:900; font-size:16px; margin-left:10px; line-height:1.1; text-align:center;">
                    10<br><span style="font-size:10px; display:block;">YEARS</span>
                </div>
            </div>

            <div class="header-main-bar">
                 <!-- Slant Element -->
                <div style="position:absolute; left:100%; top:0; height:100%; width:50px; background:inherit; clip-path: polygon(0 0, 100% 0, 0 100%);"></div>

                <div class="university-name">The University of Texas Rio Grande Valley</div>
                <nav class="header-nav">
                    <a href="#" class="header-link">Directory</a>
                    <a href="#" class="header-link">Maps</a>
                    <a href="#" class="header-link">MyUTRGV</a>
                    <a href="#" class="header-link">News</a>
                    <a href="#" class="header-link">Give</a>
                    <svg class="header-search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </nav>
            </div>
        </div>
    </div>

    <!-- App Header -->
    <div class="app-header">
        <h1 class="app-title">Vaquero Discounts</h1>
        <p class="app-subtitle">Exclusive savings for UTRGV Students, Faculty, Staff & Alumni</p>
    </div>

    <main>

        <!-- Search & Filters -->
        <section class="controls-section">
            <div class="search-container">
                <input type="text" id="searchInput" class="search-input" placeholder="Search businesses, categories..." aria-label="Search discounts">
                <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </div>

            <span class="filter-label">Browse by Category</span>
            <div class="chips-container" id="categoryContainer">
                <!-- Injected via JS -->
            </div>

            <span class="filter-label">Filter by Eligibility</span>
            <div class="eligibility-container" id="eligibilityContainer">
                <button class="toggle-btn" data-value="Students">Students</button>
                <button class="toggle-btn" data-value="Faculty">Faculty</button>
                <button class="toggle-btn" data-value="Staff">Staff</button>
                <button class="toggle-btn" data-value="Alumni">Alumni</button>
            </div>

            <button id="clearFilters" class="clear-filters" style="display: none;">Reset all filters</button>
        </section>

        <!-- Featured -->
        <section id="featuredSection" style="display: none;">
            <div class="section-title">
                Featured Offers
            </div>
            <div class="grid" id="featuredGrid">
                <!-- JS Injected -->
            </div>
        </section>

        <!-- Results -->
        <section>
            <div class="section-title">
                All Discounts
                <span class="result-count" id="resultCount">Showing 0 results</span>
            </div>
            <div class="grid" id="resultsGrid">
                <!-- JS Injected -->
            </div>
            <div id="emptyState" class="empty-state" style="display: none;">
                <svg class="empty-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                <h3>No results found</h3>
                <p>Try adjusting your search or filters.</p>
                <button class="toggle-btn" style="display:inline-block; margin-top:16px;" onclick="clearAllFilters()">Clear Filters</button>
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
                    Download PDF Coupon
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
        <svg id="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
    </div>

    <script>
        // --- DATA ---
        const DISCOUNTS = {discounts_json};

        // --- CONFIG ---
        // Updated based on actual CSV data
        const CATEGORIES = [
            "Eat & Drink (Food & Dining)",
            "Shop (Retail)",
            "Health & Beauty",
            "Fun & Events (Entertainment)",
            "Auto & Tech",
            "Services & Travel",
            "Other"
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
            check: document.getElementById('icon-check').innerHTML
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
            if (!text) return "";
            if (text.length <= limit) return text;
            return text.substring(0, limit) + "...";
        }}

        function renderCard(item) {{
            const who = item.whoCanRedeem.join(", ");
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
                <div class="modal-offer-box">
                    <span class="modal-label" style="color:var(--primary);">Discount Offer</span>
                    <strong style="font-size:1.4rem; color:var(--text-main); display:block; margin-top:4px;">${{item.discountAmount}}</strong>
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
                         ${{icons.check}}
                    </div>
                    <div>
                        <span class="modal-label">Eligibility</span>
                        <div class="modal-value">${{who}}</div>
                    </div>
                </div>

                ${{item.description ? `
                <div class="modal-detail-row">
                     <div class="modal-detail-icon" style="opacity:0;"></div>
                    <div style="font-style:italic; color:var(--text-muted); border-left:3px solid #eee; padding-left:12px;">${{item.description}}</div>
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
                        <div class="modal-value"><a href="${{item.website}}" target="_blank" style="color:var(--primary); font-weight:700;">Visit Website &rarr;</a></div>
                    </div>
                </div>
                ` : ''}}
            `;

            els.modalBackdrop.classList.add('active');
            document.body.style.overflow = 'hidden';
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
            const pageHeight = doc.internal.pageSize.getHeight();
            const contentWidth = pageWidth - (margin * 2);

            // Branding Header
            doc.setFillColor(240, 80, 35); // UTRGV Orange
            doc.rect(0, 0, pageWidth, 40, 'F');

            doc.setTextColor(255, 255, 255);
            doc.setFontSize(22);
            doc.setFont("helvetica", "bold");
            doc.text("UTRGV Vaquero Discounts", margin, 25);

            let y = 60;

            // Business Name
            doc.setTextColor(29, 29, 31); // Dark Gray
            doc.setFontSize(20);
            doc.setFont("helvetica", "bold");
            const titleSplit = doc.splitTextToSize(item.businessName, contentWidth);
            doc.text(titleSplit, margin, y);
            y += (titleSplit.length * 9) + 12;

            // Discount Box
            doc.setFillColor(250, 250, 250);
            doc.setDrawColor(220, 220, 220);
            doc.roundedRect(margin, y, contentWidth, 35, 2, 2, 'FD');

            doc.setTextColor(240, 80, 35);
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.text("OFFER:", margin + 5, y + 10);

            doc.setFontSize(12);
            doc.setFont("helvetica", "normal");
            doc.setTextColor(0, 0, 0);
            const discountSplit = doc.splitTextToSize(item.discountAmount, contentWidth - 10);
            doc.text(discountSplit, margin + 5, y + 22);

            y += 50;

            // Details
            function addDetail(label, value) {{
                if (!value) return;
                doc.setFontSize(9);
                doc.setTextColor(100, 100, 100);
                doc.setFont("helvetica", "bold");
                doc.text(label.toUpperCase(), margin, y);
                y += 5;

                doc.setFontSize(11);
                doc.setTextColor(0, 0, 0);
                doc.setFont("helvetica", "normal");
                const valSplit = doc.splitTextToSize(value, contentWidth);
                doc.text(valSplit, margin, y);
                y += (valSplit.length * 6) + 10;
            }}

            addDetail("How to Redeem", item.howToRedeem);
            addDetail("Eligibility", item.whoCanRedeem.join(", "));
            addDetail("Location", item.address);
            if (item.phone) addDetail("Phone", item.phone);

            // --- New Internal Fields (Only in PDF) ---
            y += 10; // Extra Spacer

            doc.setDrawColor(200, 200, 200);
            doc.setLineWidth(0.1);
            doc.line(margin, y, pageWidth - margin, y);
            y += 10;

            // Admin Section Title
            doc.setFontSize(9);
            doc.setTextColor(150, 150, 150);
            doc.text("PARTNER INFORMATION", margin, y);
            y += 6;

            // Using a simple grid for these
            const leftCol = margin;
            const rightCol = margin + (contentWidth / 2);

            // Row 1
            if (item.joinDate) {{
                doc.setFontSize(8); doc.setTextColor(150,150,150); doc.text("VDP JOIN DATE", leftCol, y);
                doc.setFontSize(9); doc.setTextColor(50,50,50); doc.text(item.joinDate, leftCol, y+5);
            }}

            if (item.authorizedBy) {{
                doc.setFontSize(8); doc.setTextColor(150,150,150); doc.text("AUTHORIZED BY", rightCol, y);
                doc.setFontSize(9); doc.setTextColor(50,50,50); doc.text(item.authorizedBy, rightCol, y+5);
                y += 12;
            }} else {{
                y += 12;
            }}

            // Row 2
            if (item.contactTitle) {{
                doc.setFontSize(8); doc.setTextColor(150,150,150); doc.text("CONTACT TITLE/ROLE", leftCol, y);
                doc.setFontSize(9); doc.setTextColor(50,50,50); doc.text(item.contactTitle, leftCol, y+5);
                y += 15;
            }} else {{
                y += 15;
            }}


            // --- Footer / About VDP ---
            // Push to bottom
            let footerY = pageHeight - 40;
            if (y > footerY) footerY = y + 10;

            doc.setDrawColor(240, 80, 35);
            doc.setLineWidth(0.5);
            doc.line(margin, footerY, pageWidth - margin, footerY);

            footerY += 10;

            doc.setFontSize(9);
            doc.setTextColor(80, 80, 80);

            const aboutText = "The Vaquero Discount Program (VDP) offers exclusive discounts to UTRGV students, faculty, staff, and alumni.";
            const aboutSplit = doc.splitTextToSize(aboutText, contentWidth);
            doc.text(aboutSplit, margin, footerY);

            footerY += (aboutSplit.length * 5) + 5;

            doc.setTextColor(240, 80, 35);
            doc.textWithLink("utrgv.edu/vdp", margin, footerY, {{ url: "https://www.utrgv.edu/vdp" }});

            doc.save(`${{item.businessName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}}_coupon.pdf`);
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
