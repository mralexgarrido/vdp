import json

# Category mapping
cat_map = {
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

# Load original data
with open("listings.json", "r") as f:
    data = json.load(f)

new_data = []
for item in data:
    # Who mapping
    who_raw = item.get("who", "Students, Faculty, and Staff")
    who_list = []
    if "Student" in who_raw: who_list.append("Students")
    if "Faculty" in who_raw: who_list.append("Faculty")
    if "Staff" in who_raw: who_list.append("Staff")
    # Add Alumni randomly to some entries to show feature
    if item["id"] % 5 == 0:
        who_list.append("Alumni")

    # Category mapping
    old_cat = item.get("category", "Other")
    new_cat = cat_map.get(old_cat, "Shop (Retail)")

    # Description
    desc = item.get("about", "")

    # Address/City logic
    addr = item.get("address", "")

    # Feature flag (randomly feature some)
    is_featured = False
    if item["id"] in [501, 403, 102, 602, 308]: # Example featured IDs
        is_featured = True

    new_entry = {
        "id": str(item["id"]),
        "businessName": item.get("vendor", "Unknown"),
        "category": new_cat,
        "discountAmount": item.get("discount", "See details"),
        "whoCanRedeem": who_list,
        "howToRedeem": item.get("how", "Show UTRGV ID"),
        "description": desc,
        "address": addr,
        "phone": item.get("phone", ""),
        "email": "", # Not in source
        "website": "", # Not in source clearly, mostly
        "social": "",
        "campusProximity": "Near " + addr.split(",")[1].strip() if "," in addr else "RGV Area",
        "isFeatured": is_featured,
        "tags": [new_cat.split(" ")[0].lower()] # Simple tag generation
    }

    # Clean up phone
    if not new_entry["phone"]:
        new_entry["phone"] = ""

    new_data.append(new_entry)

print(json.dumps(new_data, indent=2))
