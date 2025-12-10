import csv
import json
import urllib.request
import io

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQregHbek9Lten27U-Hs92yB81IoGO3PyJGOOekrIkTeXpI9XRV-YMaw-DNTZk-MCQTEhLcqkB3kMF5/pub?output=csv"
OUTPUT_CSV = "categorized_discounts.csv"
EXISTING_DATA_FILE = "listings.json"

# Category Mapping Logic (from transform_data.py)
OLD_CAT_TO_NEW = {
    "Dining": "Eat & Drink (Food & Dining)",
    "Fashion": "Shop (Retail)",
    "Health & Beauty": "Health & Beauty",
    "Entertainment": "Fun & Events (Entertainment)",
    "Automotive": "Auto & Tech",
    "Electronics": "Auto & Tech",
    "Services": "Services & Travel",
    "Travel": "Services & Travel",
    "Other": "Shop (Retail)"
}

# Keyword based categorization for new items
KEYWORD_RULES = [
    (["food", "pizza", "burger", "taco", "grill", "cafe", "coffee", "bakery", "sushi", "dining", "restaurant", "nutrition", "donuts", "wings"], "Eat & Drink (Food & Dining)"),
    (["boutique", "apparel", "clothing", "wear", "outfitters", "shop", "store", "gift", "jewelry", "boots", "shoes", "retail"], "Shop (Retail)"),
    (["beauty", "hair", "salon", "waxing", "barber", "spa", "wellness", "fitness", "gym", "health", "workout", "nutrition"], "Health & Beauty"),
    (["auto", "car", "oil", "tire", "mechanic", "wash", "parts", "phone", "computer", "repair", "tech", "electronics"], "Auto & Tech"),
    (["entertainment", "fun", "game", "bowling", "movie", "photo", "event", "party", "rental"], "Fun & Events (Entertainment)"),
    (["hotel", "travel", "taxi", "transport", "service", "consult", "print", "copy", "construction", "insurance", "cleaning", "pest"], "Services & Travel")
]

def load_existing_mappings():
    """Loads existing business-to-category mappings from listings.json"""
    mapping = {}
    try:
        with open(EXISTING_DATA_FILE, 'r') as f:
            data = json.load(f)
            for item in data:
                name = item.get("vendor")
                cat = item.get("category")
                if name and cat:
                    # Normalize name for better matching
                    mapping[name.lower().strip()] = OLD_CAT_TO_NEW.get(cat, "Shop (Retail)")
    except FileNotFoundError:
        print("Warning: listings.json not found. Proceeding without existing mappings.")
    return mapping

def determine_category(name, description, existing_map):
    """Determines category based on existing map or keywords."""
    name_clean = name.lower().strip()

    # 1. Check existing map
    if name_clean in existing_map:
        return existing_map[name_clean]

    # 2. Check keywords in name and description
    text = (name + " " + description).lower()
    for keywords, category in KEYWORD_RULES:
        for word in keywords:
            if word in text:
                return category

    # 3. Default
    return "Shop (Retail)"

def parse_who_can_redeem(text):
    """Parses the 'Who Can Redeem' text into a list."""
    roles = []
    text_lower = text.lower()
    if "student" in text_lower: roles.append("Students")
    if "faculty" in text_lower: roles.append("Faculty")
    if "staff" in text_lower: roles.append("Staff")
    if "alumni" in text_lower: roles.append("Alumni")

    if not roles:
        return ["Students", "Faculty", "Staff"] # Default fallback
    return roles

def main():
    print("Loading existing mappings...")
    existing_map = load_existing_mappings()

    print(f"Downloading data from {GOOGLE_SHEET_URL}...")
    try:
        response = urllib.request.urlopen(GOOGLE_SHEET_URL)
        csv_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    # Parse CSV
    print("Processing data...")
    f = io.StringIO(csv_data)
    reader = csv.DictReader(f)

    processed_rows = []
    row_id = 100 # Start IDs from 100

    # Expected Google Sheet Headers (based on observation):
    # Name of the Business, Discount Amount, Who Can Redeem, How to Redeem, About this Business, Address, Phone, Email address, Website/Social Media

    for row in reader:
        # Extract fields safely
        name = row.get("Name of the Business", "").strip()
        if not name: continue # Skip empty rows

        discount = row.get("Discount Amount", "")
        who_raw = row.get("Who Can Redeem", "")
        how = row.get("How to Redeem", "")
        about = row.get("About this Business", "")
        address = row.get("Address", "")
        phone = row.get("Phone", "")
        email = row.get("Email address", "")
        website = row.get("Website/Social Media", "")

        # Determine Category
        category = determine_category(name, about, existing_map)

        # Process specific fields
        who_list = parse_who_can_redeem(who_raw)

        # Proximity logic (simple guess)
        proximity = "RGV Area"
        if "," in address:
            parts = address.split(",")
            # usually "Street, City, Zip"
            if len(parts) >= 2:
                proximity = "Near " + parts[-2].strip() # City

        # Feature flag (simple logic: random or specific names, for now just false or keep some logic)
        # Let's feature if discount is > 20% or keywords?
        # For stability, let's just feature a few hardcoded ones if they exist, or just leave it false.
        # The original code featured specific IDs. I'll feature if "Free" or "20%" or "25%" in discount.
        is_featured = False
        if "free" in discount.lower() or "25%" in discount or "20%" in discount:
             is_featured = True

        # Construct new row
        new_row = {
            "id": str(row_id),
            "businessName": name,
            "category": category,
            "discountAmount": discount,
            "whoCanRedeem": ";".join(who_list), # Join with ; for CSV storage
            "howToRedeem": how,
            "description": about,
            "address": address,
            "phone": phone,
            "email": email,
            "website": website,
            "campusProximity": proximity,
            "isFeatured": str(is_featured),
            "tags": category.split(" ")[0].lower() # First word of category as tag
        }

        processed_rows.append(new_row)
        row_id += 1

    # Write to Output CSV
    print(f"Writing {len(processed_rows)} entries to {OUTPUT_CSV}...")
    fieldnames = [
        "id", "businessName", "category", "discountAmount", "whoCanRedeem",
        "howToRedeem", "description", "address", "phone", "email",
        "website", "campusProximity", "isFeatured", "tags"
    ]

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed_rows:
            writer.writerow(row)

    print("Done!")

if __name__ == "__main__":
    main()
